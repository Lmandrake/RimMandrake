# ⛔ DROPPED 2026-08-21 — THE MOD STAYS. Read this before anything below.

🔴 **OWNER, 2026-08-21:** *"If Tribal Furniture does not need to be cut, then don't. I did
wonder why it was causing trouble. That's fine, leave it in."*

**Everything below rests on a premise that is FALSE.** The item drops the mod because
34–39 texPaths read as dead and it "renders entirely as placeholder". Measured 2026-08-21:

- the mod ships **138 PNGs**;
- **13** of its defs declare `<graphicClass>TribalFurniture.Graphic_Appearances_Multi</graphicClass>`
  out of its own `TribalFurniture.dll`, and those 13 are exactly the ones flagged;
- their `texPath` is a **stem** the class expands with a stuff infix, so the file on disk is
  `XERTribalBed_Bricks_north.png`, not `XERTribalBed_north.png`.

`jawa/texture_audit` assumes vanilla `Graphic_Multi` suffixing and cannot see a custom
resolver, so it reported present art as dead — `TEXTURE_AUDIT_CUSTOM_GRAPHICCLASS_1`.

✅ **The safety work below was done anyway and its findings stand**, should anyone ever cut
this mod for a different reason: nothing is disarmed (0 weaponTags / 0 apparel / 0 tradeTags
across its 64 ThingDefs) and 0 authored references die (the 368 that look external are all
`recipeUsers`/`fixedBillGiverDefs` the mod injects into Core, plus runtime caches, which
vanish with it). `ModsConfig.xml` was never edited.

---

# DROP_TRIBAL_FURNITURE_MOD_1 — the owner ruled drop it; the save already names it 34 times

## spec

🔴 **OWNER, 2026-08-21: "Let's drop the entire mod."** Asked as cut-with-Cherry-Picker vs
leave vs fix-the-paths; he chose something stronger than all three — **remove
`xercaine.tribal.furniture` from the mod list**, 578 → 577.

**Why:** `first_light.py` found 53 dead texPaths across the whole 578-mod stack and **34 of
them are this one mod** — every table, bed, bench, styling station and their blueprints
point at art that is not on disk. A mod rendering entirely as placeholder earns nothing.

🔴 **BUT REP CHECKED THE KEEPER SAVE FIRST, AND IT IS NOT A CLEAN PULL.**
`world/WORLDMAP_gen.rws` — the first-draft v1 keeper — **already contains 34 `XER_`
defNames**, as `<li>` entries in a list of `Blueprint_*`, `Frame_*` and
`Blueprint_Install_*` names. Not on world objects; in a serialized def list.

⚠️ **This is the error class that a mod change cannot fix.** `rimworld-savegame` draws the
distinction and it decides how much this costs:

| error | means |
|---|---|
| `Could not resolve cross-reference` | the def LOADER, against the live mod set — fixable by changing mods |
| **`Could not load reference to`** | **Scribe: the SAVE holds a dead name.** No mod change fixes it |

⇒ **Determine which of the two this list produces BEFORE touching `ModsConfig.xml`.** If
the list is a discardable convenience — an architect-menu memory, a knowledge record —
RimWorld will drop the unknown entries and move on. If Scribe binds them, the keeper save
takes 34 dead references and the owner's v1 world is damaged to remove art nobody sees.

**The order of operations, and it is not optional:**
1. **Identify the enclosing element** of those 34 `<li>` entries. REP could not pin it
   cheaply and did not guess. This one fact decides everything below.
2. **Test on a COPY.** Back up, drop the mod, load the copy, read `Player.log` for both
   error strings above. ⛔ Never test this on `world/WORLDMAP_gen.rws` itself.
3. ⚠️ **Rebuild the tag → surviving-item index before concluding the drop is safe.**
   Cutting the last item carrying a weapon or apparel tag silently disarms every pawn kind
   whose tags ALL go to zero — see `rimworld-content-moderation`. Furniture is unlikely to
   carry weapon tags, but "unlikely" is what that trap feeds on. This interacts with
   `WEAPON_TAGS_MATCH_NOTHING_1`, which is already counting bare-handed kinds.
4. ⚠️ **`validate_patch.py --live` CANNOT prove independence from a mod you are REMOVING** —
   every reference still resolves while the donor is installed. The check is a separate
   pass that drops the departing packageId and asserts nothing points there.
   `deploying-and-liveness.md` carries this.
5. Only then: the `ModsConfig.xml` edit, which is **the owner's**, plus a fresh def dump.

🔑 **`oskarpotocki.vfe.tribals` is a DIFFERENT mod and is not in scope.** Both matched a
search for "tribal"; only `xercaine.tribal.furniture` is the one with no art.

⚠️ **Also verify the premise before executing on it.** The paths may exist under a
`LoadFolders` or version folder the audit did not walk — that was the third option the
owner declined, but if step 1 finds the drop is expensive, a five-minute path check is
worth re-offering to him rather than damaging a keeper save.

## verify

- The enclosing XML element of the 34 `<li>` entries is named in this item's closing note.
- A COPY of the keeper save loads after the drop with **zero** `Could not load reference
  to` lines naming `XER_`.
- The tag → surviving-item index is rebuilt post-cut and no pawn kind newly falls to zero.
- A drop-the-packageId reference pass reports `references that die 0`.
- `ModsConfig.xml` parses to **577** `activeMods`, counted by parsing, not by `grep -c`.

## criteria

The mod is gone, the keeper world still loads clean, and nobody was disarmed by it.

---

## 🔴 OWNER, 2026-08-21 03:11: *"It'll be fine. I'll just remake the world again."*

**This retires the caution above, and most of the ordering with it.** The 34 `XER_` names
in `world/WORLDMAP_gen.rws` were only expensive because the save was treated as
irreplaceable. The owner has accepted a remake as the recovery path, so:

- ⛔ **Steps 1 and 2 are DROPPED.** Do not pin the enclosing XML element, and do not
  rehearse the drop on a copy. If the keeper takes dead references, the answer is a
  remake, and he has said so.
- ✅ **Steps 3, 4 and 5 STAND and are unaffected by the ruling.** The tag → surviving-item
  index, the drop-the-packageId reference pass and the `ModsConfig` count are about the
  MOD SET, not about this save. A silently disarmed pawn kind survives a remake.
- 🔑 **Do it BEFORE the remake, not after.** A world generated on 577 mods never contains
  an `XER_` reference at all, so the whole problem stops existing rather than being
  repaired.

⚠️ **The path-check option the owner declined is now cheaper than the drop and should NOT
be re-offered** — he has ruled twice on this mod. Drop it.
