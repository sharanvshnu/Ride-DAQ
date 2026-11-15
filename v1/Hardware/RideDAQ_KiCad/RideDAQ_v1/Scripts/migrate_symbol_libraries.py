from pathlib import Path
import os,re,json,stat,sys
P=Path(sys.argv[1]).resolve(); share=Path(os.environ.get('KICAD10_SYMBOL_DIR',str(Path(os.environ['LOCALAPPDATA'])/'Programs'/'KiCad'/'10.0'/'share'/'kicad'/'symbols')))
invpaths=[P/'Reports'/'library_consolidation'/'post_migration'/'library_inventory.json',P/'Reports'/'library_inventory.json',P/'Reports'/'baseline'/'library_inventory.json']; inv=next((json.loads(f.read_text(encoding='utf-8')) for f in invpaths if f.is_file()),None)
if inv is None: raise SystemExit('No library inventory found')
by={}
for item in inv['placed_symbol_ids']:
 nick,name=item.split(':',1); by.setdefault(nick,set()).add(name)
def extract(s,start):
 depth=0; quoted=False; escaped=False
 for i in range(start,len(s)):
  c=s[i]
  if quoted:
   if escaped: escaped=False
   elif c=='\\': escaped=True
   elif c=='"': quoted=False
  elif c=='"': quoted=True
  elif c=='(': depth+=1
  elif c==')':
   depth-=1
   if depth==0:return s[start:i+1]
 raise ValueError('Unclosed symbol form')
def get_symbol(source,name):
 m=re.search(r'\(symbol\s+"'+re.escape(name)+r'"(?=\s|\))',source)
 if not m: raise RuntimeError(f'Symbol not found in source library: {name}')
 return extract(source,m.start())
custom={'Buck IC','RideDAQ_v1','teensy_master'}; out=P/'Libraries'/'symbols'; out.mkdir(parents=True,exist_ok=True)
for nick,names in by.items():
 if nick in custom:
  if not (out/f'{nick}.kicad_sym').is_file(): raise FileNotFoundError(f'Custom symbol definitions missing: {nick}')
  continue
 source=(share/f'{nick}.kicad_sym').read_text(encoding='utf-8'); found={}; order=[]
 def add(name):
  if name in found:return
  f=get_symbol(source,name)
  for parent in re.findall(r'\(extends\s+"([^"]+)"',f):add(parent)
  found[name]=f;order.append(name)
 for name in sorted(names):add(name)
 dst=out/f'{nick}.kicad_sym'
 if dst.exists():dst.chmod(stat.S_IREAD|stat.S_IWRITE)
 dst.write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n'+'\n'.join(found[n] for n in order)+'\n)\n',encoding='utf-8');dst.chmod(stat.S_IREAD|stat.S_IWRITE)
lines=['(sym_lib_table']
for nick in sorted(by):lines.append(f'  (lib (name "{nick}")(type "KiCad")(uri "${{KIPRJMOD}}/Libraries/symbols/{nick}.kicad_sym")(options "")(descr "RideDAQ project-local symbol library"))')
lines.append(')');(P/'sym-lib-table').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Generated local libraries for {sum(len(v) for v in by.values())} active symbol IDs')
