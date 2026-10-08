import sys, os, re, glob
root=os.getcwd()
U=os.path.join(root,"src","RimMandrake","Utils")
for p in (U, os.path.join(U,"modcheck")): sys.path.insert(0,p)
from rimdrive import Session
def classes(mod):
    out=[]
    for f in glob.glob(os.path.join(root,"src","RimMandrake",mod,"Source","**","*.cs"),recursive=True):
        s=open(f,encoding="utf-8-sig").read()
        ns=re.search(r"namespace\s+([\w.]+)",s)
        for m in re.finditer(r"class\s+(\w+)\s*:\s*ModSettings",s):
            i=s.index("{",m.end()); d=0; j=i
            while j<len(s):
                if s[j]=="{": d+=1
                elif s[j]=="}":
                    d-=1
                    if d==0: break
                j+=1
            body=s[i:j]
            fields={}
            for t,n,v in re.findall(r"public static (bool|float|int|double) (\w+)\s*=\s*([^;]+);",body):
                v=v.strip()
                try:
                    if t=="bool": fields[n]=(v=="true")
                    elif t=="int": fields[n]=int(v)
                    else: fields[n]=float(v.rstrip("fFdD"))
                except ValueError: pass  # expression default
            out.append(((ns.group(1) if ns else "")+"."+m.group(1),fields))
    return out
def same(g,w):
    if isinstance(w,bool): return str(g).lower()==str(w).lower()
    try: return abs(float(g)-float(w))<1e-6
    except: return False
with Session(lock=None) as s:
    for mod in sys.argv[1:]:
        cl=classes(mod); tot=0; fixed=[]; bad=[]
        for tn,fields in cl:
            for f,w in fields.items():
                r=s.call("jawa/mod_settings_field",typeName=tn,action="get",field=f)
                if not (r or {}).get("success"): bad.append(tn+"."+f+" unreadable"); continue
                tot+=1
                g=r.get("value")
                if not same(g,w):
                    s.call("jawa/mod_settings_field",typeName=tn,action="set",field=f,value=str(w).lower() if isinstance(w,bool) else str(w))
                    r2=s.call("jawa/mod_settings_field",typeName=tn,action="get",field=f)
                    fixed.append("%s.%s %r->%r(now %r)"%(tn.split('.')[-1],f,g,w,(r2 or {}).get("value")))
        print(mod,"classes=%d fields=%d reset=%d"%(len(cl),tot,len(fixed)),fixed,"UNREAD:",bad[:5],len(bad))
