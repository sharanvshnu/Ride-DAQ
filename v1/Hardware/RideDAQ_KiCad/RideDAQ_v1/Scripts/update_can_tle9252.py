"""Replace CAN schematic transceiver with Infineon TLE9252VLC.

Run from project root while KiCad is closed. The board remains untouched;
the TSON land pattern needs a separate package-specific verification.
"""
from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = "/158df91c-d88f-4753-99fc-2b3b07cc7b20/16deced6-d3e0-4d30-90eb-577afd30839e"


def uid() -> str:
    return str(uuid.uuid4())


def block_at(text: str, start: int) -> tuple[str, int]:
    depth = 0
    quoted = escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if quoted:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return text[start:i + 1], i + 1
    raise ValueError("Unbalanced S-expression")


def make_symbol(lib_name: str) -> str:
    # Coordinates are chosen to align direct net labels with the CAN section.
    # X/Y are symbol-local KiCad coordinates (Y positive upwards).
    pins = [
        ("input", "TXD", "1", -12.7, 5.08, 0),
        ("power_in", "GND", "2", 0, -10.16, 90),
        ("power_in", "VCC", "3", 0, 10.16, 270),
        ("output", "RXD", "4", -12.7, 2.54, 0),
        ("power_in", "VIO", "5", -2.54, 10.16, 270),
        ("input", "EN", "6", -12.7, -5.08, 0),
        ("open_collector", "INH", "7", 12.7, -5.08, 180),
        ("open_collector", "NERR", "8", 12.7, -7.62, 180),
        ("input", "WAKE", "9", 12.7, -10.16, 180),
        ("power_in", "VBAT", "10", 2.54, 10.16, 270),
        ("passive", "N.C.", "11", 12.7, 0, 180),
        ("bidirectional", "CANL", "12", 12.7, -2.54, 180),
        ("bidirectional", "CANH", "13", 12.7, 2.54, 180),
        ("input", "NSTB", "14", 12.7, 7.62, 180),
    ]
    out = [f'(symbol "{lib_name}"',
           '\t(exclude_from_sim no)', '\t(in_bom yes)', '\t(on_board yes)',
           '\t(in_pos_files yes)', '\t(duplicate_pin_numbers_are_jumpers no)',
           '\t(property "Reference" "U" (at 0 12.7 0) (effects (font (size 1.27 1.27)) (justify left)))',
           '\t(property "Value" "TLE9252VLC" (at 0 10.16 0) (effects (font (size 1.27 1.27)) (justify left)))',
           '\t(property "Footprint" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           '\t(property "Datasheet" "https://www.infineon.com/assets/row/public/documents/10/49/infineon-tle9252v-datasheet-en.pdf" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           '\t(property "Description" "High-speed CAN FD transceiver, up to 5 Mbit/s, PG-TSON-14; VCC 5 V, VIO 3.3 V, VBAT protected vehicle input" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           '\t(property "ki_keywords" "CAN CAN-FD transceiver" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           '\t(symbol "TLE9252VLC_0_1"',
           '\t\t(rectangle (start -10.16 8.89) (end 10.16 -8.89) (stroke (width 0.254) (type default)) (fill (type background)))',
           '\t)', '\t(symbol "TLE9252VLC_1_1"']
    for typ, name, num, x, y, ang in pins:
        out += [f'\t\t(pin {typ} line (at {x:g} {y:g} {ang}) (length 2.54)',
                f'\t\t\t(name "{name}" (effects (font (size 1.27 1.27))))',
                f'\t\t\t(number "{num}" (effects (font (size 1.27 1.27))))',
                '\t\t)']
    out += ['\t)', ')']
    return '\n'.join(out)


def global_label(name: str, x: float, y: float) -> str:
    return (f'\n(global_label "{name}" (shape input) (at {x:g} {y:g} 0)\n'
            f'\t(fields_autoplaced yes)\n\t(effects (font (size 1.27 1.27)) (justify left bottom))\n'
            f'\t(uuid "{uid()}")\n'
            f'\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x:g} {y-5.08:g} 0)\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify left) (hide yes)))\n)\n')


def label(name: str, x: float, y: float) -> str:
    return (f'\n(label "{name}" (at {x:g} {y:g} 0)\n'
            f'\t(effects (font (size 1.27 1.27)) (justify left bottom))\n'
            f'\t(uuid "{uid()}"))\n')


def main() -> None:
    sch_path = ROOT / "Sheets" / "L3_Processing.kicad_sch"
    power_path = ROOT / "Sheets" / "L2_Power_Conditioning.kicad_sch"
    sym_path = ROOT / "Libraries" / "symbols" / "RideDAQ_CAN.kicad_sym"
    backup = ROOT / "RideDAQ_v1-backups" / "CAN_TLE9252VLC"
    backup.mkdir(parents=True, exist_ok=True)
    for p in (sch_path, power_path, sym_path):
        shutil.copy2(p, backup / p.name)

    sch = sch_path.read_text(encoding="utf-8")
    new_block = make_symbol("RideDAQ_CAN:TLE9252VLC")
    lib_start = sch.index("\t(lib_symbols")
    lib_open = sch.index("(", lib_start)
    _, lib_end = block_at(sch, lib_open)
    lib = sch[lib_open:lib_end]
    old_marker = '(symbol "RideDAQ_CAN:MCP2542FD_E_SN"'
    old_pos = lib.find(old_marker)
    if old_pos < 0:
        raise SystemExit("Old CAN transceiver cache not found; refusing to guess")
    old_block, old_end = block_at(lib, old_pos)
    lib = lib[:old_pos] + lib[old_end:]
    lib = lib[:-1] + "\n" + new_block + "\n)"
    sch = sch[:lib_open] + lib + sch[lib_end:]

    ref_marker = '(property "Reference" "U8"'
    ref_pos = sch.index(ref_marker)
    comp_start = sch.rfind('\n(symbol\n', 0, ref_pos) + 1
    comp, comp_end = block_at(sch, comp_start)
    comp = comp.replace('RideDAQ_CAN:MCP2542FD_E_SN', 'RideDAQ_CAN:TLE9252VLC', 1)
    comp = comp.replace('"MCP2542FD-E/SN"', '"TLE9252VLCXUMA1"', 1)
    comp = re.sub(r'\(property "Footprint" "[^"]*"', '(property "Footprint" ""', comp, count=1)
    comp = re.sub(r'\(property "Datasheet" "[^"]*"',
                  '(property "Datasheet" "https://www.infineon.com/assets/row/public/documents/10/49/infineon-tle9252v-datasheet-en.pdf"', comp, count=1)
    comp = re.sub(r'\(property "Description" "[^"]*"',
                  '(property "Description" "CAN/CAN-FD transceiver, 5 Mbit/s, PG-TSON-14; VCC=5V, VIO=3.3V, VBAT=protected vehicle input"', comp, count=1)
    comp = re.sub(r'\n\t\(pin "\d+" \(uuid "[^"]+"\)\)', '', comp)
    pin_section = '\n'.join(f'\t(pin "{n}" (uuid "{uid()}"))' for n in range(1, 15)) + '\n'
    comp = comp.replace('\n\t(instances', pin_section + '\t(instances', 1)
    sch = sch[:comp_start] + comp + sch[comp_end:]

    # EN and NSTB are held high so the hardware starts in Normal-operating Mode.
    sch = sch.replace('(label "GND" (at 77.3 101.08 180)', '(label "+3V3" (at 77.3 101.08 180)', 1)
    insert_at = sch.rfind(')')
    new_text = (label("+3V3", 102.7, 88.38) + label("GND", 102.7, 106.16) +
                global_label("VBAT_PT", 92.54, 85.84) +
                ''.join(f'\n(no_connect (at {x:g} {y:g}) (uuid "{uid()}"))\n'
                        for x, y in [(102.7, 96), (102.7, 101.08), (102.7, 103.62)]))
    sch = sch[:insert_at] + new_text + sch[insert_at:]
    sch_path.write_text(sch, encoding="utf-8", newline="\n")

    # Export the protected/raw vehicle-input net to the processing sheet.
    power = power_path.read_text(encoding="utf-8")
    marker = '(label "VBAT_PT"\n\t\t(at 36.83 90.17 0)'
    if marker not in power:
        raise SystemExit("VBAT_PT entry point changed; refusing to add cross-sheet link")
    power = power.replace(marker, '(global_label "VBAT_PT"\n\t\t(shape input)\n\t\t(at 36.83 90.17 0)\n\t\t(fields_autoplaced yes)', 1)
    # Global labels carry the hidden inter-sheet references field.
    point = '(uuid "1482be15-3a27-4a05-991e-857549497c69")'
    if point in power:
        power = power.replace(point, point + '\n\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}" (at 36.83 85.09 0) (effects (font (size 1.27 1.27)) (justify left) (hide yes)))', 1)
    power_path.write_text(power, encoding="utf-8", newline="\n")

    # Keep the project-local library aligned with the embedded symbol cache.
    lib_source = make_symbol("TLE9252VLC")
    sym_path.write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n' + lib_source + '\n)\n', encoding="utf-8", newline="\n")
    print(f"Updated {sch_path}")
    print(f"Updated {power_path} with global protected-input net VBAT_PT")
    print(f"Backups: {backup}")


if __name__ == "__main__":
    main()
