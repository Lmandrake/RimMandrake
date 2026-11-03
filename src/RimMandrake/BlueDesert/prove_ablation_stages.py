"""Live proof A3 of BLUEDESERT_GPT_ENRICHMENT_1: the line gives back slowly. On the current (disposable quicktest) map,
retiled to RM_BlueDesert through modcheck.bland_world.retile, RM_AblationSalvage_Wreckage fires and unfolds in stages:
  stage 0  the marker (RM_AblationEmergence) stands hidden and no letter has come;
  stage 1  hours later its label reads "dark shape under the ice", scavengers (vekkit/vrisk) have arrived, still no letter;
  stage 2  hours later again the marker is gone, the payload (ShipChunk) lies at the spot and the letter
           "The line gave up wreckage" has arrived.
ablationPaceFactor is set to its slider floor 0.25 for the run (stages at 1250-1875 and +1875-2812 ticks) and restored.
Exits 0 when the clause holds, 1 when it does not, 2 when unmeasured.

Run under Windows python.exe with the game up (it starts a debug quicktest map if none is playing):
    python.exe src/RimMandrake/BlueDesert/prove_ablation_stages.py < /dev/null   (from the repo root)
It cleans up: the setting restored, the tile's biome and temperature restored (the spawned things stay on the
disposable map).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
sys.path.insert(0, UTILS)
sys.path.insert(0, os.path.join(UTILS, "modcheck"))
import rimbridge_client as rb       # noqa: E402
import bland_world as BW            # noqa: E402
import helpers as H                 # noqa: E402

SETTINGS = "RimMandrake.BlueDesert.RM_BlueDesertSettings"
INCIDENT = "RM_AblationSalvage_Wreckage"
MARKER = "RM_AblationEmergence"
STAGE1_LABEL = "dark shape under the ice"            # RM_AblationEmergence.Label at stage >= 1
LETTER = "The line gave up wreckage"                 # RM_AblationSalvage.xml letterLabel
SCAVENGERS = ("RM_Vekkit", "RM_Vrisk")
PAYLOAD = "ShipChunk"


PACE = 0.25                                          # ablationPaceFactor for the run (its slider floor)
STAGE1_READ = 2400                                   # ticks after the fire when stage 1 is read
STAGE2_READ = 5200                                   # ticks after the fire when stage 2 is read


def judge(obs):
    """The verdict on one run's observations: [] when the stages held, else what went wrong. Pure (selftested)."""
    bad = []
    if STAGE1_LABEL in str(obs["stage0"]["label"]) or LETTER in obs["stage0"]["letters"]:
        bad.append("stage 0 already showed the shape or the letter")
    if obs["stage1"]["label"] is None or STAGE1_LABEL not in str(obs["stage1"]["label"]):
        bad.append("no dark shape under the ice after %d ticks at pace %s" % (STAGE1_READ, PACE))
    if obs["stage1"]["scavengers"] <= 0:
        bad.append("no vekkit or vrisk came to the shape")
    if LETTER in obs["stage1"]["letters"]:
        bad.append("the letter came before the ice gave way")
    if obs["stage2"]["markers"] != 0 or obs["stage2"]["payload"] < 1 or LETTER not in obs["stage2"]["letters"]:
        bad.append("after %d ticks: markers %d, payload %d, letter %s" % (
            STAGE2_READ, obs["stage2"]["markers"], obs["stage2"]["payload"], LETTER in obs["stage2"]["letters"]))
    return bad


class Session(object):
    def __init__(self):
        host, port, token = rb.resolve_endpoint()
        self.b = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.b.connect()

    def call(self, tool, **p):
        r = self.b.call(tool, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r


def ticks(s):
    return (s.call("rimworld/get_game_info") or {}).get("ticksGame")


def advance_to(s, goal):
    """Run the clock until ticksGame >= goal (fast_advance undershoots by its margin; loop the rest)."""
    for _ in range(6):
        now = ticks(s)
        if now is None:
            return None
        if now >= goal:
            return now
        H.fast_advance(s, goal - now + 60, margin=0)
    return ticks(s)


def letters(s):
    out = []
    for l in (s.call("jawa/letter_list") or {}).get("letters") or []:
        lab = l.get("label")
        out.append(lab.get("RawText") if isinstance(lab, dict) else lab)
    return out


def things(s, d):
    r = s.call("jawa/list_things", defName=d, limit=50)
    if "countMatched" not in r:
        return None
    return r.get("things") or []


def label_of(s, thing):
    """The thing's live label through inspect_string (list_things rows are not relied on to carry it)."""
    if not thing or not thing.get("id"):
        return None
    rows = (s.call("jawa/inspect_string", thingIds=thing["id"]) or {}).get("things") or []
    return rows[0].get("label") if rows and not rows[0].get("error") else None


def count_pawns(s):
    n = 0
    for d in SCAVENGERS:
        t = things(s, d)
        if t is None:
            return None
        n += len(t)
    return n


def main():
    s = Session()
    if s.call("rimworld/get_ui_state").get("programState") != "Playing":
        s.call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
        for _ in range(120):
            if s.call("rimworld/get_ui_state").get("programState") == "Playing":
                break
            time.sleep(1)
    info = s.call("jawa/map_info")
    if info.get("sizeX") is None or info.get("tile") is None:
        print("UNMEASURED: no playing map: %r" % (info,))
        return 2
    old_pace = (s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="ablationPaceFactor") or {}).get("value")
    if old_pace is None:
        print("UNMEASURED: ablationPaceFactor unreadable")
        return 2
    try:
        rec = BW.retile(s, "RM_BlueDesert", temperature=-30)
    except BW.BlandWorldError as ex:
        print("UNMEASURED: retile failed: %s" % ex)
        return 2
    obs = {}
    try:
        biome = (s.call("jawa/map_info") or {}).get("mapBiome")
        if biome != "RM_BlueDesert":
            print("UNMEASURED: the map does not read RM_BlueDesert after the retile (%r)" % (biome,))
            return 2
        s.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="ablationPaceFactor", value=str(PACE))
        if things(s, MARKER):
            print("UNMEASURED: a salvage marker already stands on this map")
            return 2
        letters0, scav0 = letters(s), count_pawns(s)
        r = s.call("jawa/fire_incident", incidentDef=INCIDENT)
        t0 = ticks(s)
        m = things(s, MARKER)
        obs["fire"] = r
        if not m or t0 is None or scav0 is None:
            print("UNMEASURED: the incident did not place a marker (fire_incident %r, markers %r)" % (r, m))
            return 2
        obs["stage0"] = {"label": label_of(s, m[0]), "letters": letters(s)[len(letters0):]}
        advance_to(s, t0 + STAGE1_READ)
        m = things(s, MARKER) or []
        obs["stage1"] = {"ticks": (ticks(s) or 0) - t0, "label": label_of(s, m[0]) if m else None,
                         "scavengers": (count_pawns(s) or 0) - scav0, "letters": letters(s)[len(letters0):]}
        advance_to(s, t0 + STAGE2_READ)
        payload = things(s, PAYLOAD) or []
        obs["stage2"] = {"ticks": (ticks(s) or 0) - t0, "markers": len(things(s, MARKER) or []),
                         "payload": len(payload), "letters": letters(s)[len(letters0):]}
    finally:
        s.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="ablationPaceFactor", value=str(old_pace))
        problems = BW.restore_tile(s, rec)
        if problems:
            print("restore problems: %s" % problems)
    print(json.dumps(obs, default=str))
    bad = judge(obs)
    if bad:
        print("FAIL: " + "; ".join(bad))
        return 1
    print("PASS: crack, then a shape under the ice with scavengers, then wreckage and the letter")
    return 0


if __name__ == "__main__":
    sys.exit(main())
