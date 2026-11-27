// RIMMANDRAKE_FIX_STEEL_BRIDGE_UNSET_STYLE_TAKES_LAST_CHOSEN: a bridge built with no style chosen takes the default look,
// never the last look picked on another button or in an earlier game (_Shared/StylePicker/StylePickMemory.cs, read through
// the same resolve PipeLook.Core hands the designator: Machinery.PipeStyles.Resolve).

using System;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.Shared.StylePicker;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class StylePickMemoryChecks
	{
		private static void Assert(bool ok, string what)
		{
			if (!ok)
			{
				throw new Exception(what);
			}
		}

		private sealed class Button { }
		private sealed class Def { }
		private sealed class Game { }

		/// <summary>The look the button hands the designator: StylePickerCore.Resolve's call, unstyled-copy case.</summary>
		private static string Built(StylePickMemory m, object button, object game) =>
			PipeStyles.Resolve(m.ForButton(button, game), PipeStyles.Scrapper, false, null);

		public static void Run(Action<string, Action> Case)
		{
			Case("StylePick_unset_button_takes_default_not_last_pick", () =>
			{
				var m = new StylePickMemory();
				var steel = new Def();
				var game = new Game();
				var picked = new Button();     // a proof (or the player) picks Futuristic on one steel bridge button
				var fresh = new Button();      // a second steel bridge designator, nothing chosen on it
				m.Remember(picked, steel, "Futuristic", game);
				Assert(Built(m, picked, game) == "Futuristic", "can-fail: the button that picked builds in its pick");
				Assert(Built(m, fresh, game) == PipeStyles.Scrapper,
					"can-fail: a bridge built with no style chosen takes the default look, not the last pick (" + Built(m, fresh, game) + ")");
				Assert(m.LastForDef(steel, game) == "Futuristic", "the probe readout still names the def's last pick");
			});
			Case("StylePick_pick_before_load_does_not_reach_the_loaded_game", () =>
			{
				var m = new StylePickMemory();
				var steel = new Def();
				var button = new Button();     // the Architect button lives for the whole process
				var before = new Game();
				var loaded = new Game();       // a load (or a new colony) makes a new Game object
				m.Remember(button, steel, "Futuristic", before);
				Assert(Built(m, button, loaded) == PipeStyles.Scrapper,
					"can-fail: a pick made before the save was loaded is gone after the load (" + Built(m, button, loaded) + ")");
				Assert(m.LastForDef(steel, loaded) == null, "can-fail: the readout shows no pick in the loaded game");
				m.Remember(button, steel, "Modern", loaded);
				Assert(Built(m, button, loaded) == "Modern", "can-fail: a pick in the loaded game holds in it");
				Assert(m.ForButton(button, null) == null, "no game (main menu): no pick");
			});
			Case("StylePick_clear_and_null_inputs", () =>
			{
				var m = new StylePickMemory();
				var d = new Def();
				var b = new Button();
				var g = new Game();
				m.Remember(b, d, "Industrial", g);
				m.Clear();
				Assert(m.ForButton(b, g) == null && m.LastForDef(d, g) == null, "can-fail: Clear forgets every pick");
				m.Remember(null, d, "Industrial", g);
				m.Remember(b, d, null, g);
				m.Remember(b, d, "Industrial", null);
				Assert(m.ForButton(b, g) == null && m.LastForDef(d, g) == null, "a null button, look or game remembers nothing");
				Assert(m.ForButton(null, g) == null && m.LastForDef(null, g) == null, "a null key reads no pick");
				m.Remember(b, null, "Industrial", g);
				Assert(m.ForButton(b, g) == "Industrial", "a pick with no def is still the button's");
			});
		}
	}
}
