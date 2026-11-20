from pathlib import Path
import re, shutil, uuid, subprocess, xml.etree.ElementTree as ET
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
BIN = Path(r"C:\Users\Sharan\AppData\Local\Programs\KiCad\10.0\bin")
KICAD_FP = Path(r"C:\Users\Sharan\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints")
SHEET = ROOT / "Sheets" / "L3_Processing.kicad_sch"
SYMLIB = ROOT / "Libraries" / "symbols" / "RideDAQ_CAN.kicad_sym"
FP_ROOT = ROOT / "Libraries" / "footprints"
CUSTOM_FP_DIR = FP_ROOT / "RideDAQ_CAN.pretty"
FP_NAME = "PG-TSON-14_3x4.5mm_P0.65mm_EP1.65x4.25mm"
FP_ID = f"RideDAQ_CAN:{FP_NAME}"

def replace_symbol_block(text, prefix, replacement):
    start = text.index(prefix)
    # Parent symbol is top level; count sexpr parentheses from opening position.
    depth = 0
    quoted = False
    escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if quoted:
            if escaped: escaped = False
            elif c == "\\": escaped = True
            elif c == '"': quoted = False
            continue
        if c == '"': quoted = True
        elif c == "(": depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[:start] + replacement + text[i+1:]
    raise ValueError(f"unterminated block: {prefix}")

# Preserve recoverable originals before editing.
for file in (SHEET, SYMLIB, ROOT / "fp-lib-table"):
    backup = file.with_suffix(file.suffix + ".pre_can_integration.bak")
    if not backup.exists(): shutil.copy2(file, backup)

# Use KiCad's 3 x 4.5 mm, 0.65 mm pitch exposed-pad footprint as a provisional geometric
# match. Its land dimensions originate from another device; the TLE9252VLC manufacturer
# recommended copper/paste pattern must be verified before fabrication.
CUSTOM_FP_DIR.mkdir(parents=True, exist_ok=True)
source_fp = KICAD_FP / "Package_DFN_QFN.pretty" / "DFN-14-1EP_3x4.5mm_P0.65mm_EP1.65x4.25mm.kicad_mod"
fp_text = source_fp.read_text(encoding="utf-8")
fp_text = fp_text.replace('"DFN-14-1EP_3x4.5mm_P0.65mm_EP1.65x4.25mm"', f'"{FP_NAME}"', 1)
fp_text = fp_text.replace('"14-lead very thin plastic quad flat, 3.0x4.5mm size, 0.65mm pitch (http://ww1.microchip.com/downloads/en/DeviceDoc/14L_VDFN_4_5x3_0mm_JHA_C041198A.pdf)"', '"PROVISIONAL TLE9252VLC PG-TSON-14 geometry match only; verify Infineon land pattern before fabrication"')
(CUSTOM_FP_DIR / f"{FP_NAME}.kicad_mod").write_text(fp_text, encoding="utf-8")

# Register the local footprint library in the project table.
table = ROOT / "fp-lib-table"
table_text = table.read_text(encoding="utf-8")
if '(name "RideDAQ_CAN")' not in table_text:
    table_text = table_text.replace("(fp_lib_table\n", '(fp_lib_table\n  (lib (name "RideDAQ_CAN")(type "KiCad")(uri "${KIPRJMOD}/Libraries/footprints/RideDAQ_CAN.pretty")(options "")(descr "Provisional CAN footprints; verify manufacturer land pattern"))\n', 1)
    table.write_text(table_text, encoding="utf-8")

# Assign a package-matched provisional footprint to the placed transceiver symbol.
sheet_text = SHEET.read_text(encoding="utf-8")
# Assign transceiver footprint on the placed symbol instance.
inst = sheet_text.index('(lib_id "RideDAQ_CAN:TLE9252VLC")')
prop = sheet_text.index('(property "Footprint"', inst)
prop_end = sheet_text.index(')', prop)
prop_text = sheet_text[prop:prop_end]
if f'"{FP_ID}"' not in prop_text:
    sheet_text = sheet_text[:prop] + sheet_text[prop:].replace('(property "Footprint" ""', f'(property "Footprint" "{FP_ID}"', 1)
SHEET.write_text(sheet_text, encoding="utf-8")

# Export the current schematic netlist and create a separate integrated PCB copy.
net_xml = ROOT / "Reports" / "RideDAQ_CAN_integrated.xml"
subprocess.run([str(BIN / "kicad-cli.exe"), "sch", "export", "netlist", "--format", "kicadxml", "-o", str(net_xml), str(ROOT / "RideDAQ_v1.kicad_sch")], check=True)
root = ET.parse(net_xml).getroot()
components = {c.attrib["ref"]: c for c in root.findall("./components/comp")}
targets = ["U8", "J7", "C22", "C23", "R25"]
for ref in targets:
    fp = components[ref].findtext("footprint", "")
    if ref == "U8": fp = FP_ID
    if not fp: raise ValueError(f"Missing footprint for {ref}")
    lib, name = fp.split(":", 1)
    fpfile = FP_ROOT / f"{lib}.pretty" / f"{name}.kicad_mod"
    if not fpfile.exists():
        fpfile = KICAD_FP / f"{lib}.pretty" / f"{name}.kicad_mod"
    if not fpfile.exists(): raise FileNotFoundError(f"footprint unavailable: {fpfile}")

board = pcbnew.LoadBoard(str(ROOT / "RideDAQ_v1.kicad_pcb"))
out_board = ROOT / "RideDAQ_v1_CAN_Integrated.kicad_pcb"

# Extend only the lower edge by 11 mm for a CAN placement study; preserve the clipped board shape.
for drawing in board.GetDrawings():
    if drawing.GetLayer() != pcbnew.Edge_Cuts: continue
    a, b = drawing.GetStart(), drawing.GetEnd()
    ay, by = a.y / 1e6, b.y / 1e6
    if abs(ay - 99.025) < 0.02: a.y += pcbnew.FromMM(11); b.y += pcbnew.FromMM(11)
    elif abs(ay - 94.0) < 0.02 and abs(by - 99.025) < 0.02: a.y += pcbnew.FromMM(11); b.y += pcbnew.FromMM(11)
    elif abs(by - 94.0) < 0.02 and abs(ay - 99.025) < 0.02: a.y += pcbnew.FromMM(11); b.y += pcbnew.FromMM(11)
    elif abs(ay - 94.0) < 0.02 and abs(by - 43.95) < 0.02: a.y += pcbnew.FromMM(11)
    elif abs(by - 94.0) < 0.02 and abs(ay - 43.95) < 0.02: b.y += pcbnew.FromMM(11)
    drawing.SetStart(a); drawing.SetEnd(b)

# Move lower mounting holes with the extended edge to preserve approximately 6 mm edge margin.
for f in board.GetFootprints():
    if f.GetReference() in ("H1", "H4"):
        p = f.GetPosition(); p.y += pcbnew.FromMM(11); f.SetPosition(p)

# Pull the XML net membership for each new reference/pad.
pad_nets = {}
net_names = set()
for n in root.findall("./nets/net"):
    name = n.attrib["name"]
    for node in n.findall("node"):
        if node.attrib.get("ref") in targets:
            pad_nets[(node.attrib["ref"], node.attrib["pin"]) ] = name
            net_names.add(name)
next_code = max([int(n.GetNetCode()) for n in board.GetNetInfo().NetsByName().values()] + [0]) + 1
for name in sorted(net_names):
    if board.FindNet(name) is None:
        net = pcbnew.NETINFO_ITEM(board, name, next_code); board.Add(net); next_code += 1

placements = {
    "U8": (139.0, 104.0, 0),
    "C22": (134.0, 105.5, 90),
    "C23": (143.0, 105.5, 90),
    "R25": (124.5, 106.5, 0),
    "J7": (162.0, 104.0, 180),
}
existing = {f.GetReference(): f for f in board.GetFootprints()}
for ref in targets:
    comp = components[ref]
    fp = FP_ID if ref == "U8" else comp.findtext("footprint")
    lib, name = fp.split(":", 1)
    path = FP_ROOT / f"{lib}.pretty" / f"{name}.kicad_mod"
    if not path.exists(): path = KICAD_FP / f"{lib}.pretty" / f"{name}.kicad_mod"
    footprint = pcbnew.FootprintLoad(str(path.parent), name)
    if footprint is None: raise RuntimeError(f"Could not load {fp}")
    footprint.SetReference(ref)
    footprint.SetValue(comp.findtext("value", ref))
    footprint.SetFPID(pcbnew.LIB_ID(lib, name))
    x, y, angle = placements[ref]
    footprint.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    footprint.SetOrientationDegrees(angle)
    if ref in ("J7", "C23"): footprint.Reference().SetVisible(False)
    board.Add(footprint)
    existing[ref] = footprint

for ref in targets:
    footprint = existing[ref]
    for pad in footprint.Pads():
        name = pad_nets.get((ref, pad.GetNumber()))
        if ref == "U8" and pad.GetNumber() == "15": name = "GND"
        if name:
            net = board.FindNet(name)
            if net is None: raise RuntimeError(f"Net missing: {name}")
            pad.SetNet(net)

pcbnew.SaveBoard(str(out_board), board)
print(f"Created {out_board}")
print(f"Added {len(targets)} CAN footprints; lower outline extended 11 mm; project outline now about 69.6 x 71.1 mm")
print("U8 footprint is explicitly provisional pending manufacturer land-pattern verification.")
