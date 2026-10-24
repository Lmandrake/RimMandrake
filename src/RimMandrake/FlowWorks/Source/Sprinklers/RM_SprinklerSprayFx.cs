// SPRINKLER_SPRAY_REDRAW_REAL_THROW (owner 2026-10-23: "animated water leaving sprinkler is pretty dorky: just a blue burst
// ring around it, should be much more realistic and portray the actual water throw affected (radius)").
using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Sprinklers
{
	/// <summary>
	/// Draws a spraying head's water as a rotor jet: every <see cref="RM_SprayPlan.StepTicks"/> ticks the jet's droplets
	/// (vanilla fleck machinery, FleckSystemThrown) leave the nozzle, arc and land in the cells the head's last pulse wetted
	/// (<see cref="CompRM_SprinklerBase.SprayPlan"/>), and a vanilla GroundWaterSplash marks the landing. Walls stop the
	/// spray because the plan is made from the watered cells, which already exclude what the spray cannot reach.
	///
	/// A droplet is a FleckThrown with a constant ground velocity carrying it from nozzle to landing point in exactly its
	/// band's flight time, the band FleckDef's archDuration giving the same time for the arc, and a life half a tick short of
	/// it (RM_SprayPlan.SolidSeconds) so it vanishes where it lands.
	///
	/// Cost is bounded: nothing when sprinklerSprayEffects is off or the map is not the one shown; only heads whose throw
	/// is inside the camera view; at most <see cref="MaxFlecksPerTick"/> droplets a tick map-wide. Visual only: it never
	/// changes what is watered.
	/// </summary>
	public static class RM_SprinklerSprayFx
	{
		public const int MaxFlecksPerTick = 48;

		/// <summary>How far above the riser saddle (drawOffset) the nozzle sits, cells.</summary>
		public const float NozzleRise = 0.2f;

		private struct Splash
		{
			public int tick;
			public Map map;
			public Vector3 pos;
			public Color? color;
		}

		private static readonly List<Splash> pending = new List<Splash>();
		private static FleckDef[] bandDefs;
		private static FleckDef splashDef;
		private static bool resolved;

		private static void Resolve()
		{
			resolved = true;
			bandDefs = new FleckDef[RM_SprayPlan.BandTicks.Length];
			for (int b = 0; b < bandDefs.Length; b++) bandDefs[b] = DefDatabase<FleckDef>.GetNamedSilentFail(RM_SprayPlan.BandDefName(b));
			splashDef = DefDatabase<FleckDef>.GetNamedSilentFail("GroundWaterSplash");
		}

		/// <summary>Called by RM_MapComponent_Sprinklers every tick of <paramref name="map"/>.</summary>
		public static void Tick(Map map, IReadOnlyList<CompRM_SprinklerBase> heads, int now)
		{
			try
			{
				bool shown = RM_SprinklerSettings.sprinklerSprayEffects && map == Find.CurrentMap;
				FlushSplashes(map, now, shown);
				if (!shown || heads.Count == 0 || Find.CameraDriver == null) return;
				if (!resolved) Resolve();
				CellRect view = Find.CameraDriver.CurrentViewRect;
				int budget = MaxFlecksPerTick;
				for (int i = 0; i < heads.Count && budget > 0; i++)
				{
					CompRM_SprinklerBase h = heads[i];
					ThingWithComps head = h?.parent;
					if (head == null || !head.Spawned || head.Map != map || !h.DrawsSpray) continue;
					int step = RM_SprayPlan.StepAt(now, head.thingIDNumber);
					if (step < 0) continue;
					int reach = Mathf.CeilToInt(h.CoverRadius) + 1;
					if (!view.ExpandedBy(reach).Contains(head.Position)) continue;
					List<RM_SprayDrop>[] plan = h.SprayPlan();
					if (plan == null) continue;
					budget -= Throw(h, head, map, plan[step], now, budget);
				}
			}
			catch (System.Exception e)
			{
				Log.ErrorOnce("[FlowWorks] sprinkler spray effect failed: " + e, 0x5B71A2);
			}
		}

		/// <summary>One rotor step's droplets from <paramref name="head"/>; returns how many were thrown.</summary>
		private static int Throw(CompRM_SprinklerBase h, ThingWithComps head, Map map, List<RM_SprayDrop> drops, int now, int budget)
		{
			if (drops.Count == 0 || !head.Position.ShouldSpawnMotesAt(map)) return 0;
			Vector3 centre = head.Position.ToVector3Shifted();
			Graphic g = head.Graphic;
			Vector3 nozzle = (g != null ? g.DrawOffset(head.Rotation) : Vector3.zero) + RM_PipeSeat.Offset(head) + new Vector3(0f, 0f, NozzleRise);
			Color drop = DropColor(h.lastLiquid);
			Color? splash = SplashColor(h.lastLiquid);
			int thrown = 0;
			for (int k = 0; k < drops.Count && thrown < budget; k++)
			{
				RM_SprayDrop d = drops[k];
				FleckDef def = bandDefs[d.band];
				if (def == null) continue;
				int ticks = RM_SprayPlan.BandTicks[d.band];
				RM_SprayPlan.Velocity(nozzle.x, nozzle.z, d.landX, d.landZ, ticks, out float vx, out float vz);
				FleckCreationData data = FleckMaker.GetDataStatic(centre + new Vector3(nozzle.x, 0f, nozzle.z), map, def, Rand.Range(0.85f, 1.1f));
				data.velocity = new Vector3(vx, 0f, vz);
				data.airTimeLeft = (ticks + 2) / 60f;
				data.solidTimeOverride = RM_SprayPlan.SolidSeconds(ticks, def.fadeInTime, def.fadeOutTime);
				data.instanceColor = drop;
				data.rotation = Rand.Range(0f, 360f);
				map.flecks.CreateFleck(data);
				thrown++;
				// every other landing splashes: over a turn every cell still gets its splashes
				if (splashDef != null && ((d.cell + now / RM_SprayPlan.StepTicks) & 1) == 0)
				{
					pending.Add(new Splash { tick = now + ticks, map = map, pos = centre + new Vector3(d.landX, 0f, d.landZ), color = splash });
				}
			}
			return thrown;
		}

		/// <summary>The splashes whose droplet lands this tick; stale or off-screen ones are dropped, never drawn late.</summary>
		private static void FlushSplashes(Map map, int now, bool shown)
		{
			for (int i = pending.Count - 1; i >= 0; i--)
			{
				Splash s = pending[i];
				bool mine = s.map == map;
				if (mine && s.tick > now) continue;
				// another map's: its own tick flushes it; dropped when stale, or when far ahead (a new game's clock restarted)
				if (!mine && s.tick >= now - 60 && s.tick <= now + 60) continue;
				pending.RemoveAt(i);
				if (!mine || !shown || s.tick != now || splashDef == null) continue;
				FleckCreationData data = FleckMaker.GetDataStatic(s.pos, map, splashDef, Rand.Range(0.3f, 0.4f));
				data.instanceColor = s.color;
				data.rotation = Rand.Range(0f, 360f);
				map.flecks.CreateFleck(data);
			}
		}

		/// <summary>The droplet tint: the liquid's colour lifted a quarter toward white (spray reads lighter than a pool).</summary>
		public static Color DropColor(LiquidDef liquid)
		{
			Color c = liquid != null ? liquid.color : new Color(0.62f, 0.8f, 0.98f);
			c = Color.Lerp(c, Color.white, 0.25f);
			c.a = 0.85f;
			return c;
		}

		/// <summary>The splash tint: none (GroundWaterSplash's own colour) for a pale liquid, else the liquid's colour.</summary>
		public static Color? SplashColor(LiquidDef liquid)
		{
			if (liquid == null) return null;
			Color c = liquid.color;
			if (c.b >= c.r && c.b >= c.g) return null;
			return new Color(c.r, c.g, c.b, 1f);
		}
	}
}
