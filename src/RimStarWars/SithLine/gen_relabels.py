#!/usr/bin/env python3
"""Writes Patches/RSW_SithRelabel.xml from the table below (SANGUOPHAGE_KEPT_UNREACHABLE_1, design §1.2).

Every wording is PROVISIONAL: the owner reads it at review. Re-run after editing the table:
    python3 src/RimStarWars/SithLine/gen_relabels.py

🔴 SCOPE (deliberately narrower than design §1.2's 37 rows): only defs the Anzati no longer reach once they carry
their own copies (§1.5). The need, hediffs, thoughts, room role, job, research, hemogen pack, serum, gene and ability
categories and the chat interaction are SHARED with every Anzati deathrester, so renaming them would rename the
Anzati too — which the 2026-10-09 card ruling ("neither the Sith renames nor the unbuildable rule touches them")
forbids. They keep vanilla text. Owner decision owed only if he wants them retold anyway.

Each field is replaced inside a PatchOperationConditional on the node; label/description are added when absent.
The whole file sits inside RSW_PatchOperationSithSetting(reskinText), so turning the setting off (restart) restores
vanilla names.
"""
import os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Patches", "RSW_SithRelabel.xml")

T = [
    ("XenotypeDef", "Sanguophage", [
        ("label", "Sith adept"),
        ("description", "A lineage that bound itself to the dark side and now lives on what it takes from others. Ageless, near-deathless, never one of yours.\\n\\nA Sith adept holds a reserve of stolen life (essence) that fuels their arts: Force drain pulls it from a held victim, dark mending forces it into wounds, and a telekinetic shard is hurled with it. They do not age and never sicken. They must periodically sink into a dark trance for days, and fire and sunlight are their bane.\\n\\nNo adept has ever knelt to anyone. They cannot be recruited, enslaved or turned, and they pass their line to no one."),
        ("descriptionShort", "Ageless dark-side adepts who live on stolen life and sleep in days-long trances. Always an enemy; never recruitable."),
    ]),
    ("FactionDef", "Sanguophages", [
        ("label", "the Sith"),
        ("description", "A hidden, scattered line of dark-side adepts who answer to no one."),
        ("pawnSingular", "Sith adept"),
        ("pawnsPlural", "Sith adepts"),
        ("leaderTitle", "master"),
    ]),
    ("PawnKindDef", "Sanguophage", [("label", "Sith adept")]),
    ("GeneDef", "Hemogenic", [
        ("label", "dark-side reservoir"),
        ("description", "The carrier holds a reserve of stolen life that fuels their other gifts. The resource is gained and spent in various ways, all unlocked by other gifts.\\n\\nCarriers lose 2 essence per day as the stolen life fades."),
        ("resourceLabel", "essence"),
        ("resourceDescription", "A reserve of stolen life which can be gained and spent in a variety of ways.\\n\\nEssence is regained by Force drain on a living person or by consuming essence vials.\\n\\nIf essence reaches zero, {PAWN_nameDef} will become very unhappy."),
    ]),
    ("GeneDef", "HemogenDrain", [
        ("label", "dark-side hunger"),
        ("description", "The reserve bleeds away faster. The dark side is never satisfied. Carriers lose an additional 8 essence per day."),
        ("labelShortAdj", "hungering"),
        ("resourceLabel", "essence"),
    ]),
    ("GeneDef", "Bloodfeeder", [
        ("label", "life-drain"),
        ("description", "The carrier can draw a living being's strength into themselves, taking essence from an unresisting person held close."),
    ]),
    ("GeneDef", "Coagulate", [
        ("label", "dark mending"),
        ("description", "The carrier can close wounds by forcing stolen life into them."),
        ("labelShortAdj", "mender"),
    ]),
    ("GeneDef", "Deathrest", [
        ("label", "dark trance"),
        ("description", "The carrier must periodically sink into days of meditation in which the dark side remakes them. The trance can be deepened and its gifts enhanced by Sith devices.\\n\\nThose who put off the trance grow trance-starved."),
    ]),
    ("GeneDef", "PiercingSpine", [
        ("label", "telekinetic shard"),
        ("description", "The carrier hurls a shard of bone or stone with the Force, spending essence."),
    ]),
    ("AbilityDef", "Bloodfeed", [
        ("label", "Force drain"),
        ("description", "Pull the life from a held victim. The target loses blood and will be horrified, but is otherwise unharmed."),
    ]),
    ("AbilityDef", "Coagulate", [
        ("label", "dark mending"),
        ("description", "Seal a wound with stolen life."),
    ]),
    ("AbilityDef", "PiercingSpine", [
        ("label", "telekinetic shard"),
        ("description", "Hurl a shard with the Force at the target."),
    ]),
    ("ThingDef", "DeathrestCasket", [
        ("label", "Sith sarcophagus"),
        ("description", "A black stone coffin where a Sith lies in dark trance. It binds the Sith devices around it to the sleeper."),
    ]),
    ("ThingDef", "Hemopump", [
        ("label", "essence alembic"),
        ("description", "Sith alchemy that steeps the sleeper in drawn life, so they wake able to hold more essence. It must be bound to a Sith sarcophagus."),
    ]),
    ("ThingDef", "HemogenAmplifier", [
        ("label", "dark focus"),
        ("description", "An idol that sharpens what the sleeper takes: after the trance, every essence gain is greater. It must be bound to a Sith sarcophagus."),
    ]),
    ("ThingDef", "GlucosoidPump", [
        ("label", "rage font"),
        ("description", "Feeds the sleeper's body on hatred, so they move faster after the trance. It must be bound to a Sith sarcophagus."),
    ]),
    ("ThingDef", "PsychofluidPump", [
        ("label", "holocron cradle"),
        ("description", "A pyramid of whispering crystal that feeds the sleeper's mind, sharpening their psychic sensitivity after the trance. It must be bound to a Sith sarcophagus."),
    ]),
    ("ThingDef", "DeathrestAccelerator", [
        ("label", "trance obelisk"),
        ("description", "Deepens the trance so it ends sooner. It must be bound to a Sith sarcophagus."),
    ]),
    ("HediffDef", "HemogenAmplified", [
        ("label", "dark-focused"),
        ("description", "All essence gains are multiplied up because this person lay before a dark focus in trance. This lasts until the next trance."),
    ]),
    ("HediffDef", "GlucosoidRush", [
        ("label", "rage-fed"),
        ("description", "Move speed is increased because this person was fed by a rage font in trance. This lasts until the next trance."),
    ]),
    ("HediffDef", "PsychofluidRush", [
        ("label", "holocron-fed"),
        ("description", "Psychic sensitivity is enhanced because this person lay in a holocron cradle's whisper in trance. This lasts until the next trance."),
    ]),
]


def op(def_type, def_name, field, value):
    base = 'Defs/%s[defName="%s"]' % (def_type, def_name)
    v = escape(value)
    add = field in ("label", "description")
    lines = [
        '      <li Class="PatchOperationConditional">',
        '        <xpath>%s/%s</xpath>' % (base, field),
        '        <match Class="PatchOperationReplace">',
        '          <xpath>%s/%s</xpath>' % (base, field),
        '          <value><%s>%s</%s></value>' % (field, v, field),
        '        </match>',
    ]
    if add:
        lines += [
            '        <nomatch Class="PatchOperationAdd">',
            '          <xpath>%s</xpath>' % base,
            '          <value><%s>%s</%s></value>' % (field, v, field),
            '        </nomatch>',
        ]
    lines.append('      </li>')
    return lines


def main():
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<!-- GENERATED by src/RimStarWars/SithLine/gen_relabels.py — edit the table there, not this file.',
           '     SANGUOPHAGE_KEPT_UNREACHABLE_1 design §1.2 relabels (scope note in the generator). PROVISIONAL wording. -->',
           '<Patch>',
           '  <Operation Class="RimMandrake.StarWars.SithLine.RSW_PatchOperationSithSetting">',
           '    <setting>reskinText</setting>',
           '    <match Class="PatchOperationSequence">',
           '    <operations>']
    for t, n, fields in T:
        out.append('      <!-- %s %s -->' % (t, n))
        for f, v in fields:
            out += op(t, n, f, v)
    out += ['    </operations>', '    </match>', '  </Operation>', '</Patch>', '']
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    print("wrote %s: %d defs, %d fields" % (os.path.relpath(OUT), len(T), sum(len(f) for _, _, f in T)))


if __name__ == "__main__":
    main()
