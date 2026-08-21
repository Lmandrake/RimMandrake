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
