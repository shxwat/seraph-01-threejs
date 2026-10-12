import { Suspense, use, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Environment, Lightformer, OrbitControls, PerformanceMonitor, useGLTF } from '@react-three/drei'
import { Bloom, EffectComposer, SSAO, ToneMapping } from '@react-three/postprocessing'
import { ToneMappingMode } from 'postprocessing'
import { ACESFilmicToneMapping, AnimationMixer, DirectionalLight, LoopOnce, MathUtils, Mesh, PerspectiveCamera, PointLight, Vector3 } from 'three'
import { MeshoptDecoder } from 'meshoptimizer'
import type { OrbitControls as Controls } from 'three-stdlib'
import type { Metadata } from './types'
import { prepareModel } from './batching'
import { commands, getState, patchState, useStore } from './store'
import { Atmosphere } from './Atmosphere'
import { ShowcaseCapture, showcaseEnabled, useCapture } from './Showcase'

const BASE=import.meta.env.BASE_URL
const metadataPromise:Promise<Metadata>=fetch(BASE+'models/seraph.metadata.json').then(r=>{if(!r.ok)throw new Error('Model metadata could not be loaded.');return r.json()})
const URL=BASE+'models/seraph.glb'
// Exported ring geometry lies in local XZ after Blender's Z-up conversion.
const up=new Vector3(0,1,0),localNormal=new Vector3(0,1,0),localX=new Vector3(1,0,0)
const playback={frame:240}
const blendAngle=(angle:number,weight:number)=>Math.atan2(Math.sin(angle),Math.cos(angle))*weight
const interpolate=(values:number[],frame:number)=>{const i=MathUtils.clamp(Math.floor(frame)-1,0,479),t=frame-Math.floor(frame);return MathUtils.lerp(values[i],values[Math.min(i+1,479)],t)}

function OriginalSeraph({controls}:{controls:React.RefObject<Controls|null>}){
  const gltf=useGLTF(URL,false,true,loader=>loader.setMeshoptDecoder(MeshoptDecoder))
  const metadata=use(metadataPromise)
  const model=useMemo(()=>prepareModel(gltf.scene,metadata),[gltf.scene,metadata])
  const mixer=useMemo(()=>{
    const m=new AnimationMixer(model.scene),a=m.clipAction(gltf.animations[0]);a.setLoop(LoopOnce,1);a.clampWhenFinished=true;a.play();return m
  },[model,gltf.animations])
  const {camera,gl,size}=useThree()
  const hit=useRef<Mesh>(null),reactorLight=useRef<PointLight>(null)
  const frame=useRef(metadata.heroFrame),clock=useRef(0),pulseAge=useRef(100),last=useRef({...commands}),stats=useRef(0)
  const transition=useRef({age:100,time:0,fromDeity:true})
  const root=useRef<HTMLDivElement|null>(null)
  const position=useMemo(()=>new Vector3(),[]),target=useMemo(()=>new Vector3(),[])
  const rings=useMemo(()=>metadata.controls.orbits.map(n=>model.named.get(n)!),[model,metadata])
  const wings=useMemo(()=>metadata.controls.wings.map(n=>model.named.get(n)!),[model,metadata])
  const gimbals=useMemo(()=>[...model.named].filter(([n])=>n.startsWith('Reactor containment gimbal')).map(([,o])=>o),[model])
  const body=model.named.get(metadata.controls.body)!,reactor=model.named.get(metadata.controls.reactor)!
  const resetCamera=()=>{
    const cam=camera as PerspectiveCamera
    if(controls.current){controls.current.enableDamping=false;controls.current.update()}
    cam.fov=35;cam.updateProjectionMatrix()
    const distance=Math.max(22,16/(2*Math.tan(MathUtils.degToRad(17.5))*cam.aspect)*1.13)
    cam.position.set(0,2.4,distance)
    controls.current?.target.set(0,.8,0);cam.lookAt(0,.8,0);controls.current?.update()
    if(controls.current)controls.current.enableDamping=true
  }
  useEffect(()=>{
    root.current=document.getElementById('experience') as HTMLDivElement
    mixer.setTime((metadata.heroFrame-1)/24);model.capturePose();model.update();resetCamera()
    patchState({ready:true})
    if(root.current){root.current.dataset.ready='true';root.current.dataset.meshes=String(model.meshCount);root.current.dataset.batches=String(model.batchCount)}
    return()=>{mixer.stopAllAction();mixer.uncacheRoot(model.scene);model.dispose()}
  },[model,mixer])
  useEffect(()=>{if(!getState().cinematic)resetCamera()},[size.width,size.height])
  useFrame((_,rawDelta)=>{
    const delta=Math.min(rawDelta,.1),state=getState()
    if(last.current.reset!==commands.reset){resetCamera();patchState({cinematic:false});last.current.reset=commands.reset}
    if(last.current.pulse!==commands.pulse){pulseAge.current=0;last.current.pulse=commands.pulse}
    if(last.current.sequence!==commands.sequence){frame.current=1;clock.current=0;patchState({mode:'sequence',cinematic:true,paused:false});last.current.sequence=commands.sequence}
    if(last.current.transform!==commands.transform){
      const isEye=state.mode==='eye'||state.mode==='transforming'
      transition.current={age:state.mode==='deity'||state.mode==='eye'?0:100,time:clock.current,fromDeity:state.mode==='deity'}
      if(state.mode==='sequence'){frame.current=metadata.heroFrame;resetCamera()}
      patchState({mode:isEye?'returning':'transforming',cinematic:false});last.current.transform=commands.transform
    }
    const now=getState()
    if(!now.paused){
      clock.current+=delta;pulseAge.current+=delta
      transition.current.age+=delta
      if(now.mode==='sequence')frame.current=1+((frame.current-1+delta*24)%479)
      else if(now.mode==='transforming'||now.mode==='returning'){
        const destination=now.mode==='transforming'?metadata.eyeFrame:metadata.heroFrame
        const direction=Math.sign(destination-frame.current)
        frame.current+=direction*Math.min(Math.abs(destination-frame.current),delta*24)
        if(Math.abs(frame.current-destination)<.001){frame.current=destination;clock.current=0;patchState({mode:destination===metadata.eyeFrame?'eye':'deity'})}
      }
    }
    model.restorePose()
    mixer.setTime((frame.current-1)/24)
    model.capturePose()
    playback.frame=frame.current
    // Secondary movement is applied to the original controls after the baked pose.
    // No model-level spin, new wings, or replacement geometry.
    const idle=now.mode==='deity'||now.mode==='eye'
    const weight=idle?1:1-MathUtils.smoothstep(transition.current.age,0,.45)
    const idleTime=idle?clock.current:transition.current.time
    if(weight>0){
      for(let i=0;i<rings.length;i++){
        rings[i].rotateOnAxis(localNormal,blendAngle(idleTime*(.013+i*.004),weight))
        rings[i].rotateOnAxis(localX,Math.sin(idleTime*.23+i)*.018*weight)
      }
      gimbals.forEach((o,i)=>o.rotateOnAxis(i%2?localX:localNormal,blendAngle(idleTime*(.13+i*.055),weight)))
      if(idle?now.mode==='deity':transition.current.fromDeity){
        body.position.y+=Math.sin(idleTime*.65)*.035*weight
        wings.forEach((o,i)=>o.rotateOnAxis(up,Math.sin(idleTime*.4)*.014*(i?1:-1)*weight))
      }
    }
    const burst=Math.exp(-pulseAge.current*3.1)*Math.sin(Math.min(pulseAge.current,1)*Math.PI)
    for(const [name,material] of model.materials){
      const values=metadata.emissionSamples[name]
      if(!values)continue
      let intensity=interpolate(values,frame.current)
      if(now.mode==='deity'||now.mode==='eye')intensity*=1+Math.sin(clock.current*1.6)*.055
      if(name.startsWith('Orbital pulse')){
        const index=Number(name.at(-1))-1,age=pulseAge.current-index*.065
        if(age>=0&&age<1.2)intensity+=Math.exp(-age*5)*20
      }else intensity*=1+burst*5
      material.emissiveIntensity=intensity*.32
    }
    model.update()
    reactor.getWorldPosition(position)
    if(hit.current){hit.current.position.copy(position);hit.current.scale.setScalar(now.mode==='eye'?1.4:1)}
    if(reactorLight.current){reactorLight.current.position.copy(position);reactorLight.current.intensity=(8+burst*35)*(now.mode==='sequence'?interpolate(metadata.lightSamples,frame.current):1)}
    if(now.cinematic){
      const i=MathUtils.clamp(Math.floor(frame.current)-1,0,479),next=Math.min(i+1,479),t=frame.current-Math.floor(frame.current)
      const a=metadata.cameraSamples[i],b=metadata.cameraSamples[next]
      position.fromArray(a.position).lerp(target.fromArray(b.position),t)
      const cam=camera as PerspectiveCamera
      // Preserve the recorded path; widen framing only for narrow viewports.
      const narrow=Math.max(1,(16/9)/cam.aspect)
      target.fromArray(a.target).lerp(new Vector3().fromArray(b.target),t)
      if(narrow>1)position.sub(target).multiplyScalar(Math.min(narrow,2.6)).add(target)
      cam.position.copy(position);cam.fov=MathUtils.lerp(a.fov,b.fov,t);cam.lookAt(target);cam.updateProjectionMatrix()
      controls.current?.target.copy(target)
    }
    stats.current+=delta
    if(stats.current>.5&&root.current){
      stats.current=0;root.current.dataset.frame=frame.current.toFixed(1);root.current.dataset.mode=getState().mode
      root.current.dataset.calls=String(gl.info.render.calls);root.current.dataset.triangles=String(gl.info.render.triangles)
      root.current.dataset.fps=String(Math.round(1/rawDelta));root.current.dataset.cameraDistance=camera.position.length().toFixed(2)
      root.current.dataset.pulse=String(commands.pulse);root.current.dataset.cameraX=camera.position.x.toFixed(2)
    }
    gl.info.reset()
  },-1)
  return <>
    <primitive object={model.scene}/><primitive object={model.batches}/>
    <pointLight ref={reactorLight} color="#ffd5a1" distance={8} decay={2}/>
    <mesh ref={hit} onClick={e=>{if(e.delta<6){e.stopPropagation();commands.pulse++}}}
      onPointerOver={()=>{gl.domElement.style.cursor='pointer'}} onPointerOut={()=>{gl.domElement.style.cursor='grab'}}>
      <sphereGeometry args={[1.05,16,12]}/><meshBasicMaterial transparent opacity={0} depthWrite={false} colorWrite={false}/>
    </mesh>
  </>
}

function Studio({low}:{low:boolean}){
  const metadata=use(metadataPromise),scene=useThree(s=>s.scene)
  const key=useRef<DirectionalLight>(null),rim=useRef<DirectionalLight>(null),fill=useRef<DirectionalLight>(null)
  useFrame(()=>{
    const power=getState().mode==='sequence'?interpolate(metadata.lightSamples,playback.frame):1
    scene.environmentIntensity=power
    if(key.current)key.current.intensity=2*power
    if(rim.current)rim.current.intensity=2.7*power
    if(fill.current)fill.current.intensity=.65*power
  })
  return <>
    <Environment frames={1} resolution={low?128:256} background={false}>
      <Lightformer form="rect" intensity={3.4} color="#ffdeb2" position={[-5,6,8]} scale={[7,11,1]} target={[0,0,0]}/>
      <Lightformer form="rect" intensity={2.6} color="#e4efff" position={[4,2,8]} scale={[5,9,1]} target={[0,0,0]}/>
      <Lightformer form="rect" intensity={3.8} color="#5b9ee8" position={[-6,2,-3]} scale={[3,12,1]} target={[0,0,0]}/>
      <Lightformer form="rect" intensity={3.3} color="#dba656" position={[6,3,-3]} scale={[3,10,1]} target={[0,0,0]}/>
      <Lightformer form="rect" intensity={2} color="#fff4db" position={[0,10,0]} scale={[9,5,1]} target={[0,0,0]}/>
    </Environment>
    <directionalLight ref={key} position={[-5,8,8]} color="#ffe0b7" intensity={2.0}/>
    <directionalLight ref={rim} position={[6,2,-4]} color="#70adff" intensity={2.7}/>
    <directionalLight ref={fill} position={[-5,-2,5]} color="#b9d9ff" intensity={.65}/>
  </>
}

function Stage({low,onDecline}:{low:boolean;onDecline:()=>void}){
  const controls=useRef<Controls|null>(null),state=useStore()
  const capture=useCapture()
  return <>
    <color attach="background" args={['#020304']}/>
    <Studio low={low}/><Atmosphere/>
    <OriginalSeraph controls={controls}/>
    <OrbitControls ref={controls} makeDefault enabled={!state.cinematic&&!capture.running} enablePan={false} enableDamping dampingFactor={.07}
      rotateSpeed={.5} zoomSpeed={.65} minDistance={12} maxDistance={85} minPolarAngle={.18} maxPolarAngle={Math.PI-.18}/>
    <PerformanceMonitor bounds={()=>[28,55]} iterations={5} onDecline={onDecline}/>
    <EffectComposer multisampling={low?0:2} enableNormalPass={!low}>
      {!low&&<SSAO samples={8} rings={3} radius={.13} intensity={.8} luminanceInfluence={.65} resolutionScale={.5}/>}
      <Bloom mipmapBlur intensity={.38} luminanceThreshold={1.35} luminanceSmoothing={.25} radius={.55}/>
      <ToneMapping mode={ToneMappingMode.ACES_FILMIC}/>
    </EffectComposer>
    {showcaseEnabled&&<ShowcaseCapture/>}
  </>
}

export function Experience(){
  const state=useStore(),[adaptiveLow,setAdaptiveLow]=useState(false)
  const low=state.quality==='low'||(state.quality==='auto'&&adaptiveLow)
  return <Canvas camera={{position:[0,2.4,30],fov:35,near:.1,far:160}} dpr={low?[.75,1]:[1,1.5]}
    gl={{antialias:true,powerPreference:'high-performance',toneMapping:ACESFilmicToneMapping,toneMappingExposure:.9}}
    onCreated={({gl})=>{gl.info.autoReset=false;gl.domElement.setAttribute('aria-label','Interactive SERAPH-01 mechanical god');gl.domElement.style.cursor='grab'}}>
    <Suspense fallback={null}><Stage low={low} onDecline={()=>setAdaptiveLow(true)}/></Suspense>
  </Canvas>
}
