# Designer delegation intake repair — Stage 2

System item: `RIMMANDRAKE_FIX_DESIGNER_DELEGATION_UNREAD_REPLY`. Published implementation: `e7b76afee7f2187c536759d8b2046c6b6aef1f02`. No mod implementation changed.

`owner_uncited` read the OWNER ledger shard but recognized only `OWNER:<tsn>` citations. Valid Evidence-for-Ask calls deliberately use `CONDUCTOR:<tsn>`. A Stage 2 run recording its delegated flagship therefore rejected its own result as a new unread owner reply.

Acceptance: citing a matching recorded Evidence-for-Ask call as CONDUCTOR must consume that call and allow the real Stage 2 open→record→close flow. Uncited calls, numeric-prefix mismatches, ordinary owner statements cited as CONDUCTOR, and events lacking the delegated reason must retain the unread hold.

Tests were written before the fix. The focused fixture failed before the implementation changed: the delegated call remained unread and the actual Stage 2 close reported `an owner event arrived during the run and is not taken in (OWNER:1002); stage 2 reruns with it`. Related feed expectations failed because the same delegated event was stranded.

After the fix, all seven focused checks passed, including the real temporary Stage 2 close and negative controls. Full validation passed:

- `python3 src/RimMandrake/rimflow/selftest_designer_stage.py` — ALL PASS.
- `python3 src/RimMandrake/rimflow/selftest_designer_turns.py` — all passed.
- `python3 src/RimMandrake/rimflow/selftest_designer_chain.py` — PASS.

Publication also reported 13 green tree checks and 19 green pipeline checks. The source recognizes CONDUCTOR intake only when the ledger event has the Evidence-for-Ask ruling and delegated reason; ordinary owner replies still require OWNER citations. This changes intake freshness, not the authority or quotation checks.

Only temporary fixture concepts were opened/closed by the regression. The live LeaningScrub stage is left for its launcher to validate and advance. No bridge, restart or deployment was used.
