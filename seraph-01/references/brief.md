# PROJECT SERAPH-01 — THE MECHANICAL GOD
## Build a Cinematic, Procedurally Generated 3D Celestial Machine

You are a senior technical artist, procedural 3D engineer, Blender Python expert, and cinematic animation director.

Your mission is to create a breathtaking, production-quality 3D mechanical celestial entity named **SERAPH-01: THE MECHANICAL GOD**.

This is NOT a website, UI, Three.js demo, or simple 3D object.

This must be a real, fully editable, procedurally generated **Blender 3D project**, featuring intricate mechanical geometry, physically based materials, hierarchical animation, cinematic camera movement, lighting, and a dramatic transformation sequence.

Use the attached concept artwork as the primary visual reference.

### 1. TECHNOLOGY

- Blender 4.3+ with Python (`bpy`)
- Geometry Nodes where useful
- Procedural mesh generation
- Principled BSDF materials
- Eevee for previews, Cycles for final renders
- Object parenting, constraints, and keyframe animation
- Compositor glare, bloom, depth of field
- FFmpeg for final video export

Build everything programmatically using Python scripts executed inside Blender.

Do not use React, HTML, CSS, JavaScript, or web technologies.

### 2. THE ENTITY

Create an enormous floating biomechanical deity suspended in an infinite black void.

**Central body**
- Tall, imposing, humanoid-inspired mechanical silhouette
- Elegant elongated armored head with a featureless divine mask
- Narrow illuminated eyes
- Layered titanium and polished gold armor
- Exposed mechanical spine and rib-like structures
- A massive glowing energy reactor embedded in its chest
- Intricate mechanical joints, pistons, cables, and actuators
- Multiple articulated mechanical wings composed of individual feather-like metal blades
- Long floating ornamental elements beneath the torso

**Celestial ring system**
- Five large concentric orbital rings surrounding the entity
- Each ring must contain actual geometric details: gear teeth, engraved markings, radial supports, mechanical connectors, and luminous channels
- Rings rotate on different axes and at different speeds
- Nested smaller gyroscopic rings rotate around the central reactor
- Mechanical ornaments orbit along the rings

**Energy core**
- An extremely bright amber-white spherical reactor
- Several rotating containment shells
- Internal layered geometry suggesting a miniature artificial star
- Animated energy filaments
- Pulsing emission intensity
- Volumetric glow and subtle floating sparks

The entity should feel ancient, divine, technologically impossible, and intimidating.

### 3. PROCEDURAL DETAIL SYSTEM

Create reusable functions for:
- `create_gear()`
- `create_ring()`
- `create_armor_plate()`
- `create_piston()`
- `create_cable()`
- `create_mechanical_wing()`
- `create_energy_core()`
- `create_ornament()`
- `create_radial_array()`
- `create_celestial_head()`
- `create_eye_transformation()`

Use deterministic random seeds.

Generate hundreds or thousands of visually meaningful details through instancing and procedural repetition rather than creating thousands of unnecessarily expensive independent meshes.

No default cubes, placeholder spheres, or basic toruses should remain visible in the final composition unless they have been transformed into convincing detailed geometry.

### 4. MATERIALS

Create physically based procedural materials:

**Divine gold:** brushed gold with subtle imperfections and edge wear.

**Black titanium:** dark metallic armor with controlled roughness.

**Silver machinery:** reflective machined metal.

**Energy:** emissive amber-white surfaces with animated brightness.

**Ancient detailing:** engraved patterns, scratches, radial inscriptions, and ornamental grooves.

Avoid flat plastic-looking surfaces.

Use bevels, weighted normals, micro-details, and proper metallic reflections.

### 5. CINEMATIC ANIMATION — 20 SECONDS

24 FPS, 480 frames.

**00–04 seconds — THE AWAKENING**

Complete darkness.

A tiny golden energy source appears.

Hundreds of mechanical fragments float toward the center.

The reactor slowly ignites.

**04–08 seconds — DIVINE ASSEMBLY**

Mechanical components assemble into the central body.

The spine forms.

Armor plates lock into position.

The celestial head emerges.

Camera slowly pushes toward the entity.

**08–12 seconds — THE REVELATION**

Massive mechanical wings unfold.

Five orbital rings rotate into alignment.

The energy core becomes brighter.

Camera performs a dramatic orbital movement.

**12–16 seconds — THE TRANSFORMATION**

The wings retract and separate into fragments.

The central body folds inward.

Mechanical rings realign.

The entity transforms into a giant celestial mechanical eye.

**16–20 seconds — THE FINAL FORM**

The eye opens.

Its central reactor resembles an illuminated iris.

A powerful pulse of light travels through the surrounding rings.

The camera pulls back to reveal the full structure.

Finish with a composition that can transition smoothly into the opening shot.

Use carefully designed interpolation curves, mechanical timing, and secondary motion.

No arbitrary spinning or random motion.

### 6. CAMERA AND LIGHTING

Use cinematic camera choreography:
- 50mm hero shots
- 85mm mechanical close-ups
- Slow orbital camera movements
- Strong silhouettes
- Controlled depth of field
- Subtle atmospheric haze

Lighting:
- Warm gold key light
- Cool silver-blue rim light
- Bright reactor emission
- Controlled reflections across armor
- Dark, high-contrast background

The model must remain visually readable throughout the animation.

### 7. PROJECT STRUCTURE

Create:

seraph-01/
- scripts/
  - main.py
  - geometry.py
  - materials.py
  - rigging.py
  - animation.py
  - lighting.py
  - render.py
- output/
  - previews/
  - frames/
  - final/
- references/
- README.md
- requirements.txt (only if external Python packages are needed)
- seraph-01.blend

### 8. RENDER DELIVERABLES

Produce:
1. Editable Blender project
2. Complete procedural Python source code
3. Full 20-second animation
4. 1920×1080 cinematic render
5. 1080×1920 vertical render suitable for social media
6. Five high-resolution still renders
7. A short 8–12 second showcase edit
8. Instructions to reproduce every output

### 9. PERFORMANCE REQUIREMENTS

- Preview mode must be usable on modest hardware.
- Use linked mesh instances for repeated details.
- Avoid unnecessary subdivisions.
- Provide LOW, MEDIUM, and HIGH quality presets.
- Render a low-resolution preview before attempting the final animation.
- Never launch an expensive full render without explicit confirmation.
- Save the Blender project before rendering.

### 10. EXECUTION RULES

Do not stop after explaining the approach.

Implement the actual Blender Python scripts and build the project.

Work in stages:

**Stage 1:** Generate the complete static mechanical deity.

**Stage 2:** Apply production-quality materials and lighting.

**Stage 3:** Implement hierarchical mechanical rigging.

**Stage 4:** Animate assembly, awakening, and transformation.

**Stage 5:** Configure cinematic cameras and rendering.

**Stage 6:** Generate previews, inspect results, and fix visual problems.

If Blender is installed, execute the scripts and verify the resulting scene. If Blender is unavailable, still generate complete runnable source files and clearly identify what remains unverified.

Do not claim that rendering or verification succeeded unless it actually did.

### FINAL CREATIVE DIRECTION

The result should look like an ancient celestial machine designed by a civilization millions of years ahead of humanity.

Think: impossible engineering, sacred geometry, mechanical divinity, monumental scale, and cinematic science fiction.

Avoid generic robots, cartoonish armor, random floating shapes, and simplistic glowing rings.

**Make the geometry impressive even with all lights and materials disabled.**

The final result should feel like a legendary boss reveal from an AAA science-fiction game.

Begin implementing the actual project now.
