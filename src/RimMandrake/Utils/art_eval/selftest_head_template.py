#!/usr/bin/env python3
"""Selftest: the art-eval pipeline can judge humanlike species heads and head attachments (template `head`).

It checks that the template parses and every code is in the severity policy, that the checklist differs by module
(head vs attachment), that a card without its panels is held, and that the code gate (head_truth.py) refuses a
coloured skin-tinted head and a head outside the envelope before any model call, while a good grey head reaches the
reviewers with the head module in its prompt. Heads are drawn from head_envelope.json's own vanilla skull box, so the
test needs no media file (slim clones hold none). Reviewers are mocked; state goes in a temporary directory.

    python3 src/RimMandrake/Utils/art_eval/selftest_head_template.py      exit 0 all pass, 1 any fail
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import policy as P  # noqa: E402

FAILS, PASSED = [], []


def check(name, cond, detail=""):
    (PASSED if cond else FAILS).append(name)
    if not cond:
        print("FAIL", name, detail)


def head_pngs(d: Path, tag: str, fill=(196, 196, 196), dy=0.0, scale=1.0) -> dict:
    """south/east/north heads on a 512 canvas filling the vanilla skull box (moved down by dy, scaled by scale)."""
    from PIL import Image, ImageDraw
    import head_truth as HT
    env = HT.F.load_envelope()
    out = {}
    for f in ("south", "east", "north"):
        b = env["vanilla_skull"][f]
        cx, cy, w, h = (b["l"] + b["r"]) / 2, (b["t"] + b["b"]) / 2 + dy, b["w"] * scale, b["h"] * scale
        im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        box = [(cx - w / 2) * 512, (cy - h / 2) * 512, (cx + w / 2) * 512 - 1, (cy + h / 2) * 512 - 1]
        dr.ellipse(box, fill=fill + (255,), outline=(40, 40, 40, 255), width=3)
        p = d / f"{tag}_{f}.png"
        im.save(p)
        out[f] = str(p)
    return out


def run_checks(td: Path):
    import cards as C
    import head_truth as HT
    import runner as RN

    pol = P.load_policy()
    # --- the template exists, parses, and speaks only codes the policy knows
    check("head is a template", "head" in P.TEMPLATES, P.TEMPLATES)
    tpl = P.load_template("head")
    check("head template parses", tpl["template"] == "head" and tpl["checklist"] and tpl["version"].startswith("head@"))
    unknown = [it["code"] for it in tpl["checklist"] if it["code"] not in pol["codes"]]
    check("every head checklist code is in the severity policy", not unknown, unknown)
    check("gate codes are policy codes and block", all(pol["codes"].get(c, {}).get("default") == "blocking"
                                                     for c in ("SKIN_NOT_GREY", "HEAD_ENVELOPE")))
    check("module text is sent without the JSON block", "```json" not in tpl["module_text"]
          and "Template: head" in tpl["module_text"])
    g = tpl.get("gate", {}).get("greyscale", {})
    check("greyscale limits name their danger and basis", g.get("_danger") and g.get("_basis")
          and 0 < g["mean_chroma_max"] < g["p95_chroma_max"] < 1, g)
    check("shadow settings cover the head template", "head" in P.DEFAULT_SETTINGS["shadow"])

    # --- the checklist asks the head questions per module
    ids = lambda module, facts=frozenset(): {i["id"] for i in P.checklist_for(tpl, module, set(facts))}  # noqa: E731
    h, a = ids("head"), ids("attachment")
    for need in ("SOUTH_FRONT", "NORTH_REAR", "EAST_PROFILE", "SAME_HEAD", "STYLE", "OURS", "ALPHA"):
        check(f"head and attachment both ask {need}", need in h and need in a, (h, a))
    check("a head is asked HEAD_ONLY and SCALE, not ATTACH_FIT", {"HEAD_ONLY", "SCALE"} <= h and "ATTACH_FIT" not in h, h)
    check("an attachment is asked ATTACH_FIT, not HEAD_ONLY", "ATTACH_FIT" in a and "HEAD_ONLY" not in a, a)
    check("canon is asked only when the card carries canon", "CANON" not in h and "CANON" in ids("head", {"canon"}))

    # --- panels: a head card without scale, an attachment without its head, are held before any model
    full = {"south": 1, "east": 1, "north": 1, "facings": 1}
    check("head without scale -> HOLD_INPUT", P.pre_route({"module": "head", "panels": full}, tpl, None) == "HOLD_INPUT")
    check("head with scale proceeds", P.pre_route({"module": "head", "panels": dict(full, scale=1)}, tpl, None) is None)
    check("attachment without head_reference -> HOLD_INPUT",
          P.pre_route({"module": "attachment", "panels": full}, tpl, None) == "HOLD_INPUT")

    # --- the code gate: grey head in the box passes; planted faults are each refused
    good = head_pngs(td, "good")
    base = {"template": "head", "module": "head", "subject": "RSW_Togruta__Female0", "label": "Togruta head",
            "description": "a Togruta head", "owner_kept": False}
    t_good = HT.truth(dict(base, images=good))
    check("grey head inside the envelope: PASS", t_good["verdict"] == "PASS", t_good)
    t_col = HT.truth(dict(base, images=head_pngs(td, "orange", fill=(220, 120, 40))))
    check("coloured skin-tinted head: FLAG SKIN_NOT_GREY on every facing",
          t_col["verdict"] == "FLAG" and sorted(x["facing"] for x in t_col["flags"] if x["code"] == "SKIN_NOT_GREY")
          == ["east", "north", "south"], t_col)
    t_untinted = HT.truth(dict(base, skin_tint=False, images=head_pngs(td, "orange2", fill=(220, 120, 40))))
    check("the same colour drawn untinted (skin_tint false): PASS", t_untinted["verdict"] == "PASS", t_untinted)
    t_low = HT.truth(dict(base, images=head_pngs(td, "low", dy=0.08)))
    check("skull seated below the vanilla chin: FLAG HEAD_ENVELOPE",
          t_low["verdict"] == "FLAG" and {x["code"] for x in t_low["flags"]} == {"HEAD_ENVELOPE"}, t_low)
    t_big = HT.truth(dict(base, images=head_pngs(td, "big", scale=1.5)))
    check("skull 1.5x the vanilla skull: FLAG HEAD_ENVELOPE",
          t_big["verdict"] == "FLAG" and "HEAD_ENVELOPE" in {x["code"] for x in t_big["flags"]}, t_big)
    t_att = HT.truth(dict(base, module="attachment", images=head_pngs(td, "att", dy=0.2)))
    check("an attachment is not held to the skull envelope", t_att["verdict"] == "PASS", t_att)
    blank = {f: str(td / f"blank_{f}.png") for f in ("south", "east", "north")}
    from PIL import Image
    for p in blank.values():
        Image.new("RGBA", (512, 512), (0, 0, 0, 0)).save(p)
    t_blank = HT.truth(dict(base, images=blank))
    check("a blank head is UNMEASURED, never PASS", t_blank["verdict"] == "UNMEASURED", t_blank)
    check("creature specs are not head-gated", HT.truth({"template": "creature", "images": good}) is None)

    # --- the runner: a coloured head is sent back before any model; a good head reaches Opus with the head module
    calls = []

    class Mock(RN.Reviewers):
        def opus(self, prompt, card_dir):
            calls.append((card_dir.name, prompt))
            card = json.loads((card_dir / "card.json").read_text())
            items = P.checklist_for(tpl, card["module"], P.card_facts(card))
            return json.dumps({"schema": "rm-art-eval/opus@v1", "subject": card["subject"], "observed": {},
                               "checklist": {i["id"]: {"status": "ok", "seen": "-"} for i in items},
                               "findings": [], "overall": "good"}), {"models_reported": ["mock-opus"]}

        def gpt(self, prompt, images, work):
            raise AssertionError("no GPT call expected")

    settings = dict(P.DEFAULT_SETTINGS)
    scale = head_pngs(td, "scale")["south"]
    ref = head_pngs(td, "ref")
    r_col = RN.evaluate(dict(base, subject="RSW_Togruta__Orange",
                             images=dict(head_pngs(td, "o", fill=(220, 120, 40)), scale=scale)),
                        td / "card_orange", Mock(), pol, settings, {}, {})
    check("runner: coloured skin-tinted head -> REGEN, no model call, regen asks for greyscale",
          r_col["decision"] == "REGEN" and not calls and "SKIN_NOT_GREY" in r_col["regen"]["findings"]
          and "greyscale" in r_col["regen"]["request"]["prompt"], (r_col["decision"], r_col["reasons"], calls))
    r_good = RN.evaluate(dict(base, subject="RSW_Togruta__Good", images=dict(good, scale=scale)),
                         td / "card_good", Mock(), pol, settings, {}, {})
    check("runner: good grey head reaches Opus and is accepted",
          r_good["decision"] == "ACCEPT" and len(calls) == 1 and "Template: head" in calls[0][1],
          (r_good["decision"], r_good["reasons"]))
    check("runner: the card tells the reviewer what code measured",
          "head gate (envelope + greyscale): PASS" in (td / "card_good" / "card.md").read_text())
    check("runner: canon of the species reaches the head card",
          "## Canon" in (td / "card_good" / "card.md").read_text())
    r_att = RN.evaluate(dict(base, module="attachment", subject="RSW_Togruta__Montrals",
                             images=dict(head_pngs(td, "m"), head_reference=ref)),
                        td / "card_att", Mock(), pol, settings, {}, {})
    att_prompt = calls[-1][1] if len(calls) == 2 else ""
    check("runner: an attachment card carries head_reference and its reviewer reads it",
          r_att["decision"] == "ACCEPT" and "head_reference.png" in att_prompt and "ATTACH_FIT" in att_prompt,
          (r_att["decision"], r_att["reasons"]))
    check("cards: head_reference is a composite source panel", "head_reference_south" in C.source_files(
        {"images": {"head_reference": ref}}))


def main() -> int:
    import round_series as RS
    with tempfile.TemporaryDirectory() as d:
        td = Path(d)
        with patch.dict("os.environ", RM_DATA_ROOT=d, ART_EVAL_WORK=str(td / "work"),
                        ARTPIPE_STATE_DIR=str(td / "artpipe"), ART_LEDGER_DIR=str(td / "art-ledger"),
                        ARTSTORE=str(td / "artstore")), \
                patch.object(RS, "RESETS", td / "round_resets.jsonl"), \
                patch.object(RS, "ADOPTIONS", td / "fauna_run_adoptions.jsonl"):
            run_checks(td)
    print(f"selftest_head_template: {len(PASSED)} passed, {len(FAILS)} failed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
