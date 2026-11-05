// SPIKES_PARITY_FIX_FLOAT32_MIRROR: runs the production RM_SpikeDrawMath (FloorRect, SubmergedAlpha, Layout) over the
// cases gen_golden.py writes and prints every output as float32 bits, so the Python mirror (fw_scenes_spikes.py) can be
// held to the C# bit for bit offline (selftest_spike_float32_parity.py reads the result, spike_parity_golden.json).
// Built and run by gen_golden.py with dotnet.exe; dev tooling, never shipped.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using RimMandrake.FlowWorks;

public static class Harness
{
	static float F(string hex) => BitConverter.Int32BitsToSingle(unchecked((int)uint.Parse(hex, NumberStyles.HexNumber)));
	static string H(float f) => unchecked((uint)BitConverter.SingleToInt32Bits(f)).ToString("x8");

	public static int Main(string[] args)
	{
		var sb = new StringBuilder();
		var quads = new List<float>();
		foreach (string line in File.ReadAllLines(args[0]))
		{
			string[] p = line.Split(' ');
			if (p[0] == "F")
			{
				RM_SpikeDrawMath.FloorRect(int.Parse(p[1]), int.Parse(p[2]), int.Parse(p[3]), int.Parse(p[4]), int.Parse(p[5]),
					p[6] == "1", p[7] == "1", out float x0, out float z0, out float x1, out float z1);
				sb.Append(H(x0)).Append(' ').Append(H(z0)).Append(' ').Append(H(x1)).Append(' ').Append(H(z1));
			}
			else if (p[0] == "A")
				sb.Append(H(RM_SpikeDrawMath.SubmergedAlpha(int.Parse(p[1]))));
			else if (p[0] == "L")
			{
				int k = RM_SpikeDrawMath.Layout(int.Parse(p[1]), int.Parse(p[2]), F(p[3]), F(p[4]), F(p[5]), F(p[6]), quads);
				sb.Append(k);
				foreach (float q in quads) sb.Append(' ').Append(H(q));
			}
			else
				throw new Exception("bad case line: " + line);
			sb.Append('\n');
		}
		File.WriteAllText(args[1], sb.ToString());
		return 0;
	}
}
