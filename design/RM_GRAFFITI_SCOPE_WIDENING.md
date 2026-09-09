<!-- status: draft — Fable design pass for owner ruling, 2026-09-09. Item: GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 (design only; no code, no queue writes). Ground truth for what exists: src/RimMandrake/Graffiti/ (read in full) and items/GRAFFITI_FRAMEWORK_BUILD_1.md. Sibling in flight, NOT superseded: GRAFFITI_GENERIC_MARKS_1 (six glyphs). Predecessor spec, still the campaign side's authority: design/Jawa/graffiti_spec.md. Vanilla mechanisms cited below were read from RimWorld 1.6 source via RimSage, file and line named; nothing is guessed. -->
# RM Graffiti — widening the base mod: punk-urban marks and ideoligion sigils

_Owner, verbatim (2026-09-09): "we want the base Graffiti mod to have a wide
variety of functionality within it, not just the base examples we've provided
in vanilla. It should be a mod more aligned to punk style graffiti such as is
seen in urban settlements, as well as ideoligion-inspired sigils taken from the
Rimworld ideoligions as they exist in the game. Then we will go rich and fill in
the Utinni modpack for it."_

**What this document decides and what it does not.** It proposes the ENGINE
surface `mandrake.rm.graffiti` (RM tier, generic, no franchise or campaign
vocabulary) should grow to, names what is genuinely new mechanically versus
reskinned, draws the RM/RUT seam so the Salvation follow-on is a content pack
and not a second engine, and lists the forks the brief does not decide. It
does not build anything, and it does not touch the six generic glyphs
GRAFFITI_GENERIC_MARKS_1 is authoring — those are treated as a starting subset
(§2.4).

---

## 0. What exists today (MEASURED from the source, not the About.xml)

`mandrake.rm.graffiti` ships the engine's spine and exactly one mark:

| Piece | File | What it actually does |
|---|---|---|
| `RM_BaseGraffiti` | `Defs/ThingDefs_Graffiti.xml` | abstract parent: `thingClass Filth`, `placementMask Unnatural`, `canPlaceOverWall`, `rainWashes`, Beauty via `statBases` |
| `RM_Graffiti_Vandal` | same | the ONE concrete mark — `Graphic_Random` over six donor textures, Beauty −15 |
| `ModExtension_Graffiti` | `Source/ModExtension_Graffiti.cs` | per-mark data: `category` (Sacred/Mural/Jest/Taunt/Cant), `visibility`, `supportsQuality`, `hasSubject`, `tracksMaker`, `viewerReactionThought`, `godSatiationHook`, `breachLure`; a startup validator names three mis-wire shapes |
| Spree | `JobDriver_PaintGraffiti`, `JoyGiver_PaintGraffiti`, `JobGiver_GraffitiPaintingSpree`, the MentalState/ThinkTree defs | colonist joy job + mental break; **spawns `RMGraffitiDefOf.RM_Graffiti_Vandal` by hard reference** (`JobDriver_PaintGraffiti.cs:70`) — the spawn loop is still closed around one defName, exactly the defect the 2026-08-30 assessment found in the donor mod |
| Viewer reaction | `ThoughtWorker_ViewedGraffitiMark.cs` | one situational ThoughtDef per mark, 8-cell radius, room-gated; `ClanOnly` withholds it from non-player pawns |
| Breach bias | `BreachBiasHook.cs` | Harmony postfix on `BreachingGrid.FindBuildingToBreach`: raiders breach beside a `breachLure` mark — the only faction-aware behaviour in the mod, and it READS marks, it never places one |
| Ritual placement | `src/RimMandrake/SacredGraffiti/Source/SacredGraffiti.cs` | `RitualOutcomeEffectWorker_PlaceSacredMark` spawns `filthDefToSpawn` on a positive ritual outcome; no ritual references it yet; MOD_CONSOLIDATION_PLAN moves this C# into Graffiti |

**Three honest gaps in the declared data layer**, found reading the code, not
the item history:

1. **`supportsQuality` cannot work on a Filth mark.** `Filth : Thing`
   (`RimWorld/Filth.cs:7`), not `ThingWithComps` — no `CompQuality`, no
   `CompArt`, no comps at all. The Mural family's "quality-tiered like
   sculpture" needs a different `thingClass` (fork F1).
2. **`tracksMaker` and `hasSubject` have no storage.** Nothing on the spawned
   `Filth` records who painted it, for which faction or ideo, or about whom.
   "Marks carry information" is declared and unimplemented.
3. **Every placer is colonist-only or inert.** The spree paints one defName;
   the ritual worker has no ritual; nothing lets an enemy, a visitor or a
   generated settlement put a mark on a wall. A graffiti mod whose only
   authors are your own colonists cannot express territory, threat, or
   another culture's presence — which is most of what graffiti IS.

In flight and untouched by this design: **GRAFFITI_GENERIC_MARKS_1** has six
candidates through art review (`RM_Mark_arrow / handprint / hazard / spiral /
sun / tally`, Transient/art_review_generic_marks/final/). They are the
wayfinding/warning subset of §2.

---

## 1. The engine surface — what "wide variety of functionality" means beyond art

Seven mechanical pieces. Each is named, each says what vanilla already gives
us (with the source line), and each says what is new C#.

### 1.1 `Filth_Mark` — a mark that knows its provenance

A `Filth` subclass (`RimMandrake.Graffiti.Filth_Mark`) that `RM_BaseGraffiti`
adopts as its `thingClass`. It adds `IExposable` state the base class lacks:

| Field | Meaning | Who reads it |
|---|---|---|
| `makerPawn` (weak ref) | who painted it | caricature/accusation reactions; the inspect line; "who did this" |
| `makerFaction` | whose mark it is | territorial reading, goodwill reactions, going-over rules |
| `makerIdeoId` | the ideoligion it belongs to | sigil rendering (§1.3), relation-keyed thoughts (§1.5) |
| `subjectPawn` (weak ref) | who it is about, if anyone | the Shaming tier's viewer opinion effect |
| `placedTick`, `placer` | when and by which placer (enum) | aging, layering, letters/inspect text |

`Filth` already scribes `thickness`, `sources` and `drawInstances`
(`Filth.cs:64-77`); this adds five more `Scribe_*` lines. The inspect string
becomes `"<form> of the <ideo adjective> <faction name>"` — vanilla's own
`Ideo.adjective` / `Ideo.memberName` (`Ideo.cs:53-55`) supply the words, so a
generated raider religion called "Plunderism" leaves marks labelled
"plunderic tag". **New C#: one class, ~120 lines.** This is the single piece
everything else in this document depends on.

### 1.2 Two axes per mark: FORM and FUNCTION

Today one enum (`GraffitiCategory`) conflates what a mark looks like with what
it does. Split it:

- **`GraffitiForm`** — the visual/cultural grammar: `Scrawl` (the untrained
  vandal daub), `Tag` (a fast one-colour signature), `ThrowUp` (two-colour
  bubble letterforms, bigger, faster to read), `Stencil` (repeatable, crisp,
  political), `Paste` (a wheat-pasted paper poster — weathers, tears),
  `Sigil` (an ideoligion's emblem), `Glyph` (a wayfinding/warning symbol —
  the six in-flight marks), `Piece` (a mural: large, slow, quality-bearing).
- **`GraffitiCategory`** stays the FUNCTION axis, renamed generic where the
  current names lean campaign: `Devotional` (né Sacred), `Mural`, `Jest`,
  `Taunt`, `Code` (né Cant — "clan-only wayfinding" is a Jawa idea; a
  raider gang's crew marks are the same mechanism). Fork F8 asks whether the
  rename is worth the churn.

Form drives: art conventions, `cleaningWorkToReduceThickness` (a paste peels
in a fraction of a stencil's scrub), `rainWashes`, whether it can be layered
over (§1.6), and the inspect noun. Function drives: reactions, breach lure,
visibility, god hooks. A `Stencil`+`Taunt` and a `Sigil`+`Devotional` are
different marks with different art but share every mechanic on their axis.

### 1.3 Ideo-driven appearance — the sigil mechanism, three tiers of cost

The load-bearing finding of this pass: **vanilla already renders "this thing,
styled for that ideoligion", and it works on Filth.**

- `Thing.Graphic` (`Verse/Thing.cs:478-497`) returns `StyleDef.Graphic` when
  a `ThingStyleDef` is set, for ANY `Thing` — Filth included; `Thing.StyleDef`
  is a virtual property with a setter (`Thing.cs:127-136`).
- `Ideo.GetStyleFor(ThingDef)` (`RimWorld/Ideo.cs:1562`) resolves the style an
  ideoligion uses for a def, through the ideo's `thingStyleCategories`
  (`Ideo.cs:95`) and each `StyleCategoryDef.thingDefStyles` row
  (`Verse/StyleCategoryDef.cs:75`).
- `FilthMaker.TryMakeFilth(c, map, def, out Filth outFilth, …)`
  (`RimWorld/FilthMaker.cs:65`) hands back the spawned instance, so a placer
  can set `outFilth.StyleDef = ideo.GetStyleFor(def)` on the spot.
- Every ideoligion carries an emblem and a colour: `Ideo.iconDef`
  (`IdeoIconDef`, `Ideo.cs:57`; `Icon` at line 125) and `Ideo.colorDef`
  (`ColorDef`, line 59; `ApparelColor` at line 145 = faction colour, else the
  ideo colour). Vanilla Ideology ships **93 `IdeoIconDef`s (28 universal, 65
  gated to memes or cultures)** and **33 `IdeoColorDef`s** — counted from
  `Defs/Ideology/IdeoSymbolDefs/`. The gating is data: e.g. `AnimalsA-E`
  require `Rancher`/`AnimalPersonhood`, `Archist_*` require
  `Structure_Archist`, `Eagle` requires culture `Corunan` or `NaturePrimacy`
  (`IdeoIconDefs_Specific.xml:4-120`). So the emblem already encodes the
  memes.
- Named deities carry their own `iconPath` and `relatedMeme`
  (`IdeoFoundation_Deity.Deity`, `IdeoFoundation_Deity.cs:13-23`).

Three sigil tiers, cheapest first; the owner picks the v1 tier (fork F2):

| Tier | Mechanism | Art cost | What it gives |
|---|---|---|---|
| **A — Icon sigil** | `Filth_Mark` with `form=Sigil` draws the ideo's own `Icon` texture over a sprayed frame, tinted `DrawColor` → `ideo.ApparelColor` (`Thing.DrawColor` is virtual, `Thing.cs:638`) | **~3 frame textures** (halo, stencil-box, drip-frame) | every ideoligion in the game, generated or authored, has a wall sigil on day one, in its colour, with zero per-ideo art. A Cannibal/Morbid raid's sigil is their skull icon; a Rancher settlement's is their animal icon |
| **B — Style-variant marks** | RM patches `StyleCategoryDef.thingDefStyles` rows for its own mark defs across the 11 vanilla categories (`Hindu Christian Islamic Buddhist Morbid Totemic Spikecore Rustic Animalist Techist Horaxian`, `Defs/Ideology/StyleCategoryDefs/`); a placer sets `StyleDef` from `ideo.GetStyleFor` | **11 × N** per styled mark def | a Techist "warning" glyph is circuitry; a Totemic one is bone and cord; the same def, the ideo's dialect. Recommend N=2 in v1 (the sigil frame and the territorial tag), never the whole set |
| **C — Meme-affinity marks** | mark defs declare `requiresAnyMeme` (MayRequire-wrapped `MemeDef` list) and the pool selector (§1.4) only offers them to an ideo holding one | **1 per meme** covered | the content of §3: the glyph a Raider gang, a Blindsight cult, a Tunneler warren leaves is DIFFERENT, not just recoloured |

All three read the ideo of the placing pawn (`pawn.Ideo`) or faction
(`faction.ideos.PrimaryIdeo`, `FactionIdeosTracker.cs:28`). All three are
soft on Ideology: without the DLC there is no `Ideo`, the sigil form is
absent from every pool, and tiers B/C rows are `MayRequire="Ludeon.RimWorld.Ideology"`.
RM must cold-load on Core alone; that is a test, not a hope (§7).

### 1.4 Pools and placers — a data-driven "which mark, where, by whom"

Replace the hard `RM_Graffiti_Vandal` reference with a selector every placer
calls: `GraffitiPool.Pick(PlacerKind placer, Pawn maker, Faction faction, Ideo ideo, GraffitiCategory? want)`.
Each mark's `ModExtension_Graffiti` grows the selection data:

```
placers          which PlacerKinds may spawn it  (Spree, Joy, Designator, RaidExit, RaidAssault, Visitor, SettlementGen, Ritual)
weight           float, per pool
requiresAnyMeme  MayRequire-wrapped MemeDef list   (tier C)
forbidsAnyMeme   same
requiresHostile  bool — only placed by a faction hostile to the map's owner (taunts, territorial claims)
minArtistic      int — designator/joy gating by skill
```

Placers, and what is new about each:

| Placer | Exists? | Hook (verified or flagged) | Notes |
|---|---|---|---|
| Spree / Joy | yes | `JobDriver_PaintGraffiti` | becomes pool-driven; skill and mood select Scrawl vs Tag vs ThrowUp |
| Designator + bill | **new** | ordinary `Designator` + `WorkGiver` + `JobDef`, the same shape as vanilla floor-drawing (`JobDriver_Floordrawing`, the model this driver already cites) | the player verb: pick a mark, pick a wall cell, an Artistic pawn paints it. Murals/Pieces get a bill with `WorkToBuild`-style duration |
| Ritual outcome | yes (SacredGraffiti) | `RitualOutcomeEffectWorker_PlaceSacredMark` | moves into Graffiti per the consolidation plan; unchanged |
| **Raid tagging** | **new** | a lord-toil hook on the assault lord's exit/flee transition (`LordToil_ExitMap`, `Verse/AI/Group/LordToil_ExitMap.cs:5`) — the exact transition point is **to be verified in the build**, not assumed here | raiders leave their faction's tag or sigil on an exterior wall on the way out (fork F3 decides in/out/both). This is where "graffiti as seen in urban settlements" becomes a live system: your walls accumulate the marks of everyone who has hit you |
| **Settlement generation** | **new** | a `GenStep` in the settlement map-gen (this project's Inhabited already ships `GenStep_RimplacePlan`) | an enemy or friendly settlement map is born already tagged in its own ideo's sigils, territorial tags on the approach, warnings at its defences. Fork F9: v1 or later |
| **Visitor / trader** | **new, optional** | on caravan/visitor lord departure | a friendly ideo leaves a small Paste or Tag; pool weight low. Gives the Proselytizer meme something to DO on your walls (§3.2) |
| Breach reading | yes | `BreachBiasHook` | unchanged; now `breachLure` marks can be raider-placed too, which is a gameplay loop (their taunt lures the next raid to the same door — a gang war on your wall) |

### 1.5 Relation-keyed viewer reactions

`ThoughtWorker_ViewedGraffitiMark` keys one ThoughtDef per mark. Extend the
extension to a small relation table, each entry a ThoughtDef or null:

```
onViewSameIdeo      a believer sees their own sigil  (small +)
onViewOtherIdeo     a believer sees a rival's sigil  (small −; scaled by ideo hostility if present)
onViewOwnFaction    your colonist sees your colony's tag  (pride, Jest laughs)
onViewHostileMaker  your colonist sees a mark a hostile faction left  (unease — the "we were here")
onViewSubject       the subject of a caricature/accusation sees it  (existing hasSubject path)
```

The worker already scans radius and room; the change is which ThoughtDef it
grants, decided from `Filth_Mark` provenance versus the viewer's `Ideo` and
`Faction`. Presence-only, no stacking, as today. **New C#: ~60 lines in the
worker, five fields in the extension.** This is what makes a raider's tag
carry INFORMATION rather than −15 Beauty: it is read differently by the
gang that painted it, the colony it was painted at, and a visiting third
faction.

### 1.6 Layering, going-over, and decay — the wall as a record

`Filth.thickness` (1..`maxThickness`, `Filth.cs:19,125`), `ThickenFilth()`
(virtual, line 124) and `disappearAfterTicks` (line 89) already exist.

- **Repainting the same cell thickens** (vanilla). `Filth_Mark` overrides
  `ThickenFilth` so a SECOND maker of a different faction/ideo does not
  thicken — it **goes over**: the old mark is replaced by the new one with
  `coveredFaction` recorded, and the covered faction's viewers take
  `onViewGoneOver`. Territorial graffiti's core verb, in one override.
- **Form decides decay.** `Paste` sets `filth.disappearsInDays`; `Stencil`
  and `Sigil` do not; `rainWashes` true for Scrawl/Tag, false for Stencil.
  Pure XML per form, already-supported fields.
- Fork F4 asks whether going-over ships in v1.

### 1.7 Scrub semantics

Vanilla home-area cleaning treats every Filth as dirt. With provenance on the
mark, the engine can decide: `protectedFromAutoClean` (an extension flag,
default true for `Devotional` and for marks whose `makerFaction == OfPlayer`)
makes `WorkGiver_CleanFilth` skip it; a "scrub mark" designator overrides.
Hook point (`WorkGiver_CleanFilth.HasJobOnThing` or the home-area filth
lister) is **to be verified in the build**. Without this, every sigil you
paint is scrubbed by your own cleaners within the day — the mod would fight
itself.

### 1.8 What is genuinely NEW versus reskinned

| Genuinely new mechanism | Reskin / data only |
|---|---|
| `Filth_Mark` provenance (1.1) | more mark ThingDefs on `RM_BaseGraffiti` |
| Pool selector + placer enum (1.4) | per-form `filth` field tuning (1.6 decay) |
| Raid-exit tagging placer (1.4) | tier-B style rows (`StyleCategoryDef` patches) |
| Settlement `GenStep` placer (1.4) | tier-C meme-affinity lists on the extension |
| Designator + work bill placer (1.4) | relation ThoughtDefs' text |
| Icon-sigil rendering with ideo tint (1.3-A) | the six in-flight glyphs joining the `Glyph` form |
| Relation-keyed reactions (1.5) | |
| Going-over override (1.6) | |
| Protected-from-clean + scrub designator (1.7) | |

---

## 2. The punk-urban register (vanilla-generic)

What makes wall-writing read as PUNK rather than as decoration: it is fast,
unsanctioned, territorial, repeated, anti-authority, layered over what was
there before, and it names its author with a signature nobody outside the
scene can read. Each of those is a mechanic above, not a texture. The forms
in §1.2 are the real-world taxonomy (tag → throw-up → piece; stencil;
wheat-paste; crossing-out/going-over; crew marks; slogans).

### 2.1 Text policy (fork F5, recommended: asemic)

Real graffiti is mostly LETTERS. RimWorld has no in-world script, and any
English word on a texture is a localisation and a franchise problem (the
Aurebesh variant is already reserved to RSW in graffiti_spec.md §5).
Recommended: **asemic letterforms** — throw-ups and tags drawn as
letter-shaped strokes that read as writing and spell nothing. The in-flight
gen prompt already forbids lettering; this extends it to "forms that look
like letters". Slogans then live in the inspect text, not the art.

### 2.2 Proposed RM punk set (v1 candidate list, ~14 marks)

| Mark (working defName) | Form · Category | Placers | What it does |
|---|---|---|---|
| `RM_Mark_Scrawl` (= today's Vandal) | Scrawl · Jest | Spree, Joy | untrained daub, Beauty −15, the floor of the ladder |
| `RM_Mark_Tag_A/B/C` | Tag · Code | Spree, Joy, RaidExit, Visitor | one-colour signature, tinted by maker faction colour; the crew's "we were here"; low Beauty penalty; goes over Scrawls |
| `RM_Mark_ThrowUp_A/B` | ThrowUp · Taunt | Joy (skill ≥ 6), RaidExit | two-colour bubble letterforms; bigger read radius; hostile-maker unease |
| `RM_Mark_CrossOut` | Tag · Taunt | RaidExit, Designator | the going-over mark: an X and a new tag over a covered one — only placeable OVER a rival's mark |
| `RM_Mark_Stencil_Crown` | Stencil · Taunt | Designator, RaidExit (`requiresAnyMeme` none; `requiresHostile` to Empire) | a crossed-out crown: anti-authority in the one register vanilla owns (Royalty's Empire). Empire visitors: `onViewHostileMaker` |
| `RM_Mark_Stencil_Gear` | Stencil · Taunt | Designator, RaidExit | a broken gear/mechanoid silhouette — anti-machine, the other vanilla authority |
| `RM_Mark_Stencil_Fist` | Stencil · Jest/Taunt | Designator | raised fist — a generic defiance stencil |
| `RM_Mark_Paste_Flyer` | Paste · Jest | Visitor, Designator | a pasted paper poster, asemic headline; decays in days, peels in rain; small Jest thought; a Proselytizer settlement's visitors leave these |
| `RM_Mark_Paste_Wanted` | Paste · Taunt | RaidExit, SettlementGen | a torn "wanted"-style poster with a silhouette; hostile marker |
| `RM_Mark_Glyph_*` (six) | Glyph · Code | Designator, SettlementGen | GRAFFITI_GENERIC_MARKS_1's arrow / handprint / hazard / spiral / sun / tally — wayfinding and warning; `hazard` gets `breachLure` as the engine's one generic taunt-funnel example |
| `RM_Mark_Piece_Base` | Piece · Mural | Designator bill only | the mural placeholder; quality-bearing once fork F1 rules the thingClass |

Fourteen assets at the in-flight prompt's cost (one Codex call + validate
each, per generating-rimworld-sprites) plus three sigil frames for §1.3-A.

### 2.3 Behaviours that make the set punk rather than pretty

- **Tags cluster.** The RaidExit placer prefers an exterior wall cell already
  carrying another faction's mark (going over) and, failing that, a cell
  adjacent to your door. Your entrance becomes the contested wall.
- **A crew signs.** Every RaidExit mark is tinted by `faction.Color` and
  labelled with the ideo adjective. Two raids from the same gang leave
  matching tags; you learn their hand.
- **Slogans are cheap and disposable.** Pastes decay; stencils do not. The
  player can leave a defiance stencil facing the map edge (a Taunt with
  `breachLure`) and pay for it in the next raid's approach.
- **Your own vandals are part of the scene.** The spree's output is now
  chosen from the pool by skill: a Scrawl from a wretch, a ThrowUp from an
  artist — the same mental break reads differently on different pawns.

### 2.4 Relationship to GRAFFITI_GENERIC_MARKS_1

The six glyphs are the `Glyph` form, `Code` category, as-is. This design
adds forms around them; it does not change their art, names, or the owner's
review of them. If the owner's review cuts some, the form has fewer members.

---

## 3. The ideoligion-sigil register (grounded in shipped Ideology data)

"Ideoligion-inspired sigils taken from the RimWorld ideoligions as they exist
in the game" cannot mean a fixed list of religions: vanilla ideoligions are
GENERATED at world creation (there is no `IdeoDef`; see the
`rimworld-ideoligion` skill §1). What exists in data is the vocabulary they
are generated from — memes, structures, symbol packs, icons, colours, deities,
style categories. So a sigil system keys off THAT vocabulary, and then any
generated or authored ideo, including Salvation, gets sigils for free.

### 3.1 Tier A — the emblem is the sigil (every ideo, no per-ideo art)

`Ideo.Icon` + `Ideo.ApparelColor` drawn inside a sprayed frame (§1.3-A). The
Ideogram building (`Defs/Ideology/…/Ideogram`, `CompProperties_Styleable`,
`IconChristianA` default) is vanilla's own precedent for "draw this
ideoligion's emblem on the ground as a built thing"; the sigil mark is the
same idea as filth on a wall. The 65 meme-gated icons mean the emblem already
says something about the memes: an Archist ideo's sigil is a lance or spike,
a Rancher's is an animal, a Theist's is a downburst.

### 3.2 Tier C — one glyph per meme, chosen by affinity

The vanilla Ideology meme roster, read from the def database this pass
(structures excluded; DLC additions marked). Each row is a candidate
meme-affinity mark: a glyph any ideo holding that meme may leave. Subjects
are drawn from the meme's own description, symbol packs and precepts, so the
art brief is grounded, not invented.

| Meme (`MemeDef`) | Source line for the subject | Glyph subject (asemic, no text) | Placement bias |
|---|---|---|---|
| `Raider` | "The strong should take from the weak"; packs Raidism/Plunderism/Lootism/Kleptism | an open grabbing hand over a broken box | RaidExit weight ×3; goes over everything |
| `Cannibal` | Morbid style (priority 3); Manporkism/androphagy packs | skull with a fork | RaidExit; `onViewHostileMaker` stronger |
| `PainIsVirtue` | Morbid style; agonist/martyr packs | a thorn ring | Devotional at own settlement |
| `Blindsight` | "Only those who are blind can perceive the true reality"; excludes Darkness | a struck-through eye | Devotional; SettlementGen |
| `Darkness` | (vanilla) | a snuffed lamp | SettlementGen, interiors |
| `Tunneler` | (vanilla) | a mountain with an arrow into it | SettlementGen, mountain sides |
| `Rancher` / `AnimalPersonhood` | icons `AnimalsA-E` gated to these | an animal print | Visitor pastes near pens |
| `NaturePrimacy` / `TreeConnection` | Animalist style; soilist/lifeist packs; noble Neolithic weapons | a leaf-and-root glyph | SettlementGen |
| `HumanPrimacy` | (vanilla) | a standing figure over a beast | Taunt at Animalist ideos' walls |
| `Supremacist` | (vanilla) | a boot / a crown-and-chain | RaidExit; always goes over |
| `Loyalist` | (vanilla) | a banner | Devotional |
| `Collectivist` | (vanilla) | linked rings | Code (crew marks) |
| `Individualist` | (vanilla) | a single dot in a ring | Tag weight ×2 |
| `Proselytizer` | (vanilla) | an open mouth / radiating spiral | Visitor pastes on YOUR walls — the only meme that motivates friendly tagging |
| `Transhumanist` | Techist style (priority 4); `Tile_Transhumanist` designator | a circuit trace | SettlementGen |
| `FleshPurity` | (vanilla) | a crossed-out circuit | Taunt at Techist ideos' walls |
| `HighLife` | (vanilla) | a smoke curl | Jest; Visitor |
| `Nudism` | (vanilla) | a bare figure | Jest |
| `Guilty` | (vanilla) | a chain link | Devotional |
| `MaleSupremacy` / `FemaleSupremacy` | (vanilla) | gender mark, crowned | Devotional; Taunt at the other |
| `Structure_Archist` (structure) | icons `Archist_Lance/Spikes`, `ArchotechA-E` | archotech spike | Devotional |
| `Structure_Animist` (structure) | Animalist style; animism/spiritism packs | spirit-eye | Devotional |
| `Inhuman` (Anomaly) | `factionWhitelist HoraxCult` — never on a generated NPC ideo; concepts "void / entities / rage" (`Defs/Anomaly/MemeDefs/Memes_Misc.xml`) | a void ring | RaidExit by the cult only; never on own walls |
| `Bloodfeeding` (Biotech) | style category row present (`Memes_Bloodfeeding.xml:81`) | a drop with fangs | RaidExit, night |
| `Ritualist` (Anomaly) | Morbid style, priority 3 (`Memes_Misc.xml:80-85`); `PsychicRituals_Exalted` | a knife-and-circle | Devotional |

Twenty-six glyphs is the complete tier; the v1 slice should be the eight
memes most often seen on NPC factions (Raider, Cannibal, Supremacist,
Collectivist, Individualist, Proselytizer, Transhumanist, NaturePrimacy) —
that is the order in the table's placement column. Modded memes (the palette
lists 136 installed) are RUT/RSW territory unless a generic one earns a row.

### 3.3 Deity sigils

`Deity.iconPath` + `Deity.relatedMeme` (`IdeoFoundation_Deity.cs:13-23`) give
a per-god emblem for any ideo whose structure has `deityCount > 0`. Tier-A
rendering with the deity's icon instead of the ideo's is one extra branch:
`form=Sigil, deityIndex=n`. The Devotional category's "one mark per god" is
then an ENGINE feature for every embodied/abstract-theist ideo in the game —
and the Salvation pack's nine hand-drawn marks are its rich override (§4).

### 3.4 What ideoligion keys, beyond appearance

- **Placement**: `requiresAnyMeme` on the pool (Raider gangs tag; Proselytizer
  visitors paste; Supremacists go over).
- **Reaction**: §1.5 keys on ideo identity; vanilla `Ideo` has no
  inter-ideo hostility scalar this pass verified, so `onViewOtherIdeo` is
  flat in v1.
- **Style**: tier B rows let a `Glyph` or `Tag` take the ideo's style dialect
  (a Morbid hazard glyph is bones; a Techist one is a warning diode).
- **Nothing keys on precepts.** Precepts are generated from memes and no XML
  route lists them (`rimworld-ideoligion` §1); a precept-keyed sigil would
  fire unpredictably. Memes, structures, icons, colours and deities are the
  stable handles. `Precept_Relic` and `Precept_Animal` (venerated animal)
  are readable at runtime and are candidate v2 subjects (a relic outline; the
  venerated beast's silhouette), not v1.

---

## 4. The RM / RUT seam

The rule (NAMING_SCHEME_PLAN §1, engine-vs-content): the engine takes the
highest tier it honestly passes; content takes its own. Everything RUT does
must be expressible as XML plus the fields above, so the follow-on is cheap.

| Stays in RM (`mandrake.rm.graffiti`) | RUT fills in (`mandrake.rut.salvation` / `.marks`) | RSW (note only) |
|---|---|---|
| `Filth_Mark`, pools, placers, relation reactions, going-over, scrub semantics, designator, sigil rendering (A), style-row registration for the 11 vanilla categories (B), the meme-affinity fields (C) | the nine god marks as `Sigil`/`Devotional` ThingDefs pointing `godSatiationHook` at Ninefold; they OVERRIDE the deity-sigil fallback for Salvation's deities by pool weight | Aurebesh letterform variants of Tag/ThrowUp (a style row, RSW-tier art) |
| ~14 punk marks (§2.2) + 3 sigil frames + the 8-meme v1 slice of §3.2 | Cant glyph set (Cache Cross, Water-Below, Teeth, Way Home) as `Glyph`/`Code` with `ClanOnly` visibility; the Jawa-xenotype visibility check layered via `JawaRules` | |
| `ClanOnly` = player faction (the generic stand-in already in the worker) | taunt theology rows: ThoughtDefs and Ninefold deltas on the relation table | |
| `RitualOutcomeEffectWorker_PlaceSacredMark` (moved in per the consolidation plan) | the rituals that invoke it (Matrix engine, separate pass) | |
| generic ThoughtDef text ("someone left their mark here") | owner-voice ThoughtDef text for every campaign reaction | |
| Salvation's own `StyleCategoryDef` is NOT here | a Salvation style category with `thingDefStyles` rows for RM's mark defs — Salvation's dialect of every generic mark, pure XML | |

**The seam test**: RUT adds ThingDefs carrying `ModExtension_Graffiti`, adds
`StyleCategoryDef`/`thingDefStyles` rows, adds ThoughtDefs whose
`workerClass` is the RM worker, and adds pool weights — and never a C# class.
If the follow-on needs C#, the engine surface here was drawn wrong; that is
the criterion to review the build against.

---

## 5. V1 slice and cost

- **C#**: `Filth_Mark` (1.1) · form/placer enums + extension fields (1.2,
  1.4) · `GraffitiPool` (1.4) · RaidExit placer (1.4, hook to verify) ·
  designator/workgiver/job (1.4) · relation worker (1.5) · going-over
  override (1.6) · protected-clean (1.7, hook to verify) · sigil draw (1.3-A)
  · validator extensions. Estimate: comparable to GRAFFITI_FRAMEWORK_BUILD_1's
  third pass, one focused FOUNDRY session plus one live proof window.
- **Art**: 14 punk + 3 frames + 8 meme glyphs = **25 assets** via the
  in-flight pipeline; tier B rows for two defs × 11 categories = 22 more if
  the owner takes B in v1 (fork F2).
- **XML**: ~40 ThingDefs, ~10 ThoughtDefs, pool tables, style rows behind
  `MayRequire="Ludeon.RimWorld.Ideology"`.
- **Deferred to v2 by this design**: settlement `GenStep` (F9), Visitor
  placer, deity sigils beyond tier A, relic/venerated-animal subjects, murals
  with quality (pending F1), faction memory of insults, cant on the world map.

---

## 6. Verification the build must design (per BUILD-owns-verification)

Offline: extended startup validator (every mark names ≥1 placer; every
`requiresAnyMeme` resolves; every sigil-form mark has a frame texture); the
naming lint (zero RSW/RUT references); `validate_patch.py` both roots; **cold
load on Core + Harmony only, zero errors** (the soft-Ideology law).
Live, on the 5-mod `graffiti` tier: force the spree → pool picks by skill;
force a raid and let it exit → a tag with the raid faction's colour and ideo
adjective on an exterior wall (`jawa/list_things`, then inspect the
`Filth_Mark` fields); a colonist near a hostile tag gains
`onViewHostileMaker`; a second raid from a different faction goes over the
first; the home-area cleaner leaves the player's own sigil alone and scrubs
the hostile tag only when designated.

---

## 7. Forks for the owner — named, not picked

- **F1 — Murals' thingClass.** `Filth` cannot carry `CompQuality`/`CompArt`.
  Options: (a) murals become a `Building`-class wall attachment with
  `CompArt` like sculpture (quality, tale subjects, real art) while every
  other form stays Filth; (b) drop quality from murals and keep one class;
  (c) defer murals entirely. Recommendation: (a), v2.
- **F2 — Sigil tier for v1.** A alone (zero per-ideo art, every ideo covered
  day one) · A + C (the eight-meme glyph slice) · A + B (two styled defs × 11
  categories) · all three. Recommendation: A + C.
- **F3 — Raid tagging: when.** On the way OUT only (flee/exit — the losers'
  mark, cheap to hook) · on the way IN (a lull toil while assaulting — riskier
  AI change) · both. And: do friendly visitors/traders tag at all in v1?
  Recommendation: out only; visitors v2.
- **F4 — Going-over in v1.** It is one override, but it changes what
  vanilla `ThickenFilth` means for every mark. Ship v1 or hold.
- **F5 — Text.** Asemic letterforms only (recommended) · real English slogans
  in art (localisation debt; RSW Aurebesh reserved) · slogans in inspect text
  only.
- **F6 — Player verb.** Full designator + bill (choose mark, choose wall) ·
  quick-paint job from a gizmo · none in v1 (marks only from sprees, raids,
  rituals). Recommendation: designator, it is the "wide functionality" the
  player touches.
- **F7 — Scrub default.** Protect own-faction and Devotional marks from
  auto-clean (recommended) · protect all marks · protect nothing (vanilla
  filth behaviour; the mod cleans itself away).
- **F8 — Category names.** Rename `Sacred → Devotional`, `Cant → Code` in the
  RM enum now (cheap, pre-freeze; the enum is serialised by name in
  `ModExtension` XML only) · keep the graffiti_spec.md names.
- **F9 — Settlement GenStep.** v1 (settlement maps arrive tagged — the
  strongest "urban settlement" read, but it touches every settlement map
  generation and needs its own live proof) · v2.
- **F10 — The six in-flight glyphs' role.** Confirm they are the `Glyph`/`Code`
  form's default members with `hazard` carrying the engine's example
  `breachLure`, or keep them flavour-only with no mechanics attached.
