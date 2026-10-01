#!/usr/bin/env python3
"""Offline selftest for the TheForge north-star suite (validation.py): no game, no bridge.

`FGame` below is a small in-memory Forge: the mod's own parsed Defs answer jawa/get_defs and jawa/biome_probe, a
cycle state machine written from RM_GameCondition_ForgeCycle.cs (phase clock, gas wash, boiling rain and floods, the
freeze onto a temp-terrain layer, gardens, cracks, melt, the pulse/cycle/master gates), a creature model written from
RM_CompForgeCycleDormancy.cs (seal, wake, the dhuvvox clock), the spunstone Harmony postfix, the keelwork apply path and
the voices' visual cue, plus the mod's `RMTheForge` debug actions. It proves two things the first live run cannot prove
on its own:

  1. a HEALTHY world passes every component (the suite's checks are not vacuously red), and
  2. each deliberate BREAK of the mod (a toggle that gates nothing, a phase that does nothing, a def that failed to
     load, a counter that lies, a loss that vanishes unannounced ...) turns exactly the component that exists for it
     red, so the checks can fail for the reason they are named for.

This is evidence about the SUITE, not about the game: the mock encodes the response shapes the suite ASSUMES (the
header of validation.py lists which are unproven live). Temporary terrain survives a top-terrain write and a condition's end, as on a real map, so a chain that
leaves a crust behind turns the next chain's site setup red.
Run: python3 src/RimMandrake/TheForge/selftest_theforge.py
"""
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import game_paths                                              # noqa: E402
import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []

# phase length in ticks (the C# draws from a range; the mock uses a fixed value inside it)
LEN = {"StillHeat": 150000, "GasWash": 6250, "Rain": 18750, "Freeze": 30000, "Growth": 150000, "Cracks": 17500,
       "Melt": 5000}
NEXT = {"StillHeat": "GasWash", "GasWash": "Rain", "Rain": "Freeze", "Freeze": "Growth", "Growth": "Cracks",
        "Cracks": "Melt", "Melt": "StillHeat"}
HAZ_DEFAULTS = {"environmentalDamageEnabled": True, "weatherPulseEnabled": True}
SLOW_LEFT = 625
MIN_AWAKE = 5000


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


class FGame(MockGame):
    def __init__(self, brk=()):
        MockGame.__init__(self, sizex=200, sizez=200)
        self.brk = set(brk)
        self.paused = True
        self.known = {}
        for group, deftype, names, _ in V.GROUPS:
            for n in names:
                self.known[(deftype, n)] = "mandrake.rm.biomes"
        for k in (("DamageDef", "RUT_Scald"), ("ThingDef", "GravEngine")):
            self.known[k] = "Ludeon.RimWorld" if k[1] == "GravEngine" else "mandrake.rm.biomes"
        if "missing_def" in self.brk:
            del self.known[("ThingDef", V.GROUPS[3][2][-1])]
        if "donor_shadow" in self.brk:
            self.known[("ThingDef", V.GROUPS[2][2][0])] = "some.donor.mod"
        if "no_scald_def" in self.brk:
            del self.known[("DamageDef", "RUT_Scald")]
        self.temp = {}
        self.settings = {SET_FORGE: dict((k, _s(v)) for k, v in V.SETTINGS_DEFAULTS.items()),
                         V.HAZ_SETTINGS: dict((k, _s(v)) for k, v in HAZ_DEFAULTS.items())}
        if "settings_drift" in self.brk:
            self.settings[SET_FORGE]["forgeVoicesVisualCues"] = "True"
        self.cond = False
        self.cyc = None
        self.letters = []
        self.messages = []
        self.keel = 0.1 if "keel_wrong" in self.brk else 0.05
        self.spun_revealed = False
        self.spun_letters = 0
        self.n_id = 100
        self.flash = (-1, -1)
        self.last_phase_voice = None

    # ----------------------------------------------------------------- settings
    def S(self, field):
        v = self.settings[SET_FORGE][field]
        return str(v) == "True"

    def active(self, field):
        return self.S("modEnabled") and self.S(field)

    def cycle_active(self):
        return self.active("grandCycleEnabled") or "gate_grand_ignored" in self.brk

    def pulse_gate(self):
        return (self.settings[V.HAZ_SETTINGS]["weatherPulseEnabled"] == "True"
                and self.active("weatherPulseEnabled")) or "gate_pulse_ignored" in self.brk

    # ------------------------------------------------------------------ dispatcher
    def handle(self, tool, p):
        p = p or {}
        fn = getattr(self, "t_" + tool.replace("/", "_"), None)
        if fn is not None:
            return fn(p)
        return MockGame.handle(self, tool, p)

    # ---------------------------------------------------------------- time & ticking
    def t_rimworld_step_game_ticks(self, p):
        n = int(p.get("ticks") or 0)
        while n > 0:
            step = min(60, n)
            prev = self.ticks
            self.ticks += step
            n -= step
            self.world_tick(prev)
        return {"success": True}

    def t_jawa_time_set_ticks(self, p):
        self.ticks = int(p["ticks"])
        return {"success": True}

    def world_tick(self, prev):
        now = self.ticks
        if self.cond and self.cyc is not None:
            self.cycle_tick(now, now // 60 != prev // 60)
        if now // 250 != prev // 250:
            for pw in self.pawns:
                if pw["kindDef"] in V.DORMANT_NATIVES and pw.get("faction") is None and not pw.get("dead"):
                    self.dorm_check(pw, now)

    # ------------------------------------------------------------------ the cycle
    class Cyc(object):
        def __init__(self):
            self.phase = "StillHeat"
            self.end = -1
            self.hiss = False
            self.gas_left = 0
            self.next_gas = -1
            self.floods_left = 0
            self.next_flood = -1
            self.seeded = False
            self.frozen = set()
            self.burst = False
            self.burst_end = 0
            self.last_voice = None
            self.c = dict(cycles=0, gasIgnitions=0, floods=0, cellsFrozen=0, cellsMelted=0, gardensSpawned=0,
                          gardensDrifted=0, meltDestroyed=0, meltPawnsBurned=0, meltRelocated=0)

    def lava_cells(self):
        return [c for c, d in self.terrain.items() if d == "LavaDeep"]

    def emit(self, label):
        if self.active("cycleTelegraphLetters") or "telegraph_off_ignored" in self.brk:
            if "no_letters" not in self.brk:
                self.letters.append(label)

    def cycle_tick(self, now, interval):
        c = self.cyc
        # the voices' visual cue (RM_ForgeVoices.Tick): needs the voices on, the cycle on, a CHANGED phase
        voices = self.active("forgeVoicesEnabled") or "voices_off_ignored" in self.brk
        if not (voices and self.cycle_active()):
            c.last_voice = c.phase
        elif c.phase != c.last_voice:
            first = c.last_voice is None
            c.last_voice = c.phase
            if not first and (self.S("forgeVoicesVisualCues")) and "no_cue" not in self.brk:
                self.messages.append(V.CUE_TEXT[c.phase])
        if c.burst and now >= c.burst_end:
            c.burst = False
        if not interval:
            return
        if not (self.cycle_active() and self.pulse_gate()):
            if c.frozen:
                self.melt(c, gentle=True, batch=200)
            return
        if c.end < 0:
            self.enter(c, "StillHeat", now)
            return
        self.phase_work(c, now)
        if now >= c.end:
            self.advance(c, now)

    def phase_work(self, c, now):
        p = c.phase
        if p == "StillHeat":
            if not c.hiss and c.end - now <= 3750 and self.active("gasWashEnabled"):
                c.hiss = True
                if "no_hiss" not in self.brk:
                    self.emit(V.LETTERS["hiss"])
            elif not c.hiss and c.end - now <= 3750 and "hiss_ignores_gas_toggle" in self.brk:
                c.hiss = True
                self.emit(V.LETTERS["hiss"])
        elif p == "GasWash":
            if c.gas_left > 0 and now >= c.next_gas:
                c.gas_left -= 1
                if "no_gas" not in self.brk:
                    c.c["gasIgnitions"] += 5
                c.next_gas = now + max(1, (c.end - now) // (c.gas_left + 1))
        elif p == "Rain":
            if c.floods_left > 0 and now >= c.next_flood:
                c.floods_left -= 1
                if (self.active("cycleFloodingEnabled") or "flood_off_ignored" in self.brk) and "no_flood" not in self.brk:
                    c.c["floods"] += 1
                c.next_flood = now + max(1, (c.end - now) // (c.floods_left + 1))
        elif p == "Freeze":
            if self.active("lavaFreezeEnabled") or "freeze_off_ignored" in self.brk:
                self.freeze_all(c)
        elif p == "Growth":
            if not c.seeded:
                c.seeded = True
                if self.active("floatstoneBloomEnabled") or "bloom_off_ignored" in self.brk:
                    self.seed(c)
        elif p == "Cracks":
            self.crack_all(c)
        elif p == "Melt":
            self.melt(c, gentle=self.gentle(), batch=len(c.frozen))

    def gentle(self):
        """The melt spares what stands on the crust when meltBackDestroys is off (the toggle-ignored break always destroys)."""
        return False if "melt_gentle_ignored" in self.brk else not self.active("meltBackDestroys")

    def freeze_all(self, c):
        cells = [x for x in self.lava_cells() if x not in self.temp]
        if "freeze_partial" in self.brk:
            cells = cells[: len(cells) // 2]
        for x in cells:
            self.temp[x] = "RM_BasaltShingle"
            c.frozen.add(x)
            c.c["cellsFrozen"] += 1
        if "lava_touched" in self.brk:
            for x in cells[:3]:
                self.terrain[x] = "Soil"

    def seed(self, c):
        if "no_gardens" in self.brk:
            return
        cells = sorted(c.frozen)[: 7]
        for x in cells:
            self.things.setdefault(x, []).append("RM_FloatstoneGarden")
            c.c["gardensSpawned"] += 1

    def drift_gardens(self, c):
        n = 0
        for x in list(self.things):
            while "RM_FloatstoneGarden" in self.things[x]:
                self.things[x].remove("RM_FloatstoneGarden")
                n += 1
        if "garden_vanish" not in self.brk:
            c.c["gardensDrifted"] += n

    def live_gardens(self):
        return sum(ds.count("RM_FloatstoneGarden") for ds in self.things.values())

    def crack_all(self, c):
        for x in list(c.frozen):
            if self.temp.get(x):
                self.temp[x] = "RM_GlowingCrackCrust"

    def melt(self, c, gentle, batch):
        if "melt_keeps_crust" in self.brk and not gentle:
            batch = max(0, batch - 3)
        n = 0
        for x in sorted(c.frozen):
            if n >= batch:
                break
            n += 1
            c.frozen.discard(x)
            c.c["cellsMelted"] += 1
            self.temp.pop(x, None)
            ds = self.things.get(x, [])
            if not gentle:
                for d in list(ds):
                    if d in ("RM_FloatstoneGarden",):
                        continue
                    ds.remove(d)
                    if "melt_silent" not in self.brk:
                        c.c["meltDestroyed"] += 1
                for pw in list(self.pawns):
                    if (pw["x"], pw["z"]) == x:
                        pw["dead"] = True
                        self.pawns.remove(pw)
                        if "melt_silent" not in self.brk:
                            c.c["meltPawnsBurned"] += 1
                            c.c["meltDestroyed"] += 1
            else:
                for d in list(ds):
                    if d in ("RM_FloatstoneGarden",):
                        continue
                    ds.remove(d)
                    self.things.setdefault((x[0] + 9, x[1]), []).append(d)
                    c.c["meltRelocated"] += 1
                for pw in self.pawns:
                    if (pw["x"], pw["z"]) == x:
                        pw["x"] += 9
                        c.c["meltRelocated"] += 1

    def enter(self, c, nxt, now):
        c.phase = nxt
        c.end = now + LEN[nxt]
        if nxt == "StillHeat":
            c.hiss = False
            c.seeded = False
        elif nxt == "GasWash":
            c.gas_left = 2 if (self.active("gasWashEnabled") or "gas_off_ignored" in self.brk) else 0
            c.next_gas = now
        elif nxt == "Rain":
            if self.settings[V.HAZ_SETTINGS]["weatherPulseEnabled"] == "True":
                c.burst = True
                c.burst_end = now + LEN["Rain"]
                self.flash = (now, now + 5000)
            c.floods_left = 3
            c.next_flood = now + 1250
        elif nxt == "Freeze":
            if not c.frozen and (self.active("lavaFreezeEnabled") or "freeze_off_ignored" in self.brk) and self.lava_cells():
                self.emit(V.LETTERS["Freeze"])
        elif nxt == "Growth":
            self.flash = (now, c.end)
        elif nxt == "Cracks":
            self.drift_gardens(c)
            if c.frozen:
                self.emit(V.LETTERS["Cracks"])
        elif nxt == "Melt":
            if c.frozen:
                self.emit(V.LETTERS["Melt"])

    def advance(self, c, now):
        p = c.phase
        if p == "Freeze":
            nxt = "Growth" if c.frozen else "StillHeat"
        elif p == "Melt":
            if c.frozen:
                self.melt(c, gentle=self.gentle(), batch=len(c.frozen))
            nxt = "StillHeat"
            c.c["cycles"] += 1
        else:
            nxt = NEXT[p]
        self.enter(c, nxt, now)

    def debug_advance(self):
        c, now = self.cyc, self.ticks
        if c.end < 0:
            self.enter(c, "StillHeat", now)
            return
        if c.phase == "Freeze" and (self.active("lavaFreezeEnabled") or "freeze_off_ignored" in self.brk):
            self.freeze_all(c)
        elif c.phase == "Growth" and not c.seeded:
            c.seeded = True
            if self.active("floatstoneBloomEnabled") or "bloom_off_ignored" in self.brk:
                self.seed(c)
        elif c.phase == "Cracks":
            self.crack_all(c)
        self.advance(c, now)

    def report_line(self):
        c = self.cyc
        k = c.c
        return ("phase=%s endsIn=%d inBurst=%s frozen=%d gardensLive=%d cycles=%d gasIgnitions=%d floods=%d "
                "cellsFrozen=%d cellsMelted=%d gardensSpawned=%d gardensDrifted=%d meltDestroyed=%d "
                "meltPawnsBurned=%d meltRelocated=%d" % (
                    c.phase, c.end - self.ticks, c.burst, len(c.frozen), self.live_gardens(), k["cycles"],
                    k["gasIgnitions"], k["floods"], k["cellsFrozen"], k["cellsMelted"], k["gardensSpawned"],
                    k["gardensDrifted"], k["meltDestroyed"], k["meltPawnsBurned"], k["meltRelocated"]))

    # ------------------------------------------------------------ game conditions & weather
    def t_jawa_game_condition(self, p):
        if p.get("condition") != V.COND:
            return {"success": False}
        if p.get("action") == "start":
            self.cond = True
            self.cyc = FGame.Cyc()
        else:
            self.cond = False
            self.cyc = None
        return {"success": True}

    def t_jawa_weather_get(self, p):
        w = "RM_ForgeStill"
        if self.cond and self.cyc is not None and self.cycle_active():
            if self.cyc.burst:
                w = "RM_BoilingRain" if "rain_wrong_weather" not in self.brk else "RM_ForgeStill"
            elif self.cyc.phase == "Freeze":
                w = "Fog"
        conds = [{"def": V.COND, "scope": "map", "affectsThisMap": True}] if self.cond else []
        return {"success": True, "weather": {"current": w}, "conditions": conds}

    def t_jawa_letter_list(self, p):
        return {"success": True, "count": len(self.letters), "letters": [{"label": l} for l in self.letters]}

    def t_rimworld_list_messages(self, p):
        return {"success": True, "messages": [{"text": m} for m in self.messages]}

    # --------------------------------------------------------------------- the debug actions
    def t_rimworld_list_debug_action_children(self, p):
        if p.get("path") == "Actions":
            return {"success": True, "children": [{"label": "RMTheForge", "path": "Actions\\RMTheForge"},
                                                  {"label": "Other", "path": "Actions\\Other"}]}
        return {"success": True, "children": [
            {"label": "Forge cycle: report state (current map)", "path": "Actions\\RMTheForge\\report"},
            {"label": "Forge cycle: advance one phase (current map)", "path": "Actions\\RMTheForge\\advance"},
            {"label": "Spunstone: report knowledge", "path": "Actions\\RMTheForge\\spun_report"},
            {"label": "Spunstone: reveal now", "path": "Actions\\RMTheForge\\spun_reveal"}]}

    def log(self, line):
        if "log_cap" in self.brk:
            return {"success": True, "effects": {"logCount": 0, "logs": []}}
        return {"success": True, "effects": {"logCount": 1, "logs": [{"message": line}]}}

    def hidden(self):
        if self.spun_revealed or not self.active("spunstoneStudyEnabled"):
            return False
        return "project_visible" not in self.brk

    def t_rimworld_execute_debug_action(self, p):
        path = p.get("path", "")
        if path.endswith("\\report") or path.endswith("\\advance"):
            if not self.cond or self.cyc is None:
                return self.log("[RMTheForgeDebug] no RM_GameCondition_ForgeCycle active on this map.")
            if path.endswith("\\advance"):
                self.debug_advance()
                return self.log("[RMTheForgeDebug] advanced. " + self.report_line())
            return self.log("[RMTheForgeDebug] " + self.report_line())
        if path.endswith("spun_reveal"):
            if not self.spun_revealed and "reveal_noop" not in self.brk:
                self.spun_revealed = True
                self.letters.append("Spunstone bonding")
        return self.log("[RMTheForgeDebug] spunstone points=0 revealed=%s projectHidden=%s canStart=False" % (
            self.spun_revealed, self.hidden()))

    def t_jawa_research_availability(self, p):
        return {"success": True, "isFinished": False, "isHidden": self.hidden()}

    # ------------------------------------------------------------------------- terrain
    def t_jawa_get_terrain_layers(self, p):
        x, z, w, h = [int(v) for v in str(p["rect"]).split(",")]
        cells = [{"x": cx, "z": cz, "top": self.terrain.get((cx, cz), "Soil"), "temp": self.temp.get((cx, cz))}
                 for cx in range(x, x + w) for cz in range(z, z + h)]
        return {"success": True, "cellsScanned": len(cells), "cellsMatchingFilter": len(cells), "returned": len(cells),
                "truncated": False, "cells": cells}

    def t_rimworld_get_cell_info(self, p):
        xz = (p["x"], p["z"])
        walk = self.terrain.get(xz, "Soil") != "LavaDeep" or bool(self.temp.get(xz))
        return {"success": True, "cell": {"walkable": walk, "things": []}}

    # ------------------------------------------------------------------------ pawns & things
    def t_jawa_set_plants(self, p):
        for op in str(p["ops"]).split(";"):
            name, rect = op.split(":")
            x, z, w, h = [int(v) for v in rect.split(",")]
            for cx in range(x, x + w):
                for cz in range(z, z + h):
                    self.things.setdefault((cx, cz), []).append(name)
        return {"success": True}

    def t_jawa_spawn_pawn(self, p):
        self.n_id += 1
        pid = "%s%d" % (p["kindDef"], self.n_id)
        fac = None if p.get("faction") == "none" else "Player"
        row = {"id": pid, "kindDef": p["kindDef"], "x": p["x"], "z": p["z"], "faction": fac, "dead": False,
               "awake": True, "awake_since": -1, "init": False, "hediffs": []}
        self.pawns.append(row)
        return {"success": True, "pawns": [{"id": pid}]}

    def t_jawa_list_pawns(self, p):
        rows = []
        for q in self.pawns:
            if p.get("rect"):
                x, z, w, h = [int(v) for v in str(p["rect"]).split(",")]
                if not (x <= q["x"] < x + w and z <= q["z"] < z + h):
                    continue
            r = {"id": q["id"], "kindDef": q["kindDef"], "x": q["x"], "z": q["z"], "dead": q["dead"]}
            if p.get("includeHealth"):
                r["health"] = {"hediffs": [{"def": h} for h in q["hediffs"]]}
            rows.append(r)
        return {"success": True, "pawns": rows}

    def t_jawa_ordered_job(self, p):
        if p.get("jobDef") == "Harvest" and "harvest_noop" not in self.brk:
            d, rest = p["targetAId"].split("#", 1)
            cx, cz = [int(v) for v in rest.split("_")]
            if d in self.things.get((cx, cz), []):
                self.things[(cx, cz)].remove(d)
                self.things[(cx, cz)].append("RM_Floatstone")
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    # ---------------------------------------------------------------------- creatures
    def flash_open(self, now):
        return self.flash[0] <= now < self.flash[1]

    def raining(self):
        c = self.cyc
        if not self.cond or c is None:
            return False
        return c.burst or (self.cycle_active() and c.phase == "Rain")

    def want_awake(self, pw, now):
        if "rain_not_waking" in self.brk and self.raining() and pw["kindDef"] == "RM_Julmox":
            return False
        if self.raining():
            return True
        if pw["kindDef"] in ("RM_Julmox", "RM_Dhuvvox") and self.flash_open(now) and "julmox_seals_flash" not in self.brk:
            return True
        if (pw["kindDef"] == "RM_Dhokkur" and "dhokkur_stays_awake_dry" in self.brk and self.cyc is not None
                and self.cyc.phase == "Growth"):
            return True
        return False

    def run_end(self, pw):
        now = self.ticks
        if self.flash_open(now):
            return self.flash[1]
        c = self.cyc
        if c is not None and self.cycle_active() and c.phase == "Rain":
            return c.end
        return -1

    def clock_on(self, pw):
        return pw["kindDef"] == "RM_Dhuvvox" and (self.active("dhuvvoxClockEnabled") or "clock_off_ignored" in self.brk)

    def dorm_check(self, pw, now):
        enabled = True if "dormancy_off_ignored" in self.brk else self.active("cycleDormancyEnabled")
        want = (not enabled) or self.want_awake(pw, now)
        if "never_seal" in self.brk:
            return
        if not pw["awake"]:
            if want:
                pw["awake"] = True
                pw["awake_since"] = now
            return
        first = not pw["init"]
        pw["init"] = True
        if pw["awake_since"] < 0:
            pw["awake_since"] = now
        # the dhuvvox slowing hediff (UpdateSlowing)
        if pw["kindDef"] == "RM_Dhuvvox":
            want_slow = False
            if self.clock_on(pw) and want:
                end = self.run_end(pw)
                left = end - now
                want_slow = end > 0 and 0 < left <= SLOW_LEFT
            has = "RM_DhuvvoxRunSlowing" in pw["hediffs"]
            if want_slow and not has:
                pw["hediffs"].append("RM_DhuvvoxRunSlowing")
            elif not want_slow and has:
                pw["hediffs"].remove("RM_DhuvvoxRunSlowing")
        if want:
            return
        if not first and now - pw["awake_since"] < MIN_AWAKE:
            return
        pw["awake"] = False
        pw["awake_since"] = -1

    def t_jawa_inspect_string(self, p):
        rows = []
        for tid in str(p.get("thingIds") or "").split(","):
            pw = next((q for q in self.pawns if q["id"] == tid), None)
            if pw is None:
                continue
            lines = []
            shown = self.active("cycleDormancyEnabled") or "dormancy_off_ignored" in self.brk
            if shown and not pw["awake"]:
                lines.append("Sealed, waiting out the dry.")
            elif pw["kindDef"] == "RM_Dhuvvox" and self.clock_on(pw) and "no_clock_text" not in self.brk:
                end = self.run_end(pw)
                left = end - self.ticks
                if end >= 0 and left > 0:
                    lines.append("Run ends in %d ticks, then it curls back into its nodule." % left)
                    if left <= SLOW_LEFT:
                        lines.append("Slowing.")
            rows.append({"id": tid, "defName": pw["kindDef"], "inspect": lines, "error": None})
        return {"success": True, "things": rows}

    # ---------------------------------------------------------------------- settings
    def t_jawa_mod_settings_field(self, p):
        store = self.settings.get(p.get("typeName"))
        if store is None:
            return {"success": False, "message": "no such type"}
        a = p.get("action")
        if a == "list":
            return {"success": True, "fields": [{"name": k, "value": v} for k, v in store.items()]}
        f = p.get("field")
        if f not in store:
            return {"success": False, "message": "no field"}
        if a == "set":
            store[f] = str(p.get("value"))
        return {"success": True, "value": store[f]}

    def t_rimworld_open_mod_settings(self, p):
        return {"success": True}

    def t_jawa_window_list_close(self, p):
        # RM_TheForgeMod.WriteSettings -> RM_KeelworkUtility.ApplySetting
        on = self.S("keelworkEnabled") and self.S("modEnabled")
        if "keel_apply_garbled" in self.brk:
            self.keel = 0.2 if not on else 0.05
        else:
            self.keel = 0.05 if on else 0.0
        return {"success": True}

    # ---------------------------------------------------------------------------- defs
    def t_jawa_get_defs(self, p):
        rows, nf = [], []
        want = [f for f in (p.get("fields") or "").split(",") if f]
        specs = [s for s in str(p.get("defs") or "").split(";") if s]
        for spec in specs:
            typ, name = spec.split("/", 1)
            pkg = self.known.get((typ, name))
            if pkg is None and (typ, name) == ("BiomeDef", V.BIOME):
                pkg = "mandrake.rm.biomes"
            if pkg is None:
                rows.append({"requested": spec, "found": False, "defName": name})
                nf.append(spec)
                continue
            rows.append({"requested": spec, "found": True, "defName": name, "defType": typ, "packageId": pkg,
                         "fields": self._fields(typ, name, want)})
        return {"success": True, "requested": len(specs), "foundCount": len(specs) - len(nf), "notFound": nf,
                "defs": rows}

    def _fields(self, typ, name, want):
        f = {}
        if typ == "TerrainDef":
            f = {"temporary": not (name == "RM_PumiceRubble" and "terrain_not_temporary" in self.brk), "walkable": True}
        elif name in V.DORMANT_NATIVES:
            comps = [{"Class": "CompProperties_CanBeDormant", "startsDormant": True,
                      "jobDormancy": "no_jobdormancy" not in self.brk}]
            if "no_forge_comp" not in self.brk:
                comps.append({"Class": "RimMandrake.TheForge.CompProperties_ForgeCycleDormancy", "awakeDuringRain": True})
            f = {"comps": comps}
        elif name in V.FLYERS:
            sb = [{"stat": "MaxFlightTime", "value": 0.0 if "flyer_no_stat" in self.brk else 15.0}]
            f = {"statBases": sb}
        elif name == "RM_Floatstone":
            f = {"generateCommonality": 1.0 if "floatstone_generated" in self.brk else 0.0, "tradeability": "All"}
        elif name == "RM_FloatstoneKeelBrace":
            f = {"researchPrerequisites": [] if "brace_no_research" in self.brk else ["RM_SpunstoneBonding"],
                 "comps": [{"Class": "CompProperties_GravshipFacility", "fuelSavingsPercent": self.keel,
                            "maxSimultaneous": 4}]}
        elif name == "GravEngine":
            links = ["Foo"] + ([] if "engine_unlinked" in self.brk else ["RM_FloatstoneKeelBrace"])
            f = {"comps": [{"Class": "CompProperties_AffectedByFacilities", "linkableFacilities": links}]}
        elif typ == "BiomeDef":
            f = {"biomeMapConditions": [] if "no_map_condition" in self.brk else [V.COND],
                 "modExtensions": [{"Class": "RM_TheForgeBiomeRanges"}] + ([] if "no_heat_ext" in self.brk else
                                                                          [{"Class": "RM_SunHeatExtension", "heatKind": "ambient"}]),
                 "terrainPatchMakers": [{"thresholds": [{"terrain": "CooledLava"}] + ([] if "no_lava_patch" in self.brk
                                                                                    else [{"terrain": "LavaDeep"}])}]}
        return dict((k, v) for k, v in f.items() if not want or k in want)

    def t_jawa_biome_probe(self, p):
        def live(roster, drop=None, zero=None):
            out = []
            for n, (c, req) in sorted(roster.items()):
                if req and req not in V.ACTIVE_ON_TIER:
                    continue
                if n == drop:
                    continue
                out.append({"defName": n, "commonality": 0.0 if n == zero else c})
            return out
        animals = live(V.BIOME_ANIMALS, zero="RM_Julmox" if "roster_zero" in self.brk else None)
        plants = live(V.BIOME_PLANTS, drop="RM_FireLavender" if "plant_row_missing" in self.brk else None)
        find = []
        for f in [f for f in str(p.get("find") or "").split(",") if f]:
            spawning = f in [a["defName"] for a in animals]
            find.append({"defName": f, "state": "spawning" if spawning else "absent"})
        return {"success": True, "biomes": [{
            "defName": p.get("biomes"),
            "animalDensity": 0.0 if "zero_density" in self.brk else V.BIOME_SCALARS.get("animalDensity"),
            "plantDensity": V.BIOME_SCALARS.get("plantDensity"),
            "wildAnimalCount": len(animals), "animalsListed": len(animals), "animals": animals,
            "wildPlantCount": len(plants), "plantsListed": len(plants), "plants": plants,
            "findResults": find}]}


SET_FORGE = V.SETTINGS


def _s(v):
    return str(v)


def run(brk=(), log_lines=()):
    fd, path = tempfile.mkstemp(suffix=".log")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("Bridge token: x\n" + "\n".join(log_lines) + "\n")
    saved = getattr(game_paths, "PLAYER_LOG", None)
    game_paths.PLAYER_LOG = path
    saved_mesh = dict(V.PLANT_MESH)
    if "bad_mesh" in brk:
        V.PLANT_MESH["RM_CinderCrust"] = "6"
    V._ACTIONS.clear()
    try:
        game = FGame(brk)
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(V.suite, s, anchor=(75, 75), mod=None)
    finally:
        game_paths.PLAYER_LOG = saved
        V.PLANT_MESH.clear()
        V.PLANT_MESH.update(saved_mesh)
        os.unlink(path)
    out = {}
    for ch in res["chains"]:
        for c in ch["components"]:
            out["%s.%s" % (ch["name"], c["name"])] = (c["verdict"], c.get("detail") or "")
    return out


def reds(result):
    return sorted(k for k, (v, _) in result.items() if v == "FAIL")


def unmeasured(result):
    return sorted(k for k, (v, _) in result.items() if v == "UNMEASURED")


def main():
    # -- the instrument itself ------------------------------------------------------------------
    check("source parse is clean", not V._ERRORS, V._ERRORS)
    for group, _, names, floor in V.GROUPS:
        check("floor met: %s (%d >= %d)" % (group, len(names), floor), len(names) >= floor)
    check("seven phases derived from the enum", V.PHASES == ["StillHeat", "GasWash", "Rain", "Freeze", "Growth",
                                                             "Cracks", "Melt"], V.PHASES)
    check("20 settings fields derived from the C#", len(V.SETTINGS_DEFAULTS) == 20, sorted(V.SETTINGS_DEFAULTS))
    check("every wired toggle is a real settings field", set(V.WIRED) <= set(V.SETTINGS_DEFAULTS),
          sorted(set(V.WIRED) - set(V.SETTINGS_DEFAULTS)))
    check("the five scaffolding fields are exactly the unwired remainder", len(V.SCAFFOLDING) == 5, V.SCAFFOLDING)
    check("every phase has a cue text", sorted(V.CUE_TEXT) == sorted(V.PHASES), sorted(V.CUE_TEXT))
    cs = open(os.path.join(HERE, "Source", "RM_GameCondition_ForgeCycle.cs"), encoding="utf-8").read()
    check("every report token is printed by DebugStateReport",
          all(("%s=" % k) in cs.replace('" ', "").replace('"', "") or ("%s=" % k) in cs for k in V.REPORT_TOKENS),
          [k for k in V.REPORT_TOKENS if ("%s=" % k) not in cs])
    check("the debug action category is RMTheForge",
          'private const string CAT = "RMTheForge"' in open(os.path.join(HERE, "Source", "RM_ForgeCycleDebugActions.cs"),
                                                              encoding="utf-8").read())
    for lab in ("Forge cycle: report state", "Forge cycle: advance one phase", "Spunstone: report knowledge",
                "Spunstone: reveal now"):
        check("debug action label exists in the C#: %s" % lab,
              lab in open(os.path.join(HERE, "Source", "RM_ForgeCycleDebugActions.cs"), encoding="utf-8").read())
    check("the letter labels are in the C#", all(
        ('"%s"' % v) in cs for v in V.LETTERS.values()), [v for v in V.LETTERS.values() if ('"%s"' % v) not in cs])
    decl = V.suite.components_declared()
    check("the Mod Settings toggle floor is met (%d toggles)" % len(V.suite.toggles),
          set(V.suite.toggles) <= set(c["toggle"] for c in decl if c["toggle"]),
          sorted(set(V.suite.toggles) - set(c["toggle"] for c in decl if c["toggle"])))

    # -- healthy world: every component passes --------------------------------------------------
    healthy = run()
    check("healthy: %d components all PASS" % len(healthy),
          healthy and all(v == "PASS" for v, _ in healthy.values()),
          {k: v for k, v in healthy.items() if v[0] != "PASS"})

    # -- each break turns its own component red -------------------------------------------------
    W = "cycle_walk."
    A = "cycle_arms."
    cases = [
        ("missing_def", {"defs_resolve.defs_resolve_items"}),
        ("donor_shadow", {"defs_resolve.defs_resolve_plants"}),
        ("bad_mesh", {"defs_resolve.plants_mesh_count_is_perfect_square"}),
        ("terrain_not_temporary", {"defs_resolve.cycle_terrains_are_temporary"}),
        ("no_scald_def", {"defs_resolve.scald_damage_def_resolves"}),
        ("no_jobdormancy", {"def_wiring.native_dormancy_comps_wired"}),
        ("no_forge_comp", {"def_wiring.native_dormancy_comps_wired"}),
        ("flyer_no_stat", {"def_wiring.flyers_carry_flight_stat"}),
        ("floatstone_generated", {"def_wiring.floatstone_only_from_gardens"}),
        ("brace_no_research", {"def_wiring.keel_brace_needs_spunstone_research"}),
        ("engine_unlinked", {"def_wiring.engine_links_keel_brace"}),
        ("zero_density", {"biome_wiring.biome_densities_live"}),
        ("roster_zero", {"biome_wiring.wild_animals_wired"}),
        ("plant_row_missing", {"biome_wiring.wild_plants_wired"}),
        ("no_map_condition", {"biome_wiring.biome_map_condition_is_forge_pulse"}),
        ("no_heat_ext", {"biome_wiring.biome_declares_ambient_heat"}),
        ("no_lava_patch", {"biome_wiring.biome_lava_patchmakers"}),
        ("settings_drift", {"settings.settings_at_shipped_defaults"}),
        ("no_gas", {W + "gas_wash_ignites"}),
        ("no_flood", {W + "rain_forces_boiling_weather_and_floods"}),
        ("rain_wrong_weather", {W + "rain_forces_boiling_weather_and_floods"}),
        ("freeze_partial", {W + "freeze_crusts_lava", A + "bloom_off_no_gardens"}),   # both read the crust count
        ("lava_touched", {W + "freeze_crusts_lava", A + "bloom_off_no_gardens"}),
        ("no_gardens", {W + "growth_blooms_floatstone"}),
        ("garden_vanish", {W + "cracks_drift_gardens_and_glow"}),
        # a leaked crust also reddens every later chain's site setup: the precondition names the cause
        ("melt_keeps_crust", {W + "melt_restores_lava_and_counts_losses", A + "site_ready_arms",
                              "still_heat_hiss.site_ready_hiss", "voices.site_ready_voices",
                              "dormancy.site_ready_dormancy", "floatstone_harvest.site_ready_harvest"}),
        ("melt_silent", {W + "melt_restores_lava_and_counts_losses"}),
        ("no_letters", {W + "telegraph_letters_sent", "still_heat_hiss.hiss_letter_sent_before_gas_wash"}),
        ("gas_off_ignored", {A + "gas_wash_off_no_ignitions"}),
        ("flood_off_ignored", {A + "flooding_off_no_floods"}),
        ("freeze_off_ignored", {A + "freeze_off_closes_cycle_early"}),
        ("bloom_off_ignored", {A + "bloom_off_no_gardens"}),
        ("melt_gentle_ignored", {A + "melt_gentle_spares_pawn_and_items"}),
        ("telegraph_off_ignored", {A + "telegraph_off_sends_no_letters"}),
        ("gate_pulse_ignored", {A + "cycle_gate_off_pulse_toggle_never_starts"}),
        ("gate_grand_ignored", {A + "cycle_gate_off_grand_cycle_toggle_never_starts", A + "cycle_off_melts_back_gently"}),
        ("no_hiss", {"still_heat_hiss.hiss_letter_sent_before_gas_wash"}),
        ("hiss_ignores_gas_toggle", {"still_heat_hiss.hiss_not_sent_with_gas_wash_off"}),
        ("never_seal", {"dormancy.natives_seal_in_still_heat", "dormancy.fresh_natives_seal"}),
        ("dormancy_off_ignored", {"dormancy.dormancy_off_clears_sealed_line"}),
        ("rain_not_waking", {"dormancy.rain_wakes_all_natives"}),
        ("no_clock_text", {"dormancy.dhuvvox_clock_shows_countdown_and_slows"}),
        ("clock_off_ignored", {"dormancy.clock_off_removes_slowing"}),
        ("dhokkur_stays_awake_dry", {"dormancy.dry_growth_seals_dhokkur_only"}),
        ("julmox_seals_flash", {"dormancy.dry_growth_seals_dhokkur_only"}),
        ("voices_off_ignored", {"voices.voices_off_no_cue"}),
        ("no_cue", {"voices.visual_cue_message_names_phase"}),
        ("project_visible", {"spunstone.project_hidden_until_studied"}),
        ("reveal_noop", {"spunstone.reveal_opens_project"}),
        ("harvest_noop", {"floatstone_harvest.floatstone_garden_yields_floatstone"}),
        ("keel_wrong", {"keelwork.keel_default_saving"}),
        ("keel_apply_garbled", {"keelwork.keel_off_zeroes_saving"}),
    ]
    for brk, want in cases:
        got = reds(run((brk,)))
        check("break %-26s reddens exactly %s" % (brk, sorted(want)), set(got) == want, "got %s" % got)

    # breaks whose effect is a broken instrument or a harness limit read UNMEASURED, never a pass and never a red
    un = unmeasured(run(("log_cap",)))
    check("break log_cap: every debug-action component is UNMEASURED, none PASS",
          "cycle_walk.cycle_starts_in_still_heat" in un and not reds(run(("log_cap",))), un[:6])

    # the log chain: an error line naming our content fails it; an unrelated game-wide error does not
    for line, label in (("Config error in RM_Dhokkur: lifeStages count mismatch", "a config error naming RM_Dhokkur"),
                        ("RM_CinderCrust must have plant.MaxMeshCount that is a perfect square.", "the mesh-count error"),
                        ("Could not resolve cross-reference to RimWorld.DamageDef named RUT_Scald (RM_ForgePulse)",
                         "a dangling cross-reference naming RM_ForgePulse")):
        bad = run(log_lines=[line])
        check("break log: %s reddens only the log component" % label,
              reds(bad) == ["log_clean.player_log_names_no_forge_error"], reds(bad))
    other = run(log_lines=["Config error in SomeOtherMod_Thing: unrelated"])
    check("an error naming only another mod does not", not reds(other), reds(other))
    capped = run(log_lines=["Reached max messages limit. Stopping logging to avoid spam."])
    check("a log that hit RimWorld's message cap reads UNMEASURED, not PASS",
          capped["log_clean.player_log_names_no_forge_error"][0] == "UNMEASURED", capped["log_clean.player_log_names_no_forge_error"])

    print()
    if FAILS:
        print("FAILED: %d" % len(FAILS))
        for f in FAILS:
            print("  - " + f)
        return 1
    print("all TheForge suite selftests passed (%d breaks)" % (len(cases) + 6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
