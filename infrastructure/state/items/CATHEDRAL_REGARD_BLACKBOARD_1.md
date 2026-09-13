
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Python, GM external blackboard alongside Imperial Heat and Hutt Interest
(kyber spec §2/§3, build_plan.md §2/M4 pattern). Builds:
- **Regard counter** — never a save stat, never a UI gauge (arc §0). Inputs per
  arc §2: manners (polls kit §1 band history via bridge), Assailant-register
  mission completions (story flags), Heat low/falling while on Cathedral ground
  (reads the Heat number it already shares a blackboard with), zero-mindstone-
  sales standing credit, §4 restore choice (mirrors origin-canon §4 pricing,
  adds nothing), misdirection-quest success (item 5). Losses: Heat brought
  near, every mindstone/kyber sale, sacrilege mirrored from faction-13 goodwill
  deltas (one act, two ledgers — the blackboard polls goodwill, no double
  machinery), anomaly sales **by volume not buyer** (A5: running sales-volume
  counter over bolt-shed curiosities + eel-catch). Never-movers: bulk salvage,
  provoked-Sentinel fights, anything unknowable.
- **Stage machine** — WARY/TOLERATED/VOUCHED/REVEALED = f(Regard, faction-13
  goodwill, story flags) per arc §1; knowledge one-way, standing two-way;
  REVEALED entered only by item 7's beat.
- **Exposure pressure** — the §6.1 number (fed by Heat-near-Cathedral, sales
  volume, pursuit events resolving on Cathedral ground); go-dark demotion to
  WARY posture at threshold. The completion chain is item 8's, this item owns
  only the number and the dark flip.
- Consequence outputs fire through the existing bridge/CQF injection lane
  (kyber §2); this item publishes stage + dark-flag for items 2–8 to consume.

## verify
Arc §8 seed 1, in shadow mode: each §2 input moves Regard in the stated
direction; bulk salvage and provoked-Sentinel kills move nothing; a crafting
consumption moves no sale counter (kyber §2 sold-vs-crafted caveat); no input
writes any save stat; demotion 2→1→0-posture works; REVEALED unreachable from
Regard alone.

## criteria
Counter, stages, exposure pressure live in shadow mode with logged would-be
consequences; thresholds/rates in one tunable table (GM tuning owns numbers);
dark flip demotes posture without erasing history.

**Depends on:** GM blackboard M4 (kyber build_plan §2) live in shadow mode;
faction-13 goodwill readable over the bridge (kit §1 ledger is vanilla — no
kit C# strictly required to start). **Waited on by:** items 2–8 (all).
**Seat/needs:** FOUNDRY; offline Python + bridge for polling tests; game-up
only for end-to-end shadow runs. Not row-3.
