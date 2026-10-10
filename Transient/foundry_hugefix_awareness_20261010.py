"""After the HugeThings reload: awareness checks that need no restart. python.exe ... <phase>
phase load   : right after loading the save (paused): status + pawn_origin of every pawn (PAWN_ORIGIN A5)
phase tests  : arm, worker-false incident (INCIDENT A3), queued incident (A4), substituted spawn receipt (VISITOR A2), meters (A6)
Appends to Transient/foundry_hugefix_awareness_20261010.json."""
import json, os, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path("src/RimMandrake/Utils").resolve()))
import rimbridge_client as rb

OUT = "Transient/foundry_hugefix_awareness_20261010.json"
R = json.load(open(OUT)) if os.path.exists(OUT) else {}
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=200.0); S.connect()


def c(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation", None)
    return r


def save():
    json.dump(R, open(OUT, "w"), indent=1, ensure_ascii=False)


ph = sys.argv[1]
if ph == "load":
    st = c("jawa/awareness", action="status")
    pawns = c("jawa/list_pawns", limit=500)
    ids = [str(p.get("id") or p.get("thingId")) for p in (pawns.get("pawns") or [])]
    po = c("jawa/pawn_origin", ids=",".join(ids), limit=500) if ids else {"note": "no pawns listed", "raw": str(pawns)[:300]}
    rows = po.get("pawns") or []
    gens = {}
    for r in rows:
        g = json.dumps(r.get("generation"))[:80]; gens[g] = gens.get(g, 0) + 1
    R["load"] = {"status": st, "pawnCount": len(ids), "originRows": len(rows), "generationKinds": gens,
                 "preLoadClaims": [r for r in rows if "PRE_LOAD" in json.dumps(r)][:5], "sample": rows[:3]}
    save(); print(json.dumps({k: R["load"][k] for k in ("pawnCount", "originRows", "generationKinds")})[:1500])
    print("epoch", st.get("epoch"), "startedBy", st.get("startedBy"), "installed", st.get("installed"))
elif ph == "tests":
    T = R.setdefault("tests", {})
    T["arm"] = c("jawa/awareness", action="arm", minutes=30)
    # A3: worker-false. ShortCircuit's worker returns false with no conduit/battery culprit; dry run first for CanFireNow.
    for inc in ("ShortCircuit", "AnimalInsanityMass"):
        T["dry_" + inc] = c("jawa/fire_incident", incidentDef=inc, dryRun=True, forced=True)
        T["fire_" + inc] = c("jawa/fire_incident", incidentDef=inc, forced=True)
    T["journal_after_false"] = c("jawa/incident_journal", limit=4)
    # A4: queued incident fired later by the queue
    T["queue"] = c("jawa/incident_schedule", incidentDef="ResourcePodCrash", delayTicks=60)
    c("jawa/set_game_speed", speed="Fast"); time.sleep(20); c("jawa/set_game_speed", speed="Paused")
    T["journal_after_queue"] = c("jawa/incident_journal", limit=4)
    # VISITOR A2: substituted spawn - request a kind the spawn tool may substitute; receipt vs independent read
    sys.path.insert(0, str(pathlib.Path("src/RimMandrake/Utils/modcheck").resolve()))
    import contract as C
    rec = []
    for i, (kind, fac) in enumerate((("Thrumbo", "none"), ("Tribal_Warrior", "player"), ("SpaceRefugee", "player"))):
        res = c("jawa/spawn_pawn", kindDef=kind, x=120 + 3 * i, z=120, faction=fac, count=1)
        rows = (c("jawa/list_pawns", limit=500) or {}).get("pawns") or []
        rec.append(C.spawn_receipt("spawn%d" % i, "jawa/spawn_pawn", kind, res, rows))
    T["receipts"] = rec; T["receiptProblems"] = C.receipt_problems(rec)
    T["meters"] = c("jawa/awareness", action="status").get("meters")
    save()
    for k, v in T.items(): print(k, json.dumps(v, ensure_ascii=False)[:700])
