"""Orchestrator: reproduces every number and all four figures in the paper.

    cd simulation
    uv run run_all.py

Writes output/results.json and output/figures/*.png. Deterministic given the
recorded seed. A failed invariant or a failed figure fails the run.
"""
from __future__ import annotations

import json
from pathlib import Path

from analyses import run

OUT = Path(__file__).parent / "output"


def main() -> None:
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    results = run()
    (OUT / "results.json").write_text(json.dumps(results, indent=2))

    from figures import (plot_policies, plot_legibility_injustice,
                         plot_dominance, plot_ban)
    plot_policies(results, str(OUT / "figures" / "policies.png"))
    plot_legibility_injustice(results, str(OUT / "figures" / "legibility_injustice.png"))
    plot_dominance(results, str(OUT / "figures" / "dominance.png"))
    plot_ban(results, str(OUT / "figures" / "destructive_ban.png"))

    pol = results["policies"]
    print("policy                 identified  harm   host   retained  regret")
    for p in ("surface", "infomax", "xenial"):
        d = pol[p]
        print(f"  {p:20s} {d['identified']:.3f}      {d['harm_to_candidate']:.3f}  "
              f"{d['host_loss']:.3f}  {d['retained_option_space']:.3f}     {d['total_regret']:.3f}")
    leg = results["legibility_injustice"]
    print("\nlegibility injustice (articulate rock protected / silent patient destroyed):")
    for p in ("surface", "infomax", "xenial"):
        print(f"  {p:20s} {leg[p]['protection_of_the_articulate_rock']:.3f}  "
              f"{leg[p]['destruction_of_the_silent_patient']:.3f}")
    dom = results["reversible_dominance"]
    print(f"\nreversible dominance: holds in {dom['holds_in']}/{dom['cells']} regimes; "
          f"first failure {dom['first_failure']}")
    st = results["stopping_rule"]
    print(f"stopping rule: dominates in {st['with_stopping_rule']['dominates_in']}/3 with, "
          f"{st['without_stopping_rule']['dominates_in']}/3 without")
    print("destructive ban:", results["destructive_ban"]["identification_cost_of_the_ban"],
          "identification cost,",
          results["destructive_ban"]["harm_averted_by_the_ban"], "harm averted")
    print("checks:", results["checks"])
    print("wrote", OUT / "results.json")


if __name__ == "__main__":
    main()
