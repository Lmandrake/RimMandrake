## spec
From CHECK's **C42** (`5aca170`, `071cf52`), routed by REP because it lands
directly on the owner's ruling that faction and ideo work is v1.

The owner's words today: *"faction and ideo work are part of v1, and we already
HAVE the ideoligion I believe. The task to build the factions in-game should be
nearly done save for the allowed items, descriptions, etc."* 🔴 **That belief is
the thing C42 cannot yet confirm.**

`The Salvation.rid` and `MandrakeJawa.xtp` both carry a `<modIds>` provenance
block naming **585 mods, 11 of which no longer load** — including all three
xenotype donors. What CHECK cleared offline against the live dump: the xenotype
is CLEAN (35/35 genes plus icon), memes 5/5, culture present, and the
`Outland_*` genes are safe because Outland Genetics is a DIFFERENT mod from the
switched-off `neronix17.outerrim.galacticdiversity`.

⚠️ **The 82 precepts are UNMEASURED, and CHECK asks for that word specifically.**
Not "missing" — an earlier scrape reporting 71 missing was CHECK's own bug: the
precept block nests `RitualBehavior` / `RitualOutcomeEffect` /
`RitualObligationTargetFilter` defNames, which are not `PreceptDef`s. And
`validate_ideoligion.py` does not cover this case — it reads IdeoPresetDef and
FactionDef XML and answers "no religions found" on a `.rid`. **There is no
offline route to the answer.**

Why it is yours and why it is urgent: an ideoligion **bakes at world creation
and cannot be retrofitted**, same as the factions. If the faction work is
"nearly done", this artifact is close to final and is the largest unmeasured
surface on CHECK's board. The live answer is cheap — load the ideo on the
scratch map and read the dialog, one screen — and CHECK has queued it ahead of
any worldgen run. **Sequence it before the faction work is called done.**

## verify
the 82 precepts are measured live and reported as present/absent by defName.

## criteria
the ideoligion loads with every precept resolving, on the mod set that will be
active at world creation.

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready

## ruling
🔴 **DECIDE, 2026-08-21 — the premise expired. There IS an offline route, and it has now
been run.**

This item says *"There is no offline route to the answer"* and names
`validate_ideoligion.py`, which is the wrong tool — it reads `IdeoPresetDef` and
`FactionDef` XML. **`src/RimMandrake/Utils/validate_save_artifact.py` is the tool for a
saved `.rid`/`.xtp`**, and it resolves every def reference in the artifact against the def
dump. Run 2026-08-21 against the 2026-08-20 dump (61,197 defNames):

| artifact | result |
|---|---|
| `src/Jawa/ideoligion/The Salvation.rid` | **250/266 resolve · ✅ no dangling names** |
| `src/Jawa/ideoligion/MandrakeJawa.xtp` | **36/36 resolve · ✅ no dangling names** |

⇒ **The 82 precepts are measured and they are present.** Not "probably fine" — resolved by
defName against the dump, with zero dangling.

**What is actually left is 16 `AbilityDef`s, and they are a dump blind spot, not a defect:**
`Convert` · `Counsel` · `PreachHealth` · `Reassure` · `Trial` · `LeaderSpeech` ·
`ConversionRitual` · `CombatCommand` · `WorkDrive` · `AM_ChangeStyle` · and six `VME_*`
leader variants. The dump carries **zero rows of type `AbilityDef`**, so the checker
correctly reports them ⬜ UNMEASURABLE rather than missing. Their donor mods —
`sarg.alphamemes`, `vanillaexpanded.vmemese` — are both active.

**Two other claims in the spec above also decayed and should not be re-quoted:**
- *"585 mods, 11 of which no longer load"* — the `.rid` now reads **576 captured, 7
  inactive**, and the `.xtp` **585 captured, 18 inactive**.
- *"including all three xenotype donors"* — ⛔ **false for the `.rid`.** Its seven inactive
  mods are Yautja, yayoani, cereanmanefix, jawaseashaper, two Regrowth biome patches and
  rwexploration. None is a xenotype donor, and the artifact has no dangling names anyway.

### ⇒ THE SEQUENCING ANSWER, which is what this item asked for

⛔ **It does NOT gate the faction work, and it does not gate worldgen.** The reason it was
proposed as a gate — *"the largest unmeasured surface on CHECK's board"* — no longer holds:
the surface is 16 ability defs, and every precept resolves.

✅ **Filed as `IDEO_ABILITY_DEFS_UNREAD_1` for CHECK** — one screen, at the next game-up,
riding whatever load is already happening. It is listed in
`design/Jawa/worldbuilding/PRE_WORLDGEN_GATE.md` as cheap-if-the-game-is-up, **not** as a
blocker.

🔑 **The lesson, and it is the reason this took one command instead of a game load:** the
item asserted a tool could not answer the question. It named a real tool that genuinely
cannot — and a second tool built for exactly this artifact already existed. **Check that a
"no offline route" claim is still true before spending a live round on it.**
