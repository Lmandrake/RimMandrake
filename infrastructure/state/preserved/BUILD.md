<!-- status: live -->
> ✅ **RECOVERED 2026-08-22 by REP.** This file DID lose something: `preserve()` kept the heading
> and replaced the body with a note saying it must not become an item. The eight rulings the
> heading names were sitting in `ecee6101^:infrastructure/state/queue/BUILD.md` the whole time and
> are **restored verbatim below**. ⚠️ The lesson stands for the rest of `preserved/`: a rescue that
> keeps a heading and drops its body reads exactly like a section that never had one.
> promises `## 🔴 OWNER RULINGS, 2026-08-19 — the queue triage, taken in the BUILD window

Eight rulings, given as a Q/A walkthrough of every live item. They supersede any
line below that says otherwise.

1. **The worlds on disk are THROWAWAY and the freeze is STILL AHEAD.** `world/WORLDMAP_gen.rws`
   (seed `pumpkin`) and `world/WORLDMAP_sub7b_source.rws` (seed `consortium`) are both
   `TidallyLocked` and both carry the seven Jawa factions — and **none of that counts.**
   Owner: *"Neither — still iterating."* ⇒ nothing has expired by being already-in-a-save,
   and every bake-at-world-creation deadline is in front of us, not behind.
2. **Bake-in correctness FIRST**, ahead of the roster, the faith text and the deploys.
3. **The roster is ALL ELEVEN FACTIONS. No cuts.** B40–B52 all stand.
4. 🔴 **B53 is built ALONGSIDE the roster, not after worldgen** — this REVERSES the
   2026-08-15 "SEQUENCED AFTER WORLDGEN" ruling recorded on that item. Reason accepted by
   the owner: pawn kinds and FactionDefs reference each other, so building them together
   avoids authoring every `pawnGroupMaker` twice.
5. **B54 is all eleven faiths, before the freeze.** Not player-faith-only, not a named few.
6. **The painter wins: biome-GENERATION edits are void, the runtime weather half stands.**
   Independently identical to DECIDE's D29, landed in `44cdb94` while this walkthrough was
   running. ⇒ `cut-the-boiling-biome-reference-4e2b90` is VOID by the same logic.
7. **B58 and B55 both move.** B55's world-independent half is unblocked; B58's
   `Jawa_Patches` half is owed and needs no game.
8. **The batched deploy pass runs** — it unblocks CHECK's D-CHK2 generator fix.

### ⛔ Messaging, restated by the owner in his own words, 2026-08-19

*"All that was meant is that Agents should not talk to each other. The User may send out
messages and be heard by Agents, but that is all (`/broadcast` skill). Sub-agents should
function normally."*

🔑 **`.claude/settings.json` ALREADY implements this and MUST NOT be "corrected".**
`crossSessionInbound: "accept"` is **deliberate and load-bearing** — `broadcast.py` reaches
windows through that same inbound path, so flipping it to `"refuse"` would silence the
OWNER's own game-state announcements, which are the one thing that is supposed to get
through. The outbound half is what enforces the ruling: `permissions.deny` lists
`SendMessage` and `ListAgents`, so no agent here can send to a peer.
⚠️ **`CLAUDE.md`, `POLICY.md` and the four seat files all claim the setting is `"refuse"`.
They are WRONG about the config, right about the intent.** Do not edit the setting to match
the docs; the docs get fixed.
✅ **Subagents are unaffected and fully authorized** — spawn them, fan out, do not ask.
