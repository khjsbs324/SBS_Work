from pathlib import Path
import json
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
root=Path(__file__).parent
for entry in json.loads((root/'runs.json').read_text(encoding='utf-8')):
    for group in 'ABC':
        folder=Path(entry['run'])/'03_지원자료'/(group+'그룹')
        path=folder/'실습양식.docx'
        doc=Document(path)
        doc.styles['Normal'].font.name='Malgun Gothic'
        doc.styles['Normal'].font.size=Pt(11)
        for table in doc.tables:
            table.autofit=False
            table.columns[0].width=Pt(180)
            table.columns[1].width=Pt(295)
            for row in table.rows:
                for i,cell in enumerate(row.cells):
                    cell.width=Pt(180 if i==0 else 295)
                    props=cell._tc.get_or_add_tcPr()
                    margins=OxmlElement('w:tcMar')
                    for side in ['top','left','bottom','right']:
                        el=OxmlElement('w:'+side);el.set(qn('w:w'),'100');el.set(qn('w:type'),'dxa');margins.append(el)
                    props.append(margins)
        doc.save(path)
        guide=folder/'guide.html'
        guide.write_text(guide.read_text(encoding='utf-8').replace('font-size:10.2pt;line-height:1.55','font-size:12pt;line-height:1.7').replace('font-size:9pt;line-height:1.5','font-size:10.5pt;line-height:1.6'),encoding='utf-8')
print('Normalized six DOCX packages and improved guide reading size')
