p='Reports/draw_report_figures.py'
s=open(p,encoding='utf-8').read()
s=s.replace("box(d,(1150,365,1395,555),'Storage',['microSD'])\nbox(d,(1450,365,1635,555),'Links',['Bluetooth serial','CAN / CAN-FD'])\narrow(d,(435,460),(565,460)); arrow(d,(1015,460),(1150,460)); arrow(d,(1015,500),(1450,500))", "box(d,(1150,365,1635,475),'Storage',['microSD primary record'])\nbox(d,(1150,515,1635,625),'Communication',['Bluetooth serial • CAN / CAN-FD'])\narrow(d,(435,460),(565,460)); d.line((1015,460,1080,460,1080,420),fill=TEAL,width=5); arrow(d,(1080,420),(1150,420)); d.line((1080,460,1080,570),fill=TEAL,width=5); arrow(d,(1080,570),(1150,570))")
s=s.replace("d.text((60,625),'Current scope: CAN-FD is in the schematic; PCB footprint, routing and prototype validation remain open.',font=ft(19),fill=MUTED)", "d.text((60,665),'Current scope: CAN-FD is in the schematic; PCB footprint, routing and prototype validation remain open.',font=ft(19),fill=MUTED)")
open(p,'w',encoding='utf-8').write(s)
