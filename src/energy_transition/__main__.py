"""Run the full pipeline: raw data -> clean tables -> results -> figures -> dashboard.

    python -m energy_transition            # rebuild everything
    python -m energy_transition --check    # also fail if results differ from the committed versions
"""

import argparse
import json
import subprocess
import sys

from . import analysis, build, config, dashboard, figures, models


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if regenerated results differ from git")
    args = parser.parse_args(argv)

    tables = build.build()
    result = analysis.run(tables["world_bank_wide"], tables["un_sdg_7_2_1"])
    model_result = models.run(tables["world_bank_wide"])
    result["tables"]["model_coefficients"] = model_result["coefficients"]
    result["summary"]["models"] = model_result["summary"]

    config.RESULTS.mkdir(exist_ok=True)
    for name, df in result["tables"].items():
        df.to_csv(config.RESULTS / f"{name}.csv", index=False, float_format="%.4f")
    summary = json.dumps(result["summary"], indent=2, default=float)
    (config.RESULTS / "summary.json").write_text(summary + "\n", encoding="utf-8")

    figures.make_all(result["tables"], config.FIGURES, model_result)
    dashboard.build(tables["world_bank_wide"], result, config.DOCS / "index.html")
    print(summary)

    if args.check:
        diff = subprocess.run(["git", "status", "--porcelain", "--", "data/clean", "results", "docs/index.html"],
                              cwd=config.ROOT, capture_output=True, text=True, check=False).stdout
        if diff.strip():
            print("Outputs changed compared with the committed versions:\n" + diff)
            return 1
        print("Outputs match the committed versions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
