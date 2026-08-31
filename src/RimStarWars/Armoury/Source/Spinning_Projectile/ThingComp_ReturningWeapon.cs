using Verse;

namespace Spinning_Projectile;

[StaticConstructorOnStartup]
internal class ThingComp_ReturningWeapon : ThingComp
{
    private bool returning;

    public ThingCompProperties_ReturningWeapon Props => (ThingCompProperties_ReturningWeapon)props;

    public bool IsThrowingWeapon
    {
        get => returning;
        set => returning = value;
    }

    public override void PostExposeData()
    {
        base.PostExposeData();
        Scribe_Values.Look(ref returning, "returning", false);
    }
}
