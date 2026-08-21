# VEHICLE_IDENTITY_TEXT_PASS_1 — the four reskinned vehicles still describe oxen and horses

## spec

`EopieSled_Identity.xml` states the job in its own header: *"The art was already ours; the
WORDS were still Alpha Vehicles'. A player on a desert world was reading 'a sled pulled by
four trained dogs…' under a picture of two eopies in the sand."* **That pass was applied to
the sled and to nothing else.** The reskin then re-arted four more vehicles and left their
text untouched. Read live 2026-08-21 through `jawa/get_def` on full-583, post-patch:

| def | label | description opens | drawn as |
|---|---|---|---|
| AV_DogSled | **eopie sled** | *"Two eopies in harness…"* | 2 eopies ✅ |
| AV_OxCart | Ox cart | *"A two wheeled cart **pulled by oxen**…"* | 2 banthas |
| AV_CoveredCarriage | Covered Carriage | *"A **horse-drawn** four-wheeled vehicle…"* | 2 rontos |
| AV_WarChariot | War chariot | *"…the driver steering the chariot with **his reins**…"* | 2 dewbacks |
| AV_Chariot | Chariot | *"A simple **horse-driven** cart…"* | 1 dewback |

🔴 **AND THE BLUEPRINT IS A THIRD DEF THAT EVEN THE SLED MISSED.**
`rimworld/list_architect_designators` on `architect-category:vf-vehicles`:

    buildableDefName: AV_DogSled_Blueprint
    buildableLabel:   "Dog Sled"
    description:      "A sled pulled by four trained dogs used to travel over ice and
                       through snow. Absolutely terrible for anything else."

`AV_DogSled` reads *eopie sled* / *"Two eopies in harness…"*; `AV_DogSled_Blueprint` still
reads *Dog Sled* / *four trained dogs*. **A player reads the dog text in the Architect menu,
builds it, and owns an eopie sled.** Whatever is patched here must be patched on
`<defName>_Blueprint` too, for all five.

⛔ **Text only.** No stat, no geometry, no `key`, no `tags` — `VehicleBeastLabels.xml`'s
header is right that `key` is a mechanical identifier wearing a cosmetic hat, and the same
applies here. Ice and snow references are the specific thing to kill: this is a desert world.

## verify

Live, over the bridge, with the game up:

    jawa/get_def {"defName":"AV_OxCart","defType":"ThingDef"}        -> label, description
    …AV_CoveredCarriage, AV_WarChariot, AV_Chariot, AV_DogSled
    rimworld/list_architect_designators {"categoryId":"architect-category:vf-vehicles"}
      -> buildableLabel and description for each *_Blueprint

## criteria

- none of the five vehicle descriptions names an ox, a horse, a dog, ice or snow
- each of the five `*_Blueprint` designators reads the SAME label and description as the
  vehicle it builds — checked in the architect list, not in the XML
- the beast named in each description matches DECIDE's ladder: OxCart bantha ×2,
  CoveredCarriage ronto ×2, WarChariot dewback ×2, Chariot dewback ×1, DogSled eopie ×2

## notes

Filed by CHECK 2026-08-21 from `VEHICLE_WORDS_STILL_SAY_HORSES_1`, off
`VEHICLE_RESKIN_LIVE_LOOK_1/run-1@full-583`.
Evidence: `observed/bridge/VEHICLE_RESKIN_LIVE_LOOK_1_2026-08-21.md`.
The ART is confirmed correct on all four vehicles in all four facings — see the screenshots
in `observed/bridge/vehicles_2026-08-21/`. Only the words are wrong.
