# LESSONS INBOX

One line per lesson, appended by any window at any time — especially at reboot.
Claim only, no essay: `sprite facings: generate individually, composite sheets
drift — seen twice`. **No skill, memory, or doctrine file is edited at reboot
time**; a fresh-context curation session (owner says "curation pass") drains this
file into the right skills, merging rather than appending, and empties it.

*Last drained 2026-09-04 (curation pass): 79 lessons → 15 skills + memory; the
rest were already covered where they belonged.*

---
- `git diff <symlinked dir>` shows NOTHING — a pathspec naming `.claude/skills/<name>` (a symlink) matches only the link file, so the target's real changes are silently absent; diff the real `skills/<name>` path (BENCH 2026-09-04, curation pass).
- The <li> trap third sighting: Inhabited larder/stock, found via the log line naming the WANTER (Verse.ThingDefCountClass) - read the wanter before building instruments; vanilla error lines already attribute.
- A diff-based patch GENERATOR run against a capture taken with its own patch active erases itself (269 ops -> 33, silent) - diff against raw sources or emit unconditionally; caught only because git diff --stat was read before deploy.
- A stored FULL modlist decays against the deployed Mods dir: four live-verified mods were deployed-not-active and silently voided a proof load's premise - before any proof load, diff deployed packageIds vs the active list, not just fingerprints.
- Two windows launching RimWorld near-simultaneously collide invisibly: the bridge file gates DRIVING, not LAUNCHING, and Steam -applaunch on a running instance silently focuses it - my "isolation test" scored another window's session. Before interpreting any load, ask the bridge for the ACTIVE list.
- The vanilla cross-ref error line already names the WANTER type - read it before building tracer instruments; it solved in one grep what an IL sweep and a planned Harmony postfix could not.
- jawa/get_defs params bind as STRINGS: defs='Type/Name;Type/Name' (semicolon-separated, slash not colon), fields='a,b' — JSON arrays throw IConvertible; the client's declared-params guard catches silently-dropped names (BENCH 2026-09-04)
- RimWorld loads a mod's top-level Patches/*.xml BEFORE its subfolder patch files: our own top-level cut removed a node our absorbed subfolder patch then Replace'd - one standing FindMod 'failed' every load, and the abort meant the sequence's later ops NEVER ran; proven by deploy-side bisection at 33s/cycle (BENCH 2026-09-04, ARMOURY_LIGHTSABER_FINDMOD_1)
- Read-then-write on shared ledger state must be TWO tool calls: I batched 'show' with 'reassign' and yanked an item FOUNDRY had claimed 33 min earlier; the show output could only have stopped me if I read it first (BENCH 2026-09-04)
- world_tile_map_generate's SESSION-FIRST call is reliable (mapCount grew 1->2, real map); the fabricated-success trap is specifically the 2nd+ distinct-tile call per session. And the Inhabited debug harness's StuffRoster sets castInstantiated=true, which blocks FillStock - to test stock, trigger InstantiateCast on a fresh place (castInstantiated=false) via 'Stock: dump onto this map' BEFORE stuffing the roster (BENCH 2026-09-04)
- validate_patch --live WITHOUT --defs cannot validate texPath: it scans only each mod's own Textures/, so any texPath served by vanilla or a donor/other mod reads as a false 'pink placeholder' error (27 such false-positives across the absorbed-KotOR + Karrask defs in one run). --live checks DEF EXISTENCE, not textures. Use the full --defs sweep for texPath, and treat --live-only texPath errors as UNVERIFIED (BENCH 2026-09-05)
- rimplace Lua cannot take `#` of a Python list (`#ctx.plan.things` -> "attempt to get length of a POBJECT"); read back placements through the prelude's LAST_PLACED table instead, and a wall lamp is placed on the floor cell IN FRONT of its wall (Placeworker_AttachedToWall), rot toward the wall - never in the wall cell.
