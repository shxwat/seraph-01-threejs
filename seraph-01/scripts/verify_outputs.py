"""Standalone post-render QA. Uses only Python's standard library and ffprobe."""
import json
import struct
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def png_size(path):
    with path.open('rb') as file:header=file.read(24)
    assert header[:8]==b'\x89PNG\r\n\x1a\n', str(path)
    return struct.unpack('>II',header[16:24])


def video_info(path,duration):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
                    '-show_entries','stream=width,height,avg_frame_rate,nb_frames:format=duration',
                    '-of','json',str(path)],text=True))
    stream=data['streams'][0]
    assert abs(float(data['format']['duration'])-duration)<.05,(path,data)
    assert stream['avg_frame_rate']=='24/1',(path,data)
    assert (stream['width'],stream['height'])==(640,360),(path,data)
    assert int(stream['nb_frames'])==duration*24,(path,data)
    return dict(file=str(path.relative_to(ROOT)),**stream,duration_seconds=float(data['format']['duration']))


def main():
    stills=[]
    for name in ('01_divine_assembly','02_seraph_front','03_revelation','04_transfiguration','05_celestial_eye'):
        path=ROOT/'output/final'/(name+'_1920x1080.png')
        size=png_size(path);assert size==(1920,1080),(path,size)
        stills.append(dict(file=str(path.relative_to(ROOT)),width=size[0],height=size[1]))
    path=ROOT/'output/final/seraph-01_vertical_1080x1920.png'
    size=png_size(path);assert size==(1080,1920)
    stills.append(dict(file=str(path.relative_to(ROOT)),width=size[0],height=size[1]))
    videos=[video_info(ROOT/'output/previews/seraph-01_20s_preview.mp4',20),
            video_info(ROOT/'output/previews/seraph-01_10s_showcase_preview.mp4',10)]
    metadata=json.loads((ROOT/'output/previews/preview_metadata.json').read_text())
    assert metadata['frame_step']==1 and metadata['rendered_frames']==480
    sequence=list((ROOT/'output/previews/sequence').glob('*.png'));assert len(sequence)==480
    for image in sequence:assert png_size(image)==(640,360),str(image)
    audit=json.loads((ROOT/'output/scene_audit.json').read_text())
    assert len(audit['orbit_controls'])==5 and not audit['missing_external_assets']
    assert (ROOT/'seraph-01.blend').stat().st_size>100000
    # Absence of final animation frames proves the authorization gate was honored.
    final_frames=list((ROOT/'output/frames').rglob('*.png'))
    assert not final_frames,'Final frames unexpectedly exist before authorization'
    report=dict(status='PASS',scene_audit=audit,stills=stills,preview_videos=videos,
                preview_metadata=metadata,preview_png_frames=len(sequence),
                pending=['1920×1080 final 20-second MP4','1080×1920 final 20-second MP4',
                         'Final-quality ten-second showcase','Cycles final frame sequences'],
                final_render_started=False)
    (ROOT/'output/deliverables_verified.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=='__main__':main()
