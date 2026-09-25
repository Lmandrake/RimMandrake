using RimWorld;
using Verse;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1 — the husbandry loop's job vocabulary (spec §3):
	/// NET (wild breeder to a carried "wet skin" item), STOCK (carry that
	/// item into a pen, release), FEED (carry food to a pen, deliver),
	/// HARVEST (wave 4: sustainable per-species catch), CULL (wave 4: the
	/// vhorrin set-piece). Same [DefOf] shape as
	/// <c>RimMandrake.AnimalTheft.AnimalTheftDefOf</c>.
	/// </summary>
	[DefOf]
	public static class RM_PoolStockDefOf
	{
		public static JobDef RM_NetPoolBreeder;
		public static JobDef RM_StockPoolPen;
		public static JobDef RM_FeedPoolPen;
		public static JobDef RM_HarvestPoolPen;
		public static JobDef RM_CullVhorrin;

		static RM_PoolStockDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(RM_PoolStockDefOf));
	}
}
