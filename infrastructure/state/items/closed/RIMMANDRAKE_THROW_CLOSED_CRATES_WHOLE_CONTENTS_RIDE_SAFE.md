# RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE

## spec

Owner, 2026-11-12, on Station 5 (`EK_SITTING_STATION5_CONTAINER_SURVIVES_20261112`): "Shelf did survive, but I was
expecting the container to be moved while surviving. I had envisioned that if they put things in a steel crate or chest,
the whole crate/chest would go flying a bit, but their contents would remain inside and protected due to its enclosed
nature." So a blast-hit closed container is THROWN as one unit (the kernel's item throw at its whole mass, so shorter
than loose goods), its contents ride inside it, and goods inside a closed container take no blast damage.

## which things count as closed (delegated call, 2026-11-12)

Census before building (src/, both mod roots): vanilla 1.6 builds no closed storage; its sealed crates (Building_Crate:
ancient, hermetic, security crates) hold contents in a ThingOwner. Ours: Cold Storage's stasis lockers (a sealed steel
box) and evaporative crock (a lidded pot). Closed = our tag `RM_KnockbackClosedStorage`
(`Patches/RM_Knockback_ClosedContainers.xml` puts it on the lockers and the crock, FindMod "RimMandrake: Cold Storage"),
storage that hides its contents (LWM Deep Storage, `showContents` false), or a 1x1 Building_Crate with the setting
"Sealed crates count as closed containers" on. Open shelves never. Settings: "Blasts throw closed containers whole"
(`shoveClosedContainers`, on) and a mass limit (`closedContainerMassLimit`, 250 kg with contents).

## proof

Scene `container_thrown` (rows thrown, together, shorter, shielded; planted breaks: shoveClosedContainers off,
Plant nocontentsshield=on) and the owner look matrix `container` (kinds x shells 1|3 x distance 1|2|3).
