import ctypes,math,struct,sys
libm=ctypes.CDLL('libm.so.6')
M=(1<<64)-1
def mix(x):
    x&=M; x^=x>>12; x^=(x<<25)&M; x^=x>>27; return (x*0x9E3779B97F4A7C15)&M
def bits(f): return struct.unpack('<Q',struct.pack('<d',f))[0]
def fp(seed,reps=20000):
    d=[1.0+float(mix(seed+i)>>12)*1e-16 for i in range(64)]
    a=1.0000001; c=0.9999999; acc=[1.0]*4
    fma=math.fma; sq=math.sqrt
    for r in range(reps):
        for i in range(0,64,4):
            for k in range(4):
                v=d[i+k]; x=fma(acc[k],v,c); x=x/sq(x*x+a); acc[k]=x; d[i+k]=fma(v,a,-(x*c))
    h=0
    for k in range(4): h=mix(h^bits(acc[k]))
    return '%016x'%h
modes={'nearest':0x000,'down':0x400,'up':0x800,'zero':0xc00}
seed=0x1234567*(int(sys.argv[1])+1)
for name in sys.argv[2:]:
    libm.fesetround(modes[name]); print(sys.argv[1],name,fp(seed),flush=True)
libm.fesetround(0)
