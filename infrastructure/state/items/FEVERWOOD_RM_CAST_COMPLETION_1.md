# FEVERWOOD_RM_CAST_COMPLETION_1 — build the seven ratified Fever Wood creatures, the skreth as the free second front

Caused by `FEVERWOOD_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.feverwood`
(`src/RimMandrake/FeverWood/`; folds into `RimMandrake.Biomes` under `BIOME_MOD_UNIFICATION_1`). Design:
`design/Jawa/worldbuilding/biomes/feverwood_bedazzle_review_2026-10-02.md` §1 (fauna findings), §3, §4 row 0,
§8. Ruling: **build first: land the decided work plus the giant's story** (decision taken by question card
2026-10-02 11:12 PDT). Nothing here is new design: it executes the 2026-09-24 cast card
(`design/Jawa/worldbuilding/biomes/fever_wood_rm_cast_proposal_2026-09-24.md` § Rulings: *"Cast RATIFIED,
all of it"*; *"The skreth IS the free-tier face of the Webwork brood … The two-front war is identical in both
tiers"*), which `FEVERWOOD_RM_MOD_BUILD_1` closed without doing. Bodies and art briefs:
`design/Jawa/worldbuilding/biomes/fever_wood_fauna_roster_2026-09-23.md` (rows 5–7) and the cast proposal's
table. Names were collision-proven at the 2026-09-24 sitting (5/5 `check_pseudo_sw_name.py`, `src/` zero,
Wookieepedia zero with a `dewback` control); `lommerel` is the ruled rename of `mulleth`.

Sheet bans bind: **3, no native chase predators** (the silloch and grolth wait, never chase; only the two
raiders pursue); **7, no Earth flora or fauna** (alien body and colour on every one).

## spec

1. **Six roster creatures, inline on `RM_FeverWood/wildAnimals`** (ThingDef race + PawnKindDef each; rows as
   XML elements, `<RM_Nemmel>0.4</RM_Nemmel>`, never `<li>`), at the ruled commonalities:

   | defName | label | body (bodySize) | niche | diet | commonality |
   |---|---|---|---|---|---|
   | `RM_Lommerel` | lommerel | medium (~1.0) | crown grazer slung UNDER the boughs; must read upside-down | herbivore (verrow gourds) | 0.4 |
   | `RM_Silloch` | silloch | small (~0.6) | crown wait-ambusher, a flat wedge folded against bark; must read as bark; never chases | carnivore | 0.3 |
   | `RM_Brathek` | brathek | medium (~0.9) | the wood-borer that keeps digging (§6q), beside the kept `VFEI2_Megathrips` | wood pulp | 0.5 |
   | `RM_Nemmel` | nemmel | small (~0.3) | ground grazer of the causeway edges, the floor's one honest meal | herbivore | 0.4 |
   | `RM_Grolth` | grolth | medium (~0.8) | ground-slow carrion-dissolver at the causeway margins; waits, never chases | carrion | 0.05 |
   | `RM_Gorrameth` | gorrameth | very large (~4.0) | the terribly lost: a placid wanderer that drinks at the mirror pools and is taken | herbivore | 0.02 |

   Descriptions franchise-free, from the roster's art briefs. ⚠️ An art pass that "corrects" the silloch to an
   upright creature or the lommerel to a standing one has broken the design (roster §, read before drawing).
   **The brathek's digging rate and whether it can be directed are unset** in the roster
   (`fever_wood_fauna_roster_2026-09-23.md` "open"): ship it as an ordinary wild animal with
   `VFEI2_Megathrips`-like wood-eating at most, a settings toggle for any wall/bough damage, and a
   `// INVENTED` flag on every number; do not guess the open ruling.
2. **`RM_Skreth`, the free second front (off-roster, commonality 0, never a `wildAnimals` row).** ThingDef
   race + PawnKindDefs `RM_Skreth` and `RM_SkrethMatron` (the matron leads the brood: egg-clutch sheen; body
   large ~2.5, low eight-limbed silk-grey ambusher, forelimbs raised in a strike cock), and a hidden
   FactionDef `RM_FactionDef_SkrethBrood` cloned from `RM_FactionDef_KurrethSwarm` (same hidden/permanent-enemy
   posture), hostile to the kurreth swarm both ways, as the kurreth/feralisk pair already is.
   **`RM_MapComponent_TwoFrontLure`**: when `RSW_Shokk_FeraliskBrood` is absent, the second front is
   `RM_FactionDef_SkrethBrood`, never a fallback to ants. When the Shokk brood IS present, the campaign keeps
   using it (one creature, two skins: the campaign's skin goes over the skreth Sekkulaath-style; a patch that
   relabels the skreth as the feralisk is the cleaner long-run shape and is `FEVERWOOD_DIANOGA_GIANT_MAP_1`'s
   sibling, not this item's). Packaging of the raider defs (FeverWood vs `mandrake.rm.environmentalhazards`) is
   FOUNDRY's call (2026-09-24 card).
3. **Not in this item:** the gorrameth's doomed-herd IncidentDef (ruled for *"a later wave"*, 2026-09-24); the
   ants' theft (`FEVERWOOD_ANT_THEFT_RAIDBACK_1`).
4. **Art is done for all seven; deploy it, do not regenerate.** MEASURED 2026-10-02 with `artpipe_state.py find`
   (probe `korrum` hits `_artsrc/RSW_Korrum_*`): finished east/north/south renders in the artpipe `done/` and
   `_artsrc/` for `feverwood_lommerel_*`, `feverwood_silloch_*`, `feverwood_brathek_*`, `feverwood_nemmel_*`,
   `feverwood_grolth_*`, `feverwood_gorrameth_*` and `feverwood_skreth_*` (filed under `FEVERWOOD_RM_MOD_BUILD_1`).
   Deploy those PNGs into the mod's `Textures/` and point each `texPath` at them (texture binds by texPath).
   The skreth matron reuses the skreth set scaled up (its prompt already carries the egg-clutch sheen); a
   separate matron render is owed only if the owner asks. Check `Transient/*.decisions.json` for any ruling on
   these renders before deploying.
5. **Flight:** none of the seven flies (the four birds already do). No flyer rule applies.
6. **References elsewhere:** `AnimalTolerances_Ashkarr.xml` and any heat/tolerance list naming Fever Wood
   creatures gains the seven `RM_` names. `RUT_FeverWood`, the frozen twin, is not touched.

Depends on: nothing (land first). Corrects and absorbs `FEVERWOOD_TWO_FRONT_LURE_TUNING_1` spec 4 (the
free-tier second raider; see that item's 2026-10-02 additions). Soft-blocks `FEVERWOOD_ANT_THEFT_RAIDBACK_1`
(the theft is the kurreth's, but the lure's two fronts are tested together). `FEVER_WOOD_FIRST_SCRIPT_1` is
written against this item's state.

## criteria

Deterministic state reads through `jawa/get_defs` (reading `success`/`foundCount`/`notFound`, never a
substring) and an offline XML parse, recorded as cases in `FEVER_WOOD_FIRST_SCRIPT_1`'s `validation.py`:
- `ThingDef/` and `PawnKindDef/` for `RM_Lommerel`, `RM_Silloch`, `RM_Brathek`, `RM_Nemmel`, `RM_Grolth`,
  `RM_Gorrameth`, `RM_Skreth`, plus `PawnKindDef/RM_SkrethMatron` and `FactionDef/RM_FactionDef_SkrethBrood`:
  `foundCount` = 16.
- With only Core, the five DLCs and the free mod's declared dependencies loaded (no `mandrake.rsw.*`), the
  same 16 resolve and `Player.log` has no `Could not resolve` naming any of them.
- `RM_FeverWood`'s `wildAnimals`, parsed as XML elements, holds the six roster names at exactly 0.4 / 0.3 /
  0.5 / 0.4 / 0.05 / 0.02, and does **not** hold `RM_Skreth` or `RM_Kurreth`.
- Offline parse: every description of the seven contains none of `dianoga`, `Force`, `Star Wars`,
  `spider`, `ant`-as-a-word.
- `RM_MapComponent_TwoFrontLure` with the Shokk brood absent: a bridge read of the second wave's faction def
  (through the lure's own debug/inspect string or a `[Tool]`) returns `RM_FactionDef_SkrethBrood`; with the
  kurreth swarm only as the first. A source read finds no remaining ants-for-both fallback branch.
- `FactionDef/RM_FactionDef_SkrethBrood` and `RM_FactionDef_KurrethSwarm` are hostile to each other (live
  `Faction.HostileTo` read on the generated factions).
- Each of the seven `texPath`s resolves (a spawned pawn's graphic is not the error material).
- Offline parse: no `MaxFlightTime` on the seven (none flies).
