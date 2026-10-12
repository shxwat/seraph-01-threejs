"""Build SERAPH-01 inside Blender, or render an existing saved production.

blender -b --python scripts/main.py -- --preset MEDIUM --task build
blender -b seraph-01.blend --python scripts/main.py -- --task preview
"""
import argparse
import json
import sys
from pathlib import Path
import bpy

SCRIPTS=Path(__file__).resolve().parent
sys.path.insert(0,str(SCRIPTS))
from materials import create_materials
from geometry import build_scene_geometry
from lighting import build_lighting
from animation import animate
import render


def args():
    p=argparse.ArgumentParser(description='SERAPH-01 procedural production')
    p.add_argument('--preset',choices=('LOW','MEDIUM','HIGH'),default='MEDIUM')
    p.add_argument('--task',choices=('build','preview','still','stills','final','audit'),default='build')
    p.add_argument('--frame',type=int,default=240)
    p.add_argument('--path',type=str)
    p.add_argument('--vertical',action='store_true')
    p.add_argument('--camera',choices=('cinematic','detail'),default='cinematic')
    p.add_argument('--preview-step',type=int,default=1)
    p.add_argument('--preview-width',type=int,default=640)
    p.add_argument('--confirm-final',action='store_true')
    return p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])


def audit():
    s=bpy.context.scene
    report=dict(blender=bpy.app.version_string,objects=len(s.objects),
                meshes=len(bpy.data.meshes),linked_mesh_instances=sum(1 for o in s.objects if o.type=='MESH' and o.data.users>1),
                unique_mesh_vertices=sum(len(m.vertices) for m in bpy.data.meshes),
                actions=len(bpy.data.actions),frames=[s.frame_start,s.frame_end],fps=s.render.fps,
                cameras=[o.name for o in s.objects if o.type=='CAMERA'],
                orbit_controls=[o.name for o in s.objects if o.name.startswith('ORBIT ')],
                materials=len(bpy.data.materials),missing_external_assets=[])
    for image in bpy.data.images:
        if image.source=='FILE' and not image.packed_file and image.filepath and not Path(bpy.path.abspath(image.filepath)).exists():
            report['missing_external_assets'].append(image.filepath)
    assert report['frames']==[1,480] and report['fps']==24
    assert len(report['orbit_controls'])==5
    assert report['linked_mesh_instances']>500
    assert report['actions']>100
    assert not report['missing_external_assets']
    pulses=[m for m in bpy.data.materials if m.name.startswith('Orbital pulse · traveling wave') and m.users>0]
    assert len(pulses)==5
    assert len({m.node_tree.animation_data.action.as_pointer() for m in pulses})==5
    for i,m in enumerate(sorted(pulses,key=lambda x:x.name)):
        s.frame_set(404+i*4)
        assert abs(m.node_tree.nodes['Animated radiance'].inputs['Strength'].default_value-12)<.01
    report['independent_orbital_pulse_actions']=5
    # Evaluate every key phase and reject non-finite transforms or broken parent chains.
    import math
    for frame in (1,48,96,176,240,288,336,384,432,480):
        s.frame_set(frame)
        for o in s.objects:
            assert all(math.isfinite(x) for row in o.matrix_world for x in row), (frame,o.name)
    report['evaluated_frames']=[1,48,96,176,240,288,336,384,432,480]
    (render.ROOT/'output/scene_audit.json').write_text(json.dumps(report,indent=2))
    print('SERAPH AUDIT',json.dumps(report),flush=True)
    return report


def build(preset):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.users==0 or c.name=='Collection':bpy.data.collections.remove(c)
    mats=create_materials();rig=build_scene_geometry(mats,preset)
    lights,camera,target,detail=build_lighting()
    animate(rig,mats,lights,camera,target)
    render.configure(preset);render.compositor()
    s=bpy.context.scene
    for f,name in ((1,'I · THE AWAKENING'),(97,'II · DIVINE ASSEMBLY'),(193,'III · THE REVELATION'),
                   (289,'IV · THE TRANSFORMATION'),(385,'V · THE FINAL FORM')):
        s.timeline_markers.new(name,frame=f)
    s['Project']='SERAPH-01 / THE MECHANICAL GOD'
    s['Seed']=7301;s['Quality preset']=preset
    s['Final render authorization']='Required: --confirm-final after user confirmation'
    s['Animation notes']='24 fps / 480 frames / five acts; frame 240 is the deity hero, 432 the eye.'
    # Embed readable source files in the Blender Text Editor as well as on disk.
    for path in SCRIPTS.glob('*.py'):
        text=bpy.data.texts.new(path.name);text.write(path.read_text())
    s.frame_set(240)
    # Opening the .blend presents a useful camera-framed material viewport.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.shading.type='MATERIAL'
    audit();s.frame_set(240);render.save()


if __name__=='__main__':
    a=args()
    if a.task=='build':build(a.preset)
    else:
        if 'SERAPH-01 · master control' not in bpy.data.objects:
            raise RuntimeError('Open seraph-01.blend first, or run --task build.')
        if a.task=='preview':render.preview(a.preview_step,a.preview_width)
        elif a.task=='still':
            if a.camera=='detail':bpy.context.scene.camera=bpy.data.objects['CAMERA · 85 mm reactor detail']
            render.still(a.frame,a.path,a.preset,a.vertical)
        elif a.task=='stills':render.stills(a.preset)
        elif a.task=='final':render.final_animation(a.preset,a.vertical,a.confirm_final)
        elif a.task=='audit':audit()
