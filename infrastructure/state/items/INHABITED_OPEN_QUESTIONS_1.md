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
