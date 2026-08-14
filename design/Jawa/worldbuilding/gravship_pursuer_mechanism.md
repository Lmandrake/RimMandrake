# The gravship pursuer — can it be changed from mechanoids?

## ⭐ OWNER'S RULING, 2026-08-13 — WHO the pursuer is, settled

> **The Galactic Empire pursues the gravship.** Stormtroopers, combat droids and
> lightsaber-bearing Sith — not mechanoids, and **not an independent Imperial
> Droid Army, which no longer exists in the design at all.**

**ONE Empire. There is no local or planetside Empire and there never will be** —
owner's ruling, 2026-08-13, striking the two-Empire split entirely. The Galactic
Empire is a single faction, reskinned onto vanilla `Empire`, led by **Emperor
Palpatine**, and it is the thing that follows the ship. The droid-averse
contradiction — a Jawa campaign whose antagonist was a machine army the fiction
says the Jawas scavenge — **is resolved by deletion, not by argument.**

**What this does NOT change:** everything below. The mechanism question ("can the
hardcoded mechanoid pursuit be pointed at another faction?") is unaffected by
*which* faction we point it at; route **A** stays the recommendation.

⚠️ **What it DOES change for whoever builds it:** the pursuit's pawns must come
from the Galactic Empire's `pawnGroupMakers`, so the Sith/stormtrooper roster is
now on the pursuit's critical path rather than beside it. Spec:
`D:\Luke\dev\Rimworld\design\Jawa\force_users_build_spec.md`.

**Answered 2026-08-13 by WORLD, from the live def dump (573 mods) and the game
assembly. Measured, not inferred.** The question blocked the Empire-as-pursuer
design, so the mechanism is written down here rather than left in a chat log.

⚠️ **This was NOT the first answer, and this file should not be read as one.**
The mechanism was already established **2026-08-02** by reading VGE's source —
`required_mods.md` §Empire-as-pursuer and `setup_checklist.md` §4, which record
*"the faction is baked in C#… there is NO config toggle"* and rule **route (B),
Empire as a permanently-hostile live faction, as the DECIDED default.** That
ruling stands; nothing here overturns it.

What this file adds is a **second, independent derivation** — from the serialized
ScenPart, its `ScenPartDef` and the assembly, rather than from a mod's source —
and it agrees. Two routes to the same answer is worth more than one. But the
prior decision is the one on the books, and re-deriving it cost a fan-out that a
`grep` for "pursuer" would have saved.

---

## The short answer

> **The faction is hardcoded. Four routes exist; the cheapest good one is a
> Workshop mod, and the "just reskin the Mechanoid faction" idea is the WORST of
> them, not the best.**

⚠️ **Correcting this file's own first draft.** It originally led with *"you
reskin the faction it already points at"* as the answer. That route does work —
the hardcode resolves *through* an editable def — but it changes **every
mechanoid raid game-wide**, leaves mech clusters and ancient-danger spawns
referencing mech ThingDefs directly, makes the mechhive endgame incoherent, and
breaks Biotech mechanitor content that assumes `Faction.OfMechanoids` is
machines. It is viable **only** if *"there are no real mechanoids in this
campaign"* is an acceptable premise. Since a mod now supplies the clean route,
leading with the reskin was wrong.

## The four routes, ranked

| | route | mechanism | cost | blast radius |
|---|---|---|---|---|
| **A** | **`Ruthless Faction Pursuit`** WS `3621784437` | ships the Harmony patch | ⚡ subscribe | none — ⭐ **recommended** |
| **B** | your own `scenPartClass` | `PatchOperationReplace` on `ScenPartDef/scenPartClass/text()` → your class | 🔴 C# you ship | none; full control of timers too |
| **C** | reskin `FactionDef[defName="Mechanoid"]` | hardcode resolves through an editable def | ⚡ XML | 🔴 **global** — see the warning above |
| **D** | delete the pursuit, rebuild it | `PatchOperationRemove` the `li[@Class="ScenPart_PursuingMechanoids"]`, drive pressure with your own incidents | ⚡ XML | none, but you rebuild the escalation curve and lose the `Alert_MechThreat` countdown UI |

**B is the interesting one and was missed on the first pass:** `scenPartClass` is
an ordinary XML string. You can point the *existing* ScenPartDef at your own
class without touching the scenario. That is almost certainly how route A's mod
works.

## The evidence

**1. The scenario part takes no faction.** `TheGravship` (Odyssey, label "The
Gravjumper") carries `ScenPart_PursuingMechanoids`, and its complete serialized
field set is:

```json
{ "$type": "ScenPart_PursuingMechanoids",
  "onStartMap": true, "mapWarningTimers": [], "mapRaidTimers": [],
  "questCompleted": false, "tmpMaps": [], "def": "PursuingMechanoids" }
```

Timers and flags. **No `faction`, no `factionDef`, no `factionDefs`.** There is
no xpath to patch, because there is no node to patch.

**2. Its `ScenPartDef` names the faction, and not as a parameter.**

```json
{ "defName": "PursuingMechanoids",
  "scenPartClass": "RimWorld.ScenPart_PursuingMechanoids",
  "preventRemovalOfFaction": "Mechanoid",
  "canBePlayerAddedRemoved": true, "canBeRandomlyAdded": true, "maxUses": 1 }
```

`preventRemovalOfFaction: Mechanoid` is a **guard**, not a selector — it exists
to stop the faction being removed out from under the scenario. Changing it would
not redirect the pursuit; it would only disarm that protection.

**3. The class hardcodes the faction — DECOMPILED, not inferred.** Every pursuit
raid funnels through one private method of `RimWorld.ScenPart_PursuingMechanoids`:

```csharp
private void FireRaid_NewTemp(Map map, float pointsMultiplier, float minPoints)
{
    IncidentParms incidentParms = new IncidentParms();
    incidentParms.forced = true;
    incidentParms.target = map;
    incidentParms.points = Mathf.Max(minPoints,
        StorytellerUtility.DefaultThreatPointsNow(map) * pointsMultiplier);
    incidentParms.faction = Faction.OfMechanoids;          // <-- HARDCODED
    incidentParms.raidArrivalMode = PawnsArrivalModeDefOf.RandomDrop;
    incidentParms.raidStrategy = RaidStrategyDefOf.ImmediateAttack;
    IncidentDefOf.RaidEnemy.Worker.TryExecute(incidentParms);
}
```

`Faction.OfMechanoids` → `FactionManager.ofMechanoids = FirstFactionOfDef(FactionDefOf.Mechanoid)`,
and `FactionDefOf.Mechanoid` binds by reflection to the def literally named
`Mechanoid`. Arrival mode and raid strategy are hardcoded `DefOf`s too.

⚠️ **`IncidentDef` has no `faction` field**, so you cannot author a
"same incident, different faction" IncidentDef in XML either. And `Data/Odyssey/`
has **no `Assemblies/` folder** — all Odyssey code is in `Assembly-CSharp.dll`.

**Because it is one method, route B gets faction, arrival mode and raid strategy
from a single hook.**

### The escalation curve, for design maths — all `const`, none XML-exposed

| when | value |
|---|---|
| start map: warning | 2,700 ticks (~45 in-game min) |
| start map: raid | 30,000 ticks (~half a day) |
| each later landing: warning | 840,000–960,000 ticks |
| each later landing: raid | 1,080,000–2,100,000 ticks (**~18–35 days**) |
| raid strength | 1.5× points, min 2,000 — then a **second** at 2×, min 8,000, 30,000 ticks later |

Skipped entirely on `MapGeneratorDefOf.Mechhive` maps, and switched off by
`Notify_QuestCompleted()` from the mechhive/cerebrex endgame.

### ✅ Flavour text is free, whichever route you take

`LetterLabelMechanoidThreat` / `LetterTextMechanoidThreat` in
`Data/Odyssey/Languages/English/Keyed/Letters.xml`, and `AlertMechanoidThreat` /
`AlertMechanoidThreatCritical` in that folder's `Alerts.xml`, are **keyed
strings** — overridable by any language patch, no C# involved.

### ⭐ Nobody else has patched this, and that is evidence

All **1,226** installed workshop items were grepped for `PursuingMechanoids` /
`TheGravship`. **Three files, two mods, neither touching the pursuit:** Vanilla
Chemfuel Expanded adds starting chemfuel; **VGE Chapter 1 renames the scenario,
rewrites the description and the start dialog — and leaves the pursuit part
intact.** A competent team hit the same wall and settled for text.

## What this makes cheap, and what it does not

| goal | route | cost |
|---|---|---|
| Pursuer *reads* as the Empire — name, colour, icon, description | `PatchOperation*` on `FactionDef[defName="Mechanoid"]` | ⚡ one XML file |
| Pursuer *fields* Imperial units instead of scythers | replace `pawnGroupMakers` on the same def | ⚡ XML, if you field pawnkinds that already exist |
| Pursuit **turned off** entirely | `ScenPart` is `canBePlayerAddedRemoved: true` | ⚡ scenario edit |
| Pursuit driven by a **different faction object** | **`Ruthless Faction Pursuit`, WS `3621784437`** — see below | ⚡ **subscribe**, not C# |

### ⭐ The C# route is off-the-shelf — this row used to read 🔴

**`Ruthless Faction Pursuit`** (Matathias, WS `3621784437`) adds a **`Ruthless
Faction Pursuit` ScenPart you point at any faction**, plus a `Ruthless Omni
Pursuit` variant that pursues with every faction at once.

Verified against the live Workshop page 2026-08-13, because a second-hand date
looked wrong: **tagged 1.6 only**, **requires Odyssey and Harmony**, posted
**2025-12-11**, updated **2026-01-18** — both after Odyssey, so the "predates
Odyssey" worry was a year misread.

It **supplements rather than replaces** vanilla: *"you are no longer restricted
to being pursued by mechanoids, and you will be pursued whether or not you have a
grav engine."* Since the vanilla ScenPart is `canBePlayerAddedRemoved: true`, the
clean configuration is **remove `PursuingMechanoids`, add the Ruthless part
pointed at the Empire.**

⚠️ **Not yet adopted, and three things are unchecked:** whether it double-pursues
if the vanilla part is left in; how it interacts with VGE's transpiler patch on
`ScenPart_PursuingMechanoids_Tick`; and whether it moots the `pawnGroupMakers`
reskin entirely — pointing pursuit at the *real* Empire faction sidesteps the
mech-cluster leak risk below, because nothing is pretending to be a mechanoid.

⚠️ **Never change the `Mechanoid` defName.** `FactionDefOf.Mechanoid` binds by
it, and so do `GenStep_SleepingMechanoids`, `IncidentWorker_MechCluster`,
`SitePartWorker_SleepingMechanoids` and the mech-signal quest. Patch `label` and
`description`; the defName is infrastructure. Same reasoning that made us zero
the Rebel Alliance def rather than delete it.

⚠️ **`fixedName` needs `Add`, not `Replace`.** Vanilla `Mechanoid` has no
`<fixedName>` element, so a `PatchOperationReplace` on it fails silently — the
exact trap the Galactic Empire patch header records.

## ⬜ The open risk, and it decides "reskin" vs "project"

**Raids are not the only thing that spawns mechanoids.** Mech clusters, sleeping
mechs in ancient danger, and the mech-signal quest are hardcoded around
`Faction.OfMechanoids` and **[INFERRED, not verified]** select pawns C#-side by
`RaceProps.IsMechanoid` and cost — *not* by reading `pawnGroupMakers`.

If that inference holds, a `pawnGroupMakers` swap reskins **the pursuit and
raids** while ancient danger keeps disgorging vanilla scythers. That is the
difference between a one-file patch and a project, and **it must be settled by
observation before anyone promises a "complete" reskin.**

**Possible free win, same inference:** JDS Separatist droids are
`fleshType Mechanoid`, so if cluster selection really is `IsMechanoid`-filtered
they may *already* be eligible to appear. Check before writing any C#.

## The fiction collision to resolve first

`faction_roster_v2.md:244` rules that the Galactic Empire is **droid-averse** —
*"**Never 'battle droid'**"*, its machines are "dark trooper, purge sentry, probe
droid, KX security", and `Alien_Bestiary.md:51` files them as **ordnance, never
droids**, calling that prejudice "itself the flavor".

So an "Imperial **Droid** Army" contradicts the ratified roster. The same build
delivers the same mechanic under the sanctioned name — **Imperial purge units /
security ordnance**. Owner's call, not an implementation detail.

**And the capture question is a real fork.** If the pursuer fields JDS kinds
(cheapest, zero art), the player can never ion-stun, down, capture or reactivate
one — they are force-killed on downing. That directly contradicts the "Jawa
repair the droids they down" fiction. Droid Depot kinds are capturable but
default to `PlayerColony` and must be re-homed first.

---

## The "Eye of Sauron pursuer" memory — NOT corroborated

Searched for, and not found. Recorded so nobody hunts it twice.

- **Nothing Tolkien anywhere in the repo.** A full search for `sauron`,
  `barad-dur`, `dark lord`, `all-seeing`, `eye of` returns three unrelated hits:
  a Star Wars Tukata animal description, an Ideology deity title *"All-Seeing
  One"*, and *"Dark Lord of the Sith"* — both of the latter inside saves.
- **The likely real memory is `Rimworld: Nature's Wrath`** (WS `3596387303`), a
  Mr Samuel Streamer fantasy total conversion. Its own store page advertises
  *"the brand new **reworked pursuer mechanic from Odyssey**"* — i.e. **Ludeon's**
  pursuer, not a custom faction. A fantasy world plus a pursuer is very likely
  what fused into "a Sauron pursuing him".
- **His modlists contain no pursuit mod.** Both fantasy collections were parsed
  by pairing `<modIds>`/`<modNames>`/`<modSteamIds>`: no match for `pursu`,
  `ruthless`, `sauron`, `mordor`, and no `3621784437`. The only place a bespoke
  pursuer could hide is his own `mss.naturepack` C# glue mod, whose contents are
  not on disk.

⚠️ **And his authoring method could not have done it anyway.** The documented
"Streamer model" is **save-based** — bake the authored start into a starting
save. **A save file cannot change a hardcoded C# faction lookup.** So if he ran a
non-mechanoid pursuer, it was a mod, not the file-editing technique we adopted
from him. The two are orthogonal, and conflating them would send someone looking
for a pursuer in a `.rws`.
