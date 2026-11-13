"""PIT EXPOSURE live proof (PIT_TEMPERATURE_SOFTENING_1 A2-A4: an open pit tracks the desert noon, wears a prisoner's
resistance down, and grieves compassionate colonists but not psychopaths).

  python.exe src/RimMandrake/FlowWorks/northstar/pit_exposure_live.py [out_dir] [--fresh-map] [--save-name NAME] [--budget S]
  python.exe src/RimMandrake/FlowWorks/northstar/pit_exposure_live.py --resume <out_dir>/pit_exposure_result_<stamp>.json

A FlowWorks live driver (validation.py suite.live_drivers, chain pit_exposure): the result is
northstar/pit_exposure_result_<stamp>.json, stamped by driver_stamp (mod hash + the loaded DLL) so the chain reads it only
while it still describes the mod; the captures go to --shots-dir (default Transient/pit_exposure/). A whole run takes about
12 minutes; --budget S stops it after S seconds (exit 3, "RESUME <json>", for a seat whose commands are capped) and
--resume carries on from the JSON's last sample. Verdict rows are written once the last sample (--to-hour) is in.

Site (a dev quicktest map, re-rolled until its biome is a desert: --want-biome). Before anything is built: the tile's mean temperature is set to
--tile-temp (default 28 C: the quicktest desert means 16 C, a mild spring desert; Ashkarr's deserts are hot) and the clock
jumps once to year-day --day (22 = mid Jugust, northern midsummer) at local 00:00 (a declared time exception). From then
on every tick is simulated.
  pit A   5x5 dug 4 m (8 notches), OPEN to the sky                      -> prisoner PA
  pit B   5x5 dug 4 m, roofed (RoofConstructed): the roofed twin        -> prisoner PB
  cell C  a walled, roofed 5x5 prison room on the surface (a door)       -> prisoner PC  (the "normal prison cell")
Prisoners: hostile Villagers made prisoners of the colony, gear cleared (the same comfort range for all three; each pawn's
safe range is read and recorded). Colonists: the quicktest three, needs topped up once at the start (a quicktest colony
starts starving and bedless and breaks within hours), one given Psychopath. Their ideoligion is read for a Charity
precept listening for refused beggars (the shipping test, RM_PitExposure.FeelsForExposedPrisoners); if none has one,
Charity_Important is added to the player ideoligion. Colonists are left to their own work (wardens included). With
--interaction ReduceResistance (the suite's run: a player's usual setting) every prisoner's Prisoner-tab mode is set and
wardens chat with all three, the pit prisoner served from the lip; A3 then needs a chat read on PA and PC (chatsToday,
vanilla's interactionsToday) or reads UNMEASURED. Without it a new prisoner keeps vanilla's default and no warden works
them, so only the pit's own loss shows.
Timeline: settle 00:00 -> --from-hour, then one sample every --every hours to --to-hour. Each sample: outdoor and cell
temperatures of A, B, C, each prisoner's RM_NorthstarProofs.ProofExposure line (exposure, resistance, safe range, hurting,
heatstroke, room, local hour), colonists' mental state; a prisoner gone from the map is looked up (dead, carried, gone).
ROWS
  PEX_A1_defs_resolve             jawa/get_defs resolves RM_PitExposure (HediffDef) and RM_ExposedPrisoner (ThoughtDef)
  PEX_A2_open_pit_tracks_noon     both pits dry and full depth all day; pit A (open) stays within 1 C of outdoors at every
                                  sample, the roofed twin trails outdoors by more than 2 C more somewhere (a lag test: a
                                  rise alone misreads a twin still catching up from dawn); the rises are recorded
  PEX_A3_pit_wears_resistance     PA loses more resistance than PC (normal cell) and PB (roofed twin), counted from placement
                                  (00:00), and PA was hurting
  PEX_A4_compassion_not_psycho    at 12:00 every non-psychopath colonist whose ideo minds refused beggars has
                                  RM_ExposedPrisoner; the psychopath (same ideo) does not; nor does a colonist of an ideo
                                  with no Charity precept (hard morality), when the planet has one
At 12:00: a map capture of the site and a full-screen capture with PA selected (what a player sees), plus PA's inspect text.
LIES  a row whose instrument read nothing is UNMEASURED, never PASS; a prisoner lost mid-run makes its rows UNMEASURED.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
ITEM = "PIT_TEMPERATURE_SOFTENING_1"
NOTCHES = 8
DAY_TICKS, HOUR_TICKS = 60000, 2500
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
# validation.py driver_emits reads this (ast.literal_eval): the rows this driver writes
PLAN = (
    ("defs", ("PEX_A1_defs_resolve",)),
    ("day", ("PEX_A2_open_pit_tracks_noon", "PEX_A3_pit_wears_resistance", "PEX_A4_compassion_not_psycho")),
)


def local(path):
    p = str(path or "")
    if os.name != "nt" and len(p) > 2 and p[1] == ":":
        return "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/"))
    return p


def kv(s):
    out = {}
    if not str(s or "").startswith("EXPOSURE"):
        return {"raw": str(s)[:200]} if s else {}
    for tok in str(s).split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def fnum(v, d=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def tick_for(day, hour, longitude):
    """Absolute tick of local `hour` on year-day `day`. GenDate.TimeZoneAt rounds the zone to a whole hour
    (RoundToInt(longitude / 15)): a fractional zone put every sample up to half an hour off (code review 2026-11-11)."""
    off = int(round((hour - round(longitude / 15.0)) * HOUR_TICKS)) % DAY_TICKS
    return day * DAY_TICKS + off


def verdicts(res, row):
    """The three rows, from the samples alone (pure: the selftest feeds it a recorded JSON)."""
    samples, pris, cids = res["samples"], res["prisoners"], res["colonists"]["ids"]
    lost = res.get("lost") or {}

    def at(h):
        return next((s for s in samples if abs(s["hour"] - h) < 0.01), None)
    s0, s12, sl = at(res["args"]["from_hour"]), at(12.0), samples[-1] if samples else None
    full = [NOTCHES, NOTCHES]
    shallow = [s["hour"] for s in samples if s.get("depthA") != full or s.get("depthB") != full
               or s.get("fillA") not in (0, None) or s.get("fillB") not in (0, None)]   # a dry pit, full depth
    unread = [s["hour"] for s in samples if None in (s.get("TA"), s.get("TB"), s.get("out"))]
    # a sample's label is the hour asked for; the game's own hour sits a fixed zone offset from it (e.g. 5.77 for 6:00).
    # An offset that moves means a step failed or the game changed between resumes: the labels lie
    offs = [s["hour"] - fnum(s["PA"].get("hour")) for s in samples if fnum(s["PA"].get("hour")) is not None]
    drift = len(offs) < 2 or max(offs) - min(offs) > 0.1
    if not (s0 and s12) or unread or drift:
        row("PEX_A2_open_pit_tracks_noon", "UNMEASURED", "HARNESS",
            {"why": "a sample has no temperature read" if unread or not (s0 and s12) else "sample hours drift from the game clock",
             "hours_unread": unread[:6], "offsets": [round(o, 2) for o in offs][:16]})
    elif shallow or s12["PA"].get("exposed") != "True" or s12["PA"].get("outdoorRoom") != "True" \
            or s12["PB"].get("outdoorRoom") != "False":
        # flat ground or a half-dug pit also reads outdoors: the row is about a 4 m open pit and its roofed twin
        row("PEX_A2_open_pit_tracks_noon", "UNMEASURED", "SITE",
            {"why": "the pits are not a dry full-depth open pit and a roofed twin", "hours_not_dry_full_depth": shallow[:6],
             "A_exposed": s12["PA"].get("exposed"), "A_outdoorRoom": s12["PA"].get("outdoorRoom"),
             "B_outdoorRoom": s12["PB"].get("outdoorRoom")})
    else:
        riseA, riseB = s12["TA"] - s0["TA"], s12["TB"] - s0["TB"]
        lags = lambda k: [abs(s[k] - s["out"]) for s in samples if s.get(k) is not None and s.get("out") is not None]  # noqa: E731
        # "moves faster" = follows the outdoor swing: the open pit stays within 1 C of outdoors all day, the roofed twin
        # trails it by more than 2 C somewhere (a rise from the start alone misreads a twin still catching up at dawn)
        ok2 = max(lags("TA")) <= 1.0 and max(lags("TB")) > max(lags("TA")) + 2.0
        row("PEX_A2_open_pit_tracks_noon", "PASS" if ok2 else "FAIL", "MOD",
            {"hours": [s0["hour"], 12.0], "gameHour": [s0["PA"].get("hour"), s12["PA"].get("hour")],
             "outdoor": [s0["out"], s12["out"]], "pitA_open": [s0["TA"], s12["TA"]], "pitB_roofed": [s0["TB"], s12["TB"]],
             "cellC": [s0["TC"], s12["TC"]], "riseA": round(riseA, 2), "riseB": round(riseB, 2),
             "maxLagA": round(max(lags("TA")), 2), "maxLagB": round(max(lags("TB")), 2),
             "outdoorRoomA": s12["PA"].get("outdoorRoom"), "outdoorRoomB": s12["PB"].get("outdoorRoom")})
    # from placement when it was read (a warden's chat in the settle counts), else from the first sample (older runs)
    first = res.get("placed") or (samples[0] if samples else None)
    r0 = {n: fnum((first.get(n) or {}).get("resistance")) for n in pris} if first and samples else {}
    r1 = {n: fnum(sl[n].get("resistance")) for n in pris} if sl else {}
    not_prisoner = sorted({n for s in samples for n in pris if s[n].get("prisoner") != "True"})
    if not_prisoner and not lost:
        lost = {n: {"why": "not a colony prisoner in every sample (recruited, released, lost)"} for n in not_prisoner}
    if lost or not r0 or None in list(r0.values()) + list(r1.values()) or min(list(r0.values()) + list(r1.values())) < 0:
        row("PEX_A3_pit_wears_resistance", "UNMEASURED", "SITE" if lost else "HARNESS",
            {"why": "a prisoner was lost mid-run" if lost else "resistance unread", "lost": lost, "r0": r0, "r1": r1})
    else:
        d = {n: round(r0[n] - r1[n], 3) for n in pris}
        hurt = [s["hour"] for s in samples if s["PA"].get("hurting") == "True"]
        ok3 = d["PA"] > d["PC"] + 0.1 and d["PA"] > d["PB"] + 0.1 and bool(hurt)
        mode = (res.get("args") or {}).get("interaction") or ""
        # chatsToday: vanilla's interactionsToday (2 a day at most); the largest read per prisoner says wardens came
        chats = {n: max([int(fnum(s[n].get("chatsToday"), -1)) for s in samples] or [-1]) for n in pris}
        detail = {"start": r0, "end": r1, "drop": d, "PA_hurting_from_to": [hurt[0], hurt[-1]] if hurt else None,
                  "interaction": mode or "vanilla default", "chats_max": chats,
                  "mood_end": {n: sl[n].get("mood") for n in pris},
                  "safeMax": {n: sl[n].get("safeMax") for n in pris}, "ambient_end": {n: sl[n].get("ambient") for n in pris},
                  "heatstroke_end": {n: sl[n].get("heatstroke") for n in pris},
                  "from": "placement (00:00)" if res.get("placed") else "first sample", "hours": [samples[0]["hour"], sl["hour"]]}
        # the wardened comparison is fair only when counted from placement (a chat in the settle counts), wardens worked
        # all three, and the pit prisoner got no more chats than either other (an extra chat alone could beat 0.1)
        unfair = []
        if mode and not res.get("placed"):
            unfair.append("no reading at placement: chats before the first sample are lost")
        if mode and any(chats[n] < 1 for n in pris):
            unfair.append("wardens never chatted with %s" % [n for n in sorted(pris) if chats[n] < 1])
        if mode and chats["PA"] > min(chats["PB"], chats["PC"]):
            unfair.append("the pit prisoner had more chats than another (%s)" % chats)
        if unfair:
            detail["why"] = "; ".join(unfair)
            row("PEX_A3_pit_wears_resistance", "UNMEASURED", "HARNESS", detail)
        else:
            row("PEX_A3_pit_wears_resistance", "PASS" if ok3 else "FAIL", "MOD", detail)
    nt = res.get("noon_thoughts") or {}
    psycho, charity, ideos = res["colonists"]["psychopath"], res["colonists"]["charity"], res["colonists"]["ideos"]
    if not nt:
        row("PEX_A4_compassion_not_psycho", "UNMEASURED", "HARNESS", {"why": "no 12:00 thought read"})
    elif any(not nt.get(c) for c in cids):
        # an adult always carries some mood thought: an empty list is a failed read, not "no RM_ExposedPrisoner"
        row("PEX_A4_compassion_not_psycho", "UNMEASURED", "HARNESS",
            {"why": "a colonist's thoughts read empty", "empty": [c for c in cids if not nt.get(c)]})
    elif not res["colonists"].get("psycho_trait") or not charity.get(ideos.get(psycho)):
        # a psychopath outside a Charity ideoligion would lack the thought for the ideo's sake: it would prove nothing
        row("PEX_A4_compassion_not_psycho", "UNMEASURED", "HARNESS",
            {"why": "the psychopath is not a Psychopath of a Charity ideoligion", "psycho_trait": res["colonists"].get("psycho_trait"),
             "ideo": ideos.get(psycho), "charity": charity.get(ideos.get(psycho))})
    else:
        has = {c: any(t[0] == "RM_ExposedPrisoner" for t in nt.get(c) or []) for c in cids}
        cares = {c: bool(charity.get(ideos.get(c))) for c in cids}
        compassionate = [c for c in cids if c != psycho and cares[c]]
        hard = [c for c in cids if c != psycho and not cares[c]]   # a hard-morality ideo: the spec says they do not feel it
        ok4 = (bool(compassionate) and all(has[c] for c in compassionate) and bool(psycho) and not has[psycho]
               and not any(has[c] for c in hard))
        row("PEX_A4_compassion_not_psycho", "PASS" if ok4 else "FAIL", "MOD",
            {"has_thought": has, "ideo_minds_beggars": cares, "psychopath": psycho, "hard_morality": hard,
             "ideos": ideos,
             "thought_rows": {c: [t for t in nt.get(c) or [] if t[0] == "RM_ExposedPrisoner"] for c in cids}})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", nargs="?", default=None)
    ap.add_argument("--resume", default=None, help="continue the run recorded in this JSON")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--want-biome", default="Desert,AridShrubland,ExtremeDesert",
                    help="with --fresh-map: re-roll the quicktest (up to --rolls maps) until its biome is one of these")
    ap.add_argument("--rolls", type=int, default=12)
    ap.add_argument("--save-name", default=None, help="save the game at 12:00 under <name>_<stamp> (an owner review save)")
    ap.add_argument("--day", type=int, default=22, help="year-day (22 = mid Jugust, northern midsummer)")
    ap.add_argument("--tile-temp", type=float, default=28.0, help="the map tile's mean temperature (C); NaN-free")
    ap.add_argument("--from-hour", type=float, default=6.0)
    ap.add_argument("--to-hour", type=float, default=15.0)
    ap.add_argument("--every", type=float, default=1.0)
    ap.add_argument("--interaction", default="",
                    help="every prisoner's Prisoner-tab mode, e.g. ReduceResistance (a player's usual choice: wardens chat "
                         "twice a day); empty = vanilla's default for a new prisoner")
    ap.add_argument("--budget", type=float, default=0.0, help="seconds before this call saves and exits 3 (0: no limit)")
    ap.add_argument("--shots-dir", default=None, help="where the 12:00 captures go (default Transient/pit_exposure/)")
    a = ap.parse_args()
    t_start = time.time()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()

    if a.resume:
        out = a.resume
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
        res.setdefault("resumes", []).append(time.strftime("%Y-%m-%dT%H:%M:%S"))
    else:
        stamp = time.strftime("%Y%m%dT%H%M%S")
        out_dir = a.out_dir or HERE
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "pit_exposure_result_%s.json" % stamp)
        res = {"script": "pit_exposure_live.py", "item": ITEM, "stamp": stamp, "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "rows": [], "samples": [], "args": {k: getattr(a, k) for k in ("day", "tile_temp", "from_hour", "to_hour",
                                                                                  "every", "save_name", "interaction")}}
    rows, samples = res["rows"], res["samples"]
    if a.resume and res.get("finished"):
        print("REFUSED: %s finished at %s: start a fresh run" % (out, res["finished"]))
        return 2
    if a.resume and "next_hour" not in res:
        print("REFUSED: %s was saved before its site was built (setup did not finish): start a fresh run" % out)
        return 2
    shots_dir = a.shots_dir or res.get("shots_dir") or os.path.join(REPO, "Transient", "pit_exposure")
    res["shots_dir"] = shots_dir
    os.makedirs(shots_dir, exist_ok=True)
    args = res["args"]

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-32s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:1200]), flush=True)
        save()

    def sc(method, arg):
        r = B.call("jawa/static_call", type=NSP, method=method, args=arg, _answer=True) or {}
        return str(r.get("result") or r.get("message") or "")

    def step(n):
        # the client sends this through tickburst_step.advance (many ticks per frame); RM_STEP_PATH=slow is one per frame
        t0 = time.time()
        r = B.call("rimworld/step_game_ticks", ticks=int(n), pauseFirst=True, timeoutMs=240000) or {}
        res.setdefault("steps", []).append({"ticks": int(n), "wallS": round(time.time() - t0, 2),
                                            "path": r.get("path") or "rimworld/step_game_ticks", "success": r.get("success")})
        print("STEP %d ticks %.2f s via %s" % (int(n), time.time() - t0, res["steps"][-1]["path"]), flush=True)

    def temp(c):
        r = B.call("jawa/cell_temperature", cell="%d,%d" % tuple(c)) or {}
        return fnum(r.get("temperature")), fnum(r.get("outdoorTemp"))

    def thoughts(pid):
        r = B.call("jawa/pawn_thoughts", pawn=str(pid)) or {}
        return [(t.get("def"), round(fnum(t.get("moodOffset"), 0.0), 2), t.get("label")) for t in r.get("thoughts") or []]

    if not a.resume:
        want = [b for b in a.want_biome.split(",") if b]
        rolled = []
        for roll in range(max(1, a.rolls) if a.fresh_map else 1):
            if a.fresh_map:
                B.call("rimworld/go_to_main_menu")
                B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
            ok, _ = V._wait_playing(B, leave_s=0)
            if not ok:
                row("PEX_site", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
                return 2
            mi = B.call("jawa/map_info") or {}
            rolled.append(mi.get("mapBiome"))
            if not want or mi.get("mapBiome") in want:
                break
        res["biome_rolls"] = rolled
        if want and rolled[-1] not in want:
            # A2 is a DESERT noon: a forest map that merely got hot is not the line, so no row is judged on it
            row("PEX_site", "UNMEASURED", "SITE", {"why": "no %s map in %d roll(s)" % ("/".join(want), len(rolled)), "rolled": rolled})
            save()
            return 2
        import driver_stamp  # noqa: E402  (mode/mod_hash/env: what validation.py checks before it reads this result)
        driver_stamp.stamp(res, B.call)
        gd = B.call("jawa/get_defs", defs="HediffDef/RM_PitExposure;ThoughtDef/RM_ExposedPrisoner", fields="defName") or {}
        found = sorted(str(d.get("defName")) for d in gd.get("defs") or [] if isinstance(d, dict))
        if gd.get("malformed") or gd.get("success") is None:
            row("PEX_A1_defs_resolve", "UNMEASURED", "HARNESS", {"why": "get_defs did not read the request", "reply": str(gd)[:300]})
        else:
            row("PEX_A1_defs_resolve", "PASS" if found == ["RM_ExposedPrisoner", "RM_PitExposure"] else "FAIL", "MOD",
                {"found": found, "notFound": gd.get("notFound"), "foundCount": gd.get("foundCount")})
        res["map"] = {k: mi.get(k) for k in ("tile", "mapBiome", "latitude", "longitude", "season", "tileInfo")}
        lon = fnum(mi.get("longitude"), 0.0)
        res["site_calm"] = V.site_calm(B)
        # a desert noon is a clear sky: overnight rain fills an open pit and its prisoner swims out (run 8, 2026-11-11;
        # RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT), which is a different mechanism from this one
        res["weather"] = str((B.call("jawa/weather_set", weather="Clear", lockWeather=True) or {}).get("success"))

        # 1. the desert and the date, set once before the site exists
        tile = mi.get("tile")
        ts = B.call("jawa/world_tile_set", tiles=str(tile), biome="Desert", temperature=a.tile_temp) or {}
        tc = B.call("jawa/world_tile_cache_reset", tiles=str(tile)) or {}
        clk = B.call("jawa/time_clock") or {}
        start_abs = int(clk.get("ticksAbs", 0)) - int(clk.get("ticksGame", 0))
        # --day is northern midsummer; a southern tile's midsummer is half a year (30 days) on
        day = a.day if fnum(mi.get("latitude"), 0.0) >= 0 else (a.day + 30) % 60
        res["args"]["day_used"] = day
        t0 = tick_for(day, 0.0, lon)
        while t0 <= int(clk.get("ticksAbs", 0)):   # never jump backwards: the same day of a later year
            t0 += 60 * DAY_TICKS
        tj = B.call("jawa/time_set_ticks", ticks=t0 - start_abs, timeException=True,
                    why="%s: midsummer desert day for the pit exposure proof, before the site is built" % ITEM) or {}
        step(1)
        res["clock"] = {"startAbs": start_abs, "midnightAbs": t0, "jump": str(tj.get("message") or tj.get("success"))[:200],
                        "date": (B.call("jawa/time_date_at") or {}).get("dateFullString"),
                        "tileSet": str(ts.get("success")), "cacheReset": str(tc.get("success"))}
        if tj.get("success") is False:
            row("PEX_site", "UNMEASURED", "HARNESS", {"why": "the clock jump was refused", "clock": res["clock"]})
            return 2

        # 2. the site, next to the colonists
        cols = (B.call("rimworld/list_colonists") or {}).get("colonists") or []
        cids = []
        for c in cols:   # the three roles need adults with an ideoligion (a quicktest child takes neither trait nor ideo)
            cid = str(c.get("pawnId", "")).replace("Thing_", "")
            pg = ((B.call("jawa/pawn_get", pawn=cid) or {}).get("pawns") or [{}])[0]
            if pg.get("developmentalStage") == "Adult" and pg.get("ideo"):
                cids.append(cid)
        pg = ((B.call("jawa/pawn_get", pawn=cids[0]) or {}).get("pawns") or [{}])[0] if cids else {}
        pos = pg.get("position") or {"x": 120, "z": 120}
        ox, oz = int(pos["x"]) - 12, int(pos["z"]) + 6
        P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
        rect = (ox - 1, oz - 1, 27, 9)
        B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
        site_rows = []
        V.prepare_site(B, rect, site_rows, "pit_exposure_site")
        if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
            row("PEX_site", "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
            return 2
        B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % rect)
        dug = {}
        pit_cells = {"A": [P(x, z) for x in range(1, 6) for z in range(1, 6)],
                     "B": [P(x, z) for x in range(9, 14) for z in range(1, 6)]}
        for c in pit_cells["A"] + pit_cells["B"]:
            d = (B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=NOTCHES, setBodyWaterM=-1) or {}).get("depth")
            dug[d] = dug.get(d, 0) + 1
        B.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,5,5" % P(9, 1))
        room = B.call("jawa/make_empty_room", rect="%d,%d,7,7" % P(17, 0), stuffDef="BlocksSandstone",
                      floorDef="Concrete") or {}
        res["site"] = {"origin": (ox, oz), "rect": rect, "probes": {"A": P(3, 3), "B": P(11, 3), "C": P(20, 3)},
                       "pit_cells": pit_cells, "dug_depths": {str(k): v for k, v in dug.items()},
                       "room": {k: room.get(k) for k in ("success", "doorAt", "message")},
                       "roomA": sc("ProofRoom", "%d,%d;%d,%d" % (P(3, 3) + P(3, 7))),
                       "roomB": sc("ProofRoom", "%d,%d;%d,%d" % (P(11, 3) + P(11, 7)))}

        # 3. the prisoners
        def spawn_prisoner(c):
            r = B.call("jawa/spawn_pawn", kindDef="Villager", x=c[0], z=c[1], faction="hostile", count=1) or {}
            pid = ((r.get("pawns") or [{}])[0]).get("id")
            if pid:
                B.call("jawa/pawn_gear", pawn=pid, action="clear")
                B.call("jawa/pawn_set_guest_status", pawn=pid, guestStatus="Prisoner", hostFaction="PlayerColony")
            return pid
        pris = {"PA": spawn_prisoner(P(3, 3)), "PB": spawn_prisoner(P(11, 3)), "PC": spawn_prisoner(P(20, 3))}
        res["prisoners"] = pris
        if not all(pris.values()):
            row("PEX_site", "UNMEASURED", "HARNESS", {"why": "a prisoner did not spawn", "prisoners": pris})
            return 2
        if args.get("interaction"):
            res["interaction_set"] = {n: sc("ProofSetInteraction", "%s;%s" % (pid, args["interaction"])) for n, pid in pris.items()}
            if any(not v.startswith("MODE ") for v in res["interaction_set"].values()):
                row("PEX_site", "UNMEASURED", "HARNESS", {"why": "a prisoner's interaction mode did not set",
                                                          "set": res["interaction_set"]})
                return 2

        # 4. the colonists: short of three adults, new colonists join (the player's ideoligion, like any newcomer)
        while len(cids) < 3:
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=P(10, 8)[0], z=P(10, 8)[1], faction="player", count=1) or {}
            nid = ((r.get("pawns") or [{}])[0]).get("id")
            if not nid:
                row("PEX_site", "UNMEASURED", "HARNESS", {"why": "fewer than three adult colonists", "spawn": str(r)[:200]})
                return 2
            cids.append(nid)
        cids = cids[:3]
        for cid in cids:
            B.call("jawa/pawn_refresh_needs", pawn=cid)
        psycho = cids[1] if len(cids) > 1 else None
        tr = B.call("jawa/pawn_traits", pawn=psycho, action="add", trait="Psychopath") or {}
        if tr.get("added") in (0, None):
            tr = B.call("jawa/pawn_traits", pawn=psycho, action="add", trait="Psychopath", force=True) or {}
        # every ideo on the planet, and which of them mind refused beggars (the shipping test reads the same precept comp)
        all_ideos = (B.call("jawa/ideo_of", precepts=True) or {}).get("ideos") or []
        charity = {i.get("name"): [p.get("defName") for p in i.get("precepts") or [] if str(p.get("defName")).startswith("Charity_")]
                   for i in all_ideos}
        added = None
        if not any(charity.values()):
            for i in all_ideos:   # none on the planet: add the common precept to the first ideo whose memes allow it
                added = B.call("jawa/ideo_precept_edit", ideo=str(i.get("id")), action="add", precept="Charity_Important") or {}
                if added.get("success") is True:
                    for j in (B.call("jawa/ideo_of", ideo=str(i.get("id")), precepts=True) or {}).get("ideos") or []:
                        if j.get("name") == i.get("name"):   # read back, never assumed
                            charity[j.get("name")] = [p.get("defName") for p in j.get("precepts") or []
                                                      if str(p.get("defName")).startswith("Charity_")]
                    if charity.get(i.get("name")):
                        break
        kind_ideos = [n for n, v in charity.items() if v]
        hard_ideos = [n for n, v in charity.items() if not v]
        # colonist 0 compassionate, colonist 1 the psychopath, both of a charity ideo; colonist 2 of a hard-morality ideo
        plan = {cids[0]: kind_ideos[:1], psycho: kind_ideos[:1]}
        if len(cids) > 2:
            plan[cids[2]] = hard_ideos[:1] or kind_ideos[:1]
        moved = {}
        for cid, names in plan.items():
            if cid and names:
                moved[cid] = str((B.call("jawa/set_pawn_ideo", pawn=cid, action="set", ideo=names[0]) or {}).get("success"))
        pgs = {cid: (((B.call("jawa/pawn_get", pawn=cid) or {}).get("pawns") or [{}])[0]) for cid in cids}
        ideos = {cid: pgs[cid].get("ideo") for cid in cids}
        psycho_trait = any(t.get("def") == "Psychopath" for t in pgs.get(psycho, {}).get("traits") or [])
        res["colonists"] = {"ids": cids, "psychopath": psycho, "trait_added": tr.get("added"), "psycho_trait": psycho_trait,
                            "ideos": ideos,
                            "charity": {n: charity.get(n) for n in set(ideos.values())}, "moved": moved,
                            "precept_added": str(added)[:160] if added else None}
        # each prisoner as placed, before the settle: wardens may chat in it, so A3 counts every loss from here
        res["placed"] = {n: kv(sc("ProofExposure", pid)) for n, pid in pris.items()}
        step(args["from_hour"] * HOUR_TICKS)
        res["next_hour"] = args["from_hour"]
        save()

    # 5. samples, resumable
    pris, cids, probes = res["prisoners"], res["colonists"]["ids"], res["site"]["probes"]
    rect = res["site"]["rect"]
    stamp = res["stamp"]
    while res["next_hour"] <= args["to_hour"] + 1e-6:
        if a.budget and time.time() - t_start > a.budget:
            save()
            print("RESUME %s (next hour %.1f)" % (out, res["next_hour"]), flush=True)
            return 3
        hour = res["next_hour"]
        s = {"hour": hour}
        for name, c in probes.items():
            s["T" + name], s["out"] = temp(c)
        for name, pid in pris.items():
            s[name] = kv(sc("ProofExposure", pid))
            if "resistance" not in s[name] and name not in res.setdefault("lost", {}):
                res["lost"][name] = {"hour": hour, "pawn_get": str((B.call("jawa/pawn_get", pawn=pid) or {}).get("message"))[:300]}
        for pit, cells in (res["site"].get("pit_cells") or {}).items():
            reps = [B.call("jawa/flowworks_pit_report", x=c[0], z=c[1]) or {} for c in cells]
            ds = [r.get("depthRaw") for r in reps if r.get("depthRaw") is not None]
            fs = [r.get("fillRaw") for r in reps if r.get("fillRaw") is not None]
            s["depth" + pit] = [min(ds), max(ds)] if ds else None
            s["fill" + pit] = max(fs) if fs else None
        cen = (B.call("jawa/pawn_census") or {}).get("pawns") or []
        s["colonists"] = {p.get("id"): {"mental": p.get("inMentalState"), "job": (p.get("job") or {}).get("def"),
                                        "mood": round(fnum((p.get("needs") or {}).get("mood"), -1), 2)}
                          for p in cen if p.get("id") in cids}
        # where each prisoner is and what it is doing: a prisoner that walks out of its pit is a finding, not noise
        byid = {p.get("id"): p for p in cen}
        for name, pid in pris.items():
            p = byid.get(pid) or {}
            s[name + "_at"] = {"x": p.get("x"), "z": p.get("z"), "job": (p.get("job") or {}).get("def"),
                               "mental": p.get("inMentalState"), "downed": p.get("downed"),
                               "climb": sc("ProofClimb", "pawn:" + pid)[:160]}
        samples.append(s)
        print("%05.1f (game %s) out=%6.2f A=%6.2f B=%6.2f C=%6.2f | PA r=%s hurt=%s hs=%s | PB r=%s | PC r=%s hurt=%s" % (
            hour, s["PA"].get("hour"), s["out"] or -99, s["TA"] or -99, s["TB"] or -99, s["TC"] or -99,
            s["PA"].get("resistance"), s["PA"].get("hurting"), s["PA"].get("heatstroke"), s["PB"].get("resistance"),
            s["PC"].get("resistance"), s["PC"].get("hurting")), flush=True)
        if abs(hour - 12.0) < 0.01:
            res["noon_thoughts"] = {cid: thoughts(cid) for cid in cids}
            shots = {}
            for wt in ("Dialog_NamePlayerFactionAndSettlement", "Dialog_NamePlayerFaction", "Dialog_NamePlayerSettlement"):
                B.call("rimworld/close_window", windowType=wt)   # the 22-day clock jump asks to name the colony
            if args.get("save_name"):
                sn = "%s_%s" % (args["save_name"], stamp)
                res["save"] = {"name": sn, "result": str(B.call("rimworld/save_game", saveName=sn))[:200]}
            B.call("jawa/clear_ui", all=True, hideHudSeconds=5)   # its default 20 s screenshot mode would hide the inspect pane below
            sh = B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=2,
                        fileName="pit_exposure_site_%s" % stamp, suppressMessage=True) or {}
            src = local(sh.get("path"))
            crop = os.path.splitext(src)[0] + "__cell_rect.png" if src else ""
            src = crop if crop and os.path.isfile(crop) else src
            if src and os.path.isfile(src):
                shots["site"] = os.path.join(shots_dir, "pit_exposure_site_%s.png" % stamp)
                shutil.copyfile(src, shots["site"])
            pa = probes["A"]
            # the HUD back on (the site capture's screenshot-mode lease ends by itself): this capture is what a player sees
            B.call("jawa/clear_ui", hideHud=False)   # dev windows shut; the HUD and the inspect pane stay for the player view
            time.sleep(5.5)   # the site shot's 5 s screenshot-mode lease runs out
            B.call("rimworld/jump_camera_to_cell", x=pa[0], z=pa[1])

            def tab_shot(key, pid, tab):
                # rimworld/select_pawn refuses a prisoner (a non-colonist), so select by id; then open the pawn's tab
                B.call("rimworld/clear_selection")
                sel = B.call("jawa/select_things", ids=str(pid), action="select") or {}
                for _ in range(20):   # no inspect pane (so no tabs) until a frame after the selection, or while screenshot mode is on
                    time.sleep(0.5)
                    tr = B.call("rimworld/open_inspect_tab", inspectTabId=tab) or {}
                    if tr.get("success"):
                        break
                time.sleep(0.5)
                sh = B.call("rimworld/take_screenshot", fileName="pit_exposure_%s_%s" % (key, stamp), suppressMessage=True) or {}
                src = local(sh.get("path"))
                if sel.get("success") and tr.get("success") and src and os.path.isfile(src):
                    shots[key] = os.path.join(shots_dir, "pit_exposure_%s_%s.png" % (key, stamp))
                    shutil.copyfile(src, shots[key])
                else:
                    shots[key] = {"select": sel.get("message") or sel.get("success"), "tab": tr.get("message")}

            # what a player sees: the prisoner's Health tab (Pit exposure), then each colonist's Needs tab (the thought)
            tab_shot("selected", pris["PA"], "Health")
            tab_shot("prisoner_tab", pris["PA"], "Prisoner")
            for cid in cids:
                tab_shot("needs_" + cid, cid, "Needs")
            res["inspect_PA"] = json.dumps(B.call("jawa/inspect_string", thingIds=str(pris["PA"])) or {}, default=str)[:1500]
            B.call("rimworld/clear_selection")
            res["shots"] = shots
        res["next_hour"] = hour + args["every"]
        save()
        if res["next_hour"] <= args["to_hour"] + 1e-6:
            step(args["every"] * HOUR_TICKS)

    # 6. verdicts
    verdicts(res, row)
    for pid in pris.values():
        B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    print("RESULT", out)
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
