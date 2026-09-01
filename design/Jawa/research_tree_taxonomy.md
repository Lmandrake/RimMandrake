<!-- status: decision doc — RESEARCH_TAXONOMY_DRAFT_1, BENCH 2026-08-31, green-lit by the owner.
     Third layer of the research-normalization stack: research_normalization_principles.md (the
     why and the mechanism), research_tree_prep.md (the MEASURED census), canon.yml research_tree
     (the ruled shape, 2026-08-30). This doc adds the execution taxonomy: tabs, tiers, the
     manifest schema, the validator, and the migration rules. Execution itself stays gated on
     RESEARCH_TREE_NORMALIZATION_1 ("after the droids land"). -->
# Research tree taxonomy — the execution grammar

**Already ruled, not re-litigated here:** THEMATIC grouping for weapon techs;
THE SHIP as its own non-linear tree (its couples-in list is canon, including
the MiningCo laser as ancient ship tech and the orphan KotOR ship-design trio
reflavored into the Memory Core chain); modularity holds elsewhere; the
GRAVITIC SPLIT (personal = weapon school, industrial/ship = Ship tree); the
one fuel cross-link; Royalty's 19 rows cuttable (`royalty.dead_ruled`).
**Already measured** (prep doc, capture `5c9df49e`, 585 mods): 515 rows across
77 mods, KotOR carrying 89 (more than Core's 77), 12 rows measured dead, 22
empty-cache rows confirmed alive, 58 partial-cut.

**This sitting's census** (capture `5c47dd88`, 584 mods, 2026-08-29, all
MEASURED via dumpdb SQL): 38 tabs, top: Main 162 · SWKotOR 85 · Vanilla
Expanded 57 · Anomaly 40 · Outer Rim 32 · gravtech 18; 20 small tabs hold 27
rows between them, and RIMMSqol defines NINE tabs wired to nothing.
techLevel: Industrial 163, Spacer 144, Ultra 87, **Undefined 40**, Neolithic
34, Medieval 33, **Animal 14** (the last two are data smells the manifest
fixes for free). Structure: 13 roots, 310 leaves, longest prereq chain **19
hops** (ending `AM_Cryptoharmonization`), and one genuine self-loop in
shipped data (`RimFridge_PowerFactorSetting` requires itself).
`hiddenPrerequisites` 57 · `requiredResearchBuilding` 226 ·
`techprintCount>0` **448 of 515**.

🔴 **The 448 is the sitting's biggest finding: Research Reinvented is already
a live co-writer of the tree.** Vanilla `Electricity` in the resolved dump
carries `techprintCount: 1` and a prerequisite of `RR_ElectricityBasics` —
`petetimessix.researchreinvented` (+ Stepping Stones, 10 rows) rewrites
prereqs and stamps techprint fields across nearly everything at load. Any
normalization pass that ignores it will be normalized OVER; the manifest must
either run after RR's rewrite and treat its output as the substrate, or the
sitting decides RR's fate outright (§6.6).

## 1. The tab set — 38 mod tabs become seven campaign tabs (owner rules)

| tab | carries | pride register (principles §2) |
|---|---|---|
| **Scavenger** | neolithic/early-industrial utility: stills, traps, salvage benches, tailoring, cooking | pride-FREE — the humble floor |
| **Trade & Craft** | industrial colony economy: machining, drugs, fabrication basics, Rimefeller/gas/vehicle chains (the ruled-modular mods keep their internal chains, re-homed under this tab) | drip |
| **The Armory** | the thematic weapon schools: Thermal/blaster · Ionic (JawaIon vocabulary wins — canon ion doctrine) · Kinetic · Sonic (thin; may fold into Kinetic at the sitting) · Gravitic-personal (Rakatan relics) | drip, school by school |
| **The Machine** | the droid branch, gathered and VISIBLE: Droid Depot, Outer Rim droid rows, droid bionics — the Ohm/Oomo flashpoint the player walks into knowingly | ↑Ohm, ↓Oomo per completion |
| **THE SHIP** | the ruled non-linear tree: gravtech cluster, VGE systems, ShipReactor, VFE_Manufacturing, drill-laser pair, ship weaponry, Memory Core chain (hidden until the ship surfaces them — research as revelation) | Rekko-NEUTRAL for restoration rows; Ozzik-weighted for beyond-spec rows |
| **The Reach** | spacer/ultra/archotech: the temptation tab, visibly pride-marked — the archite ladder lives here when its v2 rethink lands | the trap's teeth |
| **(Anomaly)** | engine-forced tab, playstyle-gated; rows left in place — bioferrite/containment must stay researchable for the Assailant/sarlacc exception | untouched |

The research screen becomes the temptation diagram: left-to-right is the
ambition gradient, and the two pride-marked tabs LOOK different (tab naming
and ordering carry the theology without a single new mechanic).

## 2. The tier grammar — orthogonal to tabs

Every manifest row carries one tier; cost bands and theology weights hang off
the tier, never off the individual row (taste lands once, in the band):

| tier | vanilla techLevel mapping | cost band | theology |
|---|---|---|---|
| T0 Scavenger | Neolithic–early Industrial | cheap | pride-free |
| T1 Trade | Industrial | moderate | Ozzik drip |
| T2 Forge | late Industrial | expensive | drip + Ohm on machine rows |
| T3 Spacer | Spacer | steep + Visibility cost | Ozzik spike |
| T4 Reach | Ultra/Archotech | the grind; "traded items, prototypes as costs" (owner's proposition requirement) | the trap |

**Source gates are flags, not tiers** — orthogonal: `memory_core` (original
ship weaponry, hidden-prereq revealed by events), and candidate gates from
canon (`cathedral_whisper`, `vault_knowledge`, `hutt_deal`). A T2 row can be
memory-gated; a T4 row can be open. The gate list is extensible in data.

## 3. The manifest — owner-rules-as-data (principles §3B made concrete)

One CSV/JSON table in the mod, consumed by BOTH the runtime rewrite pass and
the satiation engine. Columns:

```
defName · source_mod · fate · tab · tier · cost · prereqs[] · hidden_prereqs[]
· source_gate · form · theology · merge_target · note
fate ∈ keep | cut | merge (unlocks re-pointed at merge_target) | reflavor
       (label/description swap, position kept) | untouched (explicit no-op)
```

Two hard contracts, both lessons this repo already paid for:
1. **Log-loudly:** every manifest row must resolve to a live def at load —
   an unmatched row is a red error, never a silent skip.
2. **Coverage or refuse:** every live `ResearchProjectDef` must have a row —
   `untouched` is a legal fate but must be WRITTEN. The pass refuses to run
   on partial coverage (zero-rows-is-a-failure, asserted against the
   inventory, not sampled).

## 4. The validator — offline, pre-deploy, dump + cherrypicker as inputs

Checks, each with its false-pass named:
- **Orphan check:** every row's unlocks resolved against the live dump AND
  the Cherry Picker cut list (cuts are invisible to the dump — cherrypicker.py
  is the reader). Flags dead rows and Mortars-class half-orphans (shells with
  nothing to fire them). *Lies by:* trusting an empty unlock cache — 22 rows
  are alive with empty caches (prep §1); the validator must carry that
  allowlist.
- **Prereq resolution:** no prereq names a cut or absent project.
- **Band conformance:** cost within the tier's band; techLevel matches tier
  mapping. *Lies by:* mods whose C# rescales cost at runtime — spot-check one
  known case live before trusting the band report.
- **One-chain-per-form:** no weapon form retains two research chains
  (KotOR's three blaster tiers vs VWE lasers vs Outer Rim blastersmithing —
  one survivor each, per the turret pass's precedent).
- **Coverage:** rows == live ResearchProjectDef count, MEASURED, both sides
  from the same fingerprint.
- **Self-loop / cycle check:** shipped data already contains one
  (`RimFridge_PowerFactorSetting` requires itself, MEASURED) — the validator
  walks the graph and refuses cycles.
- **Co-writer awareness:** run against the RESOLVED dump (post-RR), never raw
  XML — the 448-row techprint stamp proves the raw file is not what the game
  plays. *Lies by:* validating a manifest against raw XML and shipping a pass
  that fights Research Reinvented at load.

## 5. Migration rules — the normative moves, ready for the sitting

1. The 12 measured-dead rows: `fate: cut` (except the ship-design trio —
   `reflavor` into the Memory Core chain, already ruled).
2. Royalty's 19: `cut` per `royalty.dead_ruled` (their live unlocks re-homed
   or released to loot-only — decide per row at the sitting).
3. KotOR's 89: the big consolidation — weapon rows merge into the Armory
   schools (survivor = the chain matching CANON vocabulary: `JawaIon_Weaponry`
   beats `guy762_ResearchKotOR_ion`); non-weapon rows re-tiered in place.
4. Every merge re-points the LOSER's unlocks onto the survivor before the
   loser dies — an unlock must never be orphaned by our own normalization.
5. Anomaly rows: untouched (playstyle-gated; exception content stays
   reachable).
6. Nothing renames a defName, ever (saves + mod C# break invisibly).

## 6. RULED by the owner, 2026-08-31 (question cards) — canon `research_tree.taxonomy_ruled`

1. ✅ **Tab set: the seven tabs, as written in §1.**
2. ✅ **Research Reinvented: KEPT AS SUBSTRATE** — the manifest runs after
   RR's rewrite and builds on its output; its techprint economy is the
   "expensive research, traded costs" requirement already implemented.
3. ✅ **Theology stays decoupled** — pride-weights on completion only; no
   Ozzik-standing gates (reversible later; coupling is not).
4. ✅ **Ceiling: Ultra reachable, priced brutally** — colony techLevel
   INDUSTRIAL; the vanilla multiplier does the anti-exponential work as
   economics, not walls. Nothing forbidden; The Reach is the trap.

## 7. RULED at the normalization sitting, 2026-08-31 — canon `research_tree.sitting_ruled` / `.chains_ruled` / `.tech_gating_ruled`

Sonic school KEPT thin (creative expansion later: SONIC_WEAPONS_EXPANSION_1) ·
manifest ships in RimUtinni · cost bands vanilla-like (T0 ≤600 / T1 600–1600 /
T2 1600–3000 / T3 3000–5000 / T4 5000+) · Royalty unlocks loot-only by default ·
blaster spine = KotOR 3-tier, reflavored; Outer Rim + VWE merge onto it ·
kinetic = slug→railgun thin chain · choice shape v1 = breadth only ·
tech gating = FOUR ACCESS CLASSES (common / faction-held via techprints /
jawa-special / ship-only), superseding the cathedral/vault/hutt bespoke-flag
candidates in §2 — see canon for the owner's verbatim. Execution items:
RESEARCH_VALIDATOR_BUILD_1 · RESEARCH_MANIFEST_DRAFT_1 ·
TECHPRINT_FACTION_GATING_1.
