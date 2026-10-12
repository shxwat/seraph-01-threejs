import { BatchedMesh, Group, Mesh, MeshStandardMaterial, type Object3D, type BufferGeometry } from 'three'
import { prepareGeometry, preserveMaterial } from './materials'
import type { Metadata } from './types'

export function prepareModel(original:Group,metadata:Metadata){
  const scene=original.clone(true)
  const named=new Map<string,Object3D>(),groups=new Map<string,Mesh[]>()
  scene.traverse(o=>{
    if(o.userData.originalName)named.set(o.userData.originalName,o)
    if(!(o instanceof Mesh))return
    const material=o.material as MeshStandardMaterial
    if(Array.isArray(material))throw new Error('Unexpected multi-material primitive: '+o.name)
    const key=material.uuid
    if(!groups.has(key))groups.set(key,[])
    groups.get(key)!.push(o)
  })
  const batches=new Group();batches.name='SERAPH · render batches (source hierarchy retained)'
  const rest:{object:Object3D;position:Object3D['position'];quaternion:Object3D['quaternion'];scale:Object3D['scale']}[]=[]
  scene.traverse(object=>rest.push({object,position:object.position.clone(),quaternion:object.quaternion.clone(),scale:object.scale.clone()}))
  function restorePose(){for(const p of rest){p.object.position.copy(p.position);p.object.quaternion.copy(p.quaternion);p.object.scale.copy(p.scale)}}
  function capturePose(){for(const p of rest){p.position.copy(p.object.position);p.quaternion.copy(p.object.quaternion);p.scale.copy(p.object.scale)}}
  const entries:{source:Mesh;batch:BatchedMesh;id:number;visible:boolean}[]=[]
  const materials=new Map<string,MeshStandardMaterial>(),geometries=new Map<string,BufferGeometry>()
  for(const meshes of groups.values()){
    const source=meshes[0].material as MeshStandardMaterial
    const material=preserveMaterial(source,metadata.materials[source.name])
    materials.set(source.name,material)
    const unique=new Map<string,BufferGeometry>()
    for(const mesh of meshes){
      if(!geometries.has(mesh.geometry.uuid))geometries.set(mesh.geometry.uuid,prepareGeometry(mesh.geometry))
      unique.set(mesh.geometry.uuid,geometries.get(mesh.geometry.uuid)!)
    }
    const vertices=[...unique.values()].reduce((s,g)=>s+g.attributes.position.count,0)
    const indices=[...unique.values()].reduce((s,g)=>s+(g.index?.count??g.attributes.position.count),0)
    const batch=new BatchedMesh(meshes.length,vertices,indices,material)
    batch.name='Draw batch · '+source.name;batch.frustumCulled=false
    batch.perObjectFrustumCulled=true;batch.sortObjects=false
    const geometryIds=new Map<string,number>()
    for(const [uuid,g] of unique)geometryIds.set(uuid,batch.addGeometry(g))
    for(const mesh of meshes){
      const id=batch.addInstance(geometryIds.get(mesh.geometry.uuid)!)
      mesh.visible=false // Keep the node in the original hierarchy; render its exact world matrix in the batch.
      entries.push({source:mesh,batch,id,visible:true})
    }
    batches.add(batch)
  }
  function update(){
    scene.updateMatrixWorld(true)
    for(const e of entries){
      const m=e.source.matrixWorld.elements
      const scale=Math.max(Math.hypot(m[0],m[1],m[2]),Math.hypot(m[4],m[5],m[6]),Math.hypot(m[8],m[9],m[10]))
      const visible=scale>.003
      if(visible!==e.visible){e.batch.setVisibleAt(e.id,visible);e.visible=visible}
      if(visible)e.batch.setMatrixAt(e.id,e.source.matrixWorld)
    }
  }
  function dispose(){batches.children.forEach(b=>(b as BatchedMesh).dispose());materials.forEach(m=>m.dispose());geometries.forEach(g=>g.dispose())}
  return {scene,batches,named,materials,restorePose,capturePose,update,dispose,meshCount:entries.length,batchCount:groups.size}
}
