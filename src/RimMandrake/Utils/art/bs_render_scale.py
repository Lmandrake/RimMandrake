"""Big and Small's adult humanlike render scale, with no numpy or PIL, so the Windows interpreter that reaches the
live bridge (python.exe, no numpy) can import it. fit_head_canvas re-exports bs_render_size from here."""


def bs_render_size(size_offset, head_mult=1.0, base_body_size=1.0):
    """(body, head) render scale Big and Small draws an ADULT humanlike at, for a body-size offset (SM_BodySizeOffset
    + SM_Cosmetic_BodySizeOffset) on a race of base_body_size, at B&S's default settings (READ 2026-10-20, ilspycmd
    of workshop 2925432336 1.6/Base/Assemblies/BigAndSmall.dll, BSCache.GetBodyRenderSize / GetHeadRenderSize and
    BSSettings defaults: headPowLarge 0.8, headPowSmall 0.65, visualLarger/SmallerMult 1, scaleBodyTypes false).
    RenderingPatches multiplies the head node's DrawData scale by `head`; head-slot apparel rides on the head node,
    so hats scale with it. head_mult is SM_HeadSize_Cosmetic (stat base 1.0; a gene statOffset moves it)."""
    lin = max((base_body_size + size_offset) / base_body_size, 0.2)
    body = lin ** 0.7 if lin > 1 else lin ** 0.75 if lin < 1 else 1.0
    head = max(body - 0.5, body ** 0.8) if body > 1 else body ** 0.65
    return body, head * head_mult
