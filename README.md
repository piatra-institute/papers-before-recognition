# Before Recognition

Xenial Ethics and the Coming Stranger. The paper argues that obligation begins where power over an entity exceeds knowledge of what the entity is, and works out the ethics and the law that follow from putting the duty before the classification. Three arguments carry it. The measurement that would settle whether something can be harmed is often the measurement that harms it, so a host demanding proof is choosing to commit the act the proof was meant to license. The contemporary stranger does not cross a threshold but is cultured, compiled, and switched on inside an environment its host owns, which makes creation a source of duty on the same grounds that make a fiduciary's power one. And recognition tracks the signals observers read as mind, which are not the signals that carry capacity, so protection goes to whatever is articulate. A first-contact game measures the last two across 4000 encounters per policy: a policy reading surface legibility protects an articulate system with no capacity in every encounter and destroys a quiet system that can be harmed in every encounter; a policy paying any epistemic price identifies best at 0.96 and takes the harm identification requires; a policy probing reversibly and refusing the destructive measurement identifies at 0.64 and carries the lowest total cost of the three, 0.075 against 0.203 and 0.211, leaving its subject 0.975 of its option space. Asking before acting dominates in 14 of 15 hazard and delay regimes, and only for a policy that also knows when to stop asking; without a stopping rule the same patience wins in 1 of 3. Refusing the destructive test costs 0.27 of identification, falling hardest at 0.41 on the one kind whose defining property only that test reveals. The juridical proposal is xenial standing, a provisional procedural status short of personhood: preservation stay, boundary hearing, independent representation, least-restrictive containment, no destructive proof requirement, periodic review.

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

Requires `pandoc` and `xelatex` on PATH. From the workspace you can also run
`papers build before-recognition`.

Part of [piatra-papers](https://github.com/piatra-institute). See the workspace
docs for the research and writing pipelines.
