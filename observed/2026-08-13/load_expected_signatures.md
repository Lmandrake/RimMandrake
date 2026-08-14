# Expected-failure signatures — the load launched 2026-08-13 evening

_OPS. **Written BEFORE the launch, deliberately** — that is the whole point of the
artifact. A signature written after reading the log is not a prediction, it is a
rationalisation, and it cannot tell you the difference between "this worked" and
"I did not look properly". Closes queue item **O5**._

**Mod set: 581 active** (`grep -c "<li>"` = 586 minus 5 `<knownExpansions>`).
Previous load was 580. Delta: **+`mandrake.phytokinbarkheadfix`,
+`mandrake.kotorbandoliernorthfix`, −`mandrake.missingartfixes`.**

🔴 **Read `vendor/wisdom/benign_log_errors.md` §0 before triaging anything below.**
The known-benign baseline for the previous load was **25** `Could not resolve
cross-reference` and **0** `Could not load reference to`. A change in those two
numbers is the first thing to check.

---

## The trap that governs three of the six rows

**Four of this load's six changes CANNOT FAIL IN THE LOG.** They are loose-texture
overrides, and a loose texture that loses to load order produces **no error, no
warning and no log line at all** — RimWorld simply drew the other file. For these,
*"the log is clean"* is not evidence of anything. **The only evidence is a
screenshot of the right pawn facing the right way.**

This is also why they are cheap: each is one glance during ordinary play, not a
staged test.

---

## Row 1 — `mandrake.phytokinbarkheadfix` @562 (donor @388)

| | |
|---|---|
| **Expected log** | **NOTHING. Silence is the predicted state, not the pass.** |
| **PASS looks like** | A female Phytokin with `VRE_BarkSkin` + `Jaw_Heavy` walking **east or west** shows a **side-facing head**. |
| **FAIL looks like** | A **front-facing head on a side-facing body** — the whole head, rotated in from the north view at −90°. Unmistakable once seen. |
| **If FAIL** | The fix lost to the donor on load order. Re-check `mandrake.phytokinbarkheadfix` index > `vanillaracesexpanded.phytokin` index. Verified 562 > 388 at write time. |
| **Cost if missed** | One xenotype's heads look wrong. Cosmetic, not blocking. |

## Row 2 — `mandrake.kotorbandoliernorthfix` @579 (donor @572)

| | |
|---|---|
| **Expected log** | **NOTHING.** Same class as row 1. |
| **PASS looks like** | A pawn wearing `bandolier_chewbacca` or `bandolier_traveler`, **seen from behind**, shows a **bare leather strap** — no pouches. (CREATE's own acceptance criterion, and it is theirs to judge.) |
| **FAIL looks like** | **Chest pouches drawn on the pawn's back**, sitting on top of everything else at draw layer 65. |
| **If FAIL** | Loading before the donor. 579 > 572 was verified positionally at write time, so a FAIL here means something re-sorted the list after I wrote it. |
| **Watch for** | Wide generation tags — this rides colonists, traders and raiders, so it should appear on its own within the session. |

## Row 3 — `mandrake.missingartfixes` REMOVED (was @555)

| | |
|---|---|
| **Expected log** | **NOTHING.** All 7 of its textures are md5-identical to the per-donor successors now at 556–563. |
| **FAIL looks like** | 🔴 `Failed to find any textures at <path>` for any of its 7 paths — that fires only when **every** direction of a `Graphic_Multi` is absent, so it is a loud, real failure rather than a silent substitution. |
| **Also FAIL** | Any startup complaint naming `mandrake.missingartfixes` — would mean the entry was removed but something still references it. |
| **Why the order mattered** | The list entry was dropped **first**, folder left on disk. Dropping the folder first would have booted the game with an entry pointing at nothing. |

## Row 4 — the ground hulk: `JawaGroundHulk` GenStep + PrefabDef + register patch

| | |
|---|---|
| **Expected log** | **NOTHING**, and this one CAN fail loudly, unlike rows 1–3. |
| **FAIL — def half** | `Could not resolve cross-reference` naming `Jawa_GroundHulk` or the prefab. That is the **def loader** — a live mod-set problem. |
| **FAIL — runtime half** | An exception from the GenStep during map generation. 🔴 **This would surface as a silent "GenStep failed", with nothing naming the hulk** — PROJECT flagged that shape explicitly. |
| **PASS looks like** | A ground hulk actually present on a newly generated map. **Map generation only** — an existing map shows nothing, and that is not a failure. |
| **Do not conclude** | "The hulk is missing" from an old map. State which map any observation came from. |

## Row 5 — `BTDGravshipQuest_GrammarFix.xml` (deployed this pass)

| | |
|---|---|
| **FAIL, loud** | 🔴 A **red error naming `PatchOperationReplace`** on `BTD_DownedGravship` → the `PatchOperationFindMod` guard did not match, meaning the mod name string is wrong. Guard reads `[BTD] Gravship Blueprints`, taken from its About.xml root, not guessed. |
| **FAIL, quiet** | `Grammar unresolvable. Root 'questDescription'` appearing again → the patch deployed but did not take. |
| **PASS** | 🔴 **POSITIVE OBSERVATION REQUIRED: open the Quests tab and read the Downed Gravship description.** The disappearance of the grammar error proves **nothing**, because the quest may simply not have fired this session. |
| **Prior state** | Exactly 1 occurrence in the previous log. |

## Row 6 — `mandrake.rimdefdump` must still be LAST

| | |
|---|---|
| **Why** | A def dumper that is not last describes a game that is not the one running. Verified @580 of 581 at write time. |
| **FAIL** | The dump's mod count is not **581**. That invalidates every artefact derived from it, silently. |
| **Also** | Previous dump described **573** while 580 were loaded — so **check the dump's own count before trusting it**, every time. |

---

## Two counts to record on arrival, with their derivation

1. `grep -c "Could not resolve cross-reference"` — **baseline 25.** If higher, the
   new entries are the first suspects; if lower, something that used to load did
   not, which is not automatically good news.
2. `grep -c "Could not load reference to"` — **baseline 0.** Non-zero means a
   **saved file** holds a dead name. Different system, different fix. Never
   conflate the two phrasings.

## One open question this load can settle for free

`Error while generating pawn. Rethrowing … NullReferenceException` from
`AlienRace.GenerationChanceGenderless` — **9 in the previous log, not waived**
(queue **O12**). 8 of those were on a droid **I debug-spawned myself**, so they may
be an artefact rather than a defect. **If it appears this session on pawns nobody
spawned by hand, it is live and it matters** — relation generation runs for
faction leaders at worldgen and fails silently there.
