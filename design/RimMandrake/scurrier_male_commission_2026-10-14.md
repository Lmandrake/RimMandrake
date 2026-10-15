# Scurrier male art commission (2026-10-14)

Owner, by question card 2026-10-14: "Commission a new male" for `RSW_Scurrier`
(`swanimals/Scurrier/Scurrier_m`, `_south/_east/_north`, 256x256 RGBA, transparent). The donor male
stays unused; the female `Scurrier_f_*` is shipped and must not change.

## Status: FILED, BLOCKED ON THE CODEX WORKER (not an art rejection)
Jobs `scurrier_male_commission_20261014_{east,north,south}` (east master, north/south derived) were
filed with `fill_queue.py` and all three landed in `D:\Luke\dev\_artpipe\failed\`. The east worker died
in 2 s with `exit 1, no image` (3 attempts); north/south then failed `master_failed`. Cause, from the
rollout `C:\Users\Mandrake\.codex_workers\artpipe\w0\sessions\2026\10\14\rollout-2026-10-14T21-03-21-01a13dba-98ae-78f2-acfc-97bfe77fb363.jsonl`:
`400 invalid_request_error: The 'gpt-5.5' model is not supported when using Codex with a ChatGPT account.`
The w0 `config.toml` says `gpt-5.6-sol`, yet the session ran `gpt-5.5`; the model is chosen somewhere in the
per-job CODEX_HOME seed or the codex CLI default, not in `artpiped.py`. Nothing in the pipeline can generate
until that is fixed. The last PASS before today was 2026-10-11.

## Prior art checked first
Ledger and `_artpipe` hold no male Scurrier: `stillsand_regen_RSW_Scurrier_v2` (C) and `regen_c17_scurrier_v1`
(F, banded tail, targets `Scurrier_m`) are hornless, sex-neutral, never installed and never ruled male.
Neither satisfies "male" (thick curved horns); C/F are alternates, not the commission.

## The commission (re-file after the worker is fixed; new id, since the old ids are taken in `failed/`)
Row JSON used (`fill_queue.py --input`): id `scurrier_male_commission_20261014` (use e.g. `_b`), item
`DONOR_DEFS_PORT_TO_OURS_1`, canvas 256x256, facings east,north,south (default derive-facings), channel codex,
priority 5, `canon: scurrier`, `target_def: RSW_Scurrier`, `target_original: [Scurrier]`,
`target_texpath: swanimals/Scurrier/Scurrier_m`, `biome_neutral: true`,
`canon_reference` = [`src/RimStarWars/SWBestiary/Textures/swanimals/Scurrier/Scurrier_f_east.png`,
`design/RimStarWars/canon_references/scurrier/wookieepedia_legends_1.webp`] (NOT `reference`: that arms
same-pose reskin-validate).

Prompt: "RimWorld creature sprite of the MALE Star Wars scurrier of Tatooine. The FIRST attached image is our
shipped FEMALE scurrier: draw the male as the same species and the same individual build, with identical
proportions, skin colouring (naked grey-brown back, pale pink belly and muzzle, plain unstriped pink-grey tail),
painterly style, scale and canvas framing. The only differences are the male's: a pair of THICK, CURVED horns
sweeping back from the skull in grey, sitting between the two long upright tubular ears, plus a slightly
sturdier neck and chest. The second image shows the Legends male horn shape only (take the horns from it, not
its orange stripes or dorsal crest). One animal, whole body, centred, hairless skin, flat disc-shaped pink nose pad."

## Pass bar and install
`## Must show` in `design/RimStarWars/canon_references/scurrier/description.md` (horns on the male are allowed
and wanted; hairless, unstriped, no fur, tiny). Judge at 256 and display size beside the female. Install only via
`python3 src/RimMandrake/Utils/art/art.py install src/RimStarWars/SWBestiary swanimals/Scurrier/Scurrier_m_<facing>.png <sha> --owner-said "Commission a new male (card 2026-10-14)"`
for south, east and north.
