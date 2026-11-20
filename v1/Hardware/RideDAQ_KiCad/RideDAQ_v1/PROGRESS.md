# RideDAQ V1 project progress

**Updated:** 2026-11-17  
**Project:** Ride Quality DAQ, hardware revision V1 (KiCad 10 project)

## Current state

- The hierarchical schematic is organized around power conditioning, processing, and sensing, with dedicated BME280, RTC, and SD-card sheets. It describes a Teensy 4.0 based data acquisition board with sensor, storage, and RTC support.
- The original PCB contains 75 placed footprints and a board outline. It has no copper track segments, vias, or copper zones; routing and power-plane work remain outstanding.
- KiCad 10.0.1 DRC review found 152 unconnected items and 100 violations (1 error, 99 warnings). The error is a courtyard overlap between BT1 (battery holder) and JP3 (jumper). Warning groups include 60 silkscreen-over-copper, 16 footprint-library mismatches, 9 text-height, 6 silkscreen-overlap, 3 back-layer text mirror, 3 text-thickness, and 2 silkscreen-to-edge issues. See `Reports/pcb_drc_review.json`.
- A BOM export exists at `Manufacturing/RideDAQ_v1_BoM.csv`.
- Project-local symbol and footprint libraries, plus local 3D model references, have been consolidated. The recorded KiCad CLI validation passed 8/8 checks, including board and hierarchical schematic exports, library resolution, and structural comparison against the migration baseline.
- CAN-FD transceiver U8 (Infineon TLE9252VLCXUMA1) is integrated into the processing schematic. Its exposed paddle is modeled as pin 15 and tied to GND. ERC reports 0 errors and 13 warnings. A dangling `PACK_V_SENSE` link to Teensy ADC pad 23 was found during review and corrected.
- The CAN transceiver, connector, bypass capacitors, and optional DNP terminator are placed in separate candidate board `RideDAQ_v1_CAN_Integrated.kicad_pcb`; the original board remains unchanged. The candidate's lower edge is extended 11 mm for the placement study. Mechanical dimensions are not frozen.
- U8 has an assigned but explicitly provisional PG-TSON-14 footprint. Its package body and terminal pitch match the package family; land/paste geometry still needs confirmation against Infineon's footprint drawing.
- PCB DRC has been run previously; the board is not fabrication-ready while unrouted connections and the courtyard error remain.

## Next milestones

1. Verify U8's copper/paste land pattern and confirm `VBAT_PT` remains above 5.5 V across the full battery discharge range.
2. Verify the Teensy 4.0 underside CAN3 pad mapping and review CAN placement and connector access in KiCad.
3. Resolve BT1/JP3 courtyard overlap and review placement/clearance, including the CAN connector and mounting points.
4. Review the remaining schematic ERC warnings and confirm `PACK_V_SENSE` in the live KiCad view.
6. Complete routing, add and refill copper zones, and address the silkscreen and footprint-library warnings.
7. Re-run PCB DRC and resolve or document remaining violations.
8. Verify component values, footprints, and sourcing in the BOM; then generate and inspect fabrication outputs (Gerbers and drill files).
9. Build a prototype and record power-up, sensor, RTC, SD-card, and CAN/CAN-FD validation results.

## CAN interface progress (2026-11-17)

- Added Infineon TLE9252VLCXUMA1 to the processing schematic for classic CAN and CAN-FD up to 5 Mbit/s. The interface uses Teensy CAN3: CTX3/pad 31 to TxD and RxD to CRX3/pad 30.
- Connected TLE9252VLC VCC to existing +5 V, VIO to existing +3.3 V, and VBAT to the protected `VBAT_PT` vehicle/input net. EN/NSTB are held high for normal mode, WAKE is grounded, INH/NERR are unused, and R25 is a default-DNP 120 Ω terminator.
- Connected the power-conditioning `PACK_V_SENSE` net through the processing sheet to Teensy U3 pad 23 after the logic review exposed a floating sheet label.
- Netlist confirms CAN3 TX/RX, CANH/CANL, +5V, +3V3, VBAT_PT, and exposed-paddle pin 15 on GND. ERC reports 0 errors and 13 warnings.
- Candidate PCB DRC: 98 violations (1 error, 97 warnings) and 168 unconnected items. The original board: 100 violations (1 error, 99 warnings) and 152 unconnected items. The sole error remains the BT1/JP3 courtyard overlap; copper routing is still outstanding.
- U8 footprint is assigned provisionally; verify against the manufacturer's land pattern before fabrication. The candidate outline is about 69.6 × 71.1 mm and remains unfrozen.
- Design and logic review are recorded in `Reports/CAN_interface_design.md` and `Reports/CAN_logic_review.md`.

## Evidence

- `Reports/library_consolidation/library_migration_detailed.md`
- `Reports/library_consolidation/validation_report.json`
- `Reports/library_consolidation/migration_report.json`
- `Reports/pcb_placement_snapshot.json`
- `Reports/pcb_drc_review.json`
- `Reports/can_integrated_drc.json`
- `Reports/can_integrated_erc.txt`
- `Reports/RideDAQ_CAN_integrated.xml`
- `Reports/CAN_view/RideDAQ_CAN_Integrated.svg`
- `Reports/CAN_interface_design.md`
- `Manufacturing/RideDAQ_v1_BoM.csv`

This progress note summarizes repository artifacts inspected and PCB DRC run on the update date. It does not claim ERC, routing, or hardware validation has been completed.
