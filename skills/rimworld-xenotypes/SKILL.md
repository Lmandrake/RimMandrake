---
name: rimworld-xenotypes
description: Authoring, moving, spawning and debugging RimWorld xenotypes and the genes that give them a face. A XenotypeDef is a list of gene names and nothing else — appearance lives in GeneDef renderNodeProperties, forcedHeadTypes and HeadTypeDefs; a xenotype cannot be spawned at all without a PawnKindDef; xenotypeChances is dictionary-keyed and an `<li>` there discards the whole FactionDef silently; xenotypeSet inherits and appends so a Star Wars faction fields vanilla Hussars unless Inherit="False"; and a def can ship in an active mod and still not exist in the running process because a dedup mod deleted it at load. Use when writing or reviewing a XenotypeDef, GeneDef, HeadTypeDef or species mod, when a species has "no art", when a faction stops generating or generates the wrong pawns, when copying species between mods, when a .xtp needs promoting to a def, or before concluding any xenotype is missing or broken.
---

# Xenotypes — the def is a gene list; everything else is somewhere else

Almost every expensive mistake here is one mistake: **reading the XenotypeDef and expecting to find the species in
it.** The def is a pointer. The species is in GeneDefs, HeadTypeDefs, RulePackDefs, text files and textures. Sometimes
the species is also in a C# assembly. Each of those parts can fail on its own with no visible error.

The lessons come from this project's 1.6 mod list. The work was the rescue of 69 Star Wars species into one mod of
ours. That mod is `D:\Luke\dev\RimMandrake\src\RimStarWars\StarWarsRaces`. A "donor" is a mod that we copied species from.
An engine claim names the game class that it comes from. A claim marked *inferred* was not observed. Dates,
old counts and corrected claims are in `references/history.md`.

| I want to… | Start at | Reference |
|---|---|---|
| **write** a xenotype and see one in game | §1, §4 | — |
| find out **why a species looks wrong or "has no art"** | §2, §3 | `references/appearance.md` |
| know **which colour a pawn shows** | §3a | — |
| get a species **into a faction's pawns** | §5 | — |
| work out **why a def is missing at runtime** | §6 | `references/verifying.md` |
| **copy species out of a donor mod** | §10 | `references/closure.md` |
| **prove** any of it actually worked | §9 | `references/verifying.md` |

---

## 1. The whole surface of a XenotypeDef

Each of our 70 species defs sets these fields. The gene list here is cut short:

```xml
<XenotypeDef>
  <defName>RSW_RimMandrakeAbednedo</defName>
  <label>Abednedo</label>
  <description>...</description>
  <iconPath>RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_Abednedo</iconPath>
  <inheritable>true</inheritable>
  <canGenerateAsCombatant>true</canGenerateAsCombatant>
  <factionlessGenerationWeight>0</factionlessGenerationWeight>
  <nameMaker>RSW_NamerAbednedo</nameMaker>
  <genes>
    <li>Hair_BaldOnly</li>
    <li>RSW_AbednedoHead</li>
    <li>Skin_Orange</li>
  </genes>
</XenotypeDef>
```

Some of our defs also set `combatPowerFactor`, `chanceToUseNameMaker`, `nameMakerFemale` or `descriptionShort`.

**Genes own everything that matters**: appearance, stats, hediffs, abilities and needs. Judge a xenotype by walking its
`genes` list. Never judge a xenotype by its def alone.

⭐ **A gene list can still randomise per pawn.** `GeneEyeColor` is an abstract parent that carries
`exclusionTags: EyeColor`. List four of its children on one xenotype, and the engine makes one of them active on each
pawn. The later genes of the list win more often. `guy762_xenotype_hutt` ships four big-eye colours this way. A fixed
gene list does not mean that every pawn of the species looks the same. §3a gives both mechanisms.

---

## 2. 🔴 An icon is not the appearance

`iconPath` is a UI symbol for the xenotype panel. **A xenotype with no icon at all renders perfectly.** None of its
appearance was ever in the icon. With dev mode on, the load reports the config error
`iconPath is empty.` (`XenotypeDef.ConfigErrors`).

If you report "no art" from an icon audit, someone can delete working content. Measured gene counts against genes
that carry pawn art:

| xenotype | genes | genes carrying pawn art |
|---|---|---|
| `BTD_Lasat` | 24 | 13 |
| `Hutt` | 34 | 17 |
| `Gamorrean` | 28 | 7 |

**Before an audit, say which question you answer**: *does this have a UI icon*, or *does this render*. File analysis
got the second question wrong twice. A live spawn settled it (§9).

---

## 3. Four different ways a gene supplies appearance

If you check the wrong one, you find nothing, and "the species has no art" looks true. Check all four before you
conclude that anything is missing.

| mechanism | field on the GeneDef | gives you |
|---|---|---|
| **render nodes** | `renderNodeProperties` | textures drawn on the pawn |
| **head types** | `forcedHeadTypes` → `HeadTypeDef.graphicPath` | the whole head sprite |
| **colour only** | `skinColorOverride` · `hairColorOverride` | tint, no texture |
| **body/fur** | `bodyType` → `BodyTypeDef` · `fur` → `FurDef` | silhouette and pelt |

**Half the species identity is in head types, not in the genes.** The first 69 species needed **104 HeadTypeDefs**.
Facial Animation also has a def type named `HeadShapeDef`, and its own `FacialAnimation.HeadTypeDef`. Both differ from
the game's `HeadTypeDef`. Do not conflate them.

**The pawn is a stack of layers.** Each render node carries `drawData.defaultData.layer`. The paint order is that
number. A real node from `RSW_Jawa_Eyes_HugeOrange`, cut short:

```xml
<li Class="PawnRenderNodeProperties_Eye">
  <texPath>RimMandrakeSW/Jawa/jawaeyes_glow</texPath>
  <parentTagDef>Head</parentTagDef>
  <anchorTag>RightEye</anchorTag>
  <rotDrawMode>Fresh, Rotting</rotDrawMode>
  <drawData><defaultData><layer>55</layer></defaultData></drawData>
</li>
```

The fields that carry the meaning, from real nodes of this mod list:

| field | what it does |
|---|---|
| `nodeClass` / `Class=` | e.g. `PawnRenderNode_AttachmentHead` (the node class), `PawnRenderNodeProperties_Eye` (the properties class) |
| `parentTagDef` | what the node anchors to: `Head`, `Body` |
| `texPath` | one texture |
| `texPaths` | 🔴 a **LIST of variants**. The engine picks one per pawn, from `texSeed`, the pawn's id and the gene's `loadID`. So two pawns of one species can differ |
| `drawData.defaultData.layer` | paint order in the stack (`guy762_FacialRidges_bumpy` = 51, our glow eyes = 55) |
| `colorType` + `useSkinShader` | `Skin` tints the node to the pawn's own skin colour |
| `skipFlag` | `Hair` hides the node when drawn headgear hides the hair (apparel on `UpperHead` or `FullHead`, unless the apparel sets `renderSkipFlags`; then that list alone decides). Drawn hair does not hide the node |
| `rotDrawMode` | the corpse states in which the node draws. Unset, the node draws in all three states. `Fresh, Rotting` draws the node on a fresh or rotting corpse and stops it on a dessicated one |

An eye node (`PawnRenderNodeProperties_Eye`) always has `skipFlag` `Eyes`, whatever the XML says. A full-head hat hides
it, unless the hat sets `renderSkipFlags` or `forceEyesVisibleForRotations`.

`guy762_FacialRidges_bumpy` is the reference example of the attachment form:

- `PawnRenderNode_AttachmentHead`, `parentTagDef Head`, two `texPaths` variants, `layer 51`;
- `colorType Skin` + `useSkinShader`, `skipFlag Hair`, `rotDrawMode "Fresh, Rotting"`.

Our copy of it is `RSW_FacialRidges_bumpy`.

> **Which node class, which parent tag, what a layer number means, and how a render node interacts with Facial
> Animation?** → `references/appearance.md`

⚠️ **60 of our first 104 head types had no `requiredGenes`.** Donor mods ship them that way. A head type with no
`requiredGenes` and with `randomChosen` true (the default) is in the GLOBAL random-head pool. Such a head can land on
any pawn in the game of the head's `gender` (`Pawn_StoryTracker.TryGetRandomHeadFromSet`; its callers test
`randomChosen`). Either field closes the pool: set `requiredGenes`,
or set `randomChosen` to false. If you copy head types, decide deliberately which one you want. No head type of
StarWarsRaces is in the pool now.

---

## 3a. 🔴 Every pawn gets the whole gene list; one colour gene of a conflicting group is active

Two facts decide the colour, and they are easy to mix up.

**Fact 1: the list is not dealt out.** `Pawn_GeneTracker.SetXenotype` adds every gene of the list to every pawn. Six
`skinColorOverride` genes on a xenotype mean that every pawn carries all six. They are endogenes when the xenotype is
`inheritable`, and xenogenes otherwise. MEASURED 2026-09-20 via `jawa/pawn_genes` against 17 live Ithorians: all 17
carried the identical set. The set was `Skin_PaleRed, Outland_Skin_DeepSage, Skin_Orange, Outland_Skin_DeepBrown,
Outland_Skin_Brown, Outland_Skin_PaleBrown`. Not one gene was missing from any pawn.

**Fact 2: the pawn shows one of them, picked at random per pawn.** The code is in `Pawn_GeneTracker`
(`Notify_GenesChanged`, `SelectGene`, `OverrideAllConflicting`):

- When the engine adds a skin-colour gene, it picks one of the pawn's skin-colour genes at random, each equally likely.
  If the pawn has xenogenes among them, it picks from the xenogenes only.
- The chosen gene overrides each gene that it conflicts with. An overridden gene stays on the pawn, inactive and not
  drawn. The last pick stands, and the save file keeps it (`overriddenByGene`).
- Two genes conflict when they share an `exclusionTags` entry. Each `GeneSkinColorOverride` child inherits the
  tag `SkinColorOverride`, and so do the `Outland_Skin_*` genes. A child can replace the list with `Inherit="False"`.
  The four Dathomirian skin genes do: `SkinColorOverrideMale` and `SkinColorOverrideFemale`.
- Only a gene that the engine calls `RandomChosen` overrides others in this way. That is a gene with `randomChosen`
  true. A cosmetic gene (colour, body, head, hair, beard or graphics) is also
  `RandomChosen` when its three biostats are all 0.
- If the conflicting genes are not `RandomChosen`, the pick is not random. `CheckForOverrides` then makes one gene
  override the other by a fixed rule. A xenogene beats an endogene; if not, the earlier in `GeneUtility.GenesInOrder`
  wins. For skin colour, the rule shows only after the next gene change. Until then the last one in the list gives the
  colour.
- Other conflicting `RandomChosen` genes (eye colours) take a different path. Each added gene has a 50/50 chance against
  the current winner. So the later genes of the list win more often.
- If several skin-colour genes do not conflict, all of them stay active. The last active one in the pawn's list gives
  the colour (`EnsureCorrectSkinColorOverride`).
- A skin override replaces the melanin colour. The two do not mix (`Pawn_StoryTracker.SkinColor`).

This agrees with an earlier observation. Bith pawns with byte-identical gene lists rendered orange, green and pink in
one shot. Their four colour genes conflict. Nobody has measured if an active mod changes this pick.

Pawn generation adds a `Skin_MelaninN` gene only if no active melanin gene is on the pawn. It adds a `Hair_*` colour
gene by the same test. The diff of three Ithorians showed those differences only: `Skin_Melanin3` vs `Skin_Melanin9`,
and which `Hair_*` each pawn got.

Consequences:

1. 🔴 **If you add a skin-colour gene to a conflicting group, you add one more candidate to the pick.** With N genes,
   about 1 pawn in N shows each colour. The new gene does not replace the others. To get one colour on every pawn, leave
   one skin-colour gene in the list.
2. 🔴 **A line-up of N pawns of one species is one gene list with N colour picks.** The gene lists are identical except
   for melanin and hair. The line-up may miss a colour of the list. Do not let anyone rule a palette from a line-up
   without saying this out loud.
3. ⚠️ **`jawa/pawn_genes` cannot answer "which colour won".** The tool returns the def names of all genes, with no
   active flag. Every pawn reads the same, so a census over it gives a confident, uniform, meaningless number. A
   suspiciously uniform count, such as 17/17 on one gene, is a query bug until you prove otherwise. Look at the pawn, or
   read `overriddenByGene` in the save.

**A second way to vary a pawn** is `texPaths` on a render node, the list of variants that `texSeed` picks from (§3).

## 3b. 🔴 Facial Animation overdraws your face — exclude the xenotype or it looks human

Facial Animation is workshop mod 1635901197, called FA here. **FA replaces the pawn's face at render time.** A
xenotype can have a perfect gene list, a head type that resolves and shipped textures. The pawn can still render as a
plain human, because FA draws over it. The symptom, verbatim from the owner: *"It has the ears, but no snoot... the face is a normal
human."* Ears are a head ATTACHMENT outside the face rect, so ears survive. The snoot is inside the rect, so FA
overdraws it.

**FA itself has one switch, per xenotype, in the player's FA settings. No def can set it.**

```
Config/Mod_1635901197_FacialAnimationMod.xml
  <IgnoreEnableAnimationForRaceXenoTypeListAA>
    <li>Human-BTD_Hutt</li>        <- "Human-" + the XenotypeDef defName
```

- **FA takes its skip list ONLY from the player's ModSettings.** FA reads that file once, at startup. So an edit of the
  file needs a restart. No def, extension or XML hook exists.
- Each entry is a plain on/off. FA's settings UI shows the same entries as checkboxes.
- There is **no partial mode** in the file: one list, plus the global `DrawEyesParts` / `DrawEarsParts` booleans.
- An "intermediate" look (brows animating, eyes static, no mouth) is NOT a setting. The cause: FA still draws the
  xenotype, and the xenotype's own big-eye and jaw art masks FA's eyes and mouth.

**Our mod ships the opt-out, so a player needs no setting.** StarWarsRaces holds the list as data in
`src/RimStarWars/StarWarsRaces/Defs/Misc/RSW_FacialAnimationOptOut.xml`. Its C# postfixes
`FacialAnimationModSettings.ShouldDrawRaceXenoType(Pawn)`, resolved by name. The mod setting `hideFacialAnimationFace`
turns the opt-out on (the default) or off. Any other mod that ships an opt-out must do it in C# too. The owner's own
config is not evidence that players get the same. `python3 src/RimStarWars/StarWarsRaces/selftest_fa_optout.py` fails
when a xenotype with an `RSW_` head is not on the list. The live check of the opt-out is still owed (item
`FACE_OPTOUT_REPAIR_ONLY_AT_HOME`).

🔴 **The entries are defNames, so RENAMING A XENOTYPE SILENTLY UNPROTECTS IT.** Each entry is `Human-<XenotypeDefName>`. A stale key matches nothing, and the
species draws FA faces. `reload_mod_settings`, dirty graphics and a respawn change nothing. After any rename (a tier
prefix change, for example), re-key the opt-out def in the same commit. For a xenotype that only the player's file
protects, re-key `IgnoreEnableAnimationForRaceXenoTypeListAA` and restart. This has happened: every old entry was a
dead reference, and **all 70 new species rendered with human faces at once.**

`RSW_MandrakeJawa`, the clan's own xenotype, is not on the shipped list. Its head gene `RSW_Jawa_Head_Plain` forces
vanilla heads. Its key in the owner's FA file is the old name `Human-MandrakeJawa`, so nothing excludes it now. Whether
FA then hides the Jawa's glow eyes is UNMEASURED.

**Which species need the opt-out? Decide by what the genes DRAW, not by how alien the species looks:**

| tier | what it does | FA verdict |
|---|---|---|
| draws ON the face — eyes, brows, tusks, jowls, facial ridges (`HeadAttachments/`) | FA overdraws it directly | **must exclude** |
| replaces the head SHAPE, or adds horns/ears/tails (`forcedHeadTypes`, render nodes) | FA paints a human face onto a non-human skull | **exclude** |
| no head or face genes at all | nothing to conflict with | leave FA on |

Survey the mod; do not guess. A gene whose body mentions `HeadAttachments` is tier 1. A gene with `forcedHeadTypes` is
tier 2. In our 70, that split was 29 / 35 / 5.

⚠️ **This fix was hard to get and is easy to lose.** The repo holds backups of FA's settings file:
`deployed/config/Mod_1635901197_FacialAnimationMod.BEFORE-{hutt,gand,gamorrean,bulk}-exclude-*.xml`. Back up that file
before you edit it, and commit both sides.

## 4. 🔴 A xenotype cannot be spawned — PawnKindDef is the handle

Pawn generation takes a `PawnKindDef`. **A XenotypeDef has no spawn of its own; it needs a route.** Four def fields feed ordinary generation: a `PawnKindDef.xenotypeSet`, a faction's `xenotypeSet`, a meme's
`xenotypeSet`, and a `factionlessGenerationWeight` above 0 (`PawnGenerator`). Three other routes exist: the xenotype
picker of the start screen, a scenario part, and another xenotype's `doubleXenotypeChances`.

**Author the PawnKindDef in the same commit as the XenotypeDef.** If the defs give the species no route,
ordinary generation never produces one. We authored 70 PawnKindDefs for our 70 xenotypes.

To look at one quickly, no new kind is needed. On the bridge, `jawa/spawn_pawn` takes any `kindDef` and a `xenotype`
argument, and the argument beats the kind and the faction. The game's dev action "Set xenotype" converts a spawned pawn.

---

## 5. Getting a xenotype into the world

### 🔴 `xenotypeChances` is dictionary-keyed

```xml
<xenotypeChances>
  <BTD_Nikto>0.3</BTD_Nikto>
</xenotypeChances>
```

The element name is the defName. **If you write `<li><xenotype>X</xenotype><chance>Y</chance></li>`, the loader
DISCARDS THE ENTIRE FactionDef.** `XenotypeChance` reads the text of the first child, gets null, and the float parse
throws. The loader then writes one error line, `Exception loading def from file …`, and goes on without the def
(`DirectXmlToObjectNew`). In a long log that line is easy to miss, and nothing else tells you. The form killed five of
our authored factions. The tell was pure correlation: every file *without* an `<li>` loaded, every file *with* one did not.

**Write the keyed form, and check every existing `xenotypeChances` that you inherit.** Vanilla is unanimous: every
instance in the game is keyed.

⚠️ `validate_patch.py` cannot catch this. Its own banner says that it does not check field names, types or shapes.

### 🔴 `xenotypeSet` inherits and APPENDS

The game **appends** a child's list to its parent's list, and substitutes nothing. Vanilla parents ship:

| parent | ships |
|---|---|
| `OutlanderFactionBase` | 5 — Hussar, Dirtmole, Genie, Neanderthal, Starjack |
| `PirateBandBase` | 9 |
| `TribeBase` | none (luck, not design) |

Our patch `src/RimUtinni/UtinniPatches/Patches/XenotypeCut_SpawnSets.xml` removes many of those entries. A def that
loads without that patch still gets them.

**Write `<xenotypeSet Inherit="False">` on any faction whose species list must be exactly what you wrote.** If not,
your Star Wars outlanders field Hussars. The same rule holds for `pawnGroupMakers`.

⚠️ **An EMPTY set is not "no opinion". The faction's share is 100% baseliner.** `XenotypeSet.BaselinerChance` returns
`1f` when the list is empty (`RimWorld/XenotypeSet.cs`). So `<xenotypeSet Inherit="False" />` on a faction of ordinary
humanlikes means plain humans, unless a pawn kind or a meme names a xenotype. You usually want that for a faction whose
pawn kinds carry their own races: droids, mechanoids, insects. `PawnGenerator` iterates the faction set by `Count`, so
an empty set adds nothing, and the kind decides. You rarely want it on a faction of people.

The chances of the faction, its memes and the kind add up. Baseliner takes what is left below 1. A kind with
`useFactionXenotypes` false ignores the faction's set.

🔑 **These are two separate questions. Do not mix them.**

- *Does the parent's list still arrive?* `Inherit="False"` answers it.
- *What happens when mine is empty?* `BaselinerChance` answers it.

An empty set with the attribute strips the parent AND yields baseliners. An empty set without it inherits the parent's
five and yields those.

### 🔴 Two xenotypes can share a `label`, and then the label proves nothing

One mod can ship two xenotypes for the same species: a hand-built set and a generated one, both labelled "Jawa".
Nothing in play tells them apart, because the pawn inspect panel shows the label and not the defName. In this repo, a
`defaultFactionDef PlayerColony` pawn kind rolled the 24-gene generated one for weeks. The owner's ratified set sat
unused. Nobody saw it, because both said "Jawa". The ratified set is `RSW_MandrakeJawa` (38 genes); the generated one
is `RSW_RimMandrakeJawa` (24).

**Settle which one a pawn has by defName or by gene count, never by reading the label.** When a ruling names "the only
active xenotype", grep every `xenotypeChances` in the repo for the OTHER one. A def-keyed dictionary hides the name
inside an element tag. A plain search for `<xenotype>` will not find it.

### 🔴 `factionlessGenerationWeight` and `canGenerateAsCombatant` do not discriminate

- `XenotypeDef` sets an unset `factionlessGenerationWeight` to `1` and an unset `canGenerateAsCombatant` to `true`.
  So a xenotype that declares neither field can arrive as a factionless pawn. Write both fields on every xenotype.
- `factionlessGenerationWeight` controls **wanderer/factionless generation only**: pawns with no faction that rolled
  baseliner. A faction whose `xenotypeSet` names a xenotype still generates it at weight 0.
- `canGenerateAsCombatant` matters only when the request needs a pawn capable of violence. A `false` there removes the
  xenotype from a faction's fighters.
- A runtime field read cannot tell an unset field from a chosen value, and it once misled us. `BTD_Jawa` declared
  neither field and read `0.0 / False` at runtime. That reading is **identical to a xenotype that is deliberately
  suppressed.** The cause of that reading is unknown: it does not match the engine's defaults.

**Settle "does this generate?" from the SOURCE XML (does the def declare the field?), or by repeated generation.
Never settle it from a runtime field read.**

---

## 6. 🔴 A def can ship in an active mod and not exist in the running process

Another active mod can delete the def at load. `[BTD] Xenotype REMIX: Star Wars` did. That mod ships **70 XenotypeDefs,
zero genes**, and a Harmony assembly whose only job is deduplication: `BTD_EquivalenceLoader`, `GetAllDefsToRemove`,
`CalculateDuplicatesRemoved`, and the log string:

```
- {0} defs have {1} references to removed xenotype '{2}'
```

Its `BTD_Data/XenotypeEquivalencies.xml` maps each species to its BTD, SWX and OR equivalents, and keeps its own. So
`OuterRim_Jawa` and `guy762_xenotype_jawa` loaded, and BTD removed them. `BTD_Jawa` survived. Cherry Picker, which is
active now, also deletes XenotypeDefs and GeneDefs at load (`infrastructure/state/facts/dump-is-pre-cherrypicker.md`).

🔴 **The survivor expires.** That result was true while the three donor mods were active. The donors are now off, and
one species mod of ours replaced them. **None of those three names loads today.** The live Jawa xenotypes are
`RSW_MandrakeJawa` and `RSW_RimMandrakeJawa`, from `mandrake.rsw.starwarsraces`. Patches that still aimed at `BTD_Jawa`
matched nothing for days and logged nothing. A `PatchOperationConditional` on a missing def is a silent no-op.

⇒ **"X is the one that survives dedup" is a fact about a MOD LIST, not about a def.** Measure it again after any
change to the active set. Treat a survivor name in a doc as a claim with an expiry date.

⇒ **A def dump can hold a def that the running game does not have.** An offline scan reads files, so it always shows
the state before deletion. A DefDump comes from one load, and can be from before or after a deletion. Each reading is
correct about its own moment. No mod-list check finds the difference: all three mods were active, and all three files
were on disk.

**The test that decides is a runtime lookup by defName.** `set_pawn_xenotype` returned `"No XenotypeDef named 'X'"`
for the two removed names. The same call converted a pawn with the third name, so the tool and the spelling were
proved. Use a test of that shape: a known-good control in the same call.

⇒ **Remove such mods as a SET.** If you remove only the dedupper, every collision that it suppressed comes back.

---

## 7. Name makers: the def is not the content

`nameMaker` and `nameMakerFemale` on a XenotypeDef point at **RulePackDefs**. Their `Rule_File` entries point at
plain-text word lists under `Languages/<lang>/Strings/`.

🔴 **Copy the def alone, and the namer resolves cleanly and generates nothing.** The result is a silent empty success,
with no error anywhere. The first 48 RulePackDefs needed **140 `.txt` files**.

**Copy the `Strings/` tree with the RulePackDefs, and follow `include` for chained packs.** Chained packs pull further
packs and further files.

---

## 8. `.xtp` files are not defs

The game's own xenotype editor saves to
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Xenotypes\<name>.xtp`.
The pawn editor loads that file, and **no def can reference it**: `PawnKindDef.xenotypeSet` takes XenotypeDefs.

**To use one, promote it into a real def: transcribe its genes.** The def and the `.xtp` are then two separate things,
and they drift. Write in the def's comment which differences are on purpose. `RSW_MandrakeJawa` has 38 genes, and its
`.xtp` has 35. The three extra genes are the owner's rulings. Keep all three when someone transcribes the file again.

🔴 **The `.xtp` carries only `name` and `inheritable`, the gene list and `iconDef`. Whoever transcribed it INVENTED
every other field in the promoted def.** We found `canGenerateAsCombatant false` invented that way. It stopped a
faction from generating any fighter at all. **Audit every non-gene field of a promoted def against the `.xtp`. If the
`.xtp` does not say it, you chose it, so choose it deliberately.**

---

## 9. Verifying xenotype work

Nearly every failure in this file is silent. So **choose the check that can see the failure that you care about**:

| the question | the check that answers it |
|---|---|
| does this def exist in the *running game*? | a runtime lookup by defName. A dump can differ from the process (§6) |
| does this species render? | **spawn one and look.** Beats any file analysis |
| does this faction still load? | it generates pawns at all. A discarded FactionDef leaves one log line only (§5) |
| does this xenotype generate? | repeated generation, or the source XML. Not a runtime field read (§5) |
| is this standalone set really standalone? | **a load with the donor mods switched OFF.** Nothing else proves it |

🔴 **A dump is not the running process.** An offline scan is the right tool for "what did the mods ship". The scan is the
wrong tool for "what exists right now".

🔴 **A spawn test beats any amount of file analysis.** One spawned pawn settled the art question in §2, after two
file-based analyses got it wrong. If a game is free, spawn first and read files second. Claim the game with
`python3 src/RimMandrake/rimflow/game_lock.py claim <game> --for "<what>"`, and release it after.

🔴 **Only a load with the donors disabled proves that a standalone mod is standalone.** A load *alongside* its donors
proves nothing. Every reference that you forgot to copy resolves against the donor, and the mod looks complete.

> **The full protocol — what each of these actually costs, and the order to run them in?** →
> `references/verifying.md`

---

## 10. Moving species between mods

The closure (everything that the species points at) is much wider than genes. The rescue of 69 species pulled:

```
113 genes · 104 head types · 48 rule packs · 140 word lists · 713 textures
plus hediffs, recipes, abilities, damage defs, effecters, flecks, thoughts,
tattoos, hair, style categories, gene categories, furs, body types
```

Three mask hediffs alone pulled 3 ThingDefs and 6 RecipeDefs.

**Two traps decide whether the copy works at all:**

🔴 **Grep `geneClass` and `Class=` before you assume that a gene is pure XML.** Measured C# dependencies that hid in
genes and modExtensions:

| symbol | from |
|---|---|
| `VEF.Genes.GeneGendered` | Vanilla Expanded Framework — 6 genes / 7 species |
| `OuterRimDiversity.Gene_NoEyes` | one species (Miraluka) |
| `IntegratedGenes.*` · `OutlandGenes.Gene_Empathic` | their own mods |
| `EyeOffsetSouth.ModExtension_EyeOffsetSouth` | an assembly shipped INSIDE another mod |
| `BigAndSmall.PawnExtension` · `BetterPrerequisites.GeneExtension` | frameworks |
| `TabulaRasa.DefModExt_HeadTypeStuff` | 36 defs |

🔴 **`Name=` is a second global namespace, and defNames collide across def types.**

- An abstract parent must travel with the copied defs **and be renamed**. If not, `ParentName` resolves to nothing.
  The load then logs `Could not find parent node named`, and the child loads without every inherited field
  (`XmlInheritance`).
- `OuterRim_Wookiee` is **both** a XenotypeDef and a PawnKindDef. An index keyed on defName alone silently keeps the
  one that it walked last.

⇒ **A prefix migration is never a string replace.** Key every index on `(defType, defName)`.

> **The full extraction procedure, the closure walk, and the per-def-type list of what points at what?** →
> `references/closure.md`

---

## In this repo

```
src/RimStarWars/StarWarsRaces/            our species mod: xenotypes, genes, head types, kinds, namers
src/RimMandrake/Utils/gen_races_mod.py    regenerates its generated files from the donors; --check writes nothing
src/RimMandrake/Utils/refresh.py          says which artefact is stale; --offline rebuilds the offline scans
```

`Defs/XenotypeDefs/RimMandrakeXenotypes.xml` is generated; do not edit it by hand. `MandrakeJawaXenotype.xml` and
`Defs/PawnKindDefs/RimMandrakePawnKinds.xml` are hand-edited. Read the header of a file before you edit it.

**Survey tools that are older than this skill. Reach for them before you write your own:**

```
src/RimMandrake/Utils/genome_scan.py         every XenotypeDef + GeneDef in the ACTIVE list -> JSON
src/RimMandrake/Utils/genome_matrix_build.py the genome register: every candidate xenotype, aligned by gene
src/RimMandrake/Utils/genome_art_cache.py    gene and xenotype icons OUT of AssetBundles (needs ~/.venvs/rimart/bin/python)
```

⚠️ `genome_matrix_build.py` picks its rows from `CANDIDATE_PACKS`. That table names the three donor packs, which are
off, and not our mod. Change the table before you trust a new register.

⚠️ `genome_art_cache.py` is the answer to "the icon does not exist on disk". Vanilla ships gene art inside Unity
bundles, so a `find` sweep reports most of Biotech's genes as art-less. That report is false: the sweep looked in the
wrong place. Full treatment in `reading-rimworld-graphics`.

⇒ **Knowledge that lives only in a script is invisible.** The next person who touches a xenotype then derives it again
by hand. If you learn something here, file it with `python3 src/RimMandrake/Utils/lessons.py add "…"`. A curation
session then writes it into this file.

Deploying is `rimworld-deploy`; looking at the art is `reading-rimworld-graphics`; spawning to check is `rimbridge`.
