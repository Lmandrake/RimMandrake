# HABITABLE_RING_IS_40_57_1 — the ring is 40–57, ruled by the owner

## spec

🔴 **OWNER, 2026-08-21: "Select 40-57 habitable ring."** This closes
`canon.yml > needs_ruling.HABITABLE_RING_ARC_RULING_1`, which had stood provisional at
34–57 since the canon build, with the owner deliberately abstaining on 2026-08-20.

⚠️ **The provisional value was the OTHER one, so this is a reversal, not a confirmation.**
`canon.yml` held `habitable_ring_arc: [34, 57]` and listed `[40, 57]` under
`habitable_ring_superseded`. REP has swapped them at the source and recorded the ruling
there. **What is left is propagation, and that is why this item exists.**

Every file that asserts the ring must now read 40–57, and every file that argued FOR
34–57 needs a line at the top saying it was overruled — nobody reads backwards:

| file | what it says today |
|---|---|
| `src/RimMandrake/Utils/ashkarr_paint.py:76-77` | *"the habitable ring is ~34-57 degrees of arc"* — the comment the whole 34–57 case rested on |
| `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md:237` | asserts 34–57 |
| `design/Jawa/worldbuilding/fauna_placement.md:13` | asserts 34–57 |
| `design/Jawa/worldbuilding/worldgen_interactive_def.md:27, :134, :455` | already says 40–57, with tile counts 2,477 of which 1,791 land — **now the correct one** |
| `design/V2_DREAMS.md:1441` | already says 40–57 |

🔑 **The Setdown is the thing to check, and it is the reason this was contested.** The
player's home is sited at arc **56.9** and `ashkarr_paint.py:74-95` calls it *"the OUTER
EDGE of the habitable ring"*. That phrase reads true under both rulings — 56.9 is just
inside 57 either way — so **the siting does not change and the start tile does not move.**
What changes is the arc-34–40 band, ~700 tiles, which is now **margin, not habitable**.

⛔ **Do not "correct" the settlement census against this.** The ring is a DESIGN band; the
72 settlements span arc 10.0 to 104.6 with a median of 75.0, and always did. `canon.yml`
already carries that warning — keep it.

## verify

- `grep -rn "34.*57\|34–57" design/ src/` returns no surviving assertion of the ring as
  34–57 except inside an explicit "overruled" note.
- `python3 src/RimMandrake/Utils/check_canon.py` reports 0 contradictions.
- `canon.yml > needs_ruling` no longer contains `HABITABLE_RING_ARC_RULING_1`.
- The Setdown is still tile 2476 at arc 56.9. If a propagation edit moves the start tile,
  it is wrong — stop and say so.

## criteria

One arc, in every file, traceable to the owner's 2026-08-21 ruling, with the losing side
told it lost in the file where it argued.
