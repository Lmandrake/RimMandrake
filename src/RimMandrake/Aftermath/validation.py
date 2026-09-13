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
  src/RimMandrake/Pits/validation.py's own note after `uncover_disarms`).
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
  3. `jawa/harmony_patches`'s exact result shape (grouped by HarmonyId? by
     target method? a flat list?) was read from its tool Description text,
     not a live call -- `harmony_patches_registered` below does a
     defensive substring search across `repr(result)` for that reason,
     and will need tightening once the real shape is seen.
  4. The Pirate FactionDef is assumed hostile-to-player and present on the
     minimal mechanism list (it is vanilla Core, not a mod def) -- not
     re-verified here.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Aftermath")
suite.toggles = ["aftermathEnabled", "maxQueuedPerFaction", "maxQueuedTotal",
                 "mentalBreakWindowDays"]

HARMONY_ID = "mandrake.rm.aftermath"

# The five real seams named in this mod's own Source headers
# (Patch_RaidGenerated.cs, Patch_LordLifecycle.cs x2, Patch_ColonistCasualty.cs,
# Patch_MentalBreakNearBattle.cs). Checked as method-name substrings against
# whatever shape jawa/harmony_patches hands back -- see docstring point 3.
PATCHED_METHODS = [
    "TryGenerateRaidInfo", "MakeNewLord", "RemoveLord", "Kill", "TryStartMentalState",
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
        r = t.bridge_call("jawa/harmony_patches", harmonyId=HARMONY_ID)
        text = repr(r)
        missing = [m for m in PATCHED_METHODS if m not in text]
        if missing:
            raise ExpectationFailed(
                "jawa/harmony_patches(harmonyId=%r) does not mention: %r -- raw result: %r"
                % (HARMONY_ID, missing, r))
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
