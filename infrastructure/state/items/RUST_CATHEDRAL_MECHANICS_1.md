## spec — the C# kit
Per `design/Jawa/worldbuilding/biomes/the_rust_cathedral.md`:
hum-mood system (a slow-moving attitude value voiced as layered tones, displayed
by the bolts' dances, with droid commentary and hysteresis wiring) · the
deep-drill response event (never described) · wall-tier mining defs (common deck
plate free to mine → dead smartsteel → the sacred tiers) · **living bolts as
mechanical wildlife** · **eel-fishing consequences**.

The governing rule from the sheet: the Cathedral is negotiated **by manners, not
by force** — mine the bulk freely, touch nothing sacred, and when the hum drops,
stop moving. *The bolts freeze first — watch them.*

---

## ⭐ ADDED 2026-09-07 (owner) — THE ROACHES: THE LAND CLEANERS

**Enhancing this item rather than filing a new one, per the owner's own
instruction.** It belongs here because the bolt-dance/hum-mood display and the
coolant eels are already this item's, and the roaches are the third leg of the
same ecology.

> Owner, 2026-09-07: *"reskin the cockroaches mod to pertain to the Scarlands
> around the Rust Cathedral and the Rust Cathedral itself. Both organic and
> artificial versions. Make them much smaller and the synthetic ones strangely
> tough and powerful. Cleaners of the area on land like the eels that live in the
> coolant rivers."*

### the donor, MEASURED 2026-09-07
**`LingLuo.Cockroach` — "Rim cockroach"**, already **ACTIVE** in the mod list.
`steamapps/workshop/content/294100/3196253802`. It ships exactly two creatures,
which map one-to-one onto the ask:

| def | label (donor) | bodySize | parent |
|---|---|---:|---|
| `Ling_Cockroach` | 巨型蟑螂 "giant cockroach" | 2 | `AnimalThingBase` → the **ORGANIC** roach |
| `Ling_Cockroach_Mechanoid` | 机械蟑螂 "mechanical cockroach" | 2 | `BaseMechanoidWalker` → the **SYNTHETIC** roach |

⚠️ Donor labels are **Chinese** — the reskin must relabel and redescribe both
regardless of anything else.

### what the reskin must do
1. **Much smaller.** Both are `bodySize 2` — bigger than a human. They should
   read as small scuttling things, not giants.
   🔑 **`bodySize` does NOT scale melee damage** (see the ceiling-fields lesson) —
   so shrinking them does not disarm them. That is *convenient here*: it is
   exactly how the synthetic ones stay **"strangely tough and powerful"** at a
   fraction of the size. Set the size down; tune armour/health/damage
   deliberately and separately, never by "scale all attributes".
2. **Two registers, one animal.** Organic roaches in the **Scarlands** around the
   Cathedral; synthetic ones in and near the **Cathedral itself**. The synthetic
   version is the unsettling one: small, patient, and much harder to kill than it
   looks.
3. **Cleaners, not vermin.** They are the **land counterpart to the coolant
   eels** — they clear the ground the way the eels clear the canals. That gives
   the Cathedral a closed ecology: eels in the coolant, roaches on the land,
   bolts in the air of its attention.
4. ⛔ **NOT part of the hum-mood system — ruled by the owner, 2026-09-07:**
   *"Leave the roaches out of the hum mechanics for now."*
   The bolts remain the **only** display of the Cathedral's attitude, and the
   survival rule stays as the sheet writes it: *when the hum drops, stop moving —
   the bolts freeze first.* **The roaches are fauna, not instrumentation.** Do not
   wire them to the attitude value, and do not give them a freeze/scatter tell.
   *(Read "for now" as reversible, not as an invitation — reopen only on his word.)*
5. **Salable?** The sheet already has *"bolt-shed curiosities and eel-catch —
   both salable, both watched."* Decide whether roach parts join that list, and
   whether harvesting them is one of the things the Cathedral *minds*.

### before assuming a pure-XML reskin
🔴 The donor ships **`Assemblies/`** (and a `1.6/Assemblies/`). **Read what the
DLL actually does before planning an XML-only reskin** — behaviour may be baked
into C# that a def patch cannot reach, and a reskin that only renames the label
will leave donor behaviour intact under a campaign name.
⚠️ Also check the donor's own `Patches/` folder for what it does to vanilla.

### cross-refs
- `SCARLANDS_MECHANICS_1` — the organic roaches live in its biome; the two items
  share the Scarlands surface and should not invent two different roach stories.
- `the_rust_cathedral.md` §the coolant eels, §the living bolts.
- Naming: new defNames take the tier grammar (`design/NAMING_SCHEME_PLAN.md`) —
  `RUT_` for campaign-specific, and "Jawa" is lore text only.
