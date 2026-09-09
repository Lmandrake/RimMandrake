# GRAFFITI_PUNK_IDEOLIGION_SCOPE_1

Owner, verbatim (2026-09-09): *"we want the base Graffiti mod to have a wide
variety of functionality within it, not just the base examples we've provided
in vanilla. It should be a mod more aligned to punk style graffiti such as is
seen in urban settlements, as well as ideoligion-inspired sigils taken from the
Rimworld ideoligions as they exist in the game. Then we will go rich and fill in
the Utinni modpack for it."*

**The design is `design/RM_GRAFFITI_SCOPE_WIDENING.md`** (Fable, 2026-09-09,
15118a6c; stale premise corrected in the same commit as this file). This file
is the item's spec/verify/criteria and the questions only the owner can rule.
It does not restate the design; where the two disagree, the design doc is
wrong and this file says so.

## spec

Widen `mandrake.rm.graffiti` (RM tier, generic to any RimWorld game) from
"engine + four example marks" into a graffiti SYSTEM, in two registers, on
top of the engine that already ships (`src/RimMandrake/Graffiti/`:
`RM_BaseGraffiti`, `ModExtension_Graffiti`, the absorbed spree, the viewer
`ThoughtWorker`, the `BreachBiasHook`) and alongside — not replacing — the
five families ruled in `design/Jawa/graffiti_spec.md` §1.

**Engine surface it adds** (design §1; the seven mechanisms, in dependency order):
1. `Filth_Mark` — a `Filth` subclass carrying provenance (maker pawn, maker
   faction, maker ideo, subject, placed tick, placer). Everything below reads
   it. Today `tracksMaker`/`hasSubject` are declared on the extension with no
   storage behind them.
2. A FORM axis (`Scrawl · Tag · ThrowUp · Stencil · Paste · Sigil · Glyph ·
   Piece`) beside the existing FUNCTION axis (`GraffitiCategory`). The
   punk register IS the form axis; the five families stay the function axis.
3. Ideo-driven sigils, three cost tiers: **A** the ideo's own `IdeoIconDef`
   texture tinted by its colour inside a sprayed frame (zero per-ideo art,
   every generated ideo covered day one); **B** `StyleCategoryDef.thingDefStyles`
   rows for RM's mark defs across the 11 vanilla style categories (MEASURED
   from the 2026-09-08 dump: Animalist Buddhist Christian Hindu Islamic
   Morbid Rustic Spikecore Techist Totemic + Anomaly's Horaxian); **C** one
   meme-affinity glyph per vanilla meme, offered only to ideos holding it.
4. A data-driven pool selector replacing the hard `RM_Graffiti_Vandal`
   reference in `JobDriver_PaintGraffiti`, plus new placers: designator +
   bill (the player verb), raid-exit tagging (raiders leave their faction's
   tag on your exterior wall), settlement GenStep (v2 by the design's own
   recommendation), visitor pastes (v2).
5. Relation-keyed viewer reactions (same ideo / other ideo / own faction /
   hostile maker / subject) in place of one ThoughtDef per mark.
6. Going-over (a rival's mark replaces, never thickens) and per-form decay.
7. Scrub semantics: own-faction and Devotional marks protected from
   home-area auto-clean, a scrub designator overrides.

**The vanilla vocabulary the sigil register keys on** — memes, structures,
`IdeoIconDef`, `IdeoColorDef`, deities, style categories — never a fixed list
of religions (vanilla ideos are generated; there is no `IdeoDef`) and never
precepts (no XML route lists them). The meme roster the C tier covers is the
27 non-structure `ludeon.*` memes MEASURED from the 2026-09-08 dump (24
Ideology + Biotech `Bloodfeeding` + Anomaly `Inhuman`/`Ritualist` + Odyssey
`Shipborn`, whitelisted to `TradersGuild` — a visitor-placer meme the design
doc's table originally missed; added). Modded memes are not RM's problem.

**The RM / RUT line** (design §4, restated as the criterion the build is
reviewed against): RM owns every C# class, the pools, the placers, the
relation table, sigil rendering, the style-row registration for the 11
vanilla categories, the meme-affinity fields, and generic content (the punk
set, three sigil frames, the eight-meme v1 glyph slice, generic ThoughtDef
text). RUT (`mandrake.rut.salvation` / `.marks`, per R7/R8 in
`MOD_NAMING_CONSOLIDATION_AUDIT_1`) owns the nine god marks (as
`Sigil`/`Devotional` ThingDefs pointing `godSatiationHook` at Ninefold,
overriding the deity-sigil fallback by pool weight), the Cant glyph set with
`ClanOnly` visibility, the taunt theology rows, owner-voice reaction text,
and a Salvation `StyleCategoryDef` giving every generic mark a Salvation
dialect. **Seam test: RUT adds XML only — ThingDefs, style rows, ThoughtDefs
on the RM worker, pool weights. If the follow-on needs a C# class, the RM
surface was drawn wrong.** Nothing already rich in RUT is copied down.

**Corrections to the design doc, made this pass** (it was written while
`GRAFFITI_GENERIC_MARKS_1` was mid-flight):
- `GRAFFITI_GENERIC_MARKS_1` is **done** (b9ac45cb). It shipped THREE marks,
  `RM_Graffiti_Scratches` / `RM_Graffiti_TallyMarks` / `RM_Graffiti_WarningGlyph`,
  not the six `RM_Mark_arrow/handprint/hazard/spiral/sun/tally` PNGs in
  `Transient/art_review_generic_marks/final/` (those are review candidates,
  Transient, never defs). The `Glyph` form's default members are the three
  shipped defs; the remaining candidates are an owner-review question, not
  a fact.
- **defName stem is `RM_Graffiti_*`**, matching the four shipped defs and
  NAMING_SCHEME_PLAN §2 (one stem per mod; `RM_Mark_*` was the doc's
  invention and is dropped).
- The dump **does not capture `IdeoIconDef` or `IdeoColorDef`** (UNMEASURED,
  527 types declared, neither present) — so the offline sigil-coverage check
  must read the vanilla XML on disk, never the dump (see verify).
- `Thing.StyleDef` confirmed a virtual property (`Verse/Thing.cs:127`);
  `Ideo.GetStyleFor` (`RimWorld/Ideo.cs:1562`) and the
  `FilthMaker.TryMakeFilth(..., out Filth outFilth, ...)` overload
  (`FilthMaker.cs:65`) confirmed via RimSage this pass — the tier-A mechanism
  stands on real vanilla surface.

**Out of scope, deliberately**: murals with quality (needs a non-Filth
thingClass — fork F1, v2), any campaign vocabulary, any modded meme, English
lettering in art (F5), settlement GenStep and visitor placers in v1.

## verify

Offline, no live game, in this order — each names its instrument:

1. **Naming lint**: `python3 src/RimMandrake/Utils/naming_lint.py` on
   `src/RimMandrake/Graffiti/` — zero `RUT_`/`RSW_`/campaign-word hits; every
   new defName starts `RM_Graffiti_`.
2. **Def validity**: `validate_patch.py src/RimMandrake/Graffiti --live <fresh
   capture> --defs <RimWorld install> --defs <Workshop> --defs <Mods>` — 0/0.
   Every `StyleCategoryDef` patch and `requiresAnyMeme` list sits behind
   `MayRequire="Ludeon.RimWorld.Ideology"` (or Biotech/Anomaly/Odyssey for
   their memes).
3. **Sigil coverage vs vanilla data, read from disk not the dump**: a script
   under `src/RimMandrake/Graffiti/` (committed, not Transient) parses
   `Data/Ideology/Defs/IdeoSymbolDefs/IdeoIconDefs_{Universal,Specific}.xml`
   and `IdeoColorDefs.xml` from the install, and asserts (a) every `iconPath`
   resolves to a texture the frame can draw, (b) every `<memes>` gate names a
   `MemeDef` the dump holds (`measure get <meme>`), (c) the tier-C table
   covers every non-structure `ludeon.*` `MemeDef` the dump lists
   (`measure sql` over `def_type='MemeDef' AND package_id LIKE 'ludeon.%'`) or
   names its exclusion. **Zero rows is a failure**, not a footnote.
4. **Style rows**: for each styled mark def, exactly 11 `thingDefStyles`
   rows, one per vanilla `StyleCategoryDef` (`measure count StyleCategoryDef`
   filtered to `ludeon.*` = 11), each `styleDef` texPath on disk.
5. **Startup validator extended** (already in `ModExtension_Graffiti.cs`):
   every mark names ≥1 placer; every `requiresAnyMeme` resolves; every
   `Sigil`-form mark has a frame texture; unreachable relation ThoughtDefs
   named. Its warnings are read from `Player.log` on the next load, not
   assumed absent.
6. **Soft-Ideology law**: a cold load on the `graffiti` modset tier minus
   Ideology (`modset_builder.py`) shows zero config/crossref errors — the
   sigil form simply absent from every pool.

Live proof is the build's to design (BUILD-owns-verification) and rides the
5-mod `graffiti` tier: spree picks by skill; a raid exits and leaves a tag in
its faction colour with the ideo adjective in the inspect line
(`jawa/list_things`, then read the `Filth_Mark` fields); a colonist near it
gains `onViewHostileMaker`; a second faction goes over the first; the cleaner
leaves the player's own sigil alone.

## criteria

Done means, in order:
1. The owner has ruled the forks below (or said "recommendations stand"),
   and this file records the rulings by card — until then the item is a
   design draft and no build item is filed from it.
2. A build item (`GRAFFITI_SCOPE_BUILD_1`-shaped, FOUNDRY) exists carrying
   the ruled v1 slice with the RM/RUT seam test as its review criterion.
3. `mandrake.rm.graffiti` ships the ruled v1 slice: `Filth_Mark`, form axis,
   pool + designator + raid-exit placers, relation reactions, tier-A sigils
   (+ C if ruled), scrub semantics; ~12 new punk assets + 3 frames (+ 8
   meme glyphs if C) through `generating-rimworld-sprites`, owner-reviewed on
   a contact sheet; verify steps 1–6 green and cited in the closing commit.
4. The seam holds: a stub RUT patch (one ThingDef with `godSatiationHook`,
   one style row, one ThoughtDef on the RM worker) loads and behaves with
   zero RUT C#.
5. `design/Jawa/graffiti_spec.md` §2/§5 and this design doc are reconciled
   in one edit — wrong lines deleted, not banner-superseded.

## Open questions for the owner

Forks F1–F10 in `design/RM_GRAFFITI_SCOPE_WIDENING.md` §7 stand as written
(recommendations: murals as a `CompArt` building in v2 · sigil tiers A+C ·
raid tagging on exit only · going-over in v1 · asemic letterforms · full
designator · protect own+Devotional from auto-clean · rename `Sacred→Devotional`,
`Cant→Code` · GenStep v2 · the shipped glyphs get mechanics). The ones a
design pass genuinely cannot pick, plus what this pass added:

1. **Art register reference.** "Punk style graffiti as seen in urban
   settlements" spans NYC subway wildstyle, UK stencil (Banksy-adjacent),
   Berlin wall paste-ups, Latin American muralismo. Which one or two are the
   reference sheet? The generation prompt and the sigil frames follow it and
   nothing else. A reference image or two from him beats any description.
2. **Tone boundary on meme glyphs.** The tier-C table includes `Cannibal`
   (skull-and-fork), `MaleSupremacy`/`FemaleSupremacy` (crowned gender
   marks), `Nudism` (bare figure), `Inhuman` (void ring), `PainIsVirtue`
   (thorn ring). Does any meme get NO glyph on taste grounds, or do all
   vanilla memes get a mark because the game already ships them as playable
   choices?
3. **The mappings this pass is least sure of**: `Loyalist`→banner,
   `Guilty`→chain link, `Collectivist`→linked rings, `Individualist`→dot in a
   ring, `Shipborn` (Odyssey, TradersGuild-only)→? (a hull-and-star was the
   only candidate). These are placeholders; the ones he has an image for
   should override.
4. **Which of the six review-candidate glyph PNGs (if any) become defs
   beyond the three shipped** — a review-sheet question he was already
   owed by GRAFFITI_GENERIC_MARKS_1's contact sheet
   (`D:\Luke\dev\Rimworld\Transient\graffiti_generic_marks_contact_sheet_2026-09-09.png`).
5. **Anti-authority stencils and the campaign.** `RM_Graffiti_Stencil_Crown`
   (crossed-out crown, hostile to Royalty's Empire) is generic RM content —
   but the campaign's Galactic Empire is reskinned vanilla `Empire`
   (`galactic-empire-is-reskinned-vanilla`), so it will read as anti-Imperial
   on Ash'karr for free. Feature or overreach? If feature, RSW may want an
   Aurebesh/Imperial-cog variant; if overreach, the stencil goes to RUT.
