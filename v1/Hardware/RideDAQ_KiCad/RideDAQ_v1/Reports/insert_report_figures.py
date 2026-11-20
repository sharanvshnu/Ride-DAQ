from docx import Document
from docx.shared import Inches, Pt, RGBColor
from pathlib import Path
p=Path('Reports/RideDAQ_PreStage_Work_Report.docx')
doc=Document(p)
arch=next(t for t in doc.tables if t.rows and t.rows[0].cells[0].text.strip()=='Layer')
imgp=doc.add_paragraph(); imgp.alignment=1; imgp.paragraph_format.space_after=Pt(1); imgp.add_run().add_picture('Reports/RideDAQ_Report_QA/RideDAQ_system_architecture.png',width=Inches(7.0))
cap=doc.add_paragraph(); cap.alignment=1; cap.paragraph_format.space_after=Pt(3); r=cap.add_run('Figure 1. RideDAQ hardware and data-path architecture.'); r.italic=True; r.font.size=Pt(8); r.font.color.rgb=RGBColor(95,114,128)
arch._tbl.addprevious(imgp._p); arch._tbl.addprevious(cap._p); arch._tbl.getparent().remove(arch._tbl)
paras=doc.paragraphs
start=next(i for i,x in enumerate(paras) if x.text.strip()=='8. End-to-end workflow')
end=next(i for i,x in enumerate(paras) if x.text.strip()=='8.1 Operating-state story')
numbered=[x for x in paras[start+1:end] if x.style and x.style.name=='List Number']
for x in numbered: x._p.getparent().remove(x._p)
endp=next(x for x in doc.paragraphs if x.text.strip()=='8.1 Operating-state story')
wf=doc.add_paragraph(); wf.alignment=1; wf.paragraph_format.space_before=Pt(1); wf.paragraph_format.space_after=Pt(1); wf.add_run().add_picture('Reports/RideDAQ_Report_QA/RideDAQ_workflow.png',width=Inches(7.0))
wcap=doc.add_paragraph(); wcap.alignment=1; wcap.paragraph_format.space_after=Pt(3); rr=wcap.add_run('Figure 2. Proposed acquisition and data-handling workflow.'); rr.italic=True; rr.font.size=Pt(8); rr.font.color.rgb=RGBColor(95,114,128)
endp._p.addprevious(wf._p); endp._p.addprevious(wcap._p)
doc.save(p)
print('Inserted two figures and replaced the architecture table and numbered workflow.')
