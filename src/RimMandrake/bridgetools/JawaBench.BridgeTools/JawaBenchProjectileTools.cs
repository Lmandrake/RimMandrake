// JawaBenchProjectileTools.cs - read a projectile's damage, including the PRIVATE base fields.
//
// ARMOURY_PROJECTILE_DAMAGE_TOOL_1 (child of NORTHSTAR_PARTIAL_GAPS_FILL_1, Armoury row).
//
// WHY A TOOL (MEASURED from 1.6 source via RimSage, 2026-10-03):
//   Verse.ProjectileProperties declares `private int damageAmountBase = -1;` and
//   `private float armorPenetrationBase = -1f;`. jawa/get_defs reflects PUBLIC fields only, so the
//   Armoury ranged ladder (Patches/Armoury_RangedDamage.xml replaces projectile/damageAmountBase) had
//   no instrument that could see whether a patched value landed. The public accessors
//   GetDamageAmount(ThingDef, ThingDef) and GetArmorPenetration(Thing) answer the EFFECTIVE value
//   (base when set, else the damageDef default), which cannot tell "patched to 12" from "unset and the
//   default happens to be 12". So both are returned: raw private field AND effective value.
//
// SHAPE: get_defs-compatible top level (success, foundCount, notFound) so a shipped_defs-style caller
// reads the same three fields. A def that exists but is not a projectile is found:true,
// isProjectile:false - DATA, never a throw. Read-only, no map, safe at the main menu.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private static readonly FieldInfo ProjDamageAmountBaseField =
            typeof(ProjectileProperties).GetField("damageAmountBase", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);

        private static readonly FieldInfo ProjArmorPenetrationBaseField =
            typeof(ProjectileProperties).GetField("armorPenetrationBase", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);

        [Tool(
            "jawa/projectile_damage",
            Description =
                "Read projectile damage off ThingDefs, INCLUDING the private ProjectileProperties." +
                "damageAmountBase / armorPenetrationBase that jawa/get_defs cannot see (it reflects " +
                "public fields only). Returns the raw field (-1 = unset) AND the effective value " +
                "from the public accessor (unset reads as the damageDef default), so a patched base " +
                "can be told apart from a default that happens to match. includeWeapons=true also " +
                "accepts a weapon ThingDef and follows Verbs[0].defaultProjectile. Read-only, no map.",
            ResultDescription =
                "success, foundCount, notFound (as get_defs); rows[]: requested, defName, found, " +
                "isProjectile, viaWeapon, damageDef, damageAmountBase, damageAmount, " +
                "armorPenetrationBase, armorPenetration. A def that is not a projectile is " +
                "found:true isProjectile:false, never an error.")]
        public static async Task<object> ProjectileDamage(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "ONE semicolon-separated STRING of ThingDef names, e.g. 'Bullet_Revolver;Bullet_IncendiaryLauncher'. " +
                "Never a list.")]
            string defs,
            [ToolParameter(Description = "Also accept weapon ThingDefs and follow Verbs[0].defaultProjectile.",
                DefaultValue = false)]
            bool includeWeapons = false,
            [ToolParameter(Description = "Cap on how many defs to resolve.", DefaultValue = 500)]
            int limit = 500)
        {
            if (string.IsNullOrWhiteSpace(defs))
                return Fail("defs is required: ThingDef names separated by ';'.",
                    new { example = "Bullet_Revolver;Bullet_IncendiaryLauncher" });
            if (ProjDamageAmountBaseField == null || ProjArmorPenetrationBaseField == null)
                return Fail("ProjectileProperties no longer declares damageAmountBase/armorPenetrationBase - " +
                    "the engine changed; this tool cannot measure and says so rather than guessing.",
                    new { damageAmountBase = ProjDamageAmountBaseField != null,
                          armorPenetrationBase = ProjArmorPenetrationBaseField != null });

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var rows = new List<object>();
                var notFound = new List<string>();
                var found = 0;
                foreach (var name in defs.Split(';').Select(q => q.Trim()).Where(q => q.Length > 0).Take(limit))
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                    if (def == null)
                    {
                        notFound.Add(name);
                        rows.Add(new { requested = name, defName = name, found = false });
                        continue;
                    }
                    found++;
                    string viaWeapon = null;
                    ThingDef proj = def;
                    if (def.projectile == null && includeWeapons)
                    {
                        ThingDef followed = def.Verbs?.FirstOrDefault()?.defaultProjectile;
                        if (followed != null)
                        {
                            viaWeapon = def.defName;
                            proj = followed;
                        }
                    }
                    ProjectileProperties pp = proj.projectile;
                    if (pp == null)
                    {
                        rows.Add(new { requested = name, defName = def.defName, found = true, isProjectile = false,
                                       viaWeapon });
                        continue;
                    }
                    int rawDamage = (int)ProjDamageAmountBaseField.GetValue(pp);
                    float rawPen = (float)ProjArmorPenetrationBaseField.GetValue(pp);
                    int? effDamage = null;
                    float? effPen = null;
                    string effError = null;
                    try
                    {
                        effDamage = pp.GetDamageAmount((ThingDef)null, null);
                        effPen = pp.GetArmorPenetration(null);
                    }
                    catch (Exception e)
                    {
                        // a projectile with no damageDef NREs the accessor; the raw fields still answer
                        effError = e.GetType().Name + ": " + e.Message;
                    }
                    rows.Add(new
                    {
                        requested = name,
                        defName = proj.defName,
                        found = true,
                        isProjectile = true,
                        viaWeapon,
                        damageDef = pp.damageDef?.defName,
                        damageAmountBase = rawDamage,
                        damageAmount = effDamage,
                        armorPenetrationBase = rawPen,
                        armorPenetration = effPen,
                        effectiveError = effError
                    });
                }
                return new
                {
                    success = true,
                    message = $"{found} found, {notFound.Count} not found.",
                    foundCount = found,
                    notFound,
                    rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
