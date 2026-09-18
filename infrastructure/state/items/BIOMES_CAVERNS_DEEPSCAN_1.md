# BIOMES_CAVERNS_DEEPSCAN_1 — what the Biomes! family brings (arms the future retirement call)

Owner ruling, 2026-09-18 modlist sitting, verbatim: *"Once we make our own
version of all biomes, I'm ok with cutting. But for now we keep them until
they are retired. We'd need a deepscan of what they bring to answer this (ok
to send this recon agent out now)."* **KEEP all three for now** — this item
holds the deepscan so the eventual retirement is judged on measured content,
not memory. Recon ran same day (sonnet agent, read-only census of the three
mod folders' defs, patches and assemblies).

## Findings (MEASURED 2026-09-18)

**Biomes! Caverns (`biomesteam.biomescaverns`) — replace-cost HIGH.**
- 3 BiomeDefs: `BMT_CrystalCaverns`, `BMT_EarthenDepths`, `BMT_FungalForest`
  (the only BiomeDefs in the family).
- ~90 creature PawnKindDefs, ~98 plants, landforms, DLC integration across
  all five expansions.
- Custom mapgen C# (cavern rock/crystal scattering) plus the bundled
  sub-pack `Caveworld_Flora_Unleashed.dll` — which owns
  `MapComponent_CaveFungus`, the mycelium spawner seen in the 2026-09-08
  quicktest crash stack. Confirmed ABSENT from the other two mods'
  assemblies: any crash attribution on that class points here.

**Biomes! Polluted Lands (`biomesteam.biomespollutedlands`) — MEDIUM-HIGH.**
- Ships ZERO BiomeDefs — it patches 23+ existing biomes' wildlife and
  plants instead, so cutting it thins ecosystems everywhere, not one biome.
- Carries a real mutation system: 18 GeneDefs, mutapox disease, hediffs,
  quests/incidents. The replace cost is that mechanic, not a biome.

**Biomes! Fossils (`biomesteam.biomesfossils`) — LOW.**
- Defs-only museum/fossil content. No BiomeDef, no PawnKindDef, no
  MapComponent/GenStep/Harmony patching; 2 patch operations total.
- The natural first cut when retirement begins.

## What retirement will take (reading of the above)

Fossils can go almost free. Polluted Lands needs a decision about whether
the mutation mechanic is wanted at all on Ash'karr (if not, it also goes
cheap — its biome patches are flavor). Caverns is the real port: three
underground biomes plus a large flora/fauna roster plus mapgen C#, only
worth replacing if our own biome program ever goes underground — on a
frozen surface-desert world it may simply never be visited, which is an
argument for cut-without-replace when the time comes.

Full raw census (per-def-type counts, patch targets):
`Transient/biomes_caverns_deepscan_2026-09-18.md` — Transient shelf ~14
days; everything decision-relevant is copied above.
