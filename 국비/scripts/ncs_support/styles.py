# Readability helpers extracted once from the completed support materials. No tmp dependency.

import xml.etree.ElementTree as ET

from xml.sax.saxutils import escape as xml_escape

def style_article(raw,group,labels):
    root=ET.fromstring('<root>'+raw+'</root>')
    styles={
     'p':'margin:0 0 18px;font-size:17px;line-height:1.95;word-break:keep-all;overflow-wrap:anywhere;color:#26364a;',
     'strong':'font-weight:700;color:#173a61;',
     'h2':'margin:52px 0 22px;padding:26px 0 14px;border-top:1px solid #dce5ef;border-bottom:2px solid #d5e3f2;font-size:25px;line-height:1.5;font-weight:700;color:#173a61;word-break:keep-all;',
     'h3':'margin:32px 0 14px;padding-left:12px;border-left:4px solid #7296bd;font-size:20px;line-height:1.6;font-weight:700;color:#244e7b;',
     'ul':'display:block;margin:18px 0 26px;padding:0 0 0 26px;list-style-position:outside;list-style-type:disc;',
     'li':'display:list-item;margin:0 0 10px;padding-left:4px;font-size:17px;line-height:1.9;color:#26364a;',
     'blockquote':'display:block;margin:26px 0 32px;padding:20px 24px;background-color:#edf6f1;border-left:4px solid #559479;border-radius:0 8px 8px 0;',
     'a':'color:#175fac;text-decoration:underline;font-weight:600;overflow-wrap:anywhere;',
     'img':'display:block;width:100%;max-width:900px;height:auto;margin:26px auto;border:1px solid #e1e8ef;border-radius:10px;',
    }
    for e in root.iter():
        if e.tag in styles:e.set('style',styles[e.tag])
    for li in root.iter('li'):
        for x in list(li):
            if x.tag=='p':x.set('style','margin:0;font-size:17px;line-height:1.9;')
    for block in root.iter('blockquote'):
        for x in list(block):
            if x.tag=='p':x.set('style','margin:0;font-size:17px;line-height:1.95;color:#25493c;word-break:keep-all;overflow-wrap:anywhere;')
    for t in root.iter('table'):
        t.set('style','width:100%;max-width:100%;border-collapse:collapse;table-layout:fixed;margin:22px 0 30px;font-size:16px;line-height:1.8;border:1px solid #cdd9e6;')
        for idx,tr in enumerate(t.iter('tr')):
            n=len(tr);widths=[25,75] if n==2 else ([22,39,39] if n==3 else [100/n]*n)
            for col,cell in enumerate(tr):
                header=cell.tag=='th';bg='#e9f0f8' if header else ('#fff' if idx%2 else '#f7f9fc')
                cell.set('style',f'padding:14px 16px;border:1px solid #d3dfeb;vertical-align:top;text-align:left;word-break:keep-all;overflow-wrap:anywhere;width:{widths[col]}%;background-color:{bg};color:#26364a;'+('font-weight:700;' if header else ''))
                for x in cell.iter('p'):x.set('style','margin:0;font-size:16px;line-height:1.8;word-break:keep-all;overflow-wrap:anywhere;')
    headings=list(root.iter('h2'))
    headings[0].set('style','margin:12px 0 18px;padding:0;border:0;font-size:32px;line-height:1.45;font-weight:700;letter-spacing:-0.7px;color:#173a61;word-break:keep-all;')
    for i,h in enumerate(headings[1:],1):h.set('id',group.lower()+'-learning-'+str(i))
    nav=ET.Element('div',{'style':'margin:0 0 42px;padding:22px 24px;background-color:#f8fafc;border:1px solid #dbe5f0;border-radius:10px;'})
    heading=ET.SubElement(nav,'p',{'style':'margin:0 0 14px;font-size:16px;font-weight:700;color:#254e7b;'});heading.text='학습 순서 바로가기'
    grid=ET.SubElement(nav,'div',{'style':'display:grid;grid-template-columns:1fr 1fr;gap:8px 20px;'})
    for i,label in enumerate(labels,1):
        a=ET.SubElement(grid,'a',{'href':'#'+group.lower()+'-learning-'+str(i),'style':'color:#245c94;text-decoration:underline;font-size:15px;line-height:1.9;'});a.text=f'{i:02d} '+label
    root.insert(3,nav)
    wrapper=ET.Element('div',{'style':'box-sizing:border-box;max-width:980px;margin:0 auto;padding:36px 32px 56px;background-color:#fff;font-family:Malgun Gothic,Apple SD Gothic Neo,sans-serif;font-size:17px;line-height:1.95;color:#26364a;'})
    for child in list(root):wrapper.append(child)
    return ET.tostring(wrapper,encoding='unicode',method='html')

def xp(text,bold=False,size=21):
    return '<w:p><w:pPr><w:spacing w:after="120"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Malgun Gothic" w:hAnsi="Malgun Gothic" w:eastAsia="맑은 고딕"/>'+('<w:b/>' if bold else '')+'<w:sz w:val="'+str(size)+'"/></w:rPr><w:t xml:space="preserve">'+xml_escape(text)+'</w:t></w:r></w:p>'

def xt(head,rows):
    n=len(head); widths=[int(9500/n)]*n
    grid='<w:tblGrid>'+''.join('<w:gridCol w:w="'+str(w)+'"/>' for w in widths)+'</w:tblGrid>'
    tr=[]
    for idx,row in enumerate([head]+rows):
        tr.append('<w:tr><w:trPr><w:trHeight w:val="'+('560' if idx==0 else '850')+'" w:hRule="atLeast"/><w:cantSplit/></w:trPr>'+''.join('<w:tc><w:tcPr><w:tcW w:w="'+str(widths[j])+'" w:type="dxa"/>'+('<w:shd w:fill="E9F0F8"/>' if idx==0 else '')+'</w:tcPr>'+xp(str(c),idx==0,19)+'</w:tc>' for j,c in enumerate(row))+'</w:tr>')
    return '<w:tbl><w:tblPr><w:tblW w:w="9500" w:type="dxa"/><w:tblBorders>'+''.join('<w:'+x+' w:val="single" w:sz="4" w:color="BACADA"/>' for x in ['top','left','bottom','right','insideH','insideV'])+'</w:tblBorders></w:tblPr>'+grid+''.join(tr)+'</w:tbl>'
