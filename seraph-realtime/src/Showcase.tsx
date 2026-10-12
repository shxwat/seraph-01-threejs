import { useEffect, useSyncExternalStore } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { MathUtils, PerspectiveCamera } from 'three'
import { command, getState, patchState } from './store'

// Optional recording route. The normal experience contains no recording titles.
export const showcaseEnabled=new URLSearchParams(location.search).has('showcase')
const DURATION=38
type CaptureState={running:boolean;seconds:number;url:string;error:string}
let state:CaptureState={running:false,seconds:0,url:'',error:''}
const listeners=new Set<()=>void>()
function set(patch:Partial<CaptureState>){state={...state,...patch};listeners.forEach(f=>f())}
export function useCapture(){return useSyncExternalStore(f=>{listeners.add(f);return()=>listeners.delete(f)},()=>state)}
let recorder:MediaRecorder|null=null,output:HTMLCanvasElement|null=null,context:CanvasRenderingContext2D|null=null
let start=0,triggered=new Set<string>(),lastStatus=0
const ease=(t:number)=>MathUtils.smoothstep(MathUtils.clamp(t,0,1),0,1)
const mix=(a:number,b:number,t:number)=>MathUtils.lerp(a,b,ease(t))

export function startShowcase(){
  if(state.running||!getState().ready)return
  if(getState().mode!=='deity'){set({error:'Return to the deity pose (T) before recording.'});return}
  try{
    if(state.url)URL.revokeObjectURL(state.url)
    output=document.createElement('canvas');output.width=1920;output.height=1080
    context=output.getContext('2d',{alpha:false})!
    const stream=output.captureStream(60)
    const mimeType=['video/webm;codecs=vp9','video/webm;codecs=vp8','video/mp4'].find(m=>MediaRecorder.isTypeSupported(m))
    if(!mimeType)throw new Error('No browser video encoder is available.')
    recorder=new MediaRecorder(stream,{mimeType,videoBitsPerSecond:24_000_000})
    const chunks:BlobPart[]=[]
    recorder.ondataavailable=event=>{if(event.data.size)chunks.push(event.data)}
    recorder.onerror=()=>{set({running:false,error:'Browser recording failed.'});stream.getTracks().forEach(t=>t.stop())}
    recorder.onstop=()=>{
      const blob=new Blob(chunks,{type:mimeType})
      set({running:false,url:URL.createObjectURL(blob),seconds:DURATION})
      stream.getTracks().forEach(t=>t.stop())
      recorder=null
    }
    patchState({paused:false,cinematic:false,quality:'high',help:false})
    command('reset');triggered=new Set();lastStatus=0;start=performance.now()
    context.fillStyle='#020304';context.fillRect(0,0,1920,1080)
    recorder.start(1000);set({running:true,seconds:0,url:'',error:''})
  }catch(error){set({running:false,error:String(error)})}
}

function shot(t:number){
  // Continuous camera movement through the actual Three.js scene, with the
  // normal imported AnimationMixer and normal reactor interaction commands.
  if(t<3)return {azimuth:mix(-.16,0,t/3),distance:mix(25,23,t/3),y:2.3,targetY:.8,label:'ORIGINAL MODEL · LIVE THREE.JS'}
  if(t<8)return {azimuth:mix(0,.43,(t-3)/5),distance:mix(23,21.5,(t-3)/5),y:mix(2.3,3,(t-3)/5),targetY:.8,label:'ORBIT · LIVE CAMERA'}
  if(t<11)return {azimuth:mix(.43,.18,(t-8)/3),distance:mix(21.5,15,(t-8)/3),y:mix(3,2.6,(t-8)/3),targetY:mix(.8,1.5,(t-8)/3),label:'REACTOR · EMISSIVE PULSE'}
  if(t<14)return {azimuth:mix(.18,-.07,(t-11)/3),distance:mix(15,23,(t-11)/3),y:mix(2.6,2.2,(t-11)/3),targetY:mix(1.5,.8,(t-11)/3),label:'MECHANICAL DETAIL · ORIGINAL GLB'}
  if(t<22)return {azimuth:mix(-.07,.08,(t-14)/8),distance:23,y:2.2,targetY:.8,label:'TRANSFORMATION · IMPORTED ANIMATION'}
  if(t<26)return {azimuth:mix(.08,-.31,(t-22)/4),distance:mix(23,22,(t-22)/4),y:2.2,targetY:.8,label:'CELESTIAL EYE · INDEPENDENT GYROSCOPES'}
  if(t<34)return {azimuth:mix(-.31,0,(t-26)/8),distance:mix(22,23,(t-26)/8),y:2.2,targetY:.8,label:'RETURN · ORIGINAL ANIMATION REVERSED'}
  return {azimuth:mix(0,-.13,(t-34)/4),distance:mix(23,24,(t-34)/4),y:2.2,targetY:.8,label:'SERAPH-01 · REAL-TIME WEBGL'}
}

export function ShowcaseCapture(){
  const {camera,gl}=useThree()
  useEffect(()=>()=>{if(recorder?.state==='recording')recorder.stop()},[])
  useFrame(()=>{
    if(!state.running)return
    const t=(performance.now()-start)/1000,s=shot(t)
    for(const [name,time] of [['pulse',9.4],['transform',14],['return',26]] as const){
      if(t>=time&&!triggered.has(name)){command(name==='pulse'?'pulse':'transform');triggered.add(name)}
    }
    const cam=camera as PerspectiveCamera
    cam.fov=35;cam.position.set(Math.sin(s.azimuth)*s.distance,s.y,Math.cos(s.azimuth)*s.distance)
    cam.lookAt(0,s.targetY,0);cam.updateProjectionMatrix()
    if(t-lastStatus>.25){set({seconds:t});lastStatus=t}
  },0)
  // The composer renders at priority 1. Capture its actual finished framebuffer.
  useFrame(()=>{
    if(!state.running||!context||!output)return
    const t=(performance.now()-start)/1000,ctx=context,s=shot(t)
    ctx.drawImage(gl.domElement,0,0,1920,1080)
    const vignette=ctx.createLinearGradient(0,0,0,1080)
    vignette.addColorStop(0,'#000000a0');vignette.addColorStop(.16,'#00000000');vignette.addColorStop(.77,'#00000000');vignette.addColorStop(1,'#000000c0')
    ctx.fillStyle=vignette;ctx.fillRect(0,0,1920,1080)
    ctx.save();ctx.shadowColor='#000';ctx.shadowBlur=12
    ctx.fillStyle='#ddc99d';ctx.font='500 19px Arial';ctx.letterSpacing='5px';ctx.fillText('SERAPH—01',60,60)
    ctx.font='12px Arial';ctx.letterSpacing='2px';ctx.fillStyle='#b6b4ae';ctx.fillText('THE MECHANICAL GOD',60,86)
    ctx.fillStyle='#9de8cd';ctx.beginPath();ctx.arc(65,1000,4,0,Math.PI*2);ctx.fill()
    ctx.font='500 16px Arial';ctx.letterSpacing='2px';ctx.fillStyle='#e5e5df';ctx.fillText('THREE.JS / REAL-TIME WEBGL',82,1006)
    ctx.font='12px Arial';ctx.letterSpacing='1px';ctx.fillStyle='#aaa9a3';ctx.fillText('REACT · R3F · TYPESCRIPT · ORIGINAL BLENDER GLB',60,1033)
    ctx.textAlign='right';ctx.font='12px Arial';ctx.letterSpacing='2px';ctx.fillStyle='#d7c7a6';ctx.fillText(s.label,1860,1006)
    ctx.fillStyle='#84847d';ctx.font='11px monospace';ctx.letterSpacing='1px';ctx.fillText('LIVE GPU CAPTURE / 1920 × 1080',1860,1033)
    ctx.restore()
    ctx.fillStyle='#dfc08788';ctx.fillRect(60,1052,1800*Math.min(t/DURATION,1),1)
    if(t>=DURATION&&recorder?.state==='recording')recorder.stop()
  },2)
  return null
}

export function ShowcaseControls(){
  const capture=useCapture(),ready=getState().ready
  return <aside className="capture-controls" aria-label="Showcase recording">
    <button disabled={!ready||capture.running} onClick={startShowcase}>{capture.running?`Recording ${Math.floor(capture.seconds)} / ${DURATION}s`:'Record 1080p showcase'}</button>
    {capture.url&&<a href={capture.url} download="seraph-01-threejs-live.webm">Download recording</a>}
    {capture.error&&<span role="alert">{capture.error}</span>}
  </aside>
}
