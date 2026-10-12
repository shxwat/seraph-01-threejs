# SERAPH-01 · The Mechanical God

The original procedural Blender mechanical god, brought into an interactive Three.js scene. Golden armor, articulated wings, five independent celestial rings, a glowing reactor, and the original deity-to-eye animation run in a fullscreen WebGL canvas.

## Run locally

```sh
cd seraph-realtime
npm ci
npm run dev
```

Drag to orbit, scroll to zoom, click the reactor to pulse it, press **T** to transform, **Space** to pause, and **R** to reset the camera.

The exported GLB is included. Blender is only needed when editing and re-exporting the original model.

- [Viewer, controls, export instructions, and verification](seraph-realtime/README.md)
- [Original Blender project and procedural source](seraph-01/README.md)
- [Source inspection and conversion decisions](seraph-realtime/qa/INSPECTION.md)

Stack: React, Vite, TypeScript, Three.js, React Three Fiber, drei, React Three Postprocessing, and Meshoptimizer.

## Vercel

The GitHub-connected Vercel project builds from **`seraph-realtime`**, using **Vite**, **`npm run build`**, and output directory **`dist`**. It uses Node **24.x**. Pushes to `main` deploy production; other branches create previews.

Rendered films, raw exports, and local dependencies are excluded from Git. The recording tool remains available at `/?showcase`; see the viewer README for instructions.
