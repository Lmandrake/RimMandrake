# Mutation systems survey — MUTATION_MODIFIERS_SURVEY_1

2026-09-11. Feeds `the_contagion.md` §7 (Contagion-touched exposure) and the Unfinished's
random-limb spawner (shares the part-addition mechanism below).

## Sources and their currency

- **Vanilla (Core/Biotech/Ideology/Odyssey/Royalty/Anomaly)**: read via `mcp__rimsage__*`.
  This index covers **only the six vanilla/DLC trees** — confirmed by probing modded
  defNames (`SlurryHigh`, `GeneticStability`) which return zero hits while vanilla names
  resolve. Treat rimsage results as MEASURED against shipped-game XML/source, not
  against any mod. No dependency on the currently-loaded mod list.
- **More Consumables and Mutagens (Continued)** (`Mlie.MoreConsumablesAndMutagens`,
  workshop id `2042709249`, INACTIVE — not in `ModsConfig.xml`, per
  `design/Jawa/worldbuilding/genepack_mods_plunder.md`): read directly from the mod's
  own `1.6/Defs/Drugs/*.xml` on disk. This is design-candidate material, not live content.
- **Alpha Animals** (`sarg.alphaanimals`, workshop id `1541721856`) and **Alpha Biomes**
  (`sarg.alphabiomes`, workshop id `1841354677`): read directly from the mods' own
  `1.6/Defs/**/*.xml` on disk. Both packageIds appear in
  `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (the tracked "intended
  full list" state file, itself modified earlier in today's session — its fingerprint
  against the live `ModsConfig.xml` is **UNKNOWN**; the brief says the live game is
  mid-verification on a possibly-minimal list right now, so this survey does NOT claim
  either mod is active in the live game at this instant — only that both ship the
  content below, on disk, as authored).
- Steam workshop cache paths root: `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/<id>`.

## Classification table

Columns: **class** = genetic / somatic / part-addition / behavioral. **Reversible** =
can be undone by ordinary play (tend, gene removal, biosculpter), not "eventually decays."
**Net-neg guaranteed** = does this roll/def ALWAYS cost something, with no way to land
pure-upgrade. **Visible** = does the pawn's body or a permanent trait/UI marker show it.

### Biotech (vanilla, MEASURED via rimsage)

| defName | source | class | reversible | net-neg guaranteed | visible |
|---|---|---|---|---|---|
| `Instability_Mild` (GeneDef) | Biotech | genetic | no (germline; needs gene extraction/biosculpter to remove) | yes — `LifespanFactor 0.8`, `CancerRate 3` always ride the `biostatMet 2` discount | no (no body marker; gene-list only) |
| `Instability_Major` (GeneDef) | Biotech | genetic | no | yes — `LifespanFactor 0.6`, `CancerRate 5` for `biostatMet 4` | no |
| `ArchiteMetabolism` (GeneDef) | Biotech | genetic | no | **no** — pure upside (`biostatArc 2`, `biostatCpx 6`, `biostatMet 6`, no stat penalty); the archite-gene COST is paid in xenogerm complexity budget, not on the pawn | no |
| `XenogerminationComa` (HediffDef) | Biotech | behavioral (temporary incapacitation) | yes — self-clears, ~2 days | yes (Consciousness capped 0.1 while it lasts) | yes (health tab, downed) |
| `XenogermLossShock` (HediffDef) | Biotech | behavioral (temporary) | yes — self-clears | yes | yes (health tab) |
| `XenogermReplicating` (HediffDef) | Biotech | somatic (temporary) | yes | UNMEASURED (not read in full) | yes |

Gene complexity/metabolism cost is the `biostatCpx`/`biostatMet`/`biostatArc` triad on
every `GeneDef` — it gates how MANY genes a xenogerm can carry, not a per-gene penalty on
the pawn. Total Biotech GeneDef count: UNMEASURED (hundreds; not enumerated — out of
scope, this survey sampled instability + one archite gene as the two poles the spec asked
for).

### Anomaly (vanilla, MEASURED via rimsage — `ANOMALY_EXCEPTION_ACCESS_1` rules this content
in-bounds for reading; nothing here is cut)

| defName | source | class | reversible | net-neg guaranteed | visible |
|---|---|---|---|---|---|
| `FleshmassStomach` (HediffDef, `ParentName="AddedMutationBase"`) | Anomaly | part-addition | no (surgical removal risks `HediffCompProperties_FleshbeastEmerge` — it can detach and become a hostile fleshbeast) | yes — pain +0.08 always rides the food-poisoning immunity | yes (organ list; not exterior) |
| `FleshmassLung` (HediffDef, same parent) | Anomaly | part-addition | no (same removal risk) | yes — pain +0.06 always rides the lung-rot immunity + toxic resist | yes (organ list) |
| `Tentacle` (HediffDef, same parent) | Anomaly | part-addition | no (removal risk) | yes — `PawnBeauty -1` always rides the manipulation-boosting `partEfficiency 1.20` | **yes, exterior** — custom render node, visible on the body |
| `FleshWhip` (HediffDef, same parent) | Anomaly | part-addition | no (removal risk) | yes — `PawnBeauty -1` always rides a free melee weapon (cut, 20.5 power) | **yes, exterior** |
| `Ghoul` (HediffDef) | Anomaly | whole-identity replacement, not incremental | no (`everCurableByItem: false`) | yes — can't work, can't talk, must eat raw meat, in exchange for `MaxNutrition x2` and combat stats | yes — distinct pawnkind rendering |
| `Shambler` (HediffDef) | Anomaly | whole-identity replacement | no | pure downside — mindless, dies of exhaustion in days; no compensating benefit | yes |

The `AddedMutationBase` family (4 direct children, confirmed by regex over the whole
818-line source file, not a sample) is the closest vanilla analogue to what a Contagion
mutation hediff should look like: a `Hediff_AddedPart` that is mechanically good
(`isBad: false`) but pairs a guaranteed cost (pain, beauty, or a removal-time monster) by
construction. Ghoul/Shambler are a different shape entirely — they replace the whole
pawn's behavior tree, not a stackable roll — so they inform tone (archotech/archite
corruption) but are not a template for a repeatable mutation deck.

### More Consumables and Mutagens (mod XML, MEASURED — design-candidate, INACTIVE)

Full read: Igni family (`Crystal_Igni.xml`) and Slurry family (`HM_Slurry.xml`) read in
full; Ursa/Sil/Midia/Myrol defName rosters confirmed by grep on their own files
(stat content not fully re-read here — see `genepack_mods_plunder.md` for the earlier
pass).

| defName | source | class | reversible | net-neg guaranteed | visible |
|---|---|---|---|---|---|
| `SlurryHigh` (container HediffDef) | More Consumables | somatic (temporary reaction phase) + gates the rolls below | the phase itself self-clears (`severityPerDay -0.30`) | **yes, always** — "active" stage forces Consciousness -0.35, Moving -0.30, Sight -0.20, Manipulation -0.40, pain x1.6, vomiting, REGARDLESS of which mutation(s) roll | yes (mood-linked `SlurryReaction` thought, -12 to -30) |
| `SlurrySlimy` (HediffDef, one of 19 rolls under SlurryHigh) | More Consumables | somatic | no (permanent mutation hediff) | no on its own (pure armor + comfy-temp upside) — net-neg is carried by the mandatory `SlurryHigh` phase it rides in on, and by `makeImmuneTo` locking out `SilSkin`/`UrsaFur` (opportunity cost) | yes (skin, implied) |
| `UrsaClaws` (HediffDef, `CrystalDrugMutationPartBase`) | More Consumables | part-addition | no | UNMEASURED (stats not re-read this pass) | yes |
| `UrsaDisfigured` (HediffDef) | More Consumables | somatic | no | pure downside by name/role — one of the pool's "cost" entries | yes |
| `IgniArm` (HediffDef, `CrystalDrugMutationPartBase`) | More Consumables | part-addition | no | yes, on its own — armor +0.10/+0.06 paired with `Manipulation -0.2` in the SAME def | yes |
| `IgniFurnace` (HediffDef) | More Consumables | somatic | no | yes — `Eating` capacity +0.5 paired with `hungerRateFactor 1.3` in the same def | no (internal) |
| `SilDegraded` (HediffDef, brain-targeted) | More Consumables | somatic | no | UNMEASURED (name implies pure cost) | no |
| `MidiaSmart` / `MidiaAbsent` | More Consumables | somatic (mind) | no | UNMEASURED — plunder doc frames these as a matched pair (`+85% learning` / an absence-minded cost) | no |
| `MyrolMyrolsis` | More Consumables | somatic (regen) | no | UNMEASURED — plunder doc: heals permanent wounds (pure upside on its own) | no |

Mechanism worth stealing whole: **a container "High" hediff with a mandatory temporary
debuff stage, plus a `HediffGiver_Random` pool of ~7-8 permanent mutation hediffs per
crystal family (38 total across Igni/Ursa/Sil/Midia/Myrol/Slurry), where roughly half the
pool entries are self-contained benefit+cost (one hediff, two stat blocks) and the other
half are matched opposite pairs wired together with `makeImmuneTo`** (SilSkin↔UrsaFur↔
SlurrySlimy, IgniSpeed↔UrsaSlow, SlurryAgile↔SlurryStagnant). This is the single strongest
precedent for "every roll pairs a cost, enforced by construction" in the whole stack.

### Alpha Animals / Alpha Biomes (mod XML, MEASURED — currently in the FULL modlist state
file; live-activity status UNKNOWN this session)

| defName | source | class | reversible | net-neg guaranteed | visible |
|---|---|---|---|---|---|
| `AA_FungalHusk` (ThingDef/PawnKindDef) | Alpha Animals | whole-creature reanimation, not a pawn hediff | n/a | n/a | n/a |
| half-transformed ocular tree (plant ThingDef, no defName grepped — terrain object) | Alpha Biomes, `Plants_OcularForest.xml` | environmental/terrain transformation, not a pawn hediff | n/a | n/a | yes, on the map |
| `AB_SporesAllergy` / `AB_SporesAllergy_Heightened` | Alpha Biomes | somatic (disease) | yes — tendable, immunizable | **no** — pure downside, no paired benefit (this is the pattern the deck must NOT copy) | yes (health tab) |
| `AB_RavagingIntestinalParasites` | Alpha Biomes | somatic (disease) | yes — tend-curable | no — pure downside | yes |
| `AB_ViralAbasia` | Alpha Biomes | somatic (disease) | yes — immunizable | no — pure downside | yes |
| `AB_Gangrene` | Alpha Biomes | somatic (injury→permanent) | no once it scars (`HediffCompProperties_GetsPermanent`) | no — pure downside | yes |

**Neither Alpha Animals nor Alpha Biomes contributes a pawn-hediff "transformation"
mechanic** in the sense the spec was hunting for (a living colonist mutating into
something else while staying playable). The "half-transformed tree" and fungal-husk
patterns cited in the brief are both whole-object replacements (a plant, or a reanimated
corpse) — good flavor precedent for "the infection changes what a thing IS," bad
mechanical precedent for a mutation-roll deck. Their disease hediffs (`AB_*`) are useful
as a NEGATIVE CONTROL: this is what "always just a cost" looks like, and the Contagion
deck should not resemble it on its own — costs belong paired with a mutation, not bare.

### Vanilla mechanites / luciferium / permanent injury

| defName | source | class | reversible | net-neg guaranteed | visible |
|---|---|---|---|---|---|
| `LuciferiumHigh` | Core | somatic (drug) | no while addicted — see below | **no on the hediff itself** (`isBad: false`, all-positive stat block); the guaranteed cost is external — `LuciferiumAddiction` need + insanity risk if resupply lapses | no direct body marker; addiction is tracked as a Need |
| `FibrousMechanites` / `SensoryMechanites` | Core | somatic (disease, mechanoid-inflicted) | UNMEASURED (not read) | UNMEASURED | UNMEASURED |
| `HediffCompProperties_GetsPermanent` (comp class, not a def) | Core | mechanism, not a hediff — turns any tended injury into a permanent scar hediff on tend failure | no, by design (that's the point of the comp) | context-dependent | yes, permanent |

Luciferium is the vanilla precedent for "pure upgrade hediff, cost lives OFF the hediff"
— explicitly the shape the Contagion deck must NOT use, per the owner's "it never just
upgrades you" ruling applying to the mutation ITSELF, not a detachable side-system.

## Counts (all MEASURED against the sources named above; nothing here is a guess)

- Biotech instability genes: **2** (`Instability_Mild`, `Instability_Major`).
- Anomaly `AddedMutationBase` children: **4** (`FleshmassStomach`, `FleshmassLung`,
  `Tentacle`, `FleshWhip`) — exhaustive, confirmed by regex over the full source file.
- Anomaly whole-identity corruption hediffs sampled: **6** (`Ghoul`, `GhoulFrenzy`,
  `GhoulPlating`, `GhoulBarbs`, `Shambler`, `ShamblerCorpse`).
- More Consumables & Mutagens mutation-hediff rosters (defNames only, by family):
  Igni **7**, Ursa **7**, Sil **7**, Midia **6**, Myrol **3**, Slurry **8** = **38 total**,
  each family gated by one container "High" reaction hediff (6 more) with a mandatory
  temporary debuff phase.
- Alpha Biomes pawn-affecting disease hediffs sampled: **5** (`AB_SporesAllergy` ×2 variants,
  `AB_RavagingIntestinalParasites`, `AB_ViralAbasia`, `AB_Gangrene`/`AB_BacterialGangrene`).
- Alpha Animals / Alpha Biomes "transformation" objects found: **2**, both non-pawn
  (`AA_FungalHusk` corpse-reanimation creature, half-transformed ocular tree plant) —
  **0** living-pawn transformation hediffs found in either mod.

Total distinct mutation-relevant defNames catalogued in the table above: **~55**, spanning
7 systems (Biotech genes, Biotech xenogerm hediffs, Anomaly part-mutations, Anomaly
identity-corruption, More Consumables part/somatic mutations, Alpha Biomes disease control
group, vanilla luciferium/permanent-injury).

---

## DRAFT — owner rules the deck

Proposed Contagion-touched exposure mechanism, built entirely from the precedents above.
Nothing here is final; it is a starting point for the owner to cut, reweight, or reject
by card.

### Shape (modeled on `SlurryHigh`/`IgniHigh`)

One container hediff, **`RUT_ContagionFever`** (name TBD), applied on spore exposure:

1. **Mandatory temporary cost phase** — every exposure, no roll involved. Modeled
   directly on `SlurryHigh`'s "active" stage: Consciousness/Moving/Sight/Manipulation
   offsets, pain factor up, vomiting. This is what makes "it never just upgrades you"
   true by construction even before any mutation lands — the container itself always
   hurts. Clears on its own timeline (matches the sun/purge-arrests-progression lore:
   arresting the fever stops FUTURE rolls, it does not undo installed mutations).
2. **One or more `HediffGiver_Random` rolls** off a weighted pool while the fever is
   active, matching the Igni/Slurry mechanism exactly.

### Pool weighting (draft split)

| tier | weight | template | enforcement of "always a cost" |
|---|---|---|---|
| Somatic paired stat mutation | ~45% | `IgniArm`/`SlurrySlimy`-style: ONE hediff carrying both a benefit stat block and a cost stat block | built into the single def, like `IgniArm` (+armor / -Manipulation) |
| Part-addition | ~30% | `Tentacle`/`FleshWhip`/`FleshmassStomach`-style `Hediff_AddedPart` | `PawnBeauty` penalty AND/OR a `HediffCompProperties_FleshbeastEmerge`-equivalent removal risk, exactly as Anomaly does it |
| Genetic instability roll | ~15% | `Instability_Mild`/`Instability_Major` — the roll ADDS a real Biotech-style gene (or a bespoke `RUT_` gene built the same way) to the pawn | `LifespanFactor`/`CancerRate` cost is inherent to the gene; irreversible without a gene-editing facility (matches "arrest, not reversal") |
| Pure-cost outcome | ~10% | `AB_ViralAbasia`/`SlurryStagnant`-style: no compensating benefit at all | capped low on purpose — this is the "you just got unlucky" tail, not the median outcome, so the deck reads as "risky" rather than "punishing" |

**Never-upgrade guarantee, stated as a construction rule** (not a probability): every
mutation-tier entry in the pool must satisfy at least one of —
(a) its own HediffDef carries both a positive and a negative stat/cap block, or
(b) it is wired via `makeImmuneTo` to a same-tier opposite-effect hediff so picking one
locks out the other (opportunity cost), or
(c) it is a part-addition whose comps carry a standing risk (visible beauty penalty,
removal-time hazard).
No pool entry may be added that is `isBad: false` with zero cost hooks — that is
`LuciferiumHigh`'s shape, and it is explicitly the one this deck must not reproduce.

### Open questions for the owner

- Exact `RUT_` gene(s) for the instability tier — author new, or reuse vanilla
  `Instability_Mild`/`Major` directly as a roll outcome?
- Whether part-addition rolls should share Anomaly's `HediffCompProperties_FleshbeastEmerge`
  removal-risk verbatim (spawns a hostile creature on extraction attempt) or a
  Contagion-flavored equivalent (spawns local ocular-forest infection instead).
- Whether the "pure-cost" tail should be capped at 10% or removed entirely (per lore,
  Contagion mutation should feel "large and random," not "sometimes just bad" —
  the owner may prefer every roll guarantee SOME payoff, just always taxed).

## UNKNOWN / not determined this pass

- Full stat blocks for `UrsaClaws`, `UrsaHorns`, `UrsaWild`, `SilFlowers`, `SilStomach`,
  `SilBlood`, `SilCalm`, `MidiaForget`, `MidiaRough`, `MidiaKeen`, `MyrolStatic`,
  `MyrolLung` — defNames confirmed by grep, stat content not re-read this pass (see
  `genepack_mods_plunder.md` for a partial prior read of some of these).
- Total Biotech `GeneDef` count and full negative-gene roster — not enumerated (out of
  survey scope; hundreds of genes ship with Biotech + gene-expansion mods).
- Whether `sarg.alphaanimals`/`sarg.alphabiomes` are active in the LIVE game right now —
  the brief warns the live list may be minimal mid-verification; this survey relied on
  the mods' own on-disk XML plus their presence in the tracked
  `ModsConfig.FULL.LATEST.xml` state file, not a live bridge read.
- `FibrousMechanites`/`SensoryMechanites` full hediff content (found, not opened).
- Whether Anomaly's `Tentacle`/`FleshWhip` default `isBad` (neither def sets the field
  explicitly; inherited from `AddedBodyPartBase`, not traced to its root value here).
- The Unfinished's random-limb spawner mechanism itself was not read this pass — noted
  only as a stated consumer sharing the `Hediff_AddedPart`/`HediffGiver_Random` pattern.

## THE DECK IS RULED — owner card sitting 2026-09-12

Supersedes the draft deck's open questions above; build to THIS:

1. **Unstable genes: CUSTOM Utinni-flavored gene** — do not reuse vanilla
   instability genes as the deck's gene; design our own (campaign flavor).
2. **Part removal: copy the existing risk exactly** — failed surgical removal
   of a Contagion-added part spawns a hostile creature, same as the game's
   mutated-flesh parts. No new mechanism.
3. **Roll variance — the owner's own shape, replacing the drafted ~10%
   pure-downside:** verbatim: "It should be a large variance experience
   that's 50% all negative and 50% positive + negative. The Contagion isn't
   nice." ⇒ half of all rolls are ALL negative; the other half are positive
   PLUS negative (never positive alone); magnitudes swing wide. The draft's
   never-just-upgrades law survives by construction; the drafted 90/10 split
   is DELETED.
