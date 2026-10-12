"""Print discordant examples from build.py output for manual error analysis.
    python scripts/analysis/examples.py <analysis_dir> <label> <dataset:B-A> [--evidence]"""
import json
import sys
from pathlib import Path

d, label, key = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
show_ev = "--evidence" in sys.argv
ex = json.loads((d / f"{label}_discordant_examples.json").read_text())[key]
b, a = key.split(":")[1].split("-")
print(f"{key}: {len(ex)} discordant questions")
for e in ex:
    print(f"--- {e['question_uid']} | stratum={e.get('edge_stratum')} | {e['question']} | gold={e['gold']}")
    for r in (a, b):
        print(f"   {r}: em={e[r]['em']} answer={e[r]['answer']!r} failure={e[r]['failure']}")
        if show_ev:
            print("      " + e[r]["evidence"].replace("\n", "\n      ")[:2500])
