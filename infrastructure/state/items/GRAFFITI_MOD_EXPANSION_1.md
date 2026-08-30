
## Scope notes (BENCH, filing sitting 2026-08-30)
- We are SUBSCRIBED to a graffiti mod (Steam) — first step is identify it in
  `ModsConfig.xml`/Workshop folders, read its defs/C#, and assess what it can
  already express before writing anything.
- Expansion directions, owner's words: **sacred** graffiti (natural per-god
  iconography — nine gods, nine mark-styles; ties to the Salvation matrix in
  `design/Jawa/divine_satiation_engine.md`), **socially infuriating** graffiti,
  **amusing** graffiti, **beautiful** graffiti (art/beauty stat).
- Assessment deliverable: what the mod's framework supports (custom art sets?
  mood/social hooks? faction reactions?) vs. what needs a companion patch/DLL.

## Assessment (2026-08-30, offline — sitting for owner/BENCH decision, nothing closed)

### The mod, identified
**Graffiti Mod (Continued)** by Tarte/emipa606, packageId `Mlie.GraffitiMod`,
Steam Workshop id `2986996933` — active in `ModsConfig.xml`
(`<li>mlie.graffitimod</li>`), on disk at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2986996933`.
About.xml, verbatim: *"All graffiti currently is ugly. Beautiful wall art is
not part of this mod, right now."* — the owner's "beautiful" direction is
literally the mod author's own stated wishlist item, never built.

### The framework — read from its 1.6 Defs and its DLL (strings-checked)
The whole mod is **one hardcoded def, one stat block, one texture pool,
zero style/category concept**:
- `GraffitiMod_Paint` (`ThingDefs/GraffitiThing.xml`) is the ONLY concrete
  graffiti ThingDef. `Graphic_Random` over 6 numbered 640x640 PNGs
  (`Textures/Things/Filth/Art/GraffitiMod_Paint/graffiti_0..5.png` — each a
  scattered collage of several small spray-tag doodles across the full
  canvas, not one centered icon). `statBases`: `Beauty -15`,
  `Cleanliness -5` — flat, uniform, always ugly, no per-instance variation.
- The spawn loop (`GraffitiMod_PaintGraffitiJoy` JoyGiver ->
  `GraffitiMod_PaintGraffitiJob` JobDriver, fired when an unhappy artistic
  pawn seeks Meditative joy, or via the `GraffitiMod_GraffitiPaintingSpreeBreak`
  mental break) is C# in `GraffitiMod.dll`. **`strings` on the DLL confirms
  `GraffitiMod_Paint` is a literal string constant** — the JobDriver calls
  `DefDatabase<ThingDef>.GetNamed("GraffitiMod_Paint")` (or equivalent),
  hardcoded, not read from any field. There is no XML hook, setting, or
  patchable list that lets a plain XML patch redirect the spawn to a
  different ThingDef, let alone choose among several by mood/ideoligion/god.
- The only social/mood hook is `GraffitiMod_HappyArtist` — a flat **+2 mood
  for the PAINTER only**, 1 day, no viewer effect, no faction reaction, no
  memory of which pawn/wall/mark. No infrastructure for "colonists react to
  seeing this," no message-to-faction hook, nothing tying a mark to who made
  it beyond a flavour `TaleDef`.
- No "sacred," no "style," no "category" field anywhere. Filth-cleaning,
  wall-linking (`CornerFiller`) and the mental-break trigger are the entire
  feature set.

### Per direction: what plain XML can do vs. what needs new C#
| Direction | Plain-XML-only? | Why |
|---|---|---|
| **Beautiful** (positive Beauty) | ✅ Yes, as a NEW def | `statBases.Beauty` is an ordinary field; a new ThingDef can set it positive. Cannot be retrofitted onto `GraffitiMod_Paint` itself (its own stat block is fixed by the shipping mod) or made to appear via the mod's own spontaneous spree (hardcoded defName, above). |
| **Sacred** (nine per-god marks) | ✅ Yes, as NEW defs | Same as Beautiful — new `ParentName="BaseGraffiti"` ThingDefs, one texture + stat block each. **Placement is the open piece** (see below). |
| **Socially infuriating** | ❌ Needs new C# | No viewer-reaction, no faction-anger, no "who gets offended" hook exists at all in this mod. Vanilla RimWorld has `ThoughtDef` mood hooks that could theoretically fire off *any* filth thing's presence via a `ThoughtWorker`, and a faction goodwill hit would need a Harmony patch or a quest/incident tied to the mark being seen by a visitor — nothing GraffitiMod ships gets us there. |
| **Amusing** | ⚠️ Partial | A flavour-only "found this funny" `ThoughtDef` on a NEW joke-mark ThingDef is plain XML (same recipe as Beautiful/Sacred). But making it context-sensitive (funnier to some pawns/factions, a joke ABOUT something in the colony) needs C# same as infuriating. |

**The load-bearing finding: nothing "expands the mod's spawn loop" with XML
alone**, because the loop is closed around one hardcoded defName. Every
direction that plain XML CAN reach does so by shipping **new, standalone
ThingDefs that reuse the mod's `BaseGraffiti` abstract fields** (filth
placement/cleaning, `canPlaceOverWall`, zero flammability) — not by making
`GraffitiMod_Paint` itself smarter. Getting any of these new defs to actually
**appear on a wall** (spontaneously, tied to a ritual, tied to mood/ideoligion,
tied to "which god is fronting" per the Matrix) needs one of: a Harmony patch
on `JoyGiver_PaintGraffiti`/`JobDriver_PaintGraffiti` to choose among several
ThingDefs by context, a new `RitualOutcomeComp`/`RitualOutcomeEffect` that
spawns a specific mark on a rite (fits the Council-of-Voices boon language in
`divine_satiation_engine.md` §5c beautifully — a rite could LEAVE a physical
mark), or a bridge/authoring script for hand-placed content. None of that is
built here; it is the scoped follow-up below.

### Shipped: sacred graffiti, concrete example of the pattern
New mod `src/RimMandrake/SacredGraffiti/` (packageId `mandrake.sacredgraffiti`,
`loadAfter`/`modDependencies` on `Mlie.GraffitiMod`):
- `RimMandrake_SacredMark_Ishko` — **built, arted, validated.**
  `ParentName="BaseGraffiti"`, own texture
  (`Textures/Things/Filth/SacredMark/SacredMark_Ishko.png`, 640x640, real
  alpha, generated+chroma-keyed+conformed via the `generating-rimworld-sprites`
  pipeline), own `statBases` (`Beauty +6`, `Cleanliness -2` — positive, unlike
  every stock GraffitiMod filth). Iconography is Ishko the Unmaskable's own
  canon "Form" line in `divine_satiation_engine.md`'s pantheon section: *"a
  pair of glowing orange eyes in the dark."* Description text quotes his
  no-punished-skip trait. `validate_patch.py --live` (2026-08-30T18-37-19Z
  capture, 585-mod set) — **0 errors, 0 warnings**, `ParentName` resolved
  cross-mod, texPath confirmed on disk.
- This one def doubles as the concrete example for **both** Sacred and
  Beautiful (positive-Beauty statBases is the whole ask for "beautiful," and
  this is the first def in the project to use it on a graffiti-style filth).

### Designed, not yet arted — the other eight gods
Same recipe (`ParentName="BaseGraffiti"` + new texPath + new statBases), each
god's iconography anchor taken verbatim from its canon "Form:" line
(`divine_satiation_engine.md` pantheon section — do not invent new imagery):

| God | Form (canon) | Beauty sign (proposed) |
|---|---|---|
| ② Ohm | current in a wire; the spark that wakes a dead engine | positive |
| ③ Oomo | a single trembling droplet that never falls; the mirage-pool that recedes | positive |
| ④ Mob'Unloo | two unblinking eyes above an endless tally | neutral/positive |
| ⑤ Rekko | a scarred hand rising from a scrap-heap | positive |
| ⑥ Ta'Baa | the receding dune-line; the engine-glow climbing away | positive |
| ⑦ Zizzik | a rattle you can never locate; the errant spark in dry sand | negative (unsettling, still sacred) |
| ⑧ Sh'kaar | white glare and heat-shimmer | negative (dread, not vandalism) |
| ⑨ Ozzik | a tarnished crown half-buried in sand; a monument no one remembers building | negative (grief, not ugly) |

Worth ruling explicitly: **"sacred" and "beautiful" (Beauty-stat-positive) are
orthogonal**, not synonyms — Zizzik/Sh'kaar/Ozzik's marks should plausibly
read as unsettling-but-devotional (matches their canon temperament), which the
Beauty field alone cannot express (there's no "reverent-but-ugly" tag; that
nuance lives only in description text and Beauty sign, both of which this
pass demonstrates work).

### Deferred — needs a real decision, not built here
1. **Placement/trigger mechanism** for any of the nine marks (or the
   infuriating/amusing directions) — Harmony patch on GraffitiMod's
   JoyGiver/JobDriver vs. a RitualOutcomeEffect tied to the Matrix's per-god
   boon columns vs. hand-authored/bridge placement. This is a real scope
   decision (new C# assembly, or reuse `JawaRules`/`bridgetools`?) that should
   sit with the owner/BENCH before building — it decides whether sacred marks
   are a spontaneous colonist behavior, a ritual reward, or a hand-placed
   worldbuilding detail, and those have very different authoring costs.
2. **Socially infuriating graffiti** — genuinely needs new C# (viewer-reaction
   ThoughtWorker and/or faction-goodwill hook). Not designed beyond the table
   above.
3. **Amusing graffiti** — the flavour-only half (new ThingDef + joke
   ThoughtDef) is plain XML, same recipe as sacred; the context-sensitive half
   needs the same C# as infuriating. Not built.
4. **The other 8 sacred marks' art** — same generation pipeline that produced
   Ishko's (see `src/RimMandrake/SacredGraffiti/art_bench/`), one Codex call
   + validate pass each. Cheap, incremental, no design risk — the blocker is
   only that this pass shipped one as proof-of-pattern rather than all nine.

## Placement mechanism (2026-08-30, second pass — owner's ruling)

**Ruling:** a sacred mark is placed as a `RitualOutcomeEffect` off the
Salvation Matrix's per-god boons — i.e. completing a ritual for a given god
places that god's mark, as a reward/consequence, tied to the religion
mechanics already built — not a Harmony patch on GraffitiMod's own spawn
loop, not hand-placement.

**What "the religion mechanics already built" turned out to mean, read from
`design/Jawa/divine_satiation_engine.md` in full:** the Salvation Matrix's
nine per-god pages (BOONS/DEMANDS/TABOOS/CURSES, all nine "SHIPPED
2026-08-30") are **design prose only**. The doc says so itself, in terms:
*"The engine build (satiation counters, front selection, light zones, emitter
progression, judgement, boon/demand/taboo/curse invocation) sizes from these
pages; it files when the owner calls the build."* Confirmed by search: zero
`RitualOutcomeEffectDef`/`RitualOutcomeComp` in `src/` before this pass, and
zero `RitualDef`/`PreceptDef` XML anywhere in the mod tree — only a
`Salvation` ideoligion `.rid` (memes/precepts, no custom rituals). **So there
is no real ritual def to hook a mark-placement effect onto yet** — building
one would mean inventing a fake ritual, which the task explicitly ruled out.

**What plain vanilla already offers, read from RimWorld 1.6 source via
RimSage:** `RitualOutcomeEffectDef` (`Source/RimWorld/RitualOutcomeEffectDef.cs`)
already carries `filthDefToSpawn`/`filthCountToSpawn` fields — used today by
`RitualOutcomeEffectWorker_RemoveConsumableBuilding` to spawn `Filth_Ash` when
a Pyre/Christmas-tree ritual consumes its building
(`Defs/Ideology/Rituals/Ritual_Outcomes.xml`, `DestroyConsumableBuilding_Pyre`).
That worker only fires at a *consumed* building's occupied rect and always
destroys the target — the wrong shape for a mark that should appear at an
ordinary ritual site and destroy nothing.

**Built:** `RitualOutcomeEffectWorker_PlaceSacredMark`
(`src/RimMandrake/SacredGraffiti/Source/SacredGraffiti.cs`, assembly
`SacredGraffiti.dll`, no Harmony — `RitualOutcomeEffectDef.workerClass` is a
plain `Activator.CreateInstance` extension point, not a patch target) — a
generic, **god-agnostic** `RitualOutcomeEffectWorker_FromQuality` subclass.
It overrides `ApplyExtraOutcome` (vanilla's own extension point, called with
the already-rolled outcome, so all of `Apply`'s letter/memory/development-
point bookkeeping is untouched) and, on a **positive** outcome only, spawns
`def.filthDefToSpawn` at the ritual's `selectedTarget` cell via
`FilthMaker.TryMakeFilth` (falling back to a present participant's position
if the target carried no cell). A curse never leaves a mark. §19.5-clean: no
material reward, only the devotional wall-mark, whose own `statBases` already
carry its Beauty sign.

Reusable by construction: any future `RitualOutcomeEffectDef` points its
`workerClass` at this type and its `filthDefToSpawn` at a god's mark ThingDef
— no new C# per god. `src/RimMandrake/SacredGraffiti/Defs/RitualOutcomeEffects.xml`
ships one demonstration instance,
`RimMandrake_Ishko_RitualOutcome_PlaceSacredMark` (`filthDefToSpawn`
`RimMandrake_SacredMark_Ishko`), showing the parameterization. **It is not
referenced by any `RitualDef`/`PreceptDef`, because none exist** — same
inert-but-valid status as the ThingDef marks themselves, ready the instant a
real Matrix ritual's `outcomeEffect` names it. That wiring is the "engine
build" the design doc itself says is a separate, owner-called pass — not
invented here.

Built clean: `dotnet build … -c Release` → `SacredGraffiti.dll`, 0
warnings/0 errors.
`skills/rimworld-modding/scripts/validate_patch.py src/RimMandrake/SacredGraffiti
--live <2026-08-30T18-37-19Z capture> --defs <RimWorld install> --defs
<Workshop content> --defs <Mods>` → **0 errors, 0 warnings**, `ParentName`
`BaseGraffiti` now resolves cross-mod (Mlie.GraffitiMod present in the same
capture).

**Still open — genuinely not this pass:**
- **Live proof** that a spawned `RitualOutcomeEffectDef` actually places
  filth in a running game — needs the bridge/a real ritual to invoke it,
  which does not exist (see above). Offline: built, wired to vanilla fields
  correctly per source, validated 0/0. That is as real as it gets without a
  live ritual to fire it.
- **Wiring this mechanism to Ishko's actual Matrix page** (or any god's) —
  blocked on the Matrix engine build itself, which the design doc says is a
  separate, owner-called pass, not a graffiti-item task.
- The other eight gods' marks' art (unchanged from the prior pass — cheap,
  mechanical, no design risk).
- Socially infuriating / amusing directions (unchanged — needs new C#
  the owner hasn't asked for yet).

## verify (draft)
- [x] Mod identified (`Mlie.GraffitiMod` / Graffiti Mod (Continued), workshop 2986996933).
- [x] Its Defs + DLL strings read; framework capability table above.
- [x] One sacred-graffiti ThingDef shipped with real art, validated 0/0 against the live 585-mod dump.
- [x] Owner rules the placement-mechanism question: `RitualOutcomeEffect` off
      Matrix boons. Generic `RitualOutcomeEffectWorker_PlaceSacredMark` built,
      validated 0/0 — see "Placement mechanism" above. Not live-fired (no real
      ritual def exists to fire it; that's the Matrix engine build, ruled
      out-of-scope for this item).
- [ ] Remaining eight gods' marks arted (mechanical, once art time is spent — not a design blocker).
- [ ] Socially infuriating / amusing directions designed past the capability table, if the owner wants them built.
- [ ] Matrix engine build (separate, owner-called pass per the design doc) wires a real ritual's `outcomeEffect` to this mechanism.
