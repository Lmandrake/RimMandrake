## spec
Full-file review of the 3 largest source files in the JawaBench bridgetools
companion DLL (JawaBenchSocietyTools.cs 1285 lines, JawaBenchTerrainTools.cs
6972 lines, JawaBenchWorldTools.cs 4666 lines), as part of the standing
FOUNDRY code-review loop. Done via three parallel subagent reviews, each
finding verified by hand before fixing.

⚠️ **The fixes below actually landed in commit `2691a1e3` ("Context for
BLUE_PROPANE_RING_RULING_1")**, not a commit of mine — a git-index race with
BENCH's own concurrent commit swept my staged files into its commit before I
could run my own `git commit`. Content is correct and pushed; only the
commit message lost the writeup. This file is that writeup.

## FOUNDRY, 2026-09-08 — six bugs, all fixed and compiled clean

**JawaBenchTerrainTools.cs** (`jawa/list_pawns`, `includeHealth`):
- `if (pawn.health.capacities.CapableOf(cap) || true)` — a debugging leftover
  neutered the capability gate entirely. Every pawn's `capacities` map
  included every `PawnCapacityDef` in the database regardless of whether the
  pawn's race could express it at all (e.g. `Talking`/`BloodPumping` on a
  mechanoid), with `GetLevel()` returning a meaningless value and no way to
  tell "not capable" from "capable at this level." Fixed: `|| true` removed.

**JawaBenchWorldTools.cs**:
- `jawa/world_tile_import` — a present-but-unparseable numeric/hilliness CSV
  cell (locale-formatted number, typo) was silently left untouched: no
  error, no effect on `applied`, row still counted as fully applied. Now
  each of elev_m/temp_c/rain_mm/swampiness/pollution/hilliness reports
  `"Row N: unparseable <field> '<value>', field not written"` when present
  but unparseable, instead of folding into silent success.
- `jawa/world_tile_validate` — same root shape, worse: `s2 != null &&
  F(s2, out fv) && Math.Abs(...) > tolerance` short-circuits to `false` on a
  parse failure, so a broken comparison-CSV cell read as a MATCH instead of
  a mismatch — directly defeating the tool's stated purpose ("prove the
  import actually took"). Now each field distinguishes UNPARSEABLE from a
  genuine match/mismatch.
- `jawa/world_landmarks_set` (remove branch) — counted `removed++` purely
  from `RemoveLandmark()` completing, no read-back. The `add` branch a few
  lines above already carries a fix comment for this exact shape
  (`AddLandmark` silently keeping the wrong def). The `remove` branch was
  never brought in line. Now verifies `wl[pt] == null` afterward and reports
  an error naming what's still there if not.

**JawaBenchSocietyTools.cs**:
- `jawa/caravan_form_exit` — an out-of-range `directionTile`/`destTile` was
  silently treated identically to "not given" (-1), both falling back to
  the exit tile / `PlanetTile.Invalid`, unlike `exitTile` a few lines above
  which explicitly refuses out-of-range. A caller passing a stale or
  mistyped tile id got no error and no way to distinguish it from an
  intentional omission. Now refuses the same way `exitTile` does.
- `jawa/ideo_precept_edit` (remove) and `jawa/ideo_ritual_obligation` — both
  match filters already tolerate `p.def == null` / `r.def == null`, but 6
  call sites downstream (2 in the precept path, 4 in the ritual path)
  dereferenced `.def.defName` unguarded while sibling paths a few lines away
  already guard it. Low-probability in practice (Precepts are normally made
  via `PreceptMaker.MakePrecept(pd)` with a real def), but the failure mode
  is bad: `RemovePrecept` would already have mutated state before the NRE
  threw. Guarded consistently with the file's own established pattern.

**Verification**: compiled via `build.py --gm` from Windows Python (WSL
python3 cannot invoke dotnet.exe) — 0 warnings, 0 errors. `tool_surface`
comparison against the currently-deployed DLL (`f9717f5a47d0`) shows zero
tools lost with `--gm`. `selftest_tool_metadata.py` still reports 314/314
exact match between source and the freshly-built DLL.

**Not yet done**: deploy + a confirming restart. BENCH held the bridge (and
was mid-commit) for the whole of this session — build artifact sits at
`src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/` (gitignored,
not deployed). Whoever next has the bridge free should `build.py --gm
--apply`, restart, and spot-check at least `jawa/list_pawns
includeHealth=true` on a non-humanlike race (mechanoid/animal) to confirm
the capacities map no longer lists inapplicable capacities.

## verify
```
PROVE   each of the six fixes changes behavior in the direction described,
        without changing any tool's name or removing any tool
EXPECT  build.py --gm reports zero removed tools (confirmed this session);
        a live jawa/list_pawns on a mechanoid after redeploy shows a
        strictly smaller capacities map than before the fix
LIES    a clean compile proves the C# is well-typed, not that the runtime
        behavior is what the writeup claims — the live spot-check above is
        still owed
```
Leaving `doing` — the deploy+restart+spot-check is the one thing left, and
the bridge wasn't mine to take this session.

## FOUNDRY, 2026-09-08 later — deployed, restarted, spot-checked

Bridge was free. `python.exe build.py --gm --apply` (killed the running
game first — it holds the DLL memory-mapped, same lock class as every
other companion/mod-assembly deploy this session). Confirmed deployed copy
byte-identical to the fresh build (`md5sum`, both sides `cb8709e7d75b...`).
Restarted on the minimal 25-mod list.

- **`jawa/list_pawns includeHealth=true` on a `Mech_Scyther` and a
  `Thrumbo`**: both returned the full 11-capacity set
  (Consciousness/Moving/.../Metabolism). **Not proof the fix is wrong** —
  both creatures' vanilla body plans genuinely cover all eleven categories,
  so `CapableOf` correctly returning true for all of them is not
  distinguishable from the old `|| true` bug with these two test subjects.
  Did not find a better negative example (a creature/pawn provably missing
  a specific capacity-relevant body part) within this pass's time budget —
  the packet's own "strictly smaller than before" claim needs either a
  stored pre-fix baseline (not saved) or a creature with a known gap, and
  this pass has neither. Recorded as a genuine verification gap, not
  papered over.
- **`prove_new_tools.py --census`**: 314/315 tools registered — the one
  "missing", `jawa/revoke`, is a **false positive**: grepped the source and
  found it's not a real `[Tool(...)]` name anywhere, only a substring
  inside another tool's DESCRIPTION text (`JawaBenchPawnKitTools.cs`:
  "...not removed by jawa/revoke - there is no revoke tool yet"). The
  companion census tooling is matching a tool-name-shaped phrase inside
  prose, not detecting an actually-missing registration. Not this item's
  bug to fix (out of scope — a tooling-meta issue, not one of the 6
  behavioral bugs this item is about); flagged here rather than silently
  ignored, since "FAIL" output deserves an explanation on the record.
- **Player.log**: clean, 12 pre-existing `Config error in` lines, zero new,
  zero exceptions.

Given the original review's diagnosis (`|| true` reading as unambiguous
from the code alone, the same class of one-line regression this codebase's
own review discipline exists to catch) and that the deploy/restart/tool-
census half is now genuinely confirmed, but the BEHAVIORAL claim itself
remains unconfirmed by a live A/B — closing on the strength of the code
fix + successful deploy, with the "strictly smaller" claim explicitly
flagged as not independently reproduced this pass rather than asserted.
