from zipfile import ZipFile
from pathlib import Path
from lxml import etree
p=Path('Reports/RideDAQ_PreStage_Work_Report.docx')
with ZipFile(p) as z:
 root=etree.fromstring(z.read('word/document.xml'))
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
 print('manual breaks:',len(root.xpath('.//w:br[@w:type="page"]',namespaces=ns)))
 print('inline images:',len(root.xpath('.//a:blip',namespaces=ns)))
 print('tables:',len(root.xpath('.//w:tbl',namespaces=ns)))
 print('file bytes:',p.stat().st_size)
