from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

OUT=Path('Reports/RideDAQ_Report_QA'); OUT.mkdir(exist_ok=True)
REG=r'C:\Windows\Fonts\segoeui.ttf'; BOLD=r'C:\Windows\Fonts\seguisb.ttf'
NAVY='#15324B'; TEAL='#167D8D'; INK='#263441'; MUTED='#5F7280'; WHITE='#FFFFFF'; PALE='#EAF3F5'; GREEN='#E5F5EC'; GOLD='#E5A800'; AMBER='#FFF3D6'; LINE='#CBD8DE'; PURPLE='#EEEAFE'; BLUE='#E6F2FF'; RED='#FCE7E7'
def f(sz,b=False): return ImageFont.truetype(BOLD if b else REG,sz)
def center(d,box,lines,sz=24,color=INK,bold=False,gap=7):
 x1,y1,x2,y2=box; ff=f(sz,bold); hs=[d.textbbox((0,0),s,font=ff)[3] for s in lines]; y=y1+((y2-y1)-(sum(hs)+gap*(len(hs)-1)))/2
 for s,h in zip(lines,hs):
  bb=d.textbbox((0,0),s,font=ff); d.text((x1+(x2-x1-(bb[2]-bb[0]))/2,y),s,font=ff,fill=color); y+=h+gap
def box(d,xy,head,subs=(),fill=PALE,edge=TEAL,sz=23):
 d.rounded_rectangle(xy,20,fill=fill,outline=edge,width=3); x1,y1,x2,y2=xy; center(d,(x1+10,y1+8,x2-10,y2-8),[head,*subs],sz,INK,True,7)
def arrow(d,a,b,c=TEAL,w=4):
 d.line((*a,*b),fill=c,width=w); ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=15; d.polygon([b,(b[0]-L*math.cos(ang-.5),b[1]-L*math.sin(ang-.5)),(b[0]-L*math.cos(ang+.5),b[1]-L*math.sin(ang+.5))],fill=c)
def panel(d,xy,title,fill):
 d.rounded_rectangle(xy,22,fill=fill,outline=LINE,width=3); d.rounded_rectangle((xy[0],xy[1],xy[2],xy[1]+62),22,fill=NAVY); d.rectangle((xy[0],xy[1]+35,xy[2],xy[1]+62),fill=NAVY); d.text((xy[0]+22,xy[1]+12),title,font=f(28,True),fill=WHITE)

# Architecture, refreshed based on current schematic/netlist
im=Image.new('RGB',(1800,1120),WHITE); d=ImageDraw.Draw(im); panel(d,(16,16,1784,1104),'RideDAQ V1  |  SYSTEM ARCHITECTURE  •  schematic status', '#F8FAFC')
for x,w,title,fill in [(34,380,'POWER',BLUE),(430,450,'SENSING',AMBER),(896,430,'PROCESSING + TIME',PURPLE),(1342,420,'DATA + LINKS',GREEN)]:
 d.rounded_rectangle((x,104,x+w,1002),18,fill=fill,outline=LINE,width=2); d.text((x+18,122),title,font=f(24,True),fill=NAVY)
box(d,(65,190,390,340),'Protected input',['Fuse • TVS • EMI filtering'],BLUE,sz=20)
box(d,(65,410,390,555),'Regulation',['TPS5430 → +5 V','LD1117S33 → +3.3 V'],GREEN,sz=20)
box(d,(65,625,390,790),'Rail assignments',['+5 V: Teensy VIN, CAN VCC','+3.3 V: sensors, CAN VIO'],WHITE,sz=19)
arrow(d,(228,340),(228,410)); arrow(d,(228,555),(228,625))
box(d,(460,190,830,350),'BMI323 IMU',['I²C • J3 connector','INT not routed'],WHITE,sz=20)
box(d,(460,410,830,570),'BME280',['I²C • shared SDA/SCL'],WHITE,sz=20)
box(d,(460,630,830,790),'GP-02 GNSS connector',['UART3 • RX3 / TX3','PPS → GPIO6'],WHITE,sz=20)
box(d,(460,835,830,965),'Battery sense',['PACK_V_SENSE → GPIO16 / A2'],WHITE,sz=18)
box(d,(925,310,1297,560),'Teensy 4.0',['Acquisition • timing • buffering','RTC DS3231M via I²C'],PURPLE,sz=22)
box(d,(925,665,1297,855),'Power/status control',['GPIO LEDs • rail/sensor checks'],WHITE,sz=20)
box(d,(1370,190,1730,350),'microSD',['SPI2 • primary local logging'],WHITE,sz=20)
box(d,(1370,440,1730,600),'HM-10 header',['UART2 • optional BLE link'],WHITE,sz=20)
box(d,(1370,690,1730,865),'CAN3 + TLE9252VLC',['CAN-FD capable transceiver','Schematic only • PCB pending'],AMBER,edge=GOLD,sz=19)
for y in (270,490,710): arrow(d,(830,y),(925,405),TEAL,3)
arrow(d,(1297,405),(1370,270)); arrow(d,(1297,435),(1370,520)); arrow(d,(1297,475),(1370,775))
d.text((48,1035),'Solid status: schematic/netlist connectivity. CAN-FD rate, PCB footprint/routing and physical validation are not yet confirmed.',font=f(20),fill=MUTED)
im.save(OUT/'RideDAQ_system_architecture_v2.png')

# Pin map, verified functional mapping from the exported KiCad netlist
im=Image.new('RGB',(1800,1180),WHITE); d=ImageDraw.Draw(im); panel(d,(16,16,1784,1164),'RideDAQ V1  |  TEENSY 4.0 PIN MAP  •  verified against KiCad netlist','#F8FAFC')
def table_panel(xy,title,rows):
 x1,y1,x2,y2=xy; d.rounded_rectangle(xy,16,fill=WHITE,outline=LINE,width=2); d.rounded_rectangle((x1,y1,x2,y1+52),16,fill=NAVY); d.rectangle((x1,y1+30,x2,y1+52),fill=NAVY); d.text((x1+15,y1+10),title,font=f(22,True),fill=WHITE)
 yy=y1+66; widths=(.54,.46)
 for idx,(a,b) in enumerate(rows):
  h=47; d.rectangle((x1+10,yy,x2-10,yy+h),fill=GREEN if idx%2==0 else '#F5F8FA',outline=LINE,width=1); d.text((x1+22,yy+9),a,font=f(17,idx==0),fill=INK); d.text((x1+int((x2-x1)*widths[0]),yy+9),b,font=f(17,True),fill=INK); yy+=h
table_panel((40,100,565,497),'STATUS + BLE', [('Function','Teensy GPIO'),('Power LED','GPIO2'),('GNSS LED','GPIO3'),('BLE / logging LED','GPIO4'),('HM-10 TXD → MCU RX2','GPIO7'),('MCU TX2 → HM-10 RXD','GPIO8')])
table_panel((40,522,565,920),'I²C + GNSS', [('Function','Teensy GPIO'),('I²C SDA (shared)','GPIO18'),('I²C SCL (shared)','GPIO19'),('GP-02 TX → MCU RX3','GPIO15'),('MCU TX3 → GP-02 RX','GPIO14'),('GP-02 PPS','GPIO6')])
table_panel((1235,100,1760,497),'microSD • SPI2', [('Function','Teensy GPIO'),('MOSI','GPIO35'),('MISO','GPIO34'),('SCK','GPIO37'),('CS','GPIO36')])
table_panel((1235,522,1760,920),'POWER + CAN3', [('Function','Teensy GPIO'),('PACK_V_SENSE / A2','GPIO16'),('CAN3 RX (CRX3)','GPIO30'),('CAN3 TX (CTX3)','GPIO31'),('TLE9252VLC','Schematic only')])
# Center board icon
d.rounded_rectangle((700,150,1100,860),30,fill='#0F7546',outline='#075331',width=5); d.rounded_rectangle((750,210,1050,795),22,fill='#F1F6F4',outline='#C4D5CD',width=3)
center(d,(760,250,1040,380),['Teensy 4.0','600 MHz Cortex-M7'],30,NAVY,True,9)
d.rounded_rectangle((820,435,980,610),20,fill='#192A36',outline='#111820',width=3); center(d,(825,465,975,580),['i.MX RT1062'],21,WHITE,True)
for i in range(7):
 y=230+i*82; d.ellipse((672,y,705,y+33),fill='#D9B24A',outline='#8E722F',width=2); d.ellipse((1095,y,1128,y+33),fill='#D9B24A',outline='#8E722F',width=2)
center(d,(710,895,1090,1010),['Teensy pin aliases shown','Signal direction is named at module'],19,MUTED,False,6)
d.rounded_rectangle((55,1012,1745,1127),16,fill=AMBER,outline=GOLD,width=2)
center(d,(75,1018,1725,1119),['Notes: BMI323 interrupt is not routed. Teensy 3V3 is an output; do not drive it from the peripheral rail.','Pin functions reflect schematic connectivity; firmware assignments and electrical behavior still require validation.'],19,INK,False,8)
im.save(OUT/'RideDAQ_teensy_pinmap_v2.png')

# Firmware state machine: proposed, with explicit recovery/fault paths
im=Image.new('RGB',(1800,1120),WHITE); d=ImageDraw.Draw(im); panel(d,(16,16,1784,1104),'RideDAQ V1  |  PROPOSED FIRMWARE WORKFLOW STATE MACHINE','#F8FAFC')
def state(xy,title,sub,fill=PALE,edge=TEAL): box(d,xy,title,sub,fill,edge,20)
state((70,165,330,305),'POWER OFF',['Power absent'],WHITE)
state((420,165,720,305),'BOOT / INIT',['Rails • GPIO • buses'],BLUE)
state((820,165,1110,305),'SELF-TEST',['RTC • sensors • SD'],PURPLE)
state((1280,165,1690,305),'READY',['Session can start'],GREEN)
state((1280,425,1690,590),'RECORDING',['Timestamp • sample • buffer','SD writes in bounded blocks'],GREEN)
state((790,425,1120,590),'DEGRADED RECORDING',['Continue valid channels','Flag unavailable inputs'],AMBER,GOLD)
state((790,765,1120,925),'FLUSH / CLOSE',['Drain queue • close file','Store counters / status'],BLUE)
state((1280,765,1690,925),'STORAGE FAULT',['Stop session safely','Wait for SD recovery'],RED,'#C74C4C')
state((420,765,720,925),'SAFE IDLE',['No session active'],WHITE)
arrow(d,(330,235),(420,235)); d.text((344,202),'power good',font=f(16),fill=MUTED)
arrow(d,(720,235),(820,235)); arrow(d,(1110,235),(1280,235)); d.text((1122,198),'core ready',font=f(16),fill=MUTED)
arrow(d,(1485,305),(1485,425)); d.text((1498,345),'Start + SD ready',font=f(16),fill=MUTED)
arrow(d,(1280,500),(1120,500),GOLD); d.text((1138,465),'sensor fault',font=f(16),fill=MUTED)
arrow(d,(955,590),(955,765),TEAL); d.text((972,655),'Stop requested',font=f(16),fill=MUTED)
arrow(d,(1485,590),(1485,765),'#C74C4C'); d.text((1500,650),'write error / full',font=f(16),fill='#9B3333')
arrow(d,(1120,845),(1280,845),TEAL); d.text((1130,807),'close complete',font=f(16),fill=MUTED)
arrow(d,(1280,875),(1120,875),'#C74C4C'); d.text((1115,927),'re-init succeeds',font=f(16),fill='#9B3333')
arrow(d,(790,845),(720,845),TEAL); arrow(d,(570,765),(570,305),TEAL)
arrow(d,(820,205),(720,205),'#C74C4C'); d.text((718,140),'core init fails → safe idle / retry',font=f(16),fill='#9B3333')
arrow(d,(1110,195),(1280,195),GOLD,3); d.text((1105,135),'noncritical fault → READY with warning',font=f(16),fill='#946A00')
d.rounded_rectangle((70,1000,1715,1070),14,fill=AMBER,outline=GOLD,width=2)
center(d,(85,1005,1700,1065),['Design proposal only — firmware implementation is not present in the inspected hardware project. Sudden power loss can discard buffered records.'],18,INK,False)
im.save(OUT/'RideDAQ_firmware_state_machine.png')
print('Wrote refreshed architecture, pin map, and firmware state machine.')
