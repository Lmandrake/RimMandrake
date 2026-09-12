# CATHEDRAL_PLAYER_CONCEALMENT_ARC_1 — the Rust Cathedral ↔ player relationship arc

Source of intent: `design/Jawa/worldbuilding/biomes/the_rust_cathedral.md` §7b
amendment (owner-ratified 2026-09-10, frozen) — it hides from and dislikes the
player at first; the Rakatan gravship agitating the Empire is exactly the
scrutiny it has spent millennia avoiding; the salvage loop is its cover; the
§7b manners are how the player earns their way out.

## spec

`design/Jawa/cathedral_concealment_arc_spec.md` (drafted 2026-09-11). Shape:
four stages (WARY → TOLERATED → VOUCHED → REVEALED) driven by one new GM-
blackboard counter (Cathedral Regard, kyber-spec pattern, shadow-mode first,
never a UI gauge) composed with the existing faction-13 goodwill ledger and
story flags — no parallel relationship system. Needle-movers (§2) are concrete
player acts: manners on Cathedral ground, Assailant-register missions, Heat
kept away vs pursuit events landing there, mindstone/kyber sales, the origin-
canon §4 restore choice (priced there, mirrored here), protecting vs exposing
the cover. Surfacing (§3) rides the kit's hum-mood machinery
(`RUST_CATHEDRAL_MECHANICS_1`: band baselines, stage-keyed `RUT_HumCommentary`
pools, bolt display) plus deniably-sourced missions/boons — text/menu only,
game whole without the Oracle. Reveal beat (§5): one escorted descent showing
SCALE and ALIVENESS only, scoped to the player, knowledge gate
(`RUT_mechanoid_origin_canon.md` §5, hard) opens exactly there; bans 2/6 hold
forever. Failure directions (§6): exposure → the Cathedral goes dark
(asymptotic in v1, CARD A3); betrayal → rationed patience, never raids — the
ruled −75/0 hysteresis bounds everything, and the arc closes for good. No new
defNames coined; every cited token binds at the kit's or origin canon's build.

## verify

- Shadow-mode blackboard test: each §2 input moves Regard in the stated
  direction; ordinary bulk salvage moves nothing; nothing writes a save stat.
- Register grep: no player-facing string attributes agency to the Cathedral
  before stage 3; post-reveal strings contain no mercy explanation (ban 2) and
  no drill description (ban 6).
- The reveal fires once, only from VOUCHED + the late-game flag set, and
  changes no faction-visible text (the world does not learn).
- Betrayal consequences never exceed the vanilla faction-13 hysteresis — no
  raid, no manhunt, in any authored consequence.
- Every beat completes with the Oracle absent; no Force route; no worldgen.

## criteria

- Spec registered in `design/INDEX.md`; the frozen sheet's §7b carries a
  one-line DRAFTED pointer (pointer only — no ruling touched, freeze intact).
- All five owner cards (A1–A5) reach the owner; no build work starts on
  unruled card material (A1 reveal-usher, A3 exposure endpoint, A4 survey
  beat gate quest authoring in particular).
- No duplication of existing machinery: hum-mood, Heat blackboard, pursuit
  spine, restore-choice pricing are cited, not restated.

## Owner cards

- **A1** — Does the Utinni know the Cathedral is alive? Her vouching vs the
  hard knowledge gate: (a) she is the gate's sole exception and the reveal's
  usher, or (b) she vouches into what she believes is dead protocol and learns
  at the reveal beside the player. Spec survives either; recommends (b) as the
  stronger scene.
- **A2** — Reveal scope: §5 discloses aliveness + scale only. More of §GM in
  the spoken reveal (Assailants, decline, reserves), or held for a later
  sitting?
- **A3** — Can exposure complete? Full Imperial discovery as a losable v1
  thread, or asymptotic pressure narrated but never played? Spec assumes
  asymptotic for v1.
- **A4** — The Imperial-survey misdirection beat (spec §4): in or out? The one
  place the player actively performs concealment; adds a quest surface. K2
  anti-laundering symmetry already applied (protecting it scrubs no Heat).
- **A5** — Where does selling the anomaly start counting as exposure:
  Imperial-aligned buyers only, or any sale during high Heat? One sentence
  rules it.

## All five cards RULED — owner sitting 2026-09-12
A1 she KNOWS (receives the Rakatan transponder on dead frequencies — new lore
mechanism, propagate at build); A2 reveal = aliveness + scale only; A3
exposure CAN complete — real losable outcome (spec §6.1 amended, asymptotic
assumption superseded); A4 surveyor-misdirection quest IN; A5 sale exposure =
volume, not identity. Recorded verbatim in the spec's Cards section. Build
unblocked — rides RUST_CATHEDRAL_MECHANICS_1 (FOUNDRY) + quest authoring.
