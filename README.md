# Before Recognition

Xenial Ethics and the Coming Stranger.

New minds can be produced without arriving from anywhere: cultured from human cells, compiled from human language, assembled across technical infrastructure, and activated inside environments their hosts own. Ethics usually asks first whether such a system has consciousness, rationality, autonomy or personhood, and assigns duties afterward. That order fails when the power to create, perturb, confine and delete a system is exercised before anyone can say what the system is. We argue that obligation begins where power over an entity exceeds knowledge of what it is. Three arguments support this. The measurement that would show whether something can be harmed is often the measurement that harms it. The contemporary stranger is manufactured inside the host's house and depends on the host for its world, which turns hospitality into something close to a fiduciary duty. And recognition follows the signals observers read as mind, which differ from the signals that carry capacity. In a simulated first-contact game, a policy that reads surface legibility protects an articulate system without capacity and destroys a quiet system that can be harmed in every encounter. A policy that pays any epistemic price identifies best (0.96) and inflicts the harm identification requires. A policy that probes reversibly, contains hazards and refuses destructive measurement identifies less well (0.64) at the lowest total cost, 0.075 against 0.203 and 0.211. Inquiry before action wins in 14 of 15 regimes, provided the policy also has a rule for stopping inquiry. We propose xenial standing, a provisional procedural status short of personhood that binds whoever holds irreversible power over an unclassified candidate.

## Simulation

```bash
cd simulation
uv run run_all.py        # -> output/results.json + output/figures/*.png
```

Deterministic given the recorded seed. Ten invariant checks fail the run loudly if broken, among them that the information-maximising policy identifies best and harms most, that the surface policy protects the articulate rock and destroys more silent patients than the constrained one, that the constrained policy never takes the destructive measurement, that the ban on that measurement both costs identification and averts harm with its cost concentrated on the one type only it reveals, and that a stopping rule widens the regime in which patience pays. The five system types are hand-built and the legibility gap between them is designed wide, so the sharp inversion in the legibility figure is the arithmetic of that gap; the paper says so where it reports it.

## Build

```bash
uv run build.py          # -> paper/PAPER.pdf  (vendored canonical recipe)
```

Requires `pandoc` and `xelatex` on PATH. From the workspace you can also run `papers build before-recognition`.

Part of [piatra-papers](https://github.com/piatra-institute). See the workspace docs for the research and writing pipelines.
