# BENCH_REBOOT_HANDOFF_202609111500 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609072318`. Everything below is committed
and pushed. This was a RULINGS-AND-WRITING day at the bench, owner present
(much of it from his phone): ~30 card rulings landed and propagated, one big
census, and four bodies of authored text. No bridge held at any point; game
state untouched by this window.

## The one thing to carry forward

🔑 **Three text-voice laws are now canon** (`infrastructure/state/canon.yml`):
`narrator.butler_register_src` (the Narrator is a REAL voice on ship
speakers/comms — a mournful, bemused butler ghost, never a Jawa, never a
caption; ALL atmosphere is his), `game_fact_voice` (fact text is dry, no
atmosphere), `cathedral_voice` (semi-lucid god-mind bursts; the owner's own
verbatim is the calibration text and SHIPS as the Assailant reveal line).
Every future player-facing string obeys this split. The owner also ruled god
lines are **UNSIGNED always**, and card style is now a saved memory: simple
language, every option stating its trade.

## What the owner should see (ranked)

1. ⭐ **The blessed Nine Voices corpus** —
   `D:\Luke\dev\Rimworld\design\RimMandrake\nine_voices_v1_lines.md`: 54
   pidgin god lines, BLESSED. The 18 narrator silent-god readouts in the same
   file are DRAFT and register-superseded — they need a butler-ghost redraft
   and his bless (the one dangling writing thread).
2. **The dungeon text corpus** —
   `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\dungeons_arc_spec.md`
   §2.8 + §3.10: Assailant set AGREED, V6 + ring letters accepted-for-now,
   all provisional by his explicit word.
3. **The mindstone legends deck** —
   `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\mindstone_arc_legends.md`:
   five entries authored with him, scoping table, hard late-game gate (no
   one, Junkers included, knows the Cathedral is alive or wants the stone).
4. **Text lore load report** —
   `D:\Luke\dev\Rimworld\design\Jawa\text_lore_load_report.md`: 38 engine
   surfaces, triage, ~90–140k word load. NOTE its §3/§6 carry a same-day
   correction: the Armoury/SWBestiary "1,830 missing" was an overcount;
   real debt was 57, already written and generator-registered.

## Rulings landed and propagated (all recorded at their homes)

- **KIT_SPECS_CARD_SITTING_1 closed** — all ~30 cards ruled: biomesteam
  port-then-RETIRE (after gates; the 7 stragglers CUT), forgotten-war quote
  stands, Greentide = own RM-tier mod + no churnmud exemption + both
  deferrals REJECTED (seek-shade AI and silence cue ship v1), ShipVermin mod
  born (all hull vermin, mynock first, RSW_Mynock clone), scaria trap kept,
  Sentinels get local reprisal + radii doubled (72/80/24/80), Last Line in
  v1, Webwork moat = cripple-not-down + sun-only (no night on Ash'karr; no
  player light rivals the sun), creep-web border-yields + emergent-Shokk
  chance, Shokk = own RSW-tier mod, ambusher = debris-pile Thing.
- **Mechanoid origin canon fully ruled**: factory trickle (religiously slept
  infrastructure, winding down), hunger-as-crystal-memory, "enslaved" =
  testimony, Kindled = head-carried NEW LIFE FORM (droid/mechanoid/Kindled
  taxonomy) and **never yet made — no in-world knowledge**; mindstone kept,
  race = The Kindled, Forgotten Sentinels canonical (variants = in-world
  speech), head seam accepted with rich legends owed, wipe/spike immunity
  ratified. Sentinel surface picture refined: sparse LOST units,
  self-repairing and devolving; the trickle feeds hidden caches/vaults only.
- **Fauna graphs sitting closed (from his phone, via artifact
  a7327077-3d63-4970-a4cc-13d55a586463)**: Law-3 K=12–15×bodySize for all
  326; Law-5 tolerance = domain envelope +15°C both sides; products
  bodySize-proportional now; size-first then FAUNA_LORE_DIVERSIFICATION_1
  (huge terrify, tiny harmless — judged by art+lore later).
- **Age register**: numbers/millennia out, "ages past" in; ONE hedged
  "believed ~10,000 years, little known" encouraged where origins are
  discussed. 38/54 hits replaced repo-wide, 16 sanctioned remain.
- **RSW tier is Jawa-neutral** (ruled + both offending descs reworded).
- **Staged lore**: owner ordered a live PROOF before build/no-build —
  `STAGED_LORE_PROOF_SPIKE_1` (FOUNDRY, needs deploy).

## New systems designed and filed

- **Art regen registry** (`design/RimMandrake/art_regen_registry_design.md`,
  ruled by card): event ledger above the art queue, done=committed, retry
  cap 3, repurpose first-class, spend joined from throughput.jsonl →
  `ART_REGEN_REGISTRY_1` (FOUNDRY).
- **Dashboard hub** — ONE multi-tab artifact, per-tab data files (many
  writers, no collisions), freshness lamps → `DASHBOARD_HUB_ARTIFACT_1`
  (BENCH, unclaimed).

## Half-done / owed (each recorded on its item)

- Narrator silent-god readouts: butler redraft + bless (on
  `DUNGEON_SETPIECE_TEXT_1`'s remaining list, content notes preserved).
- Tier-fix + Jawa-neutral rewordings need a DEPLOY (FOUNDRY, next
  UtinniPatches/Droidworks push); scenario "ages past" XML likewise
  (`SCENARIO_DURATION_CUT_1` repo half done).
- `DONOR_FACTION_PROPER_NOUN_RENAMES_1` (needs owner): what orcs/trolls/
  MiningCo become — good phone card sitting, offered, not yet taken.
- Desk sheets untouched: `ASSIGNMENT_SHEETS_VERDICT_SITTING_1` (he can't do
  sheets on phone).
- Hutt-deal thread + ship-claim continuation: blocked on quest authoring.
- `MECHANOID_ORIGIN_CANON_1` residue: B3 stats charge + presence-review feed.

## Traps for whoever resumes

- ⚠️ FOUNDRY is draining BENCH-filed tickets FAST — twice today it executed
  an item within minutes of filing (tier fixes, proper-noun scan; one lane
  briefly clobbered FOUNDRY's committed file and reverted). **Check an
  item's ledger state before spawning an executor for it.**
- ⚠️ The three-voice law makes most earlier "narrator" drafts wrong by
  register — anything atmospheric written before 2026-09-11 that isn't in
  the butler voice is suspect; the god readouts are already flagged.
- Dungeon/vault text is PROVISIONAL by owner's word — wire, never freeze.
- The def dump (fingerprint 6fdca6f582164e2a) is 1 day stale and ModsConfig
  currently shows the 13-mod minimal list — restore before he plays.

## Game and bridge state

This window never took the bridge and issued no game-state command. Queue
files said game UP / bridge free at 13:35Z; artpipe daemon churning
(throughput.jsonl advancing). Re-derive with `rimflow bridge who` and
`./game` on wake — do not trust this section's snapshot.
