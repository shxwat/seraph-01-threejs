// Lossless numeric compression. No decimation, quantization, flattening, or material replacement.
import { NodeIO, PropertyType } from '@gltf-transform/core'
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions'
import { dedup } from '@gltf-transform/functions'
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer'
import { readFile, writeFile, stat } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
const root=fileURLToPath(new URL('../',import.meta.url))
await Promise.all([MeshoptEncoder.ready,MeshoptDecoder.ready])
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.encoder':MeshoptEncoder,'meshopt.decoder':MeshoptDecoder})
const doc=await io.read(root+'qa/seraph.raw.glb')
await doc.transform(dedup({propertyTypes:[PropertyType.ACCESSOR,PropertyType.MESH]}))
doc.createExtension(EXTMeshoptCompression).setRequired(true).setEncoderOptions({method:EXTMeshoptCompression.EncoderMethod.QUANTIZE})
// QUANTIZE here is only the encoder mode: without a quantize transform all floats stay unchanged.
await io.write(root+'public/models/seraph.glb',doc)
const metadata=JSON.parse(await readFile(root+'public/models/seraph.metadata.json','utf8'))
if(!metadata.cameraAspect){
  // Convert Blender's nominal sensor-height angle to the actual 16:9 rendered vertical FOV.
  metadata.cameraSamples.forEach(c=>{c.fov=2*Math.atan(Math.tan(c.fov*Math.PI/360)*36/(24*(16/9)))*180/Math.PI})
  metadata.cameraAspect=16/9
  await writeFile(root+'public/models/seraph.metadata.json',JSON.stringify(metadata))
}
const report={rawBytes:(await stat(root+'qa/seraph.raw.glb')).size,
  compressedBytes:(await stat(root+'public/models/seraph.glb')).size,
  nodes:doc.getRoot().listNodes().length,meshes:doc.getRoot().listMeshes().length,
  materials:doc.getRoot().listMaterials().map(m=>m.getName()),
  animations:doc.getRoot().listAnimations().map(a=>({name:a.getName(),channels:a.listChannels().length})),
  geometrySimplified:false,vertexQuantization:false,compression:'EXT_meshopt_compression (lossless)'}
await writeFile(root+'qa/optimization.json',JSON.stringify(report,null,2))
console.log(report)
