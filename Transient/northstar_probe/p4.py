import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from rimdrive.session import Session
OUT={}
def rec(s,key,tool,**p):
    t=time.time()
    try: r=s.call(tool,**p)
    except Exception as e: r={"EXC":type(e).__name__,"msg":str(e)[:300]}
    if isinstance(r,dict): r.pop("operation",None)
    OUT[key]={"tool":tool,"params":p,"ms":int((time.time()-t)*1000),"result":r}; return r
def P(s):
    return rec(s,"_p","jawa/list_pawns",includeHealth=True,includeCorpses=True,limit=500)["pawns"]
def brief(k):
    r=OUT[k]["result"]; return "%s %s" % (k, json.dumps({x:r.get(x) for x in list(r)[:8] if x!="ticksGame"},default=str)[:260])
with Session(strict=False,quiet=True,focus=False) as s:
    rows=P(s)
    by={r["id"]:r for r in rows}
    # 1 mental end
    rec(s,"1_mental_end","jawa/pawn_mental",pawn="Human691",action="end")
    print(brief("1_mental_end")); print("   state now:", rec(s,"1b","jawa/pawn_mental",action="list",pawn="Human691")["currentState"])
    # 2 resurrect
    rec(s,"2_resurrect","jawa/pawn_resurrect",pawn="Human696",restoreMissingParts=True,removeDiedThoughts=True)
    print(brief("2_resurrect")); r696=[r for r in P(s) if r["id"]=="Human696"][0]; print("   696 dead/spawned/downed:", r696["dead"],r696["spawned"],r696["downed"], "letters:", len(rec(s,"2b","jawa/letter_list")["letters"]))
    # 3 neutralize hostiles
    hostile=[r for r in P(s) if r["hostile"] and not r["dead"]]
    wolves=[r for r in P(s) if r["kindDef"]=="Wolf_Timber" and not r["dead"]]
    print("   targets: hostile",[h["id"] for h in hostile],"wolves",[w["id"] for w in wolves])
    if hostile:
        rec(s,"3a_kill_force","jawa/pawn_force_incapacitate",pawn=hostile[0]["id"],action="kill"); print(brief("3a_kill_force"))
    if len(hostile)>1:
        rec(s,"3b_kill_damage","jawa/damage",thingId=hostile[1]["id"],damageDef="Cut",amount=500,allowColonists=False); print(brief("3b_kill_damage"))
    if wolves:
        rec(s,"3c_kill_wolf","jawa/pawn_force_incapacitate",pawn=wolves[0]["id"],action="kill"); print(brief("3c_kill_wolf"))
    after=P(s); print("   hostile alive after:", [r["id"] for r in after if r["hostile"] and not r["dead"]], "wolves alive:", [r["id"] for r in after if r["kindDef"]=="Wolf_Timber" and not r["dead"]])
    print("   corpses now (dead rows):", len([r for r in after if r["dead"]]))
    # 4 extinguish
    rec(s,"4_ext","jawa/map_fire",action="extinguish",rect="0,0,250,250"); print(brief("4_ext"))
    print("   fires after:", rec(s,"4b","jawa/list_things",defName="Fire")["countMatched"])
    # 5 heal Fu
    fu=[r for r in P(s) if r["id"]=="Human693"][0]; hd=fu["health"]["hediffs"]; print("   Fu hediffs before:", [(h["def"],h["part"]) for h in hd])
    for h in hd:
        if h["def"] in ("Cut","Crack","Frostbite","Burn"):
            r=rec(s,"5_rm_"+h["def"],"jawa/pawn_health",pawn="Human693",action="remove",hediff=h["def"],bodyPart=h["part"]); print("   rm",h["def"],h["part"],"->",r.get("success"),str(r.get("message"))[:80])
    fu=[r for r in P(s) if r["id"]=="Human693"][0]; print("   Fu hediffs after:", [(h["def"],h["part"]) for h in fu["health"]["hediffs"]], "bleed", fu["health"].get("bleedRate"))
    # 6 needs: mood write persistence
    rec(s,"6_food","jawa/pawn_need",pawn="Human693",action="need",need="Food",level=1.0)
    rec(s,"6_mood","jawa/pawn_need",pawn="Human693",action="need",need="Mood",level=0.9)
    n=rec(s,"6b","jawa/pawn_need",pawn="Human693",action="list"); print("   needs immediately:", [(x["need"],round(x["level"],2)) for x in n["needs"] if x["need"] in ("Mood","Food")])
    rec(s,"6_step","rimworld/step_game_ticks",ticks=120,pauseFirst=True)
    n=rec(s,"6c","jawa/pawn_need",pawn="Human693",action="list"); print("   needs after 120 ticks:", [(x["need"],round(x["level"],2)) for x in n["needs"] if x["need"] in ("Mood","Food")])
    # 7 storyteller off + settings read-back
    before=rec(s,"7_dbg_before","jawa/debug_settings",action="list")["fields"]
    rec(s,"7_set","jawa/debug_settings",action="set",name="enableStoryteller",value=False); print(brief("7_set"))
    after=rec(s,"7_dbg_after","jawa/debug_settings",action="list")["fields"]; print("   enableStoryteller:", [f["value"] for f in before if f["name"]=="enableStoryteller"], "->", [f["value"] for f in after if f["name"]=="enableStoryteller"])
    rec(s,"7_restore","jawa/debug_settings",action="set",name="enableStoryteller",value=True)
    print("   restored:", [f["value"] for f in rec(s,"7_dbg_final","jawa/debug_settings",action="list")["fields"] if f["name"]=="enableStoryteller"])
open("Transient/northstar_probe/contracts_helpers.json","w").write(json.dumps(OUT,indent=1,default=str))
