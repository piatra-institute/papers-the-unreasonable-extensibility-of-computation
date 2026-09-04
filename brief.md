# Brief

## Question

A 2026 runtime puts a 90-million-parameter language model on a Sony PSP, a handheld from 2004 whose later revisions carry 64 MB of RAM and a 333 MHz MIPS processor. The processor did not change. What changed is the stock of algorithms, representations, runtimes, and trained parameters that can be brought to it. When, then, is it possible to know what a computer can do? And is the answer to that question quantitative, or only rhetorical?

## Claim

The capability of a fixed machine is a relation, not a property: it is indexed to a budget, a quality threshold, and a date. Making that indexation formal, and then computing with it, yields three results the verbal version does not reach.

1. Capability is a conjunction, and the arithmetic of the PSP case says exactly which conjunction. Four-bit weights alone leave the model six times over the console's cacheable memory; the four techniques the runtime actually uses are jointly sufficient and individually necessary, no proper subset of them fits, and on the 32 MB PSP-1000 no subset of them fits at all. The same software, one hardware revision earlier, produces no capability. Compression also relocates the binding constraint rather than removing it: below a computable bit-width the system stops being memory-bound and becomes throughput-bound, and further compression buys nothing.
2. Threshold amplification is measurable, and it makes capability far burstier than the efficiency that produces it. Under a multi-dimensional budget most efficiency improvements change no capability predicate at all, capability crossings are markedly more concentrated in time than the underlying log-efficiency gains that cause them, and a small minority of task families contributes most of the crossings. The field's standard instrument, the speedup ratio, is blind to exactly this: Koch et al. note that their measured factors considerably understate progress because many instances are now solved in seconds that the old codes could not solve at all.
3. The frontier that matters is not the one that grows. Known capability accumulates monotonically; deployable capability is the intersection of everything a stack depends on still being runnable, so it saturates rather than growing, at a level that falls with the depth of the dependency stack, and it turns over and declines once arrivals slow. The PSP stack is five components deep. Preserving the device preserves none of this.

## Kind

Formal-model. Ships a simulation; `claims_target: results.json`. The PSP arithmetic is computed from the byte format the runtime states and validated against the artifact size it reports; the census-shaped and adoption-style results are properties of stated models, labelled as such.

## Cornerstone literature that must be engaged

- Universality and its budget-blindness: Turing; Hartmanis and Stearns; Rice; Blum's speed-up theorem, which says some functions have no best algorithm; Hutter; Li and Vitányi on the uncomputability of the shortest program; Aaronson on why the resource bound is the philosophically loaded part.
- Programmability and its philosophy: Moor's logical malleability, the closest precursor; Piccinini on computing mechanisms and on computers, against interpretivism.
- Measured algorithmic progress: Sherry and Thompson's 113-family census, which is the calibration and the corrective; Hernandez and Brown; Erdil and Besiroglu; Ho et al.; Koch et al. on solvers; Leiserson et al.; Hennessy and Patterson and Moore and Denning and Lewis for the hardware baseline.
- Mechanisms: Massalin on superoptimization; Jacob et al. and Frantar and Alistarh on quantization; Gu and Dao on the state-space architecture the PSP model uses; Halevy, Norvig and Pereira and the learned-artifact question.
- Limits: Wolpert and Macready; Landauer; Hooker's hardware lottery, which is the reverse causal arrow.
- Decay: Rothenberg; Rosenthal et al.; Guttenbrunner and Rauber on emulation as measurement.
- Wigner, for the title, and for the disanalogy that has to be stated rather than borrowed.

## Discipline

The paper does not claim that software gives hardware new physical powers, that the PSP became intelligent, or that algorithmic progress is general. Sherry and Thompson's census says half of all families improve barely at all, and the paper's own model is calibrated to reproduce that. Every quantity is either arithmetic on a stated byte format or a property of an explicitly stated model, and the difference is marked at every use.
