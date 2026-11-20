from docx import Document
p='Reports/RideDAQ_PreStage_Work_Report_Updated.docx'
d=Document(p)
print('paragraphs',len(d.paragraphs),'tables',len(d.tables))
print('page_breaks',sum(len(x._p.xpath('.//w:br[@w:type="page"]')) for x in d.paragraphs))
print('pictures',sum(len(x._p.xpath('.//w:drawing')) for x in d.paragraphs))
print('captions',[x.text for x in d.paragraphs if x.text.startswith('Figure')])
print('table_heads',[t.rows[0].cells[0].text for t in d.tables])
