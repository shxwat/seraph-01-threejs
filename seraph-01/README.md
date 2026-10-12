# SERAPH-01 · THE MECHANICAL GOD

An editable, deterministic Blender production: an electrum and titanium deity
assembles in a black void, unfurls 44 articulated metal feathers, and reorganizes
into a celestial mechanical eye. Five toothed orbital mechanisms enclose both
forms. Built entirely with Blender Python, with no downloaded models, textures,
web technologies, or external Python dependencies.

## Start here

Open **`seraph-01.blend`** in Blender. The file opens at the deity hero pose,
frame **240**. Press Numpad 0 for the camera. Frame **432** shows the open eye.
The viewport is set to Material Preview; on slower machines switch to Solid.
Press Space to inspect the animation, or scrub the five labeled timeline acts.
Material Preview uses Blender's studio environment; rendered output uses the
authored lighting and black world. In the Outliner, expand the six numbered
collections and the named mechanical controls to inspect or edit the scene.

The generator was executed and inspected in **Blender 5.2.0 LTS on Apple Silicon**.
The source includes compositor compatibility for Blender 4.3–5.x; Blender 4.3
itself has not been tested. Blender generally cannot open newer `.blend` files
in older versions, so regenerate from the scripts when using Blender 4.3.

## Contents

```
seraph-01/
  seraph-01.blend
  scripts/
    main.py          # Build, command-line dispatch, scene audit
    geometry.py      # Reusable procedural parts and both forms
    materials.py     # Brushed PBR metals and keyed emission
    rigging.py       # Hierarchy, linked meshes, assembly helpers
    animation.py     # Five acts, timing, transform, camera and light keys
    lighting.py      # Warm key, cool rim, reflection cards, thin haze
    render.py        # LOW / MEDIUM / HIGH, FFmpeg, final-render gate
    review.py        # Small Cycles frame and material-free geometry check
    verify_outputs.py # Standard-library output verification with ffprobe
  references/
    concept.png      # User-provided visual direction
    brief.md         # Original production brief
  output/
    scene_audit.json # Counts, asset checks, evaluated animation phases
    previews/        # Timing film, showcase, sequence, review images
    frames/          # Resumable final PNG sequences, after authorization
    final/           # Five landscape stills and one portrait still
```

The `.blend` also embeds the generator source in its Text Editor. The scripts
on disk are the authoritative reproducible version. No `requirements.txt` is
needed: `bpy`, `bmesh`, and `mathutils` ship with Blender. **FFmpeg** must be on
PATH for MP4 encoding; frame rendering itself does not depend on FFmpeg.

## Reproduction

Run all commands **from this `seraph-01` directory**. Quote the paths if calling
them from elsewhere. On macOS, the Blender executable can also be addressed as
`/Applications/Blender.app/Contents/MacOS/Blender`.

Rebuild the complete scene and save before rendering:

```sh
blender -b --python-exit-code 1 --python scripts/main.py -- --task build --preset MEDIUM
```

Run the structural and animation evaluation audit:

```sh
blender -b seraph-01.blend --python-exit-code 1 --python scripts/main.py -- --task audit
```

After the previews and stills are present, run the pre-final output check:

```sh
python3 scripts/verify_outputs.py
```

This verifies PNG dimensions, the 480-frame preview sequence, MP4 frame rates,
exact 20- and 10-second durations, and that the expensive final render has not
started. The result is saved as `output/deliverables_verified.json`.

Render a **20-second timing preview** and **10-second showcase preview**:

```sh
blender -b seraph-01.blend --python-exit-code 1 --python scripts/main.py -- --task preview --preview-width 640 --preview-step 1
```

The delivered preview renders every timeline frame: **480 poses at 24 fps**,
at **640×360**, using Eevee LOW. It is a full-motion, low-resolution preview.
Use `--preview-step 4` for a faster 120-pose timing preview at 6 sampled fps,
held in a 24 fps MP4. Delete the
`output/previews/sequence` folder before changing the preview width or step;
its existing frames are otherwise reused for resumability. Preview metadata
records the actual resolution and sampling rate. Both films are silent.

Generate five **1920×1080** stills and one **1080×1920** portrait still:

```sh
blender -b seraph-01.blend --python-exit-code 1 --python scripts/main.py -- --task stills --preset MEDIUM
```

Render one arbitrary frame, or add `--vertical` for portrait framing:

```sh
blender -b seraph-01.blend --python-exit-code 1 --python scripts/main.py -- --task still --frame 432 --preset MEDIUM --path output/previews/eye.png
```

An additional 85 mm reactor close-up can be reproduced with:

```sh
blender -b seraph-01.blend --python-exit-code 1 --python scripts/main.py -- --task still --camera detail --frame 264 --preset MEDIUM --path output/final/06_reactor_detail_1920x1080.png
```

Reproduce the small **672×378, 24-sample Cycles** validation image and the
**960×540** Workbench geometry inspection, with authored materials and scene
lights disabled for the latter:

```sh
blender -b seraph-01.blend --python-exit-code 1 --python scripts/review.py
```

The first Metal/Cycles render can spend time compiling GPU kernels before any
render progress appears. This review command renders two single images and
does not start either final film.

### Final films — explicit authorization required

The original brief says: **“Never launch an expensive full render without
explicit confirmation.”** Consequently, the high-resolution 480-frame film
exports are prepared but must be explicitly authorized before execution.
`--task final` refuses to render without `--confirm-final`.

After confirmation, the following export the full landscape film, a ten-second
landscape showcase edit, and the full portrait film:

```sh
blender -b seraph-01.blend --python-exit-code 1 --python scripts/main.py -- --task final --preset HIGH --confirm-final
blender -b seraph-01.blend --python-exit-code 1 --python scripts/main.py -- --task final --preset HIGH --vertical --confirm-final
```

Each film renders all **480 frames at 24 fps**. HIGH uses **Cycles, 128 samples,
denoising**, and Metal when available, with CPU fallback. PNG image sequences
are preserved so interrupted jobs can resume by rerunning the same command.
Before changing quality, geometry, timing, resolution, or camera, move/delete
the corresponding `output/frames/landscape` or `vertical` folder; cached
frames are trusted and not automatically invalidated. The output MP4s use H.264,
CRF 16, YUV420p, and fast-start metadata. No audio is generated.

The renderer saves the configured scene before starting final frames. It also
changes the saved project to the export camera/settings; regenerate with
`--task build` to return to the original editable hero setup.

## Quality and performance

| Preset | Engine | Rendering | Intended use |
|---|---|---|---|
| LOW | Eevee | 16 samples, 35% still resolution | Fast pose and timing review |
| MEDIUM | Eevee | 48 samples, full resolution, ray tracing | Presentation stills / faster final film |
| HIGH | Cycles | 128 samples, denoising, full resolution | Final production export |

LOW builds use fewer transient debris particles and ions. The main mechanical
geometry is preserved across presets: details are real meshes and curves,
with linked repetitions for bolts, engraved strokes, sparks, and optical
lamellae. There are no subdivision modifiers. A bevel is used on meaningful
armor edges. The physical rings have stepped cross-sections, modeled teeth,
radial connectors, luminous channels, geometric inscription strokes, and
traveling reliquaries. Visual complexity does not rely on a texture map.

All random placement uses the fixed seed **7301**. A mesh normal pass corrects
face orientation for mirrored armor. For a modest computer, use Solid viewport
shading and the LOW preset; material rendering includes thin volumetric haze
and many small parts, so real-time viewport playback is hardware-dependent.

## Animation and controls

| Frames | Time | Act |
|---|---|---|
| 1–96 | 00–04s | Darkness, first spark, incoming linked metal fragments |
| 97–192 | 04–08s | Vertebrae, armor, limbs and mask lock into place |
| 193–288 | 08–12s | Wings unfold, five rings align, camera orbits |
| 289–384 | 12–16s | Body folds; the same feather controls become an iris crown |
| 385–480 | 16–20s | Lids open, a ring pulse propagates, camera pulls back |

The final second decays to darkness and a tiny core at the same camera position
as frame 1, providing an intentional light-based loop transition. The hero
objects are not rebuilt with handlers; all transforms, lights, and emissions
are normal editable keyframes. AUTO_CLAMPED Bezier handles create arrival
pauses without overshooting the mechanical lock poses.

`SERAPH-01 · master control` owns the entire entity. `BODY · folding skeletal
control` folds the original articulated body behind the eye. Shoulder, elbow,
wrist, hip, knee, and shin controls form object-parented mechanical chains.
Each feather has its own articulation pivot, layered alloy vane, structural
keel, inlaid grooves, and toothed root bearing. This is a mechanical object rig,
not a skinned character armature or an IK rig.

`ORBIT 1…5` control the five independently aligned gimbals. The three reactor
containment gimbals and magnetic filaments have distinct controlled motion.
The `UPPER EYELID` and `LOWER EYELID` controls open the segmented almond frame.
Emission sockets named `Animated radiance` expose the pulsing star and rails.

The main tracked camera has a continuous 50 mm hero/orbit take and a narrower
assembly pass. `CAMERA · 85 mm reactor detail` is an additional close-up camera
for detail inspection and alternate renders. The portrait output widens the
field of view to keep the structure in frame instead of cropping the wings.

## Verification and deliverable limits

`output/scene_audit.json` is written only after the generator checks the timeline,
five orbit controls, linked instances, missing image dependencies, action count,
and finite world transforms at ten representative frames. This is structural
verification; rendered review images and the timing film establish appearance.

The delivered high-resolution PNG stills use Eevee. The preview MP4s are
low-resolution Eevee renders. **Full-resolution landscape and portrait MP4s, the final
showcase, and Cycles frame sequences remain pending final-render approval.**
No claim of a completed Cycles production film is implied by the editable scene
or the preview filenames. The attached concept guides the model's silhouette
and materials; the scene is a procedural interpretation, not a reconstruction
of every surface in the concept art.
