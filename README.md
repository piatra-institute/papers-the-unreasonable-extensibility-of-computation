# The Unreasonable Extensibility of Computation

What a Fixed Machine Can Do, and When It Is Possible to Know.

A handheld games console released in 2004 can now generate text locally. A published runtime runs a 90-million-parameter model on a Sony PSP with 64 MB of memory and a 333 MHz processor, at about 0.55 tokens per second, with no network connection. The hardware is unchanged; what changed is the available software and trained parameters. We treat capability as a relation among a machine, an artifact, a task, a budget and a quality threshold, so the set of tasks a fixed machine can perform depends on the date. Three results follow. First, arithmetic on the runtime's published byte format shows that full-precision weights need 7.24 times the console's weight cache and four-bit quantisation still leaves the model at 1.02 times the cache, so 0.87 MB per token must be streamed; of the sixteen combinations of the runtime's four techniques, 2 reach 0.4 tokens per second, three techniques are individually necessary, and on the 32 MB revision of the console none runs. Second, in a model calibrated to a census of 113 algorithm families, between 0.83 and 0.89 of improvement events change no capability, and the burstiness of capability crossings relative to efficiency gains rises from 0.84 to 1.67 as the budget becomes more restrictive. Third, deployable capability requires every component of a software stack to remain runnable, so it saturates at 0.43 of known capability for a five-component stack; for such a stack to last as long as the mean interval between improvements in its field, each component would need a mean life of 201 years.

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

Requires `pandoc` and `xelatex` on PATH. From the workspace you can also run `papers build the-unreasonable-extensibility-of-computation`.

Part of [piatra-papers](https://github.com/piatra-institute). See the workspace docs for the research and writing pipelines.
