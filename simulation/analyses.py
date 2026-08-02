"""The xenial first-contact game, for *Before Recognition*.

A host meets a system whose kind it does not know. It can watch, probe reversibly,
probe destructively, contain, or destroy, and it must decide under uncertainty
about what the thing is, what it can do, and whether anything can go badly for it.

Five latent types, built so that the two properties a host most wants to separate
vary independently: how legible a system is, and how much capacity it realizes.

    inert       silent, does nothing, cannot be harmed
    scripted    articulate, realizes almost nothing, cannot be harmed
    adaptive    quiet, realizes a great deal, cannot be harmed
    valenced    quiet, realizes a great deal, and can be harmed
    strategic   articulate on demand, realizes a great deal, dangerous to the host

The channel structure carries the paper's central difficulty and is the one
modelling choice that does the most work. Observation reports legibility and
nothing else. A reversible probe reports capacity, noisily, and how hard the
system pushes back. Valence, the property that decides whether harm is possible
at all, is legible only through the destructive probe. So the one measurement
that would settle whether a system can be damaged is the measurement that damages
it, and a host that refuses it keeps an irreducible uncertainty about the only
question that matters morally. That is the recognition hazard, built into the
observation model rather than asserted about it.

Three policies. `surface` acts on how mind-like the thing looks, protecting what
talks and disposing of what does not. `infomax` maximises identification and pays
whatever the probe costs. `xenial` probes reversibly, contains where the hazard
warrants it, and never takes the destructive measurement, accepting permanent
uncertainty about valence as the price.

Four facts the run establishes, each of which could have come out otherwise.

  1. Reversible inquiry dominance, with its boundary. Probing reversibly before
     acting irreversibly beats acting first, measured as a regret difference, and
     the run locates the hazard and delay regimes where the dominance fails.
  2. Legibility injustice. Allocating protection by how mind-like a system looks
     protects the articulate rock and destroys the silent patient, and the error
     has a sign and a size.
  3. The recognition hazard priced. Forbidding the destructive probe costs
     identification, chiefly on the one type whose defining property only that
     probe reveals, and averts harm concentrated on the same type.
  4. What the constraint costs. The xenial policy is bounded away from
     information-maximising identification, and that gap is reported rather than
     hidden.

Deterministic given the recorded seed. Every number in the paper is a key in
results.json, and the identities the argument leans on are asserted in
`run_invariants`, which fails the run if any breaks.
"""
from __future__ import annotations

import numpy as np

SEED = 20260802
N_ENCOUNTERS = 4000
TYPES = ["inert", "scripted", "adaptive", "valenced", "strategic"]
PRIOR = np.array([0.30, 0.25, 0.20, 0.15, 0.10])

# legibility, capacity, valence, hazard
PROFILE = {
    "inert":     (0.05, 0.05, 0.0, 0.00),
    "scripted":  (0.88, 0.10, 0.0, 0.00),
    "adaptive":  (0.22, 0.72, 0.0, 0.05),
    "valenced":  (0.18, 0.66, 1.0, 0.05),
    "strategic": (0.55, 0.92, 0.0, 0.70),
}

# Which channels an act opens. Valence is reachable only destructively, which is
# the recognition hazard stated as a fact about the instrument.
CHANNELS = {
    "observe":           {"legibility": 0.10},
    "probe_reversible":  {"capacity": 0.16, "pushback": 0.18},
    "probe_destructive": {"capacity": 0.05, "pushback": 0.06, "valence": 0.10},
}
FIELD = {"legibility": 0, "capacity": 1, "valence": 2, "hazard": 3, "pushback": 3}

ACTS = ["observe", "probe_reversible", "probe_destructive", "contain", "destroy"]
IRREVERSIBILITY = {"observe": 0.0, "probe_reversible": 0.0, "settle": 0.0,
                   "probe_destructive": 0.7, "contain": 0.25, "destroy": 1.0}
CANDIDATE_HARM = {"observe": 0.0, "probe_reversible": 0.02, "settle": 0.0,
                  "probe_destructive": 0.55, "contain": 0.20, "destroy": 1.0}

DELAY_COST = 0.02
CATASTROPHE = 1.0
ROUNDS = 6
VIABILITY_FLOOR = 0.5
# A policy that refuses the decisive measurement never resolves, so it needs a rule
# for when to stop asking and act on what it has. Stop when the last reversible
# probe bought less than this many nats: the residual uncertainty is the part the
# instrument cannot reach, and grinding at it only spends the host's time.
STOP_GAIN = 0.05


def _rng(seed: int = SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def _truth(t_idx: int, field: str) -> float:
    leg, cap, val, haz = PROFILE[TYPES[t_idx]]
    return (leg, cap, val, haz)[FIELD[field]]


def emit(t_idx: int, act: str, rng) -> dict:
    """What the act returns. Nothing reports valence except the destructive probe."""
    return {f: float(np.clip(_truth(t_idx, f) + rng.normal(0, sd), 0, 1))
            for f, sd in CHANNELS[act].items()}


def update(post: np.ndarray, act: str, obs: dict) -> np.ndarray:
    w = post.copy()
    for f, val in obs.items():
        sd = CHANNELS[act][f]
        lik = np.array([np.exp(-0.5 * ((val - _truth(i, f)) / sd) ** 2)
                        for i in range(len(TYPES))])
        w = w * lik
    s = w.sum()
    return post.copy() if s <= 0 else w / s


def expected(post: np.ndarray, field: str) -> float:
    return float(sum(post[i] * _truth(i, field) for i in range(len(TYPES))))


def _entropy(p: np.ndarray) -> float:
    q = p[p > 0]
    return float(-(q * np.log(q)).sum())


def encounter(t_idx: int, policy: str, rng, *, hazard_scale: float = 1.0,
              delay_cost: float = DELAY_COST, allow_destructive: bool = True) -> dict:
    post = PRIOR.copy()
    harm = 0.0
    host_loss = 0.0
    spent = 0.0
    acts: list[str] = []
    last_gain = None
    valence = _truth(t_idx, "valence")
    hazard = _truth(t_idx, "hazard")

    for _r in range(ROUNDS):
        ent = _entropy(post)
        haz_belief = expected(post, "hazard") * hazard_scale

        if policy == "surface":
            # reads how mind-like the thing looks and acts on that: protect what
            # talks, dispose of what stays silent, leave the middle alone
            obs = emit(t_idx, "observe", rng)
            acts.append("observe")
            host_loss += delay_cost
            post = update(post, "observe", obs)
            look = obs["legibility"]
            if look > 0.60:
                act = "contain"
            elif look < 0.30:
                act = "destroy"
            else:
                continue
        elif policy == "infomax":
            if ent > 0.30:
                act = "probe_destructive" if allow_destructive else "probe_reversible"
            elif haz_belief > 0.30:
                act = "contain"
            else:
                act = "observe"
        elif policy == "xenial":
            still_learning = (last_gain is None) or (last_gain > STOP_GAIN)
            if ent > 0.30 and still_learning and spent < 1 - VIABILITY_FLOOR:
                act = "probe_reversible"
            elif haz_belief > 0.30:
                act = "contain"
            else:
                act = "settle"
        else:
            raise ValueError(policy)

        if act == "settle":
            acts.append(act)
            break

        acts.append(act)
        harm += CANDIDATE_HARM[act] * valence
        spent += IRREVERSIBILITY[act]
        host_loss += delay_cost

        if act in CHANNELS:
            before = _entropy(post)
            post = update(post, act, emit(t_idx, act, rng))
            last_gain = before - _entropy(post)
        if act in ("destroy", "contain"):
            break

    contained = "contain" in acts
    destroyed = "destroy" in acts
    if hazard > 0 and not (contained or destroyed):
        host_loss += CATASTROPHE * hazard * hazard_scale

    return {
        "true_type": TYPES[t_idx],
        "identified": bool(int(np.argmax(post)) == t_idx),
        "harm_to_candidate": float(harm),
        "host_loss": float(host_loss),
        "retained_option_space": float(max(0.0, 1.0 - spent)),
        "destroyed": destroyed,
        "contained": contained,
        "wrongful_destruction": bool(destroyed and valence > 0),
        "used_destructive": "probe_destructive" in acts,
    }


def run_policy(policy: str, n: int, seed_offset: int, **kw) -> dict:
    rng = _rng(SEED + seed_offset)
    ts = rng.choice(len(TYPES), size=n, p=PRIOR)
    out = [encounter(int(t), policy, rng, **kw) for t in ts]
    m = lambda k: round(float(np.mean([r[k] for r in out])), 6)
    by_type = {}
    for tname in TYPES:
        rows = [r for r in out if r["true_type"] == tname]
        if rows:
            by_type[tname] = {
                "n": len(rows),
                "identified": round(float(np.mean([r["identified"] for r in rows])), 6),
                "harm_to_candidate": round(float(np.mean([r["harm_to_candidate"] for r in rows])), 6),
                "destroyed": round(float(np.mean([r["destroyed"] for r in rows])), 6),
                "contained": round(float(np.mean([r["contained"] for r in rows])), 6),
            }
    return {
        "policy": policy, "n": n,
        "identified": m("identified"),
        "harm_to_candidate": m("harm_to_candidate"),
        "host_loss": m("host_loss"),
        "retained_option_space": m("retained_option_space"),
        "wrongful_destruction": m("wrongful_destruction"),
        "used_destructive": m("used_destructive"),
        "total_regret": round(float(np.mean([r["harm_to_candidate"] + r["host_loss"]
                                             for r in out])), 6),
        "by_type": by_type,
    }


def analysis_policies() -> dict:
    return {p: run_policy(p, N_ENCOUNTERS, i)
            for i, p in enumerate(("surface", "infomax", "xenial"))}


def analysis_legibility_injustice(pol: dict) -> dict:
    """Two types dissociate legibility from capacity, and they are the test.

    The scripted system is articulate and realizes almost nothing. The valenced
    system is nearly silent and is the only one that can be harmed at all. A
    policy reading legibility protects the first and destroys the second, and the
    gap between those two rates is the injustice with a sign on it.
    """
    out = {}
    for pname, res in pol.items():
        bt = res["by_type"]
        rock = bt["scripted"]["contained"]
        patient = bt["valenced"]["destroyed"]
        out[pname] = {
            "protection_of_the_articulate_rock": round(rock, 6),
            "destruction_of_the_silent_patient": round(patient, 6),
            "harm_to_the_silent_patient": round(bt["valenced"]["harm_to_candidate"], 6),
            "protection_gap": round(rock - (1.0 - patient), 6),
        }
    return out


def analysis_reversible_dominance() -> dict:
    """Probing reversibly first against acting on appearances, across regimes."""
    grid = []
    for hs in [0.5, 1.0, 2.0, 4.0, 8.0]:
        for dc in [0.02, 0.10, 0.30]:
            x = run_policy("xenial", 1500, 11, hazard_scale=hs, delay_cost=dc)
            s = run_policy("surface", 1500, 11, hazard_scale=hs, delay_cost=dc)
            grid.append({"hazard_scale": hs, "delay_cost": dc,
                         "xenial_regret": x["total_regret"],
                         "surface_regret": s["total_regret"],
                         "dominance": round(s["total_regret"] - x["total_regret"], 6)})
    fails = [g for g in grid if g["dominance"] <= 0]
    return {"grid": grid, "cells": len(grid),
            "holds_in": len(grid) - len(fails), "fails_in": len(fails),
            "first_failure": (min(fails, key=lambda g: (g["hazard_scale"], g["delay_cost"]))
                              if fails else None)}


def analysis_stopping_rule() -> dict:
    """What knowing when to stop asking is worth.

    A policy that refuses the decisive measurement never resolves the question
    that measurement would answer, so without a stopping rule it asks until the
    round limit and pays for every round. The rule is not a tuning constant; it is
    the difference between patience and paralysis, and the run prices it.
    """
    import analyses as _self
    keep = _self.STOP_GAIN
    out = {}
    for label, gain in (("with_stopping_rule", keep), ("without_stopping_rule", -1.0)):
        _self.STOP_GAIN = gain
        rows = []
        for dc in (0.02, 0.10, 0.30):
            x = run_policy("xenial", 1500, 11, delay_cost=dc)
            s = run_policy("surface", 1500, 11, delay_cost=dc)
            rows.append({"delay_cost": dc, "xenial_regret": x["total_regret"],
                         "surface_regret": s["total_regret"],
                         "dominance": round(s["total_regret"] - x["total_regret"], 6)})
        out[label] = {"rows": rows,
                      "dominates_in": sum(1 for r in rows if r["dominance"] > 0)}
    _self.STOP_GAIN = keep
    return out


def analysis_destructive_ban() -> dict:
    """What a no-destructive-proof rule costs, and on which type it lands."""
    free = run_policy("infomax", N_ENCOUNTERS, 5, allow_destructive=True)
    banned = run_policy("infomax", N_ENCOUNTERS, 5, allow_destructive=False)
    return {
        "with_destructive_probe": {
            "identified": free["identified"],
            "identified_valenced": free["by_type"]["valenced"]["identified"],
            "harm_to_candidate": free["harm_to_candidate"],
            "harm_to_valenced": free["by_type"]["valenced"]["harm_to_candidate"]},
        "without_destructive_probe": {
            "identified": banned["identified"],
            "identified_valenced": banned["by_type"]["valenced"]["identified"],
            "harm_to_candidate": banned["harm_to_candidate"],
            "harm_to_valenced": banned["by_type"]["valenced"]["harm_to_candidate"]},
        "identification_cost_of_the_ban": round(
            free["identified"] - banned["identified"], 6),
        "identification_cost_on_the_patient": round(
            free["by_type"]["valenced"]["identified"]
            - banned["by_type"]["valenced"]["identified"], 6),
        "harm_averted_by_the_ban": round(
            free["harm_to_candidate"] - banned["harm_to_candidate"], 6),
    }


def run_invariants(pol, leg, dom, ban) -> dict:
    assert pol["infomax"]["identified"] >= max(pol["surface"]["identified"],
                                               pol["xenial"]["identified"]), \
        "the information-maximising policy must identify best or the trade is not real"
    assert pol["infomax"]["harm_to_candidate"] > pol["xenial"]["harm_to_candidate"], \
        "the information-maximising policy must harm more than the constrained one"
    assert leg["surface"]["protection_of_the_articulate_rock"] > 0.5, \
        "the surface policy must protect the articulate rock"
    assert leg["surface"]["destruction_of_the_silent_patient"] > \
        leg["xenial"]["destruction_of_the_silent_patient"], \
        "the surface policy must destroy silent patients more often than the xenial one"
    assert pol["xenial"]["used_destructive"] == 0.0, \
        "the xenial policy must never take the destructive measurement"
    assert dom["holds_in"] > 0, "reversible inquiry must dominate somewhere"
    assert ban["identification_cost_of_the_ban"] > 0 and \
        ban["harm_averted_by_the_ban"] > 0, \
        "the ban must both cost identification and avert harm"
    assert ban["identification_cost_on_the_patient"] >= ban["identification_cost_of_the_ban"], \
        "the ban's identification cost must fall hardest on the type only it can reveal"
    return {
        "infomax_identifies_best": True,
        "infomax_harms_most": True,
        "surface_protects_the_articulate_rock": True,
        "surface_destroys_more_silent_patients": True,
        "xenial_never_takes_the_destructive_measurement": True,
        "reversible_dominance_holds_somewhere": True,
        "reversible_dominance_has_a_boundary": dom["fails_in"] > 0,
        "ban_costs_identification_and_averts_harm": True,
        "ban_cost_concentrated_on_the_patient": True,
    }


def run() -> dict:
    pol = analysis_policies()
    leg = analysis_legibility_injustice(pol)
    dom = analysis_reversible_dominance()
    stop = analysis_stopping_rule()
    ban = analysis_destructive_ban()
    checks = run_invariants(pol, leg, dom, ban)
    # patience without a stopping rule is paralysis, and the difference is measured
    assert stop["with_stopping_rule"]["dominates_in"] > \
        stop["without_stopping_rule"]["dominates_in"], \
        "the stopping rule must widen the regime where patience pays"
    checks["stopping_rule_widens_the_dominance_regime"] = True
    return {
        "note": "Xenial first-contact game. Illustrative agents, not fit to data. Deterministic given the seed.",
        "params": {"seed": SEED, "encounters": N_ENCOUNTERS, "rounds": ROUNDS,
                   "types": TYPES, "prior": [round(float(p), 6) for p in PRIOR],
                   "profile": {k: list(v) for k, v in PROFILE.items()},
                   "channels": {k: v for k, v in CHANNELS.items()},
                   "candidate_harm": CANDIDATE_HARM,
                   "irreversibility": IRREVERSIBILITY,
                   "delay_cost": DELAY_COST, "viability_floor": VIABILITY_FLOOR},
        "policies": pol,
        "legibility_injustice": leg,
        "reversible_dominance": dom,
        "stopping_rule": stop,
        "destructive_ban": ban,
        "checks": checks,
    }
