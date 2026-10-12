"""Print compact views of the analysis CSVs (no computation; reads build.py outputs).
    python scripts/analysis/show.py <analysis_dir> <label> [absolute|contrasts|accounting|taxonomy|subgroups|exp0|exp2]"""
import csv
import json
import sys
from pathlib import Path

d, label, what = Path(sys.argv[1]), sys.argv[2], sys.argv[3]


def f(x, nd=3):
    if x in ("", None):
        return "--"
    try:
        return f"{float(x):.{nd}f}"
    except ValueError:
        return x


def ci(x):
    if not x:
        return "--"
    a, b = json.loads(x)
    return f"[{a:+.3f},{b:+.3f}]"


def rows(name):
    return list(csv.DictReader(open(d / f"{label}_{name}.csv")))


if what == "absolute":
    for r in rows("absolute"):
        c = json.loads(r["score_ci"]) if r["score_ci"] else [0, 0]
        print(f"{r['dataset'][:6]:6s} {r['setting']:26s} {r['representation']:4s} n={r['n_questions']:>3s} "
              f"{r['metric']} {f(r['score'])} [{c[0]:.2f},{c[1]:.2f}] F1 {f(r['f1'])} cov {f(r['coverage'])} "
              f"ev_tok {f(r['evidence_tokens'], 0):>5s} ovh {f(r['overhead_tokens'], 0):>4s} "
              f"ans_in_ev {f(r['answer_in_evidence'])} suff {f(r['evidence_sufficient'])} lat {f(r['latency_s_mean'], 2)}")
elif what == "contrasts":
    flt = sys.argv[4] if len(sys.argv) > 4 else ""
    for r in rows("contrasts"):
        if flt and flt not in json.dumps(r):
            continue
        print(f"{r['dataset'][:6]:6s} {r['setting']:26s} {r['edge_stratum'][:28]:28s} {r['contrast']:7s} {r['metric']:3s} "
              f"n={r['n_paired']:>3s} d={f(r['delta']):>6s} {ci(r['ci'])} p={f(r['p_boot'])} "
              f"+{r['n_b_better']}/-{r['n_a_better']} ident={r['n_identical_evidence']} "
              f"inf(n={r['informative_n']}: {f(r['informative_delta'])} {ci(r['informative_ci'])}) "
              f"cov {f(r['coverage_delta'])} mcn={f(r['mcnemar_p_secondary'])} dz={f(r['d_z'], 2)}")
elif what == "accounting":
    for r in rows("protocol_accounting"):
        print(f"{r['dataset'][:6]:6s} {r['condition'][:95]:95s} facts {f(r['facts_shown'], 1)} ev {f(r['evidence_tokens'], 0)} "
              f"ovh {f(r['overhead_tokens'], 0)} kept {f(r.get('facts_kept_frac'))} req_drop {f(r.get('required_dropped'), 2)} "
              f"ans_drop {f(r.get('answer_bearing_dropped'), 2)} fit {f(r.get('required_fit_budget_frac'))} "
              f"suff {f(r['evidence_sufficient'])} aie {f(r['answer_in_evidence'])}")
elif what == "taxonomy":
    for r in rows("error_taxonomy"):
        print({k: v for k, v in r.items() if v not in ("", None) and k != "run"})
elif what == "subgroups":
    for r in rows("subgroups"):
        print(f"{r['dataset'][:6]:6s} {r['subgroup']:30s} {r['contrast']:6s} n={r['n_paired']:>3s} a={f(r['score_a'])} "
              f"b={f(r['score_b'])} d={f(r['delta'])} {ci(r['ci'])}")
elif what == "exp0":
    for r in rows("absolute"):
        c = json.loads(r["score_ci"]) if r["score_ci"] else [0, 0]
        print(f"{r['dataset'][:6]:6s} {r['system']} n={r['n_questions']} {r['metric']} {f(r['score'])} [{c[0]:.2f},{c[1]:.2f}] "
              f"F1 {f(r['f1'])} cov {f(r['coverage'])} ev_tok {f(r['evidence_tokens'], 0)} units {f(r['n_units_mean'], 1)} "
              f"supp_cov {f(r['support_coverage'])} aie {f(r['answer_in_evidence'])} lat {f(r['latency_s_mean'], 2)}")
    for r in rows("contrasts"):
        print(f"{r['dataset'][:6]:6s} {r['contrast']} {r['metric']} n={r['n_paired']} d={f(r['delta'])} {ci(r['ci'])} "
              f"p={f(r['p_boot'])} ident={r['n_identical_evidence']} cov {f(r['coverage_delta'])}")
elif what == "exp2":
    for r in rows("sensitivity"):
        print(f"{r['dataset'][:6]:6s} {r['representation']:3s} {r['perturbation']} {r['params'][:30]:30s} rate {r['rate']} "
              f"n={r['n_pairs']:>3s} pres={r['n_label_preserved']:>3s} intro={r['n_answer_introduced']} "
              f"d={f(r['delta_label_preserved']):>6s} {ci(r['ci'])} chg {f(r['answer_changed_rate'])} "
              f"abst {f(r['abstention_rate_base'])}->{f(r['abstention_rate'])} eff {r['label_effects']}")
