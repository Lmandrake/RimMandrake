import math,struct,sys
M=(1<<64)-1
def mix(x):
    x&=M; x^=x>>12; x^=(x<<25)&M; x^=x>>27; return (x*0x9E3779B97F4A7C15)&M
def bits(f): return struct.unpack('<Q',struct.pack('<d',f))[0]
V=sys.argv[2]
def fp(seed,reps=20000):
    if V=='r19999': reps=19999
    if V=='r20001': reps=20001
    if V=='r10000': reps=10000
    d=[1.0+float(mix(seed+i)>>12)*1e-16 for i in range(64)]
    if V=='d1': d=[1.0]*64
    A=[1.0000001]*4; C=[0.9999999]*4; acc=[1.0]*4
    if V=='acc_hi0': acc=[1.0,1.0,0.0,0.0]
    if V=='ac_hi0': A=[1.0000001,1.0000001,0.0,0.0]; C=[0.9999999,0.9999999,0.0,0.0]
    if V=='acc_lo_dup': pass
    for r in range(reps):
        for i in range(0,64,4):
            for k in range(4):
                v=d[i+k]; a=A[k]; c=C[k]
                x=math.fma(acc[k],c,v) if V=='fma_order' else math.fma(acc[k],v,c)
                x=x/math.sqrt(x*x+a); acc[k]=x
                if V!='nostore': d[i+k]=math.fma(v,a,-(x*c))
    h=0
    for k in range(4): h=mix(h^bits(acc[k]))
    return '%016x'%h
print(V,fp(0x1234567*(int(sys.argv[1])+1)),flush=True)
