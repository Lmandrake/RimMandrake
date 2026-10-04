# Canon image gap-fill — 2026-10-04

Owner request: the canon library showed nothing for Gorg; fill canon-beast gaps from Wookieepedia (canon and /Legends).

## Root cause (gorg)
There was **no gorg entry in the library at all** — not empty images, a missing directory. None of
`RSW_Gorg`, `RSW_LongtailGorg`, `RSW_FrilledGorg` had one, so the sheet printed "no canon-library
entry". The library was built from a 45-creature list and never covered the ~200 SWBestiary race
defs ported later (MLIE_FAUNA_ABSORPTION_1). Fixed: `gorg/` (canon `Gorg` + `Gorg/Legends`, 4
images incl. the purple `Gorg-WoSW.png`, brief + Must show written by viewing) and `longtailgorg/`
(no separate article; long-tailed variety per `Gorg/Legends`, 3 film images). `RSW_FrilledGorg`:
no Wookieepedia title ("Frilled newt" is a different animal) — looks invented by the donor mod.

## Per creature
| creature | defName | entry before | images before → after | sources | notes |
|---|---|---|---|---|---|
| frilled gorg | `RSW_FrilledGorg` | — | 0 → 0 | — | no exact Wookieepedia title for: frilled gorg, Frilled Gorg |
| longtail gorg | `RSW_LongtailGorg` | — | 0 → 3 | Legends `Gorg/Legends` + canon `Gorg` (hand-built, shares gorg images) | no exact Wookieepedia title for: longtail gorg, Longtail Gorg |
| gorg | `RSW_Gorg` | — | 0 → 4 | canon `Gorg`; Legends `Gorg/Legends` | filled |
