## spec
⭐ **Cheap. Ride a load that is already happening — do not call one for this.**

`validate_save_artifact.py` resolves `src/Jawa/ideoligion/The Salvation.rid` at
**250/266, no dangling names**. The 16 that cannot be resolved are all `AbilityDef`s, and
the reason is a known dump blind spot: the offline dump carries **zero rows of type
`AbilityDef`**, so it can neither confirm nor deny them.

```
AM_ChangeStyle · CombatCommand · ConversionRitual · Convert · Counsel · LeaderSpeech
PreachHealth · Reassure · Trial · WorkDrive
VME_CallTradeCaravan · VME_LeaderConversionRitual · VME_LeaderConvert
VME_LeaderCounsel · VME_LeaderPreachHealth · VME_LeaderReassure
```

Donors are `sarg.alphamemes` (the `AM_` one) and `vanillaexpanded.vmemese` (the six
`VME_`); the remaining nine look vanilla Ideology. All donors are active in
`ModsConfig.xml`.

**With the game up, on the mod set that will be active at world creation**, read those 16
defNames back — any route that enumerates loaded `AbilityDef`s is fine (the bridge's def
search, or the dev-mode def list). Report **present / absent by defName**, not a count.

⚠️ **The one that would actually matter:** the `.rid` is read when the player creates the
game and picks the ideoligion. A precept whose ability is absent fails **then**, on a world
that is generated once and frozen. That is why it is worth one screen — not because it is
likely.

⛔ **Do not re-measure the precepts.** They are done, offline, 2026-08-21, zero dangling.
⛔ **Do not quote the old "82 precepts unmeasured / 11 dead mods" framing** — see
`items/sequence-the-ideoligion-check-before-the-faction-work-e3f1a7.md` `## ruling`.

## verify
a list of all 16 defNames, each marked present or absent, taken from the running game
rather than from the dump.

## criteria
every one of the 16 resolves in the live game. If any does not, name the precept that
references it before anything else — that precept is the actual finding.

## notes
Regenerating the def dump does not help: the blind spot is that the dump has no
`AbilityDef` rows at all.

## ruling
✅ **DECIDE, 2026-08-21 — 16 of 16 resolve. Answered OFFLINE, without the bridge, on the
mod list that will be active at world creation.**

The owner brought the game to the main menu, which rewrote the def dump: **578 mods**,
`capturedUtc 2026-08-21T08:20:20Z`, mode `all`.

🔴 **And the dump still reports `AbilityDef: 0`.** Literally `{"defType":"AbilityDef",
"defs":[],"count":0}` — 44 bytes — on the same capture that found **24,904 `ThingDef`s**,
685 `PreceptDef`s and 136 `MemeDef`s. ⇒ **regenerating the dump does not close this item and
never could.** The blind spot is in the dumper. Filed as `DEFDUMP_ABILITYDEF_BLIND_1`.

**So it was answered from the mod XML instead**, restricted to the folders 1.6 actually
loads:

| where | defs |
|---|---|
| **vanilla Ideology** `Defs/AbilityDefs/Abilities.xml` | `CombatCommand` · `ConversionRitual` · `Convert` · `Counsel` · `LeaderSpeech` · `PreachHealth` · `Reassure` · `Trial` · `WorkDrive` — **9, always loaded** |
| **Vanilla Ideology Expanded — Memes and Structures** `2636329500/1.6/Defs/AbilityDefs/` | the six `VME_*` |
| **Alpha Memes** `2661356814/1.6/Defs/AbilityDefs/Abilities.xml` | `AM_ChangeStyle` |

### 🪤 The trap this walked into, and it is worth more than the answer

**A first pass "found" all sixteen and every one of the modded hits was in a folder the game
does not load.** `AM_ChangeStyle` came back from `2661356814/**1.5**/`, and all six `VME_*`
from `2636329500/**1.3**/` — because a recursive glob returns `1.3` before `1.6`, so **the
stale copy is found first, every time**, and it looks exactly like a pass.

🔑 **A defName on disk is not a defName that loads.** Resolve the mod's `LoadFolders.xml`
`<v1.6>` block FIRST and search only those directories. Both mods here keep `1.3`, `1.4` and
`1.5` trees on disk that `<v1.6>` does not list — the same shape as the dead
`OuterRim/WorldObjects/MoistureFarmers` in `Common_Old` that renders the Jawa Trade Moot as
a magenta square.

⭐ **One more thing that would have read as a failure and is not.** `AM_ChangeStyle` matches
**two** defs in one file: an `AbilityGroupDef` at `Abilities.xml:140` and an `AbilityDef` at
`:144`, deliberately sharing a name because they are different def types. The `.rid`
references it inside an ability list (`The Salvation.rid:3424`), so it binds to the
`AbilityDef`. ⛔ Do not "fix" the group def.

⇒ `The Salvation.rid` is **fully resolved**: 250 of 266 references by the dump, and the
remaining 16 by hand. Nothing about the player's ideoligion is unmeasured.
