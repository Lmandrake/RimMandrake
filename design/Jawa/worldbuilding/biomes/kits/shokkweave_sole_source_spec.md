# SHOKKWEAVE_SOLE_SOURCE_1 — economy spec (DRAFT for build)

Engine mapping for the sole-source ruling in
`design/Jawa/worldbuilding/biomes/the_webwork.md` §6 ban 4 and §7 (frozen sheet,
`BIOME_FREEZE_FABLE_REVIEW_1`): **the silk IS hyperweave, renamed, and the ONLY
way to obtain it in the game.** This spec invents no lore. Every def field and
leak vector below was MEASURED against the frozen official dump
(`OFFICIAL-2026-08-29`, capture `2026-08-29T13-30-02Z`, post-inheritance) on
2026-09-11 unless marked ❓. Live trader generation is the proof standard the
sheet itself sets — the XML census here scopes the build; it never closes it.

Ruled inputs honored:
- **Border creep-web YIELDS, with teeth** (2026-09-11 card sitting, kit spec
  "Owner rulings" 4; owner-verbatim: "(2) but it has a small chance of SPAWNING
  an emergent Shokk to get you"). Supersedes the kit's no-yield placeholder.
- **Tier split** (ruling 6, `SHOKK_RSW_MOD_1`): the species and its mechanisms
  are RSW (`mandrake.rsw.shokk`, built); the economy — rename, trader strip,
  harvest wiring — is campaign law, so it ships RUT_ per
  `design/NAMING_SCHEME_PLAN.md`.
- The spawn hook is BUILT and waiting: `RSW_CompEmergentSpawnOnDestroy`
  (`src/RimStarWars/Shokk/Source/RSW_CompEmergentSpawnOnDestroy.cs`) — fires on
  `DestroyMode.Vanish` only, default `spawnChance` 0.03, soft PawnKindDef lookup,
  spawned Shokk goes manhunter. This item is its declared consumer.

---

## 1. The rename — label, never defName

**`Hyperweave` keeps its defName** (Core, shortHash 26103): hundreds of inbound
refs — 617 RecipeDefs touch it as an ingredient/filter entry (MEASURED), plus
savegame Things and stuff-refs. A defName swap would orphan all of it for zero
player-visible gain. The rename is a PatchOperationReplace on:

- `label` → `shokkweave`
- `description` → rewritten. The vanilla text ("production mechanites… known
  only to the most advanced glitterworld cultures") is WRONG here and is
  replaced outright, per the deletion rule — new text is the sheet's: the
  Wyyyschokk's silk, cut from the loom, superb armor material, obtainable
  nowhere else.
- `stuffAdjective` is null (MEASURED), so "shokkweave duster" etc. derive from
  the new label automatically — no second patch point.

Consumer recipes ("make X from hyperweave") pick up the label at runtime;
nothing else renames. ❓ At build, sweep live `keyed`/description strings that
say "hyperweave" in prose (settings menus of donor mods) — flavor only, fix
what a player actually sees.

## 2. The trader strip — one structural kill, then the census

**The mechanism is one field, not eleven patches: `tradeability` All →
`Sellable`.** Traders then never stock or generate it by ANY route — SingleDef,
tag, category — while colonists still sell it (the §7 economy register: the
smuggler's jackpot needs a buyer). Stock-generator handling of `Sellable`
❓verify at build against `StockGenerator.HandlesThingDef`/`Tradeability`
semantics before trusting it alone.

Census of who stocks it today (frozen dump, 11 TraderKindDefs — the list the
live proof must clear):

| Route | Traders | Note |
|---|---|---|
| `StockGenerator_Tag` `ExoticMisc` | `Base_Empire_Standard`, `Base_Outlander_Standard`, `Caravan_Outlander_Exotic`, `Orbital_Exotic` (jm.bettertraders); `DV_Base_Keshig_Standard`, `DV_Caravan_Keshig_Exotic` (det.keshig) | never name Hyperweave — reached through its `tradeTags: [ExoticMisc]`. Belt-and-braces: also patch the tag off the ThingDef |
| `StockGenerator_SingleDef` | `AM_AncientLogisticsSystem` (10–30); `guy762_BaseTraderKind_Czerka`/`guy762_TraderKind_Czerka` (500–1000!); `guy762_BaseTraderKind_HuttGalleon`/`guy762_TraderKind_HuttGalleon` (100–250) | the KotOR traders are the flood; `tradeability` kills them without touching guy762's XML |
| `StockGenerator_Category` `Textiles` | HuttGalleon pair | already excludes Hyperweave — no action, but the live proof covers it |

**Two non-trader leaks the ban also covers** (§6 ban 4 says "from any source
but the Webwork"; a trader is only the named example):

- **Quest rewards — REQUIRED strip.** `thingSetMakerTags: ["RewardStandardCore"]`
  MEASURED on the def: raw hyperweave is in the standard reward pool today.
  Patch the tag off. (XML-declared ThingSetMakerDefs: 0 hits — the pool is
  dynamic, which is exactly why the tag matters.)
- **Cargo/resource pods** ❓ — verify at build whether `tradeability: Sellable`
  already excludes it from pod contents; if not, the pod-contents route needs
  its own exclusion. Rides the live-proof pass.
- **Stuff-rolled gear** — `stuffProps.commonality` 0.1 (MEASURED): traders,
  raiders and reward generators can roll apparel MADE OF shokkweave. The
  resource never comes back out of tailored apparel, so the resource
  sole-source holds either way — but the armor material itself walks in on a
  raider's back. **CARDED** (card 1); until ruled, commonality stays.

No recipe produces it (MEASURED: 0 of 617), no WorldObjectRecipeDef touches it.

**The live proof** (the sheet's own standard: "proven against live trader
generation, not the XML"): bridge/dev-mode generation of each of the 11 trader
kinds plus a sample of unlisted kinds, N❓INVENTED ≥ 20 rolls each, assert zero
Hyperweave stacks in generated stock. FOUNDRY work, quicktest map, never a cold
load. Zero rows generated is a failed instrument, not a pass.

## 3. The harvest routes — three from the sheet, one ruled in

All yields ❓INVENTED, expecting a live-balance pass. Sole-source guard from the
kit spec stands: beetle-destroyed and combat-destroyed web drops NOTHING —
yield only on deliberate player harvest (`DestroyMode.Vanish`, the same edge
the spawn comp keys on).

1. **Web-cutting (in-biome).** The RUT_ web/anchor/gutter ThingDefs (roster
   item, unbuilt) carry harvest yield ❓~2–5 shokkweave per line-segment. The
   cost is built into the kit: cutting web "rings the line you cut" —
   `RM_MapComponent_SenseWeb` felt-marks the cutter (kit §1). No new mechanism.
2. **Butchery (small yield).** Patch the Wyyyschokk ThingDef
   (`mlie.starwarsanimalcollection`, `MayRequire`d): `butcherProducts` is null
   today (MEASURED) — add Hyperweave ❓~10–20. `race.leatherDef`
   (`Leather_Insectile`) untouched: the silk is IN the spider, not its hide.
3. **Nest raid (the jackpot).** The nest ThingDef (roster item, unbuilt):
   Shokkweave in the walls per §8 — deconstruct/harvest yield ❓~40–80, under
   the mother and the convergence. Priced in risk like the eggs.
4. **Border creep-web (RULED).** The creep-web variant `RM_MapComponent_FrontCreep`
   spawns on border maps is harvestable — yield ❓~1–3 per cut — and carries
   `RSW_CompEmergentSpawnOnDestroy` via a patch with
   `MayRequire="mandrake.rsw.shokk"` (the cross-boundary pattern
   `RUT_Webwork.xml` already uses). Comp defaults stand (chance 0.03,
   manhunter) unless the balance pass moves them.

## 4. Home, tier, build order

**Home**: one RUT_ patch mod, proposed `src/RimUtinni/ShokkweaveEconomy/`
(packageId `mandrake.rut.shokkweaveeconomy`) — the rename and strip are
campaign law on third-party defs, exactly what a Utinni-tier patch mod is for.
No C# anywhere in this item.

Order: **1)** rename + tradeability + tag strips (one patch file, no
dependencies, provable the next quicktest) → **2)** live trader-generation
proof → **3)** butchery patch (needs only the donor mod, live now) → **4)**
web/nest/creep yields as the roster and `RM_MapComponent_FrontCreep` land.
Routes 1/3/4-yield block on the roster item; nothing blocks the strip.

## verify

Live trader generation shows zero hyperweave/Shokkweave stock across all
generated kinds; a quest-reward roll pass shows none; butchering a Wyyyschokk
yields it; border creep-web cut yields it and can spawn the emergent Shokk
(comp already proven in `SHOKK_RSW_MOD_1`).

## Cards (open)

1. **Stuff-rolled shokkweave gear** — `stuffProps.commonality` 0.1 lets
   traders/raiders/rewards generate apparel MADE OF shokkweave (the fabric
   never recoverable). (a) Zero it: nothing anywhere is generated of
   shokkweave; player crafting and biome routes untouched — "the ONLY way to
   obtain it" reads absolute, recommended. (b) Keep it: shokkweave gear
   exists offworld as flavor; only the raw fabric is sole-source. Trade: (a)
   also strips it from raider drops — slightly fewer exotic lootables; (b)
   lets a rich player buy the armor benefit without ever touching the Webwork.
