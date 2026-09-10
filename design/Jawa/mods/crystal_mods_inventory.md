# Crystal mods inventory — `CRYSTAL_MODS_INGEST_1`

_BENCH research pass, 2026-09-08. Def dump `mods=596/cec112bad2152f47 captured=2026-09-05T14:41:26Z`
(measured via `measure` — `~/.claude/skills/measuring-large-artifacts`), cross-checked against mod
XML on disk. Read against `design/Jawa/worldbuilding/biomes/the_lantern_deeps.md` (frozen
`BIOME_FREEZE_FABLE_REVIEW_1`) — this doc proposes, it does not rule._

## 1. The orange glowing crystal — identified: pyrinth

**`DV_MineablePyrinth`** (label "pyrinth"), from **Epochs — Pyrinth**
(`det.epochspyrinth`, workshop 3336544632, active). Identified by the owner from
memory at the 2026-09-09 sitting and confirmed against the mod's XML on disk.
(An earlier pass misidentified `KOTOR_SmallCrystal_orange`; that claim is
removed — the KOTOR family remains in §2 as one of the inventory systems, and
its provenance caveat is kept below.)

Evidence, read from the mod's own XML:

- **The mineable itself glows**: `glowRadius 3`, `glowColor (192,117,77)` —
  warm orange — with orange spark motes `(229,118,46)` (`DV_Mote_PyrinthSpark`).
- **Vanilla scatter, no biome gate**: `mineableScatterCommonality 0.1`,
  lump size 5–6 — it appears on ordinary maps today, exactly like kyber.
- **Yield**: vanilla path — `mineableThing DV_Pyrinth` × 10 (a ResourceBase item).
- **A product family consumes it**: pyrinth torch / wall torch / pylon
  (`DV_PyrinthLamp`/`DV_PyrinthWallLamp`/`DV_PyrinthBrazier`), a pyrinth
  heater, and a magic melee weapon — primitive glowing-ore lighting, a natural
  Jawa/Utinni register.

### Leftover caveat from the KOTOR provenance (kept — it matters for §2's KOTOR row)

**Caveat, not chased further:** the *standalone* genstep `KOTOR_CrystalFormation`
(order 1100, `guy762.mm.kotorcore`, also absorbed into our Armoury pack as
`Absorbed_KotorCore_CrystalMapGenerator.xml`) resolves in the live dump to a **single**
scatter group containing only `KOTOR_StygiumCrystal` — the repo's copy of that same
file still lists all 7 colors + 3 medium + Stygium. Something between our repo file and
the deployed/live game state trimmed it (a newer kotorcore version, a load-order
override, or a deploy drift — CLAUDE.md's standing warning that "the repo copy is
never what the game loads" applies here). **Does not affect §1** (pyrinth is a different mod entirely); it matters for the
KOTOR row in §2:  `KOTOR_CrystalFormation`'s current live
scatter is Stygium-only, not the multicolor list the repo file shows.

### Candidates ruled out

| candidate | why ruled out |
|---|---|
| `Force_CrystalFormation_Small/Medium/Large` (ThingDef, **Star Wars: The Force — Lightsaber**, `lee.theforce.lightsaber`, still active) | Separate, un-absorbed mod. Default `graphicData.color` is white `(1,1,1,1)`; actual color comes from `ColorGenerator_Options` rolled per-instance — orange is one option among ~20, weight 6 of ~215 total (≈3%). Not a fixed/labelled "orange crystal," a random kyber-formation roll. |
| `guy762_focuscrystal_BiomeCrystal` ("ready-made biome crystal" per the Lantern Deeps sheet §7) | **Not found** under that literal defName (0 hits, full dump coverage). Closest real defs: `guy762_SWForceLightsabersPartCategory_focuscrystal` (HiltPartCategoryDef) and `guy762_SWForceLightsabers_CrystalPart_*` (HiltPartDefs) — lightsaber-crafting components, not a scatterable ThingDef. The sheet's citation needs correcting or is describing something not currently in the dump. |
| `BMT_Crystal_Blue{Small,Medium,Large,Huge,Sowable}` (Biomes! Caverns native) | Blue only (`glowColor (119,189,239,0)`), not orange — this is the lanternstone candidate (below), not the orange crystal. |
| GRiNDTerra Biomes' `CrystalSmall`/`CrystalBig`/`CrystalShard` | Decorative wild-grass `ThingDef`s (`Plants_Crystal_Flowers.xml`) — no glow comp, no `harvestedThingDef`, not mineable. Cosmetic ground cover, not a harvest system. (Note: the item spec's "GRiNDTerra" candidate was written as "GRiNDTerra"; the live packageId is `grimterra.biomesmod`/`grimterra.terrainretexturemod`/`grimterra.worldmap` — same mod, "GRiNDTerra" is its display name.) |
| Alpha Biomes `AB_CrystalHorn`/`AB_CrystalFlower`/`AB_CrystalWood` | `graphicData.color (1,1,1,1)` — no distinctive tint, no glow comp found. Ruled out on both label and evidence. |
| "lanternstone" (defName) | **Measured 0** — full dump coverage, absence confirmed. It's a design-sheet working name, not an implemented def; the actual native blue crystal resource is `BMT_ResourceBlueCrystal` (below). |

## 2. Full crystal-harvest inventory

| system | mod (packageId) | def(s) | mechanism | yield | where it spawns today |
|---|---|---|---|---|---|
| **KOTOR crystal formations** (incl. orange) | absorbed → `mandrake.rsw.armoury`; donor `guy762.KotORWeapons` (retired) | `KOTOR_SmallCrystal_{red,orange,yellow,green,blue,purple,white}`, `KOTOR_MediumCrystal_{cool,soft,warm}`, `KOTOR_LargeCrystal_{cool,warm}`, `KOTOR_StygiumCrystal` (all `ParentName=KOTOR_CrystalFormation_Base`, `guy762.mm.kotorcore`, still active) | Mineable; `SecondaryMineableYield.ModExtension_SecondaryMineableYield` (60%×2 / 20-40%×1) | `guy762_crystalitem_<color>` → `guy762_SWForceLightsabers_CrystalPart_<color>` HiltPartDef (lightsaber focus crystal) | `BMT_CrystalsGenerator` (Biomes! Caverns' own genstep, order 320, patched by our absorbed injector) — **gated to `BMT_Crystal` terrain affordance = crystal-cavern maps only**. Standalone `KOTOR_CrystalFormation` genstep (order 1100) exists too but currently resolves Stygium-only live (see caveat above). |
| **Kyber (lightsaber mod)** | Star Wars: The Force — Lightsaber (`lee.theforce.lightsaber`, active, **not** absorbed) | `Force_CrystalFormation_{Small,Medium,Large}` (mineable) → `Force_KyberCrystal` (item) | Vanilla `building.mineableThing`: Small→1, Medium→2, Large→3 `Force_KyberCrystal` | `Force_CrystalFormation` genstep (order 1100, `countPer10kCellsRange 1-5`, `allowInWaterBiome false`, no biome gate visible) — reads as a general-map scatter, not caverns-specific | Crafts into lightsabers via `ColorGenerator_Options`-tinted hilt crystals; the raw `Force_KyberCrystal` item itself is also `scatterableOnMapGen true`. |
| **Lanternstone** (native Biomes! Caverns crystal, design working-name) | Biomes! Caverns (`biomesteam.biomescaverns`, active) | `BMT_Crystal_Blue{Small,Medium,Large,Huge}` (wild, **not harvestable** — each carries `CompProperties_Explosive`, wickTicks 240, radius 1.5→3.9, "surprisingly volatile"); `BMT_Crystal_BlueSowable` (plantable variant) | Sowable variant only: `plant.harvestedThingDef = BMT_ResourceBlueCrystal`, `harvestYield 6`, `growDays 33.3` | Native to `BMT_CrystalCaverns` biome's `wildPlants` list (donor inventory, already documented in the Lantern Deeps sheet §0/§7) | Matches sheet's "blazing beacons" / blasting-material framing exactly — this **is** lanternstone in all but name. |
| **GRiNDTerra crystal flora** | GRiNDTerra Biomes (`grimterra.biomesmod`, active) | `CrystalSmall`, `CrystalBig`, `CrystalShard` (Plant, `Plants_Crystal_Flowers.xml`) | None — no `harvestedThingDef`; `ingestible: true` at base-plant default only, described as inedible "bizarre grass" | Cosmetic ground cover, listed among `BMT_CrystalCaverns`'s cross-mod-compat `wildPlants` (commonality 1 / 0.32 / 0.068) | Decorative only — not a resource system. |
| **Alpha Biomes crystal flora** | Alpha Biomes (`sarg.alphabiomes`, active) | `AB_CrystalHorn` (plant) → `AB_RawCrystalHorn` (item, yield 10); `AB_CrystalFlower` (plant) → `AB_CrystalWood` (item, yield 25, also a stuff/terrain material — `AB_AlienWoodFloors_CrystalWood`) | Vanilla plant harvest | White-tinted (`1,1,1,1`), no glow | Alpha Biomes' own biomes (not traced further — out of scope; no cavern/orange connection found). |
| **Alpha Animals crystal fauna** | Alpha Animals / Alpha Genes | `AA_CrystallineCaracal`, `AA_CrystalMit`, `AA_UraniumCrystals` (creature + gene-summon defs); `BMT_Crystalope`/`Crystalback`/`Crystal Crab`/`Crystal Fairy Mole`/mantis-kin (Biomes! Caverns donor fauna) | Creature, not a harvest | — | 🔴 Already **ruled evicted** by the Lantern Deeps sheet §0 ("a bit hokey... I'd rather have crystals AS creatures") — listed here only for completeness of the "crystal" search, not a live candidate. |

## 3. Ingest assessment

The Lantern Deeps sheet (§7) already anticipates this: *"The orange glowing crystal
from one of our mod imports — housed here too... examines ingesting that mod so every
crystal harvest lives in one place."* Given what's actually in the stack:

| system | recommendation | effort | why |
|---|---|---|---|
| **Pyrinth — §1's orange ore** | **Ingest — absorb + gate.** Absorb `det.epochspyrinth`'s ore/resource/torch family into our tier per the naming grammar; retarget its ungated 0.1 scatter to Lantern Deeps maps (the same gate pattern §3 already prescribes for kyber). Keep the torch/pylon/heater family — glowing-ore lighting is exactly the Deeps' lanternstone culture, in orange. | **Medium** — absorption pass + scatter gate; small mod, ~a dozen defs. | Owner-identified 2026-09-09. Active and healthy, but its ore spawns on ordinary maps everywhere, contradicting the Deeps' uniquely-available ruling. |
| **KOTOR crystal formations (incl. orange)** | **Ingest — mostly done.** Retarget the caverns-gated `BMT_CrystalsGenerator` injection (already ours) to fire specifically inside Lantern Deeps cave maps rather than every `BMT_CrystalCaverns` map; keep the 7-color family as flavor variety around lanternstone/kyber, or fold the color naming into `KOTOR_SmallCrystal_orange`'s in-fiction identity so it reads as a Deeps mineral rather than a leftover lightsaber-crystal palette. | **Small** — the absorption and the genstep wiring already exist; this is a design/labeling pass plus resolving the `KOTOR_CrystalFormation` live-vs-repo discrepancy (verify which genstep is actually firing before touching either). |
| **Kyber (`Force_CrystalFormation_*` / `Force_KyberCrystal`)** | **Ingest — this is the sheet's kyber**, already the right fiction ("quiet where lanternstone glows... the Rakata came for kyber"). Not yet absorbed into our tier; `lee.theforce.lightsaber` stays a live donor. Gate its genstep to Lantern Deeps maps (currently a general 1-5-per-10k-cell scatter with no biome restriction) so kyber stops appearing on ordinary surface maps outside the Deeps, per the sheet's uniquely-available ruling (§7). | **Medium** — needs an absorption pass (`gen_*_absorption.py`-style) plus a new genstep gate; `KYBER_TRADE_PLOT_1`'s illegality/heat mechanic is a separate, larger owed item. |
| **Lanternstone (`BMT_Crystal_Blue*` / `BMT_ResourceBlueCrystal`)** | **Leave as-is, rename in fiction only.** Mechanically it already IS lanternstone (volatile, glowing, blasting-grade) — Biomes! Caverns is the Lantern Deeps' own donor mod, already fully credited in the sheet. No code change; a label/description pass (owner-ratified name is already "lanternstone") is enough. | **Trivial.** |
| **GRiNDTerra crystal flora (`CrystalSmall/Big/Shard`)** | **Cut from the "crystal harvest" conversation** — these are cosmetic grass with no yield, already just background wildPlants in `BMT_CrystalCaverns`. Leave them as ambient set-dressing (or evict alongside the other non-crystal cave fauna judged at the assignment sitting) rather than treating them as a harvest system to unify. | **None needed** — no mechanism to ingest. |
| **Alpha Biomes crystal flora (`AB_CrystalHorn`/`AB_CrystalFlower`)** | **Leave.** No glow, no cavern tie, own Alpha Biomes habitat — nothing here reads as Lantern Deeps material. Not a candidate for unification. | **None.** |
| **Crystal-studded fauna (Alpha Animals + Biomes! Caverns crystalope line)** | **Already ruled — evicted** (sheet §0, owner's ruling). No further action; listed here only so the census is complete. | — |

### RULED (owner, 2026-09-10 morning batch)

The §3 ingest table is **ratified** — natural abundance gated uniquely to the
Lantern Deeps as recommended (pyrinth absorb+gate, kyber absorb+gate, KOTOR
labeling pass + live-vs-repo genstep resolution, lanternstone rename-in-fiction).
**Addition, his words:** crystals showing up *"in trader inventories or as loot is
very fun. It should be expensive indeed."* — so the Deeps gate applies to natural
scatter only; expensive trader stock and loot appearances are wanted. Priced and
placed under `ECONOMY_TRADE_SWEEP_1` (a full what-is-sold-where-and-when sweep,
scheduled for the end of the world sweeps).

**Bottom line for the owner's ruling:** two real crystal-resource systems already sit in
the stack pointed at the Deeps — KOTOR-family formations (already
absorbed; the family's orange member is NOT §1's pyrinth) and the lightsaber mod's kyber (not yet absorbed) — plus the native
Biomes! Caverns blue crystal that already IS lanternstone. The unify-into-one-system
work is mostly **retargeting genstep gates to Lantern Deeps maps**, not building new
mechanism. GRiNDTerra's and Alpha Biomes' "crystal" defs are false leads (decorative
grass and an unrelated plant family respectively) and don't belong in the unification.

## 4. What could not be established

- **Why `KOTOR_CrystalFormation`'s live groups differ from the repo's absorbed copy**
  (Stygium-only live vs. full 12-entry list in
  `Absorbed_KotorCore_CrystalMapGenerator.xml`) — UNMEASURED. Needs a deploy-vs-repo
  diff (`rimworld-deploy` skill) or a check of whether `guy762.mm.kotorcore`'s current
  Workshop version shipped an update; not chased further since it doesn't change the
  orange-crystal finding.
  Sample: `python3 ~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py sql "SELECT json_extract(json,'$.fields.genStep.groups') FROM defs WHERE def_name='KOTOR_CrystalFormation'"`.
- **`guy762_focuscrystal_BiomeCrystal`** cited in the Lantern Deeps sheet §7 as the
  "ready-made biome crystal" — absent from the dump under that exact name (measured 0,
  full coverage). Either the sheet's citation is imprecise, or it names a def from a mod
  no longer active; not resolved here.
- **Alpha Biomes crystal defs' spawn biome** — which `BiomeDef` places `AB_CrystalHorn`/
  `AB_CrystalFlower` was not traced (ruled out as an ingest candidate before it mattered).
