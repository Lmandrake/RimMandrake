# WORLDGEN_FACTION_CHECKLIST.md — the Configure Factions page, box by box

> ~250 lines were moved there on 2026-08-23, byte-unchanged. **Nothing was deleted.** What
> moved: the 2026-08-15 standing worldgen ruling (verbatim in `CLAUDE.md`), rulings R1 · R2 ·
> R4 · R5, the 'what you are doing and why' preamble, **Sections 1, 2 and 3 — the 21
> hand-untick rows** — and Sections 5 and 6.
>
> 🔴 **WHY THE 21 UNTICK ROWS ARE DEAD, and this is the whole reason for the split.**
> `src/Jawa/JawaFactionSlate/Patches/OnlyOurFactions.xml` zeroes `startingCountAtWorldCreation`
> on **48 FactionDefs** (verified 2026-08-23: 48 distinct defNames, 194 ops).
> `Page_CreateWorldParams.ResetFactionCounts()` adds each configurable faction
> `startingCountAtWorldCreation` times, so **a def at 0 is never added to the default roster**.
> The live capture `2026-08-23T07-12-04Z` measured all twelve of ours at 1 and all 29 others
> at 0. ⇒ **The page opens as exactly our twelve, one each, sorted to the top. There is
> nothing left to untick by hand.** Evidence:
> `infrastructure/state/items/FACTION_SCREEN_READY_TO_PAINT_1.md`.
> ⚠️ The four Yautja clans are not even reachable — their mod is absent from `ModsConfig.xml`.
> ⚠️ **`maxConfigurableAtWorldCreation` is deliberately NOT zeroed**, so a row is never deleted
> from the page and the owner can always add one back.
> ⛔ **The archive is history. Do not execute the untick list out of it.**

**What is LIVE below:** R3 (vanilla `Empire` *is* the Galactic Empire) · Section 4, the KEEPs
to confirm · Section 4b, our own factions · the tally.

⚠️ **The 2026-08-15 standing ruling that there is no worldgen feature in any version is in
`CLAUDE.md`**, verbatim, and in the archive. It has not changed.

## R3. ⭐ ADD vanilla `Empire` to KEEP — it is THE GALACTIC EMPIRE

**Owner's canon, 2026-08-13.** Vanilla `Empire` is reskinned as **the Galactic
Empire**, led by **Emperor Palpatine**. It is the campaign's **one permanent
enemy** and the thing that pursues the gravship.

🔴 **The "Fallen Dominion" and the two-Empire split are STRUCK from the design.**
There is no local or planetside Empire. Any earlier note describing a disgraced
local aristocracy is superseded and must not be acted on.

**Confirm vanilla `Empire` is present and its count is ≥ 1.** It is not on the
untick list, so it survives by default — confirm it anyway. ⚠️ **Its name is
generated**, so the world will not say "Galactic Empire" until a `fixedName`
patch lands. **Screenshot whatever it does say.**


> ⚠️ **R1, R2, R4 and R5 are cited by name in the rows below and now live in the archive** —
>
> 🔴 **Two surviving KEEPs are among the 48 defs `OnlyOurFactions.xml` zeroes** —
> `JDSCIS_CIS_Faction` and the quest-critical `guy762_KotORFaction_RogueDroids`. Their rows are
> on the page (`maxConfigurableAtWorldCreation` is untouched) but they **default to 0**, so the
> owner must set each himself or they do not exist. `FACTION_SLATE_ZEROES_KEEPS_1`.

## SECTION 4 — KEEP. Confirm each is present and its count is ≥ 1 before you commit.

These are the Star Wars factions the world exists for. **Do not just leave them alone —
look at each one and confirm it is there**, because one of them was silently absent last
time.

| ✔ | in-game label | defName | mod | note |
|---|---|---|---|---|
| ~~☐~~ | ~~**binary star raiders**~~ | ~~`OuterRim_BinaryStarRaiders`~~ | Outer Rim - Core (2919227155) | ⛔ **RETIRED FROM KEEP 2026-08-21 (R5).** Not hidden, `settlementGenerationWeight 1` ⇒ it places holdings on a planet whose **72 settlements are already hand-placed for 13 factions**. Absent is now the desired outcome; do not restore it at the screen. |
| ☐ | **Confederacy of Independent Systems** | `JDSCIS_CIS_Faction` | [JDS] Separatist Droid Army (3276499495) | **hidden checkbox**, not a row |
| ~~☐~~ | ~~**`OuterRim_GalacticEmpire`**~~ | ~~`OuterRim_GalacticEmpire`~~ | ~~Outer Rim - Galactic Empire (2919248699)~~ | ⛔ **DEAD ROW 2026-08-20 — do not check it, do not expect it.** Owner: *"OuterRim_GalacticEmpire is no longer in the game, we patch Empire."* The Galactic Empire's vessel is **vanilla `Empire`** (the ⭐ row below) and nothing patches this def. Whatever this row does or does not say at worldgen is **not a signal about anything**. See `infrastructure/state/OWNER_DECISIONS.md`. |
| ~~☐~~ | ~~**moisture farmers**~~ | ~~`OuterRim_MoistureFarmers`~~ | Outer Rim - Core | ⛔ **RETIRED FROM KEEP 2026-08-21 (R5).** Same settlement reason, plus ⭐ **it duplicates a role we authored** — the **Homestead Defense League** *is* this planet's moisture farmers, thirteen settlements of them. Absent is the desired outcome. |
| ☐ | **rogue droid collective** *("Droid Collective")* | `guy762_KotORFaction_RogueDroids` | Star Wars KotOR Droids (3047371944) | **hidden checkbox**, not a row. 🔴 **quest-critical — antagonist of the KotOR distress call. Never untick.** |
| ☐ | ⭐ **vanilla `Empire`** — *name will be GENERATED, expect a different string* | `Empire` | **vanilla (Royalty)** | 🔴 **ADDED TO KEEP by R3 above.** Not on any untick list, so it survives by default — **confirm it anyway, count ≥ 1, and SCREENSHOT the generated name.** |
| ☐ | ~~**Rebel Alliance**~~ — **RETIRED from KEEP** | `OuterRim_RebelAlliance` | Outer Rim - Rebel Alliance (2919249903) | 🔴 **ABSENT is the DESIRED outcome (R2 above). Record absent and move on — do NOT revert the patch at the screen.** |

⭐ **On vanilla `Empire` (R3 above, owner's ruling).** Vanilla `Empire` **is** the
Galactic Empire — the campaign's one permanent enemy, led by Emperor Palpatine.
🔴 **The "Fallen Dominion" and the two-Empire split are STRUCK from the design**
(see the header of this file). There is no local or planetside Empire, no
disgraced local aristocracy, and nothing on this page turns on that reading.
**The only gate here is: vanilla `Empire` is PRESENT and its count is ≥ 1.**
⚠️ **Its name is generated, so the world will not say "Galactic Empire" until a
`fixedName` patch lands. That is expected, not a failure.** Whatever it generates
is the working name. **Screenshot it — that string is the only record.**

⛔ **THIS WHOLE PARAGRAPH IS DEAD, 2026-08-20 — it tells you to expect a string that
can no longer appear.** `GalacticEmpire.xml` was re-pointed on 2026-08-14 and
**every xpath in it now targets vanilla `Empire`**; it does not mention
`OuterRim_GalacticEmpire` outside its own comment header. Nothing patches that mod def
any more, so there is **no expectation to check** on it. The string to look at is on the
⭐ vanilla `Empire` row above — the patch adds `fixedName` **"Galactic Empire"**, so that
row should read *Galactic Empire* rather than a generated name once the deploy has
landed. See `infrastructure/state/OWNER_DECISIONS.md`.

~~🔴 **On the `OuterRim_GalacticEmpire` row, expect "the Galactic Empire" —
and do not stop for it.**
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Patches\GalacticEmpire.xml`
(repo copy: `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\GalacticEmpire.xml`,
byte-identical on disk 2026-08-13) replaces `label` **and** `fixedName` on
`OuterRim_GalacticEmpire` with **"the Galactic Empire"**, and `leaderTitle`
with **"Sector Director"**. That is the string that will be on the page.~~

~~**It is superseded scaffolding, not a defect.** The Galactic Empire reskin predates
a retired seat's strike of the two-Empire split and has not been redeployed, so the old
string simply survives. ⚠️ **Seeing "the Galactic Empire" is EXPECTED and
is NOT evidence of a bad deploy — do not abort worldgen over it.** If the row
instead reads the stock **"Galactic Empire"**, that only means the Jawa_Patches
deploy did not land; **record which of the two strings you saw and carry on** —
neither blocks generation, because this faction is no longer the antagonist the
design hangs on.~~

---

## SECTION 4b — 🔴 OUR OWN FACTIONS. SET EACH TO AT LEAST 1.

**These did not exist when the rest of this file was written.** They are the
campaign's authored roster, built and deployed 2026-08-14.

> 🔴 **A faction absent at worldgen CANNOT be added later.** This is the single
> most expensive mistake available on this page. If one of these reads 0 when you
> leave, that faction does not exist in your campaign, permanently.

⚠️ **A strict diff against this file's other sections will show these as
"unexpected". That is the expected outcome** — they postdate the untick list.

### The 8 that appear as NEW rows — set each ≥ 1

| ✔ | expect the label | defName |
|---|---|---|
| ☐ | **Hutt Cartel** | `Jawa_HuttCartel` |
| ☐ | **Free Droid Enclaves** | `Jawa_FreeDroidEnclaves` |
| ☐ | **Wildsteam Clan** | `Jawa_WildsteamClan` |
| ☐ | **Deepwater Compact** | `Jawa_DeepwaterCompact` |
| ☐ | **Geonosian Foundry Hive** | `Jawa_GeonosianFoundryHive` |
| ☐ | **Ascendant Helix** | `Jawa_AscendantHelix` |
| ☐ | **the Junkers** | `Jawa_Junkers` |
| ☐ | **Jawa Trade Moot** | `Jawa_IndigenousTribes` |

All seven authored defs carry `requiredCountAtGameStart 1`, so they *should* be
forced — but **"should be" is not "was"**, and this run is permanent. Look at each.

### The 5 vanilla rows we RESKINNED — confirm present, do not untick

| ✔ | on the page it will read | defName | is now |
|---|---|---|---|
| ☐ | a generated Empire name | `Empire` | **the Galactic Empire** — also in Section 4 |
| ☐ | an outlander union | `OutlanderCivil` | **Homestead Defense League** |
| ☐ | a tribe | `TribeCivil` | **Deep Desert Tribes** |
| ☐ | a pirate band | `Pirate` | **Blackstar Company** |
| ☐ | *(hidden checkbox)* | `Mechanoid` | **the Forgotten Arsenal** |

🔴 **Unticking any of these five deletes one of our factions.** They look like
ordinary vanilla rows and they are not any more.

⚠️ **`Mechanoid`'s row loses its safety catch when the pursuit part comes out — measured
2026-08-20, not inherited.** Vanilla's `ScenPart_PursuingMechanoids` ScenPartDef carries
`<preventRemovalOfFaction>Mechanoid</preventRemovalOfFaction>`
(`Data/Odyssey/Defs/Scenarios/ScenParts_Various.xml:9`), and `xref` shows that field is
read by **exactly one method — `WorldFactionsUIUtility::DoRow`**, the renderer for the
rows on *this page*. ⇒ **Its only effect is to stop a human unticking that row here.**

**The Empire-pursuit swap removes that part** (`design/Jawa/droid_ruling.md`), so the
catch goes with it and the `Mechanoid` row becomes untickable like any other. ⛔ **The
faction is NOT being removed and nothing removes it** — owner, 2026-08-20: *"We're not
removing Mechanoids."* This is a warning about a **click**, on the one screen where that
click is possible, and it is why this row's ☐ matters more than it looks. The Forgotten
Arsenal garrisons every ancient danger and sealed complex on the planet.

⛔ **The Unbound Hive is NOT here and that is deliberate.** `Insect` stays on the
Section 2 untick list; the faction was cut for exactly that reason. Do not hunt
for it.

## Tally

| | count |
|---|---|
| **UNTICK — Sections 1, 2 and 3** | ⛔ **0. DEAD 2026-08-23** — `OnlyOurFactions.xml` has already zeroed all 21; see the banner and the archive |
| **KEEP — Section 4** | **4** *(was 6; `OuterRim_BinaryStarRaiders` and `OuterRim_MoistureFarmers` retired by R5, 2026-08-21)* |
| **of those 4, defaulting to 0 and needing a hand-set** | **2** — `JDSCIS_CIS_Faction`, `guy762_KotORFaction_RogueDroids` |
| **SET ≥ 1 — Section 4b, our own** | **13** *(8 new rows + 5 reskinned vanilla rows)* |
| **NOT FOUND on disk** | **0** |

**Before you leave the page**, screenshot it. It is the only record of what was
actually ticked, the world is not reproducible from this file, and a cold load is
~23–30 minutes.
