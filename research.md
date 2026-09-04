# Research

Findings tiered by distance from the claim. T1 primary, T2 authoritative secondary, T3 reference, T4 lead only. Everything cited is T1 or T2 and was checked against Crossref, the arXiv listing, the publisher's own document, or the artifact itself during this pass. Seed claims are marked where the record corrected them.

## The case: what the artifact actually is

**T1. The LLMPSP runtime.** The repository README was retrieved in full and read. It states: a custom runtime running Falcon-H1-Tiny-90M-Instruct, "quantized to 4 bits", on "the PSP's 333 MHz MIPS CPU"; "on a PSP-3000 it generates about 0.5 - 0.6 tokens per second"; supported hardware is "PSP-2000/PSP-3000/Street/GO running CFW", and "a PSP-1000 only has 32 MB of RAM and it won't work". The model is described as a hybrid in which "each of the 24 layers runs grouped-query attention (8 query heads, 2 KV heads) *and* a Mamba2 recurrent branch in parallel". The weight format is "Q4_0-style - 32 weights per block, one fp16 scale, 18 bytes per block", with rows independently addressable; norms, conv weights and the Mamba tensors "stay fp32", about 0.5 MB in total; the tokenizer's 32,768 pieces are embedded in the file. On memory: "the whole thing is 52 MB, which doesn't fit in a 64 MB console alongside ~8 MB of runtime state", so the runtime allocates correctness-critical state first, then "44 MB of heap plus the 4 MB volatile partition the firmware isn't using, in 256 KB blocks and streams the last few MB from the memory stick per token". The key-value cache "is int8 with a float scale per head, which roughly halves it versus fp16". The kernels "run on the PSP's VFPU vector unit rather than the scalar FPU". And the honest quality note: the model "can answer basic questions" and "generate poems, short stories" but is "not really useful for anything".

**T1. Falcon-H1-Tiny-90M-Instruct model card**, Technology Innovation Institute. Confirms 90M parameters (91.1M in the safetensors index) and a "Hybrid Transformers + Mamba architecture".

**Seed corrections.** The seed asserted the PSP-1000 point and the 64 MB requirement; both are confirmed verbatim from the repository and are carried in the paper's first paragraph rather than buried. The seed described the model as running at "approximately 0.5-0.6 generated tokens per second on a PSP-3000", which is exactly what the README says. Nothing in the seed's account of the case needed correction, which is unusual; what needed adding is the arithmetic, since the seed treats the case as a vignette and never computes anything from the byte format the repository publishes.

**T1. Gu, A., and Dao, T. (2023). Mamba. arXiv:2312.00752.** The selective state-space architecture whose recurrent branch the model uses; cited for what the architecture is rather than for a performance claim.

## Measured algorithmic progress

**T1. Sherry, Y., and Thompson, N. C. (2021). How fast do algorithms improve? *Proceedings of the IEEE* 109(11), 1768--1777.** The full text was retrieved and read. Verified numbers: 57 textbooks and more than 1137 research papers; 113 algorithm families, 110 in the rate analysis; an average of eight algorithms per family, 276 initial algorithms and improvements, 1.44 improvements after the initial algorithm in each family; "around half of all algorithm families experience little or no improvement" while "14% experience transformative improvements"; at n = 1 thousand only 18% of families improved faster than hardware, at n = 1 million 30%, at n = 1 billion 43%; the median family improved 6% a year at n = 1 thousand, 15% at n = 1 million and 28% at n = 1 billion; and at n = 1.06 trillion the median family improved faster than hardware. Also verified, and central to this paper's second result: "While Moore's law led to hardware improvements happening smoothly over time, Fig. 2 shows that algorithms experience large, but infrequent improvements." The simulation's family-rate mixture is calibrated to four of these numbers and to nothing else, and the jump rate is taken from the 1.44 figure.

**T1. Koch, T., Berthold, T., Pedersen, J., and Vanaret, C. (2022). Progress in mathematical programming solvers from 2001 to 2020. *EURO Journal on Computational Optimization* 10, 100031.** Verified abstract: hardware got about 20 times faster; algorithms improved by about 9 for linear programming and around 50 for mixed-integer programming; total speed-ups of about 180 and 1,000. The sentence this paper leans on is the last: "these numbers have a very high variance and they considerably underestimate the progress made on the algorithmic side: many problem instances can nowadays be solved within seconds, which the old codes are not able to solve within any reasonable time." That is a field reporting that its own instrument cannot see the threshold crossings, which is the paper's second result stated by its own subjects.

**T1. Hernandez, D., and Brown, T. B. (2020). Measuring the algorithmic efficiency of neural networks. arXiv:2005.04305.** Verified: the floating-point operations needed to train a classifier to AlexNet-level ImageNet performance fell by a factor of 44 between 2012 and 2019, an efficiency doubling every 16 months over seven years, against an 11-fold improvement Moore's law would have given over the same period.

**T1. Erdil, E., and Besiroglu, T. (2022). Algorithmic progress in computer vision. arXiv:2212.05153.** Verified: algorithmic improvements were roughly as important as compute scaling; compute-augmenting innovations halve compute requirements every nine months, with a 95 percent interval of 4 to 25 months.

**T1. Ho, A., Besiroglu, T., Erdil, E., et al. (2024). Algorithmic progress in language models. arXiv:2403.05812.** Verified: over 200 evaluations on Wikitext and Penn Treebank spanning 2012 to 2023, the compute required to reach a set performance threshold halved approximately every 8 months, with a 95 percent interval of about 5 to 14 months.

**T2. Leiserson, C. E., et al. (2020). There's plenty of room at the Top. *Science* 368, eaam9744.** The argument that performance will increasingly come from software, algorithms and architecture rather than from transistor scaling.

**T2. Hennessy, J. L., and Patterson, D. A. (2019). A new golden age for computer architecture. *CACM* 62(2), 48--60.** And **T1. Moore, G. E. (1965/2006).** And **T2. Denning, P. J., and Lewis, T. G. (2017). Exponential laws of computing growth. *CACM* 60(1), 54--65.** The hardware baseline against which any software gain has to be read, and the reason that baseline is not a constant of nature.

## Universality, and why it is not the answer

**T1. Turing, A. M. (1937). On computable numbers, with an application to the Entscheidungsproblem. *Proceedings of the London Mathematical Society* s2-42(1), 230--265.** Note the locator: the paper is dated 1936 in most citations and appears in the 1937 volume.

**T1. Hartmanis, J., and Stearns, R. E. (1965). On the computational complexity of algorithms. *TAMS* 117, 285--306.** The move from computability to resource-bounded computability, which is the move this paper's formalism needs.

**T1. Blum, M. (1967). A machine-independent theory of the complexity of recursive functions. *JACM* 14(2), 322--336.** The speed-up theorem: there are computable functions for which every algorithm has an asymptotically faster one, so for those functions there is no best program and no final answer to what a machine can do with them. The seed missed this, and it is the strongest formal support the thesis has.

**T1. Rice, H. G. (1953). Classes of recursively enumerable sets and their decision problems. *TAMS* 74(2), 358--366.** And **T2. Li, M., and Vitányi, P. (2019). *An Introduction to Kolmogorov Complexity and Its Applications*, 4th ed. Springer.** Why the intrinsic feasible set of a machine is not merely unknown but uncomputable: the shortest program for a task is not computable, and nontrivial semantic properties of programs are undecidable.

**T1. Hutter, M. (2002). The fastest and shortest algorithm for all well-defined problems. *IJFCS* 13(3), 431--443.** The construction that is asymptotically optimal and useless in practice, which is the sharpest available illustration of the gap between the in-principle and the budgeted.

**T2. Aaronson, S. (2013). Why philosophers should care about computational complexity.** In *Computability: Turing, Gödel, Church, and Beyond*, 261--328. MIT Press. The argument that the resource bound, not computability, is where the philosophical content sits.

## Programmability and its philosophy

**T1. Moor, J. H. (1985). What is computer ethics? *Metaphilosophy* 16(4), 266--275.** Logical malleability: computers can be shaped to any activity characterisable through inputs, outputs and connecting logical operations. The closest precursor, and synchronic where this paper is diachronic.

**T1. Piccinini, G. (2007). Computing mechanisms. *Philosophy of Science* 74(4), 501--526.** And **T1. Piccinini, G. (2008). Computers. *Pacific Philosophical Quarterly* 89(1), 32--73.** The mechanistic account that blocks the pancomputationalist objection: a system computes in virtue of its causal organisation, not in virtue of an interpretation someone assigns it.

**T1. Wigner, E. P. (1960). The unreasonable effectiveness of mathematics in the natural sciences. *CPAM* 13(1), 1--14.** The title's source, and a disanalogy the paper has to state rather than borrow.

**T1. Halevy, A., Norvig, P., and Pereira, F. (2009). The unreasonable effectiveness of data. *IEEE Intelligent Systems* 24(2), 8--12.** The previous borrowing of the same formula, and the argument that behaviour can come from data rather than from a designed model.

## Mechanisms

**T1. Massalin, H. (1987). Superoptimizer: a look at the smallest program. *SIGARCH Computer Architecture News* 15(5), 122--126.** Instruction sequences as objects of search: the lowest layer of the stack is also a place where later discovery happens.

**T1. Jacob, B., et al. (2018). Quantization and training of neural networks for efficient integer-arithmetic-only inference. *CVPR*, 2704--2713.** And **T1. Frantar, E., and Alistarh, D. (2022). Optimal Brain Compression. *NeurIPS 35*, 4475--4488.** The representation mechanism, in the form the console runtime uses.

**T1. Hooker, S. (2021). The hardware lottery. *CACM* 64(12), 58--65.** The causal arrow this paper does not run: which algorithms succeed is itself shaped by which hardware exists. Cited as the reason the hardware-software separation is an experimental control rather than a metaphysical division.

## Limits

**T1. Wolpert, D. H., and Macready, W. G. (1997). No free lunch theorems for optimization. *IEEE Transactions on Evolutionary Computation* 1(1), 67--82.** Why no claim of general algorithmic superiority is available.

**T1. Landauer, R. (1961). Irreversibility and heat generation in the computing process. *IBM Journal of Research and Development* 5(3), 183--191.** The physical floor.

## Decay

**T1. Rothenberg, J. (1995). Ensuring the longevity of digital documents. *Scientific American* 272(1), 42--47.** The original statement that preserving the bits is not preserving the capability.

**T1. Rosenthal, D. S. H., Robertson, T., Lipkis, T., Reich, V., and Morabito, S. (2005). Requirements for digital preservation systems. *D-Lib Magazine* 11(11).** The threat model for long-lived digital systems, which is where the hazard-and-depth model comes from.

**T1. Guttenbrunner, M., and Rauber, A. (2012). A measurement framework for evaluating emulators for digital preservation. *ACM TOIS* 30(2), 1--28.** Emulation as something that can be measured rather than assumed, and the reason the paper treats emulation as a partial substitute for a surviving toolchain.

## Sources considered and dropped

- The seed proposed Karpathy's "Software 2.0" as the reference for learned artifacts as behaviour-bearing objects. It is a blog essay, T4 by the pipeline's rules, and Halevy, Norvig and Pereira carry the same point in a peer-reviewed venue. It is not cited.
- The seed cited "Wiggershaus, N. (2025), Physical Programmability" through a ResearchGate listing. The record could not be resolved to a stable locator during this pass, and Piccinini carries the programmability point. Not cited.
- The seed cited Carbin (2019) on approximate learned software through a Dagstuhl listing without a resolvable title. Not cited.
- PSP hardware specifications were taken only from the runtime's own documentation, which states the clock and the memory sizes it depends on. No console specification sheet was used, because none could be verified to a primary source in this pass.

## Discipline notes

The lattice block is arithmetic on a published byte format, with one free parameter, the scalar arithmetic rate, solved from the one throughput figure the runtime reports; every other row of that block is therefore a prediction, and one of them, that the runtime must stream about 0.9 MB per token, can be read against the repository's own description of streaming "the last few MB". The threshold and decay blocks are properties of stated models. The paper marks which is which at every use, and never presents a modelled number as a measurement.
