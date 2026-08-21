## spec
Owner, 2026-08-20: put faction-to-faction AND faction-to-player relations on the
bridge. Measured gap, read off the companion source today, not assumed:
  * `jawa/set_faction_relation` EXISTS but is hardcoded to `Faction.OfPlayer` —
    it resolves one `target` and sets its relation to the player. There is no
    way to name a PAIR.
  * `jawa/list_factions` reports `hostile` and `goodwill` from
    `faction.HostileTo(player)` / `faction.PlayerGoodwill` — player-relative only.
    ⇒ **the pairwise relation matrix is unreadable on the bridge today.**
TOOLS:
  `jawa/faction_relations_get`   — the MATRIX. No args -> every ordered pair with
                                   a non-default relation; `faction` -> one row;
                                   `faction`+`other` -> one cell. Report kind,
                                   goodwill and `naturalGoodwill`/`hostilityDisabled`
                                   where they exist, per pair, BOTH directions
                                   (RimWorld stores relations per-faction, so A->B
                                   and B->A can disagree and that disagreement is
                                   the bug this tool exists to find).
  `jawa/faction_relations_set`   — write one pair, either direction or both.
                                   Args: `faction`, `other` (defName; `Player`
                                   accepted and resolves to `Faction.OfPlayer`),
                                   `kind`, `goodwill`, `both` (default true),
                                   `sendLetter` (default false), `dryRun`.
  Extend `set_faction_relation` OR supersede it — do not leave two writers that
  disagree. If superseded, keep the old name answering with a deprecation note;
  E1's raid work calls it.
Read the real API off 1.6 source through RimSage before writing a line —
`Faction.RelationWith` / `RelationKindWith` / `GoodwillWith` /
`TryAffectGoodwillWith` / `SetRelationDirect` / `FactionRelation` /
`FactionRelationKind`. 🔴 Do NOT guess a signature; `TryAffectGoodwillWith` and
`SetRelationDirect` have different letter/goodwill-clamping behaviour and picking
the wrong one is how a write reports success and moves nothing.
New tools go in `JawaBenchWorldTools.cs` (the class is already `partial`).
Build: `python.exe src/RimMandrake/bridgetools/build.py --gm --apply`, game DOWN.
⚠️ `--gm` is mandatory here or the build silently drops `jawa/fire_incident` and
`jawa/send_letter`.

## verify
build 0 warnings 0 errors; `rimbridge/list_tools` counts the two new `jawa/` names.

## criteria
🔴 READ BACK OFF THE ENGINE, never the setter returning — every setter here is void.
(a) `faction_relations_get` with no args returns a matrix in which at least one
    NON-PLAYER pair is hostile on a live world, proving it is not player-relative.
(b) Set two non-player factions hostile to each other, then read the pair back:
    both directions report Hostile. Then set them Neutral and read back Neutral.
(c) The asymmetry case, which is the whole reason for (a)'s both-directions rule:
    write ONE direction with `both=false` and confirm the reverse direction did
    NOT move. If it moved anyway, say so — that is a finding about the engine, not
    a tool defect, and it changes what the tool can promise.
(d) The player pair still works through the new tool: `other=Player` sets and
    reads back, and E1's raid path still aims at a named faction afterwards.
⚠️ FALSE PASS: `list_factions` will keep reporting sensible player-relative numbers
no matter how wrong the pairwise matrix is. Never close this on `list_factions`.

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready — ⭐ HALF BUILT AND THE PREMISE IS NOW PROVEN, 2026-08-20.

**built:** `jawa/faction_relations_get` + `jawa/faction_relations_set` written into
`JawaBenchWorldTools.cs`, build 0/0, both names verified in the assembly bytes.
NOT deployed — the game came up before the shutdown window. Commit 7ee7bac.

**measured:** 🔴 THE EXISTING TOOL CANNOT MAKE A FACTION HOSTILE. Proven live on the 577-mod
set, game loaded, against `Jawa_HuttCartel` and `Jawa_DeepwaterCompact`:
  * `set_faction_relation kind=Hostile` -> **success FALSE**, kind stayed Neutral.
    This is `SetRelationDirect` refusing: it bails with a Log.Error when BOTH
    factions have goodwill, which is nearly every pair. The tool's own read-back
    guard caught it, which is the guard doing its job.
  * `set_faction_relation goodwill=-100` -> **success TRUE**, and kind stayed
    **Neutral**, `hostile=False`. A faction sitting at -100 goodwill that raid
    code does not treat as an enemy. The engine never produces that state:
    `CheckKindThresholds` forces Hostile at <= -75, and the tool bypasses it by
    assigning `rel.baseGoodwill` directly. ⇒ a SILENT FAILURE, success and all.
📌 The tool's stated reason for existing is "unblock aimed raids". It cannot.
E1's raid passed against `Empire`, which worldgen had ALREADY set hostile at
-100 — so the tool's premise was never actually exercised.
⇒ **SUPERSEDE, do not extend.** `faction_relations_set` writes both records and
fires `Notify_RelationKindChanged`, and clamps goodwill into the sustaining band.

**remaining:** deploy at the next shutdown window (`build.py --gm --apply`), restart, then the
criteria below. Criterion (c) is AMENDED: one-sided writes are not a feature the
engine offers — the engine mirrors both records itself — so `both=false` exists to
TEST the asymmetry, and the tool labels the result desynced rather than normal.
