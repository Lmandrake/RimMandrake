# The Text Lore Load — complete inventory and estimate (2026-09-11)

Deliverable of TEXT_LORE_LOAD_CENSUS_1 (owner spec + 3 card rulings, 2026-09-11).
Four parallel census lanes, composed at BENCH. Every number carries its word:
MEASURED (instrumented), ESTIMATE (labeled judgment), UNMEASURED (blind spot
named). Owner rulings applied throughout: scope = everything the player can
read PLUS tier-generic variants for mods used outside our scenario; frozen
sheet or ruling = LOCKED (generate now), else DEFERRED; Oracle prompt packs
count as lore load.

## 1. Executive summary

- The engine exposes **38 distinct text surfaces** (§2) — from item
  descriptions to grammar-generated combat logs, names, art plaques and
  quest text, plus two C#-hardcoded strata (alerts, toasts) reachable only by
  translation keys or patches.
- **Our own tiers**: 5,110 defs; the real debt is **~1,600 missing + 233
  placeholder descriptions**, concentrated in RSW Armoury and SWBestiary
  (absorbed donor content with its filler intact), plus **3 confirmed
  tier-grammar violations** (§3).
- **Donor stack** (MEASURED against the 577-mod dump of 2026-09-10): the
  player-facing donor text is enormous in raw count (§4), but the RENAME
  backlog is bounded by off-lore proper nouns, not by volume — the worst
  leaks are named (orc clans, trolls, MiningCo., unthemed xenotypes), and
  the Star-Wars-flavored donors are already near-lore.
- **Design-side**: ~45–55k words of LOCKED source lore (36/37 frozen biome
  sheets + ruled canon) stand ready to generate from; the biggest
  zero-lines-written gaps are the **Ninefold god lines, Oracle persona
  packs, and dungeon set-piece prose** (§5).
- **Total authoring load (ESTIMATE, §6): roughly 90–140k words** of text to
  write or rename across all categories — of which ~55–75k is generatable
  NOW against locked lore, and the rest defers on named lockdowns.

## 2. Where text belongs — the 38 engine surfaces (lane A, MEASURED)

Vanilla+DLC counts; every def type below exists ×N across the donor stack too.
Sorted by player exposure.

| Surface | Def type · fields | Vanilla+DLC | Mechanism |
|---|---|---|---|
| Thing labels/descriptions | ThingDef label/description | 1,420 | static |
| Mood thoughts | ThoughtDef stages[].label/description | 684 | static + [symbol] |
| Backstories | BackstoryDef title/titleShort/baseDesc | 577 | static |
| Letters (events) | IncidentDef letterLabel/letterText | 115 | static + [symbol] |
| Letters (conditions/sites/mental) | GameConditionDef ×26, SitePartDef ×45, MentalStateDef ×34 | 105 | static |
| Quests | QuestScriptDef node tree + rule packs | 133 | grammar, resolved at offer |
| Names — pawns/factions/settlements/features/art | RulePackDef via NameGenerator | 328 RulePacks total | pure grammar |
| Combat log | RulePackDef via BattleLogEntry_* | (in the 328) | grammar per event |
| Interactions (conversation bubbles) | InteractionDef ×43 + rule packs | 43 | grammar |
| Hediffs (health tab) | HediffDef label/description/stages | 230 | static |
| Precepts/rituals | PreceptDef ×174, RitualPatternDef ×19 | 193 | static + nameMaker |
| Memes/ideo presets | MemeDef ×22 (+IdeoDescriptionMaker grammar), IdeoPresetDef ×17 | 39 | mixed |
| Factions | FactionDef fixedName/leaderTitle/greetings/ideoDescription | 25 | static |
| Research | ResearchProjectDef | 120 | static |
| Recipes | RecipeDef jobString etc. | 180 | static |
| Genes/xenotypes | GeneDef ×130, XenotypeDef ×8 | 138 | static |
| Traits | TraitDef degreeDatas[] | 26 | static |
| Abilities | AbilityDef | 60 | static |
| PawnKind labels (gendered) | PawnKindDef | 207 | static |
| Biomes/weathers | BiomeDef ×18 (+settleWarning), WeatherDef ×17 | 35 | static |
| Scenario select + welcome | ScenarioDef ×7, ScenPartDef ×38 summaries | 45 | assembled |
| Anomaly codex | EntityCodexEntryDef | 15 | static, discovery-gated |
| Tales → art descriptions | TaleDef ×75 → RulePack grammar | 75 | grammar |
| Tutor/lessons | ConceptDef helpText | 58 | static |
| Royal titles | RoyalTitleDef + favor grammar | 6 | mixed |
| Alerts (top-right) | C# Alert_* classes — no def | UNMEASURED (dozens) | code/translation keys |
| Toasts (bottom-left) | C# Messages.Message call sites | UNMEASURED (hundreds) | code/translation keys |
| Presentation-only (LetterDef ×21, MessageTypeDef ×9, GenStepDef ×129) | — | — | carry no body text |

## 3. Our three tiers — current text state (lane B, MEASURED by XML parse, 60 mods)

| Tier | Defs | With desc | Missing | Placeholder/residue | Tier violations |
|---|---|---|---|---|---|
| RimMandrake (RM_) | 476 | 124 | 352¹ | 2 | **2** |
| RimStarWars (RSW_) | 4,089 | 2,037 | 2,052¹ | **276** | **3** |
| RimUtinni (RUT_) | 545 | 296 | 249¹ | 12 | 0 (allowed) |

¹ Much "missing" is structural (JobDef, GenStepDef etc. never carry text in
vanilla). **CORRECTED 2026-09-11 (wave-1 re-measure with ParentName
inheritance resolved):** the real Armoury+SWBestiary description debt was
**~57 entries** (42 defs shipping a literal "." inherited by 69 concrete
defs, 4 smuggling panels, 2 "TBD", 7 truly absent, 2 terrains) — the earlier
740/856/211 figures counted inherit-resolved and never-text def types. All
57 were written, registered in the absorption generator
(DESCRIPTION_BACKFILL entries, regen byte-identical), committed b8da9f097.
Remainder classification: design/Jawa/text/armoury_bestiary_desc_remainder.csv
(1,447 of 1,458 rows structural). PawnFlavor's label=0 is a parser artifact
(degreeDatas nesting), not debt.

**Tier-grammar violations (the owner's outside-scenario ruling made real):**
- CONFIRMED `RM_OpenPit_Oubliette` (Pits): says "droids" — RM tier must say
  mechanoids; vanilla has no droids.
- CONFIRMED `RM_WM_AutomatedSmelterRestoration` (WreckedMachines): "the
  Jawa's … knowledge" — campaign faction named at RM tier.
- CONFIRMED `RSW_GlassPearl` (SWBestiary): names **Ash'karr** — breaks in any
  other SW scenario.
- OWNER CALL OWED: `RSW_DW_Research_Reboot` + `RSW_Karrask` say "Jawa clan"
  — Jawas are generic SW canon, but the phrasing is campaign-flavored; is
  "Jawa clan" allowed at RSW tier? (Carded with the fixes ticket.)

## 4. Donor stack exposure (lane C, MEASURED vs dump 6fdca6f582164e2a, 577 mods, 2026-09-10)

⚠️ Live ModsConfig is currently the 13-mod minimal test list — the dump is the
best proxy for the campaign stack, ~1 day old. Cherry Picker cuts are
invisible to it (registrations zeroed, defs remain): donor counts are an
UPPER bound on what's live.

| Category | Ours | Donor | Vanilla | Read-probability (ESTIMATE) |
|---|---|---|---|---|
| Items | 495 | 3,591 | 748 | 30–50% encountered |
| Weapons | 135 | 340 | 71 | 30–50% |
| Apparel | 208 | 470 | 112 | 30–50% |
| Buildings | 90 | 6,884 | 841 | 30–50% (build-menu bloat) |
| Creature races / pawnkinds | 100 / 272 | 1,084 / 1,245 | 156 / 288 | 30–50% |
| Biomes | 28 | 65 | 22 | ~100% |
| Factions | 8 | 44 | 31 | ~100% |
| Backstories | 77 | 299 | 845 | 70–90% |
| Quests / Incidents | 2 / 1 | 89 / 226 | 151 / 131 | 70–90% |
| Thoughts / Interactions | 5 / 0 | 1,195 / 221 | 923 / 68 | 70–90% |
| Research / Recipes | 24 / 412 | 280 / 1,549 | 98 / 439 | 70–90% |
| Hediffs / Traits | 134 / 27 | 1,103 / 143 | 324 / 51 | 70–90% |

**The rename backlog is proper nouns, not volume.** Most donor thought/hediff
/recipe text is universe-neutral and needs nothing. The leaks that must be
owned (worst first): fantasy factions/xenotypes the player meets in raid
letters (**Orc Clan, trolls**), unthemed corporate/horror naming (**MiningCo.,
Horrors, Abomination**), unthemed race packs feeding pawn generation (Archon,
Saurid, Big & Small tribes). The megapack volume (VFE Props 3,661 defs, Alpha
Genes 2,312, Alpha Memes 1,990) is low-read build-menu/gene-list text. The SW
donors (SW Animal Collection 1,764, KotOR 1,222, Outer Rim 1,051) are
near-lore already — lowest rename priority.

## 5. Design-side systems — locked vs draft (lane D, verified against doc headers)

| System | Owes | Status | Size |
|---|---|---|---|
| Biome sheets (36/37 frozen) | Source lore all biome/thing text generates from | **LOCKED** | ~45–55k words ESTIMATE |
| Mindstone legends deck | 5 entries + scoping/gates | **LOCKED** (ruled today) | done — wiring owed |
| Ninefold: names + voice law (cast bible green-lit) | Per-god statement/reaction LINES | law LOCKED, **lines: 0 written** | UNMEASURED corpus |
| Oracle prompt/persona packs (counts as lore load, ruled) | Persona blocks per consumer | architecture LOCKED, **content: 0** | — |
| Dungeon set-pieces (Assailant + 6 Forsaken vaults) | Reveal letters, branch text, vault prose | **HELD FOR OWNER** (its own triage table) | 0 written |
| Ocular Overdrive site | Site + dungeon text | item OCULAR_OVERDRIVE_SITE_1 exists, **proposed/unruled** (lane D missed it — corrected here) | 0 written |
| Narrator corpus (triads, letters) | Voice bible chapters | 5/6 files **DRAFT**; the_knowing.md canon | — |
| Faction religions spec | Per-faith dressing | **LOCKED** as spec (9,076 words) | deeper voice text draft |
| Scenario text | Welcome/narration | structure **LOCKED**; narration just re-registered (SCENARIO_DURATION_CUT_1) | polish only |
| Pawn flavor | Volume mandate: 5 child/10 adult/15 traits per faction | v1 SHIPPED (50+5) = LOCKED; **mandate gap DRAFT** | UNMEASURED gap |
| Staged-lore description swaps | Stage-variant text for everything | feasible, **BUILD UNDECIDED** | would multiply locked text |
| Quest/plot text (Kyber, Flood, Vault Thaw, ~15 text-bearing items) | Letters, dialog, narration | **DRAFT** (specs not authored) | — |

## 6. The load, triaged (ESTIMATE ranges; entries × typical words)

**GENERATE NOW (locked lore, tickets filed — §7):** ~10–20k words
*(revised down 2026-09-11: the backfill line was an overcount — see §3
correction; both the backfill and the tier fixes shipped same-day)*
- Armoury+SWBestiary description backfill: **DONE** — real debt was ~57
  entries, written and generator-registered (b8da9f097)
- Tier-grammar fixes: **DONE** (e35831086, FOUNDRY); "Jawa clan" ruled NOT
  allowed at RSW — two rewordings owed (RSW_DW_Research_Reboot, RSW_Karrask)
- Donor proper-noun renames (bounded set once scanned): patch text, ~2–5k
- Biome/faction/scenario polish from frozen sheets: ~3–5k

**DESIGN FIRST (lore not up to it — tickets filed):**
- Ninefold god lines + Oracle persona packs (law locked, needs authoring
  sittings with the owner — the most lore-dense text in the game)
- Dungeon set-piece prose (explicitly held for owner)

**DEFERRED until lockdown (named dependencies, no tickets yet):**
- Narrator corpus (drafts must be confirmed) · pawn-flavor volume expansion
  (faction set still moving) · staged-lore variants (build undecided — would
  reopen frozen sheets) · quest/plot text (per-item specs first) · Ocular
  Overdrive (site unruled) · donor text behind pending Cherry Picker culls
  (don't rename what may be cut).

## 7. Tickets (filed 2026-09-11 from this report)

- `TIER_GRAMMAR_TEXT_FIXES_1` — the 3 confirmed violations + the "Jawa clan
  at RSW" owner card. Small, locked, FOUNDRY.
- `BESTIARY_ARMOURY_DESC_BACKFILL_1` — the ~1,830-entry description backfill
  + placeholder purge, generated against frozen sheets and the naming
  grammar; tier-generic variant discipline enforced in the same pass.
- `DONOR_PROPER_NOUN_SCAN_1` — instrumented scan of donor text for off-lore
  proper nouns → the bounded rename-patch backlog (fantasy factions,
  xenotypes, corporate names first; SW donors last).
- `GOD_LINES_ORACLE_PACKS_1` — design+authoring: Ninefold statement/reaction
  lines and Oracle persona packs, owner sittings required (needs owner).
- `DUNGEON_SETPIECE_TEXT_1` — design: the held-for-owner vault/reveal prose,
  scheduled when he sits to it (needs owner).

Deferred rows above deliberately carry NO tickets — each names what must
freeze first, per the lockdown ruling.
