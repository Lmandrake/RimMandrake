# Blast door `_FrameAsync_east` — measured brief before drawing

_CREATE, 2026-08-13. Three files owed. Written before the first pixel because the
registration is measurable and guessing it costs a redraw._

## The three targets

Mod: **Doors Expanded Star Wars edition**, `Lumi.doorsexpanded`, workshop
`3550435517`, path `Textures/Things/Building/Door/Blast/`.

| file | current | def |
|---|---|---|
| `SWDoorBlastDoor_FrameAsync_east.png` | 757 B, **267×267, alpha max 0** | `PH_DoorBlastCDoor` |
| `SWDoorBlastBDoor_FrameAsync_east.png` | 757 B, same | `PH_DoorThickBlastBDoor` |
| `SWDoorBlastDDoor_FrameAsync_east.png` | 757 B, same | `PH_DoorBlastDDoor` |

⛔ **Do NOT touch `PH_DoorBlastDoor`** — base Doors Expanded (`3532342422`),
different packageId, and its `_FrameAsync_east` is healthy at 16,946 B.

⚠️ **267×267 is a placeholder size, not the target.** The correct east canvas is
**933×933**, taken from each door's own healthy `Frame_east`.

## ⭐ Why this is origination and not a mirror — the check that decides it

The obvious shortcut is "mirror the healthy sibling". **It is right for north and
wrong for east**, and only measuring shows that.

**North** — `FrameAsync` really is ~a mirror of `Frame`:

```
SWDoorBlastBDoor   Frame_north 406x431 @x=3      FrameAsync_north 392x431 @x=405
mirror alpha-mismatch:  BDoor 0.70%   DDoor 0.39%   Door 0.38%
differences sit on the subject's two vertical edges; the interior is identical
```

**East** — it is NOT. Measured on the base mod's *healthy* east pair, the only
one in the stack:

```
DoorBlastDoor_Frame_east       224x224   subject 128x68 at (40,98)
DoorBlastDoor_FrameAsync_east  224x224   subject 155x65 at (33,98)
mirror alpha-mismatch: 13.61%
```

**Seen edge-on the async leaf is genuinely different art** — wider and slightly
shorter, not a reflection. So a mirrored `Frame_east` would be wrong, and wrong in
a way that validates clean.

⚠️ This is the `CereanTuft` trap in reverse. There the rule was *hash the sibling
set before assuming a missing facing needs drawing*; here the sibling set says
"mechanical" for one facing and "originate" for another. **Check the facing you
are actually drawing.**

## The transform, from the healthy base-mod pair

Frame_east → FrameAsync_east, normalised so it carries to 933×933:

| property | Frame_east | FrameAsync_east | ratio |
|---|---|---|---|
| subject width | 128 | 155 | **×1.21** |
| subject height | 68 | 65 | ×0.956 |
| left edge x | 40 | 33 | shifts **left** 7 px (of 224) |
| **top edge y** | **98** | **98** | ⭐ **identical** |

**The top edge is preserved exactly.** That is the anchor — same discipline that
made `CereanMane_south` cheap: register to a measured invariant instead of
eyeballing, then the only judgement left is the art itself.

So on a 933×933 canvas, starting from that door's own `Frame_east` subject:
widen ~21%, shorten ~4%, shift left ~3% of canvas width, and **keep the top edge
where `Frame_east` has it**.

## Masks — check per file, do not assume

Naming is inconsistent in this mod and both forms exist:

```
SWDoorBlastBDoor_Frame_east_m.png     <- underscore before m
SWDoorBlastBDoor_Frame_northm.png     <- no underscore
SWDoorBlastBDoor_FrameAsync_northm.png
```

There is **no** `FrameAsync_east` mask in the SW mod today, while base Doors
Expanded ships `DoorBlastDoor_FrameAsync_eastm.png`. Establish whether the def's
graphic needs one before shipping art without it — a missing mask means the door
will not tint, which is the same silent-failure class as a wrong texPath.
