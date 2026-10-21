# FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES

Owner 2026-10-20: "This is the same problem the fliers have. Their bodies should be kept static while the wings flap. So looking for extreme of the graphic image is not useful and couples wing motion to body motion incorrectly."

Audit every tool that aligns, crops, centres or scales flier flip-book frames (flyingAnimationFramePathPrefix sets; skills/rimworld-modding/references/flight.md; art pipeline normalisers; fit/validate scripts) for alpha-bounding-box registration. Frames must register on the rigid body so it stays static across frames while wings move. Offline audit only; NEVER live-test flight without the owner present (CLAUDE.md).

NEXT: list the flight-frame tools and the shipped flier frame sets, measure body-anchor jitter across frames per set, report offenders with a fix plan; no repaint until reviewed.

## Audit result 2026-10-20 (FOUNDRY, offline)

37 flip-book sets, 22 animated, 18 OFFENDERS (body drifts >= 2 px and >= 2% of body size); worst Sketto south 104 px, PekoPeko f east 133 px, FireHawk north 84 px. Cause is mostly redrawn bodies per frame, not sub-pixel registration. No install-path tool bbox-registers flip-book frames; `facing_regen`/`facing_scale_lint`/`facing_set_audit` would if fed one. Report with table and fix plan: `design/RimMandrake/flier_frame_registration_audit_2026-10-20.md`; tool `src/RimMandrake/Utils/art/flier_frame_registration.py`. NEXT: owner reviews the offender list; then per creature rebuild with `flyer_lock` plate recipe. No frame was modified.

## Owner acceptance test, 2026-10-20 10:05 PM PDT (card answer, his words)

"I have a simple test for you that you can do yourself. Draw a line through the eyes of each of these pictures, and then another line between their shoulders. Those lines should be level, not moving up and down with wing flaps."

NEXT: add an eye-line and a shoulder-line check to src/RimMandrake/Utils/art/flier_body_stabilize.py (eye and shoulder/wing-root points per frame from the body-part detector, draw both lines on every frame, report vertical offset and angle change in px/deg), run it on the six rebuilt sets (Sketto, PekoPeko female, FireHawk, Uvak, Hawkbat, Hawkbat juvenile) and show him the line overlays before any further set is rebuilt. Held sets stay held until he has seen it.
