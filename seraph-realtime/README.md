# SERAPH-01 · real-time conversion

Fullscreen interactive rendering of the existing `../seraph-01/seraph-01.blend` asset. The original model, armor, wings, five celestial rings, reactor, mechanical eye, particles, and animation are exported from that file. The Blender file is unchanged.

## Run

From this directory:

```sh
npm ci
npm run dev
```

Open the Local URL printed by Vite (normally http://127.0.0.1:5173). The exported model is included; Blender is only required to re-export after editing the source. Tested with Node 26.4, npm 11.17, and Blender 5.2 LTS. A browser with WebGL 2 is required.

```sh
npm run build
npm run preview
```

`dist/` is the deployable static application. Keep its `models/` folder alongside its generated assets. All model data, shaders, and reflection lighting are local; there are no remote model, texture, or HDR downloads.

## Controls

| Input | Behavior |
| --- | --- |
| Drag / touch drag | Orbit the model |
| Scroll / pinch | Smooth camera zoom |
| Click the reactor | Reactor burst and staggered ring pulse |
| Space | Pause/resume all animation; the camera remains usable |
| T | Play the original deity-to-eye animation; press again to reverse |
| R | Reset the camera and leave automatic camera mode |
| C | Replay the complete Blender sequence with its evaluated camera path |
| Q | Cycle Auto → High → Low quality |
| H / ? button | Show the control legend |

The viewer opens at Blender frame 240. Transformation plays to frame 432 at the source rate of 24 fps (eight seconds), including the original folded wings, collapsing body, iris, and eyelids. The full cinematic loops frames 1–480, approximately 20 seconds. T leaves the full sequence and starts from the deity pose. Idle ring rotation, reactor gyroscopes, breathing light, floating motion, and slight wing articulation operate on the original named controls. They fade into the baked animation when transformation starts.

## What was inspected and preserved

The source contains 3,199 objects and 477 actions. The export contains 3,181 named nodes, 2,811 renderable mesh instances, 401 shared meshes, 350,460 triangles, 15 distinct materials, and one baked scene clip with 3,512 transform tracks. The scene audit is in `qa/blender-inspection.json`; a readable explanation is in `qa/INSPECTION.md`.

Names and parenting are retained. Blender's exact names are also stored in `userData.originalName`, since Three.js sanitizes animation binding names. Geometry uses the original scale and relative positions, with the standard Blender Z-up → glTF Y-up conversion. The exporter evaluates bevels and the 359 beveled cable curves into mesh data. It excludes hidden construction templates, the original lighting rig, and the renderer-specific fog volume.

`useGLTF` loads the original export with Meshopt decoding. `THREE.AnimationMixer` evaluates the imported clip. Rendering uses Three.js `BatchedMesh` to draw compatible geometry by original material while keeping the complete animated transform hierarchy. Each source instance retains its own world matrix; the model is not flattened into one static mesh or rotated as a whole.

## Blender effects adapted for the GPU

| Blender feature | Real-time implementation |
| --- | --- |
| Gold, pale gold, titanium, silver, bronze, optical metal | Distinct original PBR colors, metalness, and roughness |
| Generated brushed-metal Noise shader | Derivative-filtered GLSL micrograin on the original metallic surfaces |
| Emission socket keyframes | 480 source samples per emissive material, interpolated during playback |
| Five independent orbital pulse actions | Five separate material curves, preserving peak frames 404/408/412/416/420 |
| Area-light reflections | Locally generated HDR studio environment and warm/cool direct lighting |
| Camera Track To constraint and lens animation | Evaluated Blender position/target/FOV sidecar, interpolated during cinematic mode |
| Key light fade | Exported light-power curve applied during the original sequence |
| Compositor glare and volume haze | Restrained bloom and a soft atmospheric GLSL backdrop |
| Suspended ion particles | Original exported particle geometry and transforms |

ACES tone mapping, high-resolution reflections, multisampled postprocessing, and ambient occlusion are enabled in High/Auto. The GLSL grain and haze approximate Blender's renderer-specific shaders; real-time lighting is tuned separately and is not a pixel-identical Cycles render. There are no image textures to downsample. No floor was introduced beneath the floating figure, so ground contact shadows are unnecessary.

## Performance

Lossless Meshopt compression reduces the GLB from **28,714,176 to 8,882,692 bytes**, with no vertex decimation or position quantization. All materials and named nodes remain distinct. The 2,811 mesh instances are rendered in 15 material batches; total GPU calls also include depth/normal and postprocessing passes. Collapsed objects with negligible scale are omitted from drawing until visible again.

Auto uses a device pixel ratio of 1–1.5 and switches down after sustained low frame rate. Low caps DPR at 1, lowers reflection resolution, and disables ambient occlusion and multisampled postprocessing. Both settings preserve the same geometry and animation. The Q key provides a manual fallback. GPU performance varies; the measured browser run is recorded in `qa/browser-verification.json` rather than treated as a guarantee for other devices.

## Re-export and verify

Run these from this directory after editing the original Blender project:

```sh
npm run export:model
npm run optimize:model
npm run verify:model
npm run verify:runtime
npm run build
```

The exporter reads the existing `.blend`, samples the animation, writes `qa/seraph.raw.glb` and `public/models/seraph.metadata.json`, and never invokes the original geometry generator or saves over the Blender file. The optimizer writes `public/models/seraph.glb`. Raw export and runtime dependencies are excluded from the production build. Re-exporting is unnecessary for normal use.

Verification compares every exported vertex before/after compression, checks node parenting, checks fourteen timeline samples against evaluated Blender transforms, verifies all five emission pulse peaks, and exercises 2,000 idle updates plus forward/reverse animation on the viewer's batched hierarchy. Current reports show zero vertex position error and maximum sampled transform error below 0.000001. Browser verification covers the visible eye transformation, reversal, pause/resume, reactor click, camera controls, cinematic playback, and Low quality.

## Source layout

| File | Purpose |
| --- | --- |
| `src/Experience.tsx` | Original GLB loading, animation, lighting, camera, interaction, effects |
| `src/batching.ts` | Material batching with the source hierarchy and stable pose restoration |
| `src/materials.ts` | Original material preservation and brushed-metal shader |
| `src/Atmosphere.tsx` | Atmospheric backdrop shader |
| `src/main.tsx` | Minimal controls, keyboard input, loading/error state |
| `scripts/export_blender.py` | Inspect and export the existing Blender project |
| `scripts/optimize-model.mjs` | Lossless Meshopt compression |
| `scripts/verify-model.mjs` | Source/export fidelity checks |
| `scripts/verify-runtime.mjs` | Viewer pose and batching regression checks |

Stack: React, Vite, TypeScript, Three.js, React Three Fiber, drei, React Three Postprocessing, and Meshoptimizer. Existing animation and delta-time playback cover the motion without requiring GSAP.

## Showcase recording

The finished live browser recording is in the local `output/showcase/` directory (large video files are excluded from Git):

- `SERAPH-01-ThreeJS-Showcase-1080p.mp4`: 38 seconds, 1920×1080, 60 fps, H.264/AAC, full-quality version.
- `SERAPH-01-ThreeJS-Showcase-Share.mp4`: same sequence at 30 fps, approximately 15 MB, for convenient sharing.
- `SERAPH-01-Showcase-Poster.jpg`: title/preview image.
- `seraph-01-threejs-live.webm`: original browser capture, retained without editing.

The sequence shows the actual Three.js rendering with a choreographed live camera, the regular reactor pulse command, and forward/reverse playback through the existing AnimationMixer. It includes small runtime/stack labels, with no fake frame-rate numbers. The only edit after capture is MP4 encoding and an original synthesized electronic sound bed. The recording is not a Blender-rendered animation.

To record again, run the app, open `/?showcase`, use a 16:9 viewport, and click **Record 1080p showcase**. After 38 seconds, use **Download recording**. The exported video is composed directly from the finished WebGL canvas after postprocessing; the controls and other desktop apps are excluded. The ordinary viewer route stays fullscreen and contains none of the recording titles. Sound design can be regenerated with `python3 scripts/showcase-sound.py` (requires NumPy). The capture and output checks are recorded in `qa/showcase-verification.json`.
