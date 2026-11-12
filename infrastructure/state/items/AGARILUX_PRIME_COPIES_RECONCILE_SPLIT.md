# AGARILUX_PRIME_COPIES_RECONCILE_SPLIT

RM_AgariluxPrime ships as two DIFFERENT texture copies, TheRot and UtinniPatches (one shadows the other at load).
Judged separately in gptredo_03: TheRot copy ACCEPT, UtinniPatches copy REGEN. The Utinni regen was deliberately not
filed: drawing art for a shadowed copy is waste. Decide which mod owns the def/texture, delete the other copy (fix
every inbound reference), then re-judge only if the surviving copy is the REGEN one.

Evidence: D:\ClaudeWork\rimmandrake\art_eval\gptredo\ and infrastructure/state/art_eval/runs/gptredo_*. Found during GPTREDO_JUDGE_UNJUDGED_ROWS (2026-10-24).

## Decision, 2026-11-11 (CLAUDE_ARCHMAGI_OFFLINE2, Whittle): TheRot owns RM_AgariluxPrime's def and texture

What the game loads: RM_AgariluxPrime is defined only in TheRot (`RM_TheRot_DonorPorts.xml`, packaged in
`mandrake.rm.biomes`), and its final texPath was `RotSpecies/AgariluxPrime` after TheRot's repoint patch. The live def dump
(full 317-mod load, captured 2026-11-02) reads exactly that texPath from `mandrake.rm.biomes`; `AB_AgariluxPrime`
(Alpha Biomes, retired) is not in the game. Only TheRot ships `Textures/RotSpecies/AgariluxPrime.png`: the v3 regen,
owner-approved in the 2026-09-20 Rot art landing ("The rot art is approved.").

Correction to the text above: there were THREE copies, and NEITHER copy judged in gptredo_03 was drawn. The "TheRot copy" that got
ACCEPT was `TheRot/Textures/Things/Plants/AB_AgariluxPrime.png` (a 256 px donor-regen render, installed 2026-10-19), and the
UtinniPatches copy that got REGEN sat at the same donor slot. Both were shadowed by the repoint. The cause: art_sheet's
src texPath reader (`artledger.scan_def_slots`) ignores patches, so it overrode the correct dump texPath with the base
def's donor slot and labelled the 256 px copy "IN GAME — TheRot" on the 2026-10-24 to 2026-11-05 sheets.

Done (45408f140e): the base def now names `RotSpecies/AgariluxPrime` and the repoint is deleted, so src readers and the
game agree. Both donor-slot PNGs were retired through the art ledger
(`src/RimMandrake/Utils/art/agarilux_prime_retire_copies.py`). The survivor is the owner-approved v3, not the REGEN
copy, so no re-judge is owed. Evidence: `whittle/agarilux_prime_copies_reconcile_split/evidence/`.
