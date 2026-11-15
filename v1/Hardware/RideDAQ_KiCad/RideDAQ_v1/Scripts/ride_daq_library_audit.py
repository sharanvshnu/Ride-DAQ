#!/usr/bin/env python3
"""Read-only RideDAQ KiCad dependency audit. Python 3.10+, standard library only.

Run:
  py ride_daq_library_audit.py --project "C:\\path\\to\\RideDAQ_v1"

Creates Reports/library_inventory.json, Reports/library_inventory.csv and
Reports/pcb_placement_snapshot.json. Does not modify KiCad design files.
"""
from __future__ import annotations
import argparse, csv, json, os, re, sys
from pathlib import Path

def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")

def unique_sorted(values):
    return sorted(set(values), key=str.casefold)

def env_path(value, project):
    expanded = value.replace("${KIPRJMOD}", str(project))
    for key, val in os.environ.items():
        expanded = expanded.replace("${" + key + "}", val)
    if "${" in expanded:
        return None
    return Path(expanded)

def locate_footprint(lib_id, project, fp_root):
    if ":" not in lib_id:
        return None
    nickname, name = lib_id.split(":", 1)
    candidates = [
        project / "Libraries" / "footprints" / f"{nickname}.pretty" / f"{name}.kicad_mod",
        project / "Libraries" / "Footprints" / f"{nickname}.pretty" / f"{name}.kicad_mod",
    ]
    if fp_root:
        candidates.append(fp_root / f"{nickname}.pretty" / f"{name}.kicad_mod")
    return next((p for p in candidates if p.is_file()), None)

def main():
    ap = argparse.ArgumentParser(description="Read-only RideDAQ KiCad library audit")
    ap.add_argument("--project", required=True, help="Directory containing RideDAQ_v1.kicad_pro")
    ap.add_argument("--out", default="Reports", help="Report directory")
    args = ap.parse_args()
    project = Path(args.project).expanduser().resolve()
    for filename in ("RideDAQ_v1.kicad_pro", "RideDAQ_v1.kicad_pcb"):
        if not (project / filename).is_file():
            print(f"ERROR: {filename} not found in {project}", file=sys.stderr)
            return 2

    fp_env = os.environ.get("KICAD10_FOOTPRINT_DIR") or os.environ.get("KICAD9_FOOTPRINT_DIR")
    model_env = os.environ.get("KICAD10_3DMODEL_DIR") or os.environ.get("KICAD9_3DMODEL_DIR")
    fp_root = Path(fp_env) if fp_env else None
    pcb = read_text(project / "RideDAQ_v1.kicad_pcb")

    starts = [m.start() for m in re.finditer(r'\(footprint\s+"([^"]+)"', pcb)]
    footprints = []
    for i, start in enumerate(starts):
        block = pcb[start:starts[i + 1] if i + 1 < len(starts) else len(pcb)]
        lib_match = re.search(r'\(footprint\s+"([^"]+)"', block)
        at_match = re.search(r'\(at\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)(?:\s+([-+0-9.eE]+))?', block)
        ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        uuid_match = re.search(r'\(uuid\s+"([^"]+)"', block)
        layer_match = re.search(r'\(layer\s+"([^"]+)"', block)
        lib_id = lib_match.group(1) if lib_match else ""
        fp_file = locate_footprint(lib_id, project, fp_root)
        footprints.append({
            "reference": ref_match.group(1) if ref_match else "",
            "library_id": lib_id,
            "x_mm": float(at_match.group(1)) if at_match else None,
            "y_mm": float(at_match.group(2)) if at_match else None,
            "rotation_deg": float(at_match.group(3) or 0) if at_match else 0,
            "side": layer_match.group(1) if layer_match else "",
            "uuid": uuid_match.group(1) if uuid_match else "",
            "definition_found": bool(fp_file),
            "definition_path": str(fp_file) if fp_file else "",
        })

    model_refs = unique_sorted(re.findall(r'\(model\s+"([^"]+)"', pcb))
    models = []
    for ref in model_refs:
        resolved = env_path(ref, project)
        models.append({
            "reference_path": ref,
            "resolved_path": str(resolved) if resolved else "",
            "exists": bool(resolved and resolved.is_file()),
            "project_local": ref.startswith("${KIPRJMOD}"),
        })

    sch_files = []
    root_sch = project / "RideDAQ_v1.kicad_sch"
    if root_sch.is_file():
        sch_files.append(root_sch)
    sheets_dir = project / "Sheets"
    if sheets_dir.is_dir():
        sch_files.extend(sorted(sheets_dir.glob("*.kicad_sch")))

    symbol_ids, embedded_symbols, schematic_report = set(), set(), []
    for sch_path in sch_files:
        text = read_text(sch_path)
        ids = unique_sorted(re.findall(r'\(lib_id\s+"([^"]+)"', text))
        embedded = unique_sorted(re.findall(r'\(symbol\s+"([^"]+)"', text))
        symbol_ids.update(ids)
        embedded_symbols.update(embedded)
        schematic_report.append({
            "file": str(sch_path.relative_to(project)),
            "placed_symbol_ids": ids,
            "embedded_symbol_names_seen": embedded,
        })

    placement = sorted(footprints, key=lambda x: (x["reference"], x["uuid"]))
    out_dir = (project / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    inventory = {
        "project": str(project),
        "read_only": True,
        "environment": {
            "footprint_library_root": str(fp_root) if fp_root else "",
            "model_library_root": model_env or "",
            "KICAD10_FOOTPRINT_DIR_set": bool(fp_root),
            "KICAD10_3DMODEL_DIR_set": bool(model_env),
        },
        "summary": {
            "pcb_footprint_instances": len(footprints),
            "unique_footprint_ids": len({x["library_id"] for x in footprints}),
            "missing_footprint_definitions": sum(not x["definition_found"] for x in footprints),
            "unique_3d_model_references": len(models),
            "missing_3d_models": sum(not x["exists"] for x in models),
            "placed_symbol_ids": len(symbol_ids),
            "embedded_symbol_names_seen": len(embedded_symbols),
        },
        "footprints": footprints,
        "models": models,
        "placed_symbol_ids": sorted(symbol_ids),
        "embedded_symbol_names_seen": sorted(embedded_symbols),
        "schematics": schematic_report,
    }
    (out_dir / "library_inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    with (out_dir / "library_inventory.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "reference", "library_id", "x_mm", "y_mm", "rotation_deg",
            "side", "uuid", "definition_found", "definition_path"
        ])
        writer.writeheader()
        writer.writerows(footprints)
    (out_dir / "pcb_placement_snapshot.json").write_text(json.dumps(placement, indent=2), encoding="utf-8")
    print(json.dumps(inventory["summary"], indent=2))
    print(f"Reports written to: {out_dir}")
    print("No KiCad project files were modified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
