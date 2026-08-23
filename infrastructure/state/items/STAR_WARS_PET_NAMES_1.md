## spec

🔴 **Owner, 2026-08-23, verbatim:** *"Spec and add a build item to generate
lore-accurate and humorous Star Wars pet names as a generator when pets are
created or tamed. That's important immersion."*

### The mechanism — verified against the 1.6 source, not assumed

**The def type is `RulePackDef`** (`Source/Verse/RulePackDef.cs`). It holds
`public List<RulePackDef> include;` and `private RulePack rulePack;`.

**`RulePack` is a PLAIN class — there is NO `LoadDataFromXmlCustom` on it**
(`Source/Verse/Grammar/RulePack.cs`, whole class read: it defines only
`Rules`, `UntranslatedRules`, `PostLoad` and `GetRulesResolved`). Its fields are
`private List<string> rulesStrings`, `private List<string> rulesFiles`,
`private List<Rule> rulesRaw`, `public List<RulePackDef> include`. Because these
are ordinary `List<T>`, ⭐ **`<li>` is CORRECT and REQUIRED here** — this is not
the `BiomePlantRecord` / custom-loader trap. Confirmed against the shipped
`Defs/Core/RulePackDefs/RulePacks_Namers_Animals.xml`:

```xml
<RulePackDef>
  <defName>NamerAnimalGenericMale</defName>
  <include>
    <li>NamerAnimalUtility</li>
  </include>
  <rulePack>
    <rulesStrings>
      <li>r_name(p=6)->[NameAnimalUnisex]</li>
      <li>r_name->[exoticname]</li>
      <li>exoticname(p=2)->[AdjectiveBadass]</li>
    </rulesStrings>
  </rulePack>
</RulePackDef>
```

**The field on the race is `nameGenerator` / `nameGeneratorFemale`, both
`private RulePackDef`, on `RaceProperties`** (`Source/Verse/RaceProperties.cs:182-184`)
— i.e. `<race><nameGenerator>X</nameGenerator></race>` on a `ThingDef`.
⛔ It is **not** called `namerAnimal`, and it is **not** on `PawnKindDef`.
`RaceProperties.GetNameGenerator(Gender)` (line 414) returns `nameGeneratorFemale`
for females when non-null, else `nameGenerator`.

### 🔴 WHEN it fires — and the reason a RulePackDef patch ALONE will not do the job

| event | code path | which name you get |
|---|---|---|
| **Tamed** | `InteractionWorker_RecruitAttempt.DoRecruit` → `RecruitUtility.Recruit` → `Pawn.SetFaction` (`Source/Verse/Pawn.cs:4002`) → `Pawn.GenerateNecessaryName()` (`Pawn.cs:4180`) | 🔴 **`NameStyle.Numeric` only** — literally `"Dromedary 1"`. The RulePackDef is **never consulted.** |
| **Born / hatched / spawned into the player faction** | `PawnGenerator.GeneratePawn` (`Source/Verse/PawnGenerator.cs:897`, guarded `request.Faction != null && (Animal \|\| mech)`) → the same `GenerateNecessaryName()` | 🔴 **Numeric.** Same. |
| **Bond forms** (tamer/doctor/master, ~0.4–1 % per interaction) | `RelationsUtility.TryDevelopBondRelation` (`Source/RimWorld/RelationsUtility.cs:132`) → `PawnBioAndNameGenerator.GeneratePawnName(animal)` (`NameStyle.Full`) → `GenerateFullPawnName` → the `nameGenner` branch → `new NameSingle(NameGenerator.GenerateName(nameGenner, …))` | ✅ **This is the ONLY routine vanilla path that reads `race.nameGenerator`.** |
| **Scenario starting animal** | `ScenPart_StartingAnimal.cs:170`, same `Full` path | ✅ rulepack name |

🔑 **So the owner's request cannot be delivered by def XML alone.** Patching
`race/nameGenerator` changes the *bond* name and nothing else; the tame and birth
moments he named both land on `GenerateNecessaryName`, which hard-codes
`NameStyle.Numeric`. **A Harmony postfix is required for taming, and the same
postfix covers birth for free**, because both routes funnel through that one method.

⚠️ **`RaceProperties.nameOnTameChance` (line 186) is a trap.** It is declared and
`ConfigErrors` (line 509) warns *"can be named, but has no nameGenerator"* when it
is > 0 — but a case-sensitive search for `nameOnTame` across the whole decompiled
1.6 tree returns **only those two lines plus def XML**. **No code reads it.**
308 ThingDef rows in the current dump set it to `1` and it buys them nothing.
⛔ Do not "fix" this item by setting `nameOnTameChance` — it is vestigial.
(UNVERIFIED in the negative only in this sense: a third-party assembly could read
it via Harmony; vanilla does not.)

### Priority order inside `GenerateFullPawnName` — read it before choosing a hook

`PawnBioAndNameGenerator.GenerateFullPawnName` (`Source/RimWorld/PawnBioAndNameGenerator.cs:342`)
tries, in order: creepjoiner → xenotype nameMaker → **`pawnKindNameMaker`
(`PawnKindDef.GetNameMaker`)** → backstory nameMaker → **`nameGenner` (the race
`nameGenerator`)** → culture → `nameCategory`.
✅ **A `PawnKindDef.nameMaker` OUTRANKS the race namer.** Measured off the dump:
only **2** PawnKindDefs in the whole ~578-mod stack set `nameMaker`
(`guy762_DroidNamer_T3`, `guy762_HeroNamer_T3M4`), so nothing will shadow us —
but if BUILD later adds a Jawa animal PawnKindDef with a `nameMaker`, this item's
namer stops firing for it, silently.

### What already exists in this install (measured off the def dump, not grepped)

`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs.sqlite`,
`defs(def_type, json)`, reading `fields.race.nameGenerator`:

- **784 `RulePackDef`s total; 8 with "Animal" in the defName.**
- **2285 ThingDef rows set a race namer** — 1721 `NamerAnimalGenericMale`,
  **320 `SWAnimalNamerMale`**, 162 `NamerMech`, 22 `OuterRim_Namer_DroidGeneric`,
  12 `NamerAnimalHorrors`.
- ⭐ **`SWAnimalNamerMale` / `SWAnimalNamerFemale` already ship**, from
  **Star Wars Animal Collection (Continued)** (`mlie.starwarsanimalcollection`),
  `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3497316713\1.6\Defs\RulePack_Namers\RulePacks_NameMakers_Animals.xml`.
  Their shape is a `Rule_File` pointing at a text list:
  ```xml
  <rulePack>
    <rulesStrings><li>name->[a]</li></rulesStrings>
    <rulesRaw>
      <li Class="Rule_File"><keyword>a</keyword><path>SWAnimalNames/SWAnimalNamesMale</path></li>
    </rulesRaw>
  </rulePack>
  ```
  🔑 **A `Rule_File` `path` resolves through `Translator.TryGetTranslatedStringsForFile`**
  (`Source/Verse/Grammar/Rule_File.cs`), i.e. under `Languages/<Lang>/Strings/`, **not
  under `Defs/`** — verified on disk at
  `...\3497316713\Languages\English\Strings\SWAnimalNames\SWAnimalNamesMale.txt`.
  Those files hold **151 male / 152 female / 200 unisex** entries, and they are
  Star Wars *person* names (Aedalus, Ailyn, Amber, Ashes). **There is no creature
  register and no humour register anywhere in the stack.** That gap is this item.

### What to build

1. **One new `RulePackDef`**, `Jawa_NamerPetSW` (plus `Jawa_NamerPetSWFemale` only
   if BUILD wants gendered splits — the corpus below is deliberately unisex, so one
   def is enough and both `nameGenerator` and `nameGeneratorFemale` can point at it).
   Put the corpus in **`rulesStrings`** — `<li>` literals, no text files. Reason: it
   keeps the corpus in the repo under `src/`, diffable and reviewable, instead of in
   a Languages folder where nobody looks.
2. **A `PatchOperation`** setting `race/nameGenerator` and `race/nameGeneratorFemale`
   to it. Scope decided below.
3. **A Harmony postfix** so tame and birth actually use it (see hook note below).

### The ratio ruling — 2 lore : 1 humour

Implement it with grammar weights, not with code:

```xml
<li>r_name(p=6)->[loreName]</li>
<li>r_name(p=3)->[jokeName]</li>
```

`Rule` selection is weighted by `p=`, so 6:3 gives **≈67 % lore, ≈33 % humour**.

🔑 **Why two-thirds lore.** The lore register is the *texture* — it has to be the
thing you mostly see, or the setting stops feeling like Star Wars and starts
feeling like a joke mod. The humour register is *characterisation of the clan*: a
Jawa outfit that names one animal in three "Warranty Void" reads as scrappers with
a sense of trade; one in two reads as memes. One in five and the joke never lands
in a normal playthrough. ⚠️ **This is a ruling, not a preference — if BUILD wants
to move it, move it in the def and say so here, do not hard-code a second ratio
anywhere else.**

### Corpus — 72 lore + 60 humour = 132 names

⚠️ **`NameGenerator.GenerateName` validates against `NameSingle.UsedThisGame`**
(`PawnBioAndNameGenerator.cs:378`) and retries **150 times** before it gives up and
logs `Could not get new name` (`Source/RimWorld/NameGenerator.cs`). A 60-name
corpus is exhaustible by a real menagerie; 132 is the floor, not the target.
Adding more later is a one-line `<li>` append.

⚠️ **Every output is passed through `GenText.CapitalizeAsTitle` →
`GenText.ToTitleCaseSmart`** (`Source/Verse/GenText.cs:497`), which capitalises the
first letter after every space, hyphen and `" '"` and **lowercases nothing**. So
`Head Of Security` stays `Head Of Security`, `as-is` becomes `As-Is`, and `M'aloo`
survives intact. Write them already cased as below and nothing surprises you.

#### Register A — lore-accurate (72)

Creatures: `Bantha` `Nerf` `Womp` `Massiff` `Vornskr` `Dewback` `Ronto`
`Tauntaun` `Mynock` `Anooba` `Nexu` `Blurrg` `Eopie` `Shaak` `Varactyl` `Fathier`
`Gundark` `Kaadu` `Narglatch` `Scurrier` `Happabore` `Luggabeast` `Steelpecker`
`Ysalamir` `Krayt` `Rancor` `Sarlacc` `Reek` `Acklay` `Porg` `Convor` `Voorpak`

Worlds: `Jakku` `Lothal` `Endor` `Hoth` `Dantooine` `Ryloth` `Sullust` `Mantell`
`Kessel` `Bespin` `Yavin` `Malastare` `Geonosis` `Mustafar` `Utapau` `Crait`

Huttese and Jawaese: `Achuta` `Sleemo` `Poodoo` `Chuba` `Peedunkee` `Wanga`
`Bargon` `Koona` `Mookee` `Skocha` `Utinni` `Ootini` `Togo` `M'aloo`

Droid designations: `Gonk` `Artoo` `Threepio` `Arfive` `Beebee` `Deetoo` `Emtee`
`Kaytoo` `Chopper` `Treadwell`

#### Register B — humour, in the clan's own voice (60)

⚠️ **The register is TRADERS AND SCRAPPERS, not memes.** Every one of these is
something a Jawa would actually write on a sales chit or a salvage tag. If a
candidate would be funny in any game, it does not belong here.

Warranty and sales patter: `Warranty Void` `Some Assembly` `As-Is` `No Refunds`
`Third Owner` `Mostly Working` `Fully Functional` `Slight Damage` `Runs Fine`
`Only Driven Once` `Two Careful Owners` `Sold As Seen` `Best Offer` `Final Sale`
`Restocking Fee` `Bulk Discount` `Trade-In` `Free With Purchase` `Buyer Beware`
`Certified Preowned`

Ironic grandeur on a small animal: `Chief Financial Officer` `The Management`
`Senior Partner` `Regional Manager` `Head Of Security` `Quality Control`
`Acting Supervisor` `The Auditor` `Board Member` `Majority Shareholder`
`Compliance` `Legal Department` `Procurement` `Logistics` `The Investor`

Droid-part and scrap puns: `Spare Parts` `Loose Wire` `Power Coupling`
`Bad Motivator` `Restraining Bolt` `Cracked Housing` `Load Bearing` `Duct Tape`
`Percussive Repair` `Sand In Everything` `Vaporator` `Coolant Leak` `Reboot`
`Firmware` `Undocumented Feature` `Known Issue` `Sold For Scrap` `Salvage Rights`
`Ballast` `Counterweight`

Inventory humour: `Utinni Surcharge` `Marked Up` `Inventory` `Overstock`
`Shrinkage`

### The Harmony hook

**Target: `Verse.Pawn.GenerateNecessaryName` (postfix).** Both the tame path and
the birth path call it, and nothing else does except back-compat. In the postfix:
guard on `__instance.RaceProps.Animal` (⛔ **not** mechanoids — `GenerateNecessaryName`
also fires for Biotech mechs), on `__instance.Faction == Faction.OfPlayer`, and on
`__instance.Name == null || __instance.Name.Numerical`; then set
`__instance.Name = new NameSingle(NameGenerator.GenerateName(namer, x => !new NameSingle(x).UsedThisGame))`
where `namer` is `__instance.RaceProps.GetNameGenerator(__instance.gender)`.

⚠️ **`GenerateNecessaryName` is a five-line non-virtual method and the JIT may
inline it into `Pawn.SetFaction`.** Harmony does not error when its target was
inlined — **it silently does nothing**, which is exactly the failure class this
project keeps getting bitten by. If the verify below shows numeric names anyway,
the fallback target is a postfix on
`PawnBioAndNameGenerator.GeneratePawnName(Pawn, NameStyle, string, bool, XenotypeDef)`
guarded on `style == NameStyle.Numeric && pawn.RaceProps.Animal` — a much larger
method, far less inline-prone.

✅ **Leaving the bond path alone is correct.** It already calls the `Full` path and
will pick the new namer up from `race/nameGenerator` with no code at all.

### Scope of the patch

Decide and record which animals get the Jawa namer:
- **Recommended:** the ~320 `SWAnimalNamerMale` ThingDefs from Star Wars Animal
  Collection **plus** vanilla desert-plausible tameables the clan will actually
  keep. ⛔ Do **not** blanket-patch all 1721 `NamerAnimalGenericMale` rows — you
  would rename every animal on the planet including hostile fauna nobody tames.
- A `PatchOperationConditional` on `race/nameGenerator[text()="SWAnimalNamerMale"]`
  is the clean selector. ⚠️ **Remember a patch that matches nothing logs nothing**
  — pair it with a `success="Always"` wrapper only if you have already proven the
  match count another way.

## verify

**Offline, no game load — this is a `--needs offline` item:**

1. `python3 skills/rimworld-modding/scripts/validate_patch.py <the new patch> --defs …`
   passes, and the new `RulePackDef` parses.
2. `python3 src/RimMandrake/Utils/refresh.py`, then query the dump:
   `Jawa_NamerPetSW` exists as a `RulePackDef` and its `fields.rulePack.rulesStrings`
   holds **132** name rules plus the `r_name` weighting rules.
   🔴 **Count it by querying `defs.sqlite`, never by `grep`/`strings`/`wc`** — see
   `infrastructure/state/BUILDABLE.md`.
3. Same query, `ThingDef` rows: the count whose `fields.race.nameGenerator ==
   "Jawa_NamerPetSW"` matches the number the patch intended, and
   `SWAnimalNamerMale`'s count has dropped by exactly that much. ⚠️ A patch that
   matched nothing shows up here as "still 320" and nowhere else.
4. `node --check` is irrelevant here; ignore.

**In game (a ~90 s quicktest on the minimal mod list, not a cold load):**

5. Dev mode → spawn a tameable → `Debug actions ▸ Tame` (or the debug tame tool).
   The message must read **"tamed and named <a corpus name>"**, not
   `Dromedary 1`. 🔑 **This is the whole item — if it says `Dromedary 1`, the
   Harmony patch was inlined away and nothing else you checked matters.**
6. Spawn a player-faction animal newborn (`Debug ▸ Spawn pawn` with the player
   faction) — same test, same expectation.
7. `Debug output ▸ Text generation ▸ Name generators` (`DebugOutputsTextGen.cs:342`)
   renders sample output for every `RulePackDef` — use it to eyeball 40 rolls of
   `Jawa_NamerPetSW` and confirm the mix looks roughly 2:1.

## criteria

- 🔴 **LOOK AT IT.** Tame five animals in a quicktest. Roughly three should carry
  a Star Wars creature/world/Huttese name and roughly two a trade-chit joke. All
  five must be *readable as names* — no `ErrorName`, no `Filestring`, no
  `Dromedary 1`.
- The humour must read as **this clan**: a Jawa scrapper's sales patter. If a
  reviewer can't tell the joke names came from a scavenger outfit specifically,
  the register failed even if the strings parsed.
- No red errors at load referencing the new `RulePackDef` or the patch.
- The bond message ("MessageNewBondRelationNewName") still produces a sensible
  name — the bond path is untouched and must stay untouched.
- ✅ Closing this item means the owner can tame something and laugh. Nothing less.

## Watch out

- 🔴 **The single biggest way this ships broken: the def work all passes and the
  animal is still called `Dromedary 1`.** Every offline check in `## verify` can
  go green while the tame moment — the thing the owner actually asked for — is
  unchanged, because tame naming does not read the RulePackDef at all. **Do the
  in-game tame test.**
- ⚠️ **Harmony on an inlinable method fails silently.** See the fallback target
  above. Do not conclude "the patch is applied" from a log line saying the mod
  loaded.
- ⚠️ **`<li>` is right here but wrong one field over.** `rulesStrings`,
  `rulesFiles`, `rulesRaw` and `include` are all plain lists and take `<li>`.
  If a future edit reaches for a `LoadDataFromXmlCustom` field elsewhere in the
  same file, an `<li>` there discards the **whole def**, silently — see
  `infrastructure/state/facts/` and the `BiomePlantRecord` precedent.
- ⚠️ **Load order:** the patch targets ThingDefs owned by
  `mlie.starwarsanimalcollection`. If our mod loads before it, the xpath matches
  nothing and **logs nothing**. Put it after that mod, and prove the match count
  from the dump (verify step 3), not from the absence of errors.
- ⚠️ **`nameGeneratorFemale` is checked FIRST for female animals**
  (`RaceProperties.GetNameGenerator`). Patch only `nameGenerator` and every female
  animal keeps the old namer. Patch both.
- ⚠️ **Corpus exhaustion is a real endgame bug.** `UsedThisGame` never releases a
  name, the retry loop is 150 deep, and then it logs an error and hands back a
  duplicate. A big colony over a long campaign will get there. If it becomes a
  problem the fix is combinatorial rules (`[adjective] [noun]`), not a bigger flat
  list.
- ⚠️ **`Jawa_NamerPetSW` must not collide with `SWAnimalNamerMale`'s keyword.**
  That def uses root keyword `name`; vanilla uses `r_name`. `NameGenerator` takes
  `rootPack.FirstRuleKeyword` — the keyword of the **first rule in list order** —
  so whichever keyword you choose, it must be the keyword of your first
  `rulesStrings` entry, or the resolver silently roots at the wrong symbol.
- ⛔ **`nameOnTameChance` is not the answer.** It has no reader in vanilla 1.6.
  Anyone who "fixes" this by setting it will believe they succeeded and will not
  have.

## notes

**from:** DECIDE, 2026-08-23. Mechanism verified against the decompiled 1.6 source
(`RaceProperties.cs`, `RulePack.cs`, `RulePackDef.cs`, `Rule_File.cs`,
`PawnBioAndNameGenerator.cs`, `RelationsUtility.cs`, `InteractionWorker_RecruitAttempt.cs`,
`RecruitUtility.cs`, `Pawn.cs`, `PawnGenerator.cs`, `NameGenerator.cs`, `GenText.cs`,
`LanguageWorker_English.cs`) and against the live def dump. Corpus written here,
not deferred.
