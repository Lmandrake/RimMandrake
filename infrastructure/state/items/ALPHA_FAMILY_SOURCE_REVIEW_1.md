# ALPHA_FAMILY_SOURCE_REVIEW_1 — study every Alpha mod: leverage, be inspired, broaden

Owner, 2026-09-06: *"let's make a ticket to look at all the alpha biome mods not just to
leverage their capabilities but be inspired by them and broaden them. Do they have a
public git we can examine?"* — Yes: **`https://github.com/juanosarg/AlphaBiomes`** and
**`https://github.com/juanosarg/AlphaAnimals`** (juanosarg = Sarg Bjornson, the author;
C# source included). Sibling repos under the same account (Alpha Genes, Alpha Memes,
Alpha Mechs, Alpha Prefabs…) — enumerate them from `github.com/juanosarg?tab=repositories`.

## spec
1. **Inventory the family**: which Alpha mods are in our stack (ModsConfig, MEASURED) and
   which are not; for each repo, the license (borrowing design and def-identities is our
   precedent — never shipped code or art files; check whether the source license changes
   that for C#).
2. **Catalog the MECHANICS, not the content** — every C# comp/worker that does something
   the base game can't, e.g. (seen today): the Agarilux Prime's spore-cloud attack, the
   Forsaken fog's darkness/accuracy mechanic, the Gelatinous terrain attacks
   (slime-in-eyes), the slime compressor, the Mycotic spore diseases, the Darkbeast's
   sun-blocking mechanites, Alpha Animals' abilities (quill volleys, gas emitters,
   burrowing, hydrogen floaters). Table: comp class · what it does · which of OUR sheets
   wants it · effort to replicate/generalize.
3. **"Replicate ourselves with other similar functions"** (owner): for each mechanic worth
   owning, propose our generalized version under the tier grammar (`RSW_`/`RUT_`) —
   e.g. a generic *active-defender plant* comp (spore cloud / gas / sap / lure) that the
   Rot's guardian mushrooms, the Contagion's aberrations and the Deeps' Lantern can all
   use; a generic *environmental-attack terrain* comp; a generic *sensor-degrading fog*
   weather comp.
4. **Broaden**: what each Alpha biome/creature concept could become on Ash'karr beyond
   the donor's intent — feed the sheets' Owed lists.
5. Output as DATA (a mechanics table) + a short design memo; card anything that needs the
   owner (licensing, scope).

## verify
The table exists with defNames/classes cited from the repos; the owner has ruled which
mechanics we replicate; nothing from the repos is copied into src/ without a license
ruling.

## status

**2026-09-09 (Fable seat) — spec items 1–5 drafted; awaiting the owner's replicate ruling.**
Deliverable: `design/Jawa/worldbuilding/research/alpha_family_mechanics_2026-09-09.md`.
MEASURED from the live `ModsConfig.xml`: 595 active mods, 7 of them Sarg's
(alphabiomes, alphaanimals, alphagenes, alphamechs, alphamemes, alphaskills,
alphavehiclesneolithic); `juanosarg` has 83 public repos, 21 Alpha-named, so 14 Alpha mods
are not in our stack. **License: all 21 report NO-LICENSE — no LICENSE file, no README, no
licence text in either About.xml — so default copyright applies and the published C# is
readable but not reusable; the licence permits strictly LESS than our precedent, not more.
The owner's 2026-08-15 ruling (private playthrough, licensing not a consideration, decide
on engineering grounds) governs, with publication as the standing carve-out. Nothing was
copied into `src/`; both repos were cloned to scratch only.** The structural result is that
most "Alpha mechanics" are not Alpha's code — AlphaAnimals uses 428 VEF classes against 80
of its own — and four prize targets cost us nothing: terrain-that-attacks is vanilla
`TerrainDef.<tools>`/`KickMaterialInEyes`, terrain-hediff is `VEF.Maps.ActiveTerrainDef`,
sensor fog is vanilla `WeatherDef.accuracyMultiplier` (plus `GasType.BlindSmoke`), and
dormancy is vanilla `CompCanBeDormant`/`CompWakeUpDormant`. **Two corrections to this
item's framing:** AlphaAnimals has NO dormancy mechanic at all (it is not the wake-trigger
donor — vanilla is), and the "107 dormant rows" is a count of **VFEI2's** rows quoted in
`dune_sea_deep_desert.json`, not of our roster rows — our sheets carry 24 dormancy mentions
in free text across 10 sheets and have no structured dormancy field. Recommended top 5 to
own, all tier `RM_`: `RM_CompEmitGas` (S, the active-defender plant desert/arid_shrubland
want), `RM_StatPart_ConditionScaled` (S), `RM_BiomeLightExtension` + a cached
`GenCelestial.CurCelestialSunGlow` postfix (M, the only mechanic with no XML equivalent),
`RM_ScatterDef` + MapComponent (M), `RM_Gas_Harmful` (S). Not done, and flagged in the
draft's §7: AlphaGenes/Mechs/Memes/Skills were not opened, VEF's own source was not read
(every VEF field name in the table is from usage, not from VEF's C#), the 107 was not
verified against VFEI2, and camouflage has no donor in our stack. No new queue items filed.
