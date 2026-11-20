import math,struct,sys,random
M=(1<<64)-1
def mix(x):
    x&=M; x^=x>>12; x^=(x<<25)&M; x^=x>>27; return (x*0x9E3779B97F4A7C15)&M
def bits(f): return struct.unpack('<Q',struct.pack('<d',f))[0]
def frombits(b): return struct.unpack('<d',struct.pack('<Q',b))[0]
def fp(seed,flip=None,reps=20000):
    d=[1.0+float(mix(seed+i)>>12)*1e-16 for i in range(64)]
    a=1.0000001; c=0.9999999; acc=[1.0]*4
    for r in range(reps):
        for i in range(0,64,4):
            for k in range(4):
                if flip and flip[0]==r and flip[1]==i and flip[2]==k:
                    if flip[3]=='acc': acc[k]=frombits(bits(acc[k])^(1<<flip[4]))
                    else: d[i+k]=frombits(bits(d[i+k])^(1<<flip[4]))
                v=d[i+k]; x=math.fma(acc[k],v,c); x=x/math.sqrt(x*x+a); acc[k]=x; d[i+k]=math.fma(v,a,-(x*c))
    h=0
    for k in range(4): h=mix(h^bits(acc[k]))
    return '%016x'%h
random.seed(int(sys.argv[2]))
seed=0x1234567*(int(sys.argv[1])+1)
for n in range(int(sys.argv[3])):
    f=(random.randrange(20000),random.randrange(0,64,4),random.randrange(4),random.choice(['acc','d']),random.randrange(0,52))
    print(f,fp(seed,f),flush=True)
