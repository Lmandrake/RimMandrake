# ANCIENTS_AS_RAKATA_SPEC.md — the frozen sleepers are Rakatan, specified for build

## 🔴 RULED v1, IN FULL — owner, 2026-08-20

> *"Let's go all out for v1 here. 'Ancients' is so boring! Let's get us some precursor
> Rakata in cold storage for all this time..."*

⭐ **THIS REVERSES THE 2026-08-15 DEFERRAL.** `D30 (5)` recorded that the owner *declined*
to name `RimMandrakeRakata` as the ancient enemy, sent B61 to `design/V2_DREAMS.md`, and
ruled that the frozen Ancients ship vanilla. **All three of those are now dead.** The
Rakata are named, B61 returns to v1, and the sleepers are Rakatan.

⇒ **BOTH halves are in, not just the appearance one.** R-A9 previously held labels back as
the owner's separate call; he has now made it, and made it maximally:
| half | status |
|---|---|
| **appearance** — six pawn kinds carry `RimMandrakeRakata` | ✅ v1 |
| **naming** — the Rakata ARE the ancient enemy, in the fiction and on the label | ✅ v1 |

### 🔑 What naming them does — it unifies three threads that were separate

This is why the ruling is worth more than a reskin:
1. **`the_forgotten_war.md` R-W5** — the ancient sleepers in the vaults are **the same people
   who built the Utinni**, and she was one of the vessels that helped start this world.
   ⇒ **The player flies a ship built by the people they are cracking out of cold storage.**
2. ⛔ ~~**R-W3** — the ancient enemy's weapon was self-replicating flesh… ⇒ **The Rakata are
   now that author.**~~ 🔴 **WRONG, AND CORRECTED BY THE OWNER 2026-08-20, SAME DAY:**
   > *"The Rakata were nearly wiped out by their bioweapon-wielding ASSAILANT, they didn't
   > release the bioweapons themselves. They were terraformers and mega builders."*
   ⇒ **The Rakata are the VICTIMS, not the perpetrators.** The self-replicating flesh in the
   vaults — and its residue in the poison forest, the mycotic jungle and the gelatinous
   superorganism — belongs to **whoever attacked them**, and that assailant remains
   **UNNAMED**. `hydrology_and_fire_ecology.md` R-H8's blank stays blank.
   ⚠️ DECIDE asserted the opposite and propagated it into four files before the correction.
   Struck in place rather than deleted, because the wrong version is the intuitive one and
   someone will reach for it again.
3. **`FACTION_SPEC.md` §8 / the Geonosian plateau** — the splinter hive worships **Rakatan
   ruins** that revealed the true origins of the subsolar Founder machinery, and has been
   trying to commune with its AI for nine years. ⇒ **They are praying to the builders of the
   thing in the vaults.**

⇒ **One name closes the Utinni's origin and the plateau cult's god.** ⛔ It does **NOT**
close the bioweapon's author — that is a separate and still-open question.

### 🔑 WHO THE RAKATA ARE — owner, 2026-08-20

**Terraformers and mega-builders.** They made this world habitable, they brought the metal
down from the asteroids, they built the works the Geonosians now worship, and they built the
*Utinni*. Then **something attacked them with self-replicating flesh and nearly finished
them**, and what survives is in the caskets.

### 🔴 RULED — the names, owner 2026-08-20

> *"**Rakata** is the ancient's name for themselves. Modern people on this planet just call
> them **the Forgotten** or **the Forsaken**, and thus their mechanoids are the Forsaken or
> Forgotten Arsenal."*

⇒ **One people, two names: `Rakata` is the ENDONYM, `the Forsaken` / `the Forgotten` is the
EXONYM.** DECIDE had offered this as a guess; it is now ruled.
🔑 **Which settles the Arsenal's ownership.** The Forsaken Arsenal is **Rakatan** — the
victims' own machines, still fighting a war whose other side left no trace.
⚠️ **Register rule for all authored text:** nobody alive on this planet says "Rakata" except
the Rakata. **A Jawa, a Hutt factor or an Imperial clerk says *the Forsaken* or *the
Forgotten*.** The word `Rakata` in a modern mouth is a scholar's word, or a sleeper's.

⇒ **The campaign's shape, restated:** the Jawa are scavenging the corpse of a terraforming
project, its makers are asleep in boxes, **and the weapon that killed them is still running
in the biomes.**

### ⚠️ AND THE MECHANISM IS STILL NOT A FACTION RESKIN

R-A7 below stands unchanged and is the reason this is cheap: **the `Ancients` faction is not
touched.** Vanilla `Ancients` cannot host a faction — that is why the Ascendant Helix was
authored fresh rather than reskinned. Ancient sleepers are not a faction you meet, they are
**cryptosleep caskets you open**, so the pawn kinds' xenotype is the entire surface.
⛔ Do not touch `hidden`, `settlementGenerationWeight` or `canMakeRandomly`.


DECIDE owns this spec; **BUILD owns the implementation.** Written 2026-08-15 at
the owner's instruction, immediately after `the_forgotten_war.md` R-W2/R-W3/R-W5
landed.

**The fiction, already decided and not up for relitigation:**

- `the_forgotten_war.md` **R-W2 ③** — one of the three things inside a Forsaken
  vault is **frozen Ancients, still in cryptosleep, still believing a war is on.**
  They are hostile because nobody ever told them it was over.
- `the_forgotten_war.md` **R-W5** — those sleepers are **the same people who built
  the Utinni**, and she was one of the *initiators* that helped start this world.
  A woken Ancient who sees the ship sees an initiator with the wrong crew aboard.
- **Owner, 2026-08-15:** those precursors are the **Rakata**. R-W3's proposal is
  now a ruling.

⇒ **So every ancient soldier the player thaws out of a casket must LOOK Rakatan.**
Today they generate as ordinary baseline humans, and the entire emotional payload
of R-W2 ③ lands on a pawn indistinguishable from a pirate. This spec closes that
gap and nothing else.

🔴 **This is an APPEARANCE change to PAWNS. It is not a faction change, it is not a
balance change, and it is not new content.** Every ruling below is written to keep
it that way.

---

## R-A1 · The xenotype is `RimMandrakeRakata` — and it EXISTS. ⚠️ TABLE CORRECTED 2026-08-20

🔴 **THIS SECTION'S TABLE WAS CORRUPTED BY A GLOBAL RENAME AND CONTRADICTED ITSELF.** It
carried two rows both labelled `RimMandrakeRakata`, one saying ✅ exists and one saying
🔴 does not exist anywhere — because a find-replace pass normalised the OLD defName
(a `BTD_*` reference) into the new one and collapsed a real before/after comparison into
nonsense. The heading said the def does not exist. **It does.**

✅ **MEASURED 2026-08-20, on disk AND in the deployed mod folder:**
`RimMandrakeRakata` (XenotypeDef) · `RimMandrakeRakata_Kind` (PawnKindDef) ·
`RimMandrake_RakatanHead` (GeneDef) · `RimMandrake_Rakatan` (HeadTypeDef) — all present in
`src/Jawa/RimMandrake_StarWarsRaces/` **and** in
`...\Steam\steamapps\common\RimWorld\Mods\RimMandrake_StarWarsRaces\`.
🔑 **It exists because of the owner's 2026-08-15 strip ruling** — Rakata was one of the six
species the generator skipped for an unresolvable gene (`OuterRim_ForceInsensitive`), and
*"remove any genes that aren't supported and build the species without"* is what brought it
back. ⚠️ It is also one of the **six species that exist nowhere but our own output**
(`queue/DECIDE.md`, `...4f81c9`) — **a regenerate that drops it by name kills this feature.**

⛔ The historical table is left below, struck, because the `FACTION_SPEC.md` R27 broken-
reference finding at the end of it is real and still owed. Read it for that, not for whether
the def exists.

~~

**Measured 2026-08-15 against the live def dump**
(`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs\`).

| defName | status |
|---|---|
| `RimMandrakeRakata` | ✅ **exists**, label "Rakata", from our own mod **RimMandrake - Star Wars Races** (`mandrake.starwarsraces`), which is ACTIVE in `ModsConfig.xml` |
| `RimMandrakeRakata` | 🔴 **DOES NOT EXIST — in any def type, anywhere in the dump.** `grep -r` across every `defs\*.json` returns zero hits. (Control: `RimMandrakeRakata` hits 7 files, so the grep works.) Every `BTD_*` def still in the dump belongs to a gravship mod — `BTD_GravEngine`, `BTD_DownedGravship` — and is unrelated |

The complete set of Rakata-named defs in the live game is: `RimMandrakeRakata`
(XenotypeDef) · `RimMandrakeRakata_Kind` (PawnKindDef) · `RimMandrake_RakatanHead`
(GeneDef) · `RimMandrake_Rakatan` (HeadTypeDef), plus three Outland-generated
implanter / ascension / morphosis defs.

🔴 **`FACTION_SPEC.md` R27 therefore carries a broken reference.** Its Ascendant
Helix row lists `RimMandrakeRakata` among eight `BTD_*` xenotypes, and
`the_forgotten_war.md` R-W3 names `RimMandrakeRakata` as the enemy species. **That name
resolves to nothing.** A `xenotypeChances` entry naming a def that does not exist
is a silent discard — the Helix simply never fields a Rakata and no error says so.

⚠️ **This is a DECIDE-owned defect in a DECIDE-owned document and DECIDE fixes
it**, not BUILD. Two follow-ups, both DECIDE's:

1. `FACTION_SPEC.md` R27 — the Ascendant Helix row must read `RimMandrakeRakata`,
   and its `MayRequire` becomes `mandrake.starwarsraces`, **not**
   `btd.xenotyperemix.starwars`.
2. `the_forgotten_war.md` R-W3 — the same substitution in prose.

📌 **The general lesson, because it will recur:** the Star Wars Races mod was built
to *own* these species outright so the three colliding donor packs could be
switched off. Its defNames are `RimMandrake*`, not `BTD_*`. **Every `BTD_*` name
still sitting in a spec is now suspect** and should be checked against the dump
before anything is built from it. That audit is DECIDE's and is out of scope here.

⇒ **BUILD writes `RimMandrakeRakata` and nothing else.** If BUILD finds a
`RimMandrakeRakata` anywhere while working, it is a bug to report, not a name to use.

## R-A2 · Scope — six pawn kinds, in two tiers

**Mandatory. Do these or the item is not done:**

| defName | source mod | label today | why |
|---|---|---|---|
| `AncientSoldier` | **Core** | ancient soldier | 🔴 The one that matters. This is what a cryptosleep casket and an ancient danger actually spawn |
| `AncientSoldier_Leader` | **Odyssey** | ancient captain | Odyssey is active; leaders spawn alongside the soldiers and a human captain leading Rakatan troops is worse than doing nothing |

**Also in scope, guarded:**

| defName | source mod | label today | combatPower |
|---|---|---|---|
| `AncientSoldierBoss` | Ancient urban ruins | ancient special unit | 225 |
| `AncientSoldierBossN` | Ancient urban ruins | ancient special unit | 225 |
| `AncientMallGuards` | Ancient urban ruins | "Fashion guy" | 425 |
| `AncientSlaughter` | Ancient urban ruins | slaughter | 525 |

**Ruling: the four "Ancient urban ruins" kinds ARE in scope.** The reasoning, so it
is not reopened:

- All four carry `defaultFactionDef AncientsHostile` — **the same faction, the same
  fiction, the same encounters.** They are not a separate species of enemy; they
  are the same sleepers with better gear.
- The mod (`xmb.ancienturbanruins.mo`) is ACTIVE and its ruins are a headline
  feature of the campaign's ancient layer. Leaving them out produces a room where
  two pawns are Rakatan and four are human, which reads as **a bug, not variety**.
- The cost of including them is four more xpaths in the same file.

⚠️ **They are guarded on their mod, per R-A6.** If Ancient urban ruins is ever cut,
those four operations must no-op silently and the two mandatory ones must still
apply. A single patch file that fails wholesale when one optional mod leaves is
not acceptable.

**Explicitly OUT of scope**, and do not touch them:

- `ABYautja_Ancient`, `ABYautja_AugmentedAncient`, `BS_Troll_Simple_Ancient`,
  `QP_AncientShaman`, `VRE_AncientFungoid`. These match the string "Ancient" and
  are **unrelated content** — Yautja, trolls, a dungeon shaman, a fungoid. Nothing
  about the Forsaken war touches them.
- Every mechanoid. The Forgotten Arsenal is machines; R-W2 ① is a separate thing
  and has its own document.
- Anything wearing the `Ancients` *faction* name. See R-A7.

## R-A3 · Mechanism — force the xenotype on the pawn kind, at 100%

`PawnKindDef.xenotypeSet` is the field. Two things must be true together, and
**one without the other leaves a pawn that is only sometimes Rakatan:**

1. **`RimMandrakeRakata` at chance `1.0`**, alone in the set.
2. **`useFactionXenotypes` set to `false`** on the same kind.

**Why (2) is not optional.** All six kinds currently carry
`useFactionXenotypes: true`, which falls the generator through to the FACTION's
xenotype set whenever the kind's own set does not produce a hit. And measured
live, that fallback is **not empty**:

| faction | xenotypeSet today |
|---|---|
| `Ancients` | `DV_Avaloi` at **0.15** |
| `AncientsHostile` | `DV_Avaloi` at **0.10** |

⚠️ **Neither of those is vanilla.** `det.avaloi` is injecting its own species into
both hidden Ancient factions, so today roughly one ancient soldier in ten already
generates as an Avaloi. Setting our chance to `1.0` should shadow it, but the
generator's precedence between a kind's set and a faction's set is **assumed, not
measured**, and this spec will not rest a visible campaign beat on an assumption.
Setting `useFactionXenotypes false` removes the question entirely and costs
nothing.

📌 **What the numbers mean:** a `xenotypeChances` list whose chances sum below 1
leaves the remainder to fall through — to the faction set, or to `Baseliner`.
`1.0` is the only value that means *always*. Do not write `0.95` "for variety";
variety here is a bug.

## R-A4 · 🔴 TWO XML TRAPS, AND BOTH HAVE ALREADY SHIPPED BROKEN IN THIS REPO

**This is the most dangerous section in the spec. Read it before writing a line.**

### Trap 1 — `xenotypeChances` is DICTIONARY-KEYED. `<li>` is fatal.

The element name **IS** the xenotype defName. The `<li><xenotype>…</xenotype>` form
is not a stylistic alternative — it makes `XenotypeChance.LoadDataFromXmlCustom`
call `ParseFloat` on a null string, and **the entire enclosing Def is discarded.**

This is **queue item B56**, found in the 2026-08-15 cold load: five authored Jawa
FactionDefs were dead on arrival for exactly this reason, and it also generated
~98,000 lines of log noise.

```xml
❌ <li MayRequire="…"><xenotype>RimMandrakeRakata</xenotype><chance>1.0</chance></li>
✅ <RimMandrakeRakata MayRequire="mandrake.starwarsraces">1.0</RimMandrakeRakata>
```

`MayRequire` is an attribute and rides on the keyed element unchanged.

🔴 **`FACTION_SPEC.md` R27's own worked example uses the `<li>` shape.** It is
wrong, it is what caused B56, and **BUILD must not copy it.** Vanilla's own
`PawnKinds_Spacer.xml` is the authority — it writes
`<Highmate MayRequire="Ludeon.RimWorld.Biotech">0.03</Highmate>`.
DECIDE owes a correction to R27's snippet; that is tracked with R-A1's fixes.

### Trap 2 — a child's list is APPENDED to its parent's, not substituted

`FACTION_SPEC.md` **R24a** and **R27**. Inheritance resolves **after** patches, so
a `<xenotypeSet>` written by a patch onto a child def gets the parent's entries
appended to it. R27 records that this already shipped live once.

**It is live here, not hypothetical.** Measured in
`Ancient urban ruins\1.6\Defs\PawnKindDefs\PawnKinds_Boss.xml`:

- `AncientSoldierBoss` is declared `<PawnKindDef Name="AMBossBase">` — it is
  **both a concrete def and the parent of another one** — and it carries
  `<Neanderthal MayRequire="Ludeon.RimWorld.Biotech">0.03</Neanderthal>`.
- `AncientSoldierBossN` is `<PawnKindDef ParentName="AMBossBase">` and declares no
  set of its own. It inherits that Neanderthal 3%.

⇒ **Patch `AncientSoldierBossN` without `Inherit="False"` and you get 97% Rakatan,
3% Neanderthal.** Not a crash, not a log line — a pawn that is *sometimes* right.
That is the failure mode this spec exists to prevent.

**Write `Inherit="False"` on BOTH the container and the list.** On the two defs
that have no parent it is a harmless no-op; on `AncientSoldierBossN` it is the
entire fix. R27 puts it on `<xenotypeSet>` only; the list actually being appended
is `<xenotypeChances>`, so put it on both rather than reason about which one the
resolver reads.

### The correct shape, in full

```xml
<xenotypeSet Inherit="False">
  <xenotypeChances Inherit="False">
    <RimMandrakeRakata MayRequire="mandrake.starwarsraces">1.0</RimMandrakeRakata>
  </xenotypeChances>
</xenotypeSet>
```

### The correct operation — Remove-then-Add, not Add

Two of the six (`AncientSoldier`, `AncientSoldier_Leader`) have **no
`<xenotypeSet>` node in their source XML at all**. Three of the others do. And a
third party is already patching one of them — `AncientSlaughter` resolves live to
`Neanderthal 0.03` + `Hussar 0.4` + **`XylTitan 0.025`**, and `XylTitan` is not in
that mod's file, so `xylthixlm.races.titan` is adding it by patch.

⇒ A bare `PatchOperationAdd` produces a duplicate node on three of six and loses
races against another mod's patch. **Use a `PatchOperationSequence` per kind:**

```xml
<Operation Class="PatchOperationSequence">
  <operations>
    <li Class="PatchOperationRemove">
      <xpath>Defs/PawnKindDef[defName="AncientSoldier"]/xenotypeSet</xpath>
      <success>Always</success>
    </li>
    <li Class="PatchOperationAdd">
      <xpath>Defs/PawnKindDef[defName="AncientSoldier"]</xpath>
      <value>
        <xenotypeSet Inherit="False">
          <xenotypeChances Inherit="False">
            <RimMandrakeRakata MayRequire="mandrake.starwarsraces">1.0</RimMandrakeRakata>
          </xenotypeChances>
        </xenotypeSet>
        <useFactionXenotypes>false</useFactionXenotypes>
      </value>
    </li>
  </operations>
</Operation>
```

`<success>Always</success>` on the Remove is what makes the same block work for
both the two defs that have the node and the two that do not. **Remove
`useFactionXenotypes` the same way if a node for it already exists** — check each
of the six rather than assuming.

⚠️ **Load order is on our side and must stay that way.** `mandrake.jawa.patches`
sits near the end of `ModsConfig.xml`, after `mandrake.starwarsraces`,
`xmb.ancienturbanruins.mo` and `xylthixlm.races.titan`. Our Remove therefore runs
last and wins. If this patch is ever moved into a mod that loads earlier, the
Remove-then-Add stops being sufficient.

## R-A5 · The faction sets are the catch-all, and they have a live defect

**Recommended, and cheap:** also force `RimMandrakeRakata` on the two hidden
faction defs, `Ancients` and `AncientsHostile`, same shape and same
`Inherit="False"`.

Two reasons:

- **It catches pawn kinds this spec did not enumerate.** Any mod that adds an
  ancient-flavoured kind pointing at `AncientsHostile` inherits the look for free,
  because `useFactionXenotypes` defaults true across the board.
- **It removes the Avaloi.** `DV_Avaloi` at 0.10/0.15 is a third-party injection
  into vanilla's ancient factions that nobody in this project chose. It is a
  visible wrong-species bug in exactly the encounter this spec is about.

⚠️ **This is belt-and-braces, not the mechanism.** R-A3's per-kind patch is what
must work; if the faction half is dropped for any reason, the six kinds still
render correctly. Do not invert that dependency.

📌 `bs.xenotypespawncontrol` is active and its stated job is overriding xenotype
spawning. If the quicktest in **Verify** shows a non-Rakatan ancient after all six
patches read back clean in the dump, **that mod is the first suspect** — a runtime
override leaves the def dump looking perfect.

## R-A6 · Guarding — and a guard that "passes" proves nothing

**Every operation is wrapped so the mod degrades safely when a donor is absent.**

| what is guarded | on what | why |
|---|---|---|
| the `RimMandrakeRakata` entry itself | `MayRequire="mandrake.starwarsraces"` | without our races mod the xenotype does not exist; the entry must vanish, not resolve to nothing |
| the four Ancient urban ruins kinds | `PatchOperationFindMod` on `Ancient urban ruins` | their defs do not exist without it and the xpath would fail the whole file |
| `AncientSoldier_Leader` | `MayRequire="Ludeon.RimWorld.Odyssey"` on the operation | Odyssey is a DLC and may not always be on |

🔴 **The standing project fact, and it applies directly here:**
**`PatchOperationFindMod` and `PatchOperationConditional` both return `true` on no
match.** A guard that reports success has told you *the guard ran*, never *the
patch landed*. ⇒ **Do not verify this item by "no errors in the log".** The only
proof is the def dump reading back the xenotype set, and then a pawn on a map.
See **Verify**.

⚠️ `MayRequire` takes a **packageId**, `PatchOperationFindMod` takes the mod's
**display name**. They are not interchangeable and a swapped pair fails silently in
the friendliest possible way. `mandrake.starwarsraces` / `RimMandrake - Star Wars
Races`; `xmb.ancienturbanruins.mo` / `Ancient urban ruins`.

## R-A7 · This is NOT a faction change. The Ancients stay hidden.

`FACTION_SPEC.md` **R9**: vanilla `Ancients` is `hidden true`,
`settlementGenerationWeight 0`, `canMakeRandomly false`. **It cannot host a
faction** — that is precisely why the Ascendant Helix had to be authored from
scratch rather than reskinned onto it. Measured again 2026-08-15 and still true of
both `Ancients` and `AncientsHostile`.

⇒ **Nothing in this item makes the Ancients playable, visible on the world map,
diplomatically reachable, or a settlement-generating faction.** No world tile, no
relations, no goodwill, no faction icon, no leader. If a change starts to look like
that, it has left this spec.

⛔ **Do not touch** `hidden`, `settlementGenerationWeight`, `canMakeRandomly`,
`permanentEnemy`, `naturalEnemy`, or any relations field on either faction. R-A5's
faction patch touches **`xenotypeSet` and nothing else.**

## R-A8 · Appearance only — the encounter must play exactly as before

These pawn kinds are load-bearing for content the player will meet without
warning: **ancient danger rooms, cryptosleep caskets, ancient ruins, and quests
that spawn them.** A pawn kind is where gear, power and generation all live, so
the file being edited is one field away from a balance change.

⛔ **Do not alter**, on any of the six:

`combatPower` · `apparelMoney` · `apparelTags` · `apparelRequired` ·
`weaponMoney` · `weaponTags` · `techHediffsMoney` · `techHediffsTags` ·
`techHediffsChance` · `itemQuality` · `forcedTraits` · `disallowedTraits` ·
`backstoryFiltersOverride` · `backstoryCryptosleepCommonality` ·
`chemicalAddictionChance` · `maxGenerationAge` · `initialWillRange` ·
`initialResistanceRange` · `defaultFactionDef` · `race`

**The diff for each kind is exactly two things: a `xenotypeSet` and a
`useFactionXenotypes`.** Anything else in the diff is a defect.

⚠️ **One real risk to watch, and it is genetic, not editorial.** A xenotype is a
gene bundle, and genes carry stat offsets. `RimMandrakeRakata`'s 21 genes include
body-shape and appendage genes (`RimMandrake_Body_gaunt`, `Body_Thin`,
`Hands_Pig`, `Outland_WebbedFeet`) that may carry real modifiers to melee, work
speed or move speed. **`combatPower` is a static number and does NOT update to
match**, so an ancient soldier could become measurably weaker or stronger than the
85 points the raid generator is spending on it.

⇒ **BUILD reports the aggregate stat effect of the 21 genes** — read the GeneDefs'
`statOffsets` / `statFactors` / `capMods` and state the total in the queue item.
It is a two-minute read and it decides whether DECIDE owes a `combatPower`
follow-up. **BUILD does not change `combatPower` on its own initiative;** report
the number and DECIDE rules.

## R-A9 · 🟡 Labels — the owner's call, and NOT part of the build

> 🔴 **OVERTAKEN BY THE OWNER, 2026-08-20, and BUILT — read this before the section below.**
> He made the call this section reserved for him, the queue item put labels in scope, and
> `src/Jawa/Jawa_Patches/Patches/AncientsAreRakata.xml` ships them.
> ⭐ **But NOT as "Rakatan" — as "the Forsaken", and that is this section's own argument
> winning rather than losing.** His naming ruling the same day makes `Rakata` the ENDONYM
> and `the Forsaken` / `the Forgotten` the EXONYM, with *"the word Rakata in a modern mouth
> is a scholar's word"*. A pawn label is read by a player who is playing a Jawa, so the
> exonym is the correct register — **and it keeps the discovery intact, which is exactly
> what the case-against below was protecting.** The xenotype label still reads "Rakata" in
> the bio and gene tab for a player who goes looking.
> Shipped: `ancient soldier` → **Forsaken soldier** · `ancient captain` → **Forsaken
> captain** · `ancient special unit` ×2 → **Forsaken special unit**.
> ⛔ `AncientMallGuards` ("Fashion guy") and `AncientSlaughter` ("slaughter") are
> deliberately NOT renamed — renaming a joke label is authoring and is DECIDE's register
> call. Their xenotype is patched exactly like the other four.
> 🔑 **The "do not bundle it" instruction below was not ignored lightly.** It is one file,
> the label ops sit in the same per-kind sequence as the xenotype ops, and reverting them
> is deleting four `<label>` operations. A separate patch file touching the same six defs
> would have been the riskier arrangement, not the safer one.

**Flagged for the owner. Default is NO CHANGE, and BUILD ships that default.**

The pawn labels today are `ancient soldier`, `ancient captain`, `ancient special
unit`, `"Fashion guy"`, `slaughter`. The question is whether a thawed sleeper
should read as *"Rakatan soldier"* in the inspect pane and combat log.

**The case for changing them:** it names the enemy. R-W3's whole argument is that
the player brings the Rakata association for free — but only if the word is ever
shown. A pawn that merely *looks* strange is a mystery; a pawn labelled Rakatan is
a revelation, and R-W2 ③ is written as a revelation.

**The case against, and it is why the default is no change:**

- 🔴 **It leaks the answer.** The sleepers are supposed to be a discovery. The
  first casket a player cracks would announce the precursor species in a tooltip
  before any story beat has landed.
- **"Ancient" is the player-facing name of a whole content category** — ancient
  danger, ancient ruins, ancient junk, the vanilla quest line. Renaming the pawn
  desynchronises the pawn from the room it is standing in.
- The xenotype label already reads **"Rakata"** in the pawn's bio and gene tab, so
  a curious player can find it. The information is present without being announced.

⚠️ **If the owner rules to change them, it is a SEPARATE queue item**, because it
is a different kind of change (player-facing strings, which touch translation and
quest text) and it must not delay or complicate the appearance patch. Do not
bundle it.

## R-A10 · Where the file goes

`D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\AncientsAreRakata.xml` —
one new file, alongside the other 29 patches in that folder. **Do not edit an
existing patch file**; a self-contained file is one `git rm` from a clean revert
if the owner changes the ruling.

🔴 **Writing it is not deploying it.** The game reads
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches`. Run
`python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Jawa_Patches`,
read the plan, then `--apply`. Per the `rimworld-deploy` skill, refuse any file in
that plan that is not yours.

---

## The graphics question — does a Rakata actually RENDER?

**This half was investigated before the spec was written, because a patch that
correctly assigns an invisible xenotype is worse than no patch.**

📌 **The framing that matters, from `skills/reading-rimworld-graphics/SKILL.md`:**
**a XenotypeDef's appearance comes from its GENES, not its `iconPath`.** The icon
is a UI symbol in the xenotype panel and is unrelated to what stands on the map. A
xenotype with **no icon at all renders perfectly**. So "does `RimMandrakeRakata`
have an icon" is the wrong question and its answer proves nothing either way.

The right question is per-gene, and the genes split into three honest categories:

**Measured 2026-08-15 against the live def dump, the mod's own `Textures\` tree
(no `LoadFolders.xml` — the root `Textures/` is the only content dir) and the
extracted bundle index at `observed\inventory\bundle_textures\index.csv`.**

**Result: ✅ ALL 21 GENES RESOLVE. Nothing is missing.**

| category | genes | verdict |
|---|---|---|
| **head — appearance-bearing** | `RimMandrake_RakatanHead` | ✅ **REAL ART.** Forces `HeadTypeDef RimMandrake_Rakatan` (exists; `requiredGenes` points back at the gene — a clean two-way link), `graphicPath RimMandrakeSW/OR/Things/Pawn/Humanlike/Heads/Rakatan/Normal`, and all three sides are on disk: `Normal_south.png` 20.5 KB · `_east.png` 18.3 KB · `_north.png` 17.2 KB. `gender: None`, so one set is the complete set |
| **body — appearance-bearing** | `RimMandrake_Body_gaunt` | ✅ **REAL ART.** Custom render node + `fur RimMandrake_FurDef_gaunt`, which maps bodyType `Thin` to `RimMandrakeSW/SWX/Pawn/BodyType/Gaunt_{south,east,north}.png` (20.8 / 19.9 / 19.5 KB). `Body_Thin` forces Thin, so the custom Gaunt art is the one used — the pairing is deliberate |
| **skin colour** | `Outland_Skin_DeepOrange` · `Outland_Skin_Brown` · `Outland_Skin_PaleBrown` | ✅ **declares no texture, correctly.** All three are `skinColorOverride` — a colour applied to the existing body graphic. "No texture" is the healthy state here, not a gap |
| **restriction only** | `Hair_BaldOnly` (`hairTagFilter` Bald/whitelist) · `Beard_NoBeardOnly` (`beardTagFilter` NoBeard) | ✅ **declares no body art, by design.** They filter which other defs may be chosen. A missing texture here is not a thing that can exist |
| **shape / appendage, icon-only** | `Body_Thin` · `Hands_Pig` · `Outland_WebbedFeet` | ✅ icon resolves; no texture of their own (vanilla hands are not a render node) |
| **the remaining 12** | psychic, stat, diet, temperature, aggression, melee, reproduction genes | ✅ icon-only, and **all 12 icons resolve** — from Biotech, Royalty, Big and Small and Outland Genetics |

⇒ **"Declares no art" is the expected answer for most of the 21 and must NOT be
reported as "missing art."** Conflating the two is what invites someone to delete
working content — the skill calls this out and it is the trap that was avoided
here.

**Two supporting findings worth recording:**

- ⚠️ `RimMandrake_FurDef_gaunt` carries `noGraphic: true`, which looks alarming and
  is not. **All 30 FurDefs in the entire loaded stack carry it**, including
  Biotech's own and those of Saurid, Phytokin, Yautja and Alpha Genes — every one
  of which renders. Do not chase this.
- The xenotype's own `iconPath` also resolves
  (`RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_Rakata.png`, 20 KB) — but per
  the skill this proves nothing about the pawn. It is recorded only so nobody
  re-derives it.
- There is also a `RimMandrakeRakata_Kind` PawnKindDef in the dump. **We are not
  using it** — this spec forces a xenotype onto the vanilla Ancient kinds so their
  gear, power and spawn behaviour survive untouched (R-A8). Swapping the pawn kind
  outright would change all three.

🔴 **What could NOT be proven offline, stated plainly, three items:**

1. The PNGs were sized, not opened. Non-trivial file size is not proof of a
   non-transparent, correctly-aligned sprite.
2. Whether Big and Small's `PawnRenderNode_FurSkinClr` worker actually draws given
   `noGraphic: true` is **C# behaviour inferred** from 29 other shipping races
   sharing the flag. Strong, not proven.
3. The dump is one snapshot of one load. A late PatchOperation from another mod
   could still alter these defs.

**The definitive test is spawning one and looking at it**, and the
`reading-rimworld-graphics` skill says so in as many words: *"the cheapest
disambiguation is to spawn one and look… a single spawned pawn settled this after
an entire file-based analysis reached the wrong conclusion twice."*

⇒ **The graphics half is GREEN on disk, and the one remaining condition is the
quicktest below.** BUILD spawns a Rakata via the bridge and looks at it before
declaring done. That is ~90 seconds and it is not optional.

---

## What BUILD owes

1. **One new patch file**, `AncientsAreRakata.xml`, in `Jawa_Patches\Patches\`,
   covering the six kinds of R-A2 and — per R-A5 — the two faction defs.
2. **The XML shape of R-A4 exactly**: dictionary-keyed entries, never `<li>`;
   `Inherit="False"` on both `xenotypeSet` and `xenotypeChances`;
   Remove-then-Add sequences with `<success>Always</success>`.
3. **`useFactionXenotypes false`** on all six.
4. **Guards per R-A6**, with `MayRequire` taking packageIds and
   `PatchOperationFindMod` taking display names.
5. **A validator pass** — `python3 skills/rimworld-modding/scripts/validate_patch.py`
   on the new file, pointed at the mod ROOT, with **both `--live` and `--defs`**.
6. **Deploy** per R-A10 and confirm the file landed in the Steam Mods copy.
7. **The gene stat report of R-A8** — aggregate `statOffsets`/`statFactors`/
   `capMods` across the 21 genes, written into the queue item. Do not act on it.
8. **The spawn-and-look of the graphics section**, before declaring done.

**BUILD does NOT:** change any label (R-A9), change `combatPower` (R-A8), touch any
faction field other than `xenotypeSet` (R-A7), or use the name `RimMandrakeRakata` (R-A1).

## Verify

🔴 **A quicktest, ~90 s. Do NOT call a cold load for this** — nothing here needs
worldgen and the project's scarcest resource is the ~25-minute restart. Use the
`rimworld-debug-testing` route: throwaway dev colony, bridge, destroy after.

**Tier 1 — the def actually changed.** Refresh the def dump
(`python3 src/RimMandrake/Utils/refresh.py`) and read back:

- `AncientSoldier.xenotypeSet.xenotypeChances` == exactly one entry,
  `RimMandrakeRakata` at `1.0`. **Not two.** A second entry means R-A4 trap 2 bit.
- `AncientSoldier.useFactionXenotypes` == `false`.
- The same for `AncientSoldier_Leader` and the four guarded kinds.
- 🔴 **`AncientSoldierBossN` is the canary.** It is the one with a parent carrying
  `Neanderthal 0.03`. If its list has one entry, `Inherit="False"` worked. If it
  has two, the patch shipped the exact bug R27 already shipped once.
- `Ancients` and `AncientsHostile` no longer list `DV_Avaloi`.

**Tier 2 — a pawn generates as one.** Spawn several `AncientSoldier` via the
bridge. Every one is Rakata; none is Baseliner, Neanderthal, Hussar or Avaloi.
Spawn ≥5 — a 3% contaminant will not show in a sample of one, and *sometimes
Rakatan* is the failure this spec is built to catch.

**Tier 3 — it RENDERS, and this is the one that cannot be skipped.** Look at the
spawned pawn, on the map, with eyes:

- The head is the Rakatan head, not a vanilla human head and not a magenta/blank
  placeholder.
- The skin reads as one of the three browns/oranges, not default flesh.
- The body silhouette is the gaunt/thin one.
- Screenshot it and put the path in the queue item. **A texture existing on disk is
  not this check** — per the skill, a blank-rate metric cannot detect a wrong
  picture.

**Tier 4 — nothing else moved.** In the same quicktest:

- The spawned soldier still carries a gun and armour of the same apparel tags —
  the gear roll is untouched.
- An ancient danger room opens and populates normally.
- Zero `Exception loading def from file AncientsAreRakata.xml` in `Player.log`, and
  zero `Could not resolve cross-reference` naming `RimMandrakeRakata`.
- ⚠️ **Absence of errors is NOT a pass on its own** — see R-A6. It is a
  prerequisite to reading Tier 1.

**Done means:** Tier 1 clean on all six plus both factions, Tier 2 clean on ≥5
pawns, a screenshot from Tier 3, Tier 4 clean, and the gene stat number reported.

## Criteria

The player cracks an ancient cryptosleep casket and what climbs out is visibly
**not human** — and is recognisably the same species as whatever else the campaign
eventually shows of the precursors. The encounter plays exactly as it did before.
