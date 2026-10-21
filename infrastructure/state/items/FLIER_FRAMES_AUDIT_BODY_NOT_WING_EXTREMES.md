# FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES

Owner 2026-10-20: "This is the same problem the fliers have. Their bodies should be kept static while the wings flap. So looking for extreme of the graphic image is not useful and couples wing motion to body motion incorrectly."

Audit every tool that aligns, crops, centres or scales flier flip-book frames (flyingAnimationFramePathPrefix sets; skills/rimworld-modding/references/flight.md; art pipeline normalisers; fit/validate scripts) for alpha-bounding-box registration. Frames must register on the rigid body so it stays static across frames while wings move. Offline audit only; NEVER live-test flight without the owner present (CLAUDE.md).

NEXT: list the flight-frame tools and the shipped flier frame sets, measure body-anchor jitter across frames per set, report offenders with a fix plan; no repaint until reviewed.
