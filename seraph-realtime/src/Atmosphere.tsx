import { useMemo } from 'react'
import { AdditiveBlending, ShaderMaterial } from 'three'
export function Atmosphere(){
  const material=useMemo(()=>new ShaderMaterial({transparent:true,depthWrite:false,blending:AdditiveBlending,
    uniforms:{uIntensity:{value:1}},
    vertexShader:'varying vec2 vUv; void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader:`varying vec2 vUv; uniform float uIntensity;
      void main(){vec2 p=(vUv-.5)*2.;
        float blue=exp(-dot((p-vec2(-.25,.05))*vec2(2.0,1.1),(p-vec2(-.25,.05))*vec2(2.0,1.1))*3.);
        float gold=exp(-dot((p-vec2(.35,.05))*vec2(2.0,1.2),(p-vec2(.35,.05))*vec2(2.0,1.2))*4.);
        vec3 c=vec3(.018,.065,.12)*blue+vec3(.075,.042,.012)*gold;
        gl_FragColor=vec4(c,uIntensity*.48);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`}),[])
  return <mesh position={[0,1,-4]} material={material} renderOrder={-10}><planeGeometry args={[23,23]}/></mesh>
}
