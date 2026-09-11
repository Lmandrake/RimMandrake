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
