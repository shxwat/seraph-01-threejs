import { Component, Suspense, useEffect, type ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import { useProgress } from '@react-three/drei'
import { Experience } from './Experience'
import { command, cycleQuality, getState, patchState, togglePause, useStore } from './store'
import './style.css'
import { ShowcaseControls, showcaseEnabled } from './Showcase'

class SceneBoundary extends Component<{children:ReactNode},{error:string}> {
  state={error:''}
  static getDerivedStateFromError(error:Error){return {error:error.message}}
  render(){return this.state.error?<div className="status" role="alert"><p>The 3D scene could not initialize.</p><small>{this.state.error}</small><button onClick={()=>location.reload()}>Reload</button></div>:this.props.children}
}
function Loading(){
  const {progress}=useProgress(),{ready}=useStore()
  return ready?null:<div className="status" aria-live="polite"><span className="loading-ring"/><p>Loading SERAPH-01</p><small>{Math.round(progress)}%</small></div>
}
function App(){
  const state=useStore()
  useEffect(()=>{
    const keys=(event:KeyboardEvent)=>{
      if(event.repeat||event.altKey||event.ctrlKey||event.metaKey)return
      if((event.target as HTMLElement).matches('input,textarea,select,[contenteditable=true]'))return
      const key=event.code
      if(key==='Space'){event.preventDefault();if(getState().ready)togglePause()}
      if(!getState().ready)return
      if(key==='KeyT')command('transform')
      if(key==='KeyR')command('reset')
      if(key==='KeyC')command('sequence')
      if(key==='KeyQ')cycleQuality()
      if(key==='KeyH')patchState({help:!getState().help})
      if(key==='Escape')patchState({help:false})
    }
    window.addEventListener('keydown',keys)
    return()=>window.removeEventListener('keydown',keys)
  },[])
  return <main id="experience" data-ready={state.ready} data-mode={state.mode} data-paused={state.paused} data-quality={state.quality}>
    <SceneBoundary><Suspense fallback={null}><Experience/></Suspense><Loading/></SceneBoundary>
    <div className="controls" aria-label="Scene controls">
      {state.help&&<p className="help">Drag to orbit · Scroll to zoom · Click the reactor for energy<br/>Space: pause · T: transform · R: reset · C: cinematic · Q: quality</p>}
      <div className="buttons">
        <button disabled={!state.ready} onClick={togglePause} aria-label={state.paused?'Resume animation':'Pause animation'} title="Pause / resume · Space">{state.paused?'▷':'Ⅱ'}</button>
        <button disabled={!state.ready} onClick={()=>command('transform')} aria-label={state.mode==='eye'?'Return to deity':'Transform to eye'} title="Transform · T">◇</button>
        <button disabled={!state.ready} onClick={()=>command('sequence')} aria-label="Replay cinematic" title="Original Blender sequence · C">▶</button>
        <button disabled={!state.ready} onClick={()=>command('reset')} aria-label="Reset camera" title="Reset camera · R">↺</button>
        <button disabled={!state.ready} onClick={cycleQuality} aria-label={'Quality: '+state.quality} title={'Quality: '+state.quality+' · Q'} className="quality">{state.quality==='auto'?'AUTO':state.quality.toUpperCase()}</button>
        <button onClick={()=>patchState({help:!state.help})} aria-label="Show controls" aria-expanded={state.help} title="Controls · H">?</button>
      </div>
    </div>
    {showcaseEnabled&&<ShowcaseControls/>}
  </main>
}
createRoot(document.getElementById('root')!).render(<App/>)
