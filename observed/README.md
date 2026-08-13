# observed/ — what a running game actually did

**Tier rule: every directory here is stamped, and the stamp is the axis.** One
`observed/<stamp>/` per live-game contact, created when the bridge first reaches a
new running game. There is no `Jawa/` vs `RimMandrake/` split — a measurement
belongs to the *moment it was taken*, not to a reuse category.

## 🔴 Track the manifest. Never the payload.

Per `observed/<stamp>/`, **only `MANIFEST.json` is tracked** — mod set, game
version, loadset fingerprint. Everything else is gitignored: `.rws` saves, def
dumps, `Player.log`, screenshots, latency dumps.

**The reason is that git never forgets.** `.git` is ~275 MB for a repo whose text
is a few megabytes; ~135 MB of that is eleven binaries, and 12 MB is a `promo/`
directory that was deleted from the tree over a day ago and is still permanent in
history. **Untracking never shrinks history — only not-adding does.** The rule is
therefore about refusing the *next* payload, not cleaning up the last one.

⚠️ **Never delete a payload "for size".** It buys nothing — the history already
holds what it holds — and it loses a file that may be unreproducible. Move it,
ignore it, leave it on disk.

## The test that decides whether something is `observed/`

> **Could a machine regenerate this without a human decision?**
> …and **does its value expire?**

| | reproducible | unreproducible |
|---|---|---|
| **value expires** | cache — never commit | **on disk, gitignored — this tier** |
| **value persists** | commit if cheap (a manifest) | commit — it is a work product |

A harvested `Player.log` is the trap: it *cannot* be regenerated, but its value is
transient — you extract the findings and the raw log is dead weight git keeps
forever. Commit the finding, ignore the log.

## What does NOT belong here

- **Tool run-artifacts** — map-synth PNGs, art-bench intermediates. Those are
  outputs of *our* scripts, not observations of a *game*; they live gitignored
  beside their generator in `src/`.
- **Game config we copied to track it** → `deployed/config/`.

`MANIFEST.json` is generated. If you are hand-writing one, something is wrong.
