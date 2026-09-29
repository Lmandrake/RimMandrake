## Scope
Follow-on to CONTAGION_RULED_CONTENT_1 Wave A (closed the 15-creature donor
port). This is cast bible §3/§5's **new species** (Part 2 of the original
item's scope), quoted verbatim from
`design/Jawa/worldbuilding/biomes/contagion_grotesque_cast_2026-09-27.md`:

> **New species**: Skinflap, Gorekite, Danglemaw, Crispling, Sloshbelly; flora
> Meatvine, Toothmoss, Wombpod (Wombpod wires into the BUILT amoeba-gestation
> loop as the harvestable host source).

Read the cast bible §3 (fauna) and §5 (flora) in full for each creature/
plant's hook, cycle role, stats sketch and wiring notes before authoring.

## Watch out
- All five new fauna are **goo-bud lines with goo-corpses** (re-absorbable by
  construction, satisfying ban 3 — "no finished natives beyond the ruled
  table"). Give each a goo-corpse deathAction, not a normal corpse.
- Skinflap and Gorekite are the owner's mandatory addition ("really gross
  fleshy flapping skin things that fly") — both are ruled FLYERS. Flight
  statBases are covered by the separate follow-on `CONTAGION_FLYER_WIRING_1`;
  do not block this item on flight, but do not ship these two without a
  clear TODO pointing at that item either.
- Wombpod's harvest must wire into the ALREADY-BUILT genome loop
  (`RM_AmoebaGestation.xml`, `Hediff_AmoebaGestation.cs`,
  `AmoebaHostUtility.cs`, `RM_GenomeSample.xml` — all live in
  `src/RimMandrake/Contagion/`). Read those files first; this is "give the
  loop its in-world organ," not a new mechanism.
- Danglemaw's true ambush-from-canopy behaviour is C# (the cast bible itself
  says so); v1 may ship as a slow high-damage lurker spawned near Eyebark
  clusters instead — note, not a blocker.
- The sheet amendment admitting these five to `the_contagion.md` §4 is
  BENCH's to write, not this item's — do not edit that sheet's frozen table
  yourself; file a note for BENCH if it still says "admission pending" when
  this item closes.
- `<li>` in wildAnimals/wildPlants silently discards the whole entry —
  shorthand element form only, same law as Wave A.
- Check `infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl` for
  already-generated art before queuing (Wave A found the whole 15-creature
  cast's art already finished under the exact new names — check whether
  these 8 got the same treatment before assuming anything is owed).

## Verify
- All 8 defs exist, validate_patch.py --defs 0 errors, wired into
  RM_Contagion's wildAnimals/wildPlants at design-sketch commonalities (cast
  bible's own numbers are marked "for the sitting to ratify" — use them
  unless BENCH's sheet amendment overrides).
- Wombpod harvest yields a usable gestation-loop input (measured, not
  assumed — a quicktest or direct C#/def read of the harvest recipe wired to
  AmoebaHostUtility).
