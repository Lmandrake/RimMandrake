using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;

// _Shared/StylePicker: the engine-free memory of menu picks behind StylePickerCore (no Verse, no RimWorld), so the
// FlowWorks SelfTest proves it offline. RIMMANDRAKE_FIX_STEEL_BRIDGE_UNSET_STYLE_TAKES_LAST_CHOSEN (walk map 2026-11-25:
// stations 52, 53, 70, 78 and 84 came out Futuristic): the old memory was one look per ThingDef for the whole process, so a
// pick on one build button reached every other designator of that def, and a pick made in an earlier save reached the
// next one. A pick now belongs to the button that made it AND to the game it was made in; anything else reads no pick,
// and a build with no pick takes the default look.
namespace RimMandrake.Shared.StylePicker
{
    /// <summary>
    /// The last menu pick of each build button, per game. Keys are opaque objects: the button (a Designator_Build), its
    /// def (a ThingDef) and the game (Current.Game). Vanilla builds each Architect button once at startup and keeps it for
    /// the life of the process, so the player's pick on his button stays on that button for the rest of that game. A
    /// designator made in code (a proof, a staging script) is a different button and starts with no pick. A new or loaded
    /// game is a different game object: every pick made before it reads as none. Neither a button nor a game is kept alive
    /// by this memory (weak references only).
    /// </summary>
    internal sealed class StylePickMemory
    {
        private sealed class Entry
        {
            public string Look;
            public WeakReference Game;
        }

        private ConditionalWeakTable<object, Entry> byButton = new ConditionalWeakTable<object, Entry>();
        private readonly Dictionary<object, Entry> byDef = new Dictionary<object, Entry>();

        private static bool SameGame(Entry e, object game) => e != null && game != null && ReferenceEquals(e.Game.Target, game);

        /// <summary>Remember that <paramref name="button"/> (placing <paramref name="def"/>) picked <paramref name="look"/>
        /// in <paramref name="game"/>. A null button, look or game remembers nothing.</summary>
        public void Remember(object button, object def, string look, object game)
        {
            if (button == null || look == null || game == null) return;
            var e = new Entry { Look = look, Game = new WeakReference(game) };
            byButton.Remove(button);
            byButton.Add(button, e);
            if (def != null) byDef[def] = e;
        }

        /// <summary>This button's own pick in this game; null when it picked nothing in this game.</summary>
        public string ForButton(object button, object game)
        {
            if (button == null || !byButton.TryGetValue(button, out Entry e)) return null;
            return SameGame(e, game) ? e.Look : null;
        }

        /// <summary>State read (probes): the last pick of any button of this def in this game; null when none.</summary>
        public string LastForDef(object def, object game)
        {
            if (def == null || !byDef.TryGetValue(def, out Entry e)) return null;
            return SameGame(e, game) ? e.Look : null;
        }

        public void Clear()
        {
            byButton = new ConditionalWeakTable<object, Entry>();
            byDef.Clear();
        }
    }
}
