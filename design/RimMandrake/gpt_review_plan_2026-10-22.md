# GPT deep-review round, 2026-10-22 (FOUNDRY helper)

Owner order 2026-10-22 (verbatim): *"Please package up each of the mods we are trying to mature and fully deploy in this push and last push. Send each of them to gpt for deep code review. Ask it to really drill down and skeptically review the design, implementation, bug check, everything. Submit only one per 15 minutes to avoid jamming gpt consult. Include the design docs with each to ensure it understands the context and intention. Also include outstanding concerns and the validation plans and evidence and methods. Especially ask advice on improving the lodestar plans to make it as efficient as possible to validate without wasted time. Finally include the associated art for analysis as well."*

## The mod set, and why

Chosen from `design/RimMandrake/release_proximity_2026-10-22.md` (ranked top five), the FOUNDRY handoff `infrastructure/state/handoffs/FOUNDRY_HANDOFF_202610221110.md` (Webwork and Rot shift work, the Wave 1 / Wave 4 deploy pointer), and `git log --since=7.days` over each mod folder (commit counts measured 2026-10-22):

| order | package | source folder | 7-day commits | why |
|---|---|---|---|---|
| 1 | GimmeSomeSlack | `src/RimMandrake/GimmeSomeSlack` | 47 | rank 1 in release proximity; owner priority since 2026-10-11 |
| 2 | IshkoDarkLandmarks | `src/RimUtinni/IshkoDarkLandmarks` (+ icons in `src/RimUtinni/AshkarrLandmarkArt`) | 0 | rank 2; the only mod GREEN at its current hash; named in the order brief |
| 3 | FlowWorks | `src/RimMandrake/FlowWorks` | 596 | rank 5, but the owner's current focus; most of this push |
| 4 | Pyrelands | `src/RimMandrake/Pyrelands` | 43 | rank 3; ships inside the composite |
| 5 | Graffiti | `src/RimMandrake/Graffiti` | 3 | rank 4 |
| 6 | Webwork | `src/RimMandrake/Webwork` | 36 | spider siege and thrixweave resale built this push (handoff) |
| 7 | TheRot | `src/RimMandrake/TheRot` | 48 | warm mat, dustveil, kin-mending built this push (handoff) |
| 8 | BiomesComposite | `src/RimMandrake/BiomesShell`, `src/RimMandrake/Biomes.compose.json`, `biomes_compose*.py`, `deploy_custom_mods.py` | 19 (shell) | our composed mod `mandrake.rm.biomes`; Wave 1 defName migration and Wave 4 retirement are built and undeployed (handoff) |

Not included: SWBestiary, UtinniPatches, LeaningScrub and the other high-churn folders. They had heavy commits but are not named as mods being matured for release in either source.

## Packages

Root: `D:\ClaudeWork\gpt_review_2026-10-22\` (agent storage, not the repo). There is one folder per mod, for example `D:\ClaudeWork\gpt_review_2026-10-22\GimmeSomeSlack\`. Each folder holds:

- `PROMPT.md`: the skeptical brief. It asks for design versus implementation, a bug hunt, RimWorld 1.6 pitfalls, save/load, performance, mod-list conflicts, settings and art. It asks for a validation critique with a falsifier for each headline claim, and for ranked findings with file:line and the cheapest check that would prove each one. A dedicated section E asks how to make the Lodestar / modcheck / north-star validation as efficient as possible. It gives the cost facts: cold load ~15 min, minimal list ~22 s, quicktest ~90 s, one bridge holder.
- `SUBMISSION.md`: what is sent. It holds the brief plus an inlined bundle: `CLAUDE.md`, the rulings paragraphs that name the mod, live ledger items, lessons, modcheck status, the result files it points at (with dates and hashes), the code-review DIRTY list, the 7-day log, design docs (about 140k chars) and prioritised source (about 200k chars: DIRTY files first, then validation scripts, C#, defs). Sizes run from 98k chars (Ishko) to 540k (FlowWorks).
- `SUBMISSION_LITE.md`: the fallback for the retry. Source and docs are not inlined; GPT reads them from disk.
- `src\`, `context\`, `MANIFEST.md`: every tracked text file and every gathered document. GPT reads them through its read-only shell. Disk reads were proven by the transport test.
- `art\ART_MANIFEST.tsv` and `art\sheets\sheet_NN.png`: each asset with its art-ledger status (live sha, owner-protected, provenance kinds, purged) and contact sheets. Up to 8 sheets are attached as images (`attach.txt`). `art\UNRESOLVED_TEXPATHS.txt` lists texPaths with no PNG in our `src/`; most of these are vanilla, DLC or donor art, so the list is not proof that art is missing. The composite package has no art.

The packager is `D:\ClaudeWork\gpt_review_2026-10-22\pack.py` (`python3 pack.py [Mod]` rebuilds a package; it only reads the repo). Packages were secret-scanned: no key patterns were found.

## Schedule

The driver is `D:\ClaudeWork\gpt_review_2026-10-22\driver.py`. It was started at 2026-10-22 15:48:53 PDT, detached (setsid). It starts one consult every 900 s (start to start), in the order above. The last first attempt starts at about 17:34. Model and effort are the `gpt_consult.py` defaults (gpt-6.1-sol, high), with a 3600 s timeout per consult.

- If a consult fails, it is retried once in the next free slot using `SUBMISSION_LITE.md`. If the retry also fails, the driver writes `GPT_FAILED.md`.
- The driver is resumable. Re-run `python3 D:\ClaudeWork\gpt_review_2026-10-22\driver.py` (WSL: `/mnt/d/ClaudeWork/...`) and it skips any package that already has `GPT_REPLY.md` or `GPT_FAILED.md`.
- Transport was proven before launch with one trivial consult through the driver's own path (4 images attached, a package file read from disk): `D:\ClaudeWork\gpt_review_2026-10-22\_transport_test\dryrun_GimmeSomeSlack.md`.

## How to read the replies

- Progress, one line per event: `D:\ClaudeWork\gpt_review_2026-10-22\driver.log`. Each package also has a `STATUS` file (RUNNING / DONE / FAILED).
- The reply is `<package>\GPT_REPLY.md`, in sections A to G: verdict, ranked findings table, design gaps, validation falsifiers, **E. the efficient-validation plan**, art findings, owner questions.
- A reply is evidence, not findings (`subagent-verdicts-are-evidence-not-findings`). Before filing or fixing anything, check each cited file:line against the source. Section E proposals that change a north-star bar need the owner's validation, because the hash covers the bar.
