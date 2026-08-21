# Disk versus runtime — when a def dump is not evidence

_Split out of SKILL.md 2026-08-20 to keep the skill body under the packaging gate._
_This is the single most expensive confusion in the project: it has produced wrong
rulings, a retracted damage analysis and a deleted patch._

---

## 5. 🔴 A def dump is DISK. The running game is RUNTIME. They differ.

**This cost two wrong rulings in one hour on 2026-08-13**, and it is the subtlest
thing in this file.

Mods mutate defs **at load**. Dedup, remap, implied-def generation — none of it is
visible in any file on disk. Measured live, from `Player.log`:

```
[BTD Xenotype Remix] Current xenotype count: 250
[BTD Xenotype Remix] Remapped 552 xenotype chances across 9 factions and 99 pawnkinds
[BTD Xenotype Remix] Successfully removed 100 duplicate xenotypes (BTD preference active)
[BTD Xenotype Remix] Final xenotype count: 150
```

A def dump taken before that ran showed **three** Jawa xenotypes and named
`OuterRim_Jawa` as the one the pawnKinds pinned. At runtime `OuterRim_Jawa` **does
not exist** — BTD deduped it away and remapped the pins onto `BTD_Jawa`. Two
rulings were made on the dump and both were wrong.

⚠️ **Read that example for its MECHANISM, not its answer.** The donors were later
switched off for one authored species mod, so `BTD_Jawa` does not exist either any
more. A dedup winner is a property of the active mod list and it expires when the
list changes — which makes the point sharper, not weaker: the dump could not tell
you the winner then, and a doc recording the old winner cannot tell you now.

> **When the question is "what does the game HAVE?", only the live game or the
> log can answer it.** The dump answers "what is on disk", which is a different
> question wearing the same words.

⚙️ **The tell:** any mod whose log lines say *remapped*, *removed*, *merged*,
*generated* or *patched at runtime* has invalidated your dump for those defs.

### The mechanism, and the trap in switching the deduper OFF

Confirmed 2026-08-15 from source, after the same mistake was made again in both
directions — a def called absent that was present, and one called present that was
gone. **All three mods are ACTIVE.** The rivals load, then BTD deletes them.

`RWM_BTD_Xenotype_REMIX_StarWars.dll` exists to delete duplicates and keep its own.
The mapping is data, not code — `BTD_Data/XenotypeEquivalencies.xml`:

```xml
<Species>Jawa</Species>
  <BTD>BTD_Jawa</BTD>              <- kept
  <SWX>guy762_xenotype_jawa</SWX>  <- REMOVED at load
  <OR>OuterRim_Jawa</OR>           <- REMOVED at load
```

🔑 **A def can be in the dump, ship in an ACTIVE mod, and still not exist in the
process — because another active mod deleted it at load.** That is not a mod-list
difference, and **no mod-list check will find it.** Checking `ModsConfig.xml` and
seeing all three present is consistent with only one of them existing at runtime.

🔴 **So the deduper cannot be switched off alone.** BTD's dedup is the only thing
suppressing the three-way collision. Turn BTD off — the obvious first move once it
looks like pure redundancy — and the SWX and Outer Rim duplicates **come back**.
Donors come out as a SET or not at all, and any test of removing them must switch
all three together.

**How to settle one of these live, cheaply:** ask the running game to USE the def,
do not just look it up, and put a known-good def through the same call as a
control. `jawa/set_pawn_xenotype` returning *"No XenotypeDef named 'X'"* while
converting a live pawn to a def you KNOW loads in the same call rules out tool,
spelling and plumbing in one move. ⚠️ Pick that control fresh from the current def
dump — a known-good defName goes stale the moment the mod list changes, and the one
this example used to name (`BTD_Jawa`) is itself gone now. ⚠️ `No <DefType> named '<defName>'` is real absence;
`No def type named '<defType>'` is a typo in YOUR question.

### 5b. 🔴 A dump field is not the operative value when a C# comp computes it

The rule in §5 has a sharper edge than "the dump can be stale". **A field can be present,
current and correct in the dump and still not be the number the game uses**, because a mod
computes it at runtime.

Measured 2026-08-20: every lightsaber in the stack showed `armorPenetration: 0` on its
blade tools. A whole damage analysis was built on that — half the swings negated, no damage
at all against the heaviest armour — and reported as fact. Then the mod's assembly turned
out to export `AdjustedArmorPenetration`, `GetArmorPenetration` and `get_ArmorPenetrationInt`.
The XML field may simply be an input to a calculation, or vestigial. The analysis was
retracted, and the patch built on it was deleted rather than shipped.

⇒ **Before computing anything from a numeric def field, ask whether a comp owns that
number.** The tell is cheap, but it is a metadata read, not a byte scan — copy
`src/RimMandrake/Utils/ilprobe/meta_core.py`, point its `DLL` at the mod's assembly, and
look for a member named after the field:

```bash
python3 -c "import sys;sys.path.insert(0,'<dir with the repointed meta_core.py>');\
import meta_core as m;print([t[0] for t in m.typedefs if 'ArmorPenetration' in t[0]])"
```

⛔ **Not `strings -a <mod>/Assemblies/*.dll | grep -i <fieldname>`.** The blind-scan hook
refuses it, and it earns the refusal: a byte scan of a .NET assembly sees one string heap
at a time — **16 of 115** names on our own companion — so a MISS is not absence. A hit
means the field is contested and disk cannot settle it; a miss means you have not looked.

⇒ **The in-game info card is the arbiter, and reading one is not a test** — no map, no
spawn, no combat, no bridge privileges. It displays the post-comp value. When an offline
number would drive a real change, spend the ten seconds.

🪤 The asymmetry that makes this dangerous: a stat that is *too low* in the dump produces a
dramatic finding ("this weapon cannot hurt anything!") and dramatic findings do not invite
the sceptical second look that boring ones do.

