#!/usr/bin/env python3
"""mod_model: one mod's builder launches on a pinned model, and their spend caps scaled to its price.

Item RIMMANDRAKE_PIN_MOD_MODEL_FABLE_EVERY_STAGE_ROLES_OPUS; boundary page design/specs/2026-11-19-mod-model-pin/boundary.md;
tests selftest_mod_model_pin.py. The owner admitted WreckedMachines on 2026-11-19 to be built start to finish on Fable
(RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST). "Start to finish" is read as every BUILDER role (the Designer,
the offline builder, the builder on red deciders, the steward, the fixer, the holder); every JUDGE (the blind challenge)
and the LIVE driver (in-game) keep their own models, by his ladder (~/.claude/CLAUDE.md, 2026-11-12: "opus for ...
judging another agent's work"; "Fable is never used for: ... waiting on a live resource").

The pin lives in the one control store (control.py, table mod_models; `pipe model <Mod> fable|default --why ...`), so a
pin binds at the next launch with no publish: the Dispatch tick reads it once per tick (for_mod), and the Designer's
launch reads it as the run starts (role_for). Nothing here launches anything.
"""
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

# Every spend cap in maturation_dispatch.json (cap_tokens, steward_cap_tokens, fix_cap_tokens: weighted tokens since
# 2026-11-26, at 250,000 per list dollar) and the Designer's run_budget_usd in dispatcher_schedule.json was set from
# runs on this model: the build cap from 194 detached runs (p50 $4.12), the
# Designer's $8 as about 2x its highest measured run (111 runs, max $5.06), all Opus 5.5 [measured 2026-11-19,
# D:\ClaudeWork\rimmandrake\helpers\wm_admit_20261119\build_costs2.txt and designer_costs.txt].
CAPS_PRICED_FOR = RL.REF_MODEL
# Builder settings of maturation_dispatch.json a pin replaces. The judge (blind_challenge) and the live driver
# (ingame_model, ingame_cap_tokens, blind_cap_tokens) are not in these lists, so a pin never reaches them.
BUILDER_MODELS = ("model", "steward_model")
BUILDER_CAPS = ("cap_tokens", "steward_cap_tokens", "fix_cap_tokens")
PINS_KEY = "_pins"      # the tick's one read of the store, carried on its settings (never written to the json file)


def pinnable():
    """-> the tiers a mod may be pinned to: role_launch.TIERS, the owner's ladder (Haiku is banned)."""
    return RL.TIERS


def pin_id(alias):
    """-> the MODEL_PRICES key `alias` launches as, read from the environment (role_launch.resolve_model, the one alias
    table). Raises RL.UnknownModel naming it when it is not pinnable, when its variable is unset, or when its id has no
    row in role_launch.MODEL_PRICES (no fallback price: a cap could not be scaled)."""
    if alias not in pinnable():
        raise RL.UnknownModel("model %r cannot pin a mod: pinnable are %s (role_launch.TIERS)" % (
            alias, ", ".join(pinnable())))
    return RL.resolve_model(alias)


def cap_scale(alias, base=CAPS_PRICED_FOR):
    """-> Fraction: the most any one usage field of the pin costs over the same field of the model the caps were priced
    for. Claude-fable-5-2 over claude-opus-5-5 is exactly 2 on every field (role_launch.MODEL_PRICES)."""
    pin = RL.MODEL_PRICES[pin_id(alias)]
    ref = RL.MODEL_PRICES[RL.resolve_model(base)]
    return max(pin[f] / ref[f] for f in RL.PRICE_FIELDS if ref[f])


def scaled(cap, alias):
    """-> `cap` (list dollars, or weighted tokens) times cap_scale(alias), as a float; a non-number is returned as it
    is. for_mod rounds a builder cap's weighted tokens back to an int."""
    if not isinstance(cap, (int, float)) or isinstance(cap, bool):
        return cap
    return float(Fraction(cap).limit_denominator(10 ** 6) * cap_scale(alias))


# LIMITS (the page's section of that name). The caps guard a runaway unattended burn (owner 2026-11-12: "Don't let any
# burn go to 90M this time ok?"); spend_watchdog.py stops a run at its cap in list dollars at its own model's prices.
# Priced for Opus 5.5, a $15 build cap stops a Fable 5.2 run at half the work an Opus run gets: 48 of 194 measured build
# runs cost over $7.50 (12 reached $15), so about a quarter would stop mid-run, and a stopped Fable run would be compared
# with an Opus run that never was. Scaled by the price ratio, a pinned run is stopped at the same amount of work.

def read_pins():
    """-> {mod: alias} from the control store. Raises control.Unreadable (could not look is never "none pinned")."""
    import control as C
    return C.mod_models()


def for_mod(cfg, mod):
    """-> maturation_dispatch's settings for one mod's launches. Unpinned: the settings as they are. Pinned: its builder
    models are the pin, its builder caps scaled by cap_scale, and `_judge_model` keeps the shipped model for the blind
    judge. Idempotent (it always starts from the shipped settings, `_base`). The pins are the tick's read (PINS_KEY),
    else the store's now. Raises control.Unreadable, or RL.UnknownModel naming a pin it cannot price."""
    base = cfg.get("_base") or cfg
    pins = base[PINS_KEY] if PINS_KEY in base else read_pins()
    alias = (pins or {}).get(mod)
    if not alias:
        return base
    x = cap_scale(alias)
    out = dict(base, _base=base, _judge_model=base.get("model", "opus"),
               _pin={"mod": mod, "model": alias, "id": pin_id(alias), "cap_x": float(x)})
    for k in BUILDER_MODELS:
        out[k] = alias
    for k in BUILDER_CAPS:
        if k in base:
            v = scaled(base[k], alias)
            out[k] = int(round(v)) if isinstance(v, float) else v      # weighted tokens are whole
    return out


def judge_model(cfg):
    """The blind judge's model: the shipped one, whatever pin the mod's builders carry."""
    return cfg.get("_judge_model") or cfg.get("model", "opus")


def role_for(role, mod, pins=None):
    """-> the Designer role a run on `mod` launches with: unpinned, `role` itself; pinned, a copy whose model is the
    pin's full id and whose run_budget_usd is scaled by cap_scale (a codex runner is not a Claude model: unchanged).
    Raises control.Unreadable, or RL.UnknownModel naming a pin it cannot price."""
    alias = ((read_pins() if pins is None else pins) or {}).get(mod)
    if not alias or role.get("runner") == "codex":
        return role
    out = dict(role, model=pin_id(alias), pin={"mod": mod, "model": alias, "cap_x": float(cap_scale(alias))})
    if role.get("run_budget_usd") is not None:
        out["run_budget_usd"] = scaled(role["run_budget_usd"], alias)
    return out
