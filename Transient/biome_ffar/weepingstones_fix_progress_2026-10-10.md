# Weeping Stones fix progress — 2026-10-10

## Part 1 — enact.py root fixes — DONE

`src/RimMandrake/Utils/art/enact.py`, proven by `src/RimMandrake/Utils/art/selftest_enact_ws.py`
(28 checks; 20 of them FAIL on the pre-fix enact.py, every class represented; art selftests 19/19 GREEN).

1. Pick on donor art no longer counts as "already live" (old ~L582): only a pick of the **donor original** column
   itself does. A render pick goes to OUR path — a Graphic_Random folder of ours (`<base>_<letter>.png`), or
   `<category>/<row>/<row>` in the def's mod with the row's own def texPath moved there (placeholder `<color>` tint
   dropped; other defs on the same vanilla path untouched). A folder this run fills sheds unkept pictures (retired, archived).
2. Ticked variants (explicit, not `variantsDefault`) ship: folder files, or `<res>V_<L>` + `alternateGraphics` (GorgV_G convention).
3. A note asking for rename/description is NOT followed by an art job alone: TODO until `--mark-done`; also re-raised
   for notes an earlier run already moved to notes_followed; `--mark-done` records that def half.
4. Redraw reference: "based on (x)" -> column x; "drop/remove ... art", "redo completely", "total regen", or a ✕ -> none.
5. Catch rows (`RM_XCatch`) wait for `RM_X` to be settled (picked letter, or a live render of its redraw); catch jobs drawn
   earlier are withdrawn to `_withdrawn/` (active ones listed); once settled the catch is filed with RM_X's picture as reference.

code_review_status: enact.py and the new selftest are DIRTY by default (no review run) — nothing extra is required to commit.

## Part 1b — two more enact defects (95e6b3173, 53edd787d)
- Every `--mark-done --evidence "OWNER: …"` question now surfaces in CONFLICTS, even on rows with art jobs
  (Rot run: 11 of 14 rename questions were hidden). Selftest check 6.
- A note whose per-facing art jobs were all withdrawn reopens and re-queues (even after its def half was marked done);
  a re-filed redraw takes the next free `_v<n>` id, never a withdrawn one's.

## Part 2 — Weeping Stones rows — DONE
- **13 picks installed** (enact --apply, 53edd787d): Burrak, Gorrask, Ivvol, Karrek, Sillik, Tirbak now draw OUR art at
  `Things/Pawn/Animal/<row>/<row>` (their own PawnKindDef texPath moved, placeholder tint dropped; other defs on the vanilla
  path untouched); Bladderquill, Dewblade, Dewgourd, Dripfringe, Rockfinger, Salvecomb, Shadefern pick B in their folders.
  Unkept A retired (archived) for Dewblade, Dewgourd, Dripfringe, Rockfinger, Salvecomb.
- **Variants shipped**: Bladderquill A+B, Shadefern A+B, Steamfrond B, Verdimoss B, Weepmat B (folder files);
  Fanback C as `FanbackV_C` + alternateGraphics (chance 0.5).
- **Renames** (label-level, defNames unchanged): Kirruk -> "dewglider"; Vizhik -> "fan eel" (also its catch, meat, breeding stock,
  Ivvol's description mention). NOT changed: the C# Mod Settings label "Vizhik escape chance" (needs a DLL rebuild).
- **Descriptions** (81644fae0): Ambrosia (new UtinniPatches description patch), Huldu, Loomu, Skarrin, Ssurr, Vhakk, Fan Eel;
  def halves recorded with --mark-done. Vellak "after art" -> `WEEPINGSTONES_SETTLED_FOLLOWUPS_1` (also enact TODO).
- **Catches**: 21 early catch jobs withdrawn to `D:\Luke\dev\_artpipe\_withdrawn\` (done ones not to be installed);
  Huldu/Loomu/Murrin/Skarrin/Vizhik catches BLOCKED until the creature is picked (enact files them then);
  Ivvol/Karrek catches re-filed with his picked C as reference. Tracked in `WEEPINGSTONES_SETTLED_FOLLOWUPS_1`.
- **Redraw references**: v1 renders made against his reference instructions withdrawn (Ambrosia, Loomu, Vizhik, Murrin
  "redo completely", Vellak, Huldu v1 — v2 from (c) remains); re-filed as v2: Ambrosia/Loomu/Vizhik/Murrin with no
  reference, Vellak with his (b). All other pending jobs of the sheet checked: wsvar variant jobs reference our own art (fine).
- RM_Dewshrooms held (its folder is The Rot's `RotSporeKit/Seadew`; B/C/E already there pixel-identical).
- Fish C picks (Duul, Ikkal, Tarrik, Ullo, Vobbal) marked done: live since 693ba6346, pixel-identical.

## Scope invented by earlier agents (owner decides; NOT reverted)
- `RM_Colossia`: a whole new creature def (stats, body) replacing ColossusToad on the roster — he asked for a rename + redraw.
- "korrim": new spice def `RM_Korrim`, Steamfrond harvest changed from RM_RawSalt, murrin broth recipe changed, plus a pending
  art job `wsitem_korrim_v1` — he asked only "Creates a unique Star Wars cuisine spice. Improve the description."
- `RM_Reeds_OwnArt.xml` repoints Odyssey's `Plant_Reeds` globally (every biome) from a biome-scoped sheet.
- Huldu "fur that is a trading commodity": described, not built (no fur/leather def) — question in the follow-up item.

## Deploys
Game measured NOT running (`./game`), so all deployed and VERIFIED in sync: SWBestiary (21 files), UtinniPatches (17),
`--compose biomes` (34; includes The Rot's committed state, as the composed mod requires). SWBestiary still needs
`--apply --prune` to delete the old Dactillion flyer frames from the game folder (owner: "remove F"). Visible after restart.

## Re-verification
Re-ran the verifier's checks per row (bytes or decoded pixels in src bound by a def texPath / folder / alternateGraphics;
labels; descriptions vs 53a55b750^; redraw jobs + references; catch blocking). Sanity probes: vanilla A, retired A, unbuilt
Huldu C and Murrin's unchanged description all correctly read as absent. **47 ruled rows: PASS 47, FAIL 0** (5 catch rows
pass as "blocked by his own note until the creature is settled"; redo rows pass on a correct job, his pick still owed).

## Commits
(pending)
