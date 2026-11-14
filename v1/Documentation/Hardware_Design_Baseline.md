# RideDAQ V1 — Hardware Design Baseline

**Branch:** `hardware-v1`  
**Baseline status:** Engineering review in progress  
**Purpose:** Record the current design intent, known inconsistencies and release gates. This document is a review register, not an electrical approval or manufacturing release.

## 1. System baseline

| Area | Current design intent | Status |
|---|---|---|
| Controller | Teensy 4.0 | Selected |
| IMU | BMI323 breakout, I²C / Qwiic | Selected; mounting and interrupt wiring to verify |
| GNSS | GP-02, UART3 and PPS | Selected; exact module signal levels to confirm from module documentation |
| Environmental sensor | BME280, I²C | Selected |
| RTC | DS3231M, I²C | Selected; backup-cell charging compatibility unresolved |
| EEPROM | I²C EEPROM | Part identity inconsistent in project history |
| BLE | HM-10, UART2 | Selected; PCB connector presence to verify |
| Storage | microSD, SPI2 | Selected |
| Input power | 2S battery, 6.0–8.4 V intended range | System assumption; pack-specific details remain open |
| Rails | TPS5430 5 V buck; LD1117S33 3.3 V LDO | Design selected; electrical qualification pending |

## 2. Intended controller interface allocation

The following allocation is the current intended mapping from the design review notes. Confirm against the latest schematic and Teensy pinout before firmware or PCB sign-off.

| Teensy pin | Signal | Intended connection |
|---|---|---|
| GPIO2 | Power LED | Status LED |
| GPIO3 | GNSS LED | Status LED |
| GPIO4 | BLE / logging LED | Status LED |
| GPIO5 | BMI323 INT1 | Optional separate interrupt; not present on 4-pin Qwiic |
| GPIO6 | GNSS PPS | GP-02 PPS |
| GPIO7 / RX2 | BLE TXD | HM-10 TXD → Teensy RX2 |
| GPIO8 / TX2 | BLE RXD | Teensy TX2 → HM-10 RXD |
| GPIO14 / TX3 | GNSS RX | Teensy TX3 → GNSS RX |
| GPIO15 / RX3 | GNSS TX | GNSS TX → Teensy RX3 |
| GPIO16 / A2 | PACK_V_SENSE | Battery divider output; connectivity must be verified |
| GPIO18 | SDA0 | Shared I²C SDA |
| GPIO19 | SCL0 | Shared I²C SCL |
| GPIO35 | MOSI2 | microSD CMD / MOSI |
| GPIO34 | MISO2 | microSD DAT0 / MISO |
| GPIO37 | SCK2 | microSD CLK |
| GPIO36 | CS2 | microSD DAT3 / CS |

## 3. Known review items

These items were identified in the earlier project-file audit and design discussions. Recheck each against the current KiCad files before changing the design.

### 3.1 Hierarchical schematic connectivity
- Earlier audit found L4 sheet pins named `SCL`, `SDA`, `PPS`, `RX` and `TX` without corresponding root-sheet connections to the L3 processing signals.
- L3 uses local signal names such as `I2C_SDA`, `I2C_SCL`, `GP02_RX`, `GP02_TX` and `GP-02_PPS`.
- **Action:** connect the hierarchy deliberately and run ERC. Do not assume similarly named local labels connect across hierarchical sheets.

### 3.2 EEPROM identity
- Earlier project audit found `AT24CS32-XHM` (32 Kbit) in the schematic/PCB, while the design notes and README previously stated `AT24C512` (512 Kbit).
- These are materially different memory capacities and not interchangeable BOM descriptions.
- **Action:** inspect the selected physical part / intended MPN, then align symbol, footprint, BOM, firmware driver and documentation.

### 3.3 Output capacitor C8
- Earlier project audit found conflicting metadata: displayed value 220 µF, MPN `UUD1C101MCL1GS` (100 µF / 16 V), purchase reference for 100 µF / 16 V and a Kemet EIA-7343-31 footprint.
- A later 220 µF / 25 V proposal (`UCM1E221MCL1GS`) was discussed but not confirmed as the final selection.
- **Action:** select one exact MPN, verify package / footprint, voltage rating, ESR and the TPS5430 output-capacitor stability requirements.

### 3.4 Input ferrite FB1
- Earlier project audit identified `BLM21SP111SZ1D`, a 0805 metric / 2012 ferrite, assigned a 0603 metric footprint.
- **Action:** correct the footprint to the manufacturer's land pattern and check impedance versus frequency, DC bias and DCR for the actual circuit.

### 3.5 HM-10 connector footprint
- Earlier project audit found the HM-10 connector in the schematic but no matching U4 footprint on the PCB.
- **Action:** if the connector is intended to be PCB-mounted, add and verify its footprint, pin numbering, orientation and mechanical clearance. Otherwise document the off-board wiring arrangement.

### 3.6 microSD pull-ups
- Earlier notes indicate the SCK pull-up is intended DNP; the tracked project snapshot may still show it populated.
- **Action:** confirm the resistor population state and document it in schematic/BOM. Keep the SCK signal connection intact.

### 3.7 Battery-voltage measurement
- Intended divider: 100 kΩ upper, 33 kΩ lower, with 100 nF filtering, connected to GPIO16/A2.
- Earlier review found the power-sheet `VSense` net was not exported to the Teensy ADC signal.
- **Action:** trace the protected battery-positive source through the divider to GPIO16, verify maximum ADC voltage at 8.4 V including tolerance, and confirm the net in the generated netlist.

### 3.8 RTC backup source
- Earlier project review noted a rechargeable-cell intention but a CR2032-style footprint / charge path whose suitability depends on the actual cell chemistry and part number.
- **Action:** identify the exact backup cell. Do not charge a primary CR2032. Approve the R13/D7 charging path only if the cell manufacturer's specification permits it.

### 3.9 KiCad project libraries
- Earlier audit noted the custom Teensy footprint library / project library table may need path validation on another machine.
- **Action:** verify project-relative library paths and 3D model references from a clean clone.

### 3.10 PCB and design-rule status
- An earlier parser-based review reported no routed copper tracks, vias, zones or assigned electrical nets in the PCB snapshot it inspected. This is not a substitute for opening the current board in KiCad.
- **Action:** inspect the current PCB, update from schematic if appropriate, then run native KiCad DRC. No ERC or DRC pass is claimed in this baseline.

## 4. Power-stage qualification register

Current intended topology:

`Battery input → F1 fuse → Q1 P-MOS reverse-polarity protection → D5 TVS → FB1 ferrite → TPS5430 5 V buck → LD1117S33 3.3 V LDO`

Previously discussed candidate parts include:
- F1: Bourns SF-1206F400-2
- Q1: AO3401A
- D4: BZT52C10 gate-source clamp
- D5: SMBJ9.0A TVS
- FB1: Murata BLM21SP111SZ1D
- U5: TPS5430DDA
- L1: 22 µH candidate
- D6: B340A
- U6: LD1117S33TR

These are recorded as candidate / discussed selections, not a complete approved BOM. Before release, verify:
1. Battery minimum and maximum at the board connector under load and transients.
2. Buck minimum-input regulation margin at the required 5 V load.
3. Inductor saturation and RMS current, diode thermal stress and switch-node layout.
4. Input/output capacitor effective capacitance under DC bias, ESR and ripple-current ratings.
5. TVS clamping and fuse coordination for the actual source impedance and transient energy.
6. LDO dissipation, junction temperature and PCB copper thermal performance.
7. Ground return, high-current loop geometry and EMI-sensitive signal routing.

## 5. Review and release sequence

| Gate | Required evidence | State |
|---|---|---|
| G1 — Schematic consistency | Hierarchical connectivity, exact MPNs, pin mapping, ERC report | Pending |
| G2 — Electrical qualification | Power calculations, datasheet checks, current / thermal budget | Pending |
| G3 — Schematic-to-PCB consistency | Updated PCB, footprint and netlist comparison | Pending |
| G4 — PCB completion | Placement, routing, copper zones, mechanical checks | Pending |
| G5 — DRC | Native KiCad DRC report with violations resolved or justified | Pending |
| G6 — Manufacturing package | Gerbers, drill, BOM, CPL and fabrication review | Pending |

## 6. Change-control rules

- Keep the current V1 design on `hardware-v1`.
- Make one logically grouped change per commit.
- Use commit messages that describe the engineering change, e.g. `fix(schematic): connect L4 GNSS hierarchy pins`.
- Keep generated backups, lock files and personal KiCad settings out of version control.
- Record component substitutions with exact MPN, footprint, datasheet reference and reason.
- Do not mark a gate complete without its corresponding report or review evidence.
- Tag a release only after the schematic, PCB and manufacturing outputs are internally consistent.

---

**Baseline note:** This document captures current design intent and previously identified review findings. It does not certify the design as electrically safe, ERC-clean, DRC-clean or ready for manufacture.
