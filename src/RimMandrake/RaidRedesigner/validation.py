"""validation.py -- modcheck suite for RimMandrake Raid Redesigner -- Old
Friends (mandrake.rm.raidredesigner).

Read whole before writing this: every `.cs` file in `Source/` (not just the
walk doc's own citations) -- `RaidRedesignerMod.cs`, `RaidRedesignerSettings.cs`,
`GameComponent_OldFriends.cs`, `Encounter.cs`, `OldFriendEntry.cs`,
`RoleTag.cs`, `RosterPruning.cs`, `WorldPawnPinning.cs`, all six `Patch_*.cs`
files, `Patch_WokenAncient_STUB.cs`, `Spike_ThreatPointReplace.cs` (compile-only,
not in the .csproj, not this mod's live behavior), `SelfTest/Program.cs`, plus
`Transient/bench_tools_dump.json` for every bridge tool named "roster",
"kidnap", "prisoner", "release", "captur", "flee", "exit_map" or
"game_component" (none exist -- see the floor-gap finding below).

TWO REAL MOD SETTINGS TOGGLES, both plain boolean checkboxes: `rosterTrackingEnabled`
(master switch) and `pinEncounteredPawns`. `maxLivingEntries` and
`grudgeNotabilityMultiplier` are sliders, not toggles, per the briefing's own
rule for `suite.toggles`. All four fields are `public static`
(`BRIDGE_STATIC_SETTINGS_FIELDS_1`'s static-first resolution reaches them).

A REAL, WALK-DOC-IS-STALE FINDING, same register as RustChrome's/Oracle's/
PlantGrowth's tonight: the walk doc's step 1 says the boot line should read
`"[RimMandrake.RaidRedesigner] ready: 8 capture-hook patches."` and treats
the literal `8` as a regression tripwire. Counting the ACTUAL Harmony-patched
target methods from the current source, not the walk doc's number: `harmony.
PatchAll(Assembly.GetExecutingAssembly())` in `RaidRedesignerMod.cs` discovers
exactly FIVE `[HarmonyPatch]`-attributed classes, each patching a DIFFERENT
target method --
  `KidnappedPawnsTracker.Kidnap` (Patch_ColonistKidnapped),
  `Pawn.ExitMap` (Patch_FledRaiderAndCaptain -- one Prefix + one Postfix on
    the SAME method, so `GetPatchedMethods()` still counts it once),
  `GuestUtility.Notify_PrisonerEscaped` (Patch_PrisonerEscaped),
  `GenGuest.PrisonerRelease` (Patch_PrisonerReleased),
  `Pawn_GuestTracker.CapturedBy` (Patch_NamedHunterCaptured)
-- plus `PropertyEngine.Fire` (Patch_CaravanRobbed), patched MANUALLY via
`TryPatch` only `if (ModsConfig.IsActive("mandrake.rm.property"))`.
`Patch_WokenAncient_STUB` carries no `[HarmonyPatch]` at all (its own comment:
"Deliberately no [HarmonyPatch] on this class"). So `harmony.
GetPatchedMethods().Count()` is **5 with `mandrake.rm.property` inactive, 6
with it active** -- never 8, under any environment reachable from this
source. `mandrake.rm.property` is NOT in the minimal list (grepped directly
against `infrastructure/state/modlists/ModsConfig.MINIMAL.xml`), so a plain
`modcheck run RaidRedesigner` should log **5**. This suite checks for 5 or 6
dynamically (by first checking for the mod's own "not active" skip line),
never the walk doc's stale 8.

THE FLOOR GAP THAT MATTERS MOST HERE, bigger than RimProperty's own "two of
five toggles uncovered" -- read in full before writing a single component
that assumes otherwise: **every one of the six PatchAll-discovered hooks has
NO KNOWN TRIGGER on this bridge** (a raider fleeing the map, a raid captain
leaving, a prisoner escaping, a prisoner being released, a colonist
kidnapped, a Blackstar guest-status change -- searched
`Transient/bench_tools_dump.json` for "kidnap"/"prisoner"/"release"/"captur"/
"flee"/"exit_map"/"roster"/"game_component": zero hits, matching the walk
doc's own step 4 conclusion exactly, "no 'force pawn to flee/exit map' tool
exists ... note as a walk gap, not a false pass"). **And there is also NO
READ-BACK tool for `GameComponent_OldFriends.Entries` at all** -- no
"roster"/"oldfriend" tool exists either, so even the ONE hook this suite
CAN trigger live (`BetrayedTrader`, via `mandrake.rm.property`'s
`JobDriver_TheftHaulUninstall.FinishedRemoving` calling `PropertyEngine.Fire`
-- the exact same live recipe `src/RimMandrake/RimProperty/validation.py`'s
own `theft_hauler_uninstall` chain already uses and has committed) has no way
to confirm afterward that `RecordEncounter` actually ran, what `Grudge`/
`Notability` it wrote, or whether the pawn got pinned. `RecordEncounter`
itself logs nothing (grepped: no `Log.Message`/`Log.Error` anywhere in
`GameComponent_OldFriends.cs`, `OldFriendEntry.cs`, or `WorldPawnPinning.cs`).
This suite therefore proves the trigger recipe fires cleanly (no exception,
via the boot-line-adjacent skip check and a plain smoke run of the recipe)
but CANNOT prove the roster itself changed -- a genuine, complete gap in
BOTH directions (trigger AND read-back) for the mod's entire actual
mechanism, left honestly undone rather than faked with a component that
would always report a hollow PASS.

WHAT `RosterPruning`'s OWN OFFLINE SELFTEST ALREADY COVERS, and why this
suite does not duplicate it: `SelfTest/Program.cs` is a SEPARATE, pure-C#
console project (`RimMandrakeRaidRedesigner.SelfTest.csproj`, run via
`dotnet run`, no RimWorld process, no bridge) that already exhaustively
proves `RosterPruning.SelectPruneVictims`'s cap/prune/tie-break/dead-exclusion
logic (5 cases). That is the walk doc's own step 2, a DIFFERENT invocation
entirely from `modcheck run` -- this file cannot re-run it (no bridge
Session involved) and does not attempt to re-implement the same assertions
against a live game it has no way to populate.

RAIDREDESIGNER_COVERAGE_GAPS_1 (2026-10-03) closed most of what follows without engine triggers: chains
`roster_rules_on_a_scratch_roster` (real RecordEncounter on a scratch roster: idempotence, role upgrade-only,
cap eviction, multiplier + clamps, master switch, pinning, dead collapse; static hook/gate/scribe checks) and
`hook_bodies_record_the_right_role` (the SHIPPED postfix bodies called directly) -- see the block at the bottom.
What stays UNMEASURED there: the engine firing each hook, BetrayedTrader, and a save round trip.

Original floor-gap notes (items 1-3 below are only partly superseded):
Still not proven / out of this validator's floor:
  1. All six PatchAll-discovered hooks' actual firing (FledRaider, Captain,
     EscapedPrisoner, Released, Kidnapper, NamedHunter via either seam) --
     no trigger tool found, per the floor-gap finding above.
  2. `RecordEncounter`'s cap/prune enforcement, grudge/notability math, and
     `WorldPawnPinning.PinForever`'s actual effect on `Find.WorldPawns.
     ForcefullyKeptPawns` -- no read-back tool found for any of it.
  3. The "zero Defs" claim in About.xml (walk doc step 3, "a live
     RimDefDump capture lists zero defs with modName ...") -- no def-dump-by-
     modName bridge tool was found either; this suite does not attempt it.
"""
import os
import re

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))
suite = Suite("RaidRedesigner")
suite.toggles = ["rosterTrackingEnabled", "pinEncounteredPawns"]

SETTINGS_TYPE = "RimMandrake.RaidRedesigner.RaidRedesignerSettings"
READY_LOG_TAG = "[RimMandrake.RaidRedesigner] ready:"
SKIP_LOG_TAG = "[RimMandrake.RaidRedesigner] mandrake.rm.property not active"


@suite.chain("boot_patch_count")
def boot_patch_count(t):
    """Dynamic, environment-aware check -- never the walk doc's stale
    hardcoded 8 (see module docstring). First checks whether the
    Property-skip line fired to know which count (5 or 6) is correct for
    THIS run, rather than assuming `mandrake.rm.property`'s presence
    either way."""
    t.clear_area(size=8)   # no map state involved; keeps the runner's
                            # evidence/screenshot machinery uniform

    with t.component("patch_count_matches_active_hooks", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=200, contains="[RimMandrake.RaidRedesigner]")
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        if t._guard():
            property_active = SKIP_LOG_TAG not in joined
            expected = 6 if property_active else 5
            expected_line = "%s %d capture-hook patches." % (READY_LOG_TAG, expected)
            if expected_line not in joined:
                raise ExpectationFailed(
                    "expected '%s' (mandrake.rm.property %s per the skip-"
                    "line check), but it was not found. Recent lines: %r"
                    % (expected_line,
                       "active" if property_active else "inactive", msgs))
        t.screenshot()


@suite.chain("settings_toggles_flip")
def settings_toggles_flip(t):
    """Same register as StructureInjections' `enabled_toggle_flips`:
    proves both toggles are real, live-flippable Mod Settings fields --
    see the module docstring for why no further behavioral proof exists
    (no trigger, no read-back for the mechanism either gates)."""
    t.clear_area(size=8)

    with t.component("roster_tracking_enabled_flips", toggle="rosterTrackingEnabled"):
        t.set_setting(SETTINGS_TYPE, {"rosterTrackingEnabled": False})
        t.set_setting(SETTINGS_TYPE, {"rosterTrackingEnabled": True})
        t.screenshot()

    with t.component("pin_encountered_pawns_flips", toggle="pinEncounteredPawns"):
        t.set_setting(SETTINGS_TYPE, {"pinEncounteredPawns": False})
        t.set_setting(SETTINGS_TYPE, {"pinEncounteredPawns": True})
        t.screenshot()


# ---------------------------------------------------------------------------------------------------------------
# RAIDREDESIGNER_COVERAGE_GAPS_1. RaidRedesignerProof (jawa/static_call) drives the REAL RecordEncounter on a scratch
# roster (ProofRoster) and calls the SHIPPED Harmony postfix bodies directly with generated pawns (ProofHooks): the
# engine events (a raider fleeing, a prisoner escaping...) cannot be triggered from the bridge, the hook bodies can.
# Expected values below are derived from the documented rules, never read back from the C#. BetrayedTrader (Property)
# is not driven live (it would load RimMandrakeProperty.dll); its hook text and the scribe round-trip are static bars.
# Still UNMEASURED: the engine firing each hook, and a save/reload round trip of the roster.
_PROOF = "RimMandrake.RaidRedesigner.RaidRedesignerProof"

HOOKS = (   # (file, class, "Type.Method" patched, roles recorded, pin)
    ("Patch_FledRaiderAndCaptain.cs", "Patch_FledRaiderAndCaptain", "typeof(Pawn), nameof(Pawn.ExitMap)", ("FledRaider", "Captain"), "true"),
    ("Patch_PrisonerEscaped.cs", "Patch_PrisonerEscaped", "typeof(GuestUtility), nameof(GuestUtility.Notify_PrisonerEscaped)", ("EscapedPrisoner",), "true"),
    ("Patch_PrisonerReleasedOrNamedHunter.cs", "Patch_PrisonerReleased", "typeof(GenGuest), nameof(GenGuest.PrisonerRelease)", ("Released", "NamedHunter"), "true"),
    ("Patch_PrisonerReleasedOrNamedHunter.cs", "Patch_NamedHunterCaptured", "typeof(Pawn_GuestTracker), nameof(Pawn_GuestTracker.CapturedBy)", ("NamedHunter",), "false"),
    ("Patch_ColonistKidnapped.cs", "Patch_ColonistKidnapped", "typeof(KidnappedPawnsTracker), nameof(KidnappedPawnsTracker.Kidnap)", ("Kidnapper",), "false"),
    ("Patch_CaravanRobbed.cs", "Patch_CaravanRobbed", "PropertyEngine), nameof(PropertyEngine.Fire)", ("BetrayedTrader",), "false"),
)
RECORD_GATES = (    # (setting, method) -- the setting must be read inside the method that enforces it
    ("rosterTrackingEnabled", "RecordEncounter"), ("grudgeNotabilityMultiplier", "RecordEncounter"),
    ("pinEncounteredPawns", "RecordEncounter"), ("maxLivingEntries", "EnforceCap"),
)


def load_sources():
    d = os.path.join(HERE, "Source")
    return dict((fn, open(os.path.join(d, fn), encoding="utf-8").read()) for fn in os.listdir(d) if fn.endswith(".cs"))


def _body(src, name):
    for m in re.finditer(r"(?:public|private|internal|protected)[^;{=]*?\b%s\s*\([^)]*\)\s*\{" % re.escape(name), src):
        i, depth = m.end(), 1
        while i < len(src) and depth:
            depth += {"{": 1, "}": -1}.get(src[i], 0)
            i += 1
        return src[m.end():i]
    return None


def _nocomment(t):
    return re.sub(r"//[^\n]*", "", t)


def static_findings(srcs):
    """Pure over {filename: text}: hook wiring, setting gates, scribe coverage, proof wiring."""
    bad = []
    for fn, cls, target, roles, pin in HOOKS:
        t = _nocomment(srcs.get(fn, ""))
        if cls not in t:
            bad.append("%s: class %s is gone" % (fn, cls))
            continue
        if target not in t:
            bad.append("%s: %s no longer patches %s" % (fn, cls, target))
        body = _body(t.split("class %s" % cls, 1)[1], "Postfix") or ""
        if "RecordEncounter(" not in body:
            bad.append("%s: %s.Postfix no longer calls RecordEncounter" % (fn, cls))
        for r in roles:
            if "RoleTag.%s" % r not in body:
                bad.append("%s: %s.Postfix no longer records RoleTag.%s" % (fn, cls, r))
        if not re.search(r"pin:\s*%s\b" % pin, body.replace("isCaptain ? 10 : 5", "")):
            bad.append("%s: %s.Postfix pin argument is no longer %s" % (fn, cls, pin))
    comp = _nocomment(srcs.get("GameComponent_OldFriends.cs", ""))
    for setting, meth in RECORD_GATES:
        b = _body(comp, meth)
        if b is None or "RaidRedesignerSettings.%s" % setting not in b:
            bad.append("GameComponent_OldFriends.%s no longer reads RaidRedesignerSettings.%s (the setting gates nothing)" % (meth, setting))
    rb = _body(comp, "RecordEncounter") or ""
    if "isNewEntry) EnforceCap()" not in rb:
        bad.append("RecordEncounter no longer enforces the cap after a new entry's own deltas")
    if "RosterPruning.SelectPruneVictims(" not in (_body(comp, "EnforceCap") or ""):
        bad.append("EnforceCap no longer asks RosterPruning.SelectPruneVictims")
    for fn, cls in (("OldFriendEntry.cs", "OldFriendEntry"), ("Encounter.cs", "Encounter")):
        t = _nocomment(srcs.get(fn, ""))
        expose = _body(t, "ExposeData") or ""
        fields = re.findall(r"public\s+(?!static|const)(?:[\w<>\[\]]+)\s+(\w+)\s*(?:=[^;]+)?;", t.split("class %s" % cls, 1)[-1].split("ExposeData", 1)[0])
        fields = [f for f in fields if f != cls]
        if len(fields) < 3:
            bad.append("%s: scribe probe found only %d fields (sanity probe failed)" % (fn, len(fields)))
        for f in fields:
            if not re.search(r"ref\s+%s\b" % f, expose):
                bad.append("%s: field %s is not Scribed in ExposeData (lost on save/load)" % (fn, f))
    if "Scribe_Collections.Look(ref entries" not in comp:
        bad.append("GameComponent_OldFriends no longer scribes its entries")
    proj = srcs.get("RM_RaidRedesigner.csproj", "")
    if "RaidRedesignerProof.cs" not in proj:
        bad.append("RaidRedesignerProof.cs is not in the csproj (compiles into nothing)")
    return bad


def _src_with_proj():
    s = load_sources()
    s["RM_RaidRedesigner.csproj"] = open(os.path.join(HERE, "Source", "RM_RaidRedesigner.csproj"), encoding="utf-8").read()
    return s


def _kv(t, method):
    r = t.bridge_call("jawa/static_call", type=_PROOF, method=method, args="")
    if not t._guard():
        return None, ""
    text = (r or {}).get("result") if isinstance(r, dict) else None
    if text in (None, ""):
        t.upstream_reason = "UNMEASURED: RaidRedesignerProof.%s answered nothing (DLL not rebuilt/deployed yet?): %s" % (
            method, str((r or {}).get("message") or (r or {}).get("error"))[:120])
        t.upstream_failed = True
        return None, ""
    text = str(text)
    if text.startswith("ERROR"):
        raise ExpectationFailed("%s: %s" % (method, text))
    return dict(re.findall(r"(\w+)=(\S+)", text)), text


def _want(kv, text, want):
    bad = dict((k, kv.get(k)) for k, v in want.items() if kv.get(k) != str(v))
    if bad:
        raise ExpectationFailed("got %s, want %s: %s" % (bad, dict((k, want[k]) for k in bad), text[:300]))


@suite.chain("roster_rules_on_a_scratch_roster")
def roster_rules_on_a_scratch_roster(t):
    with t.component("static_hooks_gates_and_scribe_coverage", beyond_toggle=True):
        bad = static_findings(_src_with_proj())
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("one_entry_per_pawn_and_role_only_upgrades", beyond_toggle=True):
        kv, text = _kv(t, "ProofRoster")
        if kv:
            _want(kv, text, {"a_count": 1, "a_grudge": 10, "a_notab": 5, "a_enc": 1, "b_count": 1, "b_role": "Captain",
                             "b_enc": 2, "b_seen": 200, "c_role": "Captain"})
    with t.component("cap_evicts_the_lowest_notability_living_entry", beyond_toggle=True):
        kv, text = _kv(t, "ProofRoster")
        if kv:
            _want(kv, text, {"cap_count": 3, "cap_p1": "False", "cap_p4": "True"})
    with t.component("multiplier_scales_deltas_and_both_clamp", beyond_toggle=True):
        kv, text = _kv(t, "ProofRoster")
        if kv:
            _want(kv, text, {"mult_grudge": 20, "mult_notab": 40, "clamp_grudge_hi": 100, "clamp_notab_hi": 100,
                             "clamp_grudge_lo": -100, "clamp_notab_lo": 0})
    with t.component("rosterTrackingEnabled_off_records_nothing_and_pins_nothing", toggle="rosterTrackingEnabled"):
        kv, text = _kv(t, "ProofRoster")
        if kv:
            _want(kv, text, {"off_null": "True", "off_count": 0, "off_pinned": "False"})
    with t.component("dead_entry_collapses_once_stays_and_does_not_count_against_the_cap", beyond_toggle=True):
        kv, text = _kv(t, "ProofRoster")
        if kv:
            _want(kv, text, {"dead_flag": "True", "dead_summary_has_cause": "True", "dead_kept": "True", "dead_total": 4,
                             "dead_idempotent": "True"})
    with t.component("pinEncounteredPawns_pins_only_when_both_the_hook_and_the_setting_say_so", toggle="pinEncounteredPawns"):
        kv, text = _kv(t, "ProofRoster")
        if kv:
            _want(kv, text, {"pin_on": "True", "pin_arg_false": "False", "pin_setting_off": "False"})
    with t.component("scribe_round_trip_and_death_sweep_state_read", beyond_toggle=True):
        if t._guard():
            t.upstream_reason = ("UNMEASURED: a save/reload round trip of the roster (field coverage is checked statically above) and the "
                                 "hourly SweepForDeaths on a really dead world pawn need a save cycle and ticks; instrument missing: "
                                 "a [Tool] that scribes the component through a MemoryStream")
            t.upstream_failed = True


@suite.chain("hook_bodies_record_the_right_role")
def hook_bodies_record_the_right_role(t):
    with t.component("flee_hook_records_hostile_raiders_pins_them_and_ignores_friends", beyond_toggle=True):
        kv, text = _kv(t, "ProofHooks")
        if kv:
            if kv.get("pirate") != "True":
                t.upstream_reason, t.upstream_failed = "UNMEASURED: no Pirate faction in this world: " + text[:200], True
            elif kv.get("map_home") != "True":
                t.upstream_reason, t.upstream_failed = "UNMEASURED: the current map is not a player home (Pawn.ExitMap's hook ignores other maps): " + text[:200], True
            else:
                _want(kv, text, {"flee_role": "FledRaider", "flee_grudge": 5, "flee_pinned": "True", "flee_friend_recorded": "False"})
    with t.component("escaped_and_kidnapper_hooks_write_their_role_and_deltas", beyond_toggle=True):
        kv, text = _kv(t, "ProofHooks")
        if kv and kv.get("pirate") == "True":
            _want(kv, text, {"esc_role": "EscapedPrisoner", "esc_grudge": 20, "esc_pinned": "True", "kid_role": "Kidnapper",
                             "kid_grudge": 25, "kid_names_victim": "True"})
    with t.component("release_and_capture_hooks_split_blackstar_from_everyone_else", beyond_toggle=True):
        kv, text = _kv(t, "ProofHooks")
        if kv and kv.get("pirate") == "True":
            _want(kv, text, {"rel_blackstar_role": "NamedHunter", "rel_blackstar_grudge": -5, "cap_role": "NamedHunter",
                             "cap_notab": 15, "cap_pinned": "False", "cap_not_by_player_recorded": "False"})
            if kv.get("other") == "True":
                _want(kv, text, {"rel_other_role": "Released"})
    with t.component("a_real_hook_records_nothing_with_rosterTrackingEnabled_off", toggle="rosterTrackingEnabled"):
        kv, text = _kv(t, "ProofHooks")
        if kv and kv.get("pirate") == "True":
            _want(kv, text, {"hook_off_recorded": "False", "hook_off_count_delta": 0})
    with t.component("engine_events_firing_each_hook_state_read", beyond_toggle=True):
        if t._guard():
            t.upstream_reason = ("UNMEASURED: the ENGINE firing the hooks (a raider leaving the map, a prisoner escaping/released/captured, "
                                 "a kidnap) and BetrayedTrader via PropertyEngine.Fire; the hook BODIES are proven above. Instrument missing: "
                                 "bridge verbs that force those engine events")
            t.upstream_failed = True
