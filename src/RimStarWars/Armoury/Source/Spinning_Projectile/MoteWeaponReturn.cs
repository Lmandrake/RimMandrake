using UnityEngine;
using Verse;

namespace Spinning_Projectile;

[StaticConstructorOnStartup]
public class MoteWeaponReturn : MoteThrown
{
    private Pawn launcher;

    private Pawn originalLauncher;

    private Graphic originalWeaponGraphic;

    public int ticksPerFrame = 8;

    public override Graphic Graphic => originalWeaponGraphic ?? base.Graphic;

    public void SetLauncher(Pawn pawn, Graphic weaponGraphic)
    {
        launcher = pawn;
        if (launcher == null)
        {
            return;
        }
        ThingWithComps primary = pawn.equipment?.Primary;
        if (launcher.equipment?.Primary != null && primary?.Graphic != null)
        {
            originalLauncher = launcher;
            originalWeaponGraphic = primary.Graphic;
            instanceColor = primary.Graphic.color;
        }
    }

    protected override void TimeInterval(float deltaTime)
    {
        // originalLauncher.Destroyed is false for a killed-but-not-yet-corpse-
        // destroyed pawn (Pawn.Kill despawns into a Corpse; Destroyed stays
        // false), so a thrower who dies or is downed mid-flight reaches the
        // block below with equipment already dropped - equipment.Primary is
        // null, not equipment itself. airTimeLeft (MoteThrown) defaults to
        // essentially forever, so without an explicit Destroy() here an
        // abandoned mote used to sit inert on the map indefinitely. Note this
        // branch cannot reach the original weapon's ThingComp_ReturningWeapon
        // (only a Pawn ref and a copied Graphic are stored here, not the
        // weapon Thing itself), so IsThrowingWeapon is left stuck true on
        // that weapon - a separate, still-open gap in this feature.
        if (originalLauncher == null || originalLauncher.Destroyed || originalLauncher.equipment?.Primary == null)
        {
            Destroy();
            return;
        }
        if (originalWeaponGraphic == null)
        {
            Log.Warning("originalWeaponGraphic is null in MoteWeaponReturn.TimeInterval");
            Destroy();
            return;
        }
        Vector3 toLauncher = originalLauncher.Position.ToVector3Shifted() - exactPosition;
        Vector3 normalized = toLauncher.normalized;
        float speed = ticksPerFrame * 1.1f;
        // Vector3.AngleFlat() already returns a heading in DEGREES, which is
        // exactly what SetVelocity(float angle, float speed) wants - the old
        // `speed * normalized.AngleFlat()` scaled that heading by ~8.8x,
        // wrapping mod 360 into an unrelated direction almost every tick.
        SetVelocity(normalized.AngleFlat(), speed);
        // base.TimeInterval (MoteThrown) is what actually advances
        // exactPosition, using the velocity just set above via
        // NextExactPosition(). It must run AFTER SetVelocity, and the old
        // manual `exactPosition += velocity * deltaTime` that used to follow
        // it here must NOT also run - the previous order called base first
        // (advancing exactPosition with LAST tick's velocity) and then added
        // `velocity * deltaTime` again with THIS tick's velocity, integrating
        // position twice per tick and moving the mote at roughly double the
        // intended `speed` from the second tick onward.
        base.TimeInterval(deltaTime);
        if (CheckCollisionWithLauncher())
        {
            Destroy();
            ThingComp_ReturningWeapon comp = originalLauncher.equipment.Primary.TryGetComp<ThingComp_ReturningWeapon>();
            if (comp != null)
            {
                comp.IsThrowingWeapon = false;
            }
        }
    }

    private bool CheckCollisionWithLauncher()
    {
        if (originalLauncher == null)
        {
            return false;
        }
        Vector2 drawSize = originalWeaponGraphic.drawSize;
        Rect moteRect = new Rect(exactPosition.x, exactPosition.z, drawSize.x, drawSize.y);
        Rect launcherRect = new Rect(originalLauncher.Position.x, originalLauncher.Position.z, originalLauncher.def.size.x, originalLauncher.def.size.z);
        return moteRect.Overlaps(launcherRect);
    }
}
