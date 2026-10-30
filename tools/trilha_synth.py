import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile
SR=44100; BPM=110; beat=60/BPM; bar=4*beat
rng=np.random.default_rng(7)
def midi(n): return 440*2**((n-69)/12)
# I - vi - IV - V em Dó (voicings suaves)
prog=[[50,57,62,66,69],[45,57,61,64,69],[43,55,62,67,71],[45,57,61,64,69]]
bars_total=22  # ~41s
L=int(SR*bar*bars_total)+SR*4
out=np.zeros((L,2))
def env(n,a,d,s,r,length):
    t=np.arange(length)/SR; e=np.ones(length)*s
    ai=int(a*SR); di=int(d*SR); ri=int(r*SR)
    e[:ai]=np.linspace(0,1,ai); e[ai:ai+di]=np.linspace(1,s,di)
    e[-ri:]*=np.linspace(1,0,ri); return e
def add(sig,start,pan=0.0):
    i=int(start*SR); j=min(L,i+len(sig)); s=sig[:j-i]
    out[i:j,0]+=s*np.cos((pan+1)*np.pi/4); out[i:j,1]+=s*np.sin((pan+1)*np.pi/4)
def epiano(f,dur,vel):
    n=int(dur*SR); t=np.arange(n)/SR
    s=np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*2*f*t)*np.exp(-t*3)+0.08*np.sin(2*np.pi*3*f*t)*np.exp(-t*5)
    return s*np.exp(-t*2.6)*vel*env(n,0.006,0.1,1,0.25,n)
def pad(f,dur,vel):
    n=int(dur*SR); t=np.arange(n)/SR
    s=sum(np.sin(2*np.pi*f*(1+d)*t+rng.uniform(0,6)) for d in (-0.003,0,0.004))/3
    s+=0.3*np.sin(2*np.pi*f*2*t)
    return s*vel*env(n,1.2,0.5,0.8,1.5,n)
for b in range(bars_total):
    ch=prog[b%4]; t0=b*bar
    # pad
    for k,nn in enumerate(ch[1:]): add(pad(midi(nn),bar+1.5,0.025),t0,pan=(k-1.5)*0.3)
    # baixo
    add(pad(midi(ch[0]),bar+0.5,0.04),t0)
    # piano: acorde no tempo 1 e arpejo leve
    if b>=1:
        arp=[ch[2]+12,ch[3]+12,ch[4]+12,ch[2]+24,ch[4]+12,ch[3]+12,ch[2]+24,ch[3]+24]
        for k,nn in enumerate(arp):
            add(epiano(midi(nn),0.9,0.03*(0.85+0.3*rng.random())),t0+beat*k*0.5,pan=rng.uniform(-0.5,0.5))

def kick(vel):
    n=int(0.35*SR); t=np.arange(n)/SR
    f=50+90*np.exp(-t*30); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*9)*vel
def hat(vel):
    n=int(0.06*SR); t=np.arange(n)/SR
    x=rng.standard_normal(n); x=sosfilt(butter(2,7000,'high',fs=SR,output='sos'),x)
    return x*np.exp(-t*70)*vel
def snap(vel):
    n=int(0.18*SR); t=np.arange(n)/SR
    x=rng.standard_normal(n); x=sosfilt(butter(2,[1200,5000],'band',fs=SR,output='sos'),x)
    return (x*np.exp(-t*28)+0.3*np.sin(2*np.pi*190*t)*np.exp(-t*25))*vel
for b in range(1,bars_total):
    t0=b*bar
    for q in range(4):
        if q in (0,2): add(kick(0.22),t0+q*beat)
        if q in (1,3): add(snap(0.07),t0+q*beat,pan=0.05)
    for e in range(8):
        add(hat(0.035 if e%2 else 0.05),t0+e*beat/2,pan=0.25)

# reverb
ir_len=int(2.8*SR); tt=np.arange(ir_len)/SR
ir=rng.standard_normal((ir_len,2))*np.exp(-tt*2.2)[:,None]
sos=butter(2,4500,'low',fs=SR,output='sos'); ir=sosfilt(sos,ir,axis=0)
wet=np.stack([fftconvolve(out[:,c],ir[:,c])[:L] for c in range(2)],1)
mix=out*0.75+wet*0.06
mix=sosfilt(butter(2,7000,'low',fs=SR,output='sos'),mix,axis=0)
mix=mix[:int(SR*bar*bars_total)]
fade=int(3*SR); mix[-fade:]*=np.linspace(1,0,fade)[:,None]; mix[:int(0.5*SR)]*=np.linspace(0,1,int(0.5*SR))[:,None]
mix/=np.max(np.abs(mix))*1.12
wavfile.write('trilha6.wav',SR,(mix*32767).astype(np.int16))
print(len(mix)/SR)
