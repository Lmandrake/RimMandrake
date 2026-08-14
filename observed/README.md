# observed/ — what a running game actually did

**There are THREE shapes here, not one.** The old rule — *"every directory here is
stamped, and the stamp is the axis"* — described a tree that no longer exists and
never fully did. Corrected 2026-08-14 against the actual layout; `infrastructure/STRUCTURE.md`
already described all three, so this file was the outlier.

A measurement belongs to the *moment it was taken*, so there is still no `Jawa/`
vs `RimMandrake/` split. But "the moment" is carried by a **filename stamp** as
often as by a directory.

## The three shapes

| shape | example | what it is |
|---|---|---|
| **① generated-data home** | `observed/2026-08-13/` | Machine output that the **next load overwrites**: `dumps/`, `inventory/`, `logs/`, `savegame/`, latency JSON, the live mod inventory. One directory, not one per load — the load's date rides in the *filename* (`manifest.585.2026-08-14.json`, `Player.startup.585.2026-08-14.log`). |
| **② finding write-up** | `observed/2026-08-13_ion_weapon_live_test.md` | One file per question a live game settled. Prose, hand-written, dated by the contact that produced it. This is the tier's work product. |
| **③ cited payload** | `observed/evidence/2026-08-13_ion_downs_kotor_droid.png` | A screenshot or capture that a ② **cites by path** as its proof. Unstamped directory, stamped filenames. |

### Where does my new file go?

- **A script wrote it and the next load will write it again** → ①, under
  `observed/2026-08-13/<subdir>/`, with the mod count and date in the filename.
  Do **not** make a new dated directory for it.
- **I am writing sentences about what I saw** → ②, `observed/<date>_<topic>.md`
  at the tier root. One question per file.
- **A ② needs to point at an image to be believed** → ③, `observed/evidence/`,
  named `<date>_<topic>_<detail>.png`. Nothing goes in `evidence/` that no
  write-up cites.
- **Raw log lines, a tool's run log, a save** → payload. ① under
  `observed/2026-08-13/logs/` or `savegame/`, gitignored. It is not a ② just
  because it is dated and at the root.

## 🔴 `observed/2026-08-13/` is the CURRENT generated-data home, not a snapshot

The name is an artefact of the restructure — `fix_refs.py` set one stamp and swept
every old path into it. **~71 references across `design/`, `infrastructure/` and
`research/` point inside it**, including `infrastructure/REFRESH.md` for the live
`GENERATED_FROM.json`. The 2026-08-14 load's manifest and startup log are both in
there, under that 08-13 name.

⚠️ **Anyone auditing on the date alone will delete live data.** Judge a directory
here by its inbound references, never by how old its stamp looks.

## 🔴 Track the provenance. Never the bulk.

**What is tracked, by shape:**

| shape | tracked | gitignored, stays on disk |
|---|---|---|
| ① `2026-08-13/` | `dumps/manifest.*.json` (~144 KB each — mod set, game version, per-def-type counts), `dumps/capture_manifest.py`, the derived `inventory/` CSVs and contact sheets, `live_mod_inventory.md`, `load_expected_signatures.md`, `vwel_weapon_dump.md` | `*.rws`, `*.log`, `logs/`, `Player.log*`, `defs/`/`DefDump/`, `latency_*.json`, `screenshots/`, `*_preview.png`, `*_items.*`, `*_ideoligions.*`, `*_legend.json` |
| ② `<date>_<topic>.md` | **yes, always** — it is the work product | its non-`.md` lookalikes are not findings and are ignored by name: `2026-08-13_load_1730_triage.txt` (raw grouped log lines), `2026-08-13_refresh_all.log` |
| ③ `evidence/*.png` | **yes** | — |

**③ is the deliberate exception to "screenshots are gitignored."** A screenshot
sitting in a stamp's `screenshots/` is a payload — thousands of them, value
expires. A screenshot a finding *cites as its only proof* is unreproducible and
its value persists: the game state that produced it is gone. Promoting it into
`evidence/` is what makes it trackable. Rule: **cited → `evidence/` → tracked.**

**The reason the payload rule is absolute is that git never forgets.** `.git` is
~275 MB for a repo whose text is a few megabytes. **Untracking never shrinks
history — only not-adding does.** The rule is about refusing the *next* payload,
not cleaning up the last one. And a single file over 100 MB hard-fails the push
for **every** seat until it is rewritten out of history.

⚠️ **Never delete a payload "for size".** It buys nothing — the history already
holds what it holds — and it loses a file that may be unreproducible. Move it,
ignore it, leave it on disk.

## The manifest: what it is actually called, and who writes it

🔴 **There is no file named `MANIFEST.json` in this tier and there never has
been.** Earlier text here promised one per stamp; that was wrong. The real
artefact is:

```
observed/2026-08-13/dumps/manifest.<modCount>.<capturedUtc date>.json
```

written by `observed/2026-08-13/dumps/capture_manifest.py`, which copies the live
`manifest.json` out of the def dump before the next load overwrites it. **It is
generated — if you are hand-writing one, something is wrong.** It lands in the ①
home, keyed by mod count and date; it does *not* go in a per-contact directory.

### `observed/2026-08-14/` has no manifest, and does not need one

That directory holds `Player.log.prelaunch` and nothing else. It is a **prelaunch
holding spot, not a contact stamp** — the log was copied aside *before* the game
came up, so at that instant there was no loaded stack to describe.

**It is exempt, and the provenance is not missing.** The 585-mod load that
followed it was captured normally:
`observed/2026-08-13/dumps/manifest.585.2026-08-14.json`
(`capturedUtc 2026-08-14T08:20:26Z`, game 1.6.4871 rev591), with its startup log
at `observed/2026-08-13/logs/Player.startup.585.2026-08-14.log`. Both went to the
① home, as shape ① requires.

**Nobody owes this directory a `MANIFEST.json`.** Whoever runs the next load runs
`capture_manifest.py` as part of the load round (`skills/rimworld-load-round/SKILL.md`);
that is the only manifest duty in this tier. A prelaunch-only directory whose
successor manifest exists is complete.

## The test that decides whether something is `observed/`

> **Could a machine regenerate this without a human decision?**
> …and **does its value expire?**

| | reproducible | unreproducible |
|---|---|---|
| **value expires** | cache — never commit | **on disk, gitignored — shape ① payload** |
| **value persists** | commit if cheap (a manifest) | commit — it is a work product (② and ③) |

A harvested `Player.log` is the trap: it *cannot* be regenerated, but its value is
transient — you extract the findings and the raw log is dead weight git keeps
forever. **Commit the finding (②), ignore the log.**

## What does NOT belong here

- **Tool run-artifacts** — map-synth PNGs, art-bench intermediates, a script's own
  run log. Those are outputs of *our* scripts, not observations of a *game*; they
  live gitignored beside their generator in `src/`.
- **Game config we copied to track it** → `deployed/config/`.
