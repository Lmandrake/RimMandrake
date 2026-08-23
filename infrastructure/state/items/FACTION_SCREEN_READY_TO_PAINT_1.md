## 🔴 CORRECTED 2026-08-23, BEFORE ANYONE ACTED ON IT — read this first

**DECIDE asserted that `requiredCountAtGameStart` forces 28 unwanted factions into every
world, and flagged it as unverified. It is WRONG.** Read from source
(`RimWorld/FactionGenerator.cs:62-86`):

```csharp
private static void InitializeFactions(PlanetLayer layer, List<FactionDef> factions)
{
    if (factions != null)                    // ← the page ALWAYS passes a list
    {
        foreach (FactionDef faction in factions)
            if (CanExistOnLayer(layer, faction)) AddFactionToManager(layer, faction);
        return;                              // ← EARLY RETURN
    }
    // requiredCountAtGameStart is only reached BELOW this line
}
```

`WorldGenStep_Factions.cs:11` calls it as
`GenerateFactionsIntoWorldLayer(layer, Current.CreatingWorld.info.factions)` — **non-null**.
⇒ **`requiredCountAtGameStart` is never consulted for a world made through the page.** It
applies only when a world is generated with no list at all (dev / quick worlds).

⛔ **DO NOT ZERO `requiredCountAtGameStart` ON THE 29.** It would change nothing on the page
and would break the one path that does use it. The proposed patch is withdrawn.

## ✅ And the page is already correct — verified from source, not inferred

`Page_CreateWorldParams.ResetFactionCounts()` (`Page_CreateWorldParams.cs:68-90`) builds the
default roster as:

1. for each **configurable** faction (`maxConfigurableAtWorldCreation > 0`), add it
   `startingCountAtWorldCreation` times — **so a def at 0 is simply never added**;
2. then remove any faction that a configurable faction's `replacesFaction` points at.

**Measured against both clauses:**
- All twelve of ours are configurable, each at `startingCountAtWorldCreation 1`. ✅
- All 29 others sit at `startingCountAtWorldCreation 0`. ✅ They are rows the owner *could*
  add; nothing adds them for him.
- Only **5** defs in the whole 86-def stack declare `replacesFaction`, and **not one points
  at any of our twelve** (`BS_LittlePeople`, `OutlanderRoughPig`, `VRESaurids_OutlanderRoughSaurid`
  → `OutlanderRough`; `TribeRoughNeanderthal` → `TribeRough`; `TribeSavageImpid` →
  `TribeSavage`). ✅ Nothing silently removes `Pirate` or any other host.

🔑 **So the default roster is exactly our twelve, one each, and nothing else.** The owner's
*"extra Junker"* was caused wholly by the `maxConfigurableAtWorldCreation: -1` defect, which
is fixed and live.

## ⇒ What is left is ONE thing: look at it

- [ ] Open a new world to Configure Factions and **count the rows**. PASS = the twelve, one
      each, sorted to the top, nothing added that he did not choose.
- [ ] Then close `AUTHORED_FACTIONS_OFF_THE_SCREEN_1` on that evidence.
- [ ] ⛔ No def edits. Nothing below this line needs building.

⚠️ Bridge calls at that screen take over 25 s against a 30 s default timeout — use
`timeout=150` and a fresh connection per call, or a late response is read as the next call's
answer.

---

*The original spec follows, kept because its measurements are good and only its
mechanism was wrong.*

---

## spec

🔴 **OWNER, 2026-08-23:** *"I was having to go in and add an extra Junker every game just to
'make room' to paint Blackstar somewhere. Can we please hack the factions to be ~correct
right now from the outside, or at least have the appropriate 'ready to repaint' options in
place so I don't have to mess with them every time we make a new world? This is a high place
of user interaction, frustration, and is errorprone due to race conditions and the inability
to 'go back' in the menu without making the game unstable."*

## ⭐ HALF OF THIS IS ALREADY FIXED — VERIFY IT, DO NOT REBUILD IT

His symptom is the exact signature of `AUTHORED_FACTIONS_OFF_THE_SCREEN_1`. The gate is
`FactionGenerator.ConfigurableFactions`, quoted from source in that item:

    from f in DefDatabase<FactionDef>.AllDefs where f.maxConfigurableAtWorldCreation > 0

On 2026-08-22, **seven of the eight authored `Jawa_*` factions read `-1`** and were therefore
**invisible on the Configure Factions page**. `Jawa_Junkers` alone read `9999`. ⇒ The only
pirate-family row he could touch was the Junkers, so bumping it was the only way to get
another pirate presence for Blackstar. **That is the "extra Junker".**

🔑 **MEASURED 2026-08-23 against the live capture `2026-08-23T07-12-04Z`: all twelve are now
configurable.** The repo fix landed; it has simply never been confirmed on screen.

| faction def | settlements | start | max | required | priority |
|---|---:|---:|---:|---:|---:|
| `OutlanderCivil` → Homestead Defense League | 37 | 1 | 9999 | 1 | 10 |
| `Jawa_HuttCartel` | 19 | 1 | 9999 | 1 | −98 |
| `Jawa_FreeDroidEnclaves` | 12 | 1 | 9999 | 1 | −94 |
| `TribeCivil` → Deep Desert Tribes | 9 | 1 | 9999 | 1 | 30 |
| `Jawa_Junkers` | 8 | 1 | 9999 | 1 | −99 |
| `Jawa_AscendantHelix` | 7 | 1 | 9999 | 1 | −93 |
| `Jawa_IndigenousTribes` → Jawa Trade Moot | 7 | 1 | 9999 | 1 | −100 |
| `Jawa_GeonosianFoundryHive` | 5 | 1 | 9999 | 1 | −95 |
| `Jawa_DeepwaterCompact` | 5 | 1 | 9999 | 1 | −97 |
| `Pirate` → Blackstar Company | 4 | 1 | 9999 | 1 | 60 |
| `Jawa_WildsteamClan` | 4 | 1 | 9999 | 1 | −96 |
| `Empire` → Galactic Empire | 3 | 1 | **1** | 1 | 70 |

All twelve: `startingCountAtWorldCreation 1`, `requiredCountAtGameStart 1`, none `hidden`,
and the eight authored ones sort to the very top on priority −93…−100.

⇒ **The page should now open with all twelve present at one each and nothing to add by hand.**
🔴 **Step one is to LOOK at it and confirm that**, because it is the whole of his complaint.

## 🔴 THE HALF THAT IS NOT FIXED — 29 other factions are still on that page

`OnlyOurFactions.xml` zeroes `startingCountAtWorldCreation` on 48 defs. **It never touches
`requiredCountAtGameStart`, and 26 of the 29 leftovers carry `requiredCountAtGameStart: 1`.**

```
Insect  AG_OutlanderCivilUnion  AG_XenohumanPirates  BS_Dvergr_Medieval_Union
BS_LittlePeople  BS_Muspelheim  BS_Niflheim  BS_OgreFaction  CannibalPirate
DV_OutlanderRoughBuzzer  DV_PirateKeshig  KAR_OrcClan  NudistTribe
OuterRim_BinaryStarRaiders  OuterRim_GalacticEmpire  OuterRim_MoistureFarmers
OutlanderRough  OutlanderRoughPig  PirateWaster  PirateYttakin  TradersGuild
TribeCannibal  TribeRough  TribeRoughNeanderthal  TribeSavage  TribeSavageImpid
VFEP_Junkers  VFEP_Mercenaries  VRESaurids_OutlanderRoughSaurid
```

⚠️ **CONFIRM THE MECHANISM FROM SOURCE BEFORE PATCHING.** DECIDE is reasoning from the field
name: `requiredCountAtGameStart` is believed to make `FactionGenerator` create the faction
regardless of a zeroed `startingCountAtWorldCreation`. **Read
`FactionGenerator.GenerateFactionsIntoWorld` and say what it actually does in the commit.**
If it does force them, zeroing `startingCountAtWorldCreation` alone was always a half-fix and
28 unwanted factions have been entering every world we build.

## what to change

**Set `requiredCountAtGameStart` to 0 on the 29**, in `OnlyOurFactions.xml` beside the
existing operations, so the same file owns the whole "only our factions" claim.

⛔ **Do NOT set `maxConfigurableAtWorldCreation` to 0 to hide them.** At 0 the row is **deleted
from the page entirely**, not capped — the owner then cannot add one back if he wants it, and
he has explicitly named *"the inability to go back in the menu"* as part of the frustration.
That warning already sits in the slate file's header and is load-bearing.

✅ **Leave all twelve of ours exactly as they are.** They are correct.

⚠️ **`Empire` is capped at `maxConfigurableAtWorldCreation 1`** — one Galactic Empire, ever.
That is almost certainly right for the lore and is called out only so nobody is surprised
later. Do not change it without a DECIDE ruling.

## verify

Open a new world to Configure Factions and read it, then compare against the table above.

**PASS =** the twelve are present at one each, sorted to the top, and **no faction the owner
did not choose has been added**. ⛔ *"It looks about right"* is not a pass — count the rows.

⚠️ **This needs the game at the world-creation screen, and bridge calls there take over 25 s
against a 30 s default timeout.** Use `timeout=150` and a fresh connection per call, or a late
response is read as the next call's answer and you get an id-mismatch cascade that looks like
four unrelated failures.

## criteria

- [ ] The page confirmed on screen: twelve present, one each, top of the list, zero clicks.
- [ ] `FactionGenerator.GenerateFactionsIntoWorld` read, and what `requiredCountAtGameStart`
      actually does recorded in the commit.
- [ ] If it forces creation: the 29 zeroed, and a world generated with no unchosen faction.
- [ ] ⛔ No `maxConfigurableAtWorldCreation` set to 0 anywhere.
- [ ] `AUTHORED_FACTIONS_OFF_THE_SCREEN_1` closed or corrected on the evidence.

## watch out

- 🔑 **A faction absent when the owner builds the world is absent from every player's game
  forever.** The world is hand-made once and frozen. Get this right before the build.
- ⚠️ `requiredCountAtGameStart 0` on a faction the game genuinely needs (`PlayerColony`,
  `PlayerTribe`, `Ancients`) would be catastrophic. **The 29 above exclude our twelve and
  every hidden def; do not widen the list by prefix.**
