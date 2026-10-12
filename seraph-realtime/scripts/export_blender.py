"""Export the existing SERAPH .blend, never regenerate or save over its source.

blender -b ../seraph-01/seraph-01.blend --python-exit-code 1 --python scripts/export_blender.py
"""
import ast
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/models'
OUT.mkdir(parents=True,exist_ok=True)
(ROOT/'qa').mkdir(parents=True,exist_ok=True)
SOURCE=Path(bpy.data.filepath)
SCENE=bpy.context.scene
HERO=240


def descendants(root):
    return [root,*root.children_recursive]


def profile(mat):
    p=dict(name=mat.name,color=[.5,.5,.5],metalness=0,roughness=.4,emissive=[0,0,0],emissiveStrength=0)
    if not mat.use_nodes:return p
    for n in mat.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED':
            p.update(color=list(n.inputs['Base Color'].default_value[:3]),
                     metalness=n.inputs['Metallic'].default_value,roughness=n.inputs['Roughness'].default_value)
            if n.inputs['Roughness'].is_linked:p['surface']='brushed-alloy'
        elif n.type=='EMISSION':
            p.update(emissive=list(n.inputs['Color'].default_value[:3]),emissiveStrength=n.inputs['Strength'].default_value)
    return p


def gltf_matrix(matrix):
    # Blender Z-up -> glTF Y-up, where Blender's front (-Y) becomes glTF +Z.
    from mathutils import Matrix
    c=Matrix.Rotation(-math.pi/2,4,'X')
    return c@matrix@c.inverted()


def run():
    assert 'SERAPH-01 · master control' in bpy.data.objects,'Load the original .blend first.'
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    master=bpy.data.objects['SERAPH-01 · master control']
    SCENE.frame_set(HERO)
    included=[o for o in descendants(master) if not o.hide_render]
    camera=SCENE.camera
    target=bpy.data.objects['CAMERA · animated focus and look target']
    included += [camera,bpy.data.objects['CAMERA · 85 mm reactor detail'],target]
    included=list(dict.fromkeys(included))
    all_materials={m.name:m for o in included if o.type in {'MESH','CURVE'} for m in o.data.materials if m}
    profiles={name:profile(m) for name,m in all_materials.items()}
    report=dict(source=str(SOURCE),sourceSha256=digest,blender=bpy.app.version_string,
                sourceObjects=len(SCENE.objects),exportObjects=len(included),
                objectTypes=dict(Counter(o.type for o in included)),
                hierarchy=[dict(name=o.name,parent=o.parent.name if o.parent else None,type=o.type,
                                modifiers=[m.type for m in o.modifiers],constraints=[c.type for c in o.constraints],
                                animated=bool(o.animation_data and o.animation_data.action)) for o in included],
                materialProfiles=profiles,textures=[im.name for im in bpy.data.images if im.source=='FILE'],
                geometryNodes=[o.name for o in included if any(m.type=='NODES' for m in o.modifiers)],
                actions=[dict(name=a.name,slots=len(a.slots) if hasattr(a,'slots') else 1) for a in bpy.data.actions],
                scripts=[])
    for file in sorted((SOURCE.parent/'scripts').glob('*.py')):
        source=file.read_text()
        report['scripts'].append(dict(name=file.name,sha256=hashlib.sha256(source.encode()).hexdigest(),
            functions=[n.name for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef)]))
    # Sample unsupported material/light animation and the evaluated constrained camera.
    emission={name:[] for name,p in profiles.items() if p['emissiveStrength']>0}
    camera_samples=[];light_samples=[];verification=[]
    checkpoints=(1,96,176,240,288,336,384,404,408,412,416,420,432,480)
    checkpoint_names=[o.name for o in included if o.name.startswith(('ORBIT ','LEFT WING','RIGHT WING','FINAL FORM','BODY ·','REACTOR ·','UPPER EYELID','LOWER EYELID'))]
    for frame in range(1,481):
        SCENE.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get()
        for name,values in emission.items():
            n=all_materials[name].node_tree.nodes.get('Animated radiance')
            values.append(float(n.inputs['Strength'].default_value))
        matrix=gltf_matrix(camera.evaluated_get(deps).matrix_world)
        pos,quat,scale=matrix.decompose()
        t=gltf_matrix(target.matrix_world).translation
        camera_samples.append(dict(position=list(pos),quaternion=list(quat),target=list(t),
                                   fov=math.degrees(2*math.atan(math.tan(camera.data.angle/2)/(SCENE.render.resolution_x/SCENE.render.resolution_y)))))
        light_samples.append(next(o.data.energy/1700 for o in SCENE.objects if o.name.startswith('KEY ·')))
        if frame in checkpoints:
            verification.append(dict(frame=frame,nodes={name:[v for row in gltf_matrix(bpy.data.objects[name].matrix_world) for v in row]
                                                       for name in checkpoint_names}))
    metadata=dict(sourceSha256=digest,fps=24,frameStart=1,frameEnd=480,heroFrame=HERO,eyeFrame=432,cameraAspect=16/9,
                  duration=480/24,materials=profiles,emissionSamples=emission,cameraSamples=camera_samples,
                  lightSamples=light_samples,checkpoints=verification,
                  controls=dict(master=master.name,body='BODY · folding skeletal control',
                  orbits=[o.name for o in included if o.name.startswith('ORBIT ')],
                  wings=[o.name for o in included if 'WING · shoulder' in o.name],
                  reactor='REACTOR · miniature artificial star',eye='FINAL FORM · celestial mechanical eye'))
    SCENE.frame_set(HERO)
    # Keep each original PBR surface; port only the unsupported shader noise to GLSL.
    for name,mat in all_materials.items():
        p=profiles[name];mat.node_tree.animation_data_clear();mat.node_tree.nodes.clear()
        bs=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        bs.inputs['Base Color'].default_value=(*p['color'],1)
        bs.inputs['Metallic'].default_value=p['metalness'];bs.inputs['Roughness'].default_value=p['roughness']
        bs.inputs['Emission Color'].default_value=(*p['emissive'],1)
        bs.inputs['Emission Strength'].default_value=p['emissiveStrength']
        out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(bs.outputs[0],out.inputs['Surface'])
        mat['originalName']=name;mat['surface']=p.get('surface','emissive' if p['emissiveStrength'] else 'metal')
    # Evaluate real bevels and beveled cable curves to triangles. Share identical data.
    deps=bpy.context.evaluated_depsgraph_get();cache={};converted=0
    for o in included:
        o['originalName']=o.name
        if o.type not in {'MESH','CURVE'}:continue
        if o.type=='MESH' and not o.modifiers:continue
        key=(o.data.as_pointer(),tuple((m.type,round(getattr(m,'width',0),6),getattr(m,'segments',0)) for m in o.modifiers))
        if key not in cache:
            cache[key]=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
        mesh=cache[key]
        # Conversion via operator preserves object ID, hierarchy, actions and names.
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
        if o.type=='CURVE':bpy.ops.object.convert(target='MESH')
        o.data=mesh
        for modifier in list(o.modifiers):o.modifiers.remove(modifier)
        converted+=1
    bpy.ops.object.select_all(action='DESELECT')
    for o in included:o.select_set(True)
    SCENE.frame_start=1;SCENE.frame_end=480
    available=bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    options=dict(filepath=str(ROOT/'qa/seraph.raw.glb'),export_format='GLB',use_selection=True,
                 export_extras=True,export_yup=True,export_cameras=True,export_lights=False,
                 export_animations=True,export_animation_mode='SCENE',export_frame_range=True,
                 export_frame_step=1,export_force_sampling=True,export_bake_animation=True,
                 export_anim_scene_split_object=False,export_anim_slide_to_zero=True,
                 export_optimize_animation_size=True,export_materials='EXPORT',
                 export_apply=False,export_hierarchy_flatten_objs=False,export_pointer_animation=False,
                 export_shared_accessors=True,export_gpu_instances=False)
    bpy.ops.export_scene.gltf(**{k:v for k,v in options.items() if k in available})
    report.update(convertedObjects=converted,rawBytes=(ROOT/'qa/seraph.raw.glb').stat().st_size,
                  exportOptions=options,webReimplementations=['Procedural micrograin shader','Animated emission sockets',
                  'Area-light/HDR reflections','Volumetric haze and compositor bloom','Camera lens animation'])
    (OUT/'seraph.metadata.json').write_text(json.dumps(metadata,separators=(',',':'),ensure_ascii=False))
    (ROOT/'qa/blender-inspection.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==digest,'Source blend changed!'
    print('SERAPH_EXPORT_COMPLETE',report['rawBytes'],len(included),flush=True)


if __name__=='__main__':run()
