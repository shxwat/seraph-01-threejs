// Exercise the actual viewer's batching and pose restoration without a GPU.
import assert from 'node:assert/strict'
import { readFile,writeFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { AnimationMixer,LoopOnce,Vector3 } from 'three'
import { MeshoptDecoder } from 'meshoptimizer'
const server=await createServer({server:{middlewareMode:true},appType:'custom'})
try{
  const {prepareModel}=await server.ssrLoadModule('/src/batching.ts')
  const bytes=await readFile('public/models/seraph.glb')
  const metadata=JSON.parse(await readFile('public/models/seraph.metadata.json','utf8'))
  const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'')
  const model=prepareModel(gltf.scene,metadata),mixer=new AnimationMixer(model.scene)
  const action=mixer.clipAction(gltf.animations[0]);action.setLoop(LoopOnce,1);action.clampWhenFinished=true;action.play()
  mixer.setTime((240-1)/24);model.capturePose()
  const body=model.named.get(metadata.controls.body),wing=model.named.get(metadata.controls.wings[0])
  const bodyStart=body.position.clone(),wingStart=wing.quaternion.clone()
  let maxFloat=0,maxWingAngle=0
  for(let i=0;i<2000;i++){
    model.restorePose();mixer.setTime((240-1)/24);model.capturePose()
    body.position.y+=Math.sin(i*.016*.65)*.035
    wing.rotateOnAxis(new Vector3(0,1,0),Math.sin(i*.016*.4)*.014)
    model.update()
    maxFloat=Math.max(maxFloat,body.position.distanceTo(bodyStart))
    maxWingAngle=Math.max(maxWingAngle,wing.quaternion.angleTo(wingStart))
  }
  assert.ok(maxFloat<=.035001,'Floating drift accumulated')
  assert.ok(maxWingAngle<=.014001,'Wing motion accumulated')
  // Evaluate forward and reverse playback on the exact cloned hierarchy used for rendering.
  let maxTransformError=0
  for(const checkpoint of [...metadata.checkpoints.slice(0,-1),...metadata.checkpoints.slice(0,-1).reverse()]){
    model.restorePose();mixer.setTime((checkpoint.frame-1)/24);model.capturePose();model.update()
    for(const [name,matrix] of Object.entries(checkpoint.nodes)){
      const o=model.named.get(name)
      for(let r=0;r<4;r++)for(let c=0;c<4;c++)maxTransformError=Math.max(maxTransformError,Math.abs(o.matrixWorld.elements[c*4+r]-matrix[r*4+c]))
    }
  }
  assert.ok(maxTransformError<.005,'Viewer hierarchy diverged from Blender')
  assert.equal(model.meshCount,2811);assert.equal(model.batchCount,15)
  const report={status:'PASS',idleFrames:2000,maxFloat,maxWingAngle,maxTransformError,meshes:model.meshCount,batches:model.batchCount}
  await writeFile('qa/runtime-verification.json',JSON.stringify(report,null,2));console.log(report)
  model.dispose()
}finally{await server.close()}
