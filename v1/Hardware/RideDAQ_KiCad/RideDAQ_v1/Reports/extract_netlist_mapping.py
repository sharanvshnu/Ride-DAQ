from pathlib import Path
import re
s=Path('Reports/CAN_TLE9252V_netlist.net').read_text(encoding='utf-8')
lines=s.splitlines(); i=0
while i<len(lines):
 if lines[i].strip()=='(net':
  bal=0; block=[]
  while i<len(lines):
   line=lines[i]; block.append(line); bal+=line.count('(')-line.count(')'); i+=1
   if bal==0: break
  b='\n'.join(block); nm=re.search(r'\(name "([^"]+)"\)',b)
  if nm and (nm.group(1).startswith('/L3_Processing/') or nm.group(1).startswith('/L4_Sensing/') or nm.group(1) in ('VBAT_PT','+5V','+3V3')):
   nodes=[]
   for m in re.finditer(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)\s+\(pinfunction "([^"]+)"\)',b,re.S): nodes.append('/'.join(m.groups()))
   print(nm.group(1)+': '+'; '.join(nodes))
 else: i+=1
