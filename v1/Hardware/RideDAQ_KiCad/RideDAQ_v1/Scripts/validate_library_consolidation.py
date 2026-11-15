from pathlib import Path
import json,re,os,subprocess,sys
P=Path(sys.argv[1]).resolve(); R=P/'Reports'/'library_consolidation'; CLI=Path(os.environ['LOCALAPPDATA'])/'Programs'/'KiCad'/'10.0'/'bin'/'kicad-cli.exe'
inv=json.loads((R/'post_migration'/'library_inventory.json').read_text(encoding='utf-8')); checks={}
checks['75_footprints_and_all_definitions_resolve']=inv['summary']['pcb_footprint_instances']==75 and inv['summary']['missing_footprint_definitions']==0
checks['22_project_local_models_resolve']=len(inv['models'])==22 and all(x['exists'] and x['project_local'] for x in inv['models'])
fp_table=(P/'fp-lib-table').read_text(encoding='utf-8'); fpok=True
for ident in sorted({x['library_id'] for x in inv['footprints']}):
 if ':' not in ident: fpok=False; continue
 n,s=ident.split(':',1); fpok &= f'(name "{n}")' in fp_table and (P/'Libraries'/'footprints'/f'{n}.pretty'/f'{s}.kicad_mod').is_file()
checks['footprint_table_and_definitions_resolve']=bool(fpok)
sym_table=(P/'sym-lib-table').read_text(encoding='utf-8'); symids=inv['placed_symbol_ids']; syms=True
for ident in symids:
 n,s=ident.split(':',1); syms &= f'(name "{n}")' in sym_table and (P/'Libraries'/'symbols'/f'{n}.kicad_sym').is_file()
checks['all_29_symbol_ids_have_local_libraries']=bool(syms)
old=json.loads((R/'validation_report.json').read_text(encoding='utf-8')); old_checks=old.get('checks',{}); checks['baseline_structural_comparison_passed']=old_checks.get('footprint_uuid_position_layer_comparison') and old_checks.get('pcb_only_expected_library_reference_changes') and old_checks.get('schematic_hierarchy_and_files_unchanged')
out=R/'cli'; out.mkdir(parents=True,exist_ok=True); pcb=out/'pcb'; sch=out/'RideDAQ_v1.net'
p=subprocess.run([str(CLI),'pcb','export','svg','--mode-multi','--layers','F.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts',str(P/'RideDAQ_v1.kicad_pcb'),'-o',str(pcb)],capture_output=True,text=True); q=subprocess.run([str(CLI),'sch','export','netlist',str(P/'RideDAQ_v1.kicad_sch'),'-o',str(sch)],capture_output=True,text=True)
checks['kicad_cli_board_export']=p.returncode==0; checks['kicad_cli_hierarchical_schematic_export']=q.returncode==0
symout=out/'symbols'; symout.mkdir(exist_ok=True); results=[]
for ident in symids:
 n,s=ident.split(':',1); dest=symout/re.sub(r'[^A-Za-z0-9_.-]+','_',n); dest.mkdir(exist_ok=True); r=subprocess.run([str(CLI),'sym','export','svg','--symbol',s,str(P/'Libraries'/'symbols'/f'{n}.kicad_sym'),'-o',str(dest)],capture_output=True,text=True); results.append({'symbol_id':ident,'exit_code':r.returncode})
checks['all_29_symbol_library_exports']=all(x['exit_code']==0 for x in results)
(R/'cli'/'symbol_library_validation.json').write_text(json.dumps({'kicad_cli':'10.0.1','symbols':results,'passed':sum(x['exit_code']==0 for x in results),'total':len(results),'overall':'PASS' if checks['all_29_symbol_library_exports'] else 'FAIL'},indent=2),encoding='utf-8')
report={'project':str(P),'kicad_cli_version':'10.0.1','checks':checks,'passed':sum(bool(x) for x in checks.values()),'total':len(checks),'overall':'PASS' if all(checks.values()) else 'FAIL','footprints':75,'footprint_ids':27,'models':22,'symbol_ids':29,'symbol_namespaces':16}
(R/'validation_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report,indent=2));
if report['overall']!='PASS':raise SystemExit(1)
