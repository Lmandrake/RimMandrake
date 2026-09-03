using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// One role inside a cast: how many of which kind.
    ///
    /// Trade is a ROLE, not a template. The oil sellers are a refinery cast that
    /// contains someone who deals -- that single reframe collapses a whole class
    /// of near-duplicate place templates.
    /// </summary>
    public class InhabitedRole
    {
        /// <summary>The pawn kind this role fields.</summary>
        public PawnKindDef kind;

        /// <summary>How many. Rolled once, when the cast is first instantiated.</summary>
        public IntRange count = new IntRange(1, 1);

        /// <summary>This one deals.</summary>
        public bool trades;

        /// <summary>This one is in charge, and speaks for the place.</summary>
        public bool leads;

        public override string ToString()
        {
            return (kind?.defName ?? "NULL") + " x" + count;
        }
    }

    /// <summary>
    /// WHO lives at a place, as opposed to what the place is.
    ///
    /// Cast sizes are DECIDE's ruling of 2026-08-20 and belong in the XML, not
    /// here: hive foundry 14-22, fortified waystation 10-16, refinery 8-14,
    /// nomad camp 6-12, trade moot 5-9, homestead 4-7, droid enclave 3-6. A
    /// faction's authored characters therefore spread across two to four places,
    /// which is the intent -- a cast is a subset of a roster, never all of it.
    ///
    /// Type name is deliberately NOT the bare `CastDef` the queue item wrote.
    /// A def type name is the XML element name, shared across every mod in the
    /// load order, and this build set carries 577 of them. `CastDef` would be a
    /// coin-flip collision; `InhabitedCastDef` cannot collide with anything.
    /// </summary>
    public class InhabitedCastDef : Def
    {
        /// <summary>Who is here. Rolled once, at first instantiation.</summary>
        public List<InhabitedRole> roles = new List<InhabitedRole>();

        /// <summary>
        /// The AUTHORED people of this place, by `CharacterDef`. They are applied
        /// to the first pawns the roles generate, in order, so a cast of eight
        /// with three named characters gets those three and five nobodies.
        ///
        /// ⭐ One or two REALLY strange standouts per cast; the rest is background
        /// texture. A cast where everyone is remarkable has nobody remarkable in
        /// it, and the dull half has to be there first or the standouts have
        /// nothing to stand against.
        ///
        /// ⚠️ A character drawn from the DISPLACED POOL is already somebody and is
        /// never overwritten. Only freshly generated pawns are dressed as an
        /// authored person -- a survivor of the refinery keeps being who he was.
        /// </summary>
        public List<CharacterDef> characters = new List<CharacterDef>();

        /// <summary>
        /// How many people in total, clamping the rolled roles. A cast that rolls
        /// larger than this is trimmed from the back of the role list, so leaders
        /// and traders -- written first -- survive the trim.
        /// </summary>
        public IntRange castSize = new IntRange(4, 7);

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (roles.NullOrEmpty())
            {
                yield return "no roles: a cast with nobody in it is not a cast";
            }
            else
            {
                // Fixed 2026-09-02 (opus code review, re-review pass): this loop
                // used to run unconditionally and dereference roles.Count even
                // when roles is genuinely null (IsNull="True" in XML) - a NullRef
                // inside def validation itself. Gated on the same NullOrEmpty
                // check above instead of an early yield break, since the
                // castSize check below must still run either way.
                for (int i = 0; i < roles.Count; i++)
                {
                    if (roles[i].kind == null)
                    {
                        yield return "role " + i + " has no kind";
                    }
                    else if (roles[i].count.min < 0)
                    {
                        yield return "role " + i + " (" + roles[i].kind.defName + ") has a negative count";
                    }
                }
            }
            if (castSize.min < 1)
            {
                yield return "castSize.min below 1: " + castSize;
            }
        }
    }
}
