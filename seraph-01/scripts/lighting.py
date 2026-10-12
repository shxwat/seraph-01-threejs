"""Sculptural studio rig in a black void, with real light driven by the reactor."""
import math
import bpy
from mathutils import Vector
from rigging import collection, empty, link


def aim(obj,point):
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()


def area(name,location,color,power,size,target=(0,0,1)):
    data=bpy.data.lights.new(name,'AREA');data.color=color;data.energy=power
    data.shape='DISK';data.size=size
    o=link(bpy.data.objects.new(name,data));o.location=location;aim(o,target)
    return o,power


def build_lighting():
    collection('06 · CINEMATOGRAPHY | lights and camera controls')
    world=bpy.data.worlds.new('Infinite black void');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.008,.012,.02,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.12
    bpy.context.scene.world=world
    lights=[area('KEY · immense warm reflection card',(-5,-8,9),(1,.78,.48),1700,7),
            area('FILL · frontal soft silver',(4,-10,3),(.68,.8,1),1400,6),
            area('FRONT · broad gold armor reflection',(0,-12,4),(1,.83,.57),1900,12),
            area('RIM · cold celestial edge',(-5,3,5),(.18,.55,1),2600,5),
            area('RIM · electrum edge',(6,3,2),(1,.58,.20),2300,5),
            area('TOP · elongated specular highlight',(0,-.8,10),(1,.90,.69),1900,5),
            area('LOW · faint armor separation',(0,-5,-5),(.28,.52,1),650,4)]
    ld=bpy.data.lights.new('REACTOR · volumetric radiance','POINT');ld.color=(1,.61,.24);ld.energy=100;ld.shadow_soft_size=.9
    lo=link(bpy.data.objects.new(ld.name,ld));lo.location=(0,-1.2,1.7);lights.append((lo,100))
    # A bounded, exceptionally thin volume provides atmosphere without a gray world.
    from geometry import prism
    fog=bpy.data.materials.new('Atmosphere · suspended gold dust');fog.use_nodes=True
    ns=fog.node_tree.nodes;ns.clear();v=ns.new('ShaderNodeVolumePrincipled')
    v.inputs['Density'].default_value=.0012;v.inputs['Color'].default_value=(.30,.38,.48,1)
    v.inputs['Anisotropy'].default_value=.25
    out=ns.new('ShaderNodeOutputMaterial');fog.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
    o=prism('ATMOSPHERE · subtle finite haze',(30,17,25),fog,location=(0,3,1),bevel=0)
    o.display_type='WIRE'
    target=empty('CAMERA · animated focus and look target',(0,0,1.0))
    d=bpy.data.cameras.new('Cinematic 50 mm');camera=link(bpy.data.objects.new('CAMERA · continuous cinematic take',d))
    camera.location=(0,-37,4);d.lens=50;d.sensor_width=36;d.clip_end=200
    con=camera.constraints.new('TRACK_TO');con.target=target;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y'
    d.dof.use_dof=True;d.dof.focus_object=target;d.dof.aperture_fstop=7.1
    bpy.context.scene.camera=camera
    detaildata=d.copy();detaildata.name='85 mm mechanical portrait';detaildata.lens=85
    detail=link(bpy.data.objects.new('CAMERA · 85 mm reactor detail',detaildata));detail.location=(3,-15,3.3);aim(detail,(0,0,1.7))
    detaildata.dof.aperture_fstop=6.3
    return lights,camera,target,detail
