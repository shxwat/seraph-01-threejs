"""Render presets, resumable image sequences, FFmpeg deliverable export.

The final animation requires --confirm-final. Previews and still images never
silently promote themselves into a 480-frame Cycles render.
"""
import json
import shutil
import subprocess
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
PRESETS={
    'LOW':dict(engine='BLENDER_EEVEE',samples=16,scale=35,cycles=24),
    'MEDIUM':dict(engine='BLENDER_EEVEE',samples=48,scale=100,cycles=64),
    'HIGH':dict(engine='CYCLES',samples=128,scale=100,cycles=128),
}


def configure(preset='MEDIUM',vertical=False):
    s=bpy.context.scene;p=PRESETS[preset]
    s.render.engine=p['engine'];s.render.resolution_x=1080 if vertical else 1920
    s.render.resolution_y=1920 if vertical else 1080;s.render.resolution_percentage=p['scale']
    s.render.fps=24;s.frame_start=1;s.frame_end=480
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
    s.render.film_transparent=False
    if hasattr(s,'eevee'):
        if hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=p['samples']
        if hasattr(s.eevee,'use_raytracing'):s.eevee.use_raytracing=preset!='LOW'
    s.cycles.samples=p['cycles'];s.cycles.use_denoising=True
    # Use Metal if available, CPU fallback remains fully supported.
    if preset=='HIGH':
        try:
            prefs=bpy.context.preferences.addons['cycles'].preferences
            prefs.compute_device_type='METAL';prefs.get_devices()
            found=False
            for dev in prefs.devices:
                dev.use=dev.type=='METAL';found=found or dev.use
            s.cycles.device='GPU' if found else 'CPU'
        except (AttributeError,TypeError,RuntimeError):s.cycles.device='CPU'
    s.view_settings.view_transform='AgX'
    try:s.view_settings.look='AgX - Medium High Contrast'
    except TypeError:pass
    s.view_settings.exposure=.45
    return s


def compositor():
    s=bpy.context.scene;s.use_nodes=True
    modern=hasattr(s,'compositing_node_group')
    if modern:
        tree=bpy.data.node_groups.new('SERAPH · cinematic optical pipeline','CompositorNodeTree')
        s.compositing_node_group=tree
        tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
    else:tree=s.node_tree
    n=tree.nodes;n.clear();l=tree.links
    r=n.new('CompositorNodeRLayers')
    g=n.new('CompositorNodeGlare')
    if hasattr(g,'glare_type'):
        g.glare_type='FOG_GLOW';g.quality='MEDIUM';g.threshold=1.7;g.size=7
    else:
        g.inputs['Type'].default_value='Fog Glow';g.inputs['Quality'].default_value='Medium'
        g.inputs['Threshold'].default_value=1.7;g.inputs['Size'].default_value=.30
        g.inputs['Strength'].default_value=.35
    g.name='Optical halation · controlled reactor bloom'
    o=n.new('NodeGroupOutput' if modern else 'CompositorNodeComposite')
    l.new(r.outputs['Image'],g.inputs['Image']);l.new(g.outputs['Image'],o.inputs['Image'])


def save():
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'seraph-01.blend'))


def ffmpeg(args):
    binary=shutil.which('ffmpeg')
    if not binary:raise RuntimeError('FFmpeg is required for MP4 export; PNG frames are preserved.')
    subprocess.run([binary,'-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)


def still(frame=264,path=None,preset='MEDIUM',vertical=False):
    s=configure(preset,vertical);s.frame_set(frame)
    # Portrait composition uses the entire structure, with camera data kept editable.
    original=s.camera
    if vertical:
        camera=original.copy();camera.data=original.data.copy();s.collection.objects.link(camera)
        camera.animation_data_clear();camera.data.animation_data_clear()
        camera.location=(0,-45,3.5);camera.data.lens=50;s.camera=camera
    s.render.filepath=str(path or ROOT/'output/previews'/('frame_%04d.png'%frame))
    bpy.ops.render.render(write_still=True)
    if vertical:
        s.camera=original;bpy.data.objects.remove(camera,do_unlink=True)
    return s.render.filepath


def preview(step=1,width=640):
    if step<1 or 480%step:raise ValueError('Preview step must be a positive divisor of 480.')
    if width<128 or width%2:raise ValueError('Preview width must be an even number of at least 128.')
    s=configure('LOW');s.render.resolution_x=width;s.render.resolution_y=round(width*9/32)*2
    s.render.resolution_percentage=100
    folder=ROOT/'output/previews/sequence';folder.mkdir(parents=True,exist_ok=True)
    frames=list(range(1,481,step))
    for i,f in enumerate(frames):
        file=folder/('%04d.png'%i)
        if file.exists():continue
        s.frame_set(f);s.render.filepath=str(file);bpy.ops.render.render(write_still=True)
        print('SERAPH_PREVIEW',i+1,len(frames),'timeline frame',f,flush=True)
    output=ROOT/'output/previews/seraph-01_20s_preview.mp4'
    ffmpeg(['-framerate',str(24/step),'-i',folder/'%04d.png','-vf','fps=24,format=yuv420p',
            '-c:v','libx264','-crf','19','-movflags','+faststart',output])
    # Ten-second showcase: assembly detail, hero reveal, transformation, open eye.
    ffmpeg(['-i',output,'-filter_complex',
            '[0:v]trim=start=4:end=6,setpts=PTS-STARTPTS[a];'
            '[0:v]trim=start=9:end=12,setpts=PTS-STARTPTS[b];'
            '[0:v]trim=start=14:end=17,setpts=PTS-STARTPTS[c];'
            '[0:v]trim=start=17.5:end=19.5,setpts=PTS-STARTPTS[d];'
            '[a][b][c][d]concat=n=4:v=1:a=0[v]',
            '-map','[v]','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',
            ROOT/'output/previews/seraph-01_10s_showcase_preview.mp4'])
    (ROOT/'output/previews/preview_metadata.json').write_text(json.dumps(dict(
        width=width,height=s.render.resolution_y,timeline_fps=24,sampled_fps=24/step,
        frame_step=step,rendered_frames=len(frames),duration_seconds=20,engine='EEVEE',
        note=('Every frame rendered at 24 fps. Silent.' if step==1 else
              'Timing preview; sampled poses are held when encoded at 24 fps. Silent.')),indent=2))


def stills(preset='MEDIUM'):
    folder=ROOT/'output/final';folder.mkdir(parents=True,exist_ok=True)
    for frame,name in ((176,'01_divine_assembly'),(240,'02_seraph_front'),(272,'03_revelation'),
                       (368,'04_transfiguration'),(432,'05_celestial_eye')):
        still(frame,folder/(name+'_1920x1080.png'),preset)
    still(240,folder/'seraph-01_vertical_1080x1920.png',preset,True)


def final_animation(preset='HIGH',vertical=False,confirmed=False):
    if not confirmed:raise RuntimeError('Final animation requires explicit user confirmation and --confirm-final.')
    s=configure(preset,vertical)
    tag='vertical' if vertical else 'landscape'
    folder=ROOT/'output/frames'/tag;folder.mkdir(parents=True,exist_ok=True)
    # Portrait camera is wider so the wings and full orbital cage stay in frame.
    if vertical:
        camera=s.camera.copy();camera.data=s.camera.data.copy();s.collection.objects.link(camera)
        camera.data.animation_data_clear();camera.data.lens=40;s.camera=camera
    save()  # Save configured scene before any expensive frame renders.
    for f in range(1,481):
        file=folder/('%04d.png'%f)
        if file.exists():continue
        s.frame_set(f);s.render.filepath=str(file);bpy.ops.render.render(write_still=True)
    output=ROOT/'output/final'/('seraph-01_'+tag+'_20s.mp4')
    ffmpeg(['-framerate','24','-start_number','1','-i',folder/'%04d.png',
            '-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',output])
    if not vertical:
        ffmpeg(['-i',output,'-filter_complex',
                '[0:v]trim=start=4:end=6,setpts=PTS-STARTPTS[a];'
                '[0:v]trim=start=9:end=12,setpts=PTS-STARTPTS[b];'
                '[0:v]trim=start=14:end=17,setpts=PTS-STARTPTS[c];'
                '[0:v]trim=start=17.5:end=19.5,setpts=PTS-STARTPTS[d];'
                '[a][b][c][d]concat=n=4:v=1:a=0[v]',
                '-map','[v]','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',
                ROOT/'output/final/seraph-01_10s_showcase.mp4'])
