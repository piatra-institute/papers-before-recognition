"""Figures for *Before Recognition*. Each reads the results dict and writes one PNG."""
from __future__ import annotations

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK = "#1a1a1a"
HOST = "#1f4e79"
HARM = "#b3202c"
XENIAL = "#1a7f37"
NEUTRAL = "#6a6a6a"
GRID = "#d9d9d9"
POLICIES = ["surface", "infomax", "xenial"]
LABEL = {"surface": "surface", "infomax": "information-maximising", "xenial": "xenial"}


def _style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK)
    ax.tick_params(colors=INK, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def plot_policies(res: dict, path: str) -> None:
    pol = res["policies"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.8, 3.8))

    x = np.arange(len(POLICIES))
    w = 0.26
    a1.bar(x - w, [pol[p]["identified"] for p in POLICIES], w, color=HOST, label="identified")
    a1.bar(x, [pol[p]["harm_to_candidate"] for p in POLICIES], w, color=HARM,
           label="harm to the candidate")
    a1.bar(x + w, [pol[p]["retained_option_space"] for p in POLICIES], w, color=XENIAL,
           label="option space left to it")
    a1.set_xticks(x)
    a1.set_xticklabels([LABEL[p] for p in POLICIES], fontsize=8.5)
    a1.set_ylim(0, 1.08)
    a1.set_title("what each policy buys and what it spends", fontsize=10, color=INK)
    a1.legend(frameon=False, fontsize=8, loc="upper center", ncol=1)

    a2.bar(x, [pol[p]["total_regret"] for p in POLICIES], 0.55,
           color=[NEUTRAL, NEUTRAL, XENIAL])
    for i, p in enumerate(POLICIES):
        a2.text(i, pol[p]["total_regret"] + 0.004, f"{pol[p]['total_regret']:.3f}",
                ha="center", fontsize=8.5, color=INK)
    a2.set_xticks(x)
    a2.set_xticklabels([LABEL[p] for p in POLICIES], fontsize=8.5)
    a2.set_ylabel("total regret (harm to candidate plus loss to host)")
    a2.set_title("the constrained policy is not the expensive one", fontsize=10, color=INK)
    for ax in (a1, a2):
        _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_legibility_injustice(res: dict, path: str) -> None:
    leg = res["legibility_injustice"]
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    x = np.arange(len(POLICIES))
    w = 0.36
    ax.bar(x - w / 2, [leg[p]["protection_of_the_articulate_rock"] for p in POLICIES], w,
           color=HOST, label="the articulate rock, protected")
    ax.bar(x + w / 2, [leg[p]["destruction_of_the_silent_patient"] for p in POLICIES], w,
           color=HARM, label="the silent patient, destroyed")
    ax.set_xticks(x)
    ax.set_xticklabels([LABEL[p] for p in POLICIES], fontsize=9)
    ax.set_ylim(0, 1.12)
    ax.set_title("protection allocated by how mind-like a thing looks", fontsize=10, color=INK)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_dominance(res: dict, path: str) -> None:
    dom = res["reversible_dominance"]
    stop = res["stopping_rule"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 3.9),
                                 gridspec_kw={"width_ratios": [1.15, 1]})

    hs = sorted({g["hazard_scale"] for g in dom["grid"]})
    dc = sorted({g["delay_cost"] for g in dom["grid"]})
    M = np.array([[next(g["dominance"] for g in dom["grid"]
                        if g["hazard_scale"] == h and g["delay_cost"] == d)
                   for h in hs] for d in dc])
    lim = float(np.abs(M).max())
    im = a1.imshow(M, cmap="RdYlGn", vmin=-lim, vmax=lim, aspect="auto")
    a1.set_xticks(range(len(hs)))
    a1.set_xticklabels([f"{h:g}" for h in hs], fontsize=8.5)
    a1.set_yticks(range(len(dc)))
    a1.set_yticklabels([f"{d:g}" for d in dc], fontsize=8.5)
    for i in range(len(dc)):
        for j in range(len(hs)):
            a1.text(j, i, f"{M[i, j]:+.2f}", ha="center", va="center", fontsize=8,
                    color=INK)
    a1.set_xlabel("hazard scale")
    a1.set_ylabel("cost of a round spent deliberating")
    a1.set_title("where asking first beats acting first", fontsize=10, color=INK)
    a1.grid(False)
    fig.colorbar(im, ax=a1, fraction=0.046, pad=0.04)

    labs = ["with a stopping rule", "without one"]
    keys = ["with_stopping_rule", "without_stopping_rule"]
    for k, lab, col in zip(keys, labs, (XENIAL, HARM)):
        rows = stop[k]["rows"]
        a2.plot([r["delay_cost"] for r in rows], [r["dominance"] for r in rows],
                "o-", color=col, lw=1.8, ms=5, label=lab)
    a2.axhline(0, color=INK, lw=0.9, ls="--")
    a2.set_xlabel("cost of a round spent deliberating")
    a2.set_ylabel("advantage of asking first")
    a2.set_title("patience needs to know when to stop", fontsize=10, color=INK)
    a2.legend(frameon=False, fontsize=8.5, loc="lower left")
    _style(a2)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_ban(res: dict, path: str) -> None:
    ban = res["destructive_ban"]
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    cats = ["identified,\nall types", "identified,\nthe patient",
            "harm,\nall types", "harm,\nthe patient"]
    free = [ban["with_destructive_probe"]["identified"],
            ban["with_destructive_probe"]["identified_valenced"],
            ban["with_destructive_probe"]["harm_to_candidate"],
            ban["with_destructive_probe"]["harm_to_valenced"]]
    banned = [ban["without_destructive_probe"]["identified"],
              ban["without_destructive_probe"]["identified_valenced"],
              ban["without_destructive_probe"]["harm_to_candidate"],
              ban["without_destructive_probe"]["harm_to_valenced"]]
    x = np.arange(len(cats))
    w = 0.36
    ax.bar(x - w / 2, free, w, color=NEUTRAL, label="destructive test permitted")
    ax.bar(x + w / 2, banned, w, color=XENIAL, label="destructive test forbidden")
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=8)
    ax.set_ylim(0, 1.12)
    ax.set_title("the price of refusing the one test that would settle it",
                 fontsize=10, color=INK)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
