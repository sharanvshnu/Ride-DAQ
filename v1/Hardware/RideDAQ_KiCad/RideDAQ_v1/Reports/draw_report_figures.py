from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap
root=Path('Reports/RideDAQ_Report_QA'); root.mkdir(exist_ok=True)
fontreg=r'C:\Windows\Fonts\segoeui.ttf'; fontbold=r'C:\Windows\Fonts\seguisb.ttf'
NAVY='#15324B'; TEAL='#167D8D'; PALE='#EAF3F5'; INK='#263441'; MUTED='#5F7280'; WHITE='#FFFFFF'; LINE='#9CB3BF'; GOLD='#D38B2C'
def ft(size,b=False): return ImageFont.truetype(fontbold if b else fontreg,size)
def center_text(draw, box, lines, font, fill=INK, gap=5):
 x1,y1,x2,y2=box; heights=[]
 for s in lines:
  bb=draw.textbbox((0,0),s,font=font); heights.append(bb[3]-bb[1])
 total=sum(heights)+gap*(len(lines)-1); y=y1+(y2-y1-total)/2
 for s,h in zip(lines,heights):
  bb=draw.textbbox((0,0),s,font=font); w=bb[2]-bb[0]
  draw.text((x1+(x2-x1-w)/2,y),s,font=font,fill=fill); y+=h+gap
def box(draw, xy, title, sub, fill=PALE, width=3):
 draw.rounded_rectangle(xy,radius=22,fill=fill,outline=TEAL,width=width)
 x1,y1,x2,y2=xy; center_text(draw,(x1+10,y1+8,x2-10,y2-8),[title]+sub,ft(28,True) if len(title)<26 else ft(24,True),INK,8)
def arrow(draw,a,b,color=TEAL,w=5):
 draw.line((a,b),fill=color,width=w)
 import math
 ang=math.atan2(b[1]-a[1],b[0]-a[0]); l=16
 p1=(b[0]-l*math.cos(ang-.55),b[1]-l*math.sin(ang-.55)); p2=(b[0]-l*math.cos(ang+.55),b[1]-l*math.sin(ang+.55))
 draw.polygon([b,p1,p2],fill=color)
# Architecture
im=Image.new('RGB',(1700,740),'white'); d=ImageDraw.Draw(im)
d.rounded_rectangle((22,18,1678,720),radius=28,fill='#F7FAFB',outline='#CBD8DE',width=3)
d.text((58,42),'RideDAQ system architecture',font=ft(37,True),fill=NAVY)
d.text((60,94),'Power path',font=ft(22,True),fill=TEAL)
box(d,(55,135,425,270),'Vehicle input',['Protected board input'])
box(d,(650,135,1055,270),'Power conditioning',['Fuse / transient protection','Buck and 3.3 V regulation'])
box(d,(1275,135,1635,270),'Board rails',['+5 V and +3.3 V'])
arrow(d,(425,202),(650,202)); arrow(d,(1055,202),(1275,202))
d.text((60,324),'Measurement and data path',font=ft(22,True),fill=TEAL)
box(d,(55,365,435,555),'Sensors',['BMI323 motion IMU','BME280 environment'])
box(d,(565,365,1015,555),'Processing and time',['Teensy 4.0','RTC / acquisition / buffering'],fill='#E4F1F3')
box(d,(1150,365,1635,475),'Storage',['microSD primary record'])
box(d,(1150,515,1635,625),'Communication',['Bluetooth serial • CAN / CAN-FD'])
arrow(d,(435,460),(565,460)); d.line((1015,460,1080,460,1080,420),fill=TEAL,width=5); arrow(d,(1080,420),(1150,420)); d.line((1080,460,1080,570),fill=TEAL,width=5); arrow(d,(1080,570),(1150,570))
# rails drop to domains
d.line((1455,270,1455,315,790,315,790,365),fill=GOLD,width=4)
d.polygon([(790,365),(781,348),(799,348)],fill=GOLD)
d.text((1105,284),'Rails power each block',font=ft(18,True),fill=GOLD)
d.text((60,665),'Current scope: CAN-FD is in the schematic; PCB footprint, routing and prototype validation remain open.',font=ft(19),fill=MUTED)
im.save(root/'RideDAQ_system_architecture.png')
# workflow
im=Image.new('RGB',(1700,420),'white'); d=ImageDraw.Draw(im)
d.rounded_rectangle((22,18,1678,402),radius=28,fill='#F7FAFB',outline='#CBD8DE',width=3)
d.text((58,38),'RideDAQ measurement workflow',font=ft(35,True),fill=NAVY)
labels=[('1  Prepare',['Mount • power','configure']),('2  Self-check',['Rails • RTC','sensors • SD']),('3  Acquire',['Timed motion','and context']),('4  Buffer',['Timestamp •','queue • monitor']),('5  Store / link',['SD primary','CAN / BLE optional']),('6  Verify',['Close file •','check integrity']),('7  Analyze',['Calibrate • filter','report limits'])]
xs=[45,280,515,750,985,1220,1455]
for i,(title,sub) in enumerate(labels):
 x=xs[i]; fill=('#E4F1F3' if i in (2,3,4) else PALE)
 d.rounded_rectangle((x,142,x+200,312),radius=18,fill=fill,outline=TEAL,width=3)
 center_text(d,(x+8,150,x+192,305),[title]+sub,ft(20,True) if i not in (4,6) else ft(18,True),INK,10)
 if i<len(labels)-1: arrow(d,(x+200,227),(xs[i+1],227),w=4)
d.text((55,342),'Acquisition continues if an optional communication link is unavailable; faults and dropped records should be counted.',font=ft(18),fill=MUTED)
im.save(root/'RideDAQ_workflow.png')
print('Created architecture and workflow figures')
