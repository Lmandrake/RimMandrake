## spec
🔴 **The owner ruled `VME_Nomad` OUT on 2026-08-20. The file the game actually reads still
has it in.** Same shape as the `Jawa_Patches` deploy trap: the repo copy is not what loads.

| copy | mtime | `VME_Nomad` | `Nomadic_Preferred` |
|---|---|---|---|
| `D:\Luke\dev\Rimworld\src\Jawa\ideoligion\The Salvation.rid` | 2026-08-20 22:44 | **0** ✅ | 1 |
| `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Ideos\The Salvation.rid` | 2026-08-14 15:49 | **1** ⛔ | 1 |

`APPROVED.md` records the drop as *"Done, in both places, in one commit"* — it was done in
the repo and in `JawaTribes.xml`, and **the game's `Ideos/` folder was never one of the two
places.** That is the whole defect.

🔴 **Why this is not cosmetic.** An Ideo is **fixed at world creation** and cannot be edited
afterwards. If the owner picks *The Salvation* at the next world creation, he bakes in the
meme he ruled out — whose forced precept `VME_PermanentBases_Despised` escalates to **−50
mood at 60 days in place**, running mod C# with no shipped source, and whose own description
says it *"will only work when using the vanilla game world system"*. Whether a gravship jump
registers was never verified. ⇒ **This is remake-gated** (see the gate table in
`design/Jawa/worldbuilding/WORLD_REDRAFT.md`) and it is the cheapest item on that gate.

**Do:** copy the repo copy over the game copy. Back the game copy up first — it is the
owner's hand-authored file and the only surviving witness to what he approved on 2026-08-14.
Config-class files never wait on the game being down (`CLAUDE.md`), but the ideo list is
read when the ideoligion screen opens, so it must be in place **before** world creation.

### Two things found alongside, neither of them this item's job
- ⚠️ `Ideos/The Salvation (built).rid` **no longer exists** — only `The Salvation (built).rid.bak`
  (2026-08-14 14:47). The built output appears to have been promoted over the source.
- ⚠️ `build_salvation_rid.py --check` now **refuses**: `name: the 2026-08-08 lock: expected
  exactly 1 match, found 0`. Its edit table looks for `<name>Path of Scavengers</name>` and
  the source already reads `The Salvation`, so its edits are already applied and it can no
  longer re-run. ⛔ **Do not repair it by relaxing the lock** — the lock is what proves the
  source is the source. `design/V2_DREAMS.md:88` still instructs a future reader to run it.

## verify
- `grep -c VME_Nomad` on the game copy reads **0**; `grep -c Nomadic_Preferred` reads **1**.
- `diff` between the repo copy and the game copy is empty.
- The pre-copy backup exists and still reads `VME_Nomad: 1`.
- `python3 skills/rimworld-ideoligion/scripts/validate_save_artifact.py` on the deployed
  `.rid` passes. ⚠️ Pass `--mods-config` if a minimal list is live, or every modded meme
  reads INVALID.

## criteria
CHECK, next load: open the ideoligion screen, select *The Salvation*, and confirm the meme
list shows four memes with no *Nomadism* / *wanderlust* entry, and that the precept list
still carries *Nomadic_Preferred*.
⚠️ The label may read **"wanderlust"** rather than "Nomadism" — `llunak.moreprecepts` is
active and its `NomadPatch.xml` renames the VME meme. Look for either.
