# MODCHECK_SHELVED_TOGGLE_COMPONENTS_1 — restore the two shelved toggle-flip components now that jawa/mod_settings_field exists

Caused by `BRIDGE_STATIC_SETTINGS_FIELDS_1`, which was closed (sha
`05f2b4ce0`, an unrelated commit — see that item's own correction note)
WITHOUT actually completing its own "two shelved components restored and
green" criterion. The mechanism this item needs now genuinely exists
(`jawa/mod_settings_field`, live-proved on `RimMandrake.Pits.PitsSettings.
trapTriggerEnabled` — commit `c90aa2d71`); wiring it in is what's left.

## spec

`src/RimMandrake/Utils/modcheck/suite.py`'s `set_setting()` (line ~211)
hardcodes `rimworld/update_mod_settings`, which only resolves INSTANCE
fields and refuses `public static` ones — the exact shape both shelved
components need. Update `set_setting()` to use `jawa/mod_settings_field`
instead (it already tries static first, falls back to instance via an
assembly-matched `Mod.GetSettings<T>()` — a strict superset of what
`update_mod_settings` could do), or add a static/instance-aware branch
that calls the new tool only when needed. Preserve the existing contract:
independent read-back verification, `persist=False` in-memory-only default
(check whether `jawa/mod_settings_field`'s `set` action needs a
`persist`/`write` parameter added, or whether a static field write is
inherently non-persistent since it's never serialized to
`ModSettings.xml` in the first place — verify this assumption against a
real mod before assuming it).

Then restore the two shelved components, both currently marked "NOT a
chain... UNCOVERED" with the restore instructions already written inline:
- `src/RimMandrake/Graffiti/validation.py` (~line 185): `viewerReactionEnabled`
  and `breachBiasEnabled` write+read-back, against `RM_GraffitiMod.cs`'s
  static fields (~line 31).
- `src/RimMandrake/StructureInjections/validation.py` (~line 225): the
  `enabled` toggle write+read-back.

## verify

```
PROVE   set_setting() flips a STATIC field live and reads it back changed,
        via jawa/mod_settings_field, on a minimal-list quicktest; both
        restored components run green in their mod's own suite
EXPECT  no regression on any suite that only ever used instance fields
        (route Pits/etc. through the same set_setting() unchanged in
        behavior, since jawa/mod_settings_field's read-back was proven
        identical in shape)
LIES    "restored" without an actual live run of both suites; a
        set_setting() that silently no-ops on a static field because it
        still calls update_mod_settings under the hood in some code path
```

## not chasing

Any mod beyond Graffiti/StructureInjections — this item is scoped to the
two components the original shelving comments name, not a broader
modcheck audit (that's `MOD_VALIDATION_RETROFIT_1`, still blocked on the
owner's sheet-format ratification).
