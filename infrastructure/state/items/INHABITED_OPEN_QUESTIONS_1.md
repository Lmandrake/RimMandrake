## spec
🔴 **Raised by the owner's 2026-08-20 reversal** — the code is v1 and is being
built, so `INHABITED_DESIGN.md` §7's open questions stopped being academic. The
eight `INHABITED_*` items are filed in `queue/BUILD.md` and seven of them are
executable; these are the gaps that are DECIDE's and nobody else's.
✅ **ALREADY RULED while filing, so BUILD is not blocked on it:** cast size
distribution, written into `INHABITED_GENSTEP_CAST_SPAWN_1` — hive foundry 14–22,
waystation 10–16, refinery 8–14, nomad camp 6–12, trade moot 5–9, homestead 4–7,
droid enclave 3–6.
⏳ **STILL OWED, in the order BUILD will hit them:**
1. 🔴 **The four missing character fields — xenotype, pawnKind, apparel, skills.**
   None of the 269 authored characters carries any of them; the prose has name,
   race-as-a-string, gender, age, traits, two backstory lines and a hook.
   `CAST_ROSTER_MACHINE_READABLE_1` is building the parser around the gap with
   those four left optional and empty. ⛔ **Nobody may guess them** — a guessed
   xenotype ships a wrong-looking person into a world that is frozen.
   ⚠️ The right instrument here is a `review-sheets` build, not 269 questions in
   chat: pre-fill every one from the prose and let the owner disagree.
2. **The twelfth faction has no cast.** Deepwater Compact (*the Balance*) is
   tabled at `INHABITED_DESIGN.md:485-497` and has no `INHABITED_CAST_*.md`
   beside the other eleven. ~25 characters, DECIDE's own authoring.
3. **How the player initiates trade** with a cast that is not a settlement (§7).
4. **What the gravship's arrival triggers** — which casts break on sight, on what
   test (§7). This is FATE:flee-arrival and no item can implement it yet.
5. **Whether a place can be re-occupied by a DIFFERENT faction** after
   abandonment. `state: Squatted` is reserved for it in
   `INHABITED_WORLD_OBJECT_CORE_1` and is unspecified.
⛔ **Do NOT answer 3, 4 or 5 before `ROSTER_SURVIVES_OFFMAP_PROOF_1` reports.**
§3.4 says that soak can invalidate the container choice, and all three answers
are shaped by whether the roster is genuinely frozen.

## verify
each of the five is either ruled in writing or struck as void, and the ruling is
written INTO the item in `queue/BUILD.md` that waits on it — not only here.

## criteria
—
⭐ **BUILD's return, overnight 2026-08-20 — item 1 is now the ONLY thing blocking content,
          and the instrument for it exists.**
          - `CAST_ROSTER_MACHINE_READABLE_1` is **done**. All 269 characters are
            `Inhabited.CharacterDef`s in `src/Jawa/Inhabited/Defs/CastRosters/`, and all
            **807 traits and every named degree resolve** against the def dump. The four
            fields are emitted empty, as instructed.
          - ⇒ **The `review-sheets` build you wanted has a real data source now.** It does
            not need to parse prose: read the 269 defs, show `label · race · ageText ·
            traits · hook` per row, and collect the four missing fields. The prose files
            stay the source of truth for everything else.
          - 🔑 **A pre-fill hint that costs nothing:** `race` is already a clean prose
            string per character (`Ugnaught`, `Chagrian`, `B1-series line infantry`), so
            xenotype and pawnKind can be pre-filled by grouping on it — there are far fewer
            distinct races than characters, and the owner then disagrees per RACE rather
            than per person.
          - ⚠️ **The spec's measurement that age is an int on every entry was wrong** and
            the parser now handles eight forms, including the Jawa robe-hem count and one
            droid who lies about his age. Detail is in `CAST_ROSTER_MACHINE_READABLE_1`.
            Nothing for DECIDE to rule; noted so the same measurement is not trusted twice.
          - 🔑 **Item 2, Deepwater, is reported cleanly by the tool every run** rather than
            failing it, so writing that cast is unblocked whenever you want it.
          - 🔴 **Items 3, 4 and 5 stay correctly held** behind the soak. BUILD found and
            fixed TWO of the three ways the container could have failed, both on disk, so
            the soak is now a narrower and more honest test than when this was written —
            see `ROSTER_SURVIVES_OFFMAP_PROOF_1`.

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready — for DECIDE

## ruling
**DECIDE, 2026-08-21. All five are closed. `INHABITED_DESIGN.md` §7 is now "The five that
were open — answered", and it is the place to read them, not this item.**

| # | was | now |
|---|---|---|
| 1 | the four missing character fields | ✅ **the owner answered it 2026-08-21**, and narrower than this item framed it: race on all 269, kit and skills only where the prose earns them. ⇒ `CAST_RACE_AND_KIT_FIELDS_1`. ⛔ The `review-sheets` build this item proposed is **not** needed — 269 rows × 4 fields was the right instrument for the question as asked, and the question shrank |
| 2 | the twelfth faction has no cast | ⏳ `DEEPWATER_CAST_ROSTER_1` — authoring debt, filed, not blocked on anything |
| 3 | how the player initiates trade | ✅ **§7.1 — trade is a PERSON.** One cast member carries `pawn.trader.traderKind`, copied from `IncidentWorker_VisitorGroup.cs:96-97`. No dialog on the world object, no new UI |
| 4 | what the gravship's arrival triggers | ✅ **§7.2 — one ratio, three faction states.** `Σ combatPower(cast) / Σ combatPower(landing party)`, with hostile factions fighting rather than fleeing |
| 5 | can a place be re-occupied | ✅ **§7.3 — yes, but never by the faction you drove out** |

🔑 **The through-line, and it is the constraint I held myself to:** every answer is built
from a number RimWorld already computes — `combatPower`, `goodwill`, `isFighter`,
`TraderKindDef`. §4.1 forbids this design growing a number of its own, and an arrival test
or a squatting rule with its own score would have been exactly that.

⚠️ **Two traps named where BUILD will hit them, not here:**
- `pawn.trader` **only exists if the kind's `trader` is true** (`PawnComponentsUtility.cs:247`).
  A trader without the tracker cannot be traded with **and nothing logs.**
- Arrival-flight costs goodwill **only when the player lands on the site's own tile.**
  Ungated, flying across the planet would strip the player's relations with everyone he
  overflew, with no way for him to know.

⭐ **What stays open is not on this list.** The `Caravan`-pattern 100-day soak (§3.4) is
still the gate on the whole architecture, and two of its three failure modes have already
been found and fixed on disk. Do it first.
