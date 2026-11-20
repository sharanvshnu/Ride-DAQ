from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.section import WD_SECTION
from pathlib import Path

out=Path('Reports/RideDAQ_PreStage_Work_Report.docx')
doc=Document()
sec=doc.sections[0]
sec.top_margin=Inches(.62); sec.bottom_margin=Inches(.58); sec.left_margin=Inches(.72); sec.right_margin=Inches(.72)
sec.header_distance=Inches(.28); sec.footer_distance=Inches(.28)
styles=doc.styles
styles['Normal'].font.name='Aptos'; styles['Normal'].font.size=Pt(9.5); styles['Normal'].font.color.rgb=RGBColor(38,52,65)
styles['Normal'].paragraph_format.space_after=Pt(4); styles['Normal'].paragraph_format.line_spacing=1.05
for name,size,color in [('Title',29,'15324B'),('Heading 1',19,'15324B'),('Heading 2',12,'167D8D'),('Heading 3',10,'167D8D')]:
 s=styles[name]; s.font.name='Aptos Display' if name in ('Title','Heading 1') else 'Aptos'; s.font.size=Pt(size); s.font.bold=name!='Title' or True; s.font.color.rgb=RGBColor.from_string(color)
 s.paragraph_format.space_before=Pt(8); s.paragraph_format.space_after=Pt(4); s.paragraph_format.keep_with_next=True
# header
h=sec.header.paragraphs[0]; h.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=h.add_run('RideDAQ  |  PRE-STAGE WORK REPORT'); r.bold=True; r.font.size=Pt(8); r.font.color.rgb=RGBColor(22,125,141)
# footer page field
f=sec.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.CENTER
rr=f.add_run('RideDAQ V1  •  17 November 2026  |  Page '); rr.font.size=Pt(8); rr.font.color.rgb=RGBColor(100,115,125)
fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); f._p.append(fld)

def para(text='',style=None,boldlead=None):
 p=doc.add_paragraph(style=style)
 if boldlead and text.startswith(boldlead):
  p.add_run(boldlead).bold=True; p.add_run(text[len(boldlead):])
 else: p.add_run(text)
 return p

def heading(t,l=1): doc.add_heading(t,level=l)
def bullet(t):
 p=doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after=Pt(2); p.add_run(t); return p
def numbered(t):
 p=doc.add_paragraph(style='List Number'); p.paragraph_format.space_after=Pt(2); p.add_run(t); return p
def shade(cell,fill):
 tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)
def set_cell(cell,text,bold=False,color='263441',size=8.5):
 cell.text=''; cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
 p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(1); p.paragraph_format.space_before=Pt(1)
 r=p.add_run(text); r.bold=bold; r.font.name='Aptos'; r.font.size=Pt(size); r.font.color.rgb=RGBColor.from_string(color)
def table(headers,rows,widths=None):
 t=doc.add_table(rows=1,cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.style='Table Grid'
 for i,x in enumerate(headers): set_cell(t.rows[0].cells[i],x,True,'FFFFFF',8.5); shade(t.rows[0].cells[i],'15324B')
 for row in rows:
  cells=t.add_row().cells
  for i,x in enumerate(row): set_cell(cells[i],x,size=8)
 for row in t.rows:
  for i,w in enumerate(widths or []): row.cells[i].width=Inches(w)
 return t

def pagebreak(): doc.add_page_break()

# PAGE 1
p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(30); p.paragraph_format.space_after=Pt(5)
r=p.add_run('RideDAQ'); r.bold=True; r.font.name='Aptos Display'; r.font.size=Pt(31); r.font.color.rgb=RGBColor(21,50,75)
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(16)
r=p.add_run('Pre-Stage Work Report'); r.font.size=Pt(18); r.font.color.rgb=RGBColor(22,125,141)
para('Ride Quality Data Acquisition System | Hardware Revision V1 | 17 November 2026')
heading('Executive summary',1)
para('RideDAQ is a vehicle-mounted data acquisition platform intended to capture motion and environmental signals, timestamp and store measurements, and provide local or vehicle-network access. The current KiCad design is centered on a Teensy 4.0 and includes a BMI323 six-axis IMU interface, BME280 environmental sensing, real-time clock, microSD storage, Bluetooth serial connector, vehicle-input conditioning and a CAN-FD interface now shown at schematic level. This is a pre-stage engineering report: it documents the design basis, proposed firmware and validation plan, and current implementation status. It does not claim that the PCB is routed, fabricated, firmware-complete, calibrated or field-tested.')
heading('1. Introduction',1)
para('Ride quality is shaped by vibration and motion transmitted through a vehicle, together with operating context such as speed, route, load and environmental conditions. A compact logger can make these conditions observable over a journey by synchronizing sensor samples with time and retaining records for later analysis. RideDAQ is being developed as an embedded measurement node: it combines motion sensing, contextual sensing, removable storage and communication on one electronics platform.')
para('The project’s immediate goal is a robust prototype architecture that can be mounted in or near a vehicle, powered from its electrical system, and used to collect repeatable datasets. The present work focuses on electronics definition and system-level planning. Signal interpretation, ride-quality scoring and vehicle-specific conclusions require later calibration and test data.')
heading('2. Problem statement',1)
para('Vehicle ride assessment often relies on subjective impressions or measurements gathered with separate instruments that are difficult to synchronize and compare. The project addresses the need for an affordable, compact and extensible system that records motion and supporting context in a consistent, inspectable format. Key engineering challenges include sensor placement and calibration, vehicle power transients, reliable timestamping and storage, vibration-resistant packaging, and a communications interface that does not compromise acquisition.')
heading('3. Relevance of the project',1)
para('RideDAQ can support prototype evaluation, comparative road or suspension studies, troubleshooting and educational work by making time-series measurements available for offline analysis. Its modular design is relevant because logging, sensor selection and communications can be developed in stages. The instrument is intended to support measurement and engineering decisions; it is not itself a certified vehicle safety device or a substitute for a calibrated laboratory instrument.')

# PAGE 2
pagebreak(); heading('4. Literature survey and design basis',1)
para('The literature and component documentation inform the measurement channels, communication link and limits of interpretation. The sources below are design references, not evidence that the assembled RideDAQ meets a standard or has achieved a specified measurement accuracy.')
table(['Reference area','Design implication for RideDAQ'],[
('Whole-body vibration — ISO 2631-1 [1]','Provides a framework for evaluating human exposure to whole-body vibration. Sensor axis, mounting, frequency weighting, exposure duration and evaluation method matter; raw acceleration alone is not a standards-based comfort or health rating.'),
('CAN FD — Bosch / ISO 11898-1 [2]','CAN FD expands payload capacity to 64 bytes and allows a faster data phase than Classical CAN. All nodes, controller timing, transceiver capability, wiring and termination must be compatible.'),
('Motion measurement — Bosch BMI323 [3]','A 3-axis accelerometer and 3-axis gyroscope provide translational and angular-rate data. Configurable range, output rate, filtering, mounting and calibration determine useful bandwidth and data quality.'),
('Environmental context — Bosch BME280 [4]','Pressure, relative humidity and temperature can accompany motion records as context. These measurements describe local ambient conditions and should not be interpreted as vehicle-dynamics channels.'),
('Embedded platform — PJRC Teensy 4.0 [5]','The high-performance Cortex-M7 platform provides multiple serial interfaces and CAN capability. The selected CAN controller instance and exposed pad routing must match firmware pin mapping and PCB footprint.'),
('Automotive CAN physical layer — Infineon TLE9252V [6]','The selected TLE9252VLC transceiver supports CAN/CAN-FD physical signaling up to 5 Mbit/s and provides separate VCC/VIO supplies. That rating is a component capability, not the achieved system bus speed.')],[1.55,5.65])
heading('4.1 Design gap addressed',2)
para('A useful pre-stage logger needs more than sensors on a microcontroller: it needs a coherent path from vehicle input protection through stable rails, sensor acquisition, time association, buffering and durable storage. It also needs a defined method to validate the measurements. RideDAQ brings these functions into one planned platform, while leaving calibration, firmware timing and vehicle-level performance as explicit development tasks.')
heading('5. Objectives and scope',1)
bullet('Integrate a motion sensor and environmental/context sensors with a common processor and timestamp source.')
bullet('Record structured data to removable storage and provide a path for configuration or data access over serial/Bluetooth and CAN/CAN-FD.')
bullet('Condition the vehicle supply and provide 5 V and 3.3 V rails for system electronics.')
bullet('Develop a repeatable workflow for configuration, acquisition, file integrity checks, analysis and prototype validation.')
bullet('Keep measurable performance claims pending until sample rate, mounting, calibration, firmware and bench/vehicle tests are documented.')

# PAGE 3
pagebreak(); heading('6. System architecture',1)
para('The design is partitioned into four cooperating layers: vehicle power and protection, sensor inputs, processing and timing, and storage/communications. The block diagram describes intended system flow; it is an architectural view, not a production wiring diagram.')
# architecture table
arch=table(['Layer','Current design elements','Role / data flow'],[
('Power input','Vehicle/input connector; fuse and transient-protection elements; buck and 3.3 V regulation','Protect and convert the external supply into board rails. Measure input through the PACK_V_SENSE divider.'),
('Sensing','BMI323 IMU interface; BME280 pressure/humidity/temperature; vehicle/auxiliary connector shown as GP-02','Capture motion and context. Confirm final sensor mounting, interface details and source pinouts.'),
('Processing and time','Teensy 4.0; DS3231M RTC; I²C/SPI/UART GPIO','Acquire samples, associate timestamps, buffer records, manage status and coordinate output.'),
('Data and links','microSD; HM-10 Bluetooth serial header; TLE9252VLC CAN/CAN-FD schematic interface','Persist datasets locally and provide selected live/status or vehicle-network communications.')],[1.15,2.45,3.6])
for row in arch.rows[1:]:
 for c in row.cells: c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
heading('6.1 Hardware design notes',2)
para('The project schematic is hierarchical, with power conditioning, processing and sensing sheets plus dedicated RTC, SD-card and BME280 sheets. The processing sheet routes the Teensy CAN3 TX/RX signals to the TLE9252VLC. The transceiver uses the existing +5 V supply at VCC and +3.3 V at VIO; VBAT is connected to the protected input net. EN and NSTB are held high, WAKE is grounded, and NERR/INH are left unused. A 120 Ω termination is shown as default-DNP and should only be fitted when this node is at a physical bus end.')
para('The current PCB has a board outline and 75 placed footprints, but the project review found no copper tracks, vias or copper zones. The CAN transceiver footprint is still unassigned pending verification of the exact PG-TSON-14 land pattern. Thus the CAN feature is at schematic stage and is not yet part of the routed PCB.')
heading('6.2 Interfaces and data ownership',2)
para('The processor owns sampling schedules and record framing. The RTC provides wall-clock reference; a monotonic timer should be retained for sample intervals so clock adjustments do not distort timing. SD storage is the primary record. Bluetooth and CAN are secondary outputs or configuration paths and should not block acquisition when a link is unavailable.')

# PAGE 4
pagebreak(); heading('7. Firmware architecture',1)
para('No firmware source was present in the inspected KiCad hardware project. The architecture below is therefore a proposed implementation plan, not a description of already-written code.')
table(['Firmware module','Responsibility','Failure handling / design rule'],[
('Board startup','Initialize clocks, GPIO, buses, sensors, RTC, SD card and communication interfaces; expose self-test results.','Report unavailable modules explicitly; do not silently claim successful logging.'),
('Sensor drivers','Read BMI323 motion data and BME280 environmental data; apply sensor configuration and convert raw codes.','Check device identity/status, bus errors, saturation and stale data; retain raw values where practical.'),
('Time and scheduler','Maintain acquisition cadence and timestamp samples using monotonic timing plus RTC epoch.','Detect missed deadlines and clock invalidity; avoid blocking delays in acquisition paths.'),
('Acquisition pipeline','Collect samples into timestamped records and a bounded RAM queue.','Define overflow behavior and counters; protect high-rate IMU sampling from slow storage writes.'),
('Storage manager','Create session files, append records, flush safely, rotate files and close sessions cleanly.','Use headers, versioning, checksums or validation markers; track card-full and write failures.'),
('Communications','Provide bounded status/configuration over Bluetooth serial; frame selected signals for CAN/CAN-FD.','Communication tasks must not stall sampling. Define message identifiers, units, scaling and rate limits.'),
('Diagnostics','Track uptime, reset cause, rail/input readings if sampled, sensor health, dropped samples and storage state.','Make faults observable in status output and in the recorded session metadata.')],[1.25,3.1,2.85])
heading('7.1 Proposed record model',2)
para('Each session should start with a metadata header containing firmware and schema version, device identifier, RTC validity, sensor configuration, units, axis convention, calibration identifiers and start time. Records should carry a sequence number, monotonic timestamp, optional UTC timestamp, IMU axes, environmental values and status flags. The final file format and sampling rate must be selected after storage-rate and analysis requirements are quantified.')
heading('7.2 Scheduling approach',2)
para('Use a periodic acquisition task for the IMU, with the actual rate selected after bandwidth and vibration targets are defined. Poll or schedule the slower environmental channel separately. Send complete records to storage in buffered blocks, and service communication on independent bounded tasks. Measure worst-case execution time, queue depth and dropped-sample count during stress testing before choosing final rates.')
heading('7.3 Data interpretation boundary',2)
para('Acceleration, angular rate, ambient pressure and temperature are primary measurements. Derived ride metrics—such as weighted RMS acceleration, vibration dose or event classification—belong in a later validated analysis pipeline. They require documented filters, coordinate transforms, sampling adequacy, calibration and a clear mapping to the chosen evaluation method.')

# PAGE 5
pagebreak(); heading('8. End-to-end workflow',1)
para('The workflow is designed to make the path from setup to defensible analysis visible and repeatable.')
for x in [
'Pre-test inspection: check mounting, connector retention, SD-card space, supply wiring, CAN termination and sensor orientation. Record the vehicle, route, load and test configuration.',
'Power-up and self-test: confirm supply rails and input sense, initialize the RTC, identify sensors, mount the SD card and report readiness or faults.',
'Configure acquisition: load the selected sampling rates, ranges, filters, axis convention, record schema and communication settings; store the configuration in the session header.',
'Acquire: sample the IMU on a controlled schedule, read slower context channels, attach timestamps and status, buffer records, and write blocks to storage.',
'Communicate: emit only chosen live summaries or messages; if a CAN node is configured, use agreed identifiers, bit timing and bus termination. Keep logging independent of link availability.',
'Close and verify: flush and close the file, record session end and counters, then validate record count, timestamps, checksum/parseability and any dropped samples.',
'Analyze and report: retain raw data, apply calibrated processing, document filtering and exclusions, summarize results with uncertainty and compare only with an appropriate evaluation framework.'
]: numbered(x)
heading('8.1 Operating-state story',2)
table(['State','Expected design behavior','Pre-stage check'],[
('Power-up','Power conditioning creates board rails; processor checks subsystems.','Verify rail startup, input transients, brownout and restart behavior.'),
('Logging','Acquisition and storage proceed from independent bounded tasks.','Stress SD writes while measuring sample loss and timing jitter.'),
('Link absent','Local logging continues without Bluetooth/CAN peer.','Disconnect links and confirm no acquisition stall.'),
('CAN active','Teensy CAN3 logic connects through TLE9252VLC to CANH/CANL.','Assign footprint; verify controller timing, peer compatibility, termination and bus fault behavior.'),
('Low supply / sensor error','Fault is detected, logged where possible and exposed in status.','Inject controlled supply and bus faults; verify restart and record integrity.')],[1.0,3.15,3.05])
heading('9. Expected outcomes',1)
bullet('A reviewed, complete schematic and mechanically constrained two-layer PCB with the CAN-FD hardware incorporated after footprint and land-pattern verification.')
bullet('Firmware that samples the chosen sensors, timestamps and stores structured sessions, monitors faults and exposes useful status.')
bullet('A validated data pipeline with documented sampling configuration, axis convention, units, file schema and analysis steps.')
bullet('Bench evidence for power behavior, sensor communication, RTC timekeeping, SD integrity, Bluetooth/CAN links and recovery from expected faults.')
bullet('Prototype datasets that enable comparison across controlled runs; any ride-quality conclusions will be bounded by calibration and test method.')

# PAGE 6
pagebreak(); heading('10. Current readiness and staged work plan',1)
table(['Work package','Current status','Next evidence / exit condition'],[
('Schematic','Core hierarchical design is present. CAN-FD transceiver added to processing sheet; PACK_V_SENSE link to Teensy ADC was corrected. ERC: 0 errors, 13 warnings.','Review warnings and signal/power states; verify VBAT range and CAN3 pin mapping.'),
('PCB','Outline and 75 footprints exist; board is unrouted. Prior DRC recorded 152 unconnected items and one courtyard-overlap error.','Verify Teensy footprint/pad map, assign TLE footprint, place CAN parts, route, zone and rerun DRC.'),
('Firmware','Architecture proposed in this report; firmware implementation not evidenced in the inspected hardware project.','Implement drivers, scheduler, buffering, session file format, diagnostics and communications.'),
('Prototype validation','No completed bench or vehicle test results are recorded here.','Run staged bring-up, calibration, storage stress, CAN interoperability and controlled field trials.')],[1.1,3.05,3.05])
heading('10.1 Key risks and mitigations',2)
bullet('Vehicle electrical transients: confirm protection and regulator limits against the intended input environment; test startup, crank-like dips and transients before vehicle deployment.')
bullet('Mechanical coupling: define the enclosure, mounting points, sensor axis and mounting stiffness; avoid claiming vehicle-body vibration without a defined installation method.')
bullet('Timing and data loss: quantify sample rate and SD throughput; use buffering, counters and file integrity checks.')
bullet('CAN integration: verify TLE9252VLC land pattern, supply range at VBAT, proper bus topology and end-of-line termination; firmware and hardware must agree on bit timing.')
bullet('Measurement validity: calibrate and document sensor orientation, scale, filtering and uncertainty; use ISO 2631-1 only as an evaluation framework where the test purpose fits.')
heading('11. Conclusion',1)
para('RideDAQ has a credible pre-stage architecture for synchronized vehicle motion and context logging. The hardware definition already links the major sensing, timing, storage and processing blocks, and a CAN-FD physical-layer interface has been added at schematic level. The main transition now is from schematic intent to a buildable and testable instrument: resolve footprint and PCB issues, establish firmware behavior, define a measurement protocol, and collect validation evidence before making performance claims.')
heading('References',1)
refs=[
'[1] ISO, ISO 2631-1:1997, Mechanical vibration and shock — Evaluation of human exposure to whole-body vibration — Part 1: General requirements. https://www.iso.org/standard/7612.html (accessed 17 Nov 2026).',
'[2] Bosch Semiconductors, CAN FD Protocol; CAN FD frame and data-rate overview. https://www.bosch-semiconductors.com/products/ip-modules/can-protocols/can-fd/ (accessed 17 Nov 2026).',
'[3] Bosch Sensortec, BMI323 Datasheet, BST-BMI323-DS000. https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmi323-ds000.pdf (accessed 17 Nov 2026).',
'[4] Bosch Sensortec, BME280 Datasheet, BST-BME280-DS002. https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf (accessed 17 Nov 2026).',
'[5] PJRC, Teensy 4.0 technical information and pinout. https://www.pjrc.com/store/teensy40.html (accessed 17 Nov 2026).',
'[6] Infineon Technologies, TLE9252V High-Speed CAN FD Transceiver Datasheet. https://www.infineon.com/assets/row/public/documents/10/49/infineon-tle9252v-datasheet-en.pdf (accessed 17 Nov 2026).',
'[7] RideDAQ V1 project artifacts: hierarchical KiCad schematic, PCB, BOM, CAN interface design note and CAN logic review, inspected 17 Nov 2026.'
]
for x in refs:
 p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(2); p.paragraph_format.left_indent=Inches(.15); p.paragraph_format.first_line_indent=Inches(-.15)
 r=p.add_run(x); r.font.size=Pt(7.4); r.font.color.rgb=RGBColor(55,68,78)

# Core properties
doc.core_properties.title='RideDAQ Pre-Stage Work Report'
doc.core_properties.subject='Ride quality data acquisition system: design basis, architecture and validation plan'
doc.core_properties.author='RideDAQ Project'
doc.save(out)
print(out.resolve())
