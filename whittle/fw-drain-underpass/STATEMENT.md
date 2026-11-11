# Drawbridge underpass proof health contract

The underpass acceptance row must reliably detect harm to a pawn beneath the raising bridge.

- Raising the bridge is reported safe only when the underpass pawn stays in the same cell and its measured injuries are unchanged.
- Worsened injury severity, replacement injuries and changed injury body parts cannot pass merely because the injury count stays the same.
- Missing or malformed health readings are reported as harness failures instead of silently becoming an empty healthy list.
- Focused offline regression checks execute the production acceptance row and demonstrate the intended unchanged-health case passes while the false-safe cases fail.
