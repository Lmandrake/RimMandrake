# STONEBACK_DEFNAME_COLLISION_1 — one defName, two different animals

## what is wrong — MEASURED 2026-09-21

`RSW_Stoneback` is declared **twice**, as both a `ThingDef` and a `PawnKindDef`, in two
directories the game **does** load:

| file | label | bodySize |
|---|---|---|
| `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml` | **bokka** | **0.4** |
| `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml` | **korrum** | **4.00** |

These are not a duplicate of one creature — they are **two different creatures**, a small
one and a giant one, colliding on a single defName. RimWorld keeps one and discards the
other, so one of these animals does not exist in the shipped game and nothing says which.

🔑 **The collision has already produced two contradictory facts in our own files**, which is
how it was found. The two biomes that wire it each describe a *different* animal:

- `RUT_Desert.xml:259` — `0.5`, comment *"bokka - anywhere on the dayside, import"*
- `RUT_ExtremeDesert.xml:143` — `0.025`, comment *"bouldermit - giant, keep"*

The second names a third creature entirely (`AA_BoulderMit`) and calls it giant, which fits
`korrum` (4.00), not `bokka` (0.4). ⚠️ So that row may ALSO be a mis-wiring — someone may
have meant `AA_BoulderMit` and typed the stoneback. Check before deleting it, or the
Stillsand silently loses a giant it intended.

## why it blocks a ruling

The owner ruled 2026-09-21 that **an animal belongs to one biome** (`BIOME_SPECIFIC_FAUNA_LAW_1`)
and, asked where the stoneback should live, ruled *"Neither — give it to a thinner roster"*.
That ruling **cannot be executed as stated**, because "the stoneback" is two animals. BENCH
was about to give it to the Scarlands on the evidence that it is bodySize 0.4 and therefore
improves that roster's weak food pyramid (53.0% small, the thinnest of the candidates at 8
wired species) — a rationale that is **only valid if `bokka` is the survivor**. If `korrum`
(4.00) wins the collision, the same move puts a giant into the weakest pyramid on the planet.

⛔ Do not wire, unwire or evict any stoneback row until the identity is settled.

## needs him — one question

**Which creature keeps `RSW_Stoneback`, and what is the other one called?** Both are already
authored; this is a naming call, not new content. The likely shape: the BiomesTeam port keeps
a `BMT`-derived name and the DesertPort creature takes `RSW_Korrum` (or vice versa), after
which `BIOME_SPECIFIC_FAUNA_LAW_1` applies to **each** separately — two creatures, two homes.

## spec

1. Get the naming ruling above.
2. Rename the loser's `ThingDef` **and** its `PawnKindDef`, plus every reference: the two
   biome wirings, the five roster rows that name a stoneback (`desert.json` — renamed to
   `RSW_Stoneback` at `b173e699d` and now ambiguous, `arid_shrubland.json`,
   `the_scarlands.json`, `wasteland.json`, and whatever `dune_sea_deep_desert.json` intends
   given `RUT_ExtremeDesert` wires it with no roster row at all), and any texPath/art
   registry entry keyed on the defName.
3. Resolve `RUT_ExtremeDesert.xml:143` on its own evidence — is that row the giant it says
   it is (`AA_BoulderMit`), or a mis-typed stoneback?
4. Then, and only then, apply the one-home ruling to each creature.

## verify

`RSW_Stoneback` resolves to exactly one `ThingDef` and one `PawnKindDef`; the other creature
has its own defName; no roster row or biome wiring is ambiguous about which animal it means;
a load log shows no duplicate-defName error for either. ⚠️ The load-log half needs the
Desktop — it cannot be checked from the Mac.

## criteria

Every animal we ship has a name that means exactly one animal.

## Noted from the same measurement, and NOT a defect

The same scan reported **32** same-type/same-defName collisions. **30 of them are inert**: a
byte-identical copy of the vault def tree sits under
`src/RimUtinni/StructureInjectionsRUT/Source/Defs/`, duplicating
`.../Defs/VaultDungeons/`. The mod has no `LoadFolders.xml`, so RimWorld loads the root
`Defs/` only and never that `Source/` path — the copies are dead files, not live collisions
(⚠️ convention-based; the authoritative check is a load log on the Desktop). They are still
worth deleting, because they make every future defName measurement over-report by 30 — this
one did, before the def **type** was taken into account. Only `RSW_Stoneback` (its ThingDef
and its PawnKindDef) is real.

## ✅ RESOLVED 2026-09-22 — `4b068ea5d`, both animals kept

Owner ruled on the served identity sheet (`touchedBySheet=true`, `writeCount=6`, 2 notes,
0 overrides) plus his words in the same sitting.

- **bokka keeps `RSW_Stoneback`** and, his words, *"goes into any arid biome where it's needed
  (desert, extreme desert, or other hot arid day-side)"*. Sheet note: *"Arid biome approved,
  make sure our art is up to modern standards."*
- **The crab is `RSW_Korrum`** — *"equally belongs in canyons, arid, but is also excellent for
  scarlands"*. Sheet note: *"This is good for Scarlands. Regenerate art."*
- **Neither name was canon**, so nothing canon was renamed: 0 hits for bokka/korrum/stoneback
  in the 137-entry library, and the donors are a Biomes! cave reptile and an Alpha Animals
  rock crab. Both labels are ours, per `NONCANON_BEAST_RENAME_1`.

**SWBestiary now has 0 duplicate `(defType, defName)` pairs across 1,641 defs** (re-measured
by parsing every file).

### 🔑 The root cause was a guard that did not exist, not a careless port

Measured from git, and this is the part worth carrying:

| when | what |
|---|---|
| 2026-09-20 **10:50** PDT | `DESERT_PORT_DUPLICATE_DEFS_1` closed *"0 duplicates"*, deleting **366** duplicate DesertPort copies (`59ad6aa7d`). |
| 2026-09-20 **17:35** PDT | `DESERT_FAMILY_PORT_EXECUTION_1` added the `AA_BoulderMit` port under the already-taken `RSW_Stoneback` (`1ab7b6f09`) — **6 h 45 m later**. |
| 2026-09-22 | Found by hand, and only because a *label* mismatch made two biome comments disagree. |

That sweep's claim was TRUE when it was made. Nothing stopped the next commit from undoing
it invisibly, and the 349-duplicate sweep's own prose had even **named `RSW_Stoneback`** as a
known collision. ⇒ Built the missing guard:
`src/RimMandrake/Utils/selftest_no_duplicate_defs.py`, in the suite, **verified by
re-introducing the original bug and watching it fail (exit 1) then pass again**. It scopes
itself to paths RimWorld actually loads and reports the rest.

### the reference that would have failed silently

`RSW_Ferroclaw`'s `<useMeatFrom>`. Its comment records the donor pointing at `AA_BoulderMit`
and the port *"repointed to this batch's own RSW_Stoneback"* — i.e. it always meant the crab.
Left alone, Ferroclaw would quietly have yielded *bokka* meat. Now `RSW_Korrum`.
⚠️ The egg in `RSW_BiomesTeamPort_Items.xml` (`hatcherPawn`) **correctly stays** on
`RSW_Stoneback` — that is the bokka's own egg, not a missed rename.

`RUT_ExtremeDesert`'s 0.025 row was always the crab: its comment said *"bouldermit - giant"*
while the def it named was bodySize 0.4. That contradiction is what exposed the whole thing.

### two numbers are BENCH's, flagged in the files for overrule

- `RSW_Korrum` into `RUT_Scarlands` at **0.05, not the roster's 0.5**. That roster is the
  thinnest (8 species, total commonality 1.51) and the weakest pyramid (53.0% small); 0.5
  makes a mountain-sized crab a quarter of all sightings and drops it to ~40%. The 0.5 was a
  round2-mapping placeholder, not an ecology call.
- The **Wasteland** row read as the bokka, not the crab — *"canyons, arid"* could also claim
  it, and that biome needs small fauna more than another giant. Left admitted-but-unwired.

### still owed, from his two sheet notes

- `STONEBACK_BOKKA_ART_STANDARD_1` — the bokka's art is from the 2026-09-11 Biomes! port;
  he asked that it be brought *"up to modern standards"*. Judge it before regenerating.
- `KORRUM_ART_REGEN_1` — the crab has **no art of ours at all**: its `texPath` still points at
  `Things/Pawn/Animal/AA_BoulderMit/AA_BoulderMit`, the donor's own texture, which violates
  that port batch's own ruling. Its 3 jobs were **re-keyed `RSW_Stoneback_* → RSW_Korrum_*`**;
  they unblock ~2026-09-26 and would otherwise have overwritten the bokka's art.
