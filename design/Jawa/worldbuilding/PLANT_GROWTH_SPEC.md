<!-- status: live -->
# PLANT_GROWTH_SPEC.md — freakish plant growth, specified for build

DECIDE owns this spec; **BUILD owns the implementation.** Written 2026-08-15 at
the owner's instruction to spec the planetary fast-growth fact completely and hand
it over.

**The planetary fact, already decided:** every plant on this world grows at a rate
that reads as *obtrusive, aggressive, wrong*. Vegetation should feel powerful — a
force the colony pushes back against rather than a crop it waits for.

**Why it matters beyond flavour:** `hydrology_and_fire_ecology.md` R-H3 makes fast
growth the fuel supply for a savanna that burns forever. Without this, the fire
ecology has nothing to burn and the whole high-risk/high-reward design for the
savanna collapses. This is load-bearing.

---

## R-G1 · The lever is a Harmony postfix, NOT an XML sweep

**Rationale, so the choice is not relitigated:** PatchOperations cannot do
arithmetic. There is no `PatchOperationMultiply`, so an XML approach means writing
a literal `growDays` for **every** plant — 566 of them across dozens of mods —
which is brittle, silently misses any plant added later, and produces an enormous
diff nobody can review.

⇒ **One Harmony postfix on `Verse.Plant.GrowthRate`**, multiplying the returned
value. One lever, applies to every plant from every mod including ones we never
enumerated, and it is a single line to tune or revert.

```
[HarmonyPatch(typeof(Plant), nameof(Plant.GrowthRate), MethodType.Getter)]
static void Postfix(Plant __instance, ref float __result)
```

⚠️ **Verify the member before writing the patch.** `GrowthRate` is a property
getter in 1.6, but confirm against the assembly rather than this document —
`strings -a -el` on `Assembly-CSharp.dll`, per the project's standing rule never to
guess a member. If `GrowthRate` turns out not to be the single funnel, the correct
target is whatever `GrowthPerTick` consumes.

**It must remain visible.** The inspect string showing growth rate should reflect
the boosted number, not the base one — a player who cannot see the world is strange
has not been told anything.

## R-G2 · The multipliers

| class of plant | multiplier | reasoning |
|---|---|---|
| **Wild plants and crops (default)** | **×4.0** | Corn's ~11.6 growDays becomes ~3. Fast enough to be startling on first sight, which is the entire point |
| **Trees** | **×2.5** | Trees are a *wood economy*, not scenery. At ×4 lumber stops being a decision. Still visibly unnatural |
| **Plants on the terminator (poison forest)** | **×0.4** | 🔴 See R-G3. This is the exception that makes the rule readable |

**All three live in one config class as named constants**, not scattered literals.
The owner will want to tune these after seeing them in motion, and tuning must not
mean recompiling three files.

⚠️ **Do not exempt player crops.** The fiction is planetary, so the physics cannot
notice who planted it. The instinct to protect farming balance is answering the
wrong question: **on this world the limit on agriculture is WATER, not time**
(`water_doctrine.md`). Growing food quickly on a planet where you cannot water it
is exactly the tension the campaign wants. Fast crops make the water economy
*sharper*, not slacker.

## R-G3 · The terminator exception, and why it must not be dropped

`hydrology_and_fire_ecology.md` **R-H2b** rules that the poison forest on the shade
side of the terminator is **stunted** — the one place on the planet where growth
has stalled, because its water arrives as trace condensation rather than as flood.

**A global multiplier would flatten exactly the biome whose identity is that it
does not grow.** So the postfix must be biome-aware: read the plant's map biome and
apply the terminator multiplier there.

```
if (biome is a terminator/poison-forest biome)  -> TERMINATOR_MULT
else if (thing is a tree)                       -> TREE_MULT
else                                            -> DEFAULT_MULT
```

**The biome set is a list in config, not a hard-coded defName.** Chain step 8 is
ratified but the terminator biome roster is not final, and `PoisonForest` and its
Advanced Biomes relatives are the current candidates — DECIDE will supply the
final list. Ship it reading from a `List<string>` so the list can change without a
rebuild.

## R-G4 · Wild regrowth is a SECOND lever, and XML this time

Individual plants growing fast does not repopulate a burnt map. That is governed
by **`BiomeDef.wildPlantRegrowDays`**, which controls how quickly wild plants
*reappear*, and it is untouched by R-G1.

🔴 **Both levers are required.** Fast growth without fast regrowth gives a savanna
that burns once and stays black — the fire ecology needs the fuel to come back.

- **Patch `wildPlantRegrowDays` down across the biomes we keep.** This one *is*
  XML, because it is a small number of literal values on ~66 defs *(as of
  2026-08-15, at modCount 585; the live dump of 2026-08-20 at modCount 578 reports
  **80** `BiomeDef`s — see the note at R-G4 below)* rather than
  arithmetic over hundreds.
- **Target: divide by ~4**, matching R-G2's default so the two levers agree.
- ⚠️ **Wait for the biome cut list.** *(The review completed 2026-08-15 and its tool
  `biome_review.py` was retired 2026-08-20 — the cut list is
  `observed/inventory/decisions_biomes.json`, **30 cut of 66 as of 2026-08-15**.)*
  Patching a biome we are about to cut is wasted work and a wasted diff.
  **R-G1 can ship immediately; R-G4 waits.**

  > ⚠️ **Stamp on the 66, added 2026-08-20.** That 66 was measured on 2026-08-15
  > at modCount 585. The live def dump of **2026-08-20 (modCount 578, matching
  > `ModsConfig.xml` exactly) reports 80 `BiomeDef`s**, so `66 − 30 = 36` can no
  > longer be re-derived from the current game. **36 survivors still stands — it
  > is the record of a decision, not a live count.** ⛔ Do NOT recompute it
  > against 80; the owner cut 30 *specific* biomes, named in
  > `decisions_biomes.json`, and that roster is the answer. 🔑 **For R-G4 this
  > matters practically:** patch the biomes on the survivor roster, not "66 minus
  > 30" worth of whatever the current dump lists. Canon:
  > `infrastructure/state/canon.yml > biomes`.

## R-G5 · Exemptions to check before shipping

Plants whose slowness is a *mechanic* rather than a growth rate. Quadrupling these
breaks systems that have nothing to do with our fiction:

- **`Plant_TreeAnima`** — anima tree. Its growth is ritual pacing, not botany.
- **`Plant_TreeGauranlen`** and the dryad economy.
- **`Plant_Ambrosia`** — a deliberately scarce drug source.
- **Anything a quest or ritual times against**, and any plant whose `growDays` is
  already under ~1 day (multiplying a near-instant plant achieves nothing and can
  produce silly per-tick values).

**Handle these as a named exempt list in the same config**, so the reasoning is
visible next to the multipliers rather than buried in an `if`.

## R-G6 · Verification — what proves this worked

- A quicktest map: wild grass visibly regrows within a session, and a sown crop
  reaches harvest in roughly a quarter of its usual time.
- **A tree does NOT keep pace with the grass** — that is the ×2.5 band working.
- On a terminator/poison-forest map, growth is visibly *slower* than vanilla, not
  faster. This is the check most likely to be skipped and the one that proves the
  biome-aware branch actually runs.
- The anima tree is unchanged.
- No error on load, and no per-tick performance regression on a large map — a
  getter postfix runs extremely often.

⚠️ **A quicktest is ~90 s and answers all of the above.** Do not wait for a cold
load to check this.

---

## What DECIDE still owes

- **The final terminator biome list** for R-G3, after the owner's biome review.
- **The biome cut list** before R-G4 can be patched.

Neither blocks R-G1, which is the whole visible effect and should ship first.
