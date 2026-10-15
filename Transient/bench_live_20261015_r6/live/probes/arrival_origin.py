"""r5: where do the uninvited hostiles on a quicktest come from? fresh quicktest -> quiet_site isolated -> the GSS noon pin
(time_set_ticks +~14000, timeException) -> awareness armed -> governed advance up to N ticks in 500-tick chunks; on any
stop, read jawa/pawn_origin + jawa/awareness incidents for the arrivals. Read-only diagnosis; nothing is scored."""
import sys, os, json, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
U = os.path.join(ROOT, "src", "RimMandrake", "Utils")
sys.path.insert(0, U); sys.path.insert(0, os.path.join(U, "modcheck"))
import validation_core as V
import quiet_site as Q
import clockgate as CG
out_path = sys.argv[1]; budget = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
B = V.Bridge()
res = {"menu": (B.call("rimworld/go_to_main_menu") or {}).get("success")}
res["start"] = (B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000) or {}).get("success")
for _ in range(120):
    if (B.call("rimworld/get_ui_state") or {}).get("programState") == "Playing": break
    time.sleep(1)
mi = B.call("jawa/map_info") or {}
res["map"] = {k: mi.get(k) for k in ("mapBiome", "tile", "longitude")}
B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
qs = Q.apply_site_profile(B, row="r5_arrival_origin")
res["settle"] = qs.settle(max_ticks=600)
res["awareness_arm"] = (B.call("jawa/awareness", action="arm") or {}).get("success")
clk = B.call("jawa/time_clock") or {}
res["pin"] = B.call("jawa/time_set_ticks", ticks=(clk.get("ticksGame") or 0) + 14000, timeException=True).get("success")
done, stop = 0, None
while done < budget:
    try:
        CG.advance_chunk(B, 500)
        done += 500
    except Exception as e:
        stop = repr(e)[:600]
        break
res["advanced"] = done; res["stop"] = stop
pw = (B.call("jawa/list_pawns") or {}).get("pawns") or []
hostile = [p for p in pw if p.get("hostile")]
res["hostiles"] = [(p.get("id"), p.get("kindDef"), p.get("factionName"), p.get("x"), p.get("z")) for p in hostile][:20]
ids = ",".join("".join(ch for ch in str(p.get("id")) if ch.isdigit()) for p in hostile[:10])
res["origin"] = B.call("jawa/pawn_origin", ids=ids) if ids else None
res["incidents"] = B.call("jawa/awareness", action="incidents") if hostile else None
res["letters"] = (B.call("jawa/quiet_site", action="status") or {}).get("letters")
res["receipt_arrivals"] = qs.receipt().get("arrivals")
json.dump(res, open(out_path, "w"), indent=1, default=str)
print(json.dumps({k: res[k] for k in ("map", "advanced", "stop", "hostiles")}, default=str)[:1500])
