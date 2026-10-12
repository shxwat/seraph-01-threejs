"""SERAPH-01: actual modeled parts, linked detail meshes, no external assets.

Coordinates: Z up, -Y is the front. Rings are constructed in local XY and
their parent pivots orient them in world XZ. All dimensions are in meters.
"""
import math
import random
import bpy
from mathutils import Vector
from rigging import empty, mesh_object, linked, collection, link

TAU = math.tau
RNG = random.Random(7301)
CACHE = {}


def cached(name, builder, location=(0, 0, 0), scale=(1, 1, 1), parent=None, rotation=(0, 0, 0)):
    if name not in CACHE:
        template = builder(); template.hide_render = True; template.hide_viewport = True
        CACHE[name] = template
    return linked(CACHE[name], name + ' · instance', location, rotation, scale, parent)


def prism(name, size, mat, parent=None, location=(0, 0, 0), bevel=.02):
    x, y, z = (v / 2 for v in size)
    v = [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    f = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    o = mesh_object(name, v, f, mat, parent, bevel); o.location = location
    return o


def cylinder(name, radius, depth, mat, location=(0,0,0), parent=None, segments=24):
    v = [(radius*math.cos(i*TAU/segments), radius*math.sin(i*TAU/segments), z)
         for z in (-depth/2, depth/2) for i in range(segments)]
    f = [tuple(range(segments-1,-1,-1)),tuple(range(segments,2*segments))]
    f += [(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
    o = mesh_object(name, v, f, mat, parent, .008); o.location = location
    return o


def rod(name, a, b, radius, mat, parent=None):
    d = Vector(b)-Vector(a)
    o = cylinder(name, radius, d.length, mat, (Vector(a)+Vector(b))/2, parent, 12)
    o.rotation_euler = d.to_track_quat('Z','Y').to_euler()
    return o


def create_cable(name, points, radius, mat, parent=None, smooth=True):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions='3D'; cu.resolution_u=8
    cu.bevel_depth=radius; cu.bevel_resolution=2
    if smooth:
        s=cu.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
        for p, co in zip(s.bezier_points, points):
            p.co=co; p.handle_left_type=p.handle_right_type='AUTO'
    else:
        s=cu.splines.new('POLY');s.points.add(len(points)-1)
        for p,co in zip(s.points,points):p.co=(*co,1)
    o=link(bpy.data.objects.new(name,cu)); o.parent=parent; cu.materials.append(mat)
    return o


def create_ring(name, radius, width, depth, mat, parent=None, segments=128):
    # Stepped eight-sided annular cross-section catches light without a torus.
    profile=[(-width/2,-depth*.32),(-width*.32,-depth/2),(width*.32,-depth/2),
             (width/2,-depth*.32),(width/2,depth*.32),(width*.32,depth/2),
             (-width*.32,depth/2),(-width/2,depth*.32)]
    v=[((radius+dr)*math.cos(i*TAU/segments),(radius+dr)*math.sin(i*TAU/segments),dz)
       for i in range(segments) for dr,dz in profile]
    f=[(i*8+j,((i+1)%segments)*8+j,((i+1)%segments)*8+(j+1)%8,i*8+(j+1)%8)
       for i in range(segments) for j in range(8)]
    return mesh_object(name,v,f,mat,parent)


def create_gear(name, radius, teeth, width, depth, mat, parent=None):
    n=teeth*4; v=[]
    for z in (-depth/2,depth/2):
        for side in (0,1):
            for i in range(n):
                r=radius-width if side==0 else radius+(width*.42 if i%4 in (1,2) else 0)
                a=TAU*i/n; v.append((r*math.cos(a),r*math.sin(a),z))
    f=[]
    for i in range(n):
        j=(i+1)%n
        f.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                  (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return mesh_object(name,v,f,mat,parent)


def create_radial_array(source, count, radius, parent=None, phase=0, z=0, scale=(1,1,1)):
    return [linked(source, source.name+' · radial %03d'%i,
                   (radius*math.cos(a:=phase+TAU*i/count),radius*math.sin(a),z),
                   (0,0,a),scale,parent) for i in range(count)]


def create_armor_plate(name, outline, depth, mat, parent=None, location=(0,0,0), ridge=.1):
    """Convex forged shield: concentric surface bands form actual curved armor."""
    n=len(outline); cx=sum(p[0] for p in outline)/n; cz=sum(p[1] for p in outline)/n
    bands=(1,.82,.58,.32,.10)
    v=[(cx+(x-cx)*r,-ridge*(1-r*r),cz+(z-cz)*r) for r in bands for x,z in outline]
    v += [(cx,-ridge,cz)]+[(x,depth,z) for x,z in outline]
    f=[]
    for k in range(len(bands)-1):
        f += [(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n)]
    f += [((len(bands)-1)*n+i,(len(bands)-1)*n+(i+1)%n,len(bands)*n) for i in range(n)]
    front_count=len(f);back=len(bands)*n+1
    f += [tuple(range(back,back+n))]+[(i,back+i,back+(i+1)%n,(i+1)%n) for i in range(n)]
    o=mesh_object(name,v,f,mat,parent,.018); o.location=location
    for poly in list(o.data.polygons)[:front_count]:poly.use_smooth=True
    return o


def edged_plate(name, outline, depth, mat, trim, parent=None, location=(0,0,0), ridge=.1):
    root=empty(name,location,parent)
    create_armor_plate(name+' · shield',outline,depth,mat,root,ridge=ridge)
    create_cable(name+' · polished perimeter',[(x,-.012,z) for x,z in outline+[outline[0]]],.012,trim,root,smooth=False)
    cx=sum(p[0] for p in outline)/len(outline);cz=sum(p[1] for p in outline)/len(outline)
    # Linked octagonal fasteners sit on the curved metal rather than floating.
    for x,z in outline[::2]:
        cached('Fastener · '+trim.name,lambda:cylinder('Fastener master',1,.60,trim,segments=8),
               (cx+(x-cx)*.78,-ridge*(1-.78**2)-.018,cz+(z-cz)*.78),
               (.024,.024,.024),root,(math.pi/2,0,0))
    return root


def create_piston(name, a, b, mats, parent=None):
    a,b=Vector(a),Vector(b); d=b-a
    root=empty(name,parent=parent)
    rod(name+' · hydraulic housing',a,a+d*.63,.09,mats['black'],root)
    rod(name+' · chromed ram',a+d*.53,b,.046,mats['silver'],root)
    for p in (a,a+d*.60,b):
        j=cylinder(name+' · end collar',.125,.085,mats['gold'],p,root,16)
        j.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return root


def create_ornament(name, mats, parent=None, location=(0,0,0)):
    root=empty(name,location,parent)
    create_armor_plate(name+' · diamond',[(0,.22),(.1,0),(0,-.22),(-.1,0)],.08,mats['gold'],root,ridge=.06)
    r=create_ring(name+' · bearing',.105,.025,.04,mats['silver'],root,32)
    r.rotation_euler[0]=math.pi/2
    return root


def create_celestial_head(mats, parent):
    root=empty('HEAD · featureless celestial mask',(0,0,4.0),parent)
    # Broad brow, impossibly elongated chin, separate central keel and side cheeks.
    outline=[(0,1.04),(.46,.88),(.56,.43),(.34,-.28),(0,-.84),(-.34,-.28),(-.56,.43),(-.46,.88)]
    edged_plate('Mask · electrum shell',outline,.38,mats['pale'],mats['silver'],root,(0,-.34,0),.38)
    for s in (-1,1):
        edged_plate('Mask · cheek '+str(s),[(s*.08,.63),(s*.44,.62),(s*.31,-.15),(s*.02,-.7)],
                    .08,mats['gold'],mats['pale'],root,(0,-.59,0),.07)
        create_cable('Eye slit · divine gaze',[(s*.105,-.77,.44),(s*.25,-.74,.48),(s*.37,-.66,.5)],.018,mats['blue'],root)
        create_cable('Temple conduit',[(s*.51,-.1,.68),(s*.65,.12,.25),(s*.43,.16,-.5)],.045,mats['silver'],root)
        create_piston('Temple actuator',(s*.55,0,.55),(s*.46,.05,-.4),mats,root)
    edged_plate('Mask · central spear',[(0,.83),(.085,.43),(0,-.8),(-.085,.43)],.06,mats['silver'],mats['pale'],root,(0,-.78,0),.04)
    # Crown halo is geometric: gear, edge channels, spokes, etched radial strokes.
    halo=empty('CROWN · sacred aureole',(0,.53,.45),root); halo.rotation_euler[0]=math.pi/2
    create_gear('Crown · 72 electrum teeth',1.10,72,.12,.13,mats['gold'],halo)
    create_ring('Crown · inner luminous channel',.92,.027,.026,mats['hot'],halo,96)
    create_ring('Crown · outer polished flange',1.19,.022,.07,mats['pale'],halo,96)
    stroke=prism('Crown · engraving template',(.11,.018,.015),mats['silver'],bevel=0)
    stroke.hide_render=True;stroke.hide_viewport=True
    create_radial_array(stroke,72,1.065,halo,z=-.085)
    return root


def create_energy_core(mats, parent):
    root=empty('REACTOR · miniature artificial star',(0,-.43,1.7),parent)
    # A sphere is appropriate inside a visibly engineered, layered reactor.
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=.57)
    star=bpy.context.object; star.name='Star · faceted plasma surface'; star.parent=root
    star.data.materials.append(mats['energy'])
    shell=[]
    for i,r in enumerate((.69,.81,.96)):
        p=empty('Reactor containment gimbal %d'%i,parent=root)
        p.rotation_euler=(math.pi/2 + i*.45,i*.6,0)
        create_gear('Reactor · segmented shell %d'%i,r,48,.075,.09,mats['silver'] if i==1 else mats['gold'],p)
        create_ring('Reactor · luminous seam %d'%i,r-.09,.018,.025,mats['hot'],p,64)
        shell.append(p)
    for i in range(9):
        pts=[]
        for j in range(25):
            a=j*TAU/24; r=.59+.045*math.sin(a*5+i)
            pts.append((r*math.cos(a),r*math.sin(a)*math.cos(i*.7),r*math.sin(a)*math.sin(i*.7)))
        create_cable('Star · magnetic filament %02d'%i,pts,.008,mats['hot'],root)
    return root,shell


def create_mechanical_wing(side, mats, parent, count=22):
    root=empty(('LEFT' if side<0 else 'RIGHT')+' WING · shoulder gimbal',(side*1.42,.30,2.78),parent)
    blades=[]
    for i in range(count):
        u=i/(count-1)
        tip=Vector((side*(4.4+2.0*math.sin(u*math.pi*.9)),0,3.5-u*10.0))
        anchor=Vector((side*(.12+i*.047),.10+u*.32,-u*.38))
        length=(tip-anchor).length; angle=math.atan2((tip-anchor).x,(tip-anchor).z)
        p=empty(('L' if side<0 else 'R')+' · articulated feather %02d'%i,anchor,root); p.rotation_euler[1]=angle
        width=.27+math.sin(u*math.pi)*.19
        shape=[(-width*.28,0),(-width*.65,length*.20),(-width*.48,length*.64),
               (0,length),(width*.68,length*.68),(width*.8,length*.27),(width*.3,0)]
        edged_plate('Feather %02d · folded alloy vane'%i,shape,.07,
                    mats['black'] if i%4==2 else mats['pale'] if i%3 else mats['silver'],mats['gold'],p,ridge=.1)
        create_cable('Feather · structural keel',[(0,-.12,.12),(.025,-.13,length*.48),(0,-.03,length*.95)],.021,mats['silver'],p)
        for q in (-1,1):
            create_cable('Feather · inlaid longitudinal groove',[(q*width*.32,-.044,length*.17),
                         (q*width*.27,-.08,length*.48),(q*width*.11,-.015,length*.84)],.009,mats['groove'],p)
        # A compact toothed bearing at every feather root.
        bearing=create_gear('Feather · articulation bearing',.13,12,.055,.08,mats['gold'],p)
        bearing.rotation_euler[0]=math.pi/2
        blades.append((p,tuple(anchor),angle,length,side,i))
    for j in range(6):
        a=(side*j*.27,-.1,-j*.18); b=(side*(.9+j*.27),.0,1.05-j*.37)
        create_piston('Wing · tendon actuator',a,b,mats,root)
    # Short layered scapular shields supply the thick, intricate shoulder silhouette.
    for j in range(9):
        p=edged_plate('Scapula · overlapping shield %d'%j,[(-.15,0),(-.21,.35),(0,.87),(.25,.34),(.12,0)],
                      .10,mats['gold'],mats['silver'],root,(side*(.12+j*.18),-.24,-j*.085),.11)
        p.rotation_euler[1]=side*(.3+j*.12)
    return root,blades


def build_body(mats, parent):
    pieces=[]
    spine=empty('SPINE · articulated vertebral column',parent=parent)
    for j in range(19):
        z=-1.1+j*.255
        p=empty('Vertebra · locking segment %02d'%j,(0,.16,z),spine)
        ring=create_gear('Vertebra · gear joint',.22,16,.085,.15,mats['silver'],p)
        edged_plate('Vertebra · dorsal plate',[(-.24,.1),(.24,.1),(.17,-.15),(-.17,-.15)],.12,mats['black'],mats['gold'],p)
        pieces.append(p)
    for s in (-1,1):
        # Suspended ribcage with exposed silver braces behind the armor.
        for j in range(7):
            z=2.55-j*.37; w=1.04-j*.07
            create_cable('Rib · titanium arc',[(s*.12,.12,z+.12),(s*w,.18,z),(s*w*.85,-.27,z-.22),(s*.32,-.43,z-.3)],.065,mats['silver'],spine)
        for j in range(4):
            z=2.7-j*.58; w=.78-j*.09
            outline=[(0,.3),(s*w,.12),(s*(w+.15),-.30),(s*.16,-.52)]
            p=edged_plate('Thorax · lamellar cuirass',outline,.16,mats['gold'] if j%2==0 else mats['black'],mats['pale'],parent,(s*.22,-.39,z),.15)
            pieces.append(p)
        shoulder=empty('SHOULDER · ball and socket '+str(s),(s*1.31,0,2.68),parent)
        joint=create_gear('Shoulder · toothed axial bearing',.42,32,.14,.3,mats['silver'],shoulder); joint.rotation_euler[0]=math.pi/2
        create_ring('Shoulder · warm inlay',.29,.024,.05,mats['dim'],joint)
        pieces.append(shoulder)
        # Segmented arms are parented as a proper shoulder/elbow/wrist chain.
        upper=empty('ARM · upper linkage '+str(s),(s*1.5,0,2.3),parent)
        create_piston('Arm · primary ram',(0,0,0),(s*.28,-.03,-1.45),mats,upper)
        p=edged_plate('Arm · upper gold armor',[(-.26,0),(.24,.05),(.3,-.75),(.11,-1.34),(-.2,-1.04)],.22,mats['pale'],mats['silver'],upper,(0,-.23,0),.1)
        elbow=empty('ARM · elbow joint '+str(s),(s*.29,0,-1.46),upper)
        gear=create_gear('Elbow · exposed gear',.26,24,.1,.22,mats['gold'],elbow); gear.rotation_euler[0]=math.pi/2
        fore=empty('ARM · forearm '+str(s),(s*.05,-.02,-.12),elbow)
        create_piston('Arm · wrist ram',(0,0,0),(s*.2,-.12,-1.20),mats,fore)
        for j in range(3):
            edged_plate('Gauntlet · overlapping armor',[(-.26,.15),(.28,.1),(.23,-.33),(0,-.54),(-.25,-.3)],.13,
                        mats['black'] if j==1 else mats['pale'],mats['gold'],fore,(s*j*.06,-.22,-j*.34),.1)
        hand=empty('HAND · articulated manipulator',(s*.21,-.08,-1.28),fore)
        edged_plate('Hand · knuckle shield',[(-.2,.1),(.2,.1),(.18,-.3),(-.15,-.33)],.18,mats['silver'],mats['gold'],hand)
        for f in range(4):
            x=-.15+f*.10
            for j in range(3):
                rod('Finger · phalanx',(x,-.03-j*.045,-.27-j*.13),(x,-.06-j*.045,-.38-j*.13),.038,mats['gold'],hand)
        create_cable('Arm · exposed braided conduit',[(s*.25,.17,-.1),(s*.5,.23,-.85),(s*.35,.18,-1.6),(s*.48,.08,-2.7)],.038,mats['black'],upper)
        pieces.append(upper)
        hip=empty('LEG · hip linkage '+str(s),(s*.47,.07,-.95),parent)
        create_piston('Leg · femoral actuator',(0,0,0),(s*.15,0,-1.9),mats,hip)
        for j in range(3):
            edged_plate('Thigh · nested cuirass',[(-.34,.20),(.32,.17),(.23,-.85),(0,-1.13),(-.25,-.83)],.20,
                        mats['black'],mats['pale'],hip,(s*j*.025,-.26,-j*.38),.16)
        knee=empty('LEG · knee gimbal',(s*.12,-.02,-1.98),hip)
        g=create_gear('Knee · exposed bearing',.28,28,.1,.24,mats['silver'],knee);g.rotation_euler[0]=math.pi/2
        edged_plate('Knee · diamond guard',[(0,.30),(.3,0),(0,-.4),(-.3,0)],.12,mats['gold'],mats['pale'],knee,(0,-.30,0),.08)
        shin=empty('LEG · tibial linkage',(0,.02,-.25),knee)
        create_piston('Shin · primary actuator',(0,0,0),(s*.03,-.04,-1.64),mats,shin)
        edged_plate('Shin · elongated black shield',[(-.24,.2),(.24,.2),(.2,-1.14),(0,-1.64),(-.18,-1.1)],.22,mats['black'],mats['silver'],shin,(0,-.22,0),.16)
        for q in (-1,1):
            create_cable('Shin · gold nerve',[(q*.19,-.27,.08),(q*.14,-.35,-.8),(0,-.29,-1.49)],.022,mats['pale'],shin)
        foot=empty('FOOT · suspended sabaton',(0,-.16,-1.72),shin)
        for j in range(4):
            edged_plate('Foot · articulated toe plate',[(-.21,.12),(.21,.12),(.24,-.12),(-.24,-.12)],.23,mats['silver'],mats['gold'],foot,(0,-j*.13,-j*.025),.035)
        pieces.append(hip)
        # Long ceremonial vanes trail below the waist.
        for j in range(5):
            p=empty('REGALIA · floating tail vane',(s*(.65+j*.28),.62+j*.1,-.65),parent)
            p.rotation_euler[1]=s*(-.10-j*.075)
            L=4.4+j*.17
            edged_plate('Regalia · sweeping metal ribbon',[(-.1,.1),(.18,0),(.23,-L*.8),(.05,-L),(-.13,-L*.94),(-.22,-L*.45)],.045,
                        mats['pale'] if j%2 else mats['black'],mats['gold'],p,ridge=.035)
            pieces.append(p)
    pelvis=edged_plate('PELVIS · central keystone',[(-.64,.25),(.64,.25),(.47,-.35),(0,-.72),(-.47,-.35)],.27,
                       mats['black'],mats['gold'],parent,(0,-.24,-.55),.20)
    g=create_gear('Abdomen · exposed ornamental bearing',.35,36,.12,.11,mats['gold'],parent);g.location=(0,-.63,-.15);g.rotation_euler[0]=math.pi/2
    pieces.append(pelvis)
    # Solid abdominal lamellae and a collar bridge the skeletal ribs into armor.
    for j in range(3):
        p=edged_plate('ABDOMEN · interlocking central shield',[(-.43,.22),(.43,.22),(.37,-.13),(0,-.31),(-.37,-.13)],
                      .18,mats['pale'] if j!=1 else mats['black'],mats['gold'],parent,(0,-.47,.59-j*.31),.17)
        pieces.append(p)
    p=edged_plate('COLLAR · divided electrum gorget',[(-.85,.08),(-.39,.31),(0,.16),(.39,.31),(.85,.08),(.42,-.16),(-.42,-.16)],
                  .14,mats['pale'],mats['silver'],parent,(0,-.18,3.00),.15)
    pieces.append(p)
    return pieces


def build_orbits(mats,parent,detail=1):
    pivots=[]; ornaments=[]
    # One linked tick mesh and bolt mesh serve all five orbital assemblies.
    tick=prism('Orbital engraving master',(.11,.018,.018),mats['pale'],bevel=0);tick.hide_render=True;tick.hide_viewport=True
    bolt=cylinder('Orbital bolt master',.032,.065,mats['silver'],segments=8);bolt.hide_render=True;bolt.hide_viewport=True
    for i in range(5):
        r=5.15+i*.31
        p=empty('ORBIT %d · precision celestial gimbal'%(i+1),(0,1.65+i*.16,.70),parent)
        create_gear('Orbit %d · %d modeled teeth'%(i+1,96+i*8),r,96+i*8,.10,.10,mats['gold'] if i%2==0 else mats['silver'],p)
        create_ring('Orbit · inner rail',r-.16,.025,.055,mats['black'],p)
        create_ring('Orbit · luminous channel',r-.10,.012,.025,mats['dim'],p)
        create_ring('Orbit · outer silver lip',r+.06,.017,.04,mats['pale'],p)
        create_radial_array(tick,96,r-.045,p,z=-.08,phase=i*.07)
        create_radial_array(bolt,32,r-.04,p,z=-.10,phase=i*.07)
        for j in range(16):
            a=j*TAU/16+i*.1
            support=prism('Orbit · radial connector',(.27,.075,.06),mats['black'],p,(r*math.cos(a),r*math.sin(a),0),.01)
            support.rotation_euler[2]=a
            # Tiny physical runes, not a texture pretending to be geometry.
            for k in range(3):
                a2=a+(k-1)*.016
                o=linked(tick,'Orbit · engraved triplet',( (r-.2)*math.cos(a2),(r-.2)*math.sin(a2),-.07),
                         (0,0,a2+.65),(.43,1,1),p)
        for j in range(4):
            a=j*TAU/4+i*.13
            orbit=empty('Orbit · traveling reliquary carrier',parent=p); orbit.rotation_euler[2]=a
            create_ornament('Orbit · electrum reliquary',mats,orbit,(r,0,-.13))
            ornaments.append((orbit,i,j))
        pivots.append(p)
    return pivots,ornaments


def create_eye_transformation(mats,parent):
    root=empty('FINAL FORM · celestial mechanical eye',(0,-.02,1.7),parent)
    iris=empty('IRIS · radial optical mechanism',parent=root)
    disk=empty('Iris · front-facing rings',parent=iris);disk.rotation_euler[0]=math.pi/2
    for i,r in enumerate((.82,1.12,1.45,1.77,2.03)):
        create_gear('Iris · aperture bearing %d'%i,r,64,.10,.09,mats['silver'] if i%2 else mats['gold'],disk)
        create_ring('Iris · plasma channel %d'%i,r-.12,.018,.035,mats['blue'] if i==2 else mats['hot'],disk)
    # Radial iris lamellae have ridges and a serrated silhouette.
    template=create_armor_plate('Iris lamella master',[(-.035,.81),(.045,.84),(.10,1.67),(0,1.95),(-.04,1.55)],.05,mats['pale'],ridge=.07)
    template.hide_render=True;template.hide_viewport=True
    for j in range(96):
        a=j*TAU/96
        o=linked(template,'Iris · engraved optical lamella %03d'%j,(0,-.29,0),(0,a,0),parent=iris)
    pupil=empty('PUPIL · obsidian optical aperture',(0,-1.22,0),iris)
    d=cylinder('Pupil · recessed black optical disc',.43,.12,mats['pupil'],parent=pupil,segments=96);d.rotation_euler[0]=math.pi/2
    rim=create_ring('Pupil · incandescent edge',.465,.027,.045,mats['hot'],pupil,96);rim.rotation_euler[0]=math.pi/2
    lids=[]
    for side in (-1,1):
        lid=empty(('LOWER' if side<0 else 'UPPER')+' EYELID · segmented orbital arch',parent=root)
        for j in range(28):
            t0=j/28;t1=(j+1)/28
            x0=-5.4+10.8*t0;x1=-5.4+10.8*t1
            z0=side*2.75*math.sin(math.pi*t0)**.88;z1=side*2.75*math.sin(math.pi*t1)**.88
            shape=[(x0,z0),(x1,z1),(x1,z1+side*.23),(x0,z0+side*.23)]
            edged_plate('Eye · interlocking lid segment %02d'%j,shape,.20,mats['gold'] if j%3 else mats['black'],mats['silver'],lid,(0,-.55,0),.07)
        pts=[(-5.4+10.8*j/48,-.80,side*2.68*math.sin(math.pi*j/48)**.88) for j in range(49)]
        create_cable('Eye · amber optic nerve',pts,.028,mats['hot'],lid)
        lids.append(lid)
    return root,iris,lids


def fragments(mats,parent,count=180):
    t=create_armor_plate('Assembly fragment master',[(-.07,-.12),(.06,-.08),(.09,.12),(0,.18),(-.08,.1)],.06,mats['gold'],ridge=.035)
    t.hide_render=True;t.hide_viewport=True
    out=[]
    for i in range(count):
        a=RNG.uniform(0,TAU); r=RNG.uniform(7.5,13); z=RNG.uniform(-6.5,7)
        o=linked(t,'Assembly · incoming sliver %03d'%i,(r*math.cos(a),RNG.uniform(-2,5),z),
                 (RNG.random()*3,RNG.random()*3,RNG.random()*3),parent=parent)
        out.append(o)
    return out


def sparks(mats,parent,count=120):
    # Emissive diamond flecks, instantiated from one four-face mesh.
    t=mesh_object('Spark master',[(0,0,.035),(.014,0,0),(0,.014,0),(-.014,0,0),(0,-.014,0),(0,0,-.035)],
                  [(0,1,2),(0,2,3),(0,3,4),(0,4,1),(5,2,1),(5,3,2),(5,4,3),(5,1,4)],mats['hot'])
    t.hide_render=True;t.hide_viewport=True
    out=[]
    for i in range(count):
        a=RNG.random()*TAU;r=RNG.uniform(2,8)
        out.append(linked(t,'Particle · suspended ion %03d'%i,(r*math.cos(a),RNG.uniform(-.1,4),1.7+r*.7*math.sin(a)),
                          scale=(RNG.uniform(.4,1.4),)*3,parent=parent))
    return out


def build_scene_geometry(mats,preset):
    CACHE.clear();RNG.seed(7301)
    collection('01 · SERAPH | hierarchical deity')
    master=empty('SERAPH-01 · master control')
    body=empty('BODY · folding skeletal control',parent=master)
    pieces=build_body(mats,body)
    head=create_celestial_head(mats,body);pieces.append(head)
    core,gimbals=create_energy_core(mats,master)
    collection('02 · WINGS | articulated individual vanes')
    wings=[];blades=[]
    for side in (-1,1):
        w,b=create_mechanical_wing(side,mats,master,22);wings.append(w);blades.extend(b)
    collection('03 · ORBITS | linked mechanical detail')
    orbits,ornaments=build_orbits(mats,master)
    collection('04 · EYE | folding iris and segmented eyelids')
    eye,iris,lids=create_eye_transformation(mats,master)
    collection('05 · PARTICLES | assembly fragments and ions')
    debris=fragments(mats,master,120 if preset=='LOW' else 180)
    ions=sparks(mats,master,80 if preset=='LOW' else 140)
    return dict(master=master,body=body,pieces=pieces,head=head,core=core,gimbals=gimbals,
                wings=wings,blades=blades,orbits=orbits,ornaments=ornaments,eye=eye,iris=iris,lids=lids,debris=debris,ions=ions)
