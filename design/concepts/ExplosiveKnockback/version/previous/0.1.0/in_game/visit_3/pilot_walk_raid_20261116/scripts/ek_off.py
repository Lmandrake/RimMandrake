import csv,sys,glob
fs=sorted(glob.glob(sys.argv[1]+'/RM_FrameProbe_*.csv'))
for i,p in enumerate(fs):
    t=0;R=[]
    for r in csv.DictReader(open(p)):
        ms=float(r['ms']);t+=ms/1000;R.append((t,ms,int(r['paused']),int(r['in_air'])))
    R=[x for x in R if 0.5<=x[0]<=10 and not x[2]]
    air=[x for x in R if x[3]>0]
    c=[x for x in R if 4.0<=x[0]<=5.2]; b=air[0][0] if air else max(c,key=lambda x:x[1])[0]
    st=[(round(x[0]-b,2),round(x[1]),x[3]) for x in R if x[1]>45]
    print('on ' if i%2==0 else 'off', st)
