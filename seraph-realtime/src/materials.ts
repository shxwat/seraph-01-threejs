import { MeshStandardMaterial, Vector3, BufferAttribute, type BufferGeometry } from 'three'
import type { MaterialProfile } from './types'

export function prepareGeometry(source:BufferGeometry){
  const g=source.clone()
  for(const name of Object.keys(g.attributes))if(!['position','normal','uv'].includes(name))g.deleteAttribute(name)
  if(!g.attributes.normal)g.computeVertexNormals()
  if(!g.attributes.uv)g.setAttribute('uv',new BufferAttribute(new Float32Array(g.attributes.position.count*2),2))
  g.computeBoundingBox()
  const box=g.boundingBox!,size=box.getSize(new Vector3()),a=g.attributes.position
  const coords=new Float32Array(a.count*3)
  for(let i=0;i<a.count;i++){
    coords[i*3]=(a.getX(i)-box.min.x)/Math.max(size.x,1e-6)
    coords[i*3+1]=(a.getY(i)-box.min.y)/Math.max(size.y,1e-6)
    coords[i*3+2]=(a.getZ(i)-box.min.z)/Math.max(size.z,1e-6)
  }
  g.setAttribute('seraphCoord',new BufferAttribute(coords,3))
  return g
}

export function preserveMaterial(source:MeshStandardMaterial,profile?:MaterialProfile){
  const material=source.clone()
  material.envMapIntensity=.85
  if(profile?.surface==='brushed-alloy'){
    material.onBeforeCompile=shader=>{
      shader.vertexShader='attribute vec3 seraphCoord; varying vec3 vSeraphCoord;\n'+shader.vertexShader
      shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvSeraphCoord=seraphCoord;')
      shader.fragmentShader=`varying vec3 vSeraphCoord;
        float seraphHash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
        float seraphGrain(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
          return mix(mix(mix(seraphHash(i),seraphHash(i+vec3(1,0,0)),f.x),mix(seraphHash(i+vec3(0,1,0)),seraphHash(i+vec3(1,1,0)),f.x),f.y),
          mix(mix(seraphHash(i+vec3(0,0,1)),seraphHash(i+vec3(1,0,1)),f.x),mix(seraphHash(i+vec3(0,1,1)),seraphHash(i+vec3(1,1,1)),f.x),f.y),f.z);}
      `+shader.fragmentShader
      shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>',`#include <roughnessmap_fragment>
        vec3 grainCoords=vSeraphCoord*vec3(145.,145.,2610.);
        float grainWeight=1.-smoothstep(.5,3.,length(fwidth(grainCoords)));
        roughnessFactor=clamp(roughnessFactor*mix(1.,mix(.65,1.35,seraphGrain(grainCoords)),grainWeight),.04,1.);
      `)
    }
    material.customProgramCacheKey=()=> 'seraph-original-brushed-alloy-v1'
  }
  return material
}
