# Existing Blender project inspection

Source: `../../seraph-01/seraph-01.blend`, Blender 5.2.0 LTS.
Source SHA-256: `af6548098e57f7697f02b60f6a21dd5f1ef714891e379aa9a63ced77396fbdad`.

## Hierarchy

- `SERAPH-01 · master control`: root of the existing creation.
- `BODY · folding skeletal control`: head, articulated spine, ribs, armor, arm/leg chains, ceremonial vanes.
- `LEFT WING · shoulder gimbal` / `RIGHT WING · shoulder gimbal`: 22 independently articulated feather controls each, layered vanes, pistons, scapula shields.
- `ORBIT 1` through `ORBIT 5 · precision celestial gimbal`: actual toothed rings, rails, inscription triplets, fasteners, traveling reliquary carriers.
- `REACTOR · miniature artificial star`: plasma surface, three containment gimbals, gears, luminous seams, magnetic filaments.
- `FINAL FORM · celestial mechanical eye`: 96 iris lamellae, five iris bearings, recessed pupil, upper/lower segmented eyelids.
- Incoming assembly slivers and suspended ion particles are actual linked geometry.
- Separate cinematic and reactor-detail cameras; the main camera uses a Track To constraint.

The complete per-object parent, type, modifier, constraint, and animation inventory is recorded in `blender-inspection.json`.

## Materials and procedural systems

Six metallic surface profiles: electrum gold, pale gold, black titanium, platinum machinery, oxidized bronze grooves, black optical aperture. Four primary emissive surfaces plus five independently animated orbital emission materials. No external image textures and no Geometry Nodes modifiers were found.

The metallic shaders use generated coordinates, a Noise Texture, stretched mapping, roughness modulation, and a small bump. glTF exports the original base PBR values; GLSL supplies a filtered micrograin approximation. Blender compositor glare, the finite fog volume, and area-light energy are handled separately in the viewer.

Bevel modifiers and beveled curve cables are evaluated into actual mesh geometry during export. There are 786 evaluated/converted objects, including 359 curves. Linked/shared mesh data remains shared where compatible.

## Animation

24 fps, frames 1–480. There are 477 source actions. Original movement uses object transform keyframes, not a skinned character rig. The exporter samples the scene into one glTF clip with 3,512 transform channels, preserving the articulated hierarchy.

Frames 1–96 awaken the reactor; 97–192 assemble the body; 193–288 reveal it; 289–384 fold the wings/body into the eye; 385–423 open the eyelids; 432 is the eye presentation pose. Five distinct orbital pulse curves peak at frames 404, 408, 412, 416, and 420. Camera constraints are evaluated, and lens changes plus material emission curves are sampled into the JSON sidecar.

## Python scripts reviewed

- `main.py`: presets, creation entry point, scene audit, editable `.blend` save.
- `geometry.py`: original modeled components, linked mesh details, rings, feathers, reactor, eye, ions, fragments.
- `materials.py`: original metallic and emission profiles and procedural shading.
- `rigging.py`: collections, mesh creation, linked objects, control parenting.
- `animation.py`: staged assembly, original transformations, orbital motion, emission curves.
- `lighting.py`: original area lights, cameras, constrained target, haze, compositor effects.
- `render.py`: preview/still/final render configuration and video generation.
- `review.py`: source geometry and Cycles validation previews.
- `verify_outputs.py`: existing image/video deliverable checks.

Function inventories and SHA-256 hashes for all nine scripts are recorded in the JSON audit. The conversion does not execute these scripts to rebuild or replace the source model.
