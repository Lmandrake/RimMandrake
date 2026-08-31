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
        base.TimeInterval(deltaTime);
        if (originalLauncher == null || originalLauncher.Destroyed)
        {
            return;
        }
        if (originalWeaponGraphic == null)
        {
            Log.Warning("originalWeaponGraphic is null in MoteWeaponReturn.TimeInterval");
            return;
        }
        Vector3 toLauncher = originalLauncher.Position.ToVector3Shifted() - exactPosition;
        Vector3 normalized = toLauncher.normalized;
        float speed = ticksPerFrame * 1.1f;
        float angle = speed * normalized.AngleFlat();
        SetVelocity(angle, speed);
        exactPosition += velocity * deltaTime;
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
