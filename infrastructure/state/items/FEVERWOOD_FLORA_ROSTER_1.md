# FEVERWOOD_FLORA_ROSTER_1 — 18 invented plants, replacing 7 donor placeholders

## spec

🔑 **The roster document IS the spec:**
`design/Jawa/worldbuilding/biomes/fever_wood_flora_roster_2026-09-23.md` — 18 `RM_` rows
with a silhouette brief each, grouped by **height above the water** (3 towers · 8 crown ·
4 pool margin · 3 ground), plus a legibility matrix that is the acceptance test.

**Owner's standing instruction, 2026-09-23:** invent our own complete roster first, then look
for Star Wars injection **opportunistically** — *"not trying to inject any-old-thing just
because it's not obviously wrong."* Under `biome_mod_architecture.md` **Q11a** an invented
exotic name is **not IP**, so all 18 live in the franchise-free tier and the free mod is rich
on its own.

## what is being replaced

🔴 `RUT_FeverWood` currently carries **7 donor plant rows** — 5 Alpha Biomes, 3 genuine canon
Star Wars, 1 ported stopgap. `AB_KeeningCordax`'s own roster note calls it an *"interim
single-tile body for the tower-trunks"*: a single-tile shrub standing in for towers the sheet
calls *"much more than one tile wide."* ⛔ Placeholders to replace, not a base to extend.

Disposition per row is in the roster doc §6: the 3 canon SW plants are **kept at low
commonality** as additive flavour, the 5 `AB_*` rows are **cut**.

## five rows exist to carry a ruling, not to fill a slot

⛔ **Do not cut or "simplify" these** — each one is load-bearing for a mechanic:

| row | what it carries |
|---|---|
| `RM_Plennith` | **makes the bough-soil** — the crown's fertility is biological, so the layer explains itself |
| `RM_Ossagrel` | the **sap host** the three ruled sap-suckers drink from; without it `FEVERWOOD_SAP_SUCKER_GUILD_1` has no food |
| `RM_Cistrel` | the **only safe water on the map** — turns "nothing goes in the water here" from a prohibition into a resource |
| `RM_Corvath` | grows **only where the thing below has fed** — the botanical tell that makes pools readable rather than an unfair coin-flip. ⛔ Keep it worthless; its value IS the information |
| `RM_Skimmel` | **disguises the sink-mud** — the visual tell the mud ruling needs |

## 🔴 no row falls

**Owner, verbatim:** *"You can destroy them, but they are so interconnected above you that
they can no longer fall. So you can just mine right through one."*
⇒ **There is no fall event in this biome at all.** ⛔ If a later pass reaches for
`RM_FellableTreeExtension` or `RM_CompCrackFall` here, it has misread the ruling.

✅ **The existing build is already correct:** `RUT_FeverTrunkHeartwood` is a mineable
`ParentName="RockBase"` blob, which is exactly "destructible, never falls, mine through."
⚠️ **A false finding was reported to the owner earlier in the 2026-09-23 session** — that
this biome lacked a fellable giant tree and needed an `RM_Greatbole` equivalent. **That was
wrong.** ⛔ Do not file work to add one.

## blocked

🔴 **8 of the 18 rows — the entire crown layer — cannot grow until
`FEVERWOOD_BOUGH_SOIL_TERRAIN_1` lands.** `RUT_Boughway` ships `fertility 0`.

## before queueing any art

🔴 **Search first.** `infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl` and any
review sheet's `.decisions.json` — by **subject**, not job-id guesswork. Finished,
already-ruled art has sat unused for days here, and three Greentide plants were nearly
regenerated on top of validated art on 2026-09-20. ⚠️ The artpipe daemon does **not** run on
the Mac, so queueing from the laptop generates nothing until the Desktop runs it.

## Watch out

- **Commonalities and `growDays` are slots, not values** — every number in the doc is unset.
- ⚠️ `RM_Seepril` may belong to a liquids system rather than to flora: the roster json records
  the seep-oils as *"none (gather point) — or terrain feature at mechanics item"*, and
  `LIQUID_TYPES_MOD_1` is named as their owner in the sheet's cross-flow ledger. **Settle
  ownership before authoring that def.**
- ⛔ Editing the live `RUT_FeverWood.xml` is governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.
- ⚠️ Two rows (`RM_Skimmel`, `RM_Sodderel`) are **deliberately deceptive** to the eye. An art
  pass that "fixes" either has broken the design; the legibility matrix records this on purpose.
