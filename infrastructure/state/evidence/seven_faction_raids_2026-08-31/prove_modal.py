"""FIRE_RAID_REPORTS_MODAL_1 - prove jawa/fire_raid reports the swallowing modal.

Mod list: the 19-mod minimal tier PLUS leo.raidprotectionfee, so the intercept is
the only non-baseline thing present. Run with WINDOWS python.exe.

Two arms, and the pair is the proof:
  A  Pirate           humanlike + hostile + off cooldown  -> extorted, EXPECT blockedByDialog
  B  Mechanoid        humanlikeFaction FALSE              -> exempt,   EXPECT a real raid
"""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rbc

OUT = r"D:\Luke\dev\Rimworld\Transient\raid_proof_2026_08_30\modal_results.json"
host, port, token = rbc.resolve_endpoint()
S = rbc.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()


def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


def log(*a):
    # The Windows console is cp1252; the tool's note carries emoji on purpose.
    print(*[str(x).encode("ascii", "backslashreplace").decode("ascii") for x in a],
          flush=True)


rec = {"startedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

log("== quicktest map")
call("rimworld/start_debug_game_ready", timeoutMs=280000,
     readiness="mapData", pauseIfNeeded=True)
for _ in range(180):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        break
    time.sleep(1)
log("   programState:", st.get("programState"))

facs = {f["defName"]: f for f in call("jawa/list_factions", limit=200).get("factions", [])}
rec["factions"] = {k: {"hostile": v.get("hostile"), "permanentEnemy": v.get("permanentEnemy")}
                   for k, v in facs.items()}
log("   factions:", json.dumps(rec["factions"]))

# clear anything already on the stack so 'opened during the call' is unambiguous
pre = call("jawa/window_list_close", action="list")
rec["windowsBefore"] = pre.get("windows")
log("   stack before:", json.dumps([w["type"] for w in pre.get("windows", [])]))


def arm(fdef):
    r = call("jawa/faction_relations_set", faction=fdef, other="Player",
             kind="Hostile", goodwill=-100, both=True)
    h = (call("jawa/list_factions", defName=fdef, includeHidden=True).get("factions") or [{}])[0].get("hostile")
    return r.get("success"), h


def shoot(fdef, label):
    ok, hostile = arm(fdef)
    log("\n==", label, fdef, "| setter", ok, "| hostile", hostile)
    r = call("jawa/fire_raid", points=2000, faction=fdef,
             strategy="ImmediateAttack", arrivalMode="EdgeWalkIn", dryRun=False)
    row = {
        "faction": fdef, "hostile": hostile,
        "success": r.get("success"), "executed": r.get("executed"),
        "blockedByDialog": r.get("blockedByDialog"),
        "windowsOpened": r.get("windowsOpened"),
        "actual": r.get("actual"), "arrived": r.get("arrived"),
        "pawnsArrivedTotal": r.get("pawnsArrivedTotal"),
        "note": r.get("note"),
    }
    log("   success=%s executed=%s blockedByDialog=%s pawns=%s"
        % (row["success"], row["executed"], row["blockedByDialog"], row["pawnsArrivedTotal"]))
    log("   windowsOpened:", json.dumps(row["windowsOpened"]))
    log("   note:", (row["note"] or "")[:500])
    return row


# ---- ARM A: the extorted faction
# `Pirate` has no faction in this world; PirateWaster is the humanlike hostile that does.
rec["A_extorted"] = shoot("PirateWaster", "ARM A (expect blockedByDialog)")

stack = call("jawa/window_list_close", action="list")
rec["stackAfterA"] = [w["type"] for w in stack.get("windows", [])]
log("\n   stack after A:", json.dumps(rec["stackAfterA"]))

closed = call("jawa/window_list_close", action="close",
              typeName="Dialog_NodeTree", closeAll=True)
rec["cleared"] = {"closedCount": closed.get("closedCount"),
                  "closed": closed.get("closed"),
                  "stillOpenCount": closed.get("stillOpenCount")}
log("   cleared:", json.dumps(rec["cleared"]))

# ---- ARM B: a faction the fee exempts (def.humanlikeFaction == false)
rec["B_exempt"] = shoot("Mechanoid", "ARM B (expect a real raid, no window)")

# ---- restore
call("jawa/faction_relations_set", faction="Mechanoid", other="Player",
     kind="Hostile", goodwill=-100, both=True)
rec["stackAtEnd"] = [w["type"] for w in
                     call("jawa/window_list_close", action="list").get("windows", [])]

a, b = rec["A_extorted"], rec["B_exempt"]
rec["verdict"] = {
    "A_reports_modal": bool(a["blockedByDialog"]) and a["pawnsArrivedTotal"] == 0
                       and bool(a["windowsOpened"]),
    "A_would_have_lied": a["executed"] is True,
    "B_clean_raid": (not b["blockedByDialog"]) and (b["pawnsArrivedTotal"] or 0) > 0
                    and not b["windowsOpened"],
}
json.dump(rec, open(OUT, "w"), indent=1)
log("\nVERDICT:", json.dumps(rec["verdict"]))
log("written:", OUT)
