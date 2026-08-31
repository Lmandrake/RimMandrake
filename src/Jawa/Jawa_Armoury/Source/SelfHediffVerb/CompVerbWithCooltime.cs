using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace SelfHediffVerb;

public class CompVerbWithCooltime : ThingComp, IVerbOwner
{
    public int remainCooltimeTicks = -1;

    private VerbTracker verbTracker;

    public CompProperties_VerbWithCooltime PropsVWC => props as CompProperties_VerbWithCooltime;

    public bool CanBeUsed => remainCooltimeTicks < 0;

    public VerbTracker VerbTracker => verbTracker ??= new VerbTracker(this);

    public List<VerbProperties> VerbProperties => parent.def.Verbs;

    public List<Tool> Tools => parent.def.tools;

    public ImplementOwnerTypeDef ImplementOwnerTypeDef => ImplementOwnerTypeDefOf.NativeVerb;

    public Thing ConstantCaster => Wearer;

    private Pawn Wearer => (parent.ParentHolder as Pawn_ApparelTracker)?.pawn;

    public override void CompTick()
    {
        base.CompTick();
        if (remainCooltimeTicks >= 0)
        {
            remainCooltimeTicks--;
        }
    }

    public void UsedOnce()
    {
        remainCooltimeTicks = PropsVWC.ticksCooldown;
    }

    public override IEnumerable<Gizmo> CompGetWornGizmosExtra()
    {
        if (parent.GetComp<CompApparelReloadable>() != null)
        {
            yield break;
        }
        ThingWithComps gear = parent;
        foreach (Verb verb in VerbTracker.AllVerbs)
        {
            if (verb.verbProps.hasStandardCommand)
            {
                if (verb.caster == null)
                {
                    verb.caster = Wearer;
                }
                yield return CreateVerbTargetCommand(gear, verb);
            }
        }
    }

    private Command_VerbTarget CreateVerbTargetCommand(Thing gear, Verb verb)
    {
        Command_VerbTarget command = new Command_VerbTarget
        {
            verb = verb
        };
        VerbProperties verbProps = verb.verbProps;
        if (verbProps.label != null)
        {
            command.defaultLabel = verbProps.label;
        }
        if (gear.def != null)
        {
            command.defaultDesc = gear.def.description;
        }
        if (verbProps.commandIcon != null)
        {
            command.icon = ContentFinder<Texture2D>.Get(verb.verbProps.commandIcon);
        }
        else if (verbProps.defaultProjectile != null)
        {
            command.icon = verb.verbProps.defaultProjectile.uiIcon;
        }
        else
        {
            command.icon = gear.def.uiIcon;
        }
        if (!Wearer.IsColonistPlayerControlled)
        {
            command.Disable("CannotOrderNonControlled".Translate());
        }
        else if (verb.verbProps.violent && Wearer.WorkTagIsDisabled(WorkTags.Violent))
        {
            command.Disable(("IsIncapableOfViolenceLower".Translate(Wearer.LabelShort, Wearer)).CapitalizeFirst() + ".");
        }
        else if (!CanBeUsed)
        {
            command.Disable("SelfHediffVerb_CooltimeRemain".Translate(remainCooltimeTicks.ToStringSecondsFromTicks("F0")));
        }
        return command;
    }

    public override void PostExposeData()
    {
        base.PostExposeData();
        Scribe_Values.Look(ref remainCooltimeTicks, "remainCooltimeTicks", -1);
    }

    public string UniqueVerbOwnerID()
    {
        return "Cooltime_" + parent.ThingID;
    }

    public bool VerbsStillUsableBy(Pawn p)
    {
        return Wearer == p;
    }
}
