## spec
🔴 **101 of the authored cast are DISCARDED at load, and the cause is our XML.**
Spawned by CHECK from `EMPTY_SKILL_DISCARDS_101_1`, a finding off
`INHABITED_DLL_FIX_AT_SHUTDOWN_1/run-1@full-578-2026-08-21T22:44Z`.

⚠️ **THE ITEM'S NAME IS WRONG AND IT MATTERS.** There is not one empty `<li>` in
any roster — measured, zero. Every one of the 133 skill entries carries a real
skill and a real number. **The defect is the SHAPE of the element, not its
emptiness**, and a fix aimed at "empty entries" would have found nothing to do
and closed clean.

**What the engine actually said**, from its own stack in `Player.log`:

```
Exception loading def from file CastRoster_BLACKSTAR.xml:
System.ArgumentNullException: Value cannot be null.  Parameter name: s
  at System.Single.Parse (System.String s, ...)
  at Verse.ParseHelper.ParseIntPermissive (System.String str)
  at RimWorld.SkillGain.LoadDataFromXmlCustom (System.Xml.XmlNode xmlRoot)
```

`CharacterDef.skills` is `List<SkillGain>` (`Source/CharacterDef.cs:143`), and
`SkillGain` is a **custom-loadable**: its loader takes the NODE NAME as the skill
and the node's inner text as the amount. We wrote the list form instead:

```xml
<skills><li><skill>Intellectual</skill><amount>16</amount></li></skills>   ⛔
```

so `xmlRoot.FirstChild` is the `<skill>` ELEMENT, whose `.Value` is `null`, and
`ParseIntPermissive(null)` throws. 🔑 **A def that throws during load is discarded
whole** — so each bad block costs an entire character, not a skill.

**Vanilla's shape, read off the game's own Data rather than remembered**
(`Core/Defs/BackstoryDefs/Shuffled/Outsider_Adult.xml`):

```xml
<skillGains><Plants>4</Plants><Crafting>3</Crafting></skillGains>            ✅
```

**Measured, and the two numbers match exactly:** 294 character defs, **101 carry a
`<skills>` block**, and the log discards **101**. `CharacterDef.cs:141` already
says *"101 characters carry a skills line"*. ⇒ **every character with skills was
being lost**, and none without.

**Done:** all 12 `CastRoster_*.xml` rewritten to the vanilla shape — 133 entries,
0 leftover `<li>`, every value numeric, and all 12 skill names confirmed against
the fresh capture (`measure count SkillDef` = 12, all present). ⛔ **No C# change**:
`List<SkillGain>` is exactly what vanilla `BackstoryDef.skillGains` uses. The def
class was right; the XML was not.

## verify
⚠️ **WRITTEN BY BUILD, WHO WROTE THE FIX — the owner waived the empty-verify
refusal explicitly (2026-08-21). Recording that plainly, because an artifact
graded by its own author proves nothing**, and the offline half below is exactly
that. The live half is independent and is the one that settles it.

**Offline (BUILD, done):** all 12 files parse; 101 `<skills>` blocks; 133 entries;
zero `<li>` remaining inside `<skills>`; every amount numeric; every skill name
present in the 2026-08-21T22:44:59Z capture.

🔑 **Live (CHECK, next load — the independent half):** `harvest_log.py` reports
`DEFS DISCARDED` back at **baseline 2**, down from 103, and **no line matching
`Exception loading def from file CastRoster_`**. Then `[Inhabited] ready:` carries
its full count with the 101 present.

⚠️ **Absence alone is not sufficient.** If the mod failed to load at all there
would also be no discard lines. The `ready:` count is the expected-PRESENT half
and both are required.

## criteria
No `CastRoster_*.xml` def is discarded at load, and a character that declares
skills actually generates carrying them.

## notes
Filed empty by CHECK's `spawn`; spec, fix and verify written by BUILD 2026-08-21
on the owner's explicit instruction to proceed without a verification plan.
🪤 **The lesson worth keeping: the finding's NAME was a hypothesis, not a
measurement.** "Empty `<li>`" was a reasonable guess at an ArgumentNullException
and it was wrong — the null came from an element that had children instead of
text. The engine's stack named the real cause in one line.
