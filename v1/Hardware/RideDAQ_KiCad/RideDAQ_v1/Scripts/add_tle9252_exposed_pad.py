from pathlib import Path
import uuid, shutil

root = Path(__file__).resolve().parents[1]
sheet = root / "Sheets" / "L3_Processing.kicad_sch"
lib = root / "Libraries" / "symbols" / "RideDAQ_CAN.kicad_sym"
fp_id = "RideDAQ_CAN:PG-TSON-14_3x4.5mm_P0.65mm_EP1.65x4.25mm"
pin = '''\t\t(pin power_in line (at 0 -12.7 90) (length 2.54)
\t\t\t(name "EP_GND" (effects (font (size 1.27 1.27))))
\t\t\t(number "15" (effects (font (size 1.27 1.27))))
\t\t)\n'''

def add_symbol_pin(path: Path, symbol_name: str, unit_name: str):
    text = path.read_text(encoding="utf-8")
    start = text.index(f'(symbol "{symbol_name}"')
    unit = text.index(f'(symbol "{unit_name}"', start)
    unit_close = text.index('\n\t)', unit)
    unit_text = text[unit:unit_close]
    if '(number "15"' not in unit_text:
        text = text[:unit_close] + '\n' + pin.rstrip() + text[unit_close:]
    path.write_text(text, encoding="utf-8")

for path in (sheet, lib):
    bak = path.with_suffix(path.suffix + ".ep_pin.bak")
    if not bak.exists(): shutil.copy2(path, bak)

add_symbol_pin(sheet, "RideDAQ_CAN:TLE9252VLC", "TLE9252VLC_1_1")
add_symbol_pin(lib, "TLE9252VLC", "TLE9252VLC_1_1")

# Keep the assigned footprint visible as the default on future symbol placements.
text = lib.read_text(encoding="utf-8")
if '(property "Footprint" ""' in text:
    text = text.replace('(property "Footprint" ""', f'(property "Footprint" "{fp_id}"', 1)
lib.write_text(text, encoding="utf-8")

text = sheet.read_text(encoding="utf-8")
cache_start = text.index('(symbol "RideDAQ_CAN:TLE9252VLC"')
cache_end = text.index('\n\t(no_connect', cache_start)
cache = text[cache_start:cache_end]
if '(property "Footprint" ""' in cache:
    cache = cache.replace('(property "Footprint" ""', f'(property "Footprint" "{fp_id}"', 1)
    text = text[:cache_start] + cache + text[cache_end:]
inst = text.index('(lib_id "RideDAQ_CAN:TLE9252VLC")')
end = text.index('(pin "14"', inst)
end = text.index('\n', end)
if '(pin "15"' not in text[inst:text.index('(instances', inst)]:
    text = text[:end+1] + f'\t(pin "15" (uuid "{uuid.uuid4()}"))\n' + text[end+1:]
if '(at 125 142.7 0)' not in text:
    final = text.rfind(')')
    text = text[:final] + f'\n(label "GND" (at 125 142.7 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uuid.uuid4()}"))\n' + text[final:]
sheet.write_text(text, encoding="utf-8")
print("Added U8 exposed-paddle pin 15 to GND in symbol and schematic.")
