"""Original quiet electronic sound design for the recorded 38-second showcase.
No sampled music, third-party audio, microphone, or system audio is used.
"""
from pathlib import Path
import wave
import numpy as np

out=Path(__file__).resolve().parents[1]/'output/showcase'
out.mkdir(parents=True,exist_ok=True)
sr=48000
t=np.arange(sr*38,dtype=np.float64)/sr
tau=2*np.pi
fade=np.minimum(t/2,1)*np.minimum(np.maximum((38-t)/2,0),1)
# Warm low electronic drone and a slow suspended harmonic bed.
left=.045*np.sin(tau*55*t)+.022*np.sin(tau*82.4069*t+.12*np.sin(tau*.13*t))
right=.045*np.sin(tau*55*t+.025)+.022*np.sin(tau*82.4069*t+.12*np.sin(tau*.13*t)+.18)
for hz,phase in [(110,0),(164.8138,.7),(220,1.5),(329.6276,2.2)]:
    env=.5+.5*np.sin(tau*.045*t+phase)
    left+=.012*env*np.sin(tau*hz*t+.08*np.sin(tau*.1*t))
    right+=.012*env*np.sin(tau*hz*t+.08*np.sin(tau*.1*t)+.2)
# Reactor impact and two gentle mechanical transition sweeps.
for at,amp in [(9.4,.12),(14,.07),(26,.07),(34,.05)]:
    d=np.maximum(t-at,0)
    mask=(t>=at)
    impact=amp*np.exp(-d*3)*np.sin(tau*(48*d+18*(1-np.exp(-d*4))))*mask
    shimmer=.018*np.exp(-d*1.4)*np.sin(tau*(620*d+90*np.log1p(d)))*mask
    left+=impact+shimmer;right+=impact-shimmer*.65
for start,stop in [(13,21.5),(25,33.5)]:
    d=np.clip((t-start)/(stop-start),0,1)
    env=np.sin(np.pi*d)**2
    for hz in (176,264,352):
        phase=tau*(hz*t+30*d*d)
        left+=.011*env*np.sin(phase);right+=.011*env*np.sin(phase+.3)
audio=np.column_stack([left,right])*fade[:,None]
audio=np.tanh(audio*1.3)*.75
with wave.open(str(out/'showcase-sound.wav'),'wb') as f:
    f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
    f.writeframes((np.clip(audio,-1,1)*32767).astype('<i2').tobytes())
print(out/'showcase-sound.wav')
