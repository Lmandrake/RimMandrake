# The Graffiti series: Graffiti, the Star Wars reskin, Sacred Graffiti

Written 2026-11-07 so that the second and third Artisan loops can start cold from this page. Nothing here is built. Every motif and bar below is **proposed** until Mandrake says otherwise; no `## north star` section was touched. Repo paths are relative to `D:\Luke\dev\RimMandrake\` (the read-only mirror); a loop reads them in its own clone. MEASURED means I read it from the file or page today; UNMEASURED means I did not.

An Artisan loop is a series of fresh `claude -p` passes on one prompt, in its own clone and branch, with the owner's words frozen and everything else free to change. Its how-to is `D:\Luke\dev\MandrakeWorkflows\artisan\README.md`, with `POLICIES.md`, `FINDINGS.md` and `template\` beside it. Its status is experimental: two mods tried, none accepted, and never yet tried on work that is less than mostly built. That last caution applies to loop 3.

## Mandrake's words

Mandrake, 2026-11-07:

> "The Star Wars layer should replace the standard graphics with entirely in-world-appropriate versions (see canon and online)... racial motifs, rebel vs. empire, etc. I'm sure there's even a website somewhere for Star Wars Graffiti. The mod sacred graffiti however is the big deal. Utinni scenario should TAKE OVER this mod and make it shine. Jawa graffiti will NOT look terran. Strange Star Wars esque symbols. Writing in Aurebesh. Droids. Jawa figures. The Nine Gods. That last part is very important. There should be the symbols of the Nine Gods, depictions of the Nine Gods, etc. But we aren't building that quite yet... I'm telling you all this so you can document it properly so those loops can come next. They're the logical follow-on to Graffiti, to continue it all the way down through the three. It's a logical series."

## The series and its order

The three tiers each repaint the one below. RimMandrake is graffiti for any RimWorld game. RimStarWars makes it the galaxy's graffiti. RimUtinni makes it the Jawas' own, and gives it gods.

| Loop | Item | Tier | Starts when |
|---|---|---|---|
| 1. Graffiti | `GRAFFITI_FINISH_RALPH_LOOP_PLAYS_FIRST` | RimMandrake, `src/RimMandrake/Graffiti` | Running now |
| 2. Star Wars reskin | `GRAFFITI_STARWARS_RESKIN_NOT_ONE_TERRAN_TAG` | RimStarWars | Loop 1 accepted and landed |
| 3. Sacred Graffiti, the Nine Gods | `SACRED_GRAFFITI_FINISH_NINE_GODS_WAIT_TURN` | RimUtinni | Loop 2 accepted and landed |

### What loop 1 is right now

Its newest code is branch `ralph/graffiti` in clone `/home/mandrake/rm/scratch/BENCH/ralph_graffiti`, with its prompt at `ralph/PROMPT.md` there. Its current brief is option D for wall paint (bolder paint in the wall face, marks climbing onto the wall top) and the social side. MEASURED on commit cdf0b7c43a, 2026-11-07: 54 ThingDefs and 96 PNGs (up from 49 designs and 80 PNGs before that commit, so "49" below means the set that existed when this page was written; count again at the start), and 42 ThoughtDefs.

The social side was first written in that commit, offline and not yet seen in the game: `GraffitiSocial.cs` (598 lines, MEASURED), `JobDrivers_AnswerMark.cs`, thoughts such as `RM_Graffiti_Humiliated` and `RM_Graffiti_PaintedMe`, jobs `RM_ScrubMark`, `RM_DefaceMark`, `RM_ConfrontPainter`, and history events `RM_Graffiti_WallInsult`, `RM_Graffiti_SharedSign`. No field or name in that code is settled, which is why nothing below may be started against it.

### What the next two inherit

- **The wall.** The geometry (`WallPlane`, the `wallgeom.py` and `wallsim.py` twin) and how paint sits on a surface. Art in the later tiers gets all this for nothing, if it is drawn the way the framework wants.
- **The art pipeline.** `art_source/manifest.py`, `bake.py`, `patch_defs.py`, `gallery_sim.py`: a pale drawing plus a pigment for `pigmented` marks, sizes written into the defs.
- **The pool.** `GraffitiPool` finds every ThingDef with a `ModExtension_Graffiti`, weighted, gated by meme, skill and hostility. Its own comment says a content pack only has to add ThingDefs.
- **The people.** Who paints what, who is angered, amused or moved, and what they do about it: the grudges, the answers (scrub, deface, confront, paint back), the goodwill, the enemy-claim thought, the log entries. A mark's `meaning` drives this, so a reskinned mark keeps its social life without further work.
- **The harness.** The `graffiti_solo` mod list, `stage_colony.py`, the shots-and-verdicts routine, the turn gate at the game.

### What they must wait for

Do not start either loop until Mandrake has looked at loop 1 and accepted it, and its branch is on main. Four things would otherwise be built on sand:

1. **How a mark is drawn.** If the bolder paint or climb changes what a good source drawing is, 49 marks drawn before that are wasted.
2. **The source art format.** Size, canvas, pale-plus-pigment. Loop 1 has been told to redo art wherever it cannot meet his demands, so the format may change.
3. **The extension's fields.** `meaning` and the social hooks are moving now. Patches and new marks name those fields.
4. **The file list.** The two hard-coded texture paths below may move.

## Loop 2: the Star Wars reskin

### What it is for

On a Star Wars mod list, nobody should see a wall that could be on Earth. Today the layer adds one stencil and leaves 49 Earth-graffiti designs in place. The Graffiti scope doc even names the register those designs are in: NYC wildstyle plus UK stencil (`design/RM_GRAFFITI_SCOPE_WIDENING.md`, line 1). That is right for RimMandrake and wrong for the galaxy. After this loop, all 49 marks are the galaxy's own in the same slots, painted by the same people for the same reasons, and rebel, Imperial and species hands can be told apart.

### What exists

`src/RimStarWars/GraffitiImperial`: packageId `mandrake.rsw.graffitiimperial`, one ThingDef `RSW_Graffiti_Stencil_ImperialCog` (a struck Imperial cog with an "asemic Aurebesh-styled" tag), no C#, no settings. Its walk is `design/validation_walks/RimStarWars/GraffitiImperial.md`, a draft with no bars. Its static check fails if a `Source` folder appears.

### How replacement really works

I read this in the decompiled game (`D:\ClaudeWork\rimmandrake\decomp\rw16\all`, `Verse/ContentFinder.cs`, `Verse/Graphic_Collection.cs`, `Verse/Thing.cs`, `Verse/ThingStyleHelper.cs`) and the Graffiti source on the loop 1 clone. Line numbers in that source will drift.

**A later mod's files in the same folder do not replace; they add.** Marks are `Graphic_Random` over a folder (`Things/Filth/Art/<defName>`). `Graphic_Collection.Init` lists the folder with `ContentFinder.GetAllInFolder`, which walks every running mod and returns all their files. A differently named file joins the rotation beside the RimMandrake art, which is the thing he does not want. A file with the same name appears twice in the list, and both entries load the later mod's picture, because `ContentFinder.Get` searches mods last to first. So same-name works but cannot remove anything or change the variant count.

**ThingStyleDef does not work for marks at all.** `Thing.Graphic` honours a style, but `ThingStyleHelper.GetStyleDef` reads `(thing as ThingWithComps)?.compStyleable`, and `Filth` derives from plain `Thing`, so for a filth the answer is always null. A grep of the Graffiti source finds no style code. So `Salvation_GraffitiScratches` in `src/RimMandrake/SacredGraffiti/Defs/StyleCategoryDefs_Salvation.xml` can never change what a wall shows. See Conflicts.

**The right route is an XML patch that repoints each mark.** The RimStarWars mod loads after `mandrake.rm.graffiti` and, for each of the 49 defs, replaces `graphicData/texPath` with a folder of its own under `RimStarWars/<ModName>/`, plus `drawSize`, `label` and `description`. The whole folder is swapped, RimMandrake's files drop out, the variant count is free, and with the mod off the base game is untouched. It needs no C#. The project has done this before: `src/RimStarWars/StarWarsPatches/Patches/AncientJunk_StarWarsReskin.xml` and `src/RimUtinni/AshkarrLandmarkArt/Patches/LandmarkIcons.xml`.

**Exceptions to check once loop 1 lands:**

- Two paths are hard-coded: `Filth_Mark.cs:435` (`RM_Graffiti_CrossOut/crossout_0` and `_1`, the slash through a mark that gets gone over) and `Designator_PaintGraffitiMark.cs:32` (the toolbar icon `RM_Graffiti_Vandal/vandal_0`). These are where same-name works: ship files at those exact paths.
- A saved mark holds a variant number. Check what it does when the count changes.
- A patch that matches nothing logs nothing, so count the matches: 49 of 49.

**What happens to the meme glyphs (27).** They stay as defs, keep their gates (`requiresAnyMeme`) and their meanings, and get new art through the same patch. A cannibal painter still paints the cannibal's mark, but in a hand of this galaxy. Five of them are placeholder mappings, not real subjects of their own (MEASURED: Loyalist, Guilty, Collectivist, Individualist, Shipborn), and a new drawing is the chance to give them one.

**What happens to the ideoligion sigils.** There are three defs, each a frame and an icon. The frames are textures (`sigilFrameTexPath` on the extension) and get patched like anything else. The icon is not a file: `Filth_Mark` paints `makerIdeo.Icon` at run time, tinted by the ideoligion's colour. It should stay, since it is the point of the mark: a colony's real faith on the wall. It looks in-world if the ideoligion is, and the campaign's six `RUT_IdeoIcon_*` defs already are. The same holds for the faction emblem (`targetFaction.def.FactionIcon`) on marks aimed at a faction. So the bar below covers frames and paint, not the player's own chosen icon.

**Rebel versus Empire and racial motifs need more than repainting.** Replacing art changes what a mark looks like, not who paints it. MEASURED gates today: meme, skill, and hostility to one named FactionDef, as a single string. Race is not consulted. So:

- Add a small general gate on the painter's race or xenotype, and let the faction gate take a list and "friendly to" as well as "hostile to". This belongs in `mandrake.rm.graffiti`, generic and naming nobody. Loop 2 may make this one change there.
- Faction-true marks are then new `RSW_` ThingDefs in the pool. Species marks likewise.
- The Empire is Royalty's `Empire` faction, reskinned: "Our Star Wars empire IS the re-skinned Empire." (owner, 2026-08-28; `canon.yml` `empire.outerrim_faction_excluded`). So the cog's gate on `Empire` is right, and every Imperial mark gates on `Empire`, never `OuterRim_GalacticEmpire`. The reskin itself is in the RimUtinni tier (`src/RimUtinni/UtinniPatches/Patches/GalacticEmpire.xml`), so on a Star Wars list without Utinni the faction is still called what vanilla calls it; the gate works either way. The gate stays open if the lookup misses (`GraffitiPool.cs` about line 174). Rebels are the open case: `OuterRim_RebelAlliance` starts with 0 on the Utinni slate (`src/RimUtinni/UtinniPatches/Patches/FactionSlate/OnlyOurFactions.xml`), so find out who paints a starbird before gating on it.

### What the galaxy's graffiti looks like

All from Wookieepedia, through its API, as the canon brief says (`design/RimStarWars/canon_references/AGENT_BRIEF.md`). I opened each page listed in Sources below.

- **Graffiti is in canon, and small.** It is defined as vandalism, etching messages on others' property. A Twi'lek, Hadaro, misspelled "poodoo" on a wall on Kwenn. The Kintan Striders, a Nikto gang on Tatooine, spray their logo, a stylized Outer Rim Basic "K", on what they raid.
- **Sabine Wren is the canon graffiti artist.** The starbird was her signature, sprayed on Imperial buildings after sabotage. She put a violet one on a TIE wing and set off a paint bomb in stormtroopers' faces ("Art Attack"). She left a graffiti calling card for her crew. The Lothal resistance marked escape routes through town sewers with starbirds, and the Spectres followed them through Jhothal's to a rendezvous. Her style drew on Janyor's protest paintings on Bith.
- **The starbird** is the "Wren Phoenix crest", a bird rising with wings spread and head turned right. Her starbird was later combined with a three-pronged symbol of Saw Gerrera's to make the Rebel Alliance starbird, so the two are different marks. The Alliance_Starbird page (Legends-era content) gives it mostly in bright red or blue; on a wall the colour is the painter's.
- **The Imperial crest** has six spokes, adapted from the Republic's eight, likened to a cogwheel, on everything from uniforms to propaganda.
- **Walls talk in Aurebesh, and it can be read.** Aurebesh has 34 letters and writes Galactic Basic. Lothal's Capital City has murals with real words: "SECTOR 12 SERVICE", "SALE", "REPAIR", and "L9", abstract with a caption. Imperial "JOIN" murals are red, white and black, with or without a stormtrooper. Clones wrote "SOME GUYS HAVE ALL THE LUCK" on a helmet, and Kix's tattoo read "A GOOD DROID IS A DEAD ONE".
- **Outer Rim Basic** is the second alphabet, 26 letters, also called Huttese, used alongside Aurebesh on the Rim. A Tatooine wall should mix them.
- **Mandalorian** art: the mythosaur skull emblem, cubist murals of crusaders killing Jedi, angled and hexagonal lines, diamonds and honeycombs.
- **Political symbols on walls:** a white sun painted on Shmi Skywalker's old home in Mos Espa, the mark of the White Suns, who freed slaves. A canon symbol on a Tatooine wall.
- **Droids have politics.** Anti-droid sentiment and droid rights (L3-37's "droid revolution") are both canon.
- **I found no painted symbol or motif** for Wookiees, Tusken Raiders or Twi'leks on their species pages (MEASURED by word search; absence on a wiki page is weak). The Wroshyr Mural is a memorial to the Empire's dead on Kashyyyk, with no image described. The Shyriiwook language has no word for "artist". The loop must source these rather than invent canon. For body shapes, use the project's canon library, `design/RimStarWars/canon_references/` (`INDEX.md`, `DROIDS_INDEX.md`).

### Does a Star Wars graffiti website exist?

Yes, he was right, though not of the kind this needs. I opened these:

- The Flickr group "The Star Wars Graffiti Pool", https://www.flickr.com/groups/starwarsgraffiti/ (631 photos, 212 members, since 2005, as the page reports).
- Street Art Utopia, 21 photos, 2026-05-04: https://streetartutopia.com/2026/05/04/star-wars-street-art/
- Graffiti Life, a blog post on a commissioned Kylo Ren: https://graffitilife.co.uk/star-wars-graffiti/

These show Earth walls with Star Wars characters on them, which is the reverse of what he asked for: they are terran graffiti about the galaxy, not the galaxy's graffiti. Search results also list Etsy, Pinterest and DeviantArt pages of the same kind, which I did not open.

The real gallery for this job is in-world: Wookieepedia's Category:Murals, 23 entries (MEASURED, https://starwars.fandom.com/wiki/Category:Murals), and its Category:Art. The richest sources are two books that Wookieepedia cites: *Sabine: My Rebel Sketchbook* and *Star Wars Propaganda: A History of Persuasive Art in the Galaxy*. I have not seen either book. If the loop can reach images of them, they are worth more than everything above.

**On fan work.** Searching `CLAUDE.md`, `design/RimMandrake/standing_rulings.md`, `design/RimMandrake/art_judge_brief.md` and the canon `AGENT_BRIEF.md` finds no rule that names fan work (MEASURED). The nearest rules are that canon is the art target and every canon fact carries a source. So, as proposed practice: fan pages are a style reference at most, never a source of canon and never art to copy. Nor should the loop ship a fan Aurebesh font. It should draw its own 34 letters from the canon letter shapes, and may use a translator such as https://aurebesh.org/translator/ only to check spelling.

**A practical note on Aurebesh.** An image generator will produce confident gibberish. Letters need to be composed by the art pipeline from a hand-set alphabet, in a few brush, spray and stencil hands, then roughened with the rest of the mark. That alphabet is worth building first, as loop 3 uses it too.

### Proposed catalogue: replacing the 22 designs

Every row is proposed. "Canon" means the motif is on the cited page; "invented" means ours, in the manner of the source. The Sources section has the links.

| RimMandrake mark | Proposed Star Wars version | Source |
|---|---|---|
| Vandal (6 variants) | Crude Aurebesh insults, "POODOO" misspelled among them; a scrawled trooper helmet | Canon word and joke: Graffiti. Helmet invented |
| Scratches | Blaster-burn scorings and tool-cut lines, no paint | Legends: Graffiti/Legends. Treat as style only |
| TallyMarks | Tallies beside the credit symbol | Canon symbol: Aurebesh. Use invented |
| WarningGlyph | Warning words in Aurebesh over a shape from no Earth sign. Fixes the ISO triangle problem in `design/validation_walks/RimMandrake/Graffiti.md` | Invented |
| Tag_A, B, C | A single big letter, Aurebesh or Outer Rim Basic, in crew hands | Canon practice: Kintan Striders' "K"; trooper Sketch's "Senth" |
| Tag_RollCall | A column of Aurebesh names and call-signs, some crossed out | Invented, from helmet slogans in Aurebesh |
| ThrowUp_Wide, A, B | Paint-bomb bursts and fast one-colour wings. Bubble letters are the Earth idiom, so they go | Canon: Art Attack, Sabine Wren |
| Piece | Big layered abstract panels with an Aurebesh caption, in the manner of Lothal | Canon manner: L9, Sector 12 Service. Do not copy |
| Stencil_Crown | Imperial crest, struck through. Absorbs the old cog | Canon: Imperial crest |
| Stencil_Gear | Droid: a head in a slash or a rallying sign, by the painter's view | Canon stance: anti-droid sentiment, droid rights. Image invented |
| Stencil_Fist | White sun | Canon: White Suns |
| Paste_Flyer | Imperial "JOIN"-style sheet, red, white and black; defaced versions | Canon: Join (mural) |
| Paste_Gig | Cantina or race bill in Aurebesh | Invented. Canon setting only |
| Paste_Wanted | Imperial wanted sheet | Invented; source still owed. *Star Wars Propaganda* is the place to look |
| CrossOut | Slash reading as a galactic hand; keep same file names | Invented |
| IdeoSigil frames (3) | Stencil box, drip frame and halo redrawn in hexagonal, crest-like shapes | Invented |

### Proposed new marks, once the painter gates exist

| Hand | Marks | Source |
|---|---|---|
| Rebel | Starbird, sprayed, in many colours and qualities; struck crest; a guiding starbird as a trail | Canon: Starbird (symbol), Sabine Wren. Her personal art is not to be copied, only the symbol |
| Imperial | Crest, stencilled and clean; "JOIN"; painted over a rebel mark | Canon: Imperial crest, Join (mural). Painting over is invented |
| Mandalorian | Mythosaur skull; hexagon and diamond line-work | Canon: Mythosaur, Mandalorian |
| Nikto gang | Outer Rim Basic initial on what they raid | Canon: Kintan Striders |
| Twi'lek | Misspelled wit | Canon joke: Graffiti. Wider motif unsourced |
| Wookiee, Tusken, others | Source first. Do not invent and call it canon | Open to the loop |

### Proposed meme glyphs: rule, not list

Each of the 27 keeps its meaning. The drawing draws on a Star Wars subject where one exists: Transhumanist from droid parts and cybernetics, Rancher from a bantha skull, Shipborn from a hull and engine glow, NaturePrimacy from a wroshyr tree or moss painting. Those pairings are invented. Where nothing fits, draw a strange sign with an Aurebesh word beside it, and do not fall back on the current emblem with new paint. A reviewer has already called a third of these tidy clip-art (`D:\ClaudeWork\rimmandrake\ralph_graffiti\blind_judge_verdict.md`).

### Tier and naming

Per `design/NAMING_SCHEME_PLAN.md` §1: an aesthetic reskin takes the tier of the aesthetic, so it is RimStarWars. A Hoth campaign would want it unchanged.

Rename the mod, since "Imperial" no longer describes it: folder `src/RimStarWars/Graffiti`, packageId `mandrake.rsw.graffiti`, display name `RimStarWars: Graffiti`, prefix `RSW_`, namespace `RimMandrake.StarWars.Graffiti` if it ever needs C#. Move the walk to match. `RSW_Graffiti_Stencil_ImperialCog` is absorbed by the crest and deleted, with every reference fixed. First check whether any kept save holds it (UNMEASURED).

CLAUDE.md says every mod ships Mod Settings, so the mod needs a settings screen, at least to turn off each hand. That needs a little C#, so the static check that fails on `Source` has to go.

### Proposed north-star bars

- `star_wars_wall_shows_no_terran_mark`: on the Star Wars list, at play zoom, across all 49 marks, nothing looks like Earth graffiti: no wildstyle, bubble letters, Latin words or Earth emblems.
- `replaced_not_added`: no RimMandrake drawing can appear on that list. Check by instrument: 49 of 49 repointed. With the mod off, RimMandrake is unchanged.
- `reads_as_painted_here`: everything loop 1 won (true perspective, paint not sticker) holds for the new art.
- `aurebesh_is_real`: lettering is real Aurebesh or Outer Rim Basic that says something (pending question 1).
- `you_can_tell_whose_hand`: a player can tell a rebel wall from an Imperial wall, and a Mandalorian mark from a gang's, without reading a tooltip.
- `every_motif_has_a_source`: each mark says where it comes from, canon or invented, and nothing invented is called canon.
- Cannot: no fan art copied; no real-world signage (the existing bar, below); no Sabine artwork reproduced as our own.

### The Earth bar, and how far it goes

`mark_carries_no_earth_signage` (`design/validation_walks/RimMandrake/Graffiti.md`, line 100): "no mark reads as a contemporary real-world sign (road-hazard triangle, exit sign, traffic glyph)". Owner ruling 2026-09-16 kept it at full scope, covering symbols, and he chose to replace the offending glyph rather than exempt it. The earlier failures were a prohibition sign and an electrical-hazard bolt.

It covers signs only. It says nothing about Latin letters, the Earth graffiti idiom, a peace sign, an anarchy A, a clenched fist or a crown, and RimMandrake's own register relies on those. "Jawa graffiti will NOT look terran" is much wider. So the bar should stay as it is in loop 1, and the higher tiers should carry the wider ones proposed above and below. His bar was also won by replacing and never exempting; keep that habit.

### The social side carried over

Reskinning keeps `meaning`, so the reaction machinery carries over. What needs doing is making it true to the galaxy:

- A starbird on a wall should enrage an Imperial and hearten a rebel, and be something an Imperial wants scrubbed.
- A struck crest is an insult with a named target, so it feeds `RM_Graffiti_WallInsult`-style reactions (whatever loop 1 lands on) and goodwill.
- A droid-hating mark should hurt someone who loves droids. Droid pawns are a real case: does a droid viewer react at all?
- Going over a rival's mark should work with the new art, using the proper slash.
- Thought text must speak in the galaxy's voice, not generic words. It can be replaced by patch.

### Brief opening for loop 2

```
Graffiti is finished for any RimWorld game. On a Star Wars mod list it is still Earth: wildstyle, bubble letters, a crown, a fist. This loop makes it the galaxy's own.

Read the owner's own words and the north star in `design/validation_walks/RimStarWars/Graffiti.md`. That is the experience we owe the player, and it is the only thing you may not change. Then read `design/RimMandrake/graffiti_series_2026-11-07.md`, loop 2. It has the mechanism and a proposed catalogue. The catalogue is a starting point, not a list to finish.

His words: "The Star Wars layer should replace the standard graphics with entirely in-world-appropriate versions (see canon and online)... racial motifs, rebel vs. empire, etc."

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Play the mod, look at what a player would actually see, work out what's really wrong, and fix it. We trust you. Impress us.

All 49 marks get replaced, not joined. A later mod's files in the same folder add to the rotation, so repoint each def by patch. Make the alphabet first: real Aurebesh, in your own hands, so the walls can say things. A person who knows the films should stop and read a wall. Someone who knows nothing should still see that it isn't from Earth. And you should be able to tell who painted it: rebel, Imperial, Mandalorian, a gang. If that needs a small general gate on the painter in the framework, add it and keep it generic.

Don't lose what Graffiti won. True perspective, paint not sticker, and marks that matter between people all carry over. A starbird on the wrong wall should start something. Prove it in a real colony with real pawns.

Canon comes from Wookieepedia and the library in `design/RimStarWars/canon_references/`. Fan art can show you a mood, nothing more. Don't copy it, and don't call anything canon that you made up.
```

Then the "Taking turns with the game" and "How to work" sections from loop 1's `ralph/PROMPT.md`, unchanged but for the shots folder and the small mod list. Add `mandrake.rsw.graffiti` to a new solo list, with whichever Star Wars races and factions the loop needs to prove the hands.

## Loop 3: Sacred Graffiti and the Nine Gods

### What it is for

This is the one he calls the big deal. A Jawa colony should be written on by Jawas, and a person who has spent time with the Nine should be able to walk down a corridor and know whose wall it is: eyes at a door, a droplet that never falls, a tally with two eyes above it. Nothing should look as though it came from Earth. It is how a people with no land mark what they hold. In the words of `design/Jawa/graffiti_spec.md`: "A scavenger people with no land... owns one kind of permanence: the mark".

### What exists

`src/RimMandrake/SacredGraffiti`, packageId `mandrake.rm.sacredgraffiti`, "RimMandrake Sacred Marks". It depends on Graffiti. MEASURED:

- **One mark.** `RM_SacredMark_Ishko`: one texture, Beauty 6, a thought of +1 (`RM_ViewedSacredMark_Ishko`). The About admits the other eight are "Designed, not yet arted".
- **A ritual outcome no ritual calls.** `RM_Ishko_RitualOutcome_PlaceSacredMark` and worker. The walk records that nothing references it.
- **A god hook no one reads.** `godSatiationHook` appears in the extension and in `SacredMarks.xml`, and no code in `src` reads it (MEASURED by grep). A sacred mark does nothing for its god today.
- **A dead style row.** `StyleCategoryDefs_Salvation.xml` cannot act on filth, as shown above.
- **A walk with no owner's words.** `design/validation_walks/RimMandrake/SacredGraffiti.md`: draft north star, "not yet dictated", five bars about looks.

The rest of the faith is in good shape: `src/RimUtinni/Rites` holds the gods (`God.cs`), and `GameComponent_Ninefold` has `ApplyDelta` and `GetSatiation`. His ruling of 2026-10-22 already says "the Nine Gods belong in Salvation Rites. They are NOT a general reuse mod" (`infrastructure/state/items/NINEFOLD_MERGE_NINE_GODS_ONE_ROOF.md`). "TAKE OVER" follows from that.

### The Nine Gods

Names and Forms are from the pantheon, `design/Jawa/divine_satiation_engine.md` line 741 on, names locked 2026-08-08. The Form is quoted word for word. The sign and its place are from `design/Jawa/graffiti_spec.md` §1, which rules: "Iconography is each god's canon Form line, verbatim — never invented."

| God | Form (verbatim) | Spec's mark and where it goes |
|---|---|---|
| Ishko the Unmaskable | "a pair of glowing orange eyes in the dark" | Threshold Eyes, by any outer door |
| Ohm the All-Current | "current in a wire; the spark that wakes a dead engine" | Knuckle-Trace, a circuit-line spiral on machine housings |
| Oomo the Unspilled | "a single trembling droplet that never falls; the mirage-pool that recedes" | Drop That Stays, at cisterns, kitchens, medical beds |
| Mob'Unloo the Ever-Owed | "two unblinking eyes above an endless tally" | Tally-Blessing, over trade and storage doors |
| Rekko of the Second Hand | "a scarred hand rising from a scrap-heap" | Righted Hand, on a repaired building |
| Ta'Baa the Unrooted | "the receding dune-line; the engine-glow climbing away" | Receding Line, at ship ramps and map exits |
| Zizzik the Spark-Maker | "a rattle you can never locate; the errant spark in dry sand" | Ward Askew, a crooked spark-glyph by decoy heaps and hazard rooms |
| Sh'kaar the All-Searing | "white glare and heat-shimmer" | Shade Line, where shade meets glare |
| Ozzik the Shamed | "a tarnished crown half-buried in sand; a monument no one remembers building" | Buried Crown, in workshops and great rooms |

**What exists for each (MEASURED).** Every god has two pictures:

- An idol statue: `src/RimUtinni/UtinniStatues/Textures/Things/Building/Art/RUT_UtinniIdols/RUT_Idol_<God>.png`, 512 px, named in `RUT_UtinniStatues.xml`. Ohm, Rekko and Sh'kaar also have grand versions.
- A menu picture: `src/RimUtinni/MenuShell/Textures/RimUtinni/MenuShell/BG_God_<God>.png`, 2560x1440.

Only Ishko has a sacred mark, a def, a thought or a texture on the wall. So eight of nine have no mark at all, and no god has a working effect from one. I have not checked whether anyone approved the idol or menu art (UNMEASURED); the statues' About still says the carved art has not landed, while the files are there.

**What those pictures say**, as I read them at thumbnail size, so confirm before relying on it:

- The menu pictures follow the Forms: eyes in the dark, lightning, a droplet, eyes over columns, an open hand, a trail above a dune, a spark in a ring, a white sun, a buried monument. They are the closest thing to approved symbols.
- The idols are all hooded, robed figures with glowing eyes and no face, like a Jawa grown large, each with an attribute: Ishko hands on a slab; Ohm with a wire between raised arms and a skull at his foot; Oomo cupping a droplet; Mob'Unloo seated with scales; Rekko with a small droid across his knees; Ta'Baa striding away; Zizzik crouched over something; Sh'kaar with a sun-disc; Ozzik tall and cracked.

So the project has already answered his two words: **symbols** are the Forms and **depictions** can be these figures. No document says this is the rule (see question 2). The scales in Mob'Unloo's hand are an Earth image of justice. His wall mark should stay with the tally of his Form.

**Limits that must hold.** The gods are never evil (`GODS_NOT_EVIL_SWEEP_1`). All are male. The Jawas "should receive very little concrete evidence of the gods" (`design/Jawa/nine_faults_permanent_rite_2026-10-01.md`), with nothing so coarse as a skill blessing. So effects are small tilts, moods and standing. Spec's marks may be ugly or unsettling and still sacred: Zizzik's, Sh'kaar's and Ozzik's can carry negative Beauty.

**Undefined in the project** and so not filled in here:

- Each god's colours. The spec says marks "reuse their livery palette rows", and I did not find a table of those rows. The loop should look (`design/Jawa/salvation_engine_review.md` line 216 mentions per-god livery). If there is none, it is the owner's call.
- A single small glyph for each god, separate from the Form. None exists anywhere I read.
- What any god looks like beyond the Form, the idol, and nothing else.

### Mechanism

The whole mod moves. RimMandrake keeps the framework with no gods in it: the Devotional category and the deity-sigil fallback for any ideoligion. RimUtinni takes everything that names the Nine. In detail:

1. **Nine marks as ThingDefs** with `ModExtension_Graffiti`, Devotional, each with its own folder, so hand-painted variety is possible.
2. **A real hook.** A small component in the RimUtinni mod reads `godSatiationHook` and calls `ApplyDelta` on painting, on defacing, on enemy trashing. It belongs here because a RimMandrake mod may not name a god. This is a small amount of C#, against the seam test in the scope doc (see Conflicts).
3. **Who paints.** The faithful of the right god in the right place, which needs a rule for placement that the current pool does not have. The spec's places (door, machine, cistern, exit) are the starting point.
4. **Rites leave marks.** The worker and outcome go with the mod. The rites register names a Dark Vigil as the caller (`design/Jawa/salvation_rites_2026-10-01.md`, lines 50 and 325), and no XML or C# in `src/RimUtinni` has it (MEASURED; "vigil" only occurs in an unrelated Miasma patch). See question 4.
5. **All the other marks, in a Jawa hand.** On the campaign list a Jawa should not paint a rebel starbird by default. Repoint by patch again, loaded after the Star Wars layer, or use loop 2's painter gate with marks of their own, gated on the campaign xenotype `RSW_MandrakeJawa` (MEASURED in `design/RimStarWars/canon_references/jawa/description.md`). The gate is the better choice, because a Twi'lek captive can still paint like a Twi'lek.
6. **Old material deleted.** The `src/RimMandrake/SacredGraffiti` folder goes, along with the dead style row, and every inbound reference is fixed (`src/RimMandrake/Utils/modset_builder.py` lines 240-244 name it, and others). Check saves for `RM_SacredMark_Ishko` first (UNMEASURED; with no caller, unlikely).

### What Jawa graffiti looks like

**What canon gives (opened today):**

- No canon Jawa alphabet or painted symbol found. Wookieepedia searches for Jawa symbols, script and murals return nothing relevant. Say this plainly: Jawa marks are our invention in the style of the setting, within what canon allows.
- Scent is an integral part of Jawaese, which is why outsiders can barely learn it, and it has 27 words for junk and no word for cowardice. A written Jawa language is therefore not a given. Marks may be pictures and tallies far more than words, with Aurebesh or Outer Rim Basic borrowed for dealing with outsiders. This is a good reason for "strange symbols".
- Real Jawa words: "Mombay m'bwa" (it's mine), "Togo togu!" (hands off), "Tandi kwa!" (give it back), "Omu'sata!" (shut up), "Mob un loo?" (how much?), "Utinni!" (come on), "Ibana", "Nyeta".
- Jawas stay hooded. Canon: "No canonical source has revealed what a Jawa looks like under the hood". Eyes yellow, orange or red.
- There is canon for Jawas and graffiti, of a kind: the Hunters of the Outer Rim costume "Tagged Salvagers" has Jawas covered in pink, green, blue and yellow graffiti, put there by someone else.

**Proposed families.** All are invented on these sources, and all labelled so:

| Family | Marks | Source |
|---|---|---|
| The Nine: symbols | One sign per god, painted from his Form | Pantheon; spec §1 |
| The Nine: depictions | Figures and big scenes, hooded and faceless per the idols, or the Form at wall scale: a Long Wall of them | Idols; menu art; spec §6 Long Wall |
| Jawa figures | Hooded, glowing-eyed, stick-simple, in lines, carrying things, on a crawler; never a face | Jawa; spec's Rude Little Man, Caricature |
| Droids | Captured, tallied, sold, rebuilt, strapped on a back, droid parts as prayer | Jawa; Tagged Salvagers; canon library `DROIDS_INDEX.md`; Rekko's idol |
| Sand-crawler | The box-and-treads shape, tallies of moves | Sandcrawler; existing `RUT_Relief_Crawler.png` |
| Trade and threat | "MOMBAY M'BWA", "TOGO TOGU" in Aurebesh or Outer Rim Basic; price tallies; come-and-get-it taunts | Jawaese; spec's Faction Insult, Challenge Glyph |
| Clan code | Cache Cross, Water-Below, Teeth Glyph, Way Home: faint scrawl to outsiders | Spec §7 ruling 4. Canon echo: starbird trail in Sabine Wren |
| Strange marks | Shapes from no Earth alphabet, machine-like, in grease | His words; Grease Dewback in spec |

**The hand itself:** short reach, low on the wall (a one-metre painter should leave a one-metre-high mark; a real game fact worth testing), scavenged pigments, grease, rust, tar, reused stencils from scrap, repairs drawn over older marks.

### Tier and naming

RimUtinni. The test in `design/NAMING_SCHEME_PLAN.md` §1 ("Does it name Ash'karr, the Kolyska, the Nine, this clan, or this story?") settles it, as do his words.

- Folder `src/RimUtinni/SacredGraffiti`, packageId `mandrake.rut.sacredgraffiti`, display name `RimUtinni: Sacred Graffiti`, prefix `RUT_`, namespace `RimMandrake.Utinni.SacredGraffiti`, with defs like `RUT_SacredMark_Ishko`. I chose his name over the earlier `mandrake.rut.marks` in the spec. The name has not been used on any mod (MEASURED: no such folder).
- Depends on `mandrake.rm.graffiti` and `mandrake.rut.rites`. Loads after `mandrake.rsw.graffiti`.
- Walk moves to `design/validation_walks/RimUtinni/SacredGraffiti.md`.
- Mod Settings, as for every mod.

### Proposed north-star bars

- `nine_gods_each_known_by_sight`: someone who knows the Nine can name the god from each mark at play zoom, in every god's case, and each has a symbol and a depiction.
- `jawa_wall_is_not_terran`: nothing on a Jawa wall could be on Earth: no Latin, no wildstyle, no peace, anarchy or Earth religious shapes. Wider than `mark_carries_no_earth_signage`, which stands.
- `a_jawa_painted_this`: low, scavenged, obstinate; different from a rebel's work at a glance.
- `never_a_jawa_face`: no face under any hood. Canon.
- `no_god_is_evil`: nothing in art or text makes a god a devil, including Zizzik and Sh'kaar.
- `the_gods_stay_quiet`: a mark's effect is small and deniable. The player can feel it, and not point to a coarse blessing.
- `defacing_is_felt`: a sacred mark scrubbed or trashed gets a response a player can read on the pawn.
- `sacred_mark_reads_devotional`, `sacred_mark_reads_at_play_zoom`, `sacred_mark_sits_on_the_wall`, `sacred_never_reads_as_dirt`, `sacred_never_real_world_english`: the existing draft bars, kept.

### The social side carried over

Everything in Graffiti, plus the faith's own rows from `design/Jawa/graffiti_spec.md` §4:

- Painting a sacred mark gives its god a small drip, capped per room.
- Defaced on purpose: a small loss. By an enemy: a grievance, signed by the god.
- A challenge taunt lowers Ishko and raises Sh'kaar slightly; a cruel caricature pleases Zizzik faintly; a mural raises Ozzik; the clan-code network raises Ishko.
- Daily gestures should show in the room's life: touching the door frame beside Ishko's eyes, a knuckle-tap on Ohm's spiral (§2.0b-ii of the pantheon).
- Rivalries give marks enemies: Ohm and Zizzik, Ishko and Sh'kaar, Rekko and Ozzik. A devotee might paint over a rival god's mark, or refuse to; the loop may invent this, inside the limits above.
- Cleaning jobs skip sacred marks by default.
- A Jawa viewer and an outsider should read clan code differently: faint scrawl to one, directions to the other.

### Brief opening for loop 3

```
Sacred Graffiti is the mod the owner calls the big deal. Today it is one set of orange eyes that nothing in the game ever paints. It should be how a people with no land write their nine gods on the walls.

Read the owner's own words and the north star in `design/validation_walks/RimUtinni/SacredGraffiti.md`. That is the experience we owe the player, and it is the only thing you may not change. Then read `design/RimMandrake/graffiti_series_2026-11-07.md`, loop 3, and the gods themselves in `design/Jawa/divine_satiation_engine.md` (the pantheon) and `design/Jawa/graffiti_spec.md`.

His words: "Utinni scenario should TAKE OVER this mod and make it shine. Jawa graffiti will NOT look terran. Strange Star Wars esque symbols. Writing in Aurebesh. Droids. Jawa figures. The Nine Gods. That last part is very important. There should be the symbols of the Nine Gods, depictions of the Nine Gods, etc."

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Play the mod, look at what a player would actually see, work out what's really wrong, and fix it. We trust you. Impress us.

Graffiti and its Star Wars layer are done, and you get all of it: walls, paint, the pool, people who care. This mod has little of its own yet, so expect to build more than you polish. Eight gods have no mark, the mark that exists feeds no god, and no ritual leaves one. Make all of that real: move the mod into RimUtinni, give every god a symbol and a depiction, make painting and defacing matter to him and to the people watching.

Never invent a god or a fact about one. The Forms in the pantheon are the iconography. Where the documents are silent, write it in `ralph/QUESTIONS.md` and do your best inside what is written. The gods are never evil, and they stay quiet: little concrete evidence, nothing coarse. A Jawa never shows a face.

Walk the colony at play zoom. Someone who knows the Nine should be able to tell, room by room, who is honoured there, and nobody should think a human from Earth painted any of it.
```

Then the same "Taking turns" and "How to work" sections, with its own shots folder and a small mod list of Rites, Graffiti, the Star Wars layer and the Jawa race. Because loop 3 is less built than Artisan has yet been tried on, give it an earlier token review point and show Mandrake the first four god marks before the other five.

## Before either loop can start

1. **A frozen north star.** Artisan needs the owner's words on the experience. His words at the top of this page are those words for loops 2 and 3. Someone who may touch the walks must add them, and the bars he accepts, to the two walks. The Sacred Graffiti walk still says "not yet dictated".
2. **The clone and branch**, own how-to-run of about 60 lines, token review point and blind judge, per the Artisan `README.md`.

## Open questions for Mandrake

1. **Does the Aurebesh say real words?** The Graffiti Imperial walk and def call it "asemic" (looks like writing, says nothing). You said "Writing in Aurebesh", and canon walls say real things. *Recommend real, readable lettering, every word chosen, in Basic for the galaxy's marks and Jawa Trade Talk for theirs.*
2. **Should a god be drawn as a figure, or only as his Form?** The pantheon defines Forms and no bodies, but all nine idols are already hooded, faceless figures. *Recommend both: the Form is his symbol, and the idol figure is his depiction. This means accepting the idols as canon for the wall.*
3. **Do plain Jawa marks live in RimUtinni or RimStarWars?** The naming plan puts the Jawa species in RimStarWars, and this clan's culture in RimUtinni. A Tatooine campaign might want Jawa tags. Your words put them in the takeover. *Recommend all in RimUtinni for now, as they are this clan's hand; split later if a second Star Wars scenario ever wants them.*
4. **Is the Dark Vigil part of loop 3?** The mark's only named caller does not exist as a rite. *Recommend yes, and let the loop also have other existing rites leave marks, since "rites leave marks" is much of what makes it shine.*
5. **Ta'Baa's name.** The pantheon says his name is a pun on Jawaese "Taa baa" meaning goodbye. Wookieepedia's Jawaese page today gives "Taa baa" as "Thank you". The name is locked. *Recommend keeping the name, dropping "goodbye" as a canon claim, and calling it the clan's own reading. Thanks for leaving is arguably the better joke.*

## Conflicts with his words and with facts

Reported, not edited.

| File and line | What it says | Problem | Fix |
|---|---|---|---|
| `design/NAMING_SCHEME_PLAN.md:54` | "SacredGraffiti (core; the nine mark-styles extract to a RimUtinni content pack)" | He says Utinni takes over the mod | Move it to the RimUtinni list, no RimMandrake core |
| `design/NAMING_SCHEME_PLAN.md:185` | Phase 3: "extract the straddle packs (SacredGraffiti marks, ...) Each is a small FOUNDRY item" | Same; also FOUNDRY is retired | Drop SacredGraffiti; point to this page |
| `design/Jawa/salvation_rites_2026-10-01.md:51` | "The marks themselves (SacredMarks.xml) stay in SacredGraffiti." | Fine only if the mod moves | Say the mod is now RimUtinni's |
| `design/Jawa/salvation_rites_2026-10-01.md:34` | Gods' engine at `mandrake.rm.ninefold` | Stale since the fold of 2026-10-22 | `mandrake.rut.rites` |
| `design/Jawa/graffiti_spec.md:214, 219, 247` | `mandrake.rut.marks` pack, and the old folder folded into it | Name and "pack" shape | `mandrake.rut.sacredgraffiti`, whole mod |
| `design/Jawa/graffiti_spec.md` §5 | RimStarWars row of Aurebesh-lettered *variants* | He says replace, not add | Replace every mark |
| `design/Jawa/graffiti_spec.md`, family list | "Come And Take It" | A real-world slogan (Texas, Earth), in a family that must not look terran | Rename it from Jawa words, for example "Mombay M'bwa" |
| `design/RM_GRAFFITI_SCOPE_WIDENING.md` lines 401-408 | Salvation style category with `thingDefStyles` rows gives "Salvation's dialect of every generic mark, pure XML"; the worker moves into Graffiti | Styles cannot act on filth (decompile). Worker names a god in RimMandrake | Use patches or gated marks; worker goes to RimUtinni |
| `design/RM_GRAFFITI_SCOPE_WIDENING.md` line 410 | "If the follow-on needs C#, the engine surface here was drawn wrong" | The god hook needs a reader, which RimMandrake may not contain | Allow C# in the RimUtinni mod |
| `src/RimStarWars/GraffitiImperial/About/About.xml`, walk, `validation.py` | One additive "content-only" mark, no Source; "asemic Aurebesh" | Additive; no settings | Rewrite with the mod |
| `src/RimMandrake/SacredGraffiti/About/About.xml` | "RimMandrake Sacred Marks"; the Salvation Matrix is "design prose only" | Wrong tier; the engine has shipped | Goes with the mod |
| `src/RimMandrake/SacredGraffiti/Defs/SacredMarks.xml:62` and `src/RimMandrake/Graffiti/Source/ModExtension_Graffiti.cs` | Name `RimMandrake.Ninefold.God` | Stale | `RimMandrake.Utinni.Rites.God`, or no god name in the framework |
| `design/validation_walks/RimMandrake/SacredGraffiti.md` | RimMandrake subject, RimMandrake packageId | Wrong tier | Move the walk with the mod |
| `design/Jawa/divine_satiation_engine.md:816` | "canon Jawaese 'Taa baa' = goodbye" | Wookieepedia says "Thank you" | See question 5 |
| `infrastructure/state/ledger/events/BENCH.jsonl:18994` | Note uses the refused name `SACRED_GRAFFITI_TAKEOVER_NINE_GODS_WAIT_TURN` | Item is `SACRED_GRAFFITI_FINISH_NINE_GODS_WAIT_TURN` | Append-only, so leave; a new note can correct it |

## Sources

Wookieepedia pages opened through the API, 2026-11-07, as `https://starwars.fandom.com/wiki/<Page>`:

Graffiti, Graffiti/Legends, Graffiti-bomb (Legends), Starbird, Starbird_(symbol), Alliance_Starbird (Legends-era content), Imperial_crest, Aurebesh, Outer_Rim_Basic, Sabine_Wren, Art_Attack, Artist, Kintan_Striders, White_Suns, L9_(mural), Sector_12_Service, Join_(mural), Spectres_mural, Mandalorian_mural, Wroshyr_Mural, Mythosaur, Mandalorian, Jawa, Jawaese, Jawa_Trade_Talk, Tagged_Salvagers, Sandcrawler, Anti-droid_sentiment, Droid_rights, Moss_painting, Tusken_Raider, Wookiee, Twi'lek, Star_Wars_Propaganda:_A_History_of_Persuasive_Art_in_the_Galaxy, Category:Murals.

Other pages opened: the Flickr, Street Art Utopia, Graffiti Life and Aurebesh.org links above, and https://www.thingiverse.com/thing:7252510 (a fan Jawa stencil; title only, of no use). The built-in web search was not available in this session, so open-web search ran through DuckDuckGo's HTML page. Search queries are the only source for the Etsy, Pinterest and DeviantArt mentions.

Not opened: *Sabine: My Rebel Sketchbook* and *Star Wars Propaganda* themselves. The wiki page title for the sketchbook did not resolve under the name I tried. "Rebels Are Terrorists", "Rebel Resistance Poster" and "Victory of the Rebel Alliance" turned up in a Wookieepedia search for rebel propaganda and I did not open them; loop 2 should.
