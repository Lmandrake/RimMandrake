using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace Spinning_Projectile;

// 🔴 KNOWN GAP (same incomplete feature documented in HarmonyPatches.cs): no
// ThingDef named "Mote_LightSaberReturn" exists anywhere in this mod's XML
// (verified across the whole src tree). Impact() below is unreachable today
// (nothing sets thingClass to SpinningWeaponProjectile, so no Verb ever fires
// one - same check), but if that Verb is ever wired up, ThingDef.Named() will
// log an error and return null, and the very next line (mote.exactPosition =
// ...) will NullReferenceException on every throw. Not fixed here: it needs a
// new mote ThingDef (graphic/sound/mote category), which is content
// authoring, not a code-review fix.
[StaticConstructorOnStartup]
public class SpinningWeaponProjectile : Projectile
{
    public float spinRate { get; set; }

    protected override void DrawAt(Vector3 drawLoc, bool flip = false)
    {
        Quaternion rotation = ExactRotation;
        Graphic graphic = def.graphic;
        if (launcher is Pawn pawn && pawn.equipment?.Primary != null)
        {
            graphic = pawn.equipment.Primary.Graphic;
        }
        float spin = def.projectile.spinRate;
        float angleRate = 100f * spin;
        float angle = Time.time * angleRate;
        rotation *= Quaternion.Euler(0f, angle, 0f);
        if (def.projectile.useGraphicClass)
        {
            Graphic.Draw(drawLoc, Rotation, this, rotation.eulerAngles.y);
        }
        else
        {
            Graphics.DrawMesh(MeshPool.GridPlane(graphic.drawSize), drawLoc, rotation, graphic.MatSingle, 0);
        }
    }

    protected override void Impact(Thing hitThing, bool blockedByShield = false)
    {
        Map map = Map;
        base.Impact(hitThing, blockedByShield);
        if (hitThing != null)
        {
            hitThing.TakeDamage(new DamageInfo(def.projectile.damageDef, def.projectile.GetDamageAmount(hitThing, (StringBuilder)null), 0f, -1f, launcher));
        }
        if (launcher is Pawn pawn && pawn.equipment?.Primary != null)
        {
            IntVec3 position = hitThing != null ? hitThing.Position : Position;
            MoteWeaponReturn mote = (MoteWeaponReturn)ThingMaker.MakeThing(ThingDef.Named("Mote_LightSaberReturn"));
            mote.exactPosition = position.ToVector3Shifted();
            mote.rotationRate = 0f;
            mote.SetLauncher(pawn, pawn.equipment.Primary.Graphic);
            GenSpawn.Spawn(mote, position, map);
        }
    }
}
