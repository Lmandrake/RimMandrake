import sys, os, json
U=os.path.join(os.getcwd(),"src","RimMandrake","Utils"); sys.path.insert(0,U)
import rimbridge_client as rb
h,p,t=rb.resolve_endpoint(); c=rb.RimBridge(host=h,port=p,token=t,timeout=60.0); c.connect()
def call(tool,**a):
    r=c.call(tool,a)
    if isinstance(r,dict) and r.get("content"): r=json.loads(r["content"][0]["text"])
    return r
S="RimMandrake.LuminousPigment.LuminousPigmentSettings"; MOD=None
import importlib.util
def menu(tag):
    r=call("rimworld/list_architect_designators",categoryId="architect-category:production",includeDetails=False) if True else None
    ds=r.get("designators") or []
    hits=[d for d in ds if "glowtank" in json.dumps(d).lower()]
    print(tag,"success",r.get("success"),"count",len(ds),"glowtank rows",len(hits),(json.dumps(hits[0])[:160] if hits else ""))
    if not ds: print(json.dumps(r)[:400])
def apply():
    spec=importlib.util.spec_from_file_location("lv",os.path.join(U,"..","LuminousPigment","validation.py"))
    mid=[l for l in open(os.path.join(U,"..","LuminousPigment","validation.py")).read().splitlines() if l.startswith("MOD_ID")][0].split("=")[1].strip().strip('"')
    call("rimworld/open_mod_settings",modId=mid,replaceExisting=True)
    call("jawa/window_list_close",action="close",typeName="ModSettings",closeAll=True)
menu("default")
orig=call("jawa/mod_settings_field",typeName=S,action="get",field="glowTankEnabled")["value"]; print("orig",orig)
call("jawa/mod_settings_field",typeName=S,action="set",field="glowTankEnabled",value="False"); apply(); menu("after OFF+apply")
call("jawa/mod_settings_field",typeName=S,action="set",field="glowTankEnabled",value=orig); apply(); menu("after restore+apply")
