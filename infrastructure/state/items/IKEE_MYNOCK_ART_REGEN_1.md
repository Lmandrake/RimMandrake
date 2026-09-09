## spec
Owner go-ahead, 2026-09-07 (live session, "Do (b)" on the offered choice): generate
new custom art for the ikee and the mynock via the improved Codex/native-transparency
pipeline (`skills/generating-images`, `skills/generating-rimworld-sprites`), retiring
donor art for both. Carried forward from `FOUNDRY_REBOOT_HANDOFF_202609070526.md`,
which recorded the ask but was told explicitly not to act on it yet — that hold is
lifted by this session's ruling.

## 🔴 OWNER RULING, 2026-09-07 — Ikee half REJECTED, Mynock half proceeds

Shown `ikee_south_sheet.png` (donor vs. redraw) and `ikee_north_final.png`, verbatim:
*"I liked the donor art better, alas."* Asked whether Mynock was still wanted:
*"Still interested in Mynock, yes. Do that in the background."*

- **Ikee: CANCELLED, not parked.** Keep the AA_Eyeling donor art exactly as-is.
  `Ikee_Rename.xml`'s own banner ("RENAME AND PLACE ONLY. THE ART IS UNTOUCHED")
  was already correct and needs no change. **Do not deploy, reference, or wire in**
  any of `Transient/art_gen/ikee/*` (`ikee_south_final.png`, `ikee_north_final.png`,
  the raw/sheet files) — they are dead work, kept for provenance only. If Ikee art
  becomes a live question again later, it starts fresh from this ruling, not from
  resuming these candidates.
- **Mynock: proceeds**, backgrounded per the owner's instruction — this item's
  scope narrows to Mynock only. Output goes to `Transient/art_gen/mynock/`,
  following the same pipeline/verify bar as below. `mlie.starwarsanimalcollection`'s
  `mynock` defName, wild-spawned across ~20 biomes, currently on unchanged donor art.
- This does **not** reopen or reverse anything about the Mlie fauna absorption
  itself (`MLIE_FAUNA_ABSORPTION_1`) — only Mynock's art.

## 🔴 BLOCKED, 2026-09-07 — Mynock generation froze the owner's screen with a UAC prompt

The background Mynock-generation agent hit a live Windows UAC "create local
account" dialog from `codex-windows-sandbox-setup.exe`, mid-run, on the
**shared** CODEX_HOME — not a fresh isolated `--codex-home` (the case
`CODEX_SANDBOX_SEED_TEMPLATE_1` already fixed). Owner, verbatim: *"That's not
ok... it asked for permission for the CODEX sandbox again. We CANNOT have a
pipeline that freezes my computer with a modal system access dialog."* Killed
the agent (`TaskStop`) immediately to unstick his screen.

Measured: the shared home's own `.sandbox/setup_marker.json` was recreated at
2026-09-07T21:47 UTC — ~3 hours after the seed template was captured (18:48
UTC) from that same home. The shared home re-ran its own sandbox setup
unprompted; the existing per-worker-home fix does not cover this case. See
`LESSONS_INBOX.md` 2026-09-07 entry.

**Do not dispatch another unattended/background Codex image-gen call for
Mynock (or anything else) until this is understood.** If Mynock art is
resumed, either (a) a human is present and watching to click through any
UAC prompt, or (b) someone roots out why the shared home's sandbox state is
being invalidated and fixes that first. This item stays blocked till then.

## Attended south-facing pass, 2026-09-07 (owner present, then went AFK)

Owner scoped it down: **3 base facings only** (south/east/north; west mirrors
east) — skip the 4 flying-animation frames and dessicated corpse texture for
now, donor art stays on those regardless of outcome.

Reference art pulled from `mlie.starwarsanimalcollection`'s AssetBundle (already
cached at `observed/inventory/bundle_textures/mlie.starwarsanimalcollection/...`
by the earlier killed run — 2243 textures, 0 re-extracted). Confirmed the def is
`Graphic_Multi` after all (bundle has `_south`/`_east`/`_north` + 4
`_flying_N_<dir>` + `_dessicated`), not `Graphic_Single` as guessed in this
item's spec above — correcting that assumption.

- **v1** (`mynock_south_raw.png` -> `mynock_south_noreg.png`, conformed with
  `--no-register`): validator PASS (1 soft WARN only, faint alpha inside
  silhouette). Correct canvas position and proportions. **But reads weak at
  actual gameplay scale** — thin outline, visible wing-bone ribs make it a
  spindly blob at the 96px "in-game" preview row. Owner's call on sight: iterate
  for a bolder look rather than accept.
- **v2** (`mynock_south_raw_v2.png` -> `mynock_south_v2_noreg.png`): re-prompted
  for a thick unbroken black outline and solid/opaque wing membranes (no rib
  linework) — **this fixed the legibility problem, reads as a clean bold bat
  silhouette even small.** But the raw generation came out squatter than the
  reference's proportions (validator: subject 214x195 vs ref's 214x218, aspect
  1.097 vs 0.982, REJECT x3) — a framing miss, not a style miss.
- Comparison sheet (donor | v1 | v2): `Transient/art_gen/mynock/mynock_south_sheet_v2.png`.

**Next step, when someone is next attended and watching for the UAC risk**: one
more south-facing generation combining v2's outline/solidity style with
explicit top-to-bottom edge-touching framing instructions (the framing note
that worked for other creatures in this pipeline — see the Atispec v3 prompt in
`art_review_alien_redraws_STATUS.md` for the exact wording pattern: "tail-spike
tip touching the very top edge... claw tips touching the very bottom edge").
East and north facings not started. **Paused here because the owner went AFK
mid-session** — no further Codex calls were made after that point.

- **Ikee** = `AA_Eyeling` (Alpha Animals donor ThingDef+PawnKindDef, shared defName),
  renamed/re-tuned into the Jawa clan pet via `Ikee_Rename.xml` / `Ikee_Tuning.xml`
  in `src/RimUtinni/UtinniPatches/Patches/`. Art was explicitly left untouched at
  rename time (`Ikee_Rename.xml`'s own banner: "RENAME AND PLACE ONLY. THE ART IS
  UNTOUCHED"). Now a small (1/3 original body size), messy, easy-to-train pet — a
  single great eye on tentacles. New art should read as a Jawa-kept pet at that
  reduced scale, not the original donor's creepy-wild presentation.
- **Mynock** = `mynock` defName from `mlie.starwarsanimalcollection` (the Mlie Star
  Wars animal collection absorption set, `MLIE_FAUNA_ABSORPTION_1`), wild-spawned
  across ~20 biomes. Currently rides donor art unchanged.

Both currently ride donor art; this item replaces it, using the harvest-fixed
`codex_image.py` pipeline (native RGBA transparency, no chroma-key stage) landed in
`CODEX_WRAPPER_HARVEST_FIX_1`.

## known gap this item also closes
`CODEX_WRAPPER_HARVEST_FIX_1` was closed with "🔴 Still owed: one authorized live
generation — nothing was proved against a real `codex exec` image turn" left
unresolved. This item's first generation call IS that authorized live proof; record
whether the `low` reasoning-effort default and the ask-for-alpha-in-prompt approach
actually hold up in anger, separately from the art content itself.

## verify
```
PROVE   generated PNGs for both creatures pass validate_sprite.py (canvas, alpha,
        silhouette-in-footprint) with no chroma-key stage invoked; deployed and
        LOOKED AT in-game at true scale per generating-rimworld-sprites doctrine
EXPECT  native RGBA alpha (not chroma-keyed), correct canvas for each def's
        graphicClass/drawSize, silhouette reads as the intended creature at game scale
LIES    a technically-valid PNG that reads wrong at game scale (magenta/checker
        never fires but the art still looks broken) — must be judged by looking,
        never scored by an instrument alone (owner doctrine, art-quality-by-looking)
```
