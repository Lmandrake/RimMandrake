## spec
found-by: BENCH detached helper on RIMMANDRAKE_PROVE_GSS_SWITCHBOARD_DENSE, 2026-11-12, reading the speed_20261112 GSS proof_all
runs on SteveDesktop (evidence `D:\ClaudeWork\rimmandrake\conductor\carryover_20261112\gss\steve\gss_before.json`, `gss_after.json`).

**MOD, not yet attributed to a line.** Two log errors charged to GSS:

1. Run 1 (first start after a companion swap): `System.ArgumentException: Illegal characters in path.` at
   `System.IO.Path.Combine` from `Verse.ContentFinder`1[T].TryFindAssetInModBundles`, at startup. It failed both
   L2_startup_log_clean and Z_log_budget. L2 counts only entries whose message or stack names GimmeSomeSlack, so a GSS frame was
   in the stack, but both rows cut the text at 200/240 chars and the frame was lost. A fresh second start did not show it.
2. Run 2: `DrawGUITexture: texture is null`, with no stack (thrower `?`), charged by Z_log_budget, which charges an unresolved
   stack to the mod by design. Only GUI code calls this path; GSS's DrawSwatch skips a null texture, so its source is unknown.

Since 4ff9d1df8b both rows keep the first stack frames that name GimmeSomeSlack (`gssFrames` on Z, `@ at ...` on L2).
**Next:** on the next occurrence read those frames and fix the call that passes a path with illegal characters to ContentFinder.
Candidates: CordMaterials.Tex (style slot paths), GimmeSomeSlackMod.DrawSwatch, ConduitVisuals switch textures.

Acceptance test: none yet, the failing call is not identified (intermittent: 1 of 2 starts). Once it is named, a selftest that
feeds that call the bad path.
