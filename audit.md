# Audit

Dated log of editorial passes and verification runs. Newest first.

## 2026-09-23 — structured-evidence migration

Structured-evidence migration (references and claims).
- references.yaml: 33 CSL entries. 31 resolved through doi.org content negotiation (27 Crossref DOIs, 4 arXiv DOIs through DataCite) and checked for year, title and authors; capitalised or annotated record titles (Hutter, Moor, Piccinini 2008, Moore, Wigner, Sherry and Thompson) restored to published form; Aaronson chapter given its book title and editors. technology2026 (Hugging Face model card) and thatblend2026 (GitHub repository) entered by hand from their URLs. In-text author-year citations converted to Pandoc [@id] syntax; the legacy list replaced by the citeproc-rendered list (Chicago author-date).
- Correction: "14 percent of the remainder improve transformatively" -> "14 percent of all families"; Sherry and Thompson (2021) report 14% of the families, and the simulation calibrates to that share.
- Correction: "reproduces the reported file size to within 5 percent" -> "5.1 percent"; results.json /lattice/file_size_relative_error = 0.05058.
- Correction: "the seven configurations the lattice predicts should fail" -> "fourteen"; 16 subsets less 2 viable (the model evaluates 6 that fit memory but miss the floor and 8 that do not fit).
- claims.yaml: 106 claims (71 computation, 22 source, 3 definition, 3 assumption, 7 interpretation). Every simulation number in abstract and body is bound to results.json. Source claims checked against the LLMPSP README, Sherry and Thompson's full text, Moor's article, and abstracts from Crossref/DataCite/OpenAlex (Hernandez and Brown, Erdil and Besiroglu, Ho et al., Koch et al., Leiserson et al., Blum, Wolpert and Macready, Piccinini, Guttenbrunner and Rauber).
- Unverified, not bound: Hutter (2002) "with a constant that makes it unusable" (the abstract states a factor of 5 plus additive terms; the size of the constant is not in the retrievable abstract); Hooker (2021) on hardware shaping which algorithms are refined (abstract too brief); Rothenberg (1995), Rosenthal et al. (2005), Landauer (1961), Halevy et al. (2009), Massalin (1987) statements (no abstract retrieved or interpretive use).
- Run: extensibility (uv run python run_all.py); results.json reproduced byte for byte.
- metadata claims_target: claim-ledger.

## 2026-09-22 — prose revision

Prose revision against the house standards. No computation or conclusion changed.
  - Manuscript rewritten paragraph by paragraph; abstract cut from about 490 to 257 words, prose from about 5,050 to about 3,800 words. 'rather than' from twenty-five instances to none; meta-commentary and epigrams removed; section titles made descriptive.
  - Stated more precisely: the floor above which the 8-bit cache becomes necessary is 0.456 tokens per second (the text gave 0.46, the next 0.01 grid step), now computed exactly in `simulation/analyses.py`; the overtaking time is 25.4 years (the text said 'in year 25').
  - Figure 2(b) axis-label overlap fixed; all figure titles rewritten; figures regenerated (26 invariants pass).
  - Build now carries an input-hash manifest. References and claims remain in their legacy state (inline bibliography, no bound ledger), unchanged by this pass.

## 2026-09-04 — v1, complete

Scope: the whole paper, simulation, and evidence base, from the seed chat to the built PDF.

Changes:
  - Sources: 33 entries, each verified against Crossref, the arXiv listing, the publisher's own document, or the artifact itself. Three seed sources were dropped rather than cited: Karpathy's "Software 2.0" is a blog essay and Halevy, Norvig and Pereira carry the same point in a peer-reviewed venue; "Physical Programmability" could not be resolved to a stable locator; and the Carbin reference had no resolvable title. Blum's speed-up theorem, Rice's theorem, Li and Vitányi, Hutter, and Hartmanis and Stearns were added, none of which the seed had, and together they are what turns the thesis from a rhetorical observation into a statement about an uncomputable gap.
  - The case was verified from the artifact, not from the seed's summary of it. The LLMPSP README was retrieved and read in full, and every stated property of the console demonstration in the paper is quoted or computed from it: the block format of 32 weights and one 16-bit scale per 18 bytes, the 52 MB file, the 44 MB heap plus 4 MB volatile partition, the roughly 8 MB of runtime state, the 8-bit key-value cache, the vector-unit kernels, the 0.5 to 0.6 tokens per second, and the statement that a PSP-1000 will not work. The model card was read for the parameter count and the hybrid architecture. The seed's account of the case needed no correction, which is unusual; what it needed was arithmetic, since it treats the artifact as a vignette and computes nothing from the byte format the repository publishes.
  - Sherry and Thompson was retrieved in full rather than summarised. The verified figures are 57 textbooks, 1137 papers, 113 families, 276 algorithms, 1.44 improvements per family after the first, around half with little or no improvement, 14 percent transformative, and 18, 30 and 43 percent faster than hardware at problem sizes of one thousand, one million and one billion with medians of 6, 15 and 28 percent a year. The mixture in the second block is calibrated to four of these and to nothing else. Their observation that hardware improved smoothly while algorithms "experience large, but infrequent improvements" is the jump structure the model uses, and Koch et al.'s admission that their own speedup factors "considerably underestimate the progress made on the algorithmic side" because instances now solved in seconds could not be solved at all is the threshold effect stated by the field itself.
  - Simulation design notes. The lattice block has exactly one free parameter and it is not stipulated: the scalar arithmetic rate is solved so the full stack reproduces the reported throughput, which makes the streaming volume, the subset lattice, the earlier-revision verdict and the constraint migration predictions rather than fits. The predicted 0.87 MB of streaming per token can be read against the repository's independent description of streaming "the last few MB". An early version of the block set the resident capacity to the console's memory minus runtime state, which made streaming unnecessary and contradicted the artifact; correcting it to the 48 MB cache the runtime actually allocates reproduced the artifact's own reasoning and made three techniques necessary instead of two.
  - The threshold block was rewritten once. The first version reported a single regime and produced four crossings out of 113 families, which was degenerate. Sweeping the distance from the budget instead produced the finding the single regime hid: amplification is conditional, with a burstiness ratio of 0.84 when the budget barely binds, and the honest null is reported and made an invariant.
  - The decay block's hazard and revival rates were retuned once. The first choice implied that 80 percent of all software is broken at any moment, which is not credible and made the depth comparison degenerate. The headline was then moved off the stipulated rates entirely and onto a derived quantity, the critical hazard at which a stack's half-life equals the mean interval between improvements in its field, which is 0.0246 a year at depth one and 0.00498 at depth five and does not depend on the choice.
  - Voice: the draft came in at 0 errors and 7 negate-pivot review candidates, all rewritten as positive declaratives; a later pass cleared 2 more and converted 11 spelled measurements to numerals. A section on the borrowed Wigner formula and its disanalogy was added after the first read of the draft, which also brought Wigner, Halevy et al., Massalin, Jacob et al., Frantar and Alistarh, Leiserson et al. and Piccinini 2008 into the text rather than leaving them unused in the bibliography.
  - Two dates the seed asserted and the sources do not support were removed from argumentative positions. The console's release year and the year of its second revision could not be verified to a primary source in this pass, so the paper states that the release dates are scene-setting and that nothing computed depends on them.

Verification:
  - voice: 0 errors, 0 review-candidates
  - refs: 33 in-text keys, 33 bib entries, 0 missing, 0 unused
  - claims: 584 sim values, 59 decimal claims in prose, 0 without a match
  - simulation: 26/26 invariants
  - build: 14 pages, no missing-character warnings
  - check => PASS

Figure pass: the first render put the budget labels on top of the bars in the lattice figure, overlapped the two regime labels in the migration panel, cut the third panel's title, and ran the preservation annotation through the curve it was pointing at. All four were repositioned and the PDF was read in full before publication.
