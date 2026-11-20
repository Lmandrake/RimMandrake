import math,struct,sys
M=(1<<64)-1
def mix(x):
    x&=M; x^=x>>12; x^=(x<<25)&M; x^=x>>27; return (x*0x9E3779B97F4A7C15)&M
def bits(f): return struct.unpack('<Q',struct.pack('<d',f))[0]
def fp(seed,v1,v2,reps=20000):
    d=[1.0+float(mix(seed+i)>>12)*1e-16 for i in range(64)]
    a=1.0000001; c=0.9999999; acc=[1.0]*4
    for r in range(reps):
        for i in range(0,64,4):
            for k in range(4):
                v=d[i+k]
                x=math.fma(acc[k],v,c) if v1 else acc[k]*v+c
                x=x/math.sqrt(x*x+a); acc[k]=x
                d[i+k]=math.fma(v,a,-(x*c)) if v2 else v*a-(x*c)
    h=0
    for k in range(4): h=mix(h^bits(acc[k]))
    return '%016x'%h
seed=0x1234567*(int(sys.argv[1])+1)
for v1,v2 in ((0,1),(1,0),(0,0)): print(sys.argv[1],'fma1' if v1 else 'unfused1','fms' if v2 else 'unfused2',fp(seed,v1,v2),flush=True)
