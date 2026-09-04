# The Unreasonable Extensibility of Computation

What a Fixed Machine Can Do, and When It Is Possible to Know. A published runtime puts a 90-million-parameter hybrid attention and state-space model on a Sony PSP with 64 MB of memory and a 333 MHz processor, at about 0.55 tokens per second, weights on a memory card, no network. The processor did not change; the stock of representations, algorithms, runtimes, and trained parameters that can be brought to it did. This paper computes with that. Capability is a relation among a machine, an artifact, a task, a budget, and a quality threshold, so the set of tasks a fixed machine can perform is indexed by a date. Three results follow. Arithmetic on the runtime's published byte format, with one free parameter solved from the one throughput figure it reports: full-precision weights need 7.24 times the console's weight cache, four-bit block quantisation reduces that by 7.11 and still leaves the model at 1.02 of the cache, the residual 0.87 MB per token must come off the card, 2 of the 16 subsets of the four techniques reach a 0.4 tokens-per-second floor with three of them individually necessary, and on the 32 MB revision of the same console 0 of 16 run at all; compression also relocates the constraint, since at or above 6 bits the system is storage-bound and at or below 5 bits arithmetic-bound, so a perfect representation would buy 1.06 times more speed and nothing else. Second, calibrating a family-improvement distribution to four published summary statistics of a 113-family census and imposing a multidimensional budget, between 0.83 and 0.89 of improvement events change no capability at all, and the burstiness of capability crossings relative to the gains causing them rises from 0.84 to 1.67 as the budget binds harder, so amplification is real and conditional; in the most demanding regime the fixed device overtakes a device with 10 times its budget running frozen software in year 25. Third, deployable capability requires every component of a stack to remain runnable at once, so it saturates rather than growing, at 0.43 of known for a five-component stack against 0.83 for one, and for a five-deep stack to survive as long as the mean interval between improvements in its field each component would have to last 201 years.

## Simulation

```bash
cd simulation
uv run run_all.py        # -> output/results.json + output/figures/*.png
```

Seeded, bit-for-bit reproducible. The first block is arithmetic on the byte format the runtime publishes, with the scalar arithmetic rate solved from the single throughput figure it reports so that every other row is a prediction; the second and third blocks are properties of stated models and no number in them is an estimate of any real frequency. Twenty-six invariant checks fail the run loudly if broken, among them: the computed artifact size matching the size the runtime reports without being told it; the predicted per-token streaming falling in the range the runtime describes; three techniques individually necessary and the fourth necessary only above a higher latency floor; no subset viable on the earlier console revision; the binding constraint migrating between 6 and 5 bits; the mixture reproducing the census median and transformative share; amplification rising with distance from the budget and absent when the budget barely binds; and the deployable fraction falling with stack depth to below one half by depth four.

## Build

```bash
uv run build.py          # -> paper/PAPER.pdf  (vendored canonical recipe)
```

Requires `pandoc` and `xelatex` on PATH. From the workspace you can also run
`papers build the-unreasonable-extensibility-of-computation`.

Part of [piatra-papers](https://github.com/piatra-institute). See the workspace
docs for the research and writing pipelines.
