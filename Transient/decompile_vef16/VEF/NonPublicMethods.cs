using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF;

[StaticConstructorOnStartup]
public static class NonPublicMethods
{
	public delegate void ApplyArmourDelegate<A, B, C, D, E, F, G>(ref A first, B second, C third, D fourth, ref E fifth, F sixth, out G seventh);

	public delegate C FuncOut<A, B, C>(A first, out B second);

	[StaticConstructorOnStartup]
	public static class DualWield
	{
		public static Action<Pawn_EquipmentTracker, ThingWithComps> Ext_Pawn_EquipmentTracker_MakeRoomForOffHand;

		public static FuncOut<Pawn_EquipmentTracker, ThingWithComps, bool> Ext_Pawn_EquipmentTracker_TryGetOffHandEquipment;

		public static Func<ThingDef, bool> Ext_ThingDef_CanBeOffHand;

		public static Func<ThingDef, bool> Ext_ThingDef_IsTwoHand;

		static DualWield()
		{
			if (ModCompatibilityCheck.DualWield)
			{
				Type typeInAnyAssembly = GenTypes.GetTypeInAnyAssembly("DualWield.Ext_Pawn_EquipmentTracker", "DualWield");
				Ext_Pawn_EquipmentTracker_MakeRoomForOffHand = (Action<Pawn_EquipmentTracker, ThingWithComps>)Delegate.CreateDelegate(typeof(Action<Pawn_EquipmentTracker, ThingWithComps>), AccessTools.Method(typeInAnyAssembly, "MakeRoomForOffHand", (Type[])null, (Type[])null));
				Ext_Pawn_EquipmentTracker_TryGetOffHandEquipment = (FuncOut<Pawn_EquipmentTracker, ThingWithComps, bool>)Delegate.CreateDelegate(typeof(FuncOut<Pawn_EquipmentTracker, ThingWithComps, bool>), AccessTools.Method(typeInAnyAssembly, "TryGetOffHandEquipment", (Type[])null, (Type[])null));
				Type typeInAnyAssembly2 = GenTypes.GetTypeInAnyAssembly("DualWield.Ext_ThingDef", "DualWield");
				Ext_ThingDef_CanBeOffHand = (Func<ThingDef, bool>)Delegate.CreateDelegate(typeof(Func<ThingDef, bool>), AccessTools.Method(typeInAnyAssembly2, "CanBeOffHand", (Type[])null, (Type[])null));
				Ext_ThingDef_IsTwoHand = (Func<ThingDef, bool>)Delegate.CreateDelegate(typeof(Func<ThingDef, bool>), AccessTools.Method(typeInAnyAssembly2, "IsTwoHand", (Type[])null, (Type[])null));
			}
		}
	}

	[StaticConstructorOnStartup]
	public static class RimCities
	{
		public static Func<Predicate<Faction>, Faction> GenCity_RandomCityFaction;

		static RimCities()
		{
			if (ModCompatibilityCheck.RimCities)
			{
				Type typeInAnyAssembly = GenTypes.GetTypeInAnyAssembly("Cities.GenCity", "Cities");
				GenCity_RandomCityFaction = (Func<Predicate<Faction>, Faction>)Delegate.CreateDelegate(typeof(Func<Predicate<Faction>, Faction>), AccessTools.Method(typeInAnyAssembly, "RandomCityFaction", (Type[])null, (Type[])null));
			}
		}
	}

	public static ApplyArmourDelegate<float, float, float, Thing, DamageDef, Pawn, bool> ArmorUtility_ApplyArmor = (ApplyArmourDelegate<float, float, float, Thing, DamageDef, Pawn, bool>)Delegate.CreateDelegate(typeof(ApplyArmourDelegate<float, float, float, Thing, DamageDef, Pawn, bool>), AccessTools.Method(typeof(ArmorUtility), "ApplyArmor", (Type[])null, (Type[])null));

	public static Func<IntVec3, Rot4, ThingDef, Map, ThingDef, bool> SiegeBlueprintPlacer_CanPlaceBlueprintAt = (Func<IntVec3, Rot4, ThingDef, Map, ThingDef, bool>)Delegate.CreateDelegate(typeof(Func<IntVec3, Rot4, ThingDef, Map, ThingDef, bool>), AccessTools.Method(typeof(SiegeBlueprintPlacer), "CanPlaceBlueprintAt", (Type[])null, (Type[])null));

	public static Func<ThingDef, Rot4, Map, IntVec3> SiegeBlueprintPlacer_FindArtySpot = (Func<ThingDef, Rot4, Map, IntVec3>)Delegate.CreateDelegate(typeof(Func<ThingDef, Rot4, Map, IntVec3>), AccessTools.Method(typeof(SiegeBlueprintPlacer), "FindArtySpot", (Type[])null, (Type[])null));

	public static Action<Projectile> Projectile_ImpactSomething = (Action<Projectile>)Delegate.CreateDelegate(typeof(Action<Projectile>), null, AccessTools.Method(typeof(Projectile), "ImpactSomething", (Type[])null, (Type[])null));

	public static Action<Pawn, PawnGenerationRequest> GenerateSkills = (Action<Pawn, PawnGenerationRequest>)Delegate.CreateDelegate(typeof(Action<Pawn, PawnGenerationRequest>), null, AccessTools.Method(typeof(PawnGenerator), "GenerateSkills", (Type[])null, (Type[])null));

	public static Action<DeepResourceGrid> RenderMouseAttachments = (Action<DeepResourceGrid>)Delegate.CreateDelegate(typeof(Action<DeepResourceGrid>), AccessToolsExtensions.Method(typeof(DeepResourceGrid), "RenderMouseAttachments", (Type[])null, (Type[])null));

	public static TDel MakeDelegate<TDel>(MethodInfo method) where TDel : Delegate
	{
		return (TDel)Delegate.CreateDelegate(typeof(TDel), method);
	}
}
