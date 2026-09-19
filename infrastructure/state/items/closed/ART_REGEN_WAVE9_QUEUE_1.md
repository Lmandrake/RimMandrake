## spec
Standing owner instruction, reaffirmed 2026-09-11: "Fan out and continue full
belt at all times... there should always be at least one agent regenerating
graphics." Continuation of `ART_REGEN_WAVE4_QUEUE_1` through
`ART_REGEN_WAVE8_QUEUE_1`, same source pool: `art: "improve"` rows in
`design/Jawa/worldbuilding/review/round2/decisions_propagated.json`, same
binding semantics (`infrastructure/artpipe/README.md`, "'improve' semantics"
section) under the owner's `ART_REGEN_WAVE4_SOURCE_DECISION_1` ruling
(2026-09-11T23:56:18Z, `infrastructure/state/ledger/events.jsonl`): full
regen, Star Wars-named creatures keep canon identity, non-SW names free to
be reimagined, heavy black outlines enforced.

Recomputed the eligible pool directly from source rather than trusting
wave 8's own carried-forward count: 51 unique `art:"improve"`, `decision:"in"`
rows with a real biome assignment (`fauna:<biome>:Name` keys, deduplicated
by name across biomes, `homeless:*` rows excluded as a design-call bucket).
Cross-referenced every name spoken for across waves 4-8 (28 names from
waves 4-7, plus `Kinrath`/`Shiro`/`Borcatu` from wave 8 = 31), plus
`AA_Eyeling` (owner explicitly kept the donor art as-is, 2026-09-07,
`IKEE_MYNOCK_ART_REGEN_1`) and `AA_Lockjaw`/`AA_Mantrap` (mid-iteration,
handled separately) = 34 total exclusions. **17 eligible candidates
remained** (one fewer than wave 8's own stated "~18" estimate — that number
appears to have accumulated small rounding across waves' prose; this item's
count was computed fresh from `decisions_propagated.json` and cross-checked
against `infrastructure/artpipe/registry.jsonl`'s job-id history, not
inherited).

**3 creatures picked** (a modest slice, not the whole remaining pool) — all
three are genuine Star Wars canon names, confirmed against
`design/RimStarWars/star_wars_canon_names.md`'s master-bestiary list AND
given real individual descriptions via fresh Wookieepedia web research
(none of the three had an "individually confirmed" entry already recorded
in that doc — this wave adds that detail):

- `Dactillion` (weeping_stones, large) — SW-canon: large winged carnivorous
  reptavian native to Utapau, catches thermal updrafts in the planet's
  sinkholes, strong grasping claws and horns, used as a tamed mount by the
  Utai/Utapaun Security Forces. Identity kept; drawn to that canonical look.
- `Fanback` (weeping_stones, large) — SW-canon: cold-blooded carnivorous
  amphibian native to Naboo, tall dorsal sail spine, sensitive snout,
  explicitly Dimetrodon-like. Identity kept.
- `Grank` (arid_shrubland, medium; source row `fauna:the_miasma:Grank`,
  propagated to `fauna:arid_shrubland:Grank`) — SW-canon: the "saw-toothed
  grank", a medium carnivore/scavenger native to the Gungan Swamps of Naboo,
  serrated teeth, senses vibrations through body hair, known to scavenge
  refuse on Coruscant's lower levels. Identity kept.

All three prompts explicitly request "heavy, clean black outline around the
whole silhouette and all major internal linework, thick enough to read
clearly at standard RimWorld zoom and below" per the outline requirement.

14 candidates remain in the pool for a future wave 10:
`AA_AcanthamoebaGiganteaLarge`, `AA_Agaripod`, `AA_BloodShrimp`,
`AA_Bumbledrone`, `AA_BumbledroneHierophant`, `AA_GreenGoo`, `AA_Razorjack`,
`AA_Thermadon`, `AA_Wildpod`, `BMT_AaroxisDendoria`, `BMT_BloodletterPetrel`,
`BMT_FungalMantis`, `BMT_Screecher`, `RSW_RustNipper` — none checked against
the SW canon doc, all `AA_`/`BMT_`/`RSW_` donor-mod prefixed and expected to
be reimagine candidates on the same pattern as prior waves' non-canon picks.

## verify
`fill_queue.py --input Transient/art_regen_wave9_improve.json --channel
codex` dry-run showed 9 jobs / 0 duplicates / 0 row errors, then filed for
real: 9 job files (3 facings × 3 creatures) landed in
`infrastructure/artpipe/pending/` (`dactillion_v1_{south,east,north}`,
`fanback_v1_{south,east,north}`, `grank_v1_{south,east,north}`). Daemon
(`artpiped.py -N 3`, pid 699477) confirmed alive via `pgrep` both before and
~90s after filing. All 9 jobs still sat in `pending/` past the usual ~60s
claim window; checked `throughput.jsonl` before assuming a hang — the last
completed job (wave 8's `kinrath_v1_south`) reported `primary_used_percent:
90.0` with `grumpy: true`, `primary_resets_at: 1789183737`
(2026-09-12T03:28:57Z) — at/above the daemon's own grumpiness-backoff
threshold, same documented de-escalating sleep-until-reset behavior that
explained wave 6's identical symptom. Not a stall or crash; left running,
will resume claiming automatically once that window resets.

## criteria
(a) Jobs filed and the daemon confirmed alive and consuming under normal
conditions (rate-limit backoff is the daemon's own documented behavior, not
a defect of this item) — MET, see verify. Wiring the finished art into game
defs once each facing completes is a follow-up step for whoever next
reviews `done/`, not part of this item's own close criterion, matching
waves 4-8's precedent (queue-and-confirm, not full wire-in).
