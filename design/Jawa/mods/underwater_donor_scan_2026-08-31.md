<!-- status: evidence — owner-commissioned scan, 2026-08-31. Extends depths_concept.md §10.
     Lens: single mod we OWN; every donor is inspiration or (where licensed) ingestion, never a dependency. -->
# Underwater donor scan — beyond the first three

Three-domain sweep (this disk's 1258 subscribed mods · published Steam landscape ·
GitHub with licenses), same lens as `design/Jawa/worldbuilding/depths_concept.md`
§10: oxygen, pressure, movement, weapons-in-water, electricity, aquatic races,
underwater settlements, flooding, resources. GravTide / Electrofishing / Nautian
Style are covered in §10 and excluded here.

## The headline finds

| Source | Find | Why it matters |
|---|---|---|
| disk, subscribed | **Ocean Biome** (`oceanmodder.oceanbiome`, 3724511552) | The only other mod attempting our whole fantasy: underwater terrain gen, diving suits + O2 tanks, drowning/decompression, a **90% ranged-accuracy debuff underwater** (their answer to "most weapons malfunction"), and **Biotech aquatic genes** — a second, independent architecture to compare against GravTide's. On disk now; read its gene/hediff defs before speccing §7's adapted races |
| GitHub, **MIT** | **MSeal/RimworldSwimming** (SwimmingKit) | Per-terrain swim-speed via one Harmony patch on movement — §5's drag mechanic, MIT-licensed: legally ingestible as a starting point, though 1.4-era and needing a 1.6 port |
| GitHub, **MIT** | **RimNauts/RimNauts2** | EVA/vacuum-survival hediff + environment-hazard pattern, MIT — the open-source template for an oxygen/pressure hazard layer where GravTide (unlicensed) can only be read |
| GitHub, **MIT** | **SmashPhil/Vehicle-Framework** | 1.6-maintained boats/submarine-capable vehicle framework, MIT. If v2 ever wants a submersible, the pathing/buoyancy problem is already solved in ingestible code |
| web | **Vanilla 1.6 ships flooding natively** (Dynamic Flooding is listed as superseded by it) | §5's flood-on-breach may partly exist in the base game — add "how far does vanilla 1.6 flooding go" to the Odyssey source-read gate |
| disk, subscribed | **Vanilla Gravship Expanded — Chapter 1** | Oxygen NETWORKS as a piped survival system — the closest thing to a shipped oxygen-supply economy; read before designing dive-suit air supply |

## Second rank — one mechanism each

- **RimShips** (Steam, 1.6, Odyssey): sea vessels with **pressure damage** in
  underwater exploration; proves world-map water transit.
- **Goji's Merren race** (Steam, 1.4–1.6): Biotech water-hydration/aquatic
  genes in the wild — a gene-vocabulary donor for §7.
- **Torment Master** (disk): a "Water Prison" with a **breath-holding
  mechanic** — a tiny, readable drowning-timer implementation.
- **SOS2** (Steam/GitHub): sealed-hull life support, airlocks, heat networks —
  the richest life-support precedent, but its license is custom/non-permissive:
  read for shapes only.
- **Biomes! Islands** (Steam, 1.6 pending): populated aquatic ecosystem
  (sharks, rays, sardine shoals) — bestiary structure precedent for §6.
- **VFE Fishing / Seed Fish Tool / FeedinFishies / fishing-is-fun (MIT)**:
  the 1.6 fishing/water-population API surface from four angles; FeedinFishies'
  corpses-feed-fish is a free scavenger-swarm flavor idea.
- **Dubs Bad Hygiene** (+ Spring Water patch, disk): water as a piped
  need-economy; adjacent, not underwater.
- **Raiders Can Swim / Impassable Chest-deep Water** (Steam, unopened):
  water-depth movement/passability vocabulary — UNCERTAIN, not verified.

## What did NOT turn up

No RimWorld mod models **electricity as an area hazard in water** (our §5
conductive-fluid pillar is genuinely novel — Electrofishing's flat AoE is the
only cousin). No Subnautica-like underwater-colony mod exists beyond GravTide
and Ocean Biome. No open-license underwater biome/mapgen repo was found — the
GitHub searches for underwater/diving/ocean/submarine came back empty of
relevant hits beyond the rows above.

## Precedence notes

Disk beats web where they touch the same object (Ocean Biome is SUBSCRIBED and
readable regardless of the web thread's "possibly abandoned"). The web rows
marked UNCERTAIN were never opened; treat them as leads, not facts. License
identities were read from the repos themselves; everything Steam-only is
all-rights-reserved by default — patterns, never copies.

## What this changes for the build

1. **Read Ocean Biome's defs next** (it is on disk): its genes, decompression
   hediffs and accuracy debuff are a second reference architecture, and the
   only one attempting adapted races.
2. **The MIT trio** (RimworldSwimming, RimNauts2, Vehicle-Framework) is the
   legal ingestion pool — start §5's movement and oxygen C# from there, not
   from a clean sheet and not from GravTide's unlicensed source.
3. **Add vanilla 1.6 flooding to the §11 gate's source-read** — flood-on-breach
   may be cheaper than v2 assumed.
