"""Integrate the RideDAQ CAN-FD circuit and Teensy 4.0 footprint locally.

Uses KiCad's S-expression files directly so the change can be reviewed in Git.
Run from the project root with KiCad closed.
"""
from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KICAD = Path(r"C:\Users\Sharan\AppData\Local\Programs\KiCad\10.0\share\kicad")


def uid() -> str:
    return str(uuid.uuid4())


def balanced_block(source: str, start: int) -> tuple[str, int]:
    """Return the balanced S-expression beginning at start and end position."""
    depth = 0
    quoted = escaped = False
    for i in range(start, len(source)):
        c = source[i]
        if quoted:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return source[start:i + 1], i + 1
    raise ValueError("Unbalanced S-expression")


def named_symbol(path: Path, name: str) -> str:
    source = path.read_text(encoding="utf-8")
    marker = f'\t(symbol "{name}"'
    pos = source.find(marker)
    if pos < 0:
        raise ValueError(f"Symbol {name} not found in {path}")
    start = source.find("(symbol", pos)
    return balanced_block(source, start)[0]


def prop(name: str, value: str, x: float, y: float, hide: bool = False) -> str:
    h = "\n\t\t\t(hide yes)" if hide else ""
    return (f'\t(property "{name}" "{value}"\n'
            f'\t\t(at {x:g} {y:g} 0){h}\n'
            f'\t\t(effects (font (size 1.27 1.27)))\n\t)')


def component(lib_id: str, ref: str, value: str, x: float, y: float,
              footprint: str, pin_numbers: list[str], page_path: str,
              datasheet: str = "", dnp: bool = False,
              description: str = "") -> str:
    visible = f"\t(property \"Reference\" \"{ref}\"\n\t\t(at {x:g} {y-13:g} 0)\n\t\t(effects (font (size 1.27 1.27)))\n\t)\n"
    visible += f"\t(property \"Value\" \"{value}\"\n\t\t(at {x:g} {y-10.5:g} 0)\n\t\t(effects (font (size 1.27 1.27)))\n\t)\n"
    hidden = prop("Footprint", footprint, x, y, True) + "\n"
    hidden += prop("Datasheet", datasheet, x, y, True) + "\n"
    hidden += prop("Description", description, x, y, True) + "\n"
    pins = "\n".join(f'\t(pin "{n}" (uuid "{uid()}"))' for n in pin_numbers)
    return (f'\n(symbol\n\t(lib_id "{lib_id}")\n\t(at {x:g} {y:g} 0)\n'
            f'\t(unit 1)\n\t(exclude_from_sim no)\n\t(in_bom yes)\n'
            f'\t(on_board yes)\n\t(dnp {"yes" if dnp else "no"})\n'
            f'\t(fields_autoplaced yes)\n\t(uuid "{uid()}")\n'
            f'{visible}{hidden}{pins}\n'
            f'\t(instances\n\t\t(project "RideDAQ_v1"\n'
            f'\t\t\t(path "{page_path}" (reference "{ref}") (unit 1))\n'
            f'\t\t)\n\t)\n)\n')


def label(name: str, x: float, y: float, angle: int = 0) -> str:
    justify = "right" if angle == 180 else "left"
    return (f'\n(label "{name}" (at {x:g} {y:g} {angle})\n'
            f'\t(effects (font (size 1.27 1.27)) (justify {justify} bottom))\n'
            f'\t(uuid "{uid()}")\n)\n')


def insert_lib_symbol(schematic: str, block: str) -> str:
    # Insert before the closing paren of the top-level lib_symbols section.
    start = schematic.find("(", schematic.index("\t(lib_symbols"))
    _, end = balanced_block(schematic, start)
    return schematic[:end - 1] + "\n" + block + "\n\t" + schematic[end - 1:]


def make_teensy_footprint() -> str:
    # PJRC Teensy 4.0 has the Teensy 3.2 outline. Pads 1-34 are the main
    # through-hole header rows; pads 35-54 are underside SMT contacts.
    pads: list[str] = []
    top = [(-16.51 + 2.54 * i, 7.62) for i in range(14)]
    for n, (x, y) in enumerate(top, 1):
        pads.append(f'(pad {n} thru_hole circle (at {x:g} {y:g}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask))')
    right = [(16.51, y) for y in (5.08, 2.54, 0, -2.54, -5.08, -7.62)]
    for n, (x, y) in enumerate(right, 15):
        pads.append(f'(pad {n} thru_hole circle (at {x:g} {y:g}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask))')
    bottom_nums = list(range(21, 34))
    bottom_x = [13.97 - 2.54 * i for i in range(13)]
    for n, x in zip(bottom_nums, bottom_x):
        pads.append(f'(pad {n} thru_hole circle (at {x:g} -7.62) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask))')
    pads.append('(pad 34 thru_hole circle (at -13.97 -5.08) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask))')
    for k, n in enumerate(range(35, 45)):
        x = 11.43 if k % 2 == 0 else 8.89
        y = -5.08 + 2.54 * (k // 2)
        pads.append(f'(pad {n} smd rect (at {x:g} {y:g}) (size 2.794 0.889) (layers F.Cu F.Paste F.Mask))')
    for k, n in enumerate(range(45, 53)):
        pads.append(f'(pad {n} smd rect (at -9.3716 {-3.5+k:g}) (size 2.0 0.6) (layers F.Cu F.Paste F.Mask))')
    pads.append('(pad 53 smd rect (at -15.24 -1.27) (size 3.048 1.016) (layers F.Cu F.Paste F.Mask))')
    pads.append('(pad 54 smd rect (at -15.24 1.27) (size 3.048 1.016) (layers F.Cu F.Paste F.Mask))')
    body = '''(module Teensy40_All_Pins (layer F.Cu) (tedit 0)
  (descr "Teensy 4.0 module, through-hole headers and underside SMT pads, based on PJRC dimensions")
  (fp_text reference REF** (at 0 -10.16) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))
  (fp_text value "Teensy 4.0" (at 0 10.16) (layer F.Fab) (effects (font (size 1 1) (thickness 0.15))))
  (fp_line (start -17.78 -8.89) (end 17.78 -8.89) (layer F.Fab) (width 0.1))
  (fp_line (start 17.78 -8.89) (end 17.78 8.89) (layer F.Fab) (width 0.1))
  (fp_line (start 17.78 8.89) (end -17.78 8.89) (layer F.Fab) (width 0.1))
  (fp_line (start -17.78 8.89) (end -17.78 -8.89) (layer F.Fab) (width 0.1))
  (fp_line (start -17.78 -8.89) (end 17.78 -8.89) (layer F.SilkS) (width 0.15))
  (fp_line (start 17.78 -8.89) (end 17.78 8.89) (layer F.SilkS) (width 0.15))
  (fp_line (start 17.78 8.89) (end -17.78 8.89) (layer F.SilkS) (width 0.15))
  (fp_line (start -17.78 8.89) (end -17.78 -8.89) (layer F.SilkS) (width 0.15))
  (fp_poly (pts (xy -3.175 -0.635) (xy -2.921 -0.889) (xy -2.667 -0.508) (xy -2.921 -0.254)) (layer F.SilkS) (width 0.1))
  (pad 1 thru_hole circle (at -16.51 7.62) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask))
'''
    # Replace initial pad row (1..14) in the scaffold with generated definitions
    # and append remaining pads only once.
    body = re.sub(r'  \(pad 1 thru_hole.*?\n', "", body, count=1)
    return body + "\n".join("  " + p for p in pads) + "\n)\n"


def main() -> None:
    sch_path = ROOT / "Sheets" / "L3_Processing.kicad_sch"
    board_path = ROOT / "RideDAQ_v1.kicad_pcb"
    fp_path = ROOT / "Libraries" / "footprints" / "Teensy.pretty" / "Teensy40_All_Pins.kicad_mod"
    fp_path.parent.mkdir(parents=True, exist_ok=True)
    if fp_path.exists():
        raise SystemExit(f"Refusing to overwrite existing footprint: {fp_path}")
    if "U8" in sch_path.read_text(encoding="utf-8"):
        raise SystemExit("U8 already occurs in processing sheet; inspect before retrying")

    # Make a rollback copy before changing the project.
    backup = ROOT / "RideDAQ_v1-backups" / "CAN_before_integration"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(sch_path, backup / sch_path.name)
    shutil.copy2(board_path, backup / board_path.name)
    shutil.copy2(ROOT / "sym-lib-table", backup / "sym-lib-table")

    schematic = sch_path.read_text(encoding="utf-8")
    teensy_symbol = 'teensy_master:Teensy4.0'
    # Keep the existing symbol/pin map; only correct its footprint association.
    idx = schematic.index('(property "Reference" "U3"')
    sym_start = schematic.rfind('\n\t(symbol\n', 0, idx) + 1
    sym_block, sym_end = balanced_block(schematic, sym_start)
    sym_block = sym_block.replace('Teensy:Teensy30_31_32_All_Pins', 'Teensy:Teensy40_All_Pins')
    schematic = schematic[:sym_start] + sym_block + schematic[sym_end:]

    intf_lib = KICAD / "symbols" / "Interface_CAN_LIN.kicad_sym"
    dev_lib = KICAD / "symbols" / "Device.kicad_sym"
    con_lib = KICAD / "symbols" / "Connector_Generic.kicad_sym"
    can = named_symbol(intf_lib, "MCP2542FDxMF")
    can = can.replace("MCP2542FDxMF", "MCP2542FD_E_SN")
    # The DFN library symbol has an exposed-pad pin 9; the SOIC-8 Robu part does not.
    m = re.search(r'\(pin passive line(?:(?!\n\t\t\t\)).)*?\(number "9".*?\n\t\t\t\)\n', can, re.S)
    if not m:
        raise ValueError("Could not strip the DFN-only exposed-pad pin")
    can = can[:m.start()] + can[m.end():]
    can = can.replace("DFN-8", "SOIC-8").replace("DFN*1EP*3x3mm*P0.65mm*", "SOIC*3.9x4.9mm*P1.27mm*")
    can = can.replace("Package_DFN_QFN:DFN-8-1EP_3x3mm_P0.65mm_EP1.55x2.4mm", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
    can = can.replace('(symbol "MCP2542FD_E_SN"', '(symbol "RideDAQ_CAN:MCP2542FD_E_SN"', 1)
    conn = named_symbol(con_lib, "Conn_01x03")
    conn = conn.replace('(symbol "Conn_01x03"', '(symbol "Connector_Generic:Conn_01x03"', 1)
    cap = named_symbol(dev_lib, "C_Small")
    cap = cap.replace('(symbol "C_Small"', '(symbol "Device:C_Small"', 1)
    local_lib = ROOT / "Libraries" / "symbols" / "RideDAQ_CAN.kicad_sym"
    if local_lib.exists():
        raise SystemExit(f"Refusing to overwrite existing symbol library: {local_lib}")
    local_lib.write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n' +
                         re.sub(r'^\(symbol "RideDAQ_CAN:', '(symbol "', can, count=1) +
                         '\n)\n', encoding="utf-8", newline="\n")
    sym_table = ROOT / "sym-lib-table"
    table_text = sym_table.read_text(encoding="utf-8")
    if '"RideDAQ_CAN"' not in table_text:
        table_text = table_text.replace('(sym_lib_table', '(sym_lib_table\n  (lib (name "RideDAQ_CAN")(type "KiCad")(uri "${KIPRJMOD}/Libraries/symbols/RideDAQ_CAN.kicad_sym")(options "")(descr "RideDAQ CAN-FD transceiver"))', 1)
        sym_table.write_text(table_text, encoding="utf-8", newline="\n")
    schematic = insert_lib_symbol(schematic, can)
    schematic = insert_lib_symbol(schematic, conn)
    schematic = insert_lib_symbol(schematic, cap)

    page_path = "/158df91c-d88f-4753-99fc-2b3b07cc7b20/16deced6-d3e0-4d30-90eb-577afd30839e"
    additions = []
    additions.append(component("RideDAQ_CAN:MCP2542FD_E_SN", "U8", "MCP2542FD-E/SN",
                               90, 96, "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
                               [str(n) for n in range(1, 9)], page_path,
                               "https://robu.in/wp-content/uploads/2023/02/2648004.pdf",
                               description="CAN FD transceiver, 8 Mbps, 5 V VDD and 3.3 V VIO"))
    additions.append(component("Connector_Generic:Conn_01x03", "J7", "CAN-FD",
                               152, 96, "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3_1x03_P5.00mm_Horizontal",
                               ["1", "2", "3"], page_path,
                               description="CANH, CANL, signal ground"))
    additions.append(component("Device:C_Small", "C22", "100nF",
                               86, 118, "Capacitor_SMD:C_0805_2012Metric", ["1", "2"], page_path))
    additions.append(component("Device:C_Small", "C23", "100nF",
                               96, 118, "Capacitor_SMD:C_0805_2012Metric", ["1", "2"], page_path))
    additions.append(component("Device:R_Small", "R25", "120R (DNP)",
                               131, 84, "Resistor_SMD:R_0805_2012Metric", ["1", "2"], page_path,
                               dnp=True, description="Optional CAN bus termination; fit only at bus end"))

    # FlexCAN3 signal names originate at Teensy symbol pads 41 (RX) and 42 (TX).
    labels = [
        label("CAN3_RX", 173.99, 58.42, 0), label("CAN3_TX", 173.99, 60.96, 0),
        label("CAN3_TX", 77.3, 90.92, 180), label("CAN3_RX", 77.3, 93.46, 180),
        label("GND", 77.3, 101.08, 180), label("+5V", 90, 85.84),
        label("+3V3", 87.46, 85.84), label("GND", 90, 106.16),
        label("CAN_H", 102.7, 93.46, 0), label("CAN_L", 102.7, 98.54, 0),
        label("CAN_H", 146.92, 93.46, 180), label("CAN_L", 146.92, 96, 180),
        label("GND", 146.92, 98.54, 180),
        label("+5V", 86, 115.46), label("GND", 86, 120.54),
        label("+3V3", 96, 115.46), label("GND", 96, 120.54),
        label("CAN_H", 127.19, 84, 180), label("CAN_L", 134.81, 84, 0),
    ]
    additions.extend(labels)
    insert = schematic.rfind(")")
    schematic = schematic[:insert] + "\n".join(additions) + schematic[insert:]
    sch_path.write_text(schematic, encoding="utf-8", newline="\n")
    fp_path.write_text(make_teensy_footprint(), encoding="utf-8", newline="\n")
    print(f"Updated {sch_path}")
    print(f"Created {fp_path}")
    print(f"Backups in {backup}")


if __name__ == "__main__":
    main()
