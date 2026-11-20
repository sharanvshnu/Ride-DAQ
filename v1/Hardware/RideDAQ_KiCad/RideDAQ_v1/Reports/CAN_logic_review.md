# CAN-FD schematic logic review

**Reviewed:** 2026-11-17 against the RideDAQ hierarchical schematic and exported KiCad netlist.
**Scope:** Circuit intent, signal paths, supply rails, startup/mode behavior, and ERC. This does not simulate CAN frames, firmware, EMC, or the physical bus.

## Expected operating story

| State | Expected behavior | Schematic implementation / assessment |
|---|---|---|
| Board powered | Existing +5 V buck and +3.3 V rail power TLE9252VLC VCC and VIO. Protected input `VBAT_PT` powers VBAT. | Netlist confirms U8 pins 3, 5, and 10 connect to +5V, +3V3, and VBAT_PT. Confirm VBAT_PT remains 5.5–40 V in the actual supply conditions. |
| Startup | The transceiver enters Normal-operating Mode. | EN pin 6 and NSTB pin 14 are tied high to +3V3. This is a defined state; they are not left floating. |
| Idle bus | TxD high represents recessive state; CANH/CANL are biased by the transceiver and the network’s terminators. | CANH/CANL go to J7 pins 1/2. R25 is DNP, so the board does not add a third terminator by default. |
| Transmit | Teensy CAN3 TX drives TxD; the transceiver converts it to differential CANH/CANL. | Netlist confirms Teensy U3 pad 42 (CAN3 TX / CTX3) connects to U8 pin 1 (TxD). |
| Receive | The transceiver converts CANH/CANL to RxD; RxD returns to Teensy CAN3 RX. | Netlist confirms U8 pin 4 (RxD) connects to Teensy U3 pad 41 (CAN3 RX / CRX3). |
| CAN-FD use | Classic CAN frames and CAN-FD frames can use the same pair; the transceiver supports the physical layer up to 5 Mbit/s. | Other nodes and the Teensy controller configuration must support the selected nominal/data bit rates. Firmware and bus compatibility were not exercised here. |
| Sleep / wake request | A controller could place the device into receive-only, standby, or sleep modes and potentially wake it from the bus or WAKE input. | Not enabled in this design: EN/NSTB are permanently high; WAKE is grounded. This is an intentional always-on choice, but it means no software-controlled low-power mode or wake-up. |
| Diagnostic fault | NERR can report diagnostic/wake conditions; INH can control external circuitry. | Both are marked no-connect. The transceiver’s internal protection remains, but RideDAQ firmware cannot read NERR and INH does not control a regulator. |
| Loss of supply | The transceiver disables normal bus operation as supplies fall outside their valid ranges; its undervoltage / fail-safe behavior limits invalid bus drive. | Must be confirmed on hardware under the actual power sequencing and input transients. |

## Logic issue found and corrected

The `PACK_V_SENSE` hierarchical label in the processing sheet was floating, while Teensy U3 pad 23 had a separate local label named `VBAT`. The power-conditioning sheet had a matching `PACK_V_SENSE` output, but the Teensy ADC input was not actually connected to it. The processing-sheet label is now attached to U3 pad 23 and the stale floating label was removed. Netlist export now shows the divider output components and U3 pad 23 on the same `/L2_Power_Conditioning/PACK_V_SENSE` net.

The TLE9252VLC exposed paddle is not internally bonded to GND. The symbol now has a dedicated pin 15 labeled `EP_GND`, connected to GND; the PCB footprint's exposed pad 15 is also assigned to GND.

## KiCad checks

- Netlist export completed successfully.
- ERC result: **0 errors, 13 warnings** (`Reports/can_integrated_erc.txt`). Warnings cover existing symbol/library configuration issues and the `+3V3`/`3V3` alias warning in the RTC sheet.
- CAN netlist paths were checked directly: TXD/RXD, CANH/CANL, ground, VCC, VIO, VBAT_PT, EN, and NSTB.
- PCB candidate DRC reports 98 total violations (1 existing error, 97 warnings) and 168 unconnected items; the original board had 100 violations (1 error, 99 warnings) and 152 unconnected items. The only error is the existing BT1/JP3 courtyard overlap. No new CAN-related DRC errors were introduced; copper remains unrouted, accounting for the added unconnected items.
- Remaining schematic/physical limitations: U8's assigned package-matched footprint is provisional and must be checked against Infineon's land-pattern drawing; VBAT_PT must stay above 5.5 V; NERR and INH are unused; CAN mode is hardwired to normal operation; CAN-FD timing and bus termination need firmware and bench validation.
