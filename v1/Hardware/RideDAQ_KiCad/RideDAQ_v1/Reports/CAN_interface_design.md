# RideDAQ CAN / CAN-FD interface

**Schematic:** CAN interface is on `Sheets/L3_Processing.kicad_sch`, with U8 exposed paddle pin 15 tied to GND.
**Transceiver:** Infineon TLE9252VLCXUMA1, PG-TSON-14, CAN and CAN-FD physical layer up to 5 Mbit/s.
**Controller:** Teensy 4.0 FlexCAN3 using the exposed underside CAN3 signals.
**PCB:** Components are placed in `RideDAQ_v1_CAN_Integrated.kicad_pcb`, a separate placement review copy. Its lower edge was extended by 11 mm; board and enclosure dimensions remain provisional.

## Connections

| Net / signal | TLE9252VLC pin | RideDAQ connection |
|---|---:|---|
| CAN3_TX / Teensy CTX3 (pad 31) | 1 TxD | Teensy U3 pad 42 |
| CAN3_RX / Teensy CRX3 (pad 30) | 4 RxD | Teensy U3 pad 41 |
| +5V | 3 VCC | Existing +5 V buck rail |
| +3V3 | 5 VIO | Existing +3.3 V rail; sets Teensy-compatible logic levels |
| VBAT_PT | 10 VBAT | Protected board input rail |
| GND | 2 GND | Common board ground |
| GND | Exposed paddle, pad 15 | Common board ground; represented in the schematic and PCB |
| CAN_H | 13 CANH | J7 pin 1 |
| CAN_L | 12 CANL | J7 pin 2 |
| GND | — | J7 pin 3 |

VBAT is separate from both +5 V and the Teensy VBAT-labelled signal. Infineon specifies 5.5 V < VBAT < 40 V; VCC must remain 4.5–5.5 V and VIO 3.0–5.5 V. The 2S battery pack and protection path must maintain VBAT_PT above the 5.5 V operating threshold through the intended discharge range. The existing +5 V and +3.3 V rails provide VCC and VIO, so no TLE4476D regulator is added.

## Mode and bus behavior

- EN (pin 6) and NSTB (pin 14) are tied to +3V3, selecting Normal-operating Mode at startup and during use.
- WAKE (pin 9) is tied to GND because local wake-up is not used in this always-on configuration.
- INH (pin 7) and NERR (pin 8) are left explicitly unconnected. The regulator-enable output and error/wake diagnostic are therefore not used by firmware.
- Pin 11 is marked no-connect per the datasheet.
- C22 and C23 provide local 100 nF bypassing for the 5 V and 3.3 V supplies.
- R25 is a selectable 120 Ω CANH-to-CANL terminator and is DNP by default. Fit it only if RideDAQ is at a physical end of the bus.
- J7 provides CANH, CANL, and signal ground. Route CANH/CANL as a differential pair with a continuous reference plane.

This wiring intentionally keeps the transceiver in normal mode. It does not provide firmware-controlled standby/sleep or CAN/local wake-up. NERR diagnostics are not routed to the Teensy.

## Verification and remaining work

- KiCad netlist confirms the Teensy CAN3 TX/RX paths, CANH/CANL connector nets, +5V/+3V3/VBAT_PT rails, and exposed paddle pin 15 on GND.
- KiCad ERC reports **0 errors and 13 warnings**. Remaining warnings concern existing library/configuration issues and the RTC `+3V3`/`3V3` alias; see `Reports/can_integrated_erc.txt`.
- PCB DRC on the integrated copy reports **98 violations (1 error, 97 warnings)** and **168 unconnected items**. The original board reports 100 violations (1 error, 99 warnings) and 152 unconnected items. The single error remains the existing BT1/JP3 courtyard overlap. The board has no routed copper or zones yet.
- U8’s assigned footprint is a provisional body/pitch match (3.0 × 4.5 mm body, 0.65 mm terminal pitch, exposed paddle). Its land pattern was adapted from a generic KiCad DFN footprint and is not approved for fabrication until its copper/paste geometry is checked against Infineon’s [PG-TSON-14-3 package footprint drawing](https://www.infineon.com/package/PG-TSON-14-3). The local footprint description is marked provisional.
- The candidate board is approximately **69.6 × 71.1 mm**, adding 11 mm along its lower edge to fit CAN parts. `RideDAQ_v1.kicad_pcb` remains unchanged; the candidate board outline, connector choice, mounting points, and enclosure are not frozen.
- Confirm the 2S pack’s minimum voltage and protection drop keep VBAT_PT above 5.5 V. Verify the Teensy underside CAN3 pad mapping against the actual module before fabrication.
- The logic review in `Reports/CAN_logic_review.md` covers expected startup, transmit, receive, idle, low-supply, and diagnostic behavior. It does not exercise firmware or a physical CAN bus.

## References

- [Infineon TLE9252V datasheet](https://www.infineon.com/assets/row/public/documents/10/49/infineon-tle9252v-datasheet-en.pdf)
- [Infineon PG-TSON-14-3 package and footprint drawing](https://www.infineon.com/package/PG-TSON-14-3)
- [Infineon TLE9252VLC product listing](https://www.infineon.com/product-table/automotive-can-transceivers)
- [Infineon clarification on the exposed paddle](https://community.infineon.com/t5/Other-Technologies-General/Is-the-TLE9252VLC-exposed-pad-electrically-connected-to-GND-and-IC/td-p/861158)
