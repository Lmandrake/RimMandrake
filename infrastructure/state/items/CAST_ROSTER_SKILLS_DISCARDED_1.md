## spec
🔴 **MEASURED, not suspected. 101 of the 269 authored cast members do not exist
in the running game** — every single one that carries a `<skills>` block is
thrown away at def load, and has been since the roster was first deployed.

**The evidence, from `Player.log` written 2026-08-22 08:40 (578 mods, rev591):**

```
Exception loading def from file CastRoster_JAWA.xml:
  System.ArgumentNullException: Value cannot be null.  Parameter name: s
    at System.Single.Parse (System.String s, System.IFormatProvider provider)
    at Verse.ParseHelper.ParseIntPermissive (System.String str)
    at Verse.ParseHelper.FromString[T] (System.String str)
    at RimWorld.SkillGain.LoadDataFromXmlCustom (System.Xml.XmlNode xmlRoot)
    (dyn) DirectXmlToObjectNew…ParseAndAddCustomLoadableToList_RimWorld_SkillGain
    (dyn) DirectXmlToObjectNew…ParseAndSetListField_RimWorld_SkillGain
    (dyn) DirectXmlToObjectNew…ParseAndReturnDef_Verse_Def
```

`SkillGain.LoadDataFromXmlCustom` does `ParseHelper.FromString<int>(xmlRoot.FirstChild.Value)`.
It is handed a node whose `FirstChild.Value` is **null**, `int.TryParse(null)` returns
false without throwing, and the `float.Parse(null)` fallback throws. **The whole def is
discarded** — not the field, the def.

⭐ **The attribution is exact, not inferred.** Per-file discard counts in the log match
per-file `<skills>`-carrying character counts on **all twelve files, 101/101**:

| file | chars with `<skills>` | defs discarded |
|---|---|---|
| BLACKSTAR 11 · DEEPWATER 12 · DROIDS 8 · EMPIRE 7 · GEONOSIAN 10 · HELIX 8 | | identical |
| HOMESTEAD 8 · HUTT 7 · JAWA 4 · JUNKERS 9 · TUSKEN 9 · WILDSTEAM 8 | | identical |

Characters with **no** `<skills>` block load fine. This is the sole trigger.

⚠️ **Three things that are NOT the cause, each ruled out by measurement:**
- **Not the assembly.** `Inhabited.dll` is deployed, md5-identical to the repo copy
  (`6d4fd4ff…`), present in `ModsConfig.xml`, and the loader got far enough to resolve
  `Inhabited.CharacterDef` and parse its `List<SkillGain> skills` field.
  ⇒ this is NOT `INHABITED_DLL_FIX_AT_SHUTDOWN_1`.
- **Not a stale deploy.** All 12 `CastRoster_*.xml` are byte-identical between
  `src/Jawa/Inhabited/Defs/CastRosters/` and the game folder.
- **Not malformed XML.** Every one of the 101 `<skills>` blocks parses clean and every
  entry is `<SkillName>integer</SkillName>` with no nested elements and no empty values.

🔑 **The shape we emit is byte-for-byte the vanilla shape** —
`Data/Core/Defs/BackstoryDefs/Shuffled/Outsider_Adult.xml` writes
`<skillGains><Plants>4</Plants></skillGains>` and loads fine. So the defect is NOT
"we wrote it wrong against the documented form". The difference the trace points at is
the **loader**: our def goes through 1.6's `DirectXmlToObjectNew` dynamic-method path,
and that path is what hands `LoadDataFromXmlCustom` a node with a null `FirstChild.Value`.
**Do not "fix" the XML to match vanilla — it already does.**

## verify
POSITIVE OBSERVATIONS, after a cold load with whatever fix is chosen:

1. `Player.log` contains **zero** `Exception loading def from file CastRoster_*.xml`
   lines. `harvest_log.py` reports DEFS DISCARDED back at its baseline of 2.
2. Dev mode → `Inhabited_Jawa_ChiefGhekkUbbUbb` **resolves** (it carries
   Intellectual 16 / Social 14 and is therefore one of the 101 currently missing).
3. That character spawns and his skills read **16 Intellectual and 14 Social** —
   not zero, not rolled. A def that loads with the skills silently dropped is a
   *different* failure wearing a pass.

HOW IT LIES: a def-load exception is thrown ONCE per def at startup and never
again. The game runs normally afterwards, the world generates, the mod list is
clean, and nothing on screen says 101 people are absent. **A quicktest cannot see
this** — defs parse only at startup, so only a cold load re-tests it.
⚠️ And `measure count`/the offline def dump will happily report all 269
`Inhabited.CharacterDef` present, because the dump reads the XML on disk, not the
running DefDatabase. The dump is not evidence here; the log is.

## criteria
Zero CastRoster def-load exceptions in a cold-load `Player.log`, AND one named
skills-carrying character resolves in the running game with his authored skill
numbers intact.

## Watch out
- ⛔ **Do not close this from a quicktest or from the def dump.** Both will show the
  269 characters present. Defs parse only at startup, and the dump reads disk XML,
  never the running `DefDatabase`. Only a cold-load `Player.log` settles it.
- 🔑 **The obvious-looking fix is the wrong one.** Our `<skills>` XML is already
  identical to vanilla's `<skillGains>`. Rewriting the XML to "match vanilla" changes
  nothing. The suspect is the `DirectXmlToObjectNew` list path for a
  `LoadDataFromXmlCustom` type whose children are not `<li>`.
- ⚠️ **A partial pass is the dangerous outcome:** a `List<SkillGain>` swapped for
  something the loader accepts may load the def while silently dropping the skill
  numbers. That reads as a clean log and a present character, and the authored
  skills are gone. Verify step 3 exists to catch exactly that — check the NUMBERS.
- **The generator, not the XML, is the edit site.** These files are emitted by
  `src/RimMandrake/Utils/cast_to_xml.py` from
  `design/Jawa/bridge/INHABITED_CAST_*.md` and carry a do-not-hand-edit header.
  A hand-edit to the XML is overwritten on the next run.
- **Blast radius.** `ROSTER_SOAK_100_DAYS_1` is the architecture gate for everything
  under `Inhabited`, and it has been soaking against a roster missing 38% of its
  people. `CAST_ROSTER_269_LOAD_1` cannot pass until this is fixed.
- The 168 characters WITHOUT a skills block have been loading correctly all along,
  so anything that appeared to work in `Inhabited` is real — it was just never the
  whole cast.
