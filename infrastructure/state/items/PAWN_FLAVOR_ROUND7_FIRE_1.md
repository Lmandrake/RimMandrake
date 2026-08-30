# PAWN_FLAVOR_ROUND7_FIRE_1 — Deep Desert Fire side

## Shipped
Four defs per `pawn_flavor_design.md`'s round-7 block: `Jawa_PyreWatcher`
(Childhood), `Jawa_FlameReaper` + `Jawa_AshSpeaker` (Adulthood, appended to
`Backstories_Homestead_Tribes.xml` under a new Round 7 header, `JawaBSC_Tribes`
spawnCategory already wired to `TribeCivil` — no new wiring needed), plus the
standalone `Jawa_ReapsTheFlames` trait and supporting `Jawa_AshJudgment` trait
(`Traits_JawaPawnFlavor.xml`).

Ash-Speaker's eases/hardens-conversion maps to `Jawa_AshJudgment`'s
`ConversionPower` statOffset (+0.5, MayRequire Ideology) — a real vanilla stat,
verified via RimSage before use. Pyre-Watcher/Flame-Reaper tied to
`Jawa_ReapsTheFlames` (shared Fire-creed identity); Ash-Speaker to
`Jawa_AshJudgment` — the design doc doesn't specify the mapping, so this is a
documented judgment call, not a guess.

Two mechanics honestly stubbed, not faked (no hook exists to approximate them
with a flat statOffset): Reaps-the-Flames' break-weight-drop-while-fire-burns
and mood-debuff-in-long-unburned-lush-green (both need a StatPart/ThoughtWorker
reading live map state — filed as C# follow-up when picked up). Fire-fear-immune
/ no-mood-hit-from-burning: no vanilla mechanic exists to hook, so left as prose
flavor text, not invented.

## Verify
`validate_patch.py` against the live 585-mod set: 0 errors (8 pre-existing
warnings, unrelated file, unchanged). `deploy_custom_mods.py --mod
Jawa_PawnFlavor`: in sync. Plain def additions (BackstoryDef/TraitDef), no
bridge-driven mechanism to silently lie about — offline validation is the
verification here per CHARTER (only bridge setters/patches-matching-nothing
need a live check).

## criteria
- [x] Four defs shipped per the design doc's round-7 block.
- [x] Wired into the existing spawn category, no new wiring patch needed.
- [x] One real mechanic mapped to a verified vanilla stat; two honestly
      stubbed rather than faked; two left as prose where no hook exists.
- [x] validate_patch.py clean against the live mod set.
- [x] Deployed, in sync.
