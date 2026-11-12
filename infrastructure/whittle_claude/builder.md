
## This loop's round (appended to the Whittle prompt by loop.sh)

Before anything else read `infrastructure/whittle_claude/common.md` (the project rules and the blockages) and
`infrastructure/whittle_claude/lane_$WC_LANE.md` (what your lane may touch). The item is `$WC_ITEM`; your Whittle
directory is `$WHITTLE_DIR`; its `MODE` file says `whittle` or `pilot`.

- Mode `whittle`: build until every STATEMENT bullet is true and shown by evidence, then let the judge pass it.
- Mode `pilot`: this is a Test Pilot sitting, not another code-and-retest round. Run `rimflow pilot $WC_ITEM` and follow
  the brief it prints, with the `test-pilot-sitting` skill: experiments that discriminate between hypotheses, each
  recorded in NOTES.md, then the fix or the filed finding.
- Live evidence comes only from your lane's game, held through the bridge lock as your lane file says, and released
  before you stop. Record proof runs on the item the way its proof script does (modcheck, or `rimflow live`: read `--help`) so the ledger
  carries them.
- Commit and `./publish` your work as it lands (explicit paths). Do NOT close the item here: the wrap-up phase closes,
  parks or drops it after checking your DONE.md and the judge.
- If you cannot go on without the owner, write the question as common.md says, put one line in `$WHITTLE_DIR/BLOCKED.md`
  naming it, and stop.
