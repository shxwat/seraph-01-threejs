"""Reproduce the small Cycles check and material-free geometry inspection.

blender -b seraph-01.blend --python-exit-code 1 --python scripts/review.py
This renders two single frames; it never starts the final animation.
"""
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
import render


def main():
    s=render.configure('HIGH');s.cycles.samples=24
    s.render.resolution_percentage=35;s.frame_set(240)
    s.render.filepath=str(render.ROOT/'output/previews/cycles_validation.png')
    bpy.ops.render.render(write_still=True)
    s.render.engine='BLENDER_WORKBENCH';s.render.use_compositing=False
    s.render.resolution_percentage=50
    shading=s.display.shading
    shading.light='STUDIO';shading.color_type='SINGLE';shading.single_color=(.48,.48,.48)
    shading.show_shadows=True;shading.show_cavity=True;shading.cavity_type='BOTH'
    shading.background_type='WORLD';s.world.color=(.025,.025,.025)
    bpy.data.objects['ATMOSPHERE · subtle finite haze'].hide_render=True
    s.render.filepath=str(render.ROOT/'output/previews/geometry_clay.png')
    bpy.ops.render.render(write_still=True)


if __name__=='__main__':main()
