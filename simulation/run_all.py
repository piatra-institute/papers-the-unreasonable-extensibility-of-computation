"""Orchestrator: reproduces every number and all three figures in the paper.

    cd simulation
    uv run run_all.py

Writes output/results.json and output/figures/*.png. Seeded; a rerun
reproduces every number bit for bit. A failed invariant fails the run.
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

    from figures import plot_lattice, plot_thresholds, plot_decay
    plot_lattice(results, str(OUT / "figures" / "lattice.png"))
    plot_thresholds(results, str(OUT / "figures" / "thresholds.png"))
    plot_decay(results, str(OUT / "figures" / "decay.png"))

    L, T, D = results["lattice"], results["thresholds"], results["decay"]
    print("lattice:")
    print(f"  four-bit weights {L['ladder'][3]['weights_mb']:.1f} MB against a "
          f"{L['cache_mb']:.0f} MB cache, {L['q4_over_cache']:.3f} of budget; "
          f"full precision {L['fp32_over_cache']:.2f}")
    print(f"  computed file {L['computed_file_mb']:.2f} MB against "
          f"{L['reported_file_mb']:.0f} reported; residual "
          f"{L['implied_tokenizer_mb']:.2f} MB")
    print(f"  streaming predicted at {L['streamed_mb_per_token']:.2f} MB per "
          f"token; {L['supported']['n_viable']} of "
          f"{L['supported']['n_subsets']} subsets run, necessary "
          f"{L['supported']['necessary_techniques']}")
    print(f"  earlier revision: {L['legacy']['n_viable']} subsets run, best "
          f"{L['legacy']['best_tokens_per_second']:.3f} tokens per second")
    print(f"  storage-bound at or above {L['io_bound_at_or_above_bits']} bits; "
          f"perfect compression buys "
          f"{L['headroom_from_perfect_representation']:.3f}x")
    print("thresholds:")
    c = T["calibration"]
    print(f"  census fit: median {c['median_rate']:.3f}, transformative "
          f"{c['share_transformative']:.3f}, implied hardware rate "
          f"{c['implied_hardware_rate']:.3f}")
    for w in T["worlds"]:
        print(f"  {w['over_budget_median']:>4.0f}x over budget: invisible "
              f"{w['invisible_share']:.3f}, burstiness "
              f"{w['burstiness_ratio']:.3f}, top decile "
              f"{w['top_decile_crossing_share']:.3f}, overtake "
              f"{w['overtake_year']}")
    print("decay:")
    print(f"  deployable share of known at forty years, by depth: "
          + ", ".join(f"{w['depth']}:{w['ratio_at_40']:.2f}"
                      for w in D["by_depth"]))
    print(f"  a five-deep stack needs each component to last "
          f"{D['critical_interval_years_stack']:.0f} years against the "
          f"{D['mean_improvement_interval_years']:.0f}-year interval between "
          f"improvements")
    print("checks:", f"{sum(results['checks'].values())}/{len(results['checks'])}")
    print("wrote", OUT / "results.json")


if __name__ == "__main__":
    main()
