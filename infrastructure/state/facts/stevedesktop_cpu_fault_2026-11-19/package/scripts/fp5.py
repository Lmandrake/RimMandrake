import math,struct,sys,itertools
M=(1<<64)-1
def mix(x):
    x&=M; x^=x>>12; x^=(x<<25)&M; x^=x>>27; return (x*0x9E3779B97F4A7C15)&M
def bits(f): return struct.unpack('<Q',struct.pack('<d',f))[0]
def lanes(seed,reps=20000):
    d=[1.0+float(mix(seed+i)>>12)*1e-16 for i in range(64)]
    a=1.0000001; c=0.9999999; acc=[1.0]*4
    for r in range(reps):
        for i in range(0,64,4):
            for k in range(4):
                v=d[i+k]; x=math.fma(acc[k],v,c); x=x/math.sqrt(x*x+a); acc[k]=x; d[i+k]=math.fma(v,a,-(x*c))
    return [bits(x) for x in acc]
def h(L):
    r=0
    for b in L: r=mix(r^b)
    return '%016x'%r
seed=0x1234567*(int(sys.argv[1])+1)
L=lanes(seed); print('canon',h(L))
cands={'NaN_ind':0xFFF8000000000000,'NaN_pos':0x7FF8000000000000,'zero':0,'one':bits(1.0),'neg1':bits(-1.0)}
for name,val in cands.items():
    for mask in itertools.product([0,1],repeat=4):
        if not any(mask): continue
        LL=[val if m else L[k] for k,m in enumerate(mask)]
        print(name,mask,h(LL))
