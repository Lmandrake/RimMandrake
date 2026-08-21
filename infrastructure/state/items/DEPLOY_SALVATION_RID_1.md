✅ **SETTLED 2026-08-21 — the hold is lifted and the direction is decided.** The owner ruled
`VME_Nomad` stays and closed the question (`NOMAD_GRAVSHIP_RESET_PATCH_1`).

⇒ **Reconcile with the meme IN.** Restore `VME_Nomad` to the repo copy
`D:\Luke\dev\Rimworld\src\Jawa\ideoligion\The Salvation.rid` so it matches the game copy,
which already has it and must not be overwritten.
⛔ **Do NOT copy the repo `.rid` over the game `.rid`.** The game copy is the correct one.
✅ `Nomadic_Preferred` stays too — it is a precept, costs no meme slot, and holding both was
always available.
**Done when:** `diff` between the two copies is empty and both read `VME_Nomad: 1`.
⚠️ An Ideo is fixed at world creation, so this must land before the next remake.

---

🔴 **REDIRECTED 2026-08-21 — the owner reversed the drop: *"But I like VME_Nomad!"***
⇒ **The reconcile direction flips.** The repo copy dropped the meme on 2026-08-20; the game
copy still has it. His preference is to keep it, so the file that is now WRONG is the repo
copy, not the game copy. ⛔ **Do not copy the repo `.rid` over the game `.rid`** — that would
execute the reversed ruling.

⏸️ **HELD on one measurement, and this is not a re-litigation of his preference.** The NPC
side is already restored and free (`NOMAD_MEME_RESTORED_TRIBES_1` — the harsh precept carries
`enabledForNPCFactions: false`). The **player** ideo is the only place
`VME_PermanentBases_Despised` can actually fire, and it escalates to −50 mood at 60 days in
one place. Whether that ever bites us depends entirely on whether a **gravship launch resets
its counter** — and this campaign is a gravship campaign, so the colony moves constantly.
🔑 Early reading of `VanillaMemesExpanded.dll` finds no `lastResettledTick` reference at all
(that is the *vanilla* field `Nomadic_Preferred` reads) and does find
`VanillaMemesExpanded_SettlementAbandonUtility_Abandon_Patch`, so the VME counter appears to
reset on **settlement abandonment**, by a route of its own. Whether a gravship launch takes
that route is being read out of the IL now.
- **If it resets:** restore `VME_Nomad` to the repo `.rid`, reconcile both copies with it IN,
  and this item closes with the owner keeping the meme everywhere.
- **If it does not:** the owner gets told the number — his colony accrues to −50 mood and
  only abandoning a settlement clears it — and he rules again with that in hand.
⚠️ Either way **both copies must end up identical**, and an Ideo is fixed at world creation,
so this must be settled before the next remake.

---

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
