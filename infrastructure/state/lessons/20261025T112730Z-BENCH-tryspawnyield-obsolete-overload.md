RimWorld 1.6 Mineable.TrySpawnYield has two overloads: (Map, bool, Pawn) and an [Obsolete] (Map, float, bool, Pawn). A name-only [HarmonyPatch(typeof(Mineable), "TrySpawnYield")] is ambiguous; pass new[]{typeof(Map), typeof(bool), typeof(Pawn)}. Verified by reflection on Assembly-CSharp.dll.
home: rimworld-modding
