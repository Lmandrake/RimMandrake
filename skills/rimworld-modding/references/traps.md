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
| write or debug a patch, an xpath, or a def | [`traps-xml-and-defs.md`](traps-xml-and-defs.md) | 13 |
| trust what a script, grep, census or the def dump just told you | [`traps-tooling.md`](traps-tooling.md) | 23 |
| call art missing, wrong, or broken | [`traps-art.md`](traps-art.md) | 9 |
| chase a mod that is absent, dead, or ignoring its files | [`traps-mods-and-managers.md`](traps-mods-and-managers.md) | 10 |
| believe a diagnosis, or call into a running game | [`traps-diagnosis.md`](traps-diagnosis.md) | 4 |

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
- 35. Retargeting a gene family is two files, and the old family must stay
- 36. The comp you are designing a patch around may not exist
- A build-over tier ladder deadlocks if the rungs disagree on terrain affordance
- Building one thing over another is vanilla in 1.6 (`replaceTags`) — and Replace Stuff forbids our case

### `traps-tooling.md` — our own tooling and offline analysis

- Vanilla textures are NOT on disk — every check for a Core texture path is blind

- A live def dump has no abstracts
- `--defs` inherits the LIVE `ModsConfig.xml`
- Workshop-tree scans count every version folder a mod ships
- The version-folder fix over-corrected and hid 667 root defs
- A validator honouring `LoadFolders.xml` can still triple-count
- Blanket find-and-replace eats the markup syntax it lives inside
- The patch validator cannot evaluate `text()` — lxml can
- A generator that reads the live dump eats its own output
- `stat()` on the Drive mount returns a stale size
- The def dump is `{defType, defs, count}`, not a bare list
- A grep for a mod's name matches the mod working perfectly
- Parallel `find` into one redirect corrupted the index
- `grep -c '<li>' ModsConfig.xml` counts the expansions too
- `grep` for a packageId is case-sensitive; `ModsConfig.xml` is lowercased
- A self-matching hash check green-lit 14 deletions
- One wrong operator became a week-long "impossible" claim
- `ls -la` columns mean different things per row
- A deploy check compared the commit, not the tool surface
- The interpreter, not the data, rewrote 13,158 rows
- A def can exist in the game and in NO file
- "Empty output" is not a result
- `len()` answers for any container, so the wrong number is plausible
- A field xref that scans three opcodes reports "no writers" for a field with writers

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

### `traps-diagnosis.md` — believing a diagnosis, and the live game

- An error count is a count of victims, not of causes — abstract bases multiply
- A strictly read-only live-bridge call hung the game and cost a 23-minute load
- A failed post-long-event action costs only itself — the queue continues
- The same mod stayed dead through two correct fixes, for three different reasons

### The numbers

Entries 34–47 carry numbers from when this was one flat file. **They are kept so
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
   `agents_def.md`, never here.
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
