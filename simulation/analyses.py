"""The unreasonable extensibility of computation, computed.

Three constructions. The first is arithmetic on a byte format that a
published runtime states, checked against the artifact size it reports.
The second and third are properties of explicitly stated models, and no
number in them is an estimate of any real frequency.

1. The technique lattice. A 90-million-parameter language model runs on a
   64 MB handheld console through four techniques: four-bit block-quantised
   weights, an eight-bit key-value cache, vector-unit kernels, and streaming
   the residual weights from storage. Every subset of the four is evaluated
   against the memory and latency budgets of the console, and against the
   32 MB budget of the console's earlier revision. Which subsets are viable,
   which techniques are individually necessary, and where the binding
   constraint moves as the weight representation narrows are computed.

2. Threshold amplification. Task families improve in large infrequent jumps
   while hardware improves smoothly. Under a budget with several resource
   dimensions a task is feasible only when every dimension is satisfied, so
   most improvement changes no capability predicate, and the crossings that
   do occur are burstier and more concentrated than the efficiency gains
   that cause them. The family-level improvement distribution is drawn from
   a mixture chosen to reproduce four published summary statistics of a
   113-family census and nothing else.

3. The deployable frontier. Known capability accumulates. Deployable
   capability requires every component of a stack to remain runnable, so it
   saturates rather than growing, at a level set by the arrival rate divided
   by the stack's failure hazard, and it turns over once arrivals slow. The
   depth at which rot outpaces discovery is computed.

Seeded, bit-for-bit reproducible. A failed invariant fails the run.
"""
from __future__ import annotations

import itertools

import numpy as np

SEED = 20260904
MB = 1024.0 * 1024.0


def _py(x):
    if isinstance(x, dict):
        return {k: _py(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_py(v) for v in x]
    if isinstance(x, (np.floating,)):
        return round(float(x), 6)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.ndarray):
        return [_py(v) for v in x.tolist()]
    if isinstance(x, float):
        return round(x, 6)
    return x


# ---------------------------------------------------------------------------
# 1. The technique lattice
# ---------------------------------------------------------------------------
# Every quantity in this block is either stated by the runtime's own
# documentation or arithmetic on the block format it specifies.

PARAMS = 91_100_000          # model card: 91.1M parameters
BLOCK_WEIGHTS = 32           # runtime: 32 weights per quantisation block
BLOCK_BYTES = 18             # runtime: one fp16 scale plus 32 four-bit weights
AUX_FP32_MB = 0.5            # runtime: norms, conv weights, Mamba tensors
REPORTED_FILE_MB = 52.0      # runtime: the whole file is 52 MB
CONSOLE_RAM_MB = 64.0        # supported revisions
LEGACY_RAM_MB = 32.0         # the 2004 revision, stated unsupported
RUNTIME_STATE_MB = 8.0       # runtime: about 8 MB of runtime state
CACHE_MB = 48.0              # runtime: 44 MB heap plus a 4 MB volatile partition
REPORTED_TOK_S = 0.55        # runtime: about 0.5 to 0.6 tokens per second
LATENCY_FLOOR_TOK_S = 0.4    # the operational threshold used throughout

# One stipulated machine parameter, and one calibrated. The storage
# bandwidth is stipulated and swept. The scalar arithmetic rate is not
# stipulated: it is solved so that the full four-technique stack reproduces
# the one performance figure the runtime reports, which leaves every other
# row of this block a prediction rather than a fit.
STICK_MB_S = 8.0             # sustained read from the storage card
VFPU_SPEEDUP = 3.2           # vector unit against the scalar path
OPS_PER_TOKEN = 2.0 * PARAMS  # one multiply and one add per weight per token
KV_FP16_MB = 6.0             # key-value cache at fp16, at the default context
USABLE_MB = 56.0             # 48 MB of cache plus 8 MB of runtime state
LEGACY_USABLE_MB = 24.0      # the same 8 MB of state in a 32 MB console


def _bytes_per_weight(bits: float) -> float:
    """Block-quantised storage: `bits` per weight plus one fp16 scale per block."""
    if bits >= 16:
        return bits / 8.0
    return (BLOCK_WEIGHTS * bits / 8.0 + 2.0) / BLOCK_WEIGHTS


def _weights_mb(bits: float) -> float:
    return PARAMS * _bytes_per_weight(bits) / MB


def _calibrate_scalar_rate() -> float:
    """Solve the scalar arithmetic rate from the reported throughput."""
    weights = _weights_mb(4)
    resident = min(weights, USABLE_MB - RUNTIME_STATE_MB)
    t_io = max(weights - resident, 0.0) / STICK_MB_S
    t_cpu = 1.0 / REPORTED_TOK_S - t_io
    return OPS_PER_TOKEN / (t_cpu * VFPU_SPEEDUP)


SCALAR_OPS_PER_S = _calibrate_scalar_rate()


def _latency(resident_mb: float, weights_mb: float, vfpu: bool) -> dict:
    """Seconds per token: streamed bytes over bandwidth, plus arithmetic."""
    streamed = max(weights_mb - resident_mb, 0.0)
    t_io = streamed / STICK_MB_S
    t_cpu = OPS_PER_TOKEN / (SCALAR_OPS_PER_S * (VFPU_SPEEDUP if vfpu else 1.0))
    return {"t_io": t_io, "t_cpu": t_cpu, "seconds_per_token": t_io + t_cpu,
            "tokens_per_second": 1.0 / (t_io + t_cpu),
            "binding": "io" if t_io > t_cpu else "compute"}


def run_lattice() -> dict:
    # --- the representation ladder ------------------------------------------
    ladder = []
    for name, bits in (("fp32", 32), ("fp16", 16), ("int8", 8), ("q4_block", 4)):
        w = _weights_mb(bits)
        ladder.append({
            "format": name, "bits": bits,
            "bytes_per_weight": _bytes_per_weight(bits),
            "weights_mb": w,
            "file_mb": w + AUX_FP32_MB,
            "over_cache_budget": w / (USABLE_MB - RUNTIME_STATE_MB),
            "over_legacy_budget": w / (LEGACY_USABLE_MB - RUNTIME_STATE_MB),
            "fits_resident": w <= (USABLE_MB - RUNTIME_STATE_MB),
        })
    q4 = next(r for r in ladder if r["format"] == "q4_block")
    fp32 = next(r for r in ladder if r["format"] == "fp32")
    # the computed file size against the size the runtime reports; the
    # residual is the embedded tokenizer, whose size the runtime does not state
    file_error = abs(q4["file_mb"] - REPORTED_FILE_MB) / REPORTED_FILE_MB
    implied_tokenizer_mb = REPORTED_FILE_MB - q4["file_mb"]

    # --- the subset lattice --------------------------------------------------
    # Four techniques. Weight quantisation sets the weight footprint; the
    # eight-bit cache halves the key-value cache; the vector unit multiplies
    # arithmetic throughput; streaming removes the requirement that the
    # weights be resident, at the cost of per-token reads.
    techniques = ("q4_weights", "int8_kv", "vfpu", "streaming")

    def _evaluate(subset, usable_mb: float, floor: float) -> dict:
        q4w = "q4_weights" in subset
        kv8 = "int8_kv" in subset
        vec = "vfpu" in subset
        strm = "streaming" in subset
        weights = _weights_mb(4 if q4w else 16)
        # the eight-bit cache returns half the fp16 cache to the weight cache
        resident_cap = max(usable_mb - RUNTIME_STATE_MB
                           - (0.0 if kv8 else KV_FP16_MB * 0.5), 0.0)
        if not strm and weights > resident_cap:
            return {"subset": sorted(subset), "fits": False, "runs": False,
                    "tokens_per_second": 0.0, "binding": "memory",
                    "resident_mb": 0.0, "weights_mb": weights,
                    "t_io": float("nan"), "t_cpu": float("nan")}
        resident = min(weights, resident_cap)
        lat = _latency(resident, weights, vec)
        return {"subset": sorted(subset), "fits": True,
                "runs": lat["tokens_per_second"] >= floor,
                "tokens_per_second": lat["tokens_per_second"],
                "binding": lat["binding"], "resident_mb": resident,
                "weights_mb": weights, "t_io": lat["t_io"], "t_cpu": lat["t_cpu"]}

    def _lattice(usable_mb: float, floor: float = LATENCY_FLOOR_TOK_S) -> dict:
        rows = []
        for k in range(len(techniques) + 1):
            for sub in itertools.combinations(techniques, k):
                rows.append(_evaluate(set(sub), usable_mb, floor))
        viable = [r for r in rows if r["runs"]]
        minimal = [r for r in viable
                   if not any(set(o["subset"]) < set(r["subset"]) for o in viable)]
        necessary = [t for t in techniques
                     if all(t in r["subset"] for r in viable)] if viable else list(techniques)
        return {"usable_mb": usable_mb, "floor": floor,
                "n_subsets": len(rows), "n_viable": len(viable),
                "viable": [r["subset"] for r in viable],
                "minimal_viable": [r["subset"] for r in minimal],
                "necessary_techniques": necessary,
                "best_tokens_per_second": max((r["tokens_per_second"] for r in rows),
                                              default=0.0),
                "rows": rows}

    supported = _lattice(USABLE_MB)
    legacy = _lattice(LEGACY_USABLE_MB)
    full = next(r for r in supported["rows"] if len(r["subset"]) == 4)
    # the latency floor at which the eight-bit cache becomes necessary
    kv_floor = None
    for f in np.arange(0.40, 1.01, 0.01):
        lat = _lattice(USABLE_MB, float(f))
        if "int8_kv" in lat["necessary_techniques"] and lat["n_viable"] > 0:
            kv_floor = round(float(f), 2)
            break
    # exact: the cache becomes necessary once the floor exceeds what the stack
    # runs at without it; the loop above only finds the next 0.01 above that
    kv_floor_exact = next(r["tokens_per_second"] for r in supported["rows"]
                          if r["subset"] == ["q4_weights", "streaming", "vfpu"])
    # sensitivity of the supported-console verdict to the stipulated bandwidth
    bandwidth_rows = []
    global STICK_MB_S
    base_bw = STICK_MB_S
    for bw in [4.0, 8.0, 12.0, 20.0]:
        STICK_MB_S = bw
        lat = _lattice(USABLE_MB)
        bandwidth_rows.append({"stick_mb_s": bw, "n_viable": lat["n_viable"],
                               "necessary": lat["necessary_techniques"]})
    STICK_MB_S = base_bw

    # --- constraint migration ------------------------------------------------
    migration = []
    for bits in [16, 12, 10, 8, 6, 5, 4, 3, 2, 1]:
        w = _weights_mb(bits)
        resident = min(w, CACHE_MB)
        lat = _latency(resident, w, True)
        migration.append({"bits": bits, "weights_mb": w,
                          "streamed_mb": max(w - resident, 0.0),
                          "t_io": lat["t_io"], "t_cpu": lat["t_cpu"],
                          "tokens_per_second": lat["tokens_per_second"],
                          "binding": lat["binding"]})
    io_bound = [m for m in migration if m["binding"] == "io"]
    switch_bits = min((m["bits"] for m in io_bound), default=None)
    compute_bound = [m for m in migration if m["binding"] == "compute"]
    compute_bits = max((m["bits"] for m in compute_bound), default=None)
    floor_tok_s = 1.0 / (OPS_PER_TOKEN / (SCALAR_OPS_PER_S * VFPU_SPEEDUP))
    # the speed a perfect representation could reach, against the one measured
    headroom = floor_tok_s / full["tokens_per_second"]

    return {
        "params": PARAMS, "block_weights": BLOCK_WEIGHTS,
        "block_bytes": BLOCK_BYTES,
        "reported_file_mb": REPORTED_FILE_MB,
        "reported_tokens_per_second": REPORTED_TOK_S,
        "console_ram_mb": CONSOLE_RAM_MB, "legacy_ram_mb": LEGACY_RAM_MB,
        "cache_mb": CACHE_MB, "runtime_state_mb": RUNTIME_STATE_MB,
        "latency_floor_tok_s": LATENCY_FLOOR_TOK_S,
        "ladder": ladder,
        "q4_over_cache": q4["over_cache_budget"],
        "fp32_over_cache": fp32["over_cache_budget"],
        "q4_over_legacy": q4["over_legacy_budget"],
        "representation_gain": fp32["weights_mb"] / q4["weights_mb"],
        "computed_file_mb": q4["file_mb"],
        "file_size_relative_error": file_error,
        "implied_tokenizer_mb": implied_tokenizer_mb,
        "scalar_ops_per_s": SCALAR_OPS_PER_S,
        "scalar_mac_per_s_millions": SCALAR_OPS_PER_S / 1e6,
        "stick_mb_s": STICK_MB_S, "vfpu_speedup": VFPU_SPEEDUP,
        "int8_kv_necessary_above_floor": kv_floor,
        "int8_kv_necessary_above_floor_exact": kv_floor_exact,
        "bandwidth_sensitivity": bandwidth_rows,
        "streamed_mb_per_token": max(q4["weights_mb"]
                                     - (USABLE_MB - RUNTIME_STATE_MB), 0.0),
        "supported": {k: v for k, v in supported.items() if k != "rows"},
        "legacy": {k: v for k, v in legacy.items() if k != "rows"},
        "full_stack": {k: v for k, v in full.items() if k != "subset"},
        "migration": migration,
        "io_bound_at_or_above_bits": switch_bits,
        "compute_bound_at_or_below_bits": compute_bits,
        "compute_floor_tok_s": floor_tok_s,
        "headroom_from_perfect_representation": headroom,
    }


# ---------------------------------------------------------------------------
# 2. Threshold amplification
# ---------------------------------------------------------------------------
# The family-level improvement-rate distribution is a three-component mixture
# whose parameters are chosen to reproduce four published summary statistics of
# a 113-family census: just under half the families show little or no
# improvement, 14 percent exceed a thousand percent a year, the median family
# improves 15 percent a year, and 30 percent improve faster than hardware.
# Nothing else about the mixture is estimated, and the hardware rate is not
# stipulated: it is read off as the seventieth percentile of the mixture and
# reported so that its plausibility can be judged.

N_FAMILIES = 113
YEARS = 40
STEPS_PER_YEAR = 12
SHARE_FLAT = 0.48
SHARE_TRANSFORMATIVE = 0.14
FLAT_MAX = 0.15
MID_SHIFT = 0.15
MID_MU, MID_SIGMA = np.log(0.35), 0.8
TRANS_BASE, TRANS_SIGMA = 10.0, 0.6
IMPROVEMENTS_PER_FAMILY = 1.44      # census: 276 algorithms over 113 families
DIMENSIONS = ("time", "memory")
COST_SIGMA = 1.0
OVER_BUDGET_MEDIANS = (2.0, 5.0, 20.0)
HEADLINE_OVER_BUDGET = 5.0
NEW_DEVICE_BUDGET_FACTOR = 10.0


def _draw_rates(n: int, rng) -> np.ndarray:
    u = rng.random(n)
    r = np.empty(n)
    flat = u < SHARE_FLAT
    trans = u >= 1.0 - SHARE_TRANSFORMATIVE
    mid = ~flat & ~trans
    r[flat] = rng.uniform(0.0, FLAT_MAX, flat.sum())
    r[mid] = MID_SHIFT + rng.lognormal(MID_MU, MID_SIGMA, mid.sum())
    r[trans] = TRANS_BASE * np.exp(np.abs(rng.normal(0.0, TRANS_SIGMA,
                                                     trans.sum())))
    return r


def _gini(x: np.ndarray) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * (idx * x).sum()) / (n * x.sum()) - (n + 1) / n)


def _one_world(rates, over_budget: float, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    n, T, D = len(rates), YEARS * STEPS_PER_YEAR, len(DIMENSIONS)
    total_gain = (1.0 + rates) ** YEARS
    n_jumps = 1 + rng.poisson(IMPROVEMENTS_PER_FAMILY, n)
    jump_times = [np.sort(rng.integers(0, T, k)) for k in n_jumps]
    jump_dims = [rng.integers(0, D, k) for k in n_jumps]
    cost = rng.lognormal(np.log(over_budget), COST_SIGMA, (n, D))

    fixed = cost.copy()
    events = np.zeros(T, dtype=int)
    crossings = np.zeros(T, dtype=int)
    logeff = np.zeros(T)
    invisible = 0
    per_family = np.zeros(n, dtype=int)
    feasible_now = (fixed <= 1.0).all(axis=1)
    curve = np.zeros(T, dtype=int)
    ever = feasible_now.copy()
    for t in range(T):
        for f in range(n):
            hits = np.nonzero(jump_times[f] == t)[0]
            if hits.size == 0:
                continue
            per_jump = total_gain[f] ** (1.0 / len(jump_times[f]))
            for h in hits:
                fixed[f, jump_dims[f][h]] /= per_jump
                events[t] += 1
                logeff[t] += np.log(per_jump)
            now = bool((fixed[f] <= 1.0).all())
            if now and not feasible_now[f]:
                feasible_now[f] = True
                ever[f] = True
                crossings[t] += 1
                per_family[f] += 1
            else:
                invisible += hits.size
        curve[t] = int(feasible_now.sum())

    new_feasible = int(((cost <= NEW_DEVICE_BUDGET_FACTOR).all(axis=1)).sum())
    overtake = next((t for t in range(T) if curve[t] > new_feasible), -1)
    ann_cross = crossings.reshape(YEARS, STEPS_PER_YEAR).sum(axis=1)
    ann_logeff = logeff.reshape(YEARS, STEPS_PER_YEAR).sum(axis=1)

    def _cv(x):
        mu = float(np.mean(x))
        return float(np.std(x) / mu) if mu > 0 else float("nan")

    order = np.argsort(-per_family)
    top = order[:max(1, n // 10)]
    return {
        "over_budget_median": over_budget,
        "initial_feasible": int(((cost <= 1.0).all(axis=1)).sum()),
        "n_events": int(events.sum()), "n_crossings": int(crossings.sum()),
        "invisible_share": invisible / max(int(events.sum()), 1),
        "cv_annual_crossings": _cv(ann_cross),
        "cv_annual_logefficiency": _cv(ann_logeff),
        "burstiness_ratio": _cv(ann_cross) / _cv(ann_logeff),
        "gini_annual_crossings": _gini(ann_cross),
        "gini_annual_logefficiency": _gini(ann_logeff),
        "top_decile_crossing_share": float(
            per_family[top].sum() / max(per_family.sum(), 1)),
        "never_crossed_share": float((~ever).mean()),
        "feasible_end": int(curve[-1]),
        "new_device_feasible": new_feasible,
        "overtake_year": (overtake / STEPS_PER_YEAR) if overtake >= 0 else None,
        "annual_crossings": ann_cross.tolist(),
        "annual_logefficiency": ann_logeff.tolist(),
        "feasible_curve": curve[::STEPS_PER_YEAR].tolist(),
    }


def run_thresholds() -> dict:
    rng = np.random.default_rng(SEED + 1)
    rates = _draw_rates(N_FAMILIES, rng)
    hw_rate = float(np.quantile(rates, 0.70))
    calibration = {
        "median_rate": float(np.median(rates)),
        "share_at_or_below_flat_max": float((rates <= FLAT_MAX).mean()),
        "share_transformative": float((rates >= TRANS_BASE).mean()),
        "share_above_hardware": float((rates > hw_rate).mean()),
        "implied_hardware_rate": hw_rate,
        "design_share_flat": SHARE_FLAT,
        "design_share_transformative": SHARE_TRANSFORMATIVE,
    }
    worlds = [_one_world(rates, m, SEED + 20 + int(m))
              for m in OVER_BUDGET_MEDIANS]
    head = next(w for w in worlds
                if w["over_budget_median"] == HEADLINE_OVER_BUDGET)
    return {
        "n_families": N_FAMILIES, "years": YEARS,
        "dimensions": list(DIMENSIONS),
        "calibration": calibration,
        "rates_quantiles": {str(q): float(np.quantile(rates, q))
                            for q in (0.1, 0.25, 0.5, 0.75, 0.9, 0.99)},
        "worlds": worlds,
        "headline": head,
        "new_device_budget_factor": NEW_DEVICE_BUDGET_FACTOR,
    }




# ---------------------------------------------------------------------------
# 3. The deployable frontier
# ---------------------------------------------------------------------------
# Knowledge accumulates. Deployment requires every component of a stack to
# remain runnable at once, so the deployable stock is governed by a survival
# process rather than by an arrival process. Components fail with an annual
# hazard and are occasionally revived by someone re-porting them.

DECAY_YEARS = 60
ARRIVALS_PER_YEAR = 6.0
WANE_TAU = 12.0              # years; the decline of interest in a platform
HAZARD = 0.03                # annual probability a component stops running
REVIVAL = 0.12               # annual probability a dead component is restored
DEPTHS = (1, 2, 3, 5, 8, 12)
REPLICATES = 40
PSP_STACK_DEPTH = 5          # firmware, toolchain, runtime, weights, tokenizer
MEAN_IMPROVEMENT_INTERVAL = YEARS / IMPROVEMENTS_PER_FAMILY


def _stationary_alive(h: float, r: float) -> float:
    return r / (r + h) if (r + h) > 0 else 0.0


def _critical_hazard(d: int, interval: float) -> float:
    """The per-component annual hazard at which a stack of depth d has a
    half-life equal to the mean interval between improvements in its field.
    Above it, an artifact rots faster than the knowledge it embodies grows."""
    return 1.0 - 0.5 ** (1.0 / (d * interval))


def _artifact_half_life(h: float, d: int) -> float:
    """Years until an unrevived stack of depth d is more likely dead than not."""
    survive = (1.0 - h) ** d
    if survive >= 1.0:
        return float("inf")
    return float(np.log(0.5) / np.log(survive))


def _one_run(depth: int, hazard: float, revival: float, waning: bool,
             seed: int):
    rng = np.random.default_rng(seed)
    known, deployable = [], []
    alive = np.zeros((0, depth), dtype=bool)
    n_known = 0
    for y in range(DECAY_YEARS):
        rate = (ARRIVALS_PER_YEAR * np.exp(-y / WANE_TAU) if waning
                else ARRIVALS_PER_YEAR)
        # existing components fail, dead ones may be revived
        if alive.size:
            fail = rng.random(alive.shape) < hazard
            rev = rng.random(alive.shape) < revival
            alive = np.where(alive, ~fail, rev)
        k = rng.poisson(rate)
        if k:
            alive = np.vstack([alive, np.ones((k, depth), dtype=bool)])
            n_known += k
        known.append(n_known)
        deployable.append(int(alive.all(axis=1).sum()) if alive.size else 0)
    return np.array(known, dtype=float), np.array(deployable, dtype=float)


def _simulate(depth: int, hazard: float, revival: float, waning: bool,
              seed: int) -> dict:
    """Average over replicates so the curves are not read off one history."""
    kns, deps = [], []
    for r in range(REPLICATES):
        k, d = _one_run(depth, hazard, revival, waning, seed + 1000 * r)
        kns.append(k)
        deps.append(d)
    kn = np.mean(kns, axis=0)
    dep = np.mean(deps, axis=0)
    peak = int(np.argmax(dep))
    return {
        "depth": depth, "hazard": hazard, "revival": revival,
        "waning": waning,
        "known_end": int(kn[-1]), "deployable_end": int(dep[-1]),
        "ratio_at_10": float(dep[9] / kn[9]) if kn[9] else 0.0,
        "ratio_at_20": float(dep[19] / kn[19]) if kn[19] else 0.0,
        "ratio_at_40": float(dep[39] / kn[39]) if kn[39] else 0.0,
        "peak_year": peak, "peak_deployable": float(dep[peak]),
        "end_over_peak": float(dep[-1] / dep[peak]) if dep[peak] else 0.0,
        "known": kn.tolist(), "deployable": dep.tolist(),
    }


def run_decay() -> dict:
    by_depth = [_simulate(d, HAZARD, REVIVAL, False, SEED + 100 + d)
                for d in DEPTHS]
    waning = [_simulate(d, HAZARD, REVIVAL, True, SEED + 300 + d)
              for d in (1, PSP_STACK_DEPTH, 12)]
    psp = next(w for w in by_depth if w["depth"] == PSP_STACK_DEPTH)
    psp_wane = next(w for w in waning if w["depth"] == PSP_STACK_DEPTH)

    alive1 = _stationary_alive(HAZARD, REVIVAL)
    analytic = [{"depth": d, "stationary_fraction": alive1 ** d,
                 "half_life_years": _artifact_half_life(HAZARD, d),
                 "critical_hazard": _critical_hazard(
                     d, MEAN_IMPROVEMENT_INTERVAL)}
                for d in DEPTHS]
    half_depth = next((d for d in range(1, 40) if alive1 ** d < 0.5), None)
    # the depth at which an unrevived stack dies faster than its field improves
    rot_depth = next((d for d in range(1, 60)
                      if _artifact_half_life(HAZARD, d)
                      < MEAN_IMPROVEMENT_INTERVAL), None)
    crit1 = _critical_hazard(1, MEAN_IMPROVEMENT_INTERVAL)
    crit_stack = _critical_hazard(PSP_STACK_DEPTH, MEAN_IMPROVEMENT_INTERVAL)

    hazard_sweep = []
    for h in (0.005, 0.01, 0.03, 0.06, 0.12):
        a = _stationary_alive(h, REVIVAL)
        hazard_sweep.append({"hazard": h,
                             "stationary_fraction_depth5": a ** PSP_STACK_DEPTH,
                             "half_life_depth5": _artifact_half_life(
                                 h, PSP_STACK_DEPTH)})

    return {
        "years": DECAY_YEARS, "arrivals_per_year": ARRIVALS_PER_YEAR,
        "hazard": HAZARD, "revival": REVIVAL,
        "stack_depth": PSP_STACK_DEPTH,
        "mean_improvement_interval_years": MEAN_IMPROVEMENT_INTERVAL,
        "improvements_per_family": IMPROVEMENTS_PER_FAMILY,
        "stationary_alive_component": alive1,
        "analytic": analytic,
        "depth_below_half": half_depth,
        "rot_outpaces_discovery_depth": rot_depth,
        "critical_hazard_depth1": crit1,
        "critical_hazard_stack": crit_stack,
        "critical_interval_years_depth1": 1.0 / crit1,
        "critical_interval_years_stack": 1.0 / crit_stack,
        "hazard_sweep": hazard_sweep,
        "by_depth": [{k: v for k, v in w.items()
                      if k not in ("known", "deployable")} for w in by_depth],
        "waning": [{k: v for k, v in w.items()
                    if k not in ("known", "deployable")} for w in waning],
        "psp_depth_curve": {"known": psp["known"],
                            "deployable": psp["deployable"]},
        "psp_waning_curve": {"known": psp_wane["known"],
                             "deployable": psp_wane["deployable"]},
        "psp_sustained": {k: v for k, v in psp.items()
                          if k not in ("known", "deployable")},
        "psp_waning": {k: v for k, v in psp_wane.items()
                       if k not in ("known", "deployable")},
    }


# ---------------------------------------------------------------------------
# orchestration and invariants
# ---------------------------------------------------------------------------
def run() -> dict:
    lat = run_lattice()
    thr = run_thresholds()
    dec = run_decay()

    sup, leg = lat["supported"], lat["legacy"]
    cal = thr["calibration"]
    worlds = thr["worlds"]
    d5 = next(w for w in dec["by_depth"] if w["depth"] == PSP_STACK_DEPTH)
    d12w = next(w for w in dec["waning"] if w["depth"] == 12)

    checks = {
        # 1. the technique lattice
        "computed_file_size_matches_the_artifact":
            lat["file_size_relative_error"] < 0.06,
        "residual_is_a_plausible_tokenizer":
            0.0 < lat["implied_tokenizer_mb"] < 5.0,
        "four_bit_weights_still_exceed_the_cache": lat["q4_over_cache"] > 1.0,
        "full_precision_exceeds_the_cache_sevenfold":
            lat["fp32_over_cache"] > 7.0,
        "representation_gain_is_the_block_ratio":
            abs(lat["representation_gain"] - 4.0 / 0.5625) < 1e-9,
        "calibration_reproduces_reported_throughput":
            abs(lat["full_stack"]["tokens_per_second"]
                - lat["reported_tokens_per_second"]) < 1e-9,
        "predicted_streaming_is_a_few_megabytes":
            0.0 < lat["streamed_mb_per_token"] < 5.0,
        "three_techniques_are_individually_necessary":
            sorted(sup["necessary_techniques"])
            == ["q4_weights", "streaming", "vfpu"] and sup["n_viable"] == 2,
        "the_eighth_bit_cache_buys_speed_not_feasibility":
            "int8_kv" not in sup["necessary_techniques"]
            and lat["int8_kv_necessary_above_floor"] is not None,
        "no_subset_runs_on_the_earlier_revision": leg["n_viable"] == 0,
        "the_binding_constraint_migrates":
            lat["io_bound_at_or_above_bits"] == 6
            and lat["compute_bound_at_or_below_bits"] == 5,
        "perfect_compression_buys_under_ten_percent":
            lat["headroom_from_perfect_representation"] < 1.10,

        # 2. threshold amplification
        "mixture_reproduces_the_census_median":
            abs(cal["median_rate"] - 0.15) < 0.03,
        "mixture_reproduces_the_transformative_share":
            abs(cal["share_transformative"] - 0.14) < 0.04,
        "implied_hardware_rate_is_in_the_benchmark_range":
            0.2 < cal["implied_hardware_rate"] < 0.6,
        "most_improvement_changes_no_capability":
            all(w["invisible_share"] > 0.8 for w in worlds),
        "burstiness_rises_with_distance_from_the_budget": all(
            worlds[i + 1]["burstiness_ratio"] > worlds[i]["burstiness_ratio"]
            for i in range(len(worlds) - 1)),
        "no_amplification_when_the_budget_barely_binds":
            worlds[0]["burstiness_ratio"] < 1.0,
        "crossings_concentrate_as_the_budget_binds": all(
            worlds[i + 1]["top_decile_crossing_share"]
            > worlds[i]["top_decile_crossing_share"]
            for i in range(len(worlds) - 1)),
        "old_hardware_overtakes_new_only_in_the_demanding_regime":
            worlds[0]["overtake_year"] is None
            and worlds[1]["overtake_year"] is None
            and worlds[2]["overtake_year"] is not None,

        # 3. the deployable frontier
        "stationary_deployability_falls_with_depth": all(
            dec["analytic"][i + 1]["stationary_fraction"]
            < dec["analytic"][i]["stationary_fraction"]
            for i in range(len(dec["analytic"]) - 1)),
        "half_the_stack_is_undeployable_by_depth_four":
            dec["depth_below_half"] == 4,
        "deployable_is_under_half_of_known_at_stack_depth":
            d5["ratio_at_40"] < 0.5,
        "critical_hazard_falls_with_depth": all(
            dec["analytic"][i + 1]["critical_hazard"]
            < dec["analytic"][i]["critical_hazard"]
            for i in range(len(dec["analytic"]) - 1)),
        "the_stack_needs_century_scale_components":
            dec["critical_interval_years_stack"] > 100.0,
        "waning_arrivals_turn_the_frontier_over":
            d12w["peak_year"] < 15 and d12w["end_over_peak"] < 0.5,
    }
    bad = [k for k, v in checks.items() if not v]
    if bad:
        raise AssertionError("invariants failed: " + ", ".join(bad))

    return _py({"lattice": lat, "thresholds": thr, "decay": dec,
                "checks": {k: bool(v) for k, v in checks.items()},
                "seed": SEED})
