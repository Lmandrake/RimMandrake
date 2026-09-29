import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r

out = {}

r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
out["start_debug_game_ready"] = r

# poll for a real map (per skill: open fresh connection already done; poll list_pawns)
map_ready = False
for i in range(120):
    lp = call("jawa/list_pawns")
    if isinstance(lp, dict) and lp.get("error"):
        pass
    msg = json.dumps(lp)
    if "No current map" not in msg:
        map_ready = True
        out["map_ready_after_polls"] = i
        break
    time.sleep(1)
out["map_ready"] = map_ready

# also wait for Playing programState
playing = False
for i in range(60):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        playing = True
        break
    time.sleep(1)
out["playing"] = playing

CANDIDATES = ["Muffalo", "LabradorRetriever", "Husky", "Boomrat", "Warg", "Alpaca", "Cow"]

chosen = None
chosen_thingId = None
baseline_rows = None

for kind in CANDIDATES:
    sp = call("jawa/spawn_pawn", kindDef=kind, x=0, z=0, count=1, faction="player")
    rows = sp.get("pawns") or []
    ok_rows = [r for r in rows if r.get("ok")]
    if not ok_rows:
        out.setdefault("spawn_attempts", []).append({"kind": kind, "spawn": sp})
        continue
    tid = ok_rows[0]["id"]
    vis = call("jawa/animal_trainable_visibility", pawn=tid, trainables="Rescue,Haul")
    out.setdefault("spawn_attempts", []).append({"kind": kind, "spawn": sp, "visibility": vis})
    if vis.get("success"):
        rows = {row["trainable"]: row for row in vis.get("rows", [])}
        if rows.get("Rescue", {}).get("visible") and rows.get("Haul", {}).get("visible"):
            chosen = kind
            chosen_thingId = tid
            baseline_rows = rows
            break

out["chosen_species"] = chosen
out["chosen_control_thingId"] = chosen_thingId
out["control_baseline_rows"] = baseline_rows

if chosen:
    # control animal: re-check visibility now (should be unchanged / still shows both)
    control_vis = call("jawa/animal_trainable_visibility", pawn=chosen_thingId, trainables="Rescue,Haul")
    out["control_final_visibility"] = control_vis

    # subject animal: same species, gets RUT_StrandedDeformation hediff added
    sp2 = call("jawa/spawn_pawn", kindDef=chosen, x=2, z=2, count=1, faction="player")
    out["subject_spawn"] = sp2
    rows2 = [r for r in (sp2.get("pawns") or []) if r.get("ok")]
    if rows2:
        subject_id = rows2[0]["id"]
        out["subject_thingId"] = subject_id

        pre_vis = call("jawa/animal_trainable_visibility", pawn=subject_id, trainables="Rescue,Haul")
        out["subject_pre_hediff_visibility"] = pre_vis

        hediff_add = call("jawa/pawn_health", pawn=subject_id, action="add",
                           hediff="RUT_StrandedDeformation", severity=1)
        out["hediff_add"] = hediff_add

        post_vis = call("jawa/animal_trainable_visibility", pawn=subject_id, trainables="Rescue,Haul")
        out["subject_post_hediff_visibility"] = post_vis

        # also check a couple of other trainables to confirm blast radius is narrow
        other_vis = call("jawa/animal_trainable_visibility", pawn=subject_id, trainables="Tameness,Obedience,Release")
        out["subject_other_trainables"] = other_vis

with open(r"D:\Luke\dev\Rimworld\Transient\warden_trainable_gate_verify_result.json", "w") as f:
    json.dump(out, f, indent=2, default=str)

print("DONE")
print(json.dumps({k: out[k] for k in ("map_ready", "playing", "chosen_species",
                                       "control_final_visibility", "subject_pre_hediff_visibility",
                                       "hediff_add", "subject_post_hediff_visibility",
                                       "subject_other_trainables") if k in out}, indent=2, default=str))
