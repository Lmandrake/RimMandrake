# Salvaging skill — engineering feasibility (2026-10-03)

Owner's ask (typed 2026-10-03): a new "Salvaging" skill the Jawa are legendary at, that replaces
recycle/disassembly skills, without becoming a total conversion. Planning only; no decision made.

## 1. Engine: how SkillDefs work in 1.6

All facts below read from the decompiled 1.6 source via RimSage on 2026-10-03.

**A SkillDef is XML-addable and the engine iterates every one generically.** The bulk of the game reads
`DefDatabase<SkillDef>.AllDefs`, not a hardcoded list:

| System | What a new SkillDef gets for free | Source |
|---|---|---|
| Pawn skill record | `Pawn_SkillTracker` ctor adds a `SkillRecord` per SkillDef | `Pawn_SkillTracker..ctor` |
| Existing saves | `ExposeData` PostLoadInit adds any missing skill, logging a **Warning** per pawn ("had no X skill. Adding.") | same file |
| Pawn generation | `PawnGenerator.FinalLevelOfSkill` runs for every skill: 0-4 base (or a curve if `usuallyDefinedInBackstories=false`), plus backstory `skillGains`, trait `skillGains`, age curves, `kindDef.extraSkillLevels`, and a `PawnKindDef.skills` range override | `PawnGenerator.FinalLevelOfSkill` |
| Passions | generic; growth-moment passion choices (Biotech children) draw from all skills | `ChoiceLetter_GrowthMoment` |
| Genes (Biotech) | `GeneDefGenerator` auto-creates aptitude/passion genes from every `GeneTemplateDef` x every SkillDef (`Aptitude<X>_RM_Salvaging` etc.) | `GeneDefGenerator.ImpliedGeneDefs` |
| Neurotrainers (Royalty) | auto-generated one per skill, shared texture | `ThingDefGenerator_Neurotrainer` |
| Skill books (Anomaly-era reading) | `BookOutcomeDoerGainSkillExp` picks from all skills | that class |
| Disable logic | `SkillDef.IsDisabled` = disabled if `disablingWorkTags` hit, or if **every** WorkTypeDef listing it in `relevantSkills` is disabled | `SkillDef.IsDisabled` |

**What a new SkillDef does NOT get for free:**

1. **Character card height.** `SkillUI.DrawSkillsOf` draws one 27 px row per skill into a fixed
   258 px-wide rect whose height is the card's remainder; `CharacterCardUtility.BasePawnCardSize`
   is a hardcoded `(480, 455)` and `MainRectsHeight` 355. Vanilla's 12 skills use 12 x 27 = 324 px;
   a 13th row needs 351 px, which is inside 355 with ~4 px spare — so ONE extra skill very likely
   fits on a plain card, a second does not. **UNMEASURED live**: the top stack (titles, ideo, faction,
   extra-faction rows) pushes the skills rect down, and our ~630-mod list already alters that card.
   Must be checked by a screenshot of the Bio tab on a busy pawn (titled, ideo, quest lodger).
   Mods that add 2+ skills ship a Harmony patch to `PawnCardSize`/`DrawSkillsOf` or a scroll view.
2. **Gene icons.** The five skill gene templates use `UI/Icons/Genes/Skills/{defName}/Terrible|Poor|
   Strong|Remarkable|PassionDrop`. A new skill needs those five PNGs or the genes render magenta.
3. **Hardcoded vanilla skill hooks.** ~90 call sites name `SkillDefOf.<X>` directly (see section 2).
   Nothing ever asks a new skill for anything until we write the code that does.
4. **Mechanoids.** Mechs have no `pawn.skills`; every skill check falls back to
   `RaceProperties.mechFixedSkillLevel` (default 10) via `Bill`, `QualityUtility`,
   `SkillRequirement`, `GenConstruct`. A recipe moved to a new skill still works for mechs as long
   as some `mechEnabledWorkTypes` WorkType lists that skill in `relevantSkills`
   (`SkillRequirement.PawnSatisfies`). If not, mechs silently lose the job.
5. **Book/filter special filters** (`SpecialThingFilterWorker_AllowBook<Skill>`) are one C# class per
   vanilla skill; a new skill's books are unfiltered. Cosmetic.
6. **Work types.** A skill does nothing unless a WorkTypeDef lists it in `relevantSkills` (that is
   what the Work tab, passion-on-work-type, and the disable logic read) and job drivers set
   `toil.activeSkill` / call `skills.Learn(...)` for it. A recipe's `workSkill` handles both for
   bills (`Bill` level checks, XP via the recipe's `workSkill`).

**Inspirations, mental breaks, quests/rewards:** no generic per-skill wiring found that would break.
Inspirations are quality/work-speed effects keyed to specific defs; quest rewards that grant skill XP
pick among existing skills. Neither needs anything from a new skill, and neither will feature it
unless we author content.

**Verdict on section 1:** adding the def is cheap and safe (XML + 5 icons). The cost is entirely in
making the def *mean* something: every "taking apart" action today is hardcoded to Construction or
Crafting and must be re-pointed one by one (section 2), and every PawnKind/backstory that should be
good at it must say so.

## 2. Inventory: where "taking things apart" uses a skill today

Read from 1.6 + all-DLC defs and source via RimSage. "Take-over" is how a Salvaging skill would claim it.

| Act | Today: skill / speed / yield | Who does it | Take-over route | Cost |
|---|---|---|---|---|
| **Deconstruct** building (`JobDriver_Deconstruct` < `JobDriver_RemoveBuilding`) | XP: Construction 0.25/tick (only if the building has a cost list). Speed: `ConstructionSpeed` x1.7 (Construction skill). `activeSkill` Construction. **Yield: flat `resourcesFractionWhenDeconstructed` (0.5), NO skill effect** | Construction work type, giver `Deconstruct` | Harmony on `JobDriver_RemoveBuilding.MakeNewToils` (speed stat + activeSkill are inside the base toil, so Uninstall is hit too unless split) and `JobDriver_Deconstruct.TickActionInterval` (XP); yield scaling needs a Harmony on `GenLeaving` (the `DestroyMode.Deconstruct` count lambda) | C#, medium. Moves a core Construction job; Construction keeps only building |
| **Deconstruct for blueprint** (gravship/Odyssey) | same as above (subclass) | Construction | same patch | free once above done |
| **Uninstall** (minify) | `ConstructionSpeed`, activeSkill Construction, no XP | Construction | Leave it. Uninstall is moving, not taking apart | none |
| **Smelt weapon / apparel / smelt-or-destroy** (`SmeltWeapon`, `SmeltApparel`, `SmeltOrDestroyThing`) | **No `workSkill` at all.** Speed `SmeltingSpeed`, whose own description says "smelting is dumb labor, not affected by any skill". **Yield fixed 25%** of cost list (`Thing.SmeltProducts`, hardcoded 0.25f; the `efficiency` argument is passed but never used) | Crafting work type, giver `DoBillsSmelter` | XML patch: add `workSkill RM_Salvaging` + an `efficiencyStat` — but **efficiency does nothing to smelting yield** without a Harmony on `Thing.SmeltProducts` (or a GenRecipe postfix) | XML trivial; meaningful yield needs C# |
| **Slag to steel** (`ExtractMetalFromSlag`) | no skill, fixed 15 steel | Crafting/smelter | leave, or XML workSkill for XP only | trivial |
| **Destroy weapon / apparel** | no skill, no yield | smelter | leave (destruction, not salvage) | none |
| **Shred mechanoid** (`ButcherCorpseMechanoid`) | `workSkill` **Crafting**; speed `ButcheryMechanoidSpeed`; yield `ButcheryMechanoidEfficiency` = 0.75 + 0.025/Crafting level, cap 1.5 | Smithing work type, `DoBillsMachiningTable` | **Pure XML**: patch recipe `workSkill` and both StatDefs' `skillNeedFactors` to the new skill | trivial |
| **Disassemble own mech** (Biotech, `JobDriver_DisassembleMech`) | **no skill**, fixed 300 ticks, fixed `IngredientsFromDisassembly` | mechanitor | leave, or small Harmony for XP/yield | small C# |
| **Repair mech** (`JobDriver_RepairMech`) | Crafting XP + activeSkill | mechanitor | out of scope (repair is not taking apart) | none |
| **Repair building** (`JobDriver_Repair`) | Construction | Construction | out of scope | none |
| **Hack** (`CompHackable`, `JobDriver_Hack`) | **Intellectual**, with `intellectualSkillPrerequisite` | any | out of scope unless the owner wants "hacking a droid lock" as salvage; every hackable checks Intellectual by name | C#, wide |
| **Extract skull / tree / bioferrite / relic** | BasicWorker / Plants / Medicine | various | not salvage | none |
| **Remove floor / smooth** (`JobDriver_AffectFloor`) | Construction | Construction | not salvage | none |

**Odyssey and Anomaly add no new "take apart" verb.** Odyssey's salvage content is a *faction*
(`Salvagers`, `Salvager_Scrapper` pawnkinds) and orbital wreck sites whose loot is reached by the
ordinary Deconstruct/Mine/haul jobs. Anomaly's only "extract" is bioferrite (Medicine). Nothing
there to re-point; the new skill would only touch them through Deconstruct.

**Key finding the owner should hear:** in vanilla, the two most salvage-shaped acts carry almost no
skill at all. Deconstruct yield is a flat 50% regardless of who does it, and smelting is flat 25%
and deliberately skill-free. So a Salvaging skill is not *replacing* existing skill play there; it
is *inventing* it. That is where its identity value lives, and also where the balance risk lives:
the moment yield scales with a skill the Jawa are legendary at, deconstruction becomes a
resource engine.

**Our own content already in the repo:** no SkillDef anywhere under `src/`. Salvage-flavoured
content exists as map/faction/building defs (`RUT_FoundrySalvageCache`, `JawaGroundHulk` prefab,
`JawaJunkers` faction, `DroidsAreMachines` doctrine patch), none of which check a skill.

## 3. Active mod list: skill-adding mods and conflicts

MEASURED 2026-10-03 by parsing the live `ModsConfig.xml` with ElementTree: **610 active mods**, 604
resolved to an installed folder across both roots (6 are DLC/Core with no `About` in those roots).
Every `.xml` in every active mod was searched for a `<SkillDef` element and every `.dll` for the
skill-UI symbols `SkillUI` / `DrawSkillsOf` / `PawnCardSize`. Sanity probe: the same pass found 5,502
XML files containing `<ThingDef`, so the scan can see.

- **Active mods defining a SkillDef: 0.** (One hit, Custom Quest Framework, is a translation string,
  not a def.) So we would be the only mod adding a skill: no prior art in our list, and also no
  collision.
- **Active DLLs touching the skill UI (real hits):** Vanilla Skills Expanded (`vanillaexpanded.skills`,
  adds per-skill expertise and redraws skill rows), Character Editor, RimHUD, Numbers, Better Growth
  Moments. Copies of `Assembly-CSharp.dll` bundled inside several mods matched too and are false
  positives.
- **Whether each of those iterates all SkillDefs or hardcodes the vanilla 12: UNMEASURED.** VSE is
  the one that matters: it owns the skill row drawing and has per-skill expertise defs, so a new skill
  will at minimum get no expertise unless we author some, and its row drawing must be checked for the
  13-row height. RimHUD and Numbers draw their own panels/columns and are the next two to check.
  The cheapest proof is one quicktest pawn with the def loaded and a screenshot of the Bio tab, RimHUD
  panel and Numbers table.
- **Character card height** (section 1): one extra row probably fits the vanilla card with ~4 px to
  spare. With VSE redrawing rows, the margin is UNMEASURED.

## 4. Alternatives short of a new skill

The Jawa are a xenotype (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/MandrakeJawaXenotype.xml`),
so every option below can make them "legendary" through genes. What differs is whether salvage
talent can be **separate from building talent**, which is the owner's actual requirement.

| | A. New SkillDef `RM_Salvaging` | B. Salvaging STAT(s) only | C. Pseudo-skill (hediff/gene that levels up) | D. New WorkType "Salvage" on existing skills |
|---|---|---|---|---|
| What the player sees | a 13th skill row with passion flames, levels 0-20, XP | numbers in the stat panel ("salvage yield 140%"); no row, no passion | a health-tab or gene entry with a level; no passion, no Work tab link | a new column in the Work tab; no new talent number |
| Separate from building talent? | **Yes, fully.** Deconstruct XP stops feeding Construction | **No**, if fed by Construction/Crafting skill (that is exactly "good builder = good salvager"). Only yes if driven purely by genes/traits/gear and never by a skill | Yes, but we hand-build learning, decay, display | **No**, it averages Construction+Crafting |
| "Legendary Jawa" route | xenotype carries the engine's auto-generated `AptitudeRemarkable_RM_Salvaging` gene (+ passion gene) for free | custom gene with `statOffsets`/`statFactors` | custom gene/hediff | none of its own; needs B as well |
| Build cost | SkillDef + 5 gene icons + WorkType + XML repoint of mech shredding + **C# Harmony** on Deconstruct (speed/XP/activeSkill) and smelting yield + backstory/pawnkind `skillGains` across Jawa content + Mod Settings toggle | 1-3 StatDefs + XML patches to recipes (`efficiencyStat`/`workSpeedStat`) + **the same C#** for deconstruct/smelt yield, since those don't read any stat today | most C#: our own XP, UI, save data; reinvents SkillRecord | WorkTypeDef + move WorkGivers; XML only |
| Total-conversion risk | **Highest.** Touches every pawn in the game (all factions get the row and a random level), every save, every UI mod that draws skills (VSE, RimHUD, Numbers, Character Editor) | Low: invisible to anything that doesn't read the stat | Low-medium | Low; but moves Deconstruct out of the Construction column for everyone |
| Mod compat | UNMEASURED for the four UI mods; 0 active mods add a skill (no prior art either way) | none expected | none expected | Work-tab mods handle new WorkTypes routinely |
| Save compat | Safe: engine adds the missing skill on load with a Warning per pawn. Moot anyway: world is remade at the end and no saves exist | safe | needs Scribe care | safe |
| Removability | Hard: once backstories, genes, xenotype, recipes and quests name the skill, turning it off means a missing def | Easy: stats default to base value | medium | easy |

**Honest read of the alternatives:** B and D are cheap and safe but cannot deliver what the owner
asked for. Both tie salvage to the existing Construction/Crafting skill, so a Jawa who is legendary at
salvage is also a legendary builder or crafter, which is the "shining pagodas" outcome he named. B
can avoid that only by ignoring skill entirely and letting genes/gear set the number, which gives a
racial bonus but nothing that grows with practice. C gets separation without the UI row but means
writing our own skill system badly. **A is the only option that makes salvage a talent of its own
that rises with use and leaves Construction/Crafting untouched**, and the engine supports it better
than expected (generic tracker, auto-generated genes, safe save upgrade).

The C# cost is the same for A and B: Deconstruct and smelting have **no** yield lever in vanilla, so
any option that makes salvage *yield* depend on talent needs Harmony on `GenLeaving` (deconstruct
refund) and `Thing.SmeltProducts` (hardcoded 25%). The difference between A and B is not the
code, it is the reach: A shows up on every pawn on the planet.

## 5. Recommendation and decision points

**Recommendation: feasible, and A (a real SkillDef) is the right shape, but only in a deliberately
narrow form.** Ship it as `RM_Salvaging` in a franchise-free `RM_` mod (the mechanic is not Star
Wars IP; the Jawa get legendary at it through their xenotype's aptitude gene and their backstories),
covering exactly: deconstruct, mech shredding, smelting, and our own salvage recipes/caches. Leave
building, crafting, repair, uninstall and hacking where they are. Before committing, pay for one
cheap proof: load the def on the quicktest list and screenshot the Bio tab, VSE rows, RimHUD and
Numbers, because the UI fit is the one thing that could turn a narrow feature into a UI rewrite.

Effort estimate (rough, for scale only): XML + icons + WorkType ~ a day; Harmony for deconstruct
speed/XP/yield and smelt yield ~ a day plus a functional script; authoring Jawa backstory/pawnkind
gains ~ a pass over existing Jawa content. The UI fit is the unknown.

**Decisions for the owner, in plain language:**

1. **Does every pawn on the planet get the skill, or only matter for some?** A real skill appears on
   every person in every faction, with a random level. That is the honest cost of "a new skill".
   The alternative (a hidden stat that only Jawa genes raise) never shows a row and never grows with
   practice. *Trade: identity and growth vs. the game looking unchanged for everyone else.*
2. **Does salvage talent change how MUCH you get, or only how FAST?** Vanilla gives a flat 50% back
   from deconstruction and a flat 25% from smelting, no matter who does it. Letting skill raise the
   yield is what makes a legendary Jawa feel legendary, and also what can turn deconstruction into a
   free-resources machine. Speed-only is safe and dull; yield needs a cap. *Trade: Jawa fantasy vs.
   economy balance. Suggest: speed always, yield up to a modest cap, and only above vanilla at high
   levels.*
3. **Where does the line sit between "taking apart" and its neighbours?** Proposed IN: deconstruct,
   shred mechanoids, smelt weapons/apparel. Proposed OUT: uninstall/moving, repair, hacking
   (Intellectual), disassembling your own mechs. Each item moved in takes XP and identity away from
   Construction or Crafting for every pawn. *Trade: a bigger, more meaningful skill vs. a smaller
   blast radius.*
4. **What happens to Construction when it stops learning from deconstruction?** Today, tearing
   things down is one of the main ways colonists get better at building. Moving it means Jawa (and
   everyone) level Construction more slowly, which is exactly his "no shining pagodas" wish, but it
   also slows every non-Jawa colony that relies on teardown to train builders. *Trade: the Jawa
   fantasy vs. a quiet nerf to vanilla play.*
5. **Is a 13th row on the character card acceptable if it needs a UI change?** One extra row probably
   just fits the vanilla card; with Vanilla Skills Expanded and RimHUD redrawing skills, that is
   unproven. If it does not fit, we either patch the card taller (touches every pawn screen) or
   abandon the row for the stat route. *Trade: worth a quick test before deciding, not a guess.*
