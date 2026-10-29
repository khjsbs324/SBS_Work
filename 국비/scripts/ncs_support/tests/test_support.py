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
from scripts.ncs_support.catalog import confirm_target, inventory, write_report
from scripts.ncs_support.pipeline import next_in_course, next_step, start_unit
from scripts.ncs_support.revisions import begin_revision
from scripts.ncs_support.meeting import MEETING_PATH, REVIEW_CHECKS, check_meeting, material_plan, registration_check


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
        self.save('sources_collected', {'task_basis':'original', 'original_task_full_text_available':True, 'task_read':True, 'scores_read':True, 'feedback_read':True, 'meeting_read':True, 'source_urls':['https://example.org/test-fixture']})
        self.save('meeting_resolved', self.meeting_receipt('skipped' if skip else 'existing'))

    def meeting_receipt(self, mode='existing'):
        path = self.run / MEETING_PATH
        if not path.exists():
            roster = {'course_id':'A', 'unit':'테스트 단위', 'lcode':'6', 'checked_at':now(),
                      'source_url':self.job['course']['base_url']+'/appraisal/app/index.php?Pcode=300002&Lcode=6',
                      'unit_elements':['실제 요소 제작하기'],
                      'students':[{'id':g, 'name':'학생'+g} for g in 'ABC']}
            write_json(self.run/'01_근거자료/평가대상.json', roster)
            names = '\n'.join(g+'그룹 : [학생'+g+']' for g in 'ABC')
            write_json(path, {'schema_version':1, 'example':False, 'unit':'테스트 단위',
                'actual_date':'2026-10-29', 'meeting_date':'2026-10-29',
                'roster_path':'01_근거자료/평가대상.json',
                'analysis':'주제\n목적\n결과\n'+names+'\n실제 요소 제작하기\n종합 의견\n건의사항',
                'improvement':'조치사항\n'+names+'\n학생 변화\n교수법 개선\n후속 지도',
                'groups':{g:{'student_ids':[g], 'basis':'Observed basis '+g, 'strengths':'Strength '+g,
                             'needs':'Need '+g, 'activities':'Activity '+g, 'criteria':'Criterion '+g} for g in 'ABC'},
                'teaching_link':{'previous_unit':'이전 단위', 'next_unit':'다음 단위', 'follow_up':'실제 후속 지도'}})
        doc = read_json(path)
        checks = check_meeting(self.run)
        return {'mode':mode, 'reason':'isolated test fixture', 'meeting_path':MEETING_PATH,
                'meeting_sha256':checks['meeting_sha256'], 'roster_sha256':checks['roster_sha256'],
                'review_checks':{k:True for k in REVIEW_CHECKS}, 'review_notes':'Fixture manual review',
                'local_reviewed':True, 'exclusion_request':'Explicit fixture exclusion' if mode=='skipped' else '',
                'exact_readback':True, 'readback':{**{k:doc[k] for k in ('analysis','improvement','meeting_date')},
                    'checked_at':now(), 'url':self.job['course']['base_url']+'/appraisal/analysis/index.php?Pcode=300002&Lcode=6'}}

    def materials(self, group='A'):
        if 'meeting_resolved' not in load_run(self.run)[2]['global']:
            self.globals()
        p = group_dir(self.run, group)
        (p / 'process.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='))
        data = {'example':False,'group':group,'unit':'테스트 단위','subtitle':'Fixture learning goal',
                'support_plan_sha256':material_plan(self.run, group)['support_plan_sha256'],
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
        self.save('materials_verified', {'pdf_page_count':2,
            'support_plan_sha256':material_plan(self.run, group)['support_plan_sha256'],
            'plan_alignment_reviewed':True, 'plan_alignment_notes':'Fixture needs/activity/criteria review',
            **{k:True for k in ('local_checks','pdf_reviewed','visual_reviewed','sources_reviewed','privacy_reviewed')}}, group)

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
            result=self.save('verified',verify,g)
            self.assertEqual(result['status'],'complete' if g=='C' else 'in_progress')

    def test_resume_rejects_changed_unit_identity(self):
        with self.assertRaises(ValueError):
            initialize('A','테스트 단위','2026-07-03','99','register','same task',root=self.root)

    def test_prepare_only_run_cannot_register(self):
        job=read_json(self.run/'작업정보.json');job['action']='prepare';write_json(self.run/'작업정보.json',job)
        self.globals()
        for g in 'ABC': self.materials(g);self.review(g)
        self.assertEqual(status(self.run)['status'],'prepared')
        with self.assertRaises(ValueError): self.save('registered',self.registration(),'A')

    def test_skip_meeting_requires_explicit_mode(self):
        self.save('target_confirmed', {'course_name':self.job['course']['name'],'unit_end_date':'2026-07-03','screen_confirmed':True})
        self.save('sources_collected', {'task_basis':'original','original_task_full_text_available':True,'task_read':True,'scores_read':True,'feedback_read':True,'meeting_read':True,'source_urls':['https://example.org']})
        with self.assertRaises(ValueError): self.save('meeting_resolved',{'mode':'skipped','reason':'not requested'})
        job=read_json(self.run/'작업정보.json');job['meeting_mode']='skip';write_json(self.run/'작업정보.json',job)
        self.save('meeting_resolved',self.meeting_receipt('skipped'))

    def test_templates_and_unverified_sources_are_rejected(self):
        p=self.materials();data=read_json(p/'content.json');data['example']=True;write_json(p/'content.json',data)
        with self.assertRaises(ValueError): build_group(self.run,'A')
        data['example']=False;data['sources'][0]['checked_at']='not checked';write_json(p/'content.json',data)
        with self.assertRaises(ValueError): build_group(self.run,'A')

    def catalog_fixture(self):
        write_json(self.root/'설정/작업대상.json', {'schema_version':1,'course_id':'A','units':[
            {'unit':'테스트 단위','enabled':True,'observation':None},
            {'unit':'다음 단위','enabled':True,'observation':None}]})

    def verify_fixture(self, group):
        r = self.registration(group)
        return {**r, **{k:True for k in ('course_confirmed','title_exact','date_exact','text_exact',
                 'images_loaded','anchors_valid','anchor_navigation','references_checked','layout_reviewed')},
                'reference_urls':['https://example.org/test-fixture'], 'attachment_status':200,
                'attachment_sha256':sha256(group_dir(self.run,group)/'학습자료.zip')}

    def complete_fixture(self):
        self.globals()
        for g in 'ABC':
            self.materials(g); self.review(g)
            self.save('registered',self.registration(g),g)
            self.save('verified',self.verify_fixture(g),g)

    def test_pipeline_resumes_skips_complete_and_reports_without_mutating_runs(self):
        self.catalog_fixture()
        self.assertEqual(next_in_course(root=self.root)['stage'],'target_confirmed')
        self.globals()
        self.assertEqual(next_step(self.run)['stage'],'materials_verified')
        self.materials(); self.review()
        self.assertEqual(next_step(self.run)['stage'],'registered')
        self.save('registered',self.registration(),'A')
        self.assertEqual(next_step(self.run)['stage'],'verified')
        self.save('verified',self.verify_fixture('A'),'A')
        for g in 'BC':
            self.materials(g); self.review(g); self.save('registered',self.registration(g),g)
            self.save('verified',self.verify_fixture(g),g)
        before = sha256(self.run/'진행상태.json')
        self.assertEqual(next_step(self.run)['stage'],'done')
        self.assertEqual(next_in_course(root=self.root)['unit'],'다음 단위')
        self.assertEqual(write_report(root=self.root)['units'],2)
        self.assertEqual(sha256(self.run/'진행상태.json'),before)
        with self.assertRaises(ValueError): inventory('B',root=self.root)

    def test_catalog_requires_observed_target_and_preserves_prior_observations(self):
        self.catalog_fixture()
        with self.assertRaises(ValueError): start_unit('테스트 단위',root=self.root)
        fields={**self.envelope(),'course_name':self.job['course']['name'],'unit_end_date':'2026-07-03',
                'screen_confirmed':True,'source_url':'https://sbsartdj.maniaro.net/teacher/curri/ver4/lecture/index.php?Pcode=300002'}
        path=self.root/'target.json'
        write_json(path,{**fields,'Pcode':'500000'})
        with self.assertRaises(ValueError): confirm_target(path,root=self.root)
        write_json(path,fields)
        confirm_target(path,root=self.root);confirm_target(path,root=self.root)
        data=read_json(self.root/'설정/작업대상.json')
        self.assertEqual(len(data['units'][0]['observation_history']),1)
        resumed=start_unit('테스트 단위',action='register',request='test',root=self.root)
        self.assertTrue(resumed['resumed'])
        self.assertEqual(Path(resumed['run']),self.run)

    def test_catalog_uses_latest_run_but_exposes_bad_identity(self):
        self.catalog_fixture(); self.complete_fixture()
        old=self.run.parent/'2000-01-01T000000'
        old.mkdir()
        job={**self.job,'created_at':'2000-01-01T00:00:00+09:00'}
        write_json(old/'작업정보.json',job)
        write_json(old/'진행상태.json',{'global':{},'groups':{g:{} for g in 'ABC'},'history':[]})
        self.assertEqual(inventory(root=self.root)['units'][0]['status'],'complete')
        with self.assertRaises(ValueError):
            initialize('A','테스트 단위','2026-07-03','6','register','test',root=self.root)
        job['lcode']='99';write_json(old/'작업정보.json',job)
        self.assertEqual(inventory(root=self.root)['units'][0]['status'],'needs_attention')

    def test_revision_preserves_original_and_requires_same_post_and_reverification(self):
        self.complete_fixture()
        original=sha256(group_dir(self.run,'A')/'학습자료.zip')
        evidence=self.root/'live.json'
        write_json(evidence,{**self.envelope('A'),**self.registration(),'live_post_checked':True})
        result=begin_revision(self.run,'A',evidence,'test correction','authorized test')
        self.assertEqual(result['active_revisions'],['A'])
        self.assertEqual(result['status'],'in_progress')
        stages=load_run(self.run)[2]['groups']['A']
        backup=self.run/stages['revision']['backup']
        self.assertEqual(sha256(backup/'수정전자료/학습자료.zip'), original)
        with self.assertRaises(ValueError): begin_revision(self.run,'A',evidence,'again','test')
        with self.assertRaises(ValueError): build_group(self.run,'B')
        folder=group_dir(self.run,'A')
        data=read_json(folder/'content.json');data['subtitle']='Corrected content';write_json(folder/'content.json',data)
        build_group(self.run,'A');package_group(self.run,'A');self.review('A')
        with self.assertRaises(ValueError): self.save('registered',self.registration(),'A')
        wrong=self.verify_fixture('A');wrong['post_id']='999'
        with self.assertRaises(ValueError): self.save('verified',wrong,'A')
        self.assertEqual(next_step(self.run)['stage'],'verified')
        final=self.save('verified',self.verify_fixture('A'),'A')
        self.assertEqual(final['status'],'complete');self.assertEqual(final['active_revisions'],[])
        self.assertTrue((backup/'정정완료.json').exists())
        self.assertEqual(sha256(backup/'수정전자료/학습자료.zip'),original)
        with self.assertRaises(ValueError): build_group(self.run,'A')

    def test_reconstructed_evidence_does_not_claim_original_was_read(self):
        self.save('target_confirmed', {'course_name':self.job['course']['name'],'unit_end_date':'2026-07-03','screen_confirmed':True})
        evidence={'task_basis':'feedback_reconstruction','original_task_full_text_available':False,
                  'task_read':True,'scores_read':True,'feedback_read':True,'meeting_read':True,
                  'task_scope':'Observed feedback scope','limitations':['Original unavailable'],
                  'source_urls':['https://example.org/test-fixture']}
        with self.assertRaises(ValueError): self.save('sources_collected',evidence)
        evidence['task_read']=False
        self.save('sources_collected',evidence)
        self.assertEqual(next_step(self.run)['stage'],'meeting_resolved')

    def test_prepare_can_record_local_meeting_draft_without_claiming_lms_save(self):
        job=read_json(self.run/'작업정보.json');job['action']='prepare';write_json(self.run/'작업정보.json',job)
        self.save('target_confirmed', {'course_name':self.job['course']['name'],'unit_end_date':'2026-07-03','screen_confirmed':True})
        self.save('sources_collected', {'task_basis':'original','original_task_full_text_available':True,
                  'task_read':True,'scores_read':True,'feedback_read':True,'meeting_read':True,'source_urls':['https://example.org']})
        draft=self.run/'02_회의록/회의록.json'
        self.save('meeting_resolved',self.meeting_receipt('drafted'))
        self.assertEqual(load_run(self.run)[2]['global']['meeting_resolved']['draft_sha256'],sha256(draft))
        content=read_json(draft);content['analysis']+='\nUpdated draft';write_json(draft,content)
        self.assertEqual(status(self.run)['stale_global'],['meeting_resolved'])
        self.assertEqual(next_step(self.run)['stage'],'meeting_resolved')
        self.save('meeting_resolved',self.meeting_receipt('drafted'))
        self.assertEqual(status(self.run)['stale_global'],[])
        self.assertTrue(any(e['stage']=='draft_review_replaced' for e in load_run(self.run)[2]['history']))

    def test_empty_catalog_is_not_reported_as_completed(self):
        write_json(self.root/'설정/작업대상.json',{'schema_version':1,'course_id':'A','units':[]})
        self.assertEqual(next_in_course(root=self.root)['stage'],'inspect_catalog')

    def test_revision_rejects_files_changed_before_backup(self):
        self.complete_fixture()
        evidence=self.root/'live.json'
        write_json(evidence,{**self.envelope('A'),**self.registration(),'live_post_checked':True})
        (group_dir(self.run,'A')/'학습자료.pdf').write_bytes(b'%PDF-changed')
        before=sha256(self.run/'진행상태.json')
        with self.assertRaises(ValueError): begin_revision(self.run,'A',evidence,'test','test')
        self.assertEqual(sha256(self.run/'진행상태.json'),before)
        self.assertEqual(next_step(self.run)['stage'],'inspect_changed_materials')

    def test_no_material_mutation_before_complete_meeting(self):
        for call in (lambda: build_group(self.run, 'A'), lambda: package_group(self.run, 'A'),
                     lambda: material_plan(self.run, 'A'), lambda: registration_check(self.run, 'A')):
            with self.subTest(call=call), self.assertRaises(ValueError): call()
        self.assertFalse((group_dir(self.run, 'A')/'article.html').exists())
        self.assertFalse((group_dir(self.run, 'A')/'학습자료.zip').exists())

    def test_existing_flag_is_not_a_review(self):
        self.globals()
        before = sha256(self.run/'진행상태.json')
        with self.assertRaises(ValueError):
            self.save('meeting_resolved', {'mode':'existing','exact_readback':True,'reason':'exists'})
        self.assertEqual(before, sha256(self.run/'진행상태.json'))

    def test_empty_duplicate_missing_unknown_and_body_mismatched_students_rejected(self):
        self.meeting_receipt()
        path = self.run/MEETING_PATH
        good = read_json(path)
        variants=[]
        for members in ([], ['A'], ['unknown'], ['C','C']):
            bad=copy.deepcopy(good);bad['groups']['C']['student_ids']=members;variants.append(bad)
        bad=copy.deepcopy(good);bad['analysis']=bad['analysis'].replace('C그룹 : [학생C]', 'C그룹 : [해당 없음]');variants.append(bad)
        for bad in variants:
            with self.subTest(group=bad['groups']['C']):
                write_json(path,bad)
                with self.assertRaises(ValueError): check_meeting(self.run)
        write_json(path,good)
        roster_path=self.run/good['roster_path'];roster=read_json(roster_path)
        roster['students'].append({'id':'D','name':'누락학생'});write_json(roster_path,roster)
        with self.assertRaises(ValueError): check_meeting(self.run)

    def test_summary_metadata_and_missing_element_cannot_pass(self):
        self.meeting_receipt();path=self.run/MEETING_PATH;good=read_json(path)
        for body in ('간략한 교수법 기록만 있음',good['analysis'].replace('실제 요소 제작하기',''),
                     good['analysis']+'\n추가 기록일 : 2026-10-29',good['analysis']+'\nT01 안내'):
            write_json(path,{**good,'analysis':body})
            with self.subTest(body=body), self.assertRaises(ValueError): check_meeting(self.run)

    def test_saved_meeting_requires_exact_date_text_target_and_manual_review(self):
        self.globals();good=self.meeting_receipt()
        for field,value in [('meeting_date','2026-01-01'),('analysis','wrong body'),
                            ('url',good['readback']['url'].replace('Lcode=6','Lcode=99'))]:
            bad=copy.deepcopy(good);bad['readback'][field]=value
            with self.subTest(field=field), self.assertRaises(ValueError): self.save('meeting_resolved',bad)
        bad=copy.deepcopy(good);bad['review_checks']['support_alignment']=False
        with self.assertRaises(ValueError): self.save('meeting_resolved',bad)
        with self.assertRaises(ValueError): self.save('meeting_resolved',self.meeting_receipt('drafted'))

    def test_plan_change_blocks_build_and_registration_and_only_stales_affected_group(self):
        self.complete_fixture()
        path=self.run/MEETING_PATH;doc=read_json(path)
        doc['groups']['B']['needs']='New observed need';write_json(path,doc)
        result=status(self.run)
        self.assertEqual(result['stale_global'],['meeting_resolved'])
        self.assertEqual(result['stale_groups'],['B'])
        with self.assertRaises(ValueError): registration_check(self.run,'A')
        self.save('meeting_resolved',self.meeting_receipt())
        self.assertEqual(status(self.run)['stale_groups'],['B'])
        self.assertEqual(registration_check(self.run,'A')['group'],'A')
        with self.assertRaises(ValueError): registration_check(self.run,'B')
        self.assertEqual(next_step(self.run)['stage'],'inspect_changed_materials')

    def test_text_only_meeting_revision_preserves_group_reviews(self):
        self.complete_fixture();old=load_run(self.run)[2]['global']['meeting_resolved']['meeting_sha256']
        path=self.run/MEETING_PATH;doc=read_json(path);doc['analysis']+='\n문장 설명 보완';write_json(path,doc)
        self.assertEqual(status(self.run)['stale_groups'],[])
        self.assertEqual(status(self.run)['status'],'in_progress')
        self.save('meeting_resolved',self.meeting_receipt())
        self.assertEqual(status(self.run)['status'],'complete')
        history=load_run(self.run)[2]['history']
        self.assertTrue(any(e.get('previous',{}).get('meeting_sha256')==old for e in history))

    def test_new_roster_observation_invalidates_meeting(self):
        self.globals();path=self.run/'01_근거자료/평가대상.json';roster=read_json(path)
        roster['new_observation']='Recheck';write_json(path,roster)
        self.assertEqual(status(self.run)['stale_global'],['meeting_resolved'])
        with self.assertRaises(ValueError): material_plan(self.run,'A')

    def test_outdated_content_reference_and_missing_alignment_review_blocked(self):
        self.globals();folder=self.materials()
        data=read_json(folder/'content.json');data['support_plan_sha256']='0'*64;write_json(folder/'content.json',data)
        with self.assertRaises(ValueError): build_group(self.run,'A')
        with self.assertRaises(ValueError): package_group(self.run,'A')
        data['support_plan_sha256']=material_plan(self.run,'A')['support_plan_sha256'];write_json(folder/'content.json',data)
        with self.assertRaises(ValueError):
            self.save('materials_verified',{'pdf_page_count':2,**{k:True for k in ('local_checks','pdf_reviewed','visual_reviewed','sources_reviewed','privacy_reviewed')}},'A')
        self.review()
        self.assertEqual(registration_check(self.run,'A')['support_plan_sha256'],data['support_plan_sha256'])

    def test_legacy_history_readable_but_mutations_require_new_meeting(self):
        self.complete_fixture()
        job=read_json(self.run/'작업정보.json');job['evidence_version']=2;write_json(self.run/'작업정보.json',job)
        state=read_json(self.run/'진행상태.json')
        state['global']['meeting_resolved']={'mode':'existing','exact_readback':True,'reason':'legacy'}
        write_json(self.run/'진행상태.json',state)
        before=sha256(self.run/'진행상태.json')
        self.assertEqual(status(self.run)['status'],'complete')
        self.assertEqual(next_step(self.run)['stage'],'done')
        self.assertTrue(validate_group(self.run,'A')['ok'])
        self.assertEqual(before,sha256(self.run/'진행상태.json'))
        with self.assertRaises(ValueError): registration_check(self.run,'A')
        with self.assertRaises(ValueError): build_group(self.run,'A')
        self.save('meeting_resolved',self.meeting_receipt())
        self.assertEqual(registration_check(self.run,'A')['group'],'A')


if __name__ == '__main__':
    unittest.main()
