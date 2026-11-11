// SPRINKLER_HEADS_BUILD_PUMP_REQUIRED (design/RimMandrake/sprinklers_design_2026-10-16.md §6 step 2, §8.1): the `sprinkler:x,z`
// probe verb's answer -- head state, litres last pulse, cells, a wetUntil sample -- so a live run reads the head from
// FlowWorks' own state instead of parsing its inspect line. Verse-free: Hose/HoseNetProbe.cs fills a row from the live head and
// the map's sprinkled grid; SelfTest/SprinklerChecks.cs formats rows offline.
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace RimMandrake.FlowWorks.Sprinklers
{
    /// <summary>One sprinkled-grid cell as the probe reports it.</summary>
    public struct RM_SprinkledSample
    {
        public int x, z, wetUntil, owner;
        public string liquid;
    }

    /// <summary>A head's probe row. Fill the fields, then <see cref="ToJson"/>.</summary>
    public sealed class RM_SprinklerProbeRow
    {
        /// <summary>At most this many cells go in "sample" (the row stays small on a VFE head's ~105 cells).</summary>
        public const int MaxSample = 8;

        public string cmd, def, state, status, liquid;
        public int id, x, z, now, nextPulseTick;
        public bool featureEnabled, switchOn, pumpOnNet;
        public float radius;
        public int lastUnits, lastCells, lastNeed, lastAvailable, totalUnits;
        /// <summary>The cells the last paid pulse sprayed (-1 = not known: no paid pulse since load).</summary>
        public int sprayCells = -1;
        /// <summary>Of <see cref="sprayCells"/>, how many are wet now and were paid by THIS head.</summary>
        public int wetOwnCells;
        /// <summary>Map-wide: live sprinkled cells now, and the session counters RM_MapComponent_Sprinklers keeps.</summary>
        public int liveCellsMap, pulses, sprayedUnits;
        public readonly List<RM_SprinkledSample> sample = new List<RM_SprinkledSample>();

        public void AddSample(RM_SprinkledSample s)
        {
            if (sample.Count < MaxSample) sample.Add(s);
        }

        public string ToJson()
        {
            var sb = new StringBuilder(512);
            sb.Append("{\"success\":true,\"cmd\":").Append(Str(cmd))
              .Append(",\"id\":").Append(I(id))
              .Append(",\"def\":").Append(Str(def))
              .Append(",\"cell\":[").Append(I(x)).Append(',').Append(I(z)).Append(']')
              .Append(",\"state\":").Append(Str(state))
              .Append(",\"status\":").Append(Str(status))
              .Append(",\"featureEnabled\":").Append(Bool(featureEnabled))
              .Append(",\"switchOn\":").Append(Bool(switchOn))
              .Append(",\"pumpOnNet\":").Append(Bool(pumpOnNet))
              .Append(",\"radius\":").Append(Num(radius))
              .Append(",\"liquid\":").Append(Str(liquid))
              .Append(",\"lastUnits\":").Append(I(lastUnits))
              .Append(",\"lastLitres\":").Append(Num(RM_Volume.Litres(lastUnits)))
              .Append(",\"lastCells\":").Append(I(lastCells))
              .Append(",\"lastNeed\":").Append(I(lastNeed))
              .Append(",\"lastAvailable\":").Append(I(lastAvailable))
              .Append(",\"totalUnits\":").Append(I(totalUnits))
              .Append(",\"nextPulseTick\":").Append(I(nextPulseTick))
              .Append(",\"sprayCells\":").Append(I(sprayCells))
              .Append(",\"wetOwnCells\":").Append(I(wetOwnCells))
              .Append(",\"sample\":[");
            for (int i = 0; i < sample.Count; i++)
            {
                RM_SprinkledSample s = sample[i];
                if (i > 0) sb.Append(',');
                sb.Append("{\"cell\":[").Append(I(s.x)).Append(',').Append(I(s.z)).Append("],\"wetUntil\":").Append(I(s.wetUntil))
                  .Append(",\"wet\":").Append(Bool(RM_SprinklerKernel.IsWet(s.wetUntil, now)))
                  .Append(",\"owner\":").Append(I(s.owner))
                  .Append(",\"liquid\":").Append(Str(s.liquid)).Append('}');
            }
            sb.Append("],\"liveCellsMap\":").Append(I(liveCellsMap))
              .Append(",\"pulses\":").Append(I(pulses))
              .Append(",\"sprayedUnits\":").Append(I(sprayedUnits))
              .Append(",\"tick\":").Append(I(now)).Append('}');
            return sb.ToString();
        }

        private static string Bool(bool b) => b ? "true" : "false";

        /// <summary>StringBuilder.Append(int) uses the current culture's NegativeSign; JSON needs ASCII "-" (-1 sentinels).</summary>
        private static string I(int i) => i.ToString(CultureInfo.InvariantCulture);

        private static string Num(float f) => f.ToString("0.###", CultureInfo.InvariantCulture);

        /// <summary>A JSON string literal (null -> null): quotes, backslashes and control characters escaped.</summary>
        public static string Str(string s)
        {
            if (s == null) return "null";
            var sb = new StringBuilder(s.Length + 2).Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < ' ') sb.Append("\\u").Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                        else sb.Append(c);
                        break;
                }
            }
            return sb.Append('"').ToString();
        }
    }
}
