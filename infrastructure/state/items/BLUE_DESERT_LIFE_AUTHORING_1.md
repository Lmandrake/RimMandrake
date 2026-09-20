# BLUE_DESERT_LIFE_AUTHORING_1 — the Blue Desert's life was commissioned, never built

## why this exists

The owner asked, 2026-09-20: *"Blue desert should have some life. I thought we
had commissioned some hydrocarbon based strange life growing there. No?"*

He is right. `RUT_BlueDesert` is **1,029 tiles carrying zero fauna and zero
flora** — `<animalDensity>0</animalDensity>`, `<plantDensity>0</plantDensity>`,
an empty `<wildAnimals />`, no `<wildPlants>` element at all — and that is a
**gap, not design intent**. The def's own comment says so:

> *"Zeroed, not the sheet's donor-read 0.5/0.33: nothing to scale until
> Swallowers/Burners/Pickers and the transparent fractal flora exist."*
> *"The Burners and the rest of the Blue Desert's intended life are new defs,
> not pool creatures."*

The donor read it inherited was animalDensity **0.5**, plantDensity **0.33**.
Those are the numbers to restore once the cast exists — not invented ones.

⚠️ **BENCH first recorded this biome as "deliberately sterile by design"** and
published that to the owner, to a running subagent, and into
`infrastructure/state/facts/biome_rosters.md`, on the strength of the zeroed
densities plus the word FROZEN on the sheet. The refuting sentence was in the
same file a few lines down. Corrected on his word; the fact file now carries the
correct reading. 🔑 An empty table is a question, not an answer.

## the cast — owner-ratified, already specced

Source of truth is `design/Jawa/worldbuilding/biomes/the_blue_desert.md` §
"Hydrocarbon biology" and § "How the biology adapted". It is **ratified design,
not a proposal** — read it before authoring anything, and do not re-litigate it.

**The admission test: hydrocarbon-metabolic, cold-stable, warm-reactive.
Nothing water-based lives here.**

- ⭐ **The Swallowers** — herbivores. They close their mouths over a plant, tear
  it up **whole-rooted**, and swallow, keeping oxygen (and the risk) away until
  the anaerobic gut. Slow, sealed, armoured; **wound one in the wrong place and
  it goes up.**
- ⭐ **The Burners** — the fast oxidizers. Their bodies **blaze with a halo of
  blue fire** when they move very fast or fight hard, and they **explode if
  wounded too greatly**. They run hot and die young.
- **The Pickers** — scavengers working the ablation line where the sky's debris
  surfaces.
- **The flora** — **transparent** (they need no light), growing **fractal
  branches for gas exchange** instead of leaves: ferns, dandelions, fuzzballs.
  Every one a charge of liquid butane. **Plants stay small** — no polar water
  molecule means inefficient transport. Wild only; §6 bans cultivation.

🔴 **Not a fire — an explosive chain reaction.** Cold makes them very hard to
ignite; once they go, they go all at once.

⛔ **The spore forms are NOT residents** — the Horrors' cold-storage crysalises
are cargo in the ice, injected by `HORRORS_RAIDING_FACTION_1`. Do not put them
in `<wildAnimals>`.

## the bans that constrain authoring (sheet §6)

1. 🔴 No water-based plants or animals — an ordinary water metabolism disqualifies
   a def outright. This is why no donor pool creature can be borrowed here.
2. 🔴 No cultivation of the hydrocarbon flora (owner: beyond the scenario's scope).
3. 🔴 No warm-safe hydrocarbon organics — plant, produce and creature-product defs
   must carry the warm-reactivity.

## spec

1. **Design pass first** — `kind: design`, so per `Agent_Policy.md` it is
   backgrounded to a Fable subagent, never done in-window. Output is a creature
   brief per kind (Swallower / Burner / Picker) and one for the fractal flora
   family, grounded the way `goo_boom_commission.md` was: real Core source read
   for every mechanical claim, not invented numbers.
   🔑 The **Burner's detonation-on-death** and the **flora's warm-detonation
   comp** both want `DeathActionWorker_*` / explosion source read properly —
   `GOO_BOOM_COMMISSION_1`'s brief already caught that blast radius is picked by
   **life-stage index, not adulthood**. Reuse that finding; do not rediscover it.
2. **Art** — the transparent fractal flora is on the NEW-ART ledger. Jobs go
   through `fill_queue.py` only. Transparency and fractal branching are the two
   things a render must actually show.
3. **Defs** — new ThingDefs/PawnKindDefs, ours (`RUT_` tier per
   `NAMING_SCHEME_PLAN.md`), plus the halo VFX and detonation comps.
4. **Wire** — populate `<wildAnimals>`/`<wildPlants>` on `RUT_BlueDesert` and
   restore `animalDensity` 0.5 / `plantDensity` 0.33 (the donor read), in the
   same change, so the biome is never left with a cast and no density.
5. **Mod Settings** — per the standing rule, every shipped mechanic gets a
   toggle; the detonation behaviours are exactly the kind a player may want off.

## Watch out

- ⛔ **Do not solve this by importing pool creatures.** The def comment rules it
  out explicitly and §6 ban 1 makes every water-metabolism donor ineligible. If
  a later pass proposes borrowing something here, that is a regression.
- The sheet is FROZEN — it is the target, not a draft to edit. If something in it
  is *false* (as opposed to merely inconvenient), correctness outranks the freeze:
  fix it and say what was wrong.
- `RUT_BlueDesert` shares its tiles with `BiomeGRimond` while the world paint is
  switched over — check which def the live world actually carries before
  concluding a spawn failure is a def bug.
- This biome is frigid (median −42.6 °C). Tolerances must cover it, or the cast
  will be authored and then die on contact with its own biome.

## verify

A live look: stand on a Blue Desert map and see transparent fractal flora on the
ground and at least one of the three fauna kinds moving. Then a post-load def
dump confirming the new defs resolved and the densities read 0.5 / 0.33 — not the
patch file, which proves nothing.

## criteria

The Blue Desert reads as inhabited by something strange and hydrocarbon-based
rather than as an empty plateau, and nothing in it runs on water.
