# traps — Reading errors, and the live game

Log triage, error counts, and calls into a running game.

**Read this one before trusting a diagnosis** — especially before repeating a claim about the engine that you did not verify yourself.

Entry format, admission test and the append rule: `references/traps.md`.

---

### An error count is a count of victims, not of causes — abstract bases multiply
**Symptom:** 16 × `Could not resolve cross-reference: No Verse.SoundDef named Pawn_Melee_Punch_HitBuilding found to give to Verse.RaceProperties`. Sixteen looks like a widespread problem across many mods.
**Cause:** **two** lines of XML, in two `Abstract="True"` base ThingDefs (`AsimovNonEnergyAutomatonBase`, `JDSSWCIS_Droids`). Every concrete race inheriting a base inherits the dangling reference and fails to resolve it independently, so one authoring mistake bills once per descendant.
**Fix:** none needed — the engine falls back with *"using undefined sound"*. Divide before you panic: N identical messages naming the same missing def usually means one mistake in an abstract base with N-ish descendants, so search `Abstract="True"` defs for the reference first.
**Recurs when:** triaging by volume — severity comes from the `wanter` (SKILL.md §7), not the tally; a large count is not automatically severe and a small one is not automatically safe.

---

### A strictly read-only live-bridge call hung the game and cost a 23-minute load
**Symptom:** `rimworld/list_debug_action_roots` returned but slowly; `rimworld/search_debug_actions` never returned. `Player.log` stopped mid-line, the socket timed out at 60 s, and Windows raised `AppHangB1` and closed RimWorld. Nothing had been mutated — the calls were pure discovery.
**Cause:** bridge tools execute **on the game's main thread**. Both of those build RimWorld's debug-action node graph, and across 562 mods that build never completed — a livelock, not a deadlock: CPU pinned, log still growing, until the process was killed.
**Fix:** never run enumerating discovery tools against a game you care about — learn the paths on a throwaway quick-test colony, then use the known path on the real one. The vanilla surface is also obtainable fully offline: parsing `[DebugAction]` attributes out of `Assembly-CSharp.dll` yields all **411** of them with categories and target kinds.
**Recurs when:** any in-process bridge tool named list/search/discover — classify bridge tools by how much work they do on the thread that must keep responding, not by whether they mutate state.

---

### A failed post-long-event action costs only itself — the queue continues
**Symptom:** `Could not execute post-long-event action` was rated near-top severity for a full day, on the folklore belief that one throw abandons the rest of RimWorld's post-load queue for every mod. The log line *sounds* fatal.
**Cause:** the IL says otherwise — FAT header with an EH section, a typed `catch(System.Exception)` over an **18-byte** try containing a single `Action::Invoke`, and a handler whose `leave` targets the **loop increment**. It is `for (…) { try { list[i](); } catch { Log.Error(…); } }`. One failed action costs one action.
**Fix:** severity is per-action. Retracted across all five files that restated it, and a correction owed on the upstream bug report that cited it.
**Recurs when:** any claim about **engine behaviour** rather than an observed log string — it will be used to predict things you have not observed, so re-derive it from the IL, the decompiled source or an authoritative citation before it justifies a mod removal or an outward-facing report.

---

### The same mod stayed dead through two correct fixes, for three different reasons
**Symptom:** `Error in static constructor of ChooseWildAnimalSpawns.Main` on three consecutive loads, always thrown from `BiomeDef.CommonalityOfAnimal`, and twice running with the *identical* `ArgumentNullException: Value cannot be null. Parameter name: key` at the identical frame.
**Cause:** three unrelated bugs converging on one line, `cachedAnimalCommonalities.Add(key, value)`. Load 1: `ArgumentException` duplicate key — `Armadillo` registered from both directions. Load 2: `ArgumentNullException` because the **BiomeDef** was null (our own `<li>` bug). Load 3: same exception because the **PawnKindDef** was null — five unresolved `BiomeAnimalRecord` entries injected by a compat patch guarded on the mod rather than the def.
**Fix:** each one separately. An exception that keeps the same *type* at the same *frame* can still be a different bug, so ask "what is null this time, and who put it there", never "is it still broken".
**Recurs when:** any single `Dictionary.Add` reachable from several feeders — the frame identifies the *victim*, never the cause. Diff the surrounding evidence between loads instead of comparing the exception line.

---

### A correct general principle applied to the WRONG SET — and the leading question that launders it
**Symptom:** a seat reviewed a 24-key removal list, recognised Anomaly creature defs in it, and withdrew nine of them on the grounds that *"deleting defs destroys the reskin donor library the owner said to keep."* **The principle is true. The list did not contain a single donor.** The owner had already separated keeps from rejects, and **the two sets never intersected** — the nine keys were verdicts the owner had personally given, and they were spent. ⚠️ **The compounding failure was worse than the edit: the finding was taken to the owner as a question built on the false premise, the owner answered the question as asked, and the answer was then written into `V1_SCOPE.md` as doctrine marked "do not re-propose."**
**Cause:** ⭐ **the reasoning survives review, which is precisely what makes it dangerous.** Nobody rejects "do not delete your donor assets" — it is correct, it is well argued, and it was reached from evidence. What was never checked is **what the argument was pointed at.** The mechanism had been verified in detail (how Cherry Picker's PawnKindDef branch differs from its ThingDef branch, read from decompiled IL); **the premise — that these particular defs were donors — had not been checked at all.** A true statement about a set you have not enumerated is not a finding, it is a guess wearing a proof.
**Fix:** two checks, both cheap.
1. 🔴 **Does the removal list INTERSECT the keep list?** Enumerate both and compare. Two minutes. If the answer is "no", the donor argument does not apply and the objection evaporates.
2. 🔴 **Before escalating a finding to the owner, verify the PREMISE, not just the mechanism.** *"I confirmed how the tool works"* is not the same as *"I confirmed what it is aimed at."* **A leading question is worse than a wrong edit**, because the owner's answer converts your error into their ruling — and a ruling gets written down, propagated to other seats, and marked settled.
**Recurs when:** any review that reasons from a category rather than from the list — "these are all X, and we must not remove X." ⚠️ **The tell is a *category noun* doing the work in your own sentence** ("the donor library", "the vanilla defs", "the quest content") where a specific enumeration should be. **Generalises to** every escalation: state the principle, then name the members it applies to. If you cannot name them, you have not finished checking.
