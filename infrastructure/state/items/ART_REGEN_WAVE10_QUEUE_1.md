## spec
Standing owner instruction, reaffirmed 2026-09-11: "Fan out and continue full
belt at all times... there should always be at least one agent regenerating
graphics." Continuation of `ART_REGEN_WAVE4_QUEUE_1` through
`ART_REGEN_WAVE9_QUEUE_1`, same source pool: `art: "improve"` rows in
`design/Jawa/worldbuilding/review/round2/decisions_propagated.json`, same
binding semantics (`infrastructure/artpipe/README.md`, "'improve' semantics"
section): full regen, Star Wars-named creatures keep canon identity,
non-SW names free to be reimagined, heavy black outlines enforced.

Wave 9 named its own remainder pool of 14: `AA_AcanthamoebaGiganteaLarge`,
`AA_Agaripod`, `AA_BloodShrimp`, `AA_Bumbledrone`,
`AA_BumbledroneHierophant`, `AA_GreenGoo`, `AA_Razorjack`, `AA_Thermadon`,
`AA_Wildpod`, `BMT_AaroxisDendoria`, `BMT_BloodletterPetrel`,
`BMT_FungalMantis`, `BMT_Screecher`, `RSW_RustNipper`. This wave (worked by
a background art-pipeline-keeper subagent while the daemon sat idle ~18h)
took that exact set, verified none had landed in `done/`, `failed/`, or
`registry.jsonl` since, cross-checked all 14 against
`design/RimStarWars/star_wars_canon_names.md` (zero hits — none are SW
canon), and reimagined each per the improve ruling: kind/ecological niche
kept, name and design invented, heavy black outline mandated in every
prompt. Caught one id collision before filing (invented name "Slagmaw"
collided with an existing wave-5 creature of the same name; renamed to
"Oozemaw").

Final 14 reimagined names: ashrunner, bilespawn, corronip, direwail,
fumeback, gorewalker, huskrunner, mireflit, mireflitwarden, miremoth,
oozemaw, rotscythe, sporehulk, wastewing.

## verify
`Transient/art_regen_wave10a_improve.json` (7 creatures) +
`Transient/art_regen_wave10b_improve.json` (7 creatures) = 14 creatures x 3
facings = 42 job files filed into `infrastructure/artpipe/pending/` via
`fill_queue.py --channel codex` (dry-run checked first). Daemon
(`artpiped.py -N 3`, pid 699477) confirmed alive via `pgrep` before and
across two post-file verify rounds; `active/` held 6 claimed jobs (3
workers x 2, see note below) and `pending/` was draining normally.
Codex rate-limit meters climbed 16% -> 39% primary across the session with
`grumpy: false` throughout and zero new failures in `throughput.jsonl`.

⚠️ **Found, not caused, by this wave:** a SECOND `artpiped.py` process was
already running (pid 1410335, default `-N 3`, started 2026-09-12 11:50 from
some other window's shell) alongside the expected one (pid 699477, running
since 2026-09-11 10:50). Not started by this wave's work and not killed by
it either -- ownership couldn't be confirmed from inside this item, and the
daemon's atomic `os.rename` claim is safe against two movers (confirmed:
`active/` held exactly 6 jobs = 3+3, no double-claim corruption), so it was
left alone rather than killed on a guess. Whoever next holds the bridge
should confirm which window owns it and stop the stray one if it isn't
meant to be running.

## criteria
(a) Jobs filed and the daemon confirmed alive and consuming under normal
conditions -- MET, see verify. Wiring finished art into game defs once each
facing completes is a follow-up step for whoever next reviews `done/`, not
part of this item's own close criterion, matching waves 4-9's precedent
(queue-and-confirm, not full wire-in).
