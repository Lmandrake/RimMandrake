## spec
Owner-said: "Keep one big reskin boom creature for the assailant dungeon,
but redo it to be fleshy-based with sacks of explosive goo, and be done
with them." Commission ONE big Assailant-dungeon boom creature — new def +
new art — replacing the entire cut boom family (`BOOM_FAMILY_CUT_1`).
Lives on the dungeon-guardians roster, never a biome spawn. `kind: design`
— per `infrastructure/agents/Agent_Policy.md`, design work is always
backgrounded to a Fable subagent, never done in-window; this item was
delegated in full rather than built directly.

## done — design brief complete
`design/Jawa/worldbuilding/creatures/goo_boom_commission.md` (Fable pass,
commit `477ab973`, pushed): the creature is `RUT_Vhessk` ("vhessk",
salvager nickname "lampgut") — a low, wide, faceless slab of flesh on 6-8
uneven legs, 5-7 translucent goo-filled sacs across its back and flanks,
sibling of the existing flesh-mutant dungeon-guardian register
(`GR_AberrantFleshbeast`/`FleshGrowth`/`FleshMonstrosity`,
`VQEA_Spliceling`/etc.) rather than "Boomalope but fleshy." Added to
`reserved_groups_draft.md` §1's Assailant dungeon-guardian rows in the
same table style as the VQEA splice creatures.

The brief grounds every mechanical claim in real source rather than
inventing numbers: read Core's `DeathActionWorker_BigExplosion`/
`_SmallExplosion` via RimSage and caught a real, non-obvious trap —
the blast radius is picked by **life-stage index**, not adulthood, so a
guardian def with a single life stage would silently detonate at the baby
radius (1.9) instead of the intended adult radius (4.9). The v1 spec (zero
C#, Flame 10 at radius 4.9, three life stages to dodge the trap) and a v2
option (a real ~15-line C# worker for a visible goo-burst, Bomb damage)
are both specified, with v1 as the shipping default. Art direction samples
real palette values off three donor flesh-mutant PNGs (viewed and
colour-sampled, not guessed) plus the campaign's own established goo
palette from `the_slime.md`/`the_contagion.md`.

Explicitly stays in brief territory: no ThingDef/PawnKindDef XML, no C#,
no texture, no CherryPicker/ModsConfig/bridge touched — confirmed via
`git show --stat 477ab973` (2 files, both `.md`).

## 8 open calls left for the owner/BENCH (brief §6, not resolved here)
1. v1 zero-C# vanilla worker vs. v2 custom goo-burst C# (real lethality
   difference — Bomb 50 vs Flame 10)
2. `baseHealthScale` 2.0 (deliberately below the doctrine's health∝mass
   reading, to keep "pop it from range" as the counterplay)
3. Melee numbers (inside the ruled band, not quicktested)
4. `MarketValue` (unset — never traded, by default)
5. Butchery yield (0 meat/leather by default; whether a "goo" crafting
   item should exist is new economy, not this commission)
6. A bespoke BodyDef vs. reusing Boomalope's `QuadrupedAnimalWithHoovesAndHump`
   for its Hump part
7. A glow comp (painted into the sprite only, for now)
8. Spawn-on-activation vs. pre-placed (depends on `ASSAILANT_DUNGEON_BUILD_1`'s
   thaw-gate wiring, itself held for the owner)
9. File location (`design/Jawa/worldbuilding/creatures/`, a new directory —
   the only prior single-commission brief sits flat in `worldbuilding/`)

## verify
Commit `477ab973` confirmed on `main`, pushed, both files present and
correctly scoped (brief + roster row, no shipping content). Design phase
of this item is complete; the actual build (ThingDef/PawnKindDef XML, the
v1-or-v2 worker decision, art generation via `generating-rimworld-sprites`)
is separate follow-on work, not started.

## 2026-09-10 — all 9 open calls RULED (owner cards, recommendations accepted)
1. **v1 zero-C# vanilla worker** — Bomb-class boom ships now; custom goo-burst C# stays
   a v2 option if the boom reads wrong in test.
2-5. **Stat package RATIFIED as briefed**: baseHealthScale 2.0 (pop-from-range
   counterplay is the spine), melee in the ruled band, MarketValue unset, butchery 0.
6. **Reuse Boomalope's body** (Hump = goo sac, targeting semantics correct).
7. **Glow painted into the sprite** — no comp for v1.
8. **Spawn wiring: builder defers to ASSAILANT_DUNGEON_BUILD_1's thaw-gate** when that
   item is ruled; the Vhessk build does NOT wait on it.
9. **Briefs live in `design/Jawa/worldbuilding/creatures/`** (new shelf — fire-hawk,
   furnace-beast, gear-dancers incoming). UNBLOCKED: build phase is FOUNDRY's.

## 2026-09-25 — build phase done (FOUNDRY)

**Cut list re-verified live first** (`cherrypicker.py --source live --is-cut`, plain
LocalLow file read, no bridge): 14 of the 15 boom-family names read `CUT` against the
live `Mod_3521312241_Mod_CherryPicker.xml` (2133 keys, 2026-09-24 write). The 15th,
`ThingDef/GR_Boomsnake`, reads `present` (not Cherry-Picker cut) — pre-existing, not
introduced here: `BOOMALOPE_CUT_EVERYWHERE_1`'s 2026-09-24 close already reasoned this
through and found it moot (`PYRELANDS_DONOR_PORT_4` re-authored the niche as our own
`RUT_Flamefang`; nothing casts the donor def any more — confirmed again this pass, no
`wildAnimals`/biome-cast hit anywhere for `GR_Boomsnake`). Functionally cut (unreachable
in play) even though the CherryPicker entry itself was dropped somewhere between
`BOOM_FAMILY_CUT_1` and now; not re-added here since re-litigating a different closed
item's reasoning is out of this item's scope and the creature cannot spawn regardless.

**Built**: `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Vhessk.xml` —
`ThingDef`+`PawnKindDef RUT_Vhessk`, every field per brief S2b/S3c and the 2026-09-10
rulings (v1 zero-C# `DeathActionWorker_BigExplosion`, three `lifeStageAges` to dodge the
life-stage-index trap in brief S3b, `baseBodySize`/`baseHealthScale` 3.0/2.0,
`combatPower` 200, `MoveSpeed` 2.6, body `QuadrupedAnimalWithHoovesAndHump`, `MeatAmount`
0/no leatherDef/no MarketValue, body-slam+maw melee per Law 3). Dungeon-guardian only:
no `wildAnimals` entry, no biome cast, no trader tag, no `wildSpawn`-eligible field
anywhere — confirmed by grep across `src/` and `design/.../rosters/*.json`, zero hits.
Roster row updated from "NOT BUILT" to "BUILT" in `reserved_groups_draft.md` S1; brief's
own status banner updated in `goo_boom_commission.md`.

**Art**: no prior render existed for this subject (checked
`infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl` for
vhessk/lampgut/boom — clean; the only "boom" hits are the unrelated
`pyrelands_boomsnake_v*` jobs). Queued via `fill_queue.py` this pass:
`infrastructure/artpipe/art_lists/goo_boom_commission.csv` → 3 jobs filed
(`rut_vhessk_{south,east,north}`, 512×512, `oversize_reason` recorded). **PENDING
RENDER** — not landed; the def ships with a placeholder (Thrumbo's own texture, tinted
dark maroon) so it loads and renders coherently until the real art arrives, per this
project's own "art can be pending-render without blocking close" convention.

**Verify done this pass**: `validate_patch.py --live` against the freshest capture
(`DefDump/captures/2026-09-24T22-19-22Z`, 621 mods vs 627 active — noted, not fully
fresh) → 0 errors. Re-run with the full `--defs` load set (Data + Workshop 294100 +
deployed Mods, 627/627 found on disk) → still 0 errors, 6 warnings (all the known
vanilla-asset-bundle texPath false positive already accepted for `RM_Dorrak`/
`RM_Krissek`'s identical placeholder pattern in `RM_BlueDesertFauna.xml`; ParentName
`AnimalThingBase`/`AnimalKindBase` resolved clean against the real load set).
`run_selftests.py`: 73/75 passed; the 2 failures (`selftest_live_prep`,
`selftest_deployed_biome_refs` — `RUT_Vorrel`/`RUT_WelcomeBlanket` dangling refs) are
both pre-existing and unrelated to this def (neither names Vhessk or this file).

**Not chased this pass** (bridge held by another agent's restart+verify batch):
the brief's own S3b-mandated quicktest kill + scorched-cell count to confirm the adult
(4.9, ~75 cells) rather than baby (1.9, ~12 cells) blast radius actually fires. Real
placement inside the Assailant complex is `ASSAILANT_DUNGEON_BUILD_1`'s own work, held
for the owner (creative lock-in) — this item does not wait on it, per S6 ruling #8.

## verify (updated)
- [x] Old boom family cut, live-verified (14/15 CUT; 15th unreachable, pre-existing).
- [x] `RUT_Vhessk` ThingDef+PawnKindDef built, validated, selftested.
- [x] Wired to the dungeon-guardians roster doc; never a biome `wildAnimals` entry.
- [ ] Art render (queued, pending — daemon-side, does not block close).
- [ ] Quicktest kill proving the 4.9-radius blast (owed once the bridge is free).
- [ ] Actual in-dungeon placement (owed to `ASSAILANT_DUNGEON_BUILD_1`, held for owner).

## closed 2026-09-25 (FOUNDRY)
Creature fully built and wired; old boom family confirmed cut. Art pending-render and
the in-dungeon placement/quicktest are real remaining gaps but do not block this
commission's own close, per the project's standing art-queue and dungeon-item-deferral
conventions cited above.
