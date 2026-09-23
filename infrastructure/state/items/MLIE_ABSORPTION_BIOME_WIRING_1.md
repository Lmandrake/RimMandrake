# MLIE_ABSORPTION_BIOME_WIRING_1 — 98 live biome rows still name the bare donor for creatures we already ported

**planet-wide — 11 biome defs**

Successor to the wiring half of `MLIE_FAUNA_ABSORPTION_1` (**closed**), which recognised this
exact defect class, fixed one instance, and closed with the rest outstanding.

## the measurement

MEASURED 2026-09-23 by parsing `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/*.xml` for
`MayRequire="mlie.starwarsanimalcollection"` and testing each bare name against every
`<defName>` in `src/`:

| figure | value |
|---|---|
| live biome rows gated on the **donor** mod where we **already ship** an `RSW_` port | **98** |
| distinct creatures those rows cover | **73** |
| live biome rows gated on the donor with **no port of ours** | 10 |
| distinct subjects in that remainder | 8 — and **6 of them are canon plants** (hydenock, jogan, muja, tooke trap, bubblespore, felucian glowspore), plus `Snoruuk` |
| biome files affected | **11** — AridShrubland, CrackedLands, FeverWood, Greentide, Miasma, PoisonForest, Scarlands, TheForge, Wasteland, Webwork, WeepingStones |
| rows already gated on **our** bestiary (`mandrake.rsw.swbestiary`) | 143 |

⚠️ **Instrument caveat, stated because the number would otherwise look cleaner than it is:**
the regex that collects donor-gated names also matched one literal `li` from a
`<li MayRequire=…>` element, so the "8 distinct subjects" in the no-port remainder includes a
parse artefact. The **98 / 73 figures are unaffected** — every one of those resolved to a real
creature name with a real `RSW_` counterpart.

## why this is real and not a naming style

🔴 **The design rosters are NOT wrong, and an earlier note calling them so was a
misdiagnosis** — corrected on `ROSTER_DEAD_BMT_NAMES_SWEEP_1` this pass. The 144 bare-name rows
in `design/Jawa/worldbuilding/biomes/rosters/*.json` faithfully mirror the live XML, which
deliberately uses the donor's defName gated on the donor's mod. That is the correct convention
for a donor creature.

The defect is one level up. `MLIE_FAUNA_ABSORPTION_1` **ported** these creatures — e.g.
`RSW_Urusai` carries its own header: *"Wave C, Pass 24 — Urusai creature port… renamed under
the `RSW_` tier prefix"*, with 16 PNGs extracted, bodies reused, sounds absorbed, eggs made —
and then the biomes were never switched over to them. That item found the same gap for
`RSW_Bantha` on 2026-09-09 (*"Bantha's port existed but its 3 cast slots still named the bare
donor"*), fixed it, recorded **7** creatures wired, and closed.

⇒ Two consequences, both live today:
1. **The campaign still hard-depends on `mlie.starwarsanimalcollection`** for 98 cast rows.
2. **73 creatures we paid to port are shipping unused** — art extracted, defs written, nothing
   spawning them.

## spec

1. For each of the 98 rows, decide and apply one of two outcomes — this is **not** a blanket
   rename:
   - **switch to our port** — row becomes `RSW_<Name>` with
     `MayRequire="mandrake.rsw.swbestiary"`; or
   - **keep the donor row deliberately**, with a comment saying why (an `*ArtOverride`
     we prefer, a def we chose not to absorb faithfully, a variant the port does not cover).
2. ⚠️ **Where a bare name has two candidates, pick the creature and not the leather.** Several
   resolve to both `RSW_<Name>` and `RSW_Leather_<Name>` — Bantha, Ronto, Wraid, Nerf, Horax,
   Wampa, Zakkeg, LavaFlea, KraytDragon, Fambaa. A `wildAnimals` row takes the pawn.
3. **Mirror each decision into the design roster** (`rosters/<biome>.json`) so the record and
   the game agree, and so the next census does not re-find this.
4. Close out `MLIE_FAUNA_ABSORPTION_1`'s surviving unchecked line — *"Our own 3 Mlie-touching
   patch files repointed and confirmed resolving"* — or record why it is moot.

## verify

- Re-run the measurement; the 98 must go to zero or to a documented deliberate remainder.
- 🔴 **Whether each `RSW_` port actually resolves against the LIVE active mod list is
  UNMEASURABLE on the Mac** — `measure` is not executable here and there is no local def dump.
  Existence in `src/` is all that was verified. A **Desktop** pass must confirm resolution
  before wiring, exactly as `ROSTER_DEAD_BMT_NAMES_SWEEP_1` records for its own rows.
- `validate_patch.py` on every edited file, then a post-load def dump — an unmatched op is
  silent.
- A cold-load `Player.log` grep for Config errors, and a spot check that a switched creature
  still spawns.

## criteria

Every biome cast row names the def we intend it to name; the campaign's dependency on the donor
mod is either removed or deliberate and documented; and no ported creature sits unused because
nothing spawns it.

## Watch out

- ⛔ **Not a sweeping auto-rename.** 98 rows across 11 biomes touching 73 creatures is exactly
  the shape of change the owner stopped for rosters on 2026-09-22 — *"much better to carefully
  handle biome by biome rather than sweeping changes."* ⇒ Work it **per biome**, and a biome
  that is mid-sitting waits for its sitting.
- ⚠️ **A port is not automatically better than the donor row.** `MLIE_ARTOVERRIDE_COLLISION_CHECK_1`
  closed over art-override collisions; check whether an override is in play before switching.
- 🔴 **Do not touch the `RUT_` twins' rows as a way of "fixing" a biome's appearance today.**
  `BIOME_PAINT_ONCE_AT_THE_END_1` governs the live world, and repointing owned content at a
  donor def to make something appear has nearly shipped twice.
- ⚠️ The remainder's six canon **plants** are a different question entirely (canon flora we have
  not ported) and should not be folded into this item.
