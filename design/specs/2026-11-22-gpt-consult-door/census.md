# GPT consult points, the one door, and one sign-in (measured 2026-11-22)

Item: `RIMMANDRAKE_ROUTE_EVERY_GPT_CONSULT_THROUGH_DISPATCH_ONE_DOOR_CAREFULLY`. The door's design page is in Dispatch:
`D:\Luke\dev\Dispatch\design\specs\2026-11-22-gpt-door.md`; its code is `providers\chatgpt\bin\gpt_door.py`.

## What raises the Windows modal dialog

The dialog is the Windows consent prompt that `codex.exe`'s sandbox setup raises when it creates the machine-wide users
`CodexSandboxOffline` and `CodexSandboxOnline`. The setup runs when `codex.exe` starts against a Codex home whose
`.sandbox/setup_marker.json` and `.sandbox-secrets/sandbox_users.json` do not match the provisioning Windows holds now
(`net user` "Password last set"). That happens with a new home, a home copied from a stale template, or a runner changed
by an auto-update. Every setup resets the users' passwords, so every other home goes stale at once (closed items
`CODEX_UAC_STORM_1`, about 30 prompts; `SANDBOX_UAC_ONE_STATE` in `codex_image.py`). The Linux CLI has no such setup.
A second, separate dialog is Chrome's "Allow remote debugging" sheet, raised by Dispatch's Chrome transport on the Mac.

Reading before any launch [measured 15:38 PST]: the Windows home `C:\Users\Mandrake\.codex` marker matched the
machine's provisioning (17:20:37Z against 17:20:36Z, 2026-10-16), and its runner matched the installed build
(0.166.0-alpha.5.1). This run launched `codex.exe` only against that home, three times, and today's sandbox log shows
only "Windows sandbox selection: elevated", never a setup line. No home was created, copied or seeded.

## Census: who asks GPT, and through what

Method: `git grep` over RimMandrake, Dispatch, MandrakeWorkflows, Lodestar and Machinist for `gpt_consult`,
`codex exec`, `codex_worker`, `consult.py`, `chatgpt-consult`, `ask GPT`, `gpt-6`, `codex_cli`, `codex.exe`, `openai`;
the user systemd units. Not looked at: other machines, and conversation logs (their mentions are history).

**Launchers (programs that start Codex to ask a question), before this run: 7.**

| launcher | repo | home | model, effort | after this run |
|---|---|---|---|---|
| `src/RimMandrake/Utils/gpt_consult.py` | RimMandrake | side default or `--codex-home` | gpt-6.1-sol, high | a shim over the door |
| `codex_side.py` shell launcher (designer scripts) | RimMandrake | side default | caller's | through the door's finder and sandbox guard |
| `artpipe/canon_check.py` `codex_vision` | RimMandrake | the art daemon's leased worker home | gpt-6.1-sol, high | left: the art item's (worker homes) |
| `skills/oracle-delphi/scripts/run_gpt.sh` | MandrakeWorkflows | `~/.codex` | caller's | left: GPT reads a codebase from its working folder; the door has no working-folder option |
| `tools/placard/placardlib/backends.py` codex route | MandrakeWorkflows | the container home or native | the account's default | left |
| `providers/chatgpt/bin/consult.py` + `codex_worker.py` | Dispatch | the container home (Mac) | gpt-6.1-sol, high | left; the door wraps `codex_worker.run` for its `container` side |
| `consult.py --transport chrome` | Dispatch | the user's chatgpt.com tab | the account's | left (not Codex) |

The three left are one ticket: `RIMMANDRAKE_ROUTE_OUTSIDE_GPT_LAUNCHERS_THROUGH_DOOR_THREE_LEFT`, with its acceptance test.
Not consult points: `agent_runner.py` and the Codex designer and lane scripts start Codex as a builder; `augur`
observes Codex processes; `clear-findings/tools/run_arm.py` and Dispatch's `simpleqa.py` call other models.

**Callers of `gpt_consult.py` in code: 11** (`run_gpt_review.py`, `run_consult.sh`, `run_canon_review.py`,
`LeaningScrub/validation.py`, `art/prereview.py`, `art_eval/race.py`, `art_eval/runner.py`,
`code_review_calibration.py`, `agent_runner.py`'s rate probe, `canon_check.py` (its model default), and
a MandrakeWorkflows loop template, `phone_gpt.sh`). **Prose that tells an agent to run it: 36** live RimMandrake docs
(skills, specs, briefs, `CLAUDE.md`), plus 16 MandrakeWorkflows, 44 Lodestar, 3 Machinist and 13 Dispatch docs that
name a consult tool. The shim keeps the CLI, so none of them changed.

**How each answer kind was handled before:** only `gpt_consult.py` and `codex_worker.py` kept "could not look",
"failed", "zero" and "empty" apart (exit codes 20/21/22/23/1 and a verdict line); `run_gpt.sh` writes `exit $?` into a
log and nothing reads it; `canon_check.py` raises on an empty answer. The door now holds the one taxonomy.

## One sign-in

[measured 15:30-15:36 PST] 76 `auth.json` files on both sides carry ONE ChatGPT account (id prefix `e2a474b0`), in 14
token families (copies share a family). Three concurrent locked-down consults through one Linux home: 3 of 3 answered,
and the home's `auth.json` did not change. The Windows login of 15:17 did not revoke the Linux login of 15:01. With
the 2026-09-26 measurement (copies of one family fail when a sibling refreshes first:
`ARTPIPE_WORKER_AUTH_STALENESS_1`), the answer for consults is: **one home per side is enough; copies are the hazard,
concurrency is not.** Unmeasured: two processes in ONE home both refreshing at the same instant (Codex refreshes when
`last_refresh` is older than about a day). The door retries once on AUTH for that case.

Hazard left for the art item: new art worker homes are seeded with a copy of `~/.codex/auth.json`, the consult home
(`design/specs/2026-11-22-art-pipeline-and-dispatch/study.md`). When a worker copy refreshes first, the consult home's
token family is revoked and every consult answers AUTH.

## Equivalence, old against new

- **Replay** of every kept consult job on disk (567 job folders, 264 joined to a recorded call-log entry for their rc):
  the old classifier and the door's give the same outcome on all 567 (308 no-answer-unclassified, 160 answered,
  55 deadline, 27 allowance, 14 auth, 3 transport). 0 differences.
- **The replay found two real defects**, now fixed in the door, test first: 109 Windows-side consults
  (2026-10-30 to 11-03) exited 0, were recorded as no answer, and hold a non-empty answer file now; the door re-reads an
  absent answer for 5 s after exit 0. 9 Linux consults killed at their deadline wrote an answer afterwards, so codex had
  outlived the kill; the door now kills the whole process group.
- **Planted faults through the real CLI**, old and new side by side, fake codex: answer, empty answer, short refusal,
  revoked sign-in, timeout. 5 of 5 give the same verdict line and exit code.
- **Door tests**: 29 (Dispatch `providers/chatgpt/tests/test_gpt_door.py`); 9 planted faults in the door, 9 caught.
- **Real consults**: through the door, Linux and Windows both ANSWERED at 15:44 PST; through the shim, Linux with a file
  and an image and Windows with a file, both ANSWERED.

## Deleted, and what would be deleted

Deleted: `src/RimMandrake/Utils/codex_cli.py` (172 lines, the second copy of the Codex finder). Its tests now test the
door's finder.

Nothing under `C:\Users\Mandrake` and no sign-in home was deleted. Candidates, for a later decision (sizes below).

| home(s) | count | size [measured du, 16:10 PST] | token families, last refresh | what reads it | call |
|---|---|---|---|---|---|
| `C:\Users\Mandrake\.codex_workers\artpipe\w0..w31` | 32 | 77,726 MB | 1, 2026-11-05 (stale) | the art daemon (`artpipe/common.py`) | the art item's: most of the size is sessions and generated images |
| other `C:\Users\Mandrake\.codex_workers\*` (bench_lad, bench_spk, dw, pyr, w_*, greatbole_art, painterly_regen, pyre_repaint, artpipe_x, ...) | 28 | 13,353 MB | 7, 2026-09-03..10-19 (stale) | one-off art scripts that name `.codex_workers` as a root (`gen_direct.py`, `bridge_redraw.py`); no live reader found | delete after the art item rules |
| `C:\Users\Mandrake\.codex_bacta_*` | 7 | 2,203 MB | 1, 2026-09-14 (expired) | none found in code | delete |
| `C:\Users\Mandrake\.codex_arena_judge`, `..._benchprobe` | 2 | 782 MB | 1, 2026-10-29 (expired) | none found in code (the arena judge passes `--codex-home`) | delete, or renew if the arena judge returns |
| `/home/mandrake/.codex_workers/artpipe/w0..w4` | 5 | 1,129 MB | 5 own device logins, 2026-11-21 | the art daemon (Linux) | keep |
| `/home/mandrake/.codex` | 1 | 2,898 MB | own login, 2026-11-22 | every Linux consult | keep (old `sessions/` could be pruned) |
| `C:\Users\Mandrake\.codex` | 1 | UNMEASURED (du passed 30 s) | own login, 2026-11-22 | every Windows consult; the sandbox base | keep |

Deleting a home does not raise the dialog (only a `codex.exe` launch against a stale home does), but a deleted home that
something later recreates and launches against would. So each deletion goes with removing or repointing its reader.
