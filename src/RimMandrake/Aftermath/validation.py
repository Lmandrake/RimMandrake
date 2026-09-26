"""validation.py -- modcheck suite for RimMandrake Aftermath (mandrake.rm.aftermath).

Grounded in this mod's actual Source (AftermathMod.cs, RM_AftermathMod.cs,
MapComponent_BattleRecorder.cs, AftermathRuleRunner.cs, BattleOutcomeClassifier.cs,
Patch_RaidGenerated.cs, Patch_LordLifecycle.cs, Patch_ColonistCasualty.cs,
Patch_MentalBreakNearBattle.cs, NinefoldBandBridge.cs) -- never the mod's name or
design/Jawa/proposals/plot_mechanisms_wave.md's aspirations for it.

WHAT THIS MOD ACTUALLY IS AT RUNTIME, split for the smoke test's benefit:

  (1) THE BATTLE RECORDER (MapComponent_BattleRecorder + Patch_RaidGenerated /
      Patch_LordCreated / Patch_LordRemoved / Patch_ColonistCasualty). Fully
      self-contained: opens a BattleRecord the instant
      IncidentWorker_Raid.TryGenerateRaidInfo returns true for a hostile
      faction, closes it when the raid's correlated Lord is removed OR (the
      fallback every 250 ticks) once every original pawn is
      dead/downed/off-map, classifies the outcome via
      BattleOutcomeClassifier.Classify, and publishes a `battle.closed`
      ChronicleEvent. RM_AftermathMod.cs's own header is explicit that the
      master settings switch does NOT gate this -- Ninefold and any other
      spine consumer need it regardless. This is the part this suite can
      actually exercise live, and does.

  (2) THE RULE RUNNER (AftermathRuleRunner). Reads RM_AftermathRuleDef
      instances and turns a closed battle / a nearby mental break / a
      long-held prisoner into a queued follow-up incident. THE RULE DEFS
      SHIP IN A SEPARATE MOD (mandrake.rut.aftermath, folder
      src/RimUtinni/AftermathRites) -- About.xml says "defs ship separately"
      and a grep of src/RimMandrake/Aftermath confirms zero
      RM_AftermathRuleDef instances anywhere in it. Per this runner spec's
      own environment rule ("minimal mechanism list + the mod under test"),
      AftermathRites is not part of THIS mod's smoke environment, so with
      zero RM_AftermathRuleDefs loaded every
      `foreach (RM_AftermathRuleDef def in DefDatabase<...>...)` loop in
      AftermathRuleRunner is empty by construction -- nothing can be
      observed queuing. That is a scope fact about testing this mod alone,
      not a defect in it.

MOD SETTINGS -- suite.toggles below, ALL UNCOVERED, and why (this is the
mandatory register, not an oversight):
  RM_AftermathSettings declares its four fields `public static`
  (aftermathEnabled, maxQueuedPerFaction, maxQueuedTotal,
  mentalBreakWindowDays) -- exactly the shape the Pits pilot already found
  live 2026-09-12 makes `rimworld/update_mod_settings` (t.set_setting)
  refuse with "Could not resolve field ... on ...Settings" (that tool's
  reflection walks INSTANCE fields on the ModSettings object; see
  src/RimMandrake/FlowWorks/validation.py's own note after `uncover_disarms`).
  The same mechanical fact applies here without needing to re-discover it
  live. And even a working setter could prove nothing without (1)'s zero
  rule-defs, or (for the one WIRED trigger that needs no rule-def context
  at all, PrisonerHeldDuration) burning minHeldDays' default 3 real days --
  ~180,000 ticks -- which is far outside any reasonable smoke-test budget.
  Every component below is therefore beyond_toggle=True.

Still not proven / likely first-live-run corrections:
  1. `jawa/storyteller_fire(incidentDef="RaidEnemy", dryRun=False)` lands its
     raiders wherever IncidentWorker_RaidEnemy's own arrival-mode picks --
     NOT inside a `clear_area` rect. There is no bridge call that opens a
     BattleRecord any other way (OpenBattle is only ever reached through
     the real TryGenerateRaidInfo seam), so this chain cannot honor the
     spec's usual "hostiles spawn inside the cleared test area" the way a
     spawn-and-walk chain can. `clear_area(size=90)` is the closest honest
     approximation (enough to plausibly cover a small raid's landing spot
     on a quicktest map), not a guarantee.
  2. Whether raiders are visible to `jawa/list_pawns(faction="hostile")`
     within `wait_ticks(200)` of the fire call returning -- drop-pod vs.
     edge-walk-in arrival timing for a 120-point RaidEnemy was not measured
     live before writing this file.
  3. FIXED 2026-09-26 (was: item point 3 as originally written). The suite
     called `jawa/harmony_patches(harmonyId=HARMONY_ID)` -- that parameter
     does not exist. Read against the tool's own C# source
     (`JawaBenchHarmonyInspect.cs`): `typeName` is REQUIRED (case-
     insensitive simple or full name), `methodName` is an optional exact
     filter, and the tool is grouped BY TYPE, not by HarmonyId -- results
     are `methods[].{prefixes,postfixes,transpilers,finalizers}[].owner`,
     with `owner` being the HarmonyId string. There is no way to query
     "every method any mod patches under HarmonyId X" directly; you query
     per declaring TYPE and check `owner` on the rows that come back.
     `harmony_patches_registered` below now calls once per (type, method)
     seam (read from each Patch_*.cs's own `[HarmonyPatch(typeof(...),
     nameof(...))]` attribute, not guessed) and asserts `HARMONY_ID`
     appears as an `owner` on that exact method -- this was still an
     UnknownParameterError first live run 2026-09-13 (`harmonyId` silently
     discarded, tool ran on defaults and returned success on an
     unfiltered/wrong-shaped result), not a mod defect.
  4. FIXED 2026-09-26 (was: "the Pirate FactionDef is assumed ... present
     on the minimal mechanism list ... not re-verified here"). It measured
     ABSENT live 2026-09-13: `jawa/storyteller_fire(faction="Pirate")`
     failed with "FactionDef 'Pirate' exists but no such faction is in
     this world." This is not flaky and not minimal-list-specific --
     `jawa/faction_create`'s own C# docstring names the exact, deterministic
     cause: Biotech's `PirateWaster` declares `replacesFaction` at vanilla
     `Pirate` with `requiredCountAtGameStart` above zero, so
     `FactionGenerator.InitializeFactions` SKIPS generating a `Pirate`
     instance on any world generated with Biotech active -- and
     CLAUDE.md's own standing rule is that every test mod list carries ALL
     FIVE expansions, Biotech included, with no ablation. So no quicktest
     world this suite ever runs against will have a live `Pirate` faction,
     ever, by construction -- the SAME root cause the item's own history
     flagged for RimProperty's chain-setup abort ("no Pirate Faction
     INSTANCE in this test world"), not a coincidence. `t.ensure_faction`
     (modcheck.suite, shared -- this is not Aftermath-specific) creates it
     via `jawa/faction_create` before firing the raid, tolerating "already
     exists" as success rather than failure.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Aftermath")
suite.toggles = ["aftermathEnabled", "maxQueuedPerFaction", "maxQueuedTotal",
                 "mentalBreakWindowDays"]

HARMONY_ID = "mandrake.rm.aftermath"

# The five real seams named in this mod's own Source headers
# (Patch_RaidGenerated.cs, Patch_LordLifecycle.cs x2, Patch_ColonistCasualty.cs,
# Patch_MentalBreakNearBattle.cs), each read straight off that file's own
# `[HarmonyPatch(typeof(X), nameof(X.Y))]` attribute -- not guessed. See
# docstring point 3: jawa/harmony_patches is queried per (type, method),
# never by HarmonyId (no such parameter exists).
PATCHED_SEAMS = [
    ("IncidentWorker_Raid", "TryGenerateRaidInfo"),
    ("LordMaker", "MakeNewLord"),
    ("LordManager", "RemoveLord"),
    ("Pawn", "Kill"),
    ("MentalStateHandler", "TryStartMentalState"),
]


@suite.chain("harmony_patches_registered")
def harmony_patches_registered(t):
    """Beyond-toggle: proves the mod's five Harmony postfixes are actually
    live under its own HarmonyId, not merely that AftermathMod's static
    constructor ran without throwing (Log.Message's own patch COUNT says
    nothing about WHICH methods -- a signature drift after a RimWorld
    update silently drops just one Patch class while the others still
    apply and the boot log still reports success)."""
    with t.component("patches_applied", beyond_toggle=True):
        missing = []
        for type_name, method_name in PATCHED_SEAMS:
            r = t.bridge_call("jawa/harmony_patches", typeName=type_name,
                              methodName=method_name)
            methods = (r or {}).get("methods") or []
            row = next((m for m in methods if m.get("method") == method_name), None)
            owners = []
            if row:
                for key in ("prefixes", "postfixes", "transpilers", "finalizers"):
                    owners.extend(p.get("owner") for p in (row.get(key) or []))
            if HARMONY_ID not in owners:
                missing.append("%s.%s (owners seen: %r)" % (type_name, method_name, owners))
        if missing:
            raise ExpectationFailed(
                "jawa/harmony_patches does not show %r as the owner of: %s"
                % (HARMONY_ID, "; ".join(missing)))
        t.screenshot()


@suite.chain("battle_lifecycle_repelled")
def battle_lifecycle_repelled(t):
    """The battle recorder's whole lifecycle, end to end, through the REAL
    seam (see module docstring point 1 for why the area cannot be strictly
    cleared first): fire a real RaidEnemy, let Patch_RaidGenerated open a
    BattleRecord, kill every raider outright (>=60% dead/downed forces
    BattleOutcomeClassifier.Classify to REPELLED ahead of the LOST/ROUTED
    branches -- see that file's own priority-ordering comment), let the
    250-tick fallback poll (MapComponent_BattleRecorder.CheckFallbackClosures)
    close it, and read the classification back through this mod's own
    (DevMode-gated -- its only channel; enabled explicitly below) Log.Message
    line in Close()."""
    t.clear_area(size=90)

    with t.component("devmode_and_raid_fire", beyond_toggle=True):
        t.bridge_call("jawa/prefs", devMode=True)
        t.ensure_faction("Pirate")
        r = t.bridge_call("jawa/storyteller_fire", incidentDef="RaidEnemy",
                          points=120, faction="Pirate", dryRun=False)
        if not (r or {}).get("fired"):
            raise ExpectationFailed(
                "jawa/storyteller_fire did not report fired=true: %r" % r)
        t.expect_log_contains("[RimMandrake.Aftermath] battle opened")
        t.screenshot()

    with t.component("kill_all_raiders_closes_repelled", beyond_toggle=True):
        t.wait_ticks(200)  # let arrival mode finish placing raiders (docstring #2)
        pawns = (t.bridge_call("jawa/list_pawns", faction="hostile", limit=100) or {}).get("pawns") or []
        if not pawns:
            raise ExpectationFailed(
                "no hostile pawn visible via jawa/list_pawns(faction='hostile') after "
                "the raid fired -- either arrival is slower than 200 ticks, or the raid "
                "landed on a different loaded map (see module docstring #1/#2).")
        for p in pawns:
            pid = p.get("id")
            if pid:
                t.bridge_call("jawa/damage", damageDef="Bullet", amount=9999,
                              thingId=pid, allowColonists=False)
        t.wait_ticks(300)  # >= MapComponent_BattleRecorder.FallbackPollIntervalTicks (250)
        t.expect_log_contains("-> Repelled")
        t.screenshot()
