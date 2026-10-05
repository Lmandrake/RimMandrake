# MessyConduit style checks: terrain independence (2026-10-04)
- Cause: validation_style.py / validation_style_hose.py cleared things + Soil + fog on their sites but never removed ROOF (sites lie outside human_review REGION), so masts/reels hit random roof/rock.
- Fix: `validation_style.prepare_site(B, rect, rows, rid)` = destroy All, Soil, unfog, roof None, then read back get_roof_batch + list_things; any roof, refused verb or rock/plant/ruin left records UNMEASURED (class SITE) and aborts, never a mod FAIL.
- Used for SITE and SITE2 (validation_style) and SITE (validation_style_hose); hose reel lay targets lie inside SITE.
- Offline: both --offline PASS; helper unit-checked with a fake bridge. Live rerun pending (main window).
- Unproven: list_things without defName semantics; hence the leftover check is limited to terrain-type defNames.
