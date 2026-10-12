"""Five authored acts at 24 fps; animation lives in editable Blender actions."""
import math
import random
from mathutils import Vector
from rigging import key, animate_assembly, polish_curves


def animate(rig, mats, lights, camera, target):
    rng=random.Random(7301)
    for i,p in enumerate(rig['pieces']):
        home=p.location.copy()
        start=72+(i%19)*3
        end=134+(i%17)*3
        if p==rig['head']: start,end=146,190
        animate_assembly(p,home,start,end,(rng.choice((-1,1))*rng.uniform(2,5),rng.uniform(1.5,4),rng.uniform(-2,3)))
    # The body folds behind the final iris; every original part remains in the file.
    b=rig['body']
    key(b,'scale',1,(1,1,1));key(b,'scale',288,(1,1,1));key(b,'scale',384,(.24,.45,.20))
    key(b,'location',288,(0,0,0));key(b,'location',384,(0,1.3,1.35))
    key(b,'rotation_euler',288,(0,0,0));key(b,'rotation_euler',384,(math.radians(75),0,0))
    # Shoulder gimbals unfold, pause mechanically, retract, then release vanes.
    for w,s in zip(rig['wings'],(-1,1)):
        key(w,'scale',1,(.001,)*3);key(w,'scale',162,(.001,)*3);key(w,'scale',196,(1,1,1))
        key(w,'rotation_euler',1,(0,s*1.1,0));key(w,'rotation_euler',192,(0,s*1.1,0))
        key(w,'rotation_euler',250,(0,-s*.035,0));key(w,'rotation_euler',280,(0,0,0))
        key(w,'rotation_euler',308,(0,s*.35,0));key(w,'rotation_euler',380,(0,0,0))
    for p,home,angle,length,s,i in rig['blades']:
        key(p,'location',280,home);key(p,'rotation_euler',280,(0,angle,0));key(p,'scale',280,(1,1,1))
        # Ordered proximal-to-distal separation; radial destination is in world XZ.
        release=300+i*.9
        key(p,'location',release,Vector(home)+Vector((s*.15,0,-.2)))
        a=math.tau*(i+(0 if s<0 else .5))/22
        radius=1.72+(i%3)*.13
        destination=Vector((radius*math.sin(a),.55+(i%3)*.07,1.7+radius*math.cos(a)))
        destination-=p.parent.location
        key(p,'location',380+i*.35,destination)
        key(p,'rotation_euler',380+i*.35,(0,a,0))
        key(p,'scale',380+i*.35,(.65,1,.42))
    # Orbital alignment uses different tilt axes and gear ratios, not free spinning.
    for i,p in enumerate(rig['orbits']):
        key(p,'scale',1,(.001,)*3);key(p,'scale',166+i*4,(.001,)*3);key(p,'scale',235+i*6,(1,1,1))
        pre=(math.pi/2+(i-2)*.36,(i-2)*.20,i*.31)
        hero=(math.pi/2+(i-2)*.10,(i-2)*.085,i*.21)
        eye=(math.pi/2+(i-2)*.21,(i-2)*.13,i*.31+.4)
        key(p,'rotation_euler',1,pre);key(p,'rotation_euler',192,pre)
        key(p,'rotation_euler',270,hero);key(p,'rotation_euler',290,hero)
        key(p,'rotation_euler',390,eye)
        key(p,'rotation_euler',460,(eye[0]+.045,eye[1]+.035,eye[2]+(i+1)*.045))
        # Last second closes down to match the dark opening for a light-based loop.
        key(p,'scale',458,(1,1,1));key(p,'scale',480,(.001,)*3)
    for o,i,j in rig['ornaments']:
        initial=o.rotation_euler.copy()
        key(o,'rotation_euler',1,initial)
        key(o,'rotation_euler',480,(0,0,initial.z+(i+1)*.65))
    core=rig['core']
    key(core,'scale',1,(.001,)*3);key(core,'scale',26,(.06,)*3);key(core,'scale',96,(.65,)*3)
    key(core,'scale',186,(1,1,1));key(core,'scale',288,(1,1,1));key(core,'scale',390,(1.25,)*3)
    key(core,'scale',456,(1.25,)*3);key(core,'scale',480,(.001,)*3)
    for i,p in enumerate(rig['gimbals']):
        base=p.rotation_euler.copy()
        for f,t in ((1,0),(96,.15),(192,.7),(288,1.3),(384,2.2),(480,2.7)):
            key(p,'rotation_euler',f,(base.x+t*(.45+i*.1),base.y+t*(.28+i*.08),t*.35))
    for i,filament in enumerate(c for c in core.children if 'magnetic filament' in c.name):
        key(filament,'rotation_euler',1,(0,0,0))
        key(filament,'rotation_euler',240,(.12*(i+1),.08*i,.4))
        key(filament,'rotation_euler',480,(.22*(i+1),.16*i,.8))
    for i,p in enumerate(p for p in rig['pieces'] if 'REGALIA' in p.name):
        rest=p.rotation_euler.copy()
        for frame,d in ((180,0),(228,.025),(276,-.02),(312,.015),(384,0)):
            key(p,'rotation_euler',frame,(rest.x,rest.y+d*math.sin(i+1),rest.z))
    eye=rig['eye']
    key(eye,'scale',1,(.001,)*3);key(eye,'scale',318,(.001,)*3);key(eye,'scale',386,(1,1,1))
    key(eye,'scale',458,(1,1,1));key(eye,'scale',480,(.001,)*3)
    for lid in rig['lids']:
        key(lid,'scale',318,(1,1,.025));key(lid,'scale',386,(1,1,.025));key(lid,'scale',423,(1,1,1))
    iris=rig['iris']
    key(iris,'rotation_euler',360,(0,0,0));key(iris,'rotation_euler',456,(0,.20,0))
    for o in rig['debris']:
        home=o.location.copy();finish=rng.randint(92,174)
        key(o,'location',1,home);key(o,'scale',1,(.001,)*3)
        key(o,'scale',rng.randint(24,60),(1,1,1));key(o,'location',finish-28,home*.5)
        key(o,'location',finish,(rng.uniform(-.2,.2),.2,rng.uniform(.2,2.5)))
        key(o,'scale',finish,(.001,)*3)
    for i,o in enumerate(rig['ions']):
        home=o.location.copy();sc=o.scale.copy()
        key(o,'scale',1,(.001,)*3);key(o,'scale',120,sc)
        key(o,'location',1,home);key(o,'location',460,home+Vector((.07*math.sin(i),.1,.45)))
        key(o,'scale',460,sc);key(o,'scale',480,(.001,)*3)
    # Keyed pulse strengths remain editable on the material node socket.
    for name,factor in (('energy',1),('hot',.6),('blue',.32),('dim',.15)):
        socket=mats[name].node_tree.nodes['Animated radiance'].inputs['Strength']
        for frame,value in ((1,0),(16,.05),(40,2),(96,5),(192,10),(260,15),(288,12),
                            (340,8),(388,13),(410,22),(425,12),(440,18),(456,12),(480,0)):
            socket.default_value=value*factor;socket.keyframe_insert('default_value',frame=frame)
    # A second emissive rail lets the light pulse propagate across the orbits.
    for i,p in enumerate(rig['orbits']):
        pulse=next((c for c in p.children if 'luminous channel' in c.name),None)
        if pulse:
            m=mats['dim'].copy();m.name='Orbital pulse · traveling wave %d'%(i+1)
            # Material copies share their original action unless explicitly detached.
            # Each rail needs independent keys for a traveling, rather than global, pulse.
            m.node_tree.animation_data_clear()
            pulse.data.materials.clear();pulse.data.materials.append(m)
            socket=m.node_tree.nodes['Animated radiance'].inputs['Strength']
            for f,v in ((1,0),(192,.5),(280,1.5),(396+i*4,1.5),(404+i*4,12),(416+i*4,1.5),(458,1.5),(480,0)):
                socket.default_value=v;socket.keyframe_insert('default_value',frame=f)
    for light,base in lights:
        for f,power in ((1,0),(48,.04),(96,.16),(160,.65),(205,1),(288,1),(384,.75),(420,1),(458,.85),(480,0)):
            light.data.energy=base*power;light.data.keyframe_insert('energy',frame=f)
    # Tracked camera: wide awakening, a close assembly pass, full hero, three-quarter
    # orbit at revelation, iris approach, then final pullback. No camera cuts.
    shots=[(1,(0,-41,4.0),50,(0,0,1.4)),
           (60,(.5,-37,3.6),50,(0,0,1.6)),
           (112,(-3.0,-28,3.3),70,(0,0,1.5)),
           (176,(-1.8,-30,3.1),50,(0,0,1.0)),
           (224,(0,-37,4.5),50,(0,0,.8)),
           (264,(7.8,-35,5.2),50,(0,0,1.0)),
           (288,(9.0,-34,4.2),50,(0,0,1.0)),
           (336,(4,-30,3.5),50,(0,0,1.7)),
           (384,(0,-28,2.7),50,(0,0,1.7)),
           (428,(0,-32,3.5),50,(0,0,1.4)),
           (458,(0,-39,4),50,(0,0,1.1)),
           (480,(0,-41,4),50,(0,0,1.4))]
    for f,loc,lens,look in shots:
        key(camera,'location',f,loc);key(target,'location',f,look)
        camera.data.lens=lens;camera.data.keyframe_insert('lens',frame=f)
    # Standalone 85 mm detail camera is available without disrupting the main take.
    polish_curves()
