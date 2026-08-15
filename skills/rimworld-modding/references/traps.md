# traps.md — earned lessons, by topic

Every entry below cost a real debug cycle. **Read the one file that matches what
you are about to do**, not all of them.

| If you are about to… | Read |
|---|---|
| write or debug a patch, an xpath, or a def | [`traps-xml-and-defs.md`](traps-xml-and-defs.md) |
| trust what a script, grep, census or the def dump just told you | [`traps-tooling.md`](traps-tooling.md) |
| call art missing, wrong, or broken | [`traps-art.md`](traps-art.md) |
| chase a mod that is absent, dead, or ignoring its files | [`traps-mods-and-managers.md`](traps-mods-and-managers.md) |
| believe a diagnosis, or call into a running game | [`traps-diagnosis.md`](traps-diagnosis.md) |
| **write or debug a quest** | **a different skill: `skills/rimworld-quests/`** |

**If you only read one, read `traps-tooling.md`.** The single most repeated
failure in this project is not a wrong patch, it is **a tool that answered
confidently — and answered a different question than the one asked.**

## Appending

At the end of a task, if something surprised you, append it to the matching file.
Keep it short: what it looked like, what was actually true, what worked.

**It goes in only if it is specific, non-obvious and RimWorld-bound** — an error
string, a flag, an xpath, a defName, a number — **and still true today.** General
software or process advice is not a trap and does not belong here; that is what
made this log unusable once already.

If it would change what `SKILL.md` tells you to do by default, put it in
`SKILL.md` instead and do not log it. If `SKILL.md` already says it, do not log it.

**Never number an entry, and never cite one by number, line or heading.** Say
"as per the trap file" and stop.
