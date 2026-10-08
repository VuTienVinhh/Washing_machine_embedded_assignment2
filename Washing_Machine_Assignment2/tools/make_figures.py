#!/usr/bin/env python3
"""Exact diagrams drawn from the controller specification, not generated art."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT/'report/figures'
FIG.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
INK='#183048'; BLUE='#2563a6'; LINE='#54718b'; PALE='#eef5fc'; GREY='#f4f6f8'

def canvas(w=12,h=4):
    fig,ax=plt.subplots(figsize=(w,h))
    ax.set_xlim(0,12); ax.set_ylim(0,h); ax.axis('off')
    return fig,ax

def box(ax,x,y,text,w=2.2,h=.82,fill=PALE,edge=BLUE):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.04,rounding_size=0.08',facecolor=fill,edgecolor=edge,linewidth=1.2))
    ax.text(x,y,text,ha='center',va='center',color=INK,fontsize=11,linespacing=1.55)

def arrow(ax,a,b,label=None,rad=0,lp=None,dashed=False):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=12,linewidth=1.2,color=LINE,connectionstyle=f'arc3,rad={rad}',linestyle='--' if dashed else '-'))
    if label:
        p=lp or ((a[0]+b[0])/2,(a[1]+b[1])/2+.18)
        ax.text(*p,label,ha='center',va='center',fontsize=10,color=INK,bbox={'facecolor':'white','edgecolor':'none','pad':1.2})

def save(fig,name,crop=None):
    bbox='tight'
    if crop:
        from matplotlib.transforms import Bbox
        fig.canvas.draw()
        a=fig.axes[0].transData.transform((crop[0],crop[1]))
        b=fig.axes[0].transData.transform((crop[2],crop[3]))
        bbox=Bbox.from_extents(a[0]/fig.dpi,a[1]/fig.dpi,b[0]/fig.dpi,b[1]/fig.dpi)
    for fmt in ['pdf','png','svg']:
        fig.savefig(FIG/f'{name}.{fmt}',bbox_inches=bbox,pad_inches=.1,dpi=220,facecolor='white')
    plt.close(fig)

fig,ax=canvas(h=3.8)
box(ax,1.3,2.7,'Buttons / coins\nFault signal',w=2.25)
box(ax,4.25,2.7,'Input handling\n30 ms debounce',w=2.35)
box(ax,7.3,2.7,'State controller\nCredit + STOP count',w=2.6)
box(ax,10.5,2.7,'Output logic\nRLED / BLED / wash',w=2.5)
arrow(ax,(2.47,2.7),(3.02,2.7))
arrow(ax,(5.48,2.7),(5.94,2.7))
arrow(ax,(8.65,2.7),(9.18,2.7))
box(ax,7.3,1.05,'Cycle timer\n30 min elapsed time',w=2.6,fill=GREY,edge=LINE)
box(ax,10.5,1.05,'Trace output\nState and time left',w=2.5,fill=GREY,edge=LINE)
arrow(ax,(6.97,2.22),(6.97,1.51),'start',lp=(6.45,1.9))
arrow(ax,(7.7,1.51),(7.7,2.22),'timeout',lp=(8.35,1.9))
arrow(ax,(8.65,2.55),(9.28,1.49),dashed=True)
ax.text(3,1.05,'The timer remains active\nin RUNNING and PAUSED.',ha='center',va='center',color=LINE,fontsize=11,linespacing=1.6)
save(fig,'01_module_diagram',crop=(0,.49,12,3.29))

fig,ax=canvas(h=5.4)
box(ax,1.9,3.8,'STANDBY\nCredit < 50',w=2.15)
box(ax,6,3.8,'READY\nCredit >= 50',w=2.15)
box(ax,10,3.8,'RUNNING\nWash output ON',w=2.5)
box(ax,10,1.5,'PAUSED\nWash output OFF',w=2.5)
arrow(ax,(3.02,3.8),(4.88,3.8),'coin; total >= 50',lp=(3.95,4.06))
arrow(ax,(7.12,3.8),(8.68,3.8),'RUN',lp=(7.9,4.06))
arrow(ax,(9.42,3.34),(9.42,1.96),'PAUSE',lp=(8.7,2.65))
arrow(ax,(10.55,1.96),(10.55,3.34),'RUN',lp=(11.1,2.65))
# Routed normal termination path above the states.
ax.plot([10,10,1.9],[4.27,4.91,4.91],color=LINE,linewidth=1.2)
arrow(ax,(1.9,4.91),(1.9,4.27))
ax.text(5.6,5.1,'30 min elapsed OR second STOP',ha='center',color=INK,fontsize=10)
# Paused termination uses the same rules, routed around the left states.
ax.plot([8.7,.35,.35],[1.5,1.5,3.8],color=LINE,linewidth=1.2)
arrow(ax,(.35,3.8),(.77,3.8))
ax.text(4.8,1.72,'30 min elapsed OR second STOP',ha='center',color=INK,fontsize=10)
box(ax,2.7,.42,'FAULT in any normal state',w=4.3,h=.58,fill=GREY,edge=LINE)
box(ax,7.4,.42,'ERROR',w=1.7,h=.58,fill='#fff0ee',edge='#b85d50')
arrow(ax,(4.91,.42),(6.51,.42))
ax.text(9.65,.4,'Clear fault, then reset board\nERROR -> STANDBY',ha='center',va='center',fontsize=9.5,color=LINE,linespacing=1.45)
ax.text(5.2,2.8,'Coins update credit before RUN.\nThe first STOP changes only its counter.\nPAUSE never resets the start time.',ha='center',va='center',fontsize=10,color=LINE,linespacing=1.65)
save(fig,'02_state_diagram')

fig,ax=canvas(h=4.45)
box(ax,6.1,2.25,'Arduino UNO R3\n\nSTOP       D2\nRUN        D3\nPAUSE     D4\nCOIN10   D5\nCOIN20   D6\nCOIN50   D7\nFAULT     A0',w=2.75,h=3.6)
ax.text(1.45,4.15,'Input switches',ha='center',fontsize=12,color=INK,fontweight='bold')
labels=['STOP','RUN','PAUSE','10 c','20 c','50 c','FAULT']
for i,label in enumerate(labels):
    y=3.64-i*.39
    ax.text(.25,y,label,va='center',ha='left',fontsize=9.5,color=INK)
    ax.plot([1.18,1.53],[y,y],color=LINE,linewidth=1.2)
    ax.plot([1.58,1.9],[y+.08,y+.18],color=LINE,linewidth=1.2)
    ax.plot([1.98,4.68],[y,y],color=LINE,linewidth=1.2)
    ax.plot([1.18,1.18],[y,.56],color=LINE,linewidth=.9)
ax.plot([.75,2.85],[.56,.56],color=LINE,linewidth=1.2)
ax.text(1.9,.3,'GND; pressed = LOW',ha='center',color=LINE,fontsize=9)
box(ax,10.25,3.4,'D8 -> 330 ohm -> RLED -> GND',w=3.3,h=.55,fill='#fff0ee',edge='#b85d50')
box(ax,10.25,2.45,'D9 -> 330 ohm -> BLED -> GND',w=3.3,h=.55)
box(ax,10.25,1.42,'D10 -> driver enable\nLogic signal only',w=3.3,h=.8,fill=GREY,edge=LINE)
arrow(ax,(7.52,3.4),(8.55,3.4))
arrow(ax,(7.52,2.45),(8.55,2.45))
arrow(ax,(7.52,1.42),(8.55,1.42))
ax.text(9.55,.53,'USB power and shared GND.\nInternal pullups on every input.',ha='center',va='center',fontsize=10,color=LINE,linespacing=1.5)
save(fig,'03_wiring_diagram')

fig,ax=plt.subplots(figsize=(12,3.15))
segments=[(0,8,'RUNNING',BLUE),(8,8,'PAUSED','#8ba2b8'),(16,14,'RUNNING',BLUE)]
for start,dur,label,color in segments:
    ax.broken_barh([(start,dur)],(1,1),facecolors=color)
    ax.text(start+dur/2,1.5,label,ha='center',va='center',color='white',fontsize=11,fontweight='bold')
ax.set_xlim(-.7,30.7); ax.set_ylim(.1,3.7)
for t,event,left in [(0,'RUN','30 min left'),(8,'PAUSE','22 min left'),(16,'RUN','14 min left'),(30,'TIMEOUT','0 min left')]:
    ax.plot([t,t],[.83,2.2],color=LINE,linestyle=':',linewidth=1)
    ax.text(t,2.4,event,ha='center',fontsize=10,color=INK)
    ax.text(t,2.86,left,ha='center',fontsize=10,color=LINE)
ax.set_xticks([0,8,16,30]); ax.set_xlabel('Elapsed time since first RUN (minutes)',labelpad=10,color=INK)
ax.set_yticks([])
for name in ['top','right','left']: ax.spines[name].set_visible(False)
ax.spines['bottom'].set_position(('data',.68)); ax.spines['bottom'].set_color(LINE)
ax.tick_params(axis='x',colors=INK)
save(fig,'04_pause_timeline')
print('Created 4 exact diagrams, each in PDF, PNG and editable SVG.')
