# VEHICLE_RESKIN_LIVE_LOOK_1 — run 1, live, full-583

Scratch map (owner authorised), 16 vehicles spawned via `jawa/spawn_batch`: the four
draught vehicles × rot 0/1/2/3, in four rows at z=140/148/156/164.
Screenshots: `observed/bridge/vehicles_2026-08-21/{north,east,south,west}_lit.png`
(brightened 2.6× — the map is at night; the raw captures are legible but dark).

## RESULT: PASS on the art. FAIL found on the words. One criterion UNMEASURED.

### ✅ Criterion 1 — each of the four draws its own beasts, in all four facings

| | north | east | south | west | beasts drawn |
|---|---|---|---|---|---|
| OxCart | ✅ | ✅ | ✅ | ✅ | **2 orange-brown shaggy banthas** |
| CoveredCarriage | ✅ | ✅ | ✅ | ✅ | **2 pale cream rontos** |
| WarChariot | ✅ | ✅ | ✅ | ✅ | **2 yellow-green dewbacks** |
| Chariot | ✅ | ✅ | ✅ | ✅ | **1 yellow-green dewback** |

Species and counts match DECIDE's ladder on every facing. **West draws as a clean mirrored
east** — beasts lead, cart trails, nothing inverted or substituted. No missing facing, no
donor art, no magenta.

⭐ **Art-direction note 1 in the spec is half right and the half matters.** BUILD reported
*"ronto and dewback both came out olive-green… at sprite size they may not read as
different."* In **east and west they read as clearly different** — the ronto is pale cream,
the dewback yellow-green. In **north and south they converge** and are hard to tell apart.
So it is a per-facing problem, not a palette problem, and only two of the four facings have it.

### 🔴 Criterion 2 — the architect menu label. This is the FALSE PASS the item was built to catch, and it fired.

`rimworld/list_architect_designators` on `architect-category:vf-vehicles`:

    buildableDefName: AV_DogSled_Blueprint
    buildableLabel:   "Dog Sled"
    description:      "A sled pulled by four trained dogs used to travel over ice
                       and through snow. Absolutely terrible for anything else."

and the vehicle def the blueprint builds, read live through `jawa/get_def`:

    AV_DogSled   label: "eopie sled"
    description: "Two eopies in harness, and a flatbed of lashed scrap riding on
                  runners because wheels drown in soft sand."

🔑 **The blueprint is a third def — `<defName>_Blueprint` — and `EopieSled_Identity.xml`
never touched it.** A player opens Architect ▸ Vehicles, reads *"Dog Sled — pulled by four
trained dogs… over ice and through snow"* on a desert world, builds it, and owns an *eopie
sled*. The item predicted this exact shape and it is real on the shipped stack.

### 🔴 And the other four never got the identity pass at all

`jawa/get_def`, resolved live, post-patch:

| def | label | description opens |
|---|---|---|
| AV_DogSled | **eopie sled** | *"Two eopies in harness…"* ✅ done |
| AV_OxCart | Ox cart | *"A two wheeled cart **pulled by oxen**…"* |
| AV_CoveredCarriage | Covered Carriage | *"A **horse-drawn** four-wheeled vehicle…"* |
| AV_WarChariot | War chariot | *"…the driver steering the chariot with his reins…"* |
| AV_Chariot | Chariot | *"A simple **horse-driven** cart…"* |

`EopieSled_Identity.xml`'s own header states the complaint it exists to fix — *"The art was
already ours; the WORDS were still Alpha Vehicles'."* That fix was applied to the sled and
to nothing else, while the reskin went on to re-art the other four. All four now show
Tatooine beasts under text about oxen and horses. Filed as
VEHICLE_WORDS_STILL_SAY_HORSES_1.

### ⚠️ Criterion 3 — health tab labels — UNMEASURED, and not for lack of trying

The spec asks the health tab to read Left/Right **Bantha** / **Ronto** / **Dewback** from
`VehicleBeastLabels.xml`. **Two independent bridge gaps block it, and neither is a guess:**

1. `rimworld/select_pawn` refuses a vehicle — *"Could not find player-controlled colonist
   id 'AV_OxCart69647'."* — by id AND by name, although `jawa/set_pawn_faction` confirms
   the vehicle is **already in PlayerColony**. It filters on colonists, and a `VehiclePawn`
   is not one. No selection ⇒ no `open_inspect_tab`, no `get_ui_layout` on Health.
2. `jawa/get_defs` cannot reach the labels either. `fields: "components"` returns
   `["VehicleComponentProperties" × 5]` — the reflective reader flattens list elements to
   their class name and does not descend, so `VehicleComponentProperties.label` is
   unreadable. `jawa/get_def` returns `comps` (the CompProperties list) but not
   `components` (the vehicle's damageable parts), which is a different field.

⛔ **Do not read this as "the labels are wrong".** Nothing was observed either way. Filed as
VEHICLE_HEALTH_TAB_UNREACHABLE_1.

### Incidental, and it cost the first four screenshots
`rimworld/screenshot_cell_rect` returned `success: true` four times, for four different
cell rects and four different filenames, and wrote **four byte-identical PNGs**
(`md5 2e3fe5ca…`) — of the **Debug log window**, which was open and covering the map.
`rimworld/get_ui_state` named it (`topWindowType: LudeonTK.EditWindow_Log`); closing it
made every capture distinct. The tool captures the SCREEN, and a UI window over the target
cells is captured instead of them, with no warning. Filed as
SCREENSHOT_CAPTURES_OPEN_WINDOW_1.
