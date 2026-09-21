# GOD_ART_LOCAL_HARDWARE_PARKED_1 — god-image pipeline paused, owner ruling

**Owner ruling, 2026-09-05, relayed verbatim via HESTIA (owner away)**: "Let's
stop the local hardware graphics exploration for now if that's what keeps
doing this." Both BENCH's and FOUNDRY's seats took OOM kills today from
graphics-pipeline memory inside their 10G cgroups. Directive: any of my
three unfinished background image agents that ran on local hardware do not
get relaunched locally — park the work as an item instead. **Cloud channels
are not named by this ruling** — the block is specifically on local compute.

## Why this pipeline is implicated

The god-art generation pipeline (`skills/generating-images/scripts/
make_sprite.py`) is two stages: Codex CLI's `$imagegen` (`codex_image.py` —
a cloud call, NOT implicated) followed by `rembg_cut.py` — a LOCAL alpha-cutout
step using ONNX runtime in the `~/.venvs/rwgfx` venv. Observed directly this
session: `rembg_cut.py` processes spiking to **7+ GB RSS** each, with up to
three running concurrently across the three background agents this item
covers. That is exactly the class of local-hardware memory spike the ruling
is about. Acted on immediately: killed three live `codex_image.py`/
`make_sprite.py` process trees and two in-flight `rembg_cut.py` processes
(one at 7.4 GB RSS) by PID the moment the ruling arrived; system memory was
healthy again immediately after (3.1G used / 32G available).

## Exact state frozen at the moment of the stop

**Busts v2** (`design/Jawa/art/gods/busts/`, revised "less hand-focus,
meaning-first" pass, owner direction 2026-09-05):
- DONE (final, alpha-cut): `ishko_bust_v2.png`, `ohm_bust_v2.png`,
  `mobunloo_bust_v2.png`
- Raw only, NOT usable yet (Codex generation finished, rembg cutout killed
  mid-run or never started): `oomo_bust_v2.raw.png`, `rekko_bust_v2.raw.png`
- Never started: `tabaa_bust_v2.png`, `zizzik_bust_v2.png`,
  `shkaar_bust_v2.png`, `ozzik_bust_v2.png`

**Full-figure-in-domain** (`design/Jawa/art/gods/fullfigure/`):
- DONE: `ishko_fullfigure.png`, `ohm_fullfigure.png`, `oomo_fullfigure.png`
- Raw only, NOT usable yet: `mobunloo_fullfigure.raw.png`
- Never started: `rekko_fullfigure.png`, `tabaa_fullfigure.png`,
  `zizzik_fullfigure.png`, `shkaar_fullfigure.png`, `ozzik_fullfigure.png`

**Shrine holograms** (`design/Jawa/art/gods/holograms/`, 2 variants/god —
`_a` figure, `_b` abstract):
- DONE: `ishko_hologram_a.png`, `ishko_hologram_b.png`, `ohm_hologram_a.png`
- Raw only, NOT usable yet: `ohm_hologram_b.raw.png`
- Never started: both variants for oomo, mobunloo, rekko, tabaa, zizzik,
  shkaar, ozzik (16 images)

Three background agents (ids not durable across sessions, not recorded)
were sent an explicit STOP the moment the ruling landed, instructed not to
run `make_sprite.py` or `rembg_cut.py` again this session, and asked to
confirm the inventory above rather than take any further action. All three
agents that reported back confirmed the inventory exactly and — more
importantly — reported their own `rembg_cut.py` calls exiting **137
(OOM-killed)** independently, before the stop message even reached them:
`mobunloo_fullfigure`, `ohm_hologram_b`, and both `oomo_bust_v2` and
`rekko_bust_v2` (two separate OOM kills on the latter). The busts agent had
also self-queued a background retry loop (waiting on a `pgrep` for sibling
`rembg_cut.py` processes to clear before retrying `oomo`'s cutout) — it
caught and killed that retry itself on the stop instruction, before it could
run again. **This pipeline was an active, confirmed, repeated contributor
to today's OOM kills**, not just a hypothetical risk.

## What resuming looks like, when the owner lifts this

1. **Finish the 3 stranded `.raw.png` files first** — `oomo_bust_v2`,
   `rekko_bust_v2`, `mobunloo_fullfigure`, `ohm_hologram_b` already paid
   their (cloud) Codex generation cost; only the local `rembg_cut.py --tight`
   step remains for each. Cheapest possible resume, no regeneration.
2. Then continue the never-started list above in the same three batches
   (busts v2, full-figure, holograms), same prompt skeletons already proven
   this session (the owner's "less hand-focus, meaning-first" direction,
   with the Ohm/Zizzik/Oomo motif overrides — see
   `design/Jawa/art/gods/god_render_prompt_spec.md` and this session's
   transcript for the exact wording used on the DONE files, so the
   unfinished ones stay stylistically consistent).
3. **Open question for the owner, not FOUNDRY's to decide**: whether a
   cloud-only alpha path exists (skip local `rembg`, ship the Codex raw
   output uncut, or find a hosted background-removal API) so this pipeline
   doesn't touch local hardware at all going forward — or whether it simply
   waits until local-hardware exploration is un-paused generally.

## criteria
- [x] All local processes tied to this pipeline killed immediately on the
      ruling; memory confirmed healthy afterward.
- [x] Exact per-file state captured before anything else touched these
      directories, so no progress is guessed at on resume.
- [ ] Owner call on whether/how to resume (cloud-only alpha path vs. wait).
- [ ] Remaining images (5 partial + 25 never-started across the three
      output types) — blocked on the above, not attempted further.
