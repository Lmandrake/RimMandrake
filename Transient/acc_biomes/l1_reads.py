"""acc_biomes L1 reads, 2026-10-08. python.exe only. Verdicts from tool success/foundCount/notFound, never substrings."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host,port,token=rbc.resolve_endpoint()
def gd(rb, defs, **kw):
    a={"defs":";".join(defs) if isinstance(defs,list) else defs}; a.update(kw)
    r=rb.call("jawa/get_defs",a,check=False)
    return {"success":r.get("success"),"found":r.get("foundCount"),"requested":r.get("requested"),"notFound":r.get("notFound"),"msg":(r.get("message") or "")[:160],"raw":r}
out={}
with rbc.RimBridge(host,port,token) as rb:
    tools=rb.call("rimbridge/list_tools",{},check=False) if False else None
    try:
        tl=rb.list_tools() if hasattr(rb,"list_tools") else None
    except Exception as e: tl=None
    out["tools_api"]=str(type(tl))
    names=[]
    if tl:
        names=[t.get("name") if isinstance(t,dict) else str(t) for t in (tl if isinstance(tl,list) else tl.get("tools",[]))]
    out["jawa_tools_n"]=len([n for n in names if n and "jawa" in n])
    out["graffiti_tools"]={t:any(n and n.endswith("/"+t) for n in names) for t in ["thing_graphic","spawn_variant","running_mods","glow_at","site_state"]}
    out["chotrix_print"]=gd(rb,"ThingDef/RM_Filth_SettledFilm",fields="modExtensions",deep=True)
    out["chotrix_job"]=gd(rb,"JobDef/RM_ChotrixDragKill",fields="driverClass")
    out["chotrix_tt"]=gd(rb,"ThinkTreeDef/RM_ThinkTree_Chotrix",fields="thinkRoot",deep=True)
    out["aero"]=gd(rb,["ThingDef/RM_AerosolScreen","ThingDef/RM_ProjectorCore"],fields="comps",deep=True)
    out["aero_biome"]=gd(rb,"BiomeDef/RM_Wasteland",fields="modExtensions",deep=True)
    wf=["GenStepDef/"+n for n in "RM_WreckField_Abyss RM_WreckField_BlueDesert RM_WreckField_Contagion RM_WreckField_FeverWood RM_WreckField_FloodedCanyon RM_WreckField_GreyFloor RM_WreckField_LanternDeeps RM_WreckField_Miasma RM_WreckField_NightsideIce RM_WreckField_Scald RM_WreckField_ScaldFloor RM_WreckField_Stillsand RM_WreckField_TheRot RM_WreckField_TwilightFloor RM_WreckField_Warscar RM_WreckField_Wasteland".split()]
    out["wreckfields"]=gd(rb,wf,fields="defName")
    out["jacket"]=gd(rb,"ThingDef/RM_BrineJacket",fields="defName")
    out["wrecklists"]=gd(rb,["RimMandrake.Wreckage.RM_WreckListDef/RM_WreckList_CrawlerRoad","RimMandrake.Wreckage.RM_WreckListDef/RM_WreckList_Fresh"],fields="defName")
    out["harmony1"]=rb.call("jawa/harmony_patches",{"typeName":"ToxicUtility","methodName":"DoAirbornePawnToxicDamage"},check=False)
    out["harmony2"]=rb.call("jawa/harmony_patches",{"typeName":"GameCondition_ToxicFallout","methodName":"DoCellSteadyEffects"},check=False)
    out["log_err"]=rb.call("jawa/drain_log",{"limit":400,"errorsOnly":True},check=False)
for k,v in out.items():
    if isinstance(v,dict) and "raw" in v: v2={a:b for a,b in v.items() if a!="raw"}; print(k,json.dumps(v2)[:500])
    else: print(k,json.dumps(v)[:900])
json.dump(out,open(r"Transient\acc_biomes\l1_reads_raw.json","w"),indent=1,default=str)
