export type Mode = 'deity' | 'eye' | 'transforming' | 'returning' | 'sequence'
export type Quality = 'auto' | 'high' | 'low'
export interface MaterialProfile { name:string; color:number[]; metalness:number; roughness:number; emissive:number[]; emissiveStrength:number; surface?:string }
export interface CameraSample { position:number[]; quaternion:number[]; target:number[]; fov:number }
export interface Metadata {
  sourceSha256:string; fps:number; frameStart:number; frameEnd:number; heroFrame:number; eyeFrame:number; duration:number;
  materials:Record<string,MaterialProfile>; emissionSamples:Record<string,number[]>;
  cameraSamples:CameraSample[]; lightSamples:number[];
  controls:{master:string;body:string;orbits:string[];wings:string[];reactor:string;eye:string}
}
