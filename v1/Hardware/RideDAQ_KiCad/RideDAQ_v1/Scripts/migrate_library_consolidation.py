from pathlib import Path
import os,re,json,shutil,hashlib,sys
P=Path(sys.argv[1]).resolve()
_done_paths=[P/'Reports'/'validation_report.json',P/'Reports'/'library_consolidation'/'validation_report.json']
if any(f.is_file() and json.loads(f.read_text(encoding='utf-8')).get('overall')=='PASS' for f in _done_paths):
 print('Validated library consolidation already exists; no changes made.')
 raise SystemExit(0)
K=Path(os.environ.get('LOCALAPPDATA',r'C:\Users\Sharan\AppData\Local'))/'Programs'/'KiCad'/'10.0'/'share'/'kicad'
FP=K/'footprints'; MD=K/'3dmodels'
pcb=P/'RideDAQ_v1.kicad_pcb'; before=pcb.read_text(encoding='utf-8'); initial=before
inv=json.loads((P/'Reports'/'baseline'/'library_inventory.json').read_text(encoding='utf-8'))
# Snapshot active geometry and identity before changing references.
def blocks(text,pattern):
 ms=list(re.finditer(pattern,text)); return [(m.start(),ms[i+1].start() if i+1<len(ms) else len(text),m.group(1)) for i,m in enumerate(ms)]
fpblocks=blocks(before,r'\(footprint\s+"([^"]+)"')
placements=[]
for a,b,n in fpblocks:
 s=before[a:b]
 placements.append({'reference':(re.search(r'\(property\s+"Reference"\s+"([^"]*)"',s) or [None,''])[1], 'uuid':(re.search(r'\(uuid\s+"([^"]+)"',s) or [None,''])[1], 'at':(re.search(r'\(at\s+([^\)]+)',s) or [None,''])[1], 'layer':(re.search(r'\(layer\s+"([^"]+)"',s) or [None,''])[1], 'name':n})
modelrefs=sorted(set(re.findall(r'\(model\s+"([^"]+)"',before)))
# Create reversible copy of exact project state before migration.
bak=P/'Backups'/'pre-library-consolidation'; bak.mkdir(parents=True,exist_ok=True)
for n in ['RideDAQ_v1.kicad_pcb','RideDAQ_v1.kicad_pro','RideDAQ_v1.kicad_sch','Sheets','Libraries']:
 src=P/n; dst=bak/n
 if src.is_dir():
  if not dst.exists(): shutil.copytree(src,dst)
 elif src.exists() and not dst.exists(): shutil.copy2(src,dst)
# Resolve and copy ordinary footprint definitions, retaining nicknames and exact bytes.
fp_root=P/'Libraries'/'footprints'; fp_root.mkdir(parents=True,exist_ok=True)
ids=sorted(set(x['library_id'] for x in inv['footprints'] if ':' in x['library_id']))
fp_paths={}
for libid in ids:
 nick,name=libid.split(':',1)
 local=fp_root/f'{nick}.pretty'/f'{name}.kicad_mod'
 if local.is_file(): src=local
 else:
  src=FP/f'{nick}.pretty'/f'{name}.kicad_mod'
 if not src.is_file(): raise FileNotFoundError(f'Footprint source missing for {libid}: {src}')
 local.parent.mkdir(parents=True,exist_ok=True)
 if local.exists() and local.read_bytes()!=src.read_bytes(): raise RuntimeError(f'Footprint overwrite conflict: {local}')
 if not local.exists(): shutil.copy2(src,local)
 fp_paths[libid]=str(local.relative_to(P))
# Preserve both distinct embedded LOGO graphics as separately named local library items.
logo_names=[]
for idx,(a,b,n) in enumerate(fpblocks):
 if n!='LOGO': continue
 name=f'RideDAQ_Logo_{idx+1}'
 dest=fp_root/'RideDAQ_Graphics.pretty'/f'{name}.kicad_mod'; dest.parent.mkdir(parents=True,exist_ok=True)
 # Local library definition uses the original complete footprint geometry and properties.
 block=before[a:b].strip()
 block=re.sub(r'^\(footprint\s+"LOGO"','(footprint "'+name+'"',block,count=1)
 if dest.exists() and dest.read_text(encoding='utf-8')!=block+'\n': raise RuntimeError(f'Logo overwrite conflict: {dest}')
 if not dest.exists(): dest.write_text(block+'\n',encoding='utf-8')
 logo_names.append(name)
# Copy all referenced models into local storage, preserving source subdirectories and transforms.
modelroot=P/'Libraries'/'3dmodels'; modelroot.mkdir(parents=True,exist_ok=True)
model_map={}
for ref in modelrefs:
 if ref.startswith('${KIPRJMOD}/'):
  src=(P/ref.replace('${KIPRJMOD}/','').replace('/',os.sep)).resolve()
 else:
  rel=ref.replace('${KICAD10_3DMODEL_DIR}/','').replace('${KICAD9_3DMODEL_DIR}/','')
  src=(MD/Path(rel.replace('/',os.sep))).resolve()
 if not src.is_file(): raise FileNotFoundError(f'Model source missing: {ref} -> {src}')
 try: relpath=src.relative_to(MD.resolve())
 except ValueError: relpath=Path('custom')/src.name
 dest=modelroot/relpath
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists() and dest.read_bytes()!=src.read_bytes(): raise RuntimeError(f'Model overwrite conflict: {dest}')
 if not dest.exists(): shutil.copy2(src,dest)
 new='${KIPRJMOD}/Libraries/3dmodels/'+relpath.as_posix()
 model_map[ref]=new
# Update only model paths and the two LOGO library item names; preserve all geometry/identity data.
for old,new in model_map.items(): before=before.replace('"'+old+'"','"'+new+'"')
for name in logo_names:
 # Exact footprint declarations only; embedded geometry remains byte-identical.
 before=before.replace('(footprint "LOGO"','(footprint "'+name+'"',1)
pcb.write_text(before,encoding='utf-8')
# Create deterministic project-local footprint table.
lines=['(fp_lib_table']
for nick in sorted({Path(v).parent.name[:-7] for v in fp_paths.values()}|{'RideDAQ_Graphics'}):
 lines.append(f'  (lib (name "{nick}")(type "KiCad")(uri "${{KIPRJMOD}}/Libraries/footprints/{nick}.pretty")(options "")(descr "RideDAQ project-local footprints"))')
lines.append(')')
(P/'fp-lib-table').write_text('\n'.join(lines)+'\n',encoding='utf-8')
# Symbol definitions are embedded in each schematic; register the supplied custom library locally.
(P/'sym-lib-table').write_text('(sym_lib_table\n  (lib (name "RideDAQ_HM10")(type "KiCad")(uri "${KIPRJMOD}/Libraries/symbols/RideDAQ_HM10.kicad_sym")(options "")(descr "RideDAQ HM10 module symbol"))\n)\n',encoding='utf-8')
# Snapshot comparison and report.
after=pcb.read_text(encoding='utf-8')
placements_after=[]
for a,b,n in blocks(after,r'\(footprint\s+"([^"]+)"'):
 s=after[a:b]; placements_after.append({'reference':(re.search(r'\(property\s+"Reference"\s+"([^"]*)"',s) or [None,''])[1], 'uuid':(re.search(r'\(uuid\s+"([^"]+)"',s) or [None,''])[1], 'at':(re.search(r'\(at\s+([^\)]+)',s) or [None,''])[1], 'layer':(re.search(r'\(layer\s+"([^"]+)"',s) or [None,''])[1], 'name':n})
if len(placements)!=len(placements_after): raise RuntimeError('Footprint count changed')
for x,y in zip(placements,placements_after):
 for k in ['reference','uuid','at','layer']:
  if x[k]!=y[k]: raise RuntimeError(f'PCB structural change: {k} {x} != {y}')
# Each board file is changed only by explicitly mapped path/name references.
canon_before=initial
for old,new in model_map.items(): canon_before=canon_before.replace('"'+old+'"','"'+new+'"')
for name in logo_names: canon_before=canon_before.replace('(footprint "LOGO"','(footprint "'+name+'"',1)
if canon_before!=after: raise RuntimeError('Unexpected PCB text changes outside approved reference updates')
report={'status':'migration_complete_pending_cli_validation','project':str(P),'footprints_copied':len(fp_paths),'footprint_ids':ids,'logo_graphics_preserved_as':logo_names,'models_copied':len(model_map),'model_paths':model_map,'pcb_footprint_count':len(placements),'placement_uuid_reference_position_layer_comparison':'PASS','pcb_change_scope_comparison':'PASS','schematics_modified':False,'rollback_backup':str(bak.relative_to(P)),'symbol_strategy':'schematic symbol definitions remain embedded; local table registers supplied HM10 source library'}
(P/'Reports'/'migration_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
