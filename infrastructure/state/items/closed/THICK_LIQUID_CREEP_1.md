
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row FL-2 there is the spec:

| FL-2 | Thick liquids visibly creep. Today, liquid that reaches a cell can pass straight on to the next cell within the same pulse, so on a long canal tar can race almost as fast as water. Cap how far a fill front moves in one pulse, so tar, slime and blood crawl at their stated speed. | Kernel: a recipient that was filled this pulse cannot donate again in the same pulse (or a per-fluid hop limit per pulse). Add a fixture that measures how fast the front travels down a 40-cell channel for water and for tar. | M | med. This is a kernel change, so the oracle and fuzz must stay green. Water may slow too unless its limit is generous. | FlowWorks (Sump tar inherits it) | RM_FlowKernel.cs:224-240: recipients loop, and a filled recipient becomes a donor in the same pulse. Viscosity is only a stride that decides which pulses a liquid moves on (RM_StockMath.cs:389). No selftest measures front speed (grep "front" in SelfTest). Not in FLOW_ORDER_EXTERNAL_INPUT_1's spec. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify THICK_LIQUID_CREEP_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A2 (L2): a tar channel on a bridge map fills at the stated speed in game
Evidence is the Player.log line or bridge state read the criterion names.
