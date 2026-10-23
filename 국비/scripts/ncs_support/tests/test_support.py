import base64
import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.ncs_support.common import WORK_ROOT, child, now, read_json, sha256, write_json
from scripts.ncs_support.dates import next_weekday
from scripts.ncs_support.package import package_group
from scripts.ncs_support.records import group_dir, initialize, load_run, record, status
from scripts.ncs_support.render import build_group
from scripts.ncs_support.validate import validate_group


class DateTests(unittest.TestCase):
    def test_weekdays_weekends_month_year_leap(self):
        for end, expected in [('2026-06-04', '2026-06-05'), ('2026-06-05', '2026-06-08'),
                              ('2026-06-06', '2026-06-08'), ('2026-06-07', '2026-06-08'),
                              ('2026-07-31', '2026-08-03'), ('2026-12-31', '2027-01-01'),
                              ('2024-02-28', '2024-02-29')]:
            with self.subTest(end=end):
                self.assertEqual(next_weekday(end), expected)

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            next_weekday('2026-02-30')


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '설정').mkdir()
        write_json(self.root / '설정/과정정보.json', read_json(WORK_ROOT / '설정/과정정보.json'))
        self.run = Path(initialize('A', '테스트 단위', '2026-07-03', '6', 'register', 'isolated test fixture', root=self.root)['run'])
        self.job = load_run(self.run)[1]

    def envelope(self, group=None):
        e = {'course_id':'A', 'unit':'테스트 단위', 'lcode':'6', 'Pcode':'300002', 'BoardCode':'85', 'version':'ver4', 'checked_at':now()}
        if group:
            e.update(group=group, post_date='2026-07-06')
        return e

    def save(self, stage, fields, group=None):
        e = self.envelope(group)
        e.update(fields)
        file = self.run / '01_근거자료' / ('test-' + stage + (group or '') + '.json')
        write_json(file, e)
        return record(self.run, stage, file, group)

    def globals(self, skip=False):
        self.save('target_confirmed', {'course_name':self.job['course']['name'], 'unit_end_date':'2026-07-03', 'screen_confirmed':True})
        self.save('sources_collected', {'task_read':True, 'scores_read':True, 'feedback_read':True, 'meeting_read':True, 'source_urls':['https://example.org/test-fixture']})
        self.save('meeting_resolved', {'mode':'skipped' if skip else 'existing', 'exact_readback':True, 'reason':'isolated test fixture'})

    def materials(self, group='A'):
        p = group_dir(self.run, group)
        (p / 'process.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='))
        data = {'example':False,'group':group,'unit':'테스트 단위','subtitle':'Fixture learning goal',
                'sections':[{'title':'Observe, practice and check','html':'<p>Isolated fixture.</p><p><img src="@@process.png@@" alt="test fixture" /></p><table><tr><th>Observe</th><th>Check</th></tr><tr><td>A</td><td>B</td></tr></table>'}],
                'images':['process.png'], 'sources':[{'url':'https://example.org/test-fixture','provider':'test fixture','title':'Fixture reference','language':'ko','free':True,'scope':'test scope','activity':'test activity','checked_at':now()}],
                'worksheets':[{'title':'Practice evidence','fields':['File','Reason','Result']}],
                'files':['학습자료.pdf','실습양식.docx','읽는순서.txt','process.png','빈칸양식/01_실습.csv']}
        write_json(p / 'content.json', data)
        build_group(self.run, group)
        # Minimal signature fixture only. Real PDF rendering is verified separately.
        (p / '학습자료.pdf').write_bytes(b'%PDF-1.4\n% isolated validator fixture\n%%EOF')
        package_group(self.run, group)
        return p

    def review(self, group='A'):
        self.save('materials_verified', {'pdf_page_count':2, **{k:True for k in ('local_checks','pdf_reviewed','visual_reviewed','sources_reviewed','privacy_reviewed')}}, group)

    def registration(self, group='A'):
        p = group_dir(self.run, group)
        post = read_json(p / 'post.json')
        return {'title':post['title'],'post_id':str(100 + ord(group)), 'url':'https://sbsartdj.maniaro.net/teacher/curri/ver4/bbs/view.php?Pcode=300002&BoardCode=85&no='+str(100 + ord(group)), 'observed_in_list':True}

    def test_resume_does_not_overwrite_or_create_new_run(self):
        self.globals()
        result = initialize('A','테스트 단위','2026-07-03','6','register','same authorized task',root=self.root)
        self.assertTrue(result['resumed'])
        self.assertEqual(Path(result['run']), self.run)
        self.assertEqual(len(result['state']['global']), 3)

    def test_course_separation(self):
        other = initialize('B','테스트 단위','2026-07-03','6',root=self.root)
        self.assertNotEqual(Path(other['run']),self.run)
        self.assertIn('B과정', other['run'])

    def test_path_traversal_and_internal_package_rejected(self):
        for name in ('../secret', '/abs', 'C:/secret', 'folder/../../secret', 'CON.txt', 'folder\\..\\secret'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                child(self.root,name)
        p=self.materials()
        data=read_json(p/'content.json');data['files'].append('content.json');write_json(p/'content.json',data)
        with self.assertRaises(ValueError):
            package_group(self.run,'A')

    def test_cannot_skip_stages_or_mix_course(self):
        with self.assertRaises(ValueError):
            self.save('sources_collected',{})
        with self.assertRaises(ValueError):
            self.save('target_confirmed',{'Pcode':'500000','course_name':self.job['course']['name'],'unit_end_date':'2026-07-03','screen_confirmed':True})

    def test_render_package_preserves_readability_and_editable_sheets(self):
        p=self.materials()
        result=validate_group(self.run,'A')
        self.assertTrue(result['ok'])
        html=(p/'article.html').read_text(encoding='utf-8')
        for value in ('max-width:980px','font-size:17px','line-height:1.95','padding:14px 16px','a-learning-1'):
            self.assertIn(value,html)
        with zipfile.ZipFile(p/'학습자료.zip') as z:
            self.assertNotIn('content.json',z.namelist())
            self.assertEqual(len(z.namelist()),5)

    def test_changed_zip_member_is_rejected(self):
        p=self.materials()
        (p/'읽는순서.txt').write_text('changed',encoding='utf-8')
        with self.assertRaises(ValueError):
            validate_group(self.run,'A')

    def test_failed_manual_review_does_not_complete(self):
        self.globals();self.materials()
        with self.assertRaises(ValueError):
            self.save('materials_verified',{'local_checks':True},'A')
        self.assertEqual(status(self.run)['status'],'in_progress')

    def test_material_change_invalidates_review_and_blocks_registration(self):
        self.globals();p=self.materials();self.review()
        (p/'학습자료.pdf').write_bytes(b'%PDF-1.4 changed')
        self.assertEqual(status(self.run)['stale_groups'],['A'])
        with self.assertRaises(ValueError):
            self.save('registered',self.registration(),'A')

    def test_wrong_url_duplicate_and_attachment_mismatch_are_blocked(self):
        self.globals();self.materials();self.review()
        r=self.registration();wrong=copy.deepcopy(r);wrong['url']=wrong['url'].replace('BoardCode=85','BoardCode=1')
        with self.assertRaises(ValueError): self.save('registered',wrong,'A')
        self.save('registered',r,'A')
        with self.assertRaises(ValueError): self.save('registered',r,'A')
        verify={**r,**{k:True for k in ('course_confirmed','title_exact','date_exact','text_exact','images_loaded','anchors_valid','anchor_navigation','references_checked','layout_reviewed')},'reference_urls':['https://example.org/test-fixture'],'attachment_status':200,'attachment_sha256':'0'*64}
        with self.assertRaises(ValueError): self.save('verified',verify,'A')
        with self.assertRaises(ValueError): build_group(self.run,'A')

    def test_three_groups_required_for_complete(self):
        self.globals()
        for g in 'ABC':
            p=self.materials(g);self.review(g);r=self.registration(g);self.save('registered',r,g)
            verify={**r,**{k:True for k in ('course_confirmed','title_exact','date_exact','text_exact','images_loaded','anchors_valid','anchor_navigation','references_checked','layout_reviewed')},'reference_urls':['https://example.org/test-fixture'],'attachment_status':200,'attachment_sha256':sha256(p/'학습자료.zip')}

    def test_resume_rejects_changed_unit_identity(self):
        with self.assertRaises(ValueError):
            initialize('A','테스트 단위','2026-07-03','99','register','same task',root=self.root)
            result=self.save('verified',verify,g)
            self.assertEqual(result['status'],'complete' if g=='C' else 'in_progress')

    def test_prepare_only_run_cannot_register(self):
        job=read_json(self.run/'작업정보.json');job['action']='prepare';write_json(self.run/'작업정보.json',job)
        self.globals()
        for g in 'ABC': self.materials(g);self.review(g)
        self.assertEqual(status(self.run)['status'],'prepared')
        with self.assertRaises(ValueError): self.save('registered',self.registration(),'A')

    def test_skip_meeting_requires_explicit_mode(self):
        self.save('target_confirmed', {'course_name':self.job['course']['name'],'unit_end_date':'2026-07-03','screen_confirmed':True})
        self.save('sources_collected', {'task_read':True,'scores_read':True,'feedback_read':True,'meeting_read':True,'source_urls':['https://example.org']})
        with self.assertRaises(ValueError): self.save('meeting_resolved',{'mode':'skipped','reason':'not requested'})
        job=read_json(self.run/'작업정보.json');job['meeting_mode']='skip';write_json(self.run/'작업정보.json',job)
        self.save('meeting_resolved',{'mode':'skipped','reason':'explicit user exclusion'})

    def test_templates_and_unverified_sources_are_rejected(self):
        p=self.materials();data=read_json(p/'content.json');data['example']=True;write_json(p/'content.json',data)
        with self.assertRaises(ValueError): build_group(self.run,'A')
        data['example']=False;data['sources'][0]['checked_at']='not checked';write_json(p/'content.json',data)
        with self.assertRaises(ValueError): build_group(self.run,'A')


if __name__ == '__main__':
    unittest.main()
