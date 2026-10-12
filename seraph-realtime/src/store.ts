import { useSyncExternalStore } from 'react'
import type { Mode, Quality } from './types'
type State={ready:boolean;paused:boolean;mode:Mode;cinematic:boolean;quality:Quality;help:boolean}
let state:State={ready:false,paused:false,mode:'deity',cinematic:false,quality:'auto',help:false}
const listeners=new Set<()=>void>()
export const commands={transform:0,reset:0,pulse:0,sequence:0}
export const getState=()=>state
export function patchState(patch:Partial<State>){state={...state,...patch};listeners.forEach(f=>f())}
export function command(name:keyof typeof commands){commands[name]++;listeners.forEach(f=>f())}
export function useStore(){return useSyncExternalStore(f=>{listeners.add(f);return()=>listeners.delete(f)},getState)}
export const togglePause=()=>patchState({paused:!state.paused})
export function cycleQuality(){patchState({quality:state.quality==='auto'?'high':state.quality==='high'?'low':'auto'})}
