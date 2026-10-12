import { readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import assert from 'node:assert/strict'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { MeshoptDecoder } from 'meshoptimizer'
import { AnimationMixer, LoopOnce } from 'three'
import validator from 'gltf-validator'
const root=fileURLToPath(new URL('../',import.meta.url))
const bytes=await readFile(root+'public/models/seraph.glb')
const raw=await readFile(root+'qa/seraph.raw.glb')
const metadata=JSON.parse(await readFile(root+'public/models/seraph.metadata.json','utf8'))
const loader=new GLTFLoader().setMeshoptDecoder(MeshoptDecoder)
const load=async buffer=>loader.parseAsync(buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength),'')
const [gltf,original]=await Promise.all([load(bytes),load(raw)])
const validation=await validator.validateBytes(new Uint8Array(bytes),{uri:'seraph.glb',maxIssues:50})
assert.equal(validation.issues.numErrors,0,JSON.stringify(validation.issues))
assert.equal(gltf.animations.length,1)
const mixer=new AnimationMixer(gltf.scene)
const action=mixer.clipAction(gltf.animations[0]);action.setLoop(LoopOnce,1);action.clampWhenFinished=true;action.play()
const named=new Map();let meshes=0;let triangles=0;let geometryError=0;let attributeError=0
gltf.scene.traverse(o=>{if(o.userData.originalName)named.set(o.userData.originalName,o);if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3}})
const originalNames=new Map();original.scene.traverse(o=>{if(o.userData.originalName)originalNames.set(o.userData.originalName,o)})
// Meshopt may cyclically rotate a triangle's three indices for compression.
// Compare oriented triangles, retaining winding and every triangle, rather than byte order.
const trianglesOf=g=>{
  const a=g.index?.array??Uint32Array.from({length:g.attributes.position.count},(_,i)=>i),result=[]
  for(let i=0;i<a.length;i+=3){const x=a[i],y=a[i+1],z=a[i+2];result.push([`${x},${y},${z}`,`${y},${z},${x}`,`${z},${x},${y}`].sort()[0])}
  return result.sort()
}
assert.equal(named.size,originalNames.size,'Node names/hierarchy were removed')
for(const [name,o] of originalNames){
  const n=named.get(name);assert.ok(n,name)
  assert.equal(n.parent?.userData.originalName,o.parent?.userData.originalName,'Parent changed: '+name)
  if(!o.isMesh)continue
  assert.equal(n.geometry.attributes.position.count,o.geometry.attributes.position.count,name)
  const a=o.geometry.attributes.position,b=n.geometry.attributes.position
  for(let i=0;i<a.count;i++)for(let c=0;c<3;c++)geometryError=Math.max(geometryError,Math.abs(a.array[i*a.itemSize+c]-b.array[i*b.itemSize+c]))
  assert.deepEqual(Object.keys(n.geometry.attributes).sort(),Object.keys(o.geometry.attributes).sort(),name+' attributes')
  for(const key of Object.keys(o.geometry.attributes)){
    const a=o.geometry.attributes[key],b=n.geometry.attributes[key]
    assert.equal(a.array.length,b.array.length,name+' '+key)
    for(let i=0;i<a.array.length;i++)attributeError=Math.max(attributeError,Math.abs(a.array[i]-b.array[i]))
  }
  assert.deepEqual(trianglesOf(n.geometry),trianglesOf(o.geometry),name+' oriented triangles')
}
assert.equal(geometryError,0,'Compression altered vertex positions')
assert.equal(attributeError,0,'Compression altered vertex attributes')
const frames=[];let maxTransformError=0
for(const checkpoint of metadata.checkpoints){
  mixer.setTime((checkpoint.frame-1)/24);gltf.scene.updateMatrixWorld(true)
  let error=0
  for(const [name,matrix] of Object.entries(checkpoint.nodes)){
    const o=named.get(name);assert.ok(o,name)
    for(let r=0;r<4;r++)for(let c=0;c<4;c++)error=Math.max(error,Math.abs(o.matrixWorld.elements[c*4+r]-matrix[r*4+c]))
  }
  maxTransformError=Math.max(maxTransformError,error);frames.push({frame:checkpoint.frame,error})
}
assert.ok(maxTransformError<.005,'Baked animation differs from Blender: '+maxTransformError)
const pulsePeaks=Object.entries(metadata.emissionSamples).filter(([n])=>n.startsWith('Orbital pulse')).map(([name,a])=>({name,peakFrame:a.indexOf(Math.max(...a))+1}))
assert.deepEqual(pulsePeaks.map(p=>p.peakFrame),[404,408,412,416,420])
assert.equal(metadata.controls.orbits.length,5)
assert.equal(metadata.controls.wings.length,2)
const report={status:'PASS',sourceSha256:metadata.sourceSha256,bytes:bytes.length,namedNodes:named.size,
  meshes,triangles,animation:{name:gltf.animations[0].name,duration:gltf.animations[0].duration,tracks:gltf.animations[0].tracks.length},
  geometryMaxPositionError:geometryError,geometryMaxAttributeError:attributeError,maxTransformError,frames,pulsePeaks,
  validation:{errors:validation.issues.numErrors,warnings:validation.issues.numWarnings,messages:validation.issues.messages}}
await writeFile(root+'qa/model-verification.json',JSON.stringify(report,null,2))
console.log(JSON.stringify(report,null,2))
