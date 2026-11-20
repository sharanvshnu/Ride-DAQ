from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph
from pathlib import Path

source=Path('Reports/RideDAQ_PreStage_Work_Report.docx')
out=Path('Reports/RideDAQ_PreStage_Work_Report_Updated.docx')
d=Document(source)
def find(text): return next(x for x in d.paragraphs if x.text.strip()==text or x.text.strip().startswith(text[:100]))
def set_text(par,text):
 par.clear(); par.add_run(text)
def remove_par(par): par._p.getparent().remove(par._p)
def image_after(anchor,path,width,caption):
 par=d.add_paragraph(); par.alignment=WD_ALIGN_PARAGRAPH.CENTER; par.paragraph_format.space_before=Pt(2); par.paragraph_format.space_after=Pt(1); par.add_run().add_picture(str(path),width=Inches(width))
 cp=d.add_paragraph(); cp.alignment=WD_ALIGN_PARAGRAPH.CENTER; cp.paragraph_format.space_after=Pt(3); rr=cp.add_run(caption); rr.italic=True; rr.font.size=Pt(8); rr.font.color.rgb=RGBColor(95,114,128)
 anchor._p.addnext(par._p); par._p.addnext(cp._p)

# Page 1: concise project framing plus the refreshed mechanical concept board.
set_text(find('RideDAQ is a vehicle-mounted data acquisition platform intended to capture motion and environmental signals, timestamp and store measurements, and provide local or vehicle-network access. The current KiCad design is centered on a Teensy 4.0 and includes a BMI323 six-axis IMU interface, BME280 environmental sensing, real-time clock, microSD storage, Bluetooth serial connector, vehicle-input conditioning and a CAN-FD interface now shown at schematic level. This is a pre-stage engineering report: it documents the design basis and next validation steps; it does not claim a finished or tested product.'),
'RideDAQ is a Teensy 4.0 based vehicle data logger for synchronized motion and context measurements. The KiCad design includes BMI323 and BME280 sensing, RTC, microSD, an HM-10 serial interface and a CAN-FD physical layer at schematic stage. This pre-stage report records the design basis and validation work still required; it does not claim a tested product.')
set_text(find('Ride quality is shaped by vibration and motion transmitted through a vehicle, together with operating context such as speed, route, load and environmental conditions. A compact logger can make these conditions observable over a journey by synchronizing sensor samples with time and retaining records for later analysis. RideDAQ is being developed as an embedded measurement node: it combines motion sensing, contextual sensing, removable storage and communication on one electronics platform.'),
'Ride quality depends on vibration and motion together with operating context. A compact logger can make these conditions observable by synchronizing sensor samples and retaining them for later analysis. RideDAQ combines motion sensing, contextual inputs, removable storage and communication on one embedded platform.')
remove_par(find('The project’s immediate goal is a robust prototype architecture that can be mounted in or near a vehicle, powered from its electrical system, and used to collect repeatable datasets. The present work focuses on electronics definition and system-level planning. Signal interpretation, ride-quality scoring and vehicle-specific conclusions require later calibration and test data.'))
set_text(find('Vehicle ride assessment often relies on subjective impressions or measurements gathered with separate instruments that are difficult to synchronize and compare. The project addresses the need for an affordable, compact and extensible system that records time-series measurements in a consistent, inspectable format. Key engineering challenges include sensor placement and calibration, vehicle power transients, reliable timestamping and storage, vibration-resistant packaging, and a communications interface that does not compromise acquisition.'),
'Ride assessment often relies on subjective impressions or separate instruments that are difficult to synchronize. RideDAQ addresses the need for a compact, extensible logger that records comparable time-series data. Key challenges are sensor placement, power transients, timestamping, storage integrity and a communication path that cannot interrupt acquisition.')
set_text(find('RideDAQ can support prototype evaluation, comparative road or suspension studies, troubleshooting and educational work by making time-series measurements available for offline analysis. Its modular design is relevant because logging, sensor selection and communications can be developed in stages. The instrument is intended to support measurement and engineering decisions; it is not itself a certified vehicle safety device or a substitute for a calibrated laboratory instrument.'),
'RideDAQ can support prototype evaluation, road or suspension comparisons, troubleshooting and education through offline analysis of recorded measurements. Its modular design supports staged development. It is a measurement aid, not a certified safety device or substitute for calibrated laboratory equipment.')
image_after(find('RideDAQ can support prototype evaluation, road or suspension comparisons, troubleshooting and education through offline analysis of recorded measurements. Its modular design supports staged development. It is a measurement aid, not a certified safety device or substitute for calibrated laboratory equipment.'),'Reports/RideDAQ_Report_QA/RideDAQ_enclosure_concept.png',6.85,'Figure 1. Enclosure and mounting concept; dimensions, PCB fit and environmental sealing remain unverified.')

# Replace architecture infographic with refreshed schematic-checked version.
fig=find('Figure 1. RideDAQ hardware and data-path architecture.')
imgpara=fig._p.getprevious()
for shape in imgpara.xpath('.//w:drawing'): shape.getparent().getparent().remove(shape.getparent())
Paragraph(imgpara,d._body).add_run().add_picture('Reports/RideDAQ_Report_QA/RideDAQ_system_architecture_v2.png',width=Inches(6.9))
set_text(fig,'Figure 2. Schematic-checked system architecture; CAN-FD PCB integration remains pending.')

# Page 4: make the pin map the visual anchor and retain a concise firmware design note.
fwtable=next(t for t in d.tables if t.rows[0].cells[0].text.strip()=='Firmware module')
fwtable._tbl.getparent().remove(fwtable._tbl)
intro=find('No firmware source was present in the inspected KiCad hardware project. The architecture below is therefore a proposed implementation plan, not a description of already-written code.')
set_text(intro,'No firmware source was present in the inspected KiCad hardware project. The pin map below reflects schematic connectivity; task scheduling, fault handling and record format remain proposed firmware work.')
for exact in [
'7.1 Proposed record model','Each session should start with a metadata header containing firmware and schema version, device identifier, RTC validity, sensor configuration, units, axis convention, calibration identifiers and start time. Records should carry a sequence number, monotonic timestamp, optional UTC timestamp, IMU axes, environmental values and status flags. The final file format and sampling rate must be selected after storage-rate and analysis requirements are quantified.',
'7.2 Scheduling approach','Use a periodic acquisition task for the IMU, with the actual rate selected after bandwidth and vibration targets are defined. Poll or schedule the slower environmental channel separately. Send complete records to storage in buffered blocks, and service communication on independent bounded tasks. Measure worst-case execution time, queue depth and dropped-sample count during stress testing before choosing final rates.',
'7.3 Data interpretation boundary','Acceleration, angular rate, ambient pressure and temperature are primary measurements. Derived ride metrics—such as weighted RMS acceleration, vibration dose or event classification—belong in a later validated analysis pipeline. They require documented filters, coordinate transforms, sampling adequacy, calibration and a clear mapping to the chosen evaluation method.'
]:
 try: remove_par(find(exact))
 except StopIteration: pass
image_after(intro,'Reports/RideDAQ_Report_QA/RideDAQ_teensy_pinmap_v2.png',6.85,'Figure 3. Teensy GPIO mapping checked against the exported KiCad netlist.')
para=d.add_paragraph('Firmware design rule: use monotonic timestamps for sample intervals, buffer records before SD writes, count missed samples, and keep optional BLE/CAN work bounded so it cannot stall acquisition. Define the session schema and sampling rates after storage and measurement requirements are quantified.')
para.paragraph_format.space_after=Pt(2)
pin_caption=find('Figure 3. Teensy GPIO mapping checked against the exported KiCad netlist.')
pin_caption._p.addnext(para._p)

# Page 5: replace linear workflow with explicit firmware states and fault paths.
wf=find('Figure 2. Proposed acquisition and data-handling workflow.')
oldimg=wf._p.getprevious()
for shape in oldimg.xpath('.//w:drawing'): shape.getparent().getparent().remove(shape.getparent())
Paragraph(oldimg,d._body).add_run().add_picture('Reports/RideDAQ_Report_QA/RideDAQ_firmware_state_machine.png',width=Inches(6.9))
set_text(wf,'Figure 4. Proposed firmware state machine with degraded operation and SD recovery paths.')
oper=find('8.1 Operating-state story')
op_table=next(t for t in d.tables if t.rows[0].cells[0].text.strip()=='State')
op_table._tbl.getparent().remove(op_table._tbl)
set_text(oper,'8.1 Operating-state assumptions')
note=d.add_paragraph('SD is required before a session starts. A sensor fault allows remaining valid channels to continue with status flags; SD write failure stops the session safely. Recovery and power-loss behavior must be implemented and bench-tested.')
note.paragraph_format.space_after=Pt(3)
wf._p.addnext(note._p)

# Refresh repeated figure numbering in the existing text and properties.
d.core_properties.title='RideDAQ Pre-Stage Work Report'
d.save(out)
print(out.resolve())
