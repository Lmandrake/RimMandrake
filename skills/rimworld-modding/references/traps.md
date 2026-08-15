# traps.md — the index of earned lessons

Every entry in the files below cost a real debug cycle. **Read the one file that
matches what you are about to do**, not all of them — the whole point of the
2026-08-12 split is that you no longer pay for the log you don't need.

**Append at the end of a task.** Where to append, and the entry format, are at
the bottom of this file. Format and promotion rules are in `SKILL.md` §9.

**Already promoted into SKILL.md — do not re-log these:** `--` forbidden in XML
comments · `PatchOperationRemove` deletes every match · `MayRequire` checks the
mod not the def · `GameComponent` needs `(Game game)` · `modDependency` does not
imply load order · a failed post-long-event action costs only itself, the queue
continues · compatibility patches must load last · read the `wanter` before
calling an unresolved cross-reference benign · `LoadFolders.xml` makes a mod's def
set depend on the whole mod list · the validator cannot see patch-created nodes
and does not check `Defs/` · `--live` and `--defs` are orthogonal, pass BOTH
(→ `skills/rimworld-deploy/SKILL.md`) · `fogGrid` is a bitfield in a table of
shorts, leave it untouched (→ `skills/rimworld-savegame/SKILL.md`).

---

## Which file

| If you are about to… | Read | Entries |
|---|---|---|
| write or debug a patch, an xpath, or a def | [`traps-xml-and-defs.md`](traps-xml-and-defs.md) | 18 |
| trust what a script, grep, census or the def dump just told you | [`traps-tooling.md`](traps-tooling.md) | 39 |
| call art missing, wrong, or broken | [`traps-art.md`](traps-art.md) | 13 |
| chase a mod that is absent, dead, or ignoring its files | [`traps-mods-and-managers.md`](traps-mods-and-managers.md) | 13 |
| believe a diagnosis, or call into a running game | [`traps-diagnosis.md`](traps-diagnosis.md) | 7 |
| **write or debug a quest** — `QuestScriptDef`, `QuestNode`, quest text, a quest that never fires | **a different skill: `skills/rimworld-quests/`** | — |

**If you only read one, read `traps-tooling.md`.** It is the largest section for
a reason: the single most repeated failure in this project is not a wrong patch,
it is **a tool that answered confidently — and answered a different question than
the one asked.**

---

## The full index

### `traps-xml-and-defs.md` — the authoring surface

- ParentName must name an ABSTRACT def — `validate_patch.py` checks this since 2026-08-13
- An `<li>` written into a dictionary-keyed field deleted seven biomes
- An animal registered into a biome from both directions crashes the biome's animal table
- A field silently moved off its class in 1.6, and eight races carried the stale version
- `Inherit="False"` makes a correct patch a silent no-op
- ParentName is LOAD-ORDER dependent, and failing it corrupts map generation
- "PatchOperationFindMod(X) failed" does not mean mod X is missing
- A def's XML element name IS its C# class — `VFEPirates.WarcasketDef` is invisible to `/Defs/ThingDef` yet lives in `ThingDef.json`
- 34. One failed op silently kills every op after it in the same sequence
- `isJunk` on a scatterer lets a world-tile mutator silently multiply its count to ZERO
- 35. Retargeting a gene family is two files, and the old family must stay
- 36. The comp you are designing a patch around may not exist
- A build-over tier ladder deadlocks if the rungs disagree on terrain affordance
- Building one thing over another is vanilla in 1.6 (`replaceTags`) — and Replace Stuff forbids our case
- 48. "It is placeable" and "it can be removed" are different claims — and the do-not-place twins are one word apart
- A `WorldGenStepDef` that is not listed on the layer def is loaded, valid, and never called
- Vanilla's river step sources its mouths from the BIOME, but paths on ELEVATION
- `xenotypeChances` is a def-keyed dictionary — the xenotype is the ELEMENT NAME, not a value

### `traps-tooling.md` — our own tooling and offline analysis

- Vanilla textures are NOT on disk — every check for a Core texture path is blind
- A live def dump has no abstracts
- `--defs` inherits the LIVE `ModsConfig.xml`
- Workshop-tree scans count every version folder a mod ships
- The version-folder fix over-corrected and hid 667 root defs
- A validator honouring `LoadFolders.xml` can still triple-count
- Blanket find-and-replace eats the markup syntax it lives inside
- The patch validator cannot evaluate `text()` — lxml can
- A vanilla def's XML is not what the game loaded — read the dump, even for Core and DLC
- A generator that reads the live dump eats its own output
- `stat()` on the Drive mount returns a stale size
- The def dump is `{defType, defs, count}`, not a bare list
- A grep for a mod's name matches the mod working perfectly
- Parallel `find` into one redirect corrupted the index
- `grep -c '<li>' ModsConfig.xml` counts the expansions too
- `grep` for a packageId is case-sensitive; `ModsConfig.xml` is lowercased
- A self-matching hash check green-lit 14 deletions
- One wrong operator became a week-long "impossible" claim
- `jawa/get_def` returns `extra: null` for def types it does not model, and it reads as "absent"
- A grep over `Data/` proves no shipped def uses a field — never that the engine ignores it
- A check that CANNOT run must fail loud — a benign verdict from a blind instrument is the worst outcome
- `ls -la` columns mean different things per row
- A deploy check compared the commit, not the tool surface
- The interpreter, not the data, rewrote 13,158 rows
- A def can exist in the game and in NO file
- "Empty output" is not a result
- `len()` answers for any container, so the wrong number is plausible
- A guard that tests a STATUS STRING instead of the capability fails safe-looking and silent
- A field xref that scans three opcodes reports "no writers" for a field with writers
- An artifact that records an OUTCOME cannot answer a question about a CAPABILITY
- Take the RULE from a precedent, never the NUMBER
- A blind string replace becomes an ABORT INSTRUCTION when it crosses into a filename or an expected observation
- A SETTING that suppresses behaviour and a DELETION that removes the def are not interchangeable
- `strings` scans 7-bit ASCII, so a deployed message reads as ABSENT

- A `timeout`-wrapped scan that gets killed leaves a PARTIAL result that looks complete
- The two primary RimWorld documentation domains both 403 `WebFetch` — and the web has nothing on 1.6 quests anyway
- A redirected Python run's output file stays 0 bytes — that is buffering, not a stall
- Read the CLASSES, never the count — a validator's warning total is not a backlog
- Before CORRECTING a number, check what it is a number OF — the correction was the error

### `traps-art.md` — art, textures and what a census cannot see

- A mod's art can be invisible to a file audit — AssetBundles are readable, and loose files still beat them
- Twice now, "the art is bad" has meant "the wrong art is being selected"
- The mod whose entire job is deduplication resolved to the worse asset
- Absence of a texture folder is not absence of art
- 37. A missing directional texture is not a defect — read `visibleFacing` first
- 41. Two art bugs that no log line and no file census can ever reveal
- 43. "Non-transparent pixel count" is the wrong emptiness metric, twice over
- 44. A tint mask marks the animal's FILL, not the animal — the keyline is tagged as vehicle
- 45. Art can be correct at source and broken at render — judge the sprite, not the file
- Our own mods shadow each other, and identical bytes make it invisible
- 46. `Graphic_Multi` falls back to the BARE path, and render nodes are lazy — a clean log proves almost nothing
- 47. A mask is NOT required to tint a building — plain `Cutout` honours `<color>`, and it multiplies
- 48. Spawning the pawn does not test the art — a style override is only drawn when the style is SELECTED

### `traps-mods-and-managers.md` — the mod stack

- RimSort sort rules saved into Community Rules vanish silently
- RimSort's local and workshop folder paths were swapped, so custom mods were never scanned
- A mod shipped an assembly referencing an AssetBundle it never packaged
- Subscribed to a Workshop item that Steam has removed
- Bulk Workshop metadata: use the Steam Web API, not the item pages
- "Mods with Missing Publish Field ID" in RimSort is not an error
- Disabling a mod orphaned its add-on's assembly and killed Prepatcher outright
- Mod-list state on disk is not authoritative while the game is running
- A delete in a Steam-synced folder is undone by the next launch
- RimSort's "ignore" dismisses a WARNING, not your sort rules
- A reskin whose donor ships art LOOSE fails silently if it loads first
- Three mods shipped the base game's own assemblies, and one shipped all of it
- 38. A dead mod that the dead-mod grep cannot see
- A def deployed AFTER launch is invisible to the running game, and looks perfectly deployed on disk

### `traps-diagnosis.md` — believing a diagnosis, and the live game

- An error count is a count of victims, not of causes — abstract bases multiply
- A strictly read-only live-bridge call hung the game and cost a 23-minute load
- A failed post-long-event action costs only itself — the queue continues
- The same mod stayed dead through two correct fixes, for three different reasons
- A correct general principle applied to the WRONG SET — and the leading question that launders it
- A sampled extrapolation entered the record as a measured count — and then drifted
- A one-shot generator's output dates the DEF THAT BUILT THE MAP, not the def on disk

### The numbers

Entries 34–48 carry numbers from when this was one flat file. **They are kept so
older commit messages that cite "traps 45" still resolve** — the numbers are
historical IDs, not positions, and they were never contiguous with the entries
before them (what is labelled 34 was the 37th entry). **39 no longer exists on its
own**: it was merged into the element-name-is-the-C#-class entry in
`traps-xml-and-defs.md`, which now carries both facts. **Do not number new
entries.** Cite by title; titles are what the index is built on.

### Admission test — ALL FIVE, or it does not go in

A trap log full of aphorisms is worse than no log, because the real entries stop
being findable. Before appending, check every one:

1. **SPECIFIC** — names an error string, a flag, an xpath, a defName, a number.
   *A principle is not a trap.*
2. **NON-OBVIOUS** — a competent engineer would not have predicted it.
3. **ACTIONABLE** — says what to DO differently, not what happened.
4. **DOMAIN-BOUND** — about RimWorld, its modding stack, or this project's tools.
   General software or process wisdom belongs in `DOC_BUDGET.md` or
   `infrastructure/agents/POLICY.md`, never here.
5. **STILL TRUE** — if the tool was since fixed, the entry becomes ONE line or goes.

**If it fails one, it is not a trap.** Most rejected candidates fail 1 or 4.

### The format — 8 lines, hard cap

```markdown
### <short title, stating the trap itself>
**Symptom:** what it looked like, with the exact log string or value.
**Cause:** what was actually true.
**Fix:** what worked.
**Recurs when:** the named tool, file type or API where this bites again.
```

**`Recurs when:` must name a THING, not a lesson.** "Any script that counts
folders" is a trap. "Be careful with assumptions" is life advice — the failure
mode this log exists to keep out. If you cannot name the thing, the entry is a
diary entry; delete it.

**No dates, no discovery narrative, no attribution.** Git has all three. The entry
says what is true and what to do; the commit says how we found out.

### When a topic file gets long

Past **roughly forty entries**, consolidate rather than append. That rule produced
the 2026-08-12 split, after the flat log hit **51** unnoticed — a rule a document
states about *itself* is the one nobody is assigned to check. `src/RimMandrake/Utils/doc_budget.py`
now enforces a 700-line ceiling on these files, so the check no longer depends on
anyone remembering.

---

## Capture, rejection, promotion — the long form

*(Moved from `SKILL.md` §9 on 2026-08-14 to keep the skill body under its 500-line
budget. The short form — "capture is part of finishing the task; the format and
the file-choosing rule live here" — stayed in the skill.)*

**After any RimWorld task, ask: did anything here surprise me?** A patch that
didn't apply, a field that moved, a mod that failed in an unfamiliar shape, an
xpath idiom that took three tries. If yes, append an entry to the matching topic
file, and add its title to the index in the same commit. **The entry format, and
the rule for choosing a file, live in `references/traps.md`** — kept in one place
so the two cannot drift apart.

⚠️ **Most candidate lessons should be REJECTED.** `references/traps.md` carries a
five-part admission test — specific, non-obvious, actionable, domain-bound, still
true — and an entry failing any one of them is not a trap. General software or
process wisdom goes to `DOC_BUDGET.md` or `infrastructure/agents/POLICY.md`; a log
full of aphorisms
is worse than no log, because the real entries stop being findable.

If an entry would change what this skill tells you to do *by default*, don't leave
it in the log — **promote it into the body of this file** and delete the log entry.
The log is a staging area, not an archive; when **one topic file** grows past roughly
forty entries, split it rather than append.

> ⚠️ **That threshold went unenforced for eleven entries.** The log was one flat
> file and reached **51**, because *a rule a document states about itself is the
> one nobody is assigned to check.* Split 2026-08-12 into five topic files
> (largest: 17). If you notice a file over forty, you are the one who noticed.

**Where the canonical copy lives.** An installed skill is a read-only cache;
editing it there changes nothing durable. Edit the copy in the user's project,
re-package, and say it has been **delivered** rather than saved — installing it
is theirs to do.
