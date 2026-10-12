"""Paper tables (CSV + LaTeX) generated mechanically from build.py outputs. No number is typed by hand.
    python scripts/analysis/tables.py <analysis_dir> <out_tables_dir> [--paper-tables paper/tables]
Labels expected in <analysis_dir>: A_exp0 (Exp0), C_exp1 (Exp1, 350 q), C_exp2 (Exp2), and optionally
F_exp1 (confirmatory Exp1, stage full)."""
import csv
import json
import shutil
import sys
from pathlib import Path

A = Path(sys.argv[1])
OUT = Path(sys.argv[2])
PAPER = Path(sys.argv[sys.argv.index("--paper-tables") + 1]) if "--paper-tables" in sys.argv else None
OUT.mkdir(parents=True, exist_ok=True)
DSN = {"musique": "MuSiQue", "2wikimultihopqa": "2Wiki", "hotpotqa": "HotpotQA", "hover": "HoVer", "fever": "FEVER"}
REPS = ["R0", "R1", "R2", "R3", "R4", "R4P", "R5"]


def rows(name):
    p = A / name
    return list(csv.DictReader(open(p))) if p.exists() and p.stat().st_size else []


def num(x, nd=2, sign=False):
    if x in ("", None):
        return "--"
    v = float(x)
    return f"{v:+.{nd}f}" if sign else f"{v:.{nd}f}"


def ci(x, nd=2):
    if not x:
        return "--"
    a, b = json.loads(x)
    return f"[{a:+.{nd}f}, {b:+.{nd}f}]"


def emit(name, header, body, caption, label, colspec, star=False, size="\\small", csv_rows=None):
    env = "table*" if star else "table"
    tex = [f"\\begin{{{env}}}[t]", "\\centering", size, f"\\begin{{tabular}}{{{colspec}}}", "\\toprule",
           " & ".join(header) + " \\\\", "\\midrule"]
    for r in body:
        tex.append("\\midrule" if r == "MID" else " & ".join(r) + " \\\\")
    tex += ["\\bottomrule", "\\end{tabular}", f"\\caption{{{caption}}}", f"\\label{{{label}}}", f"\\end{{{env}}}"]
    (OUT / f"{name}.tex").write_text("\n".join(tex) + "\n")
    with open(OUT / f"{name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in (csv_rows or [r for r in body if r != "MID"]):
            w.writerow(r)
    if PAPER:
        PAPER.mkdir(parents=True, exist_ok=True)
        shutil.copy(OUT / f"{name}.tex", PAPER / f"{name}.tex")


def contrast_rows(label, settings=("A",), datasets=("musique", "2wikimultihopqa"), contrasts=("R1-R0", "R5-R1", "R4-R5"),
                  metric_for=lambda ds: "em" if ds not in ("hover", "fever") else "verdict_acc"):
    out = []
    co = rows(f"{label}_contrasts.csv")
    for ds in datasets:
        for s in settings:
            for c in contrasts:
                for r in co:
                    if (r["dataset"] == ds and r["setting"] == s and r["edge_stratum"] == "all" and r["contrast"] == c
                            and r["metric"] == metric_for(ds)):
                        out.append(r)
    return out


# T-primary: pilot (C_exp1, Protocol A) primary contrasts
body = []
for r in contrast_rows("C_exp1"):
    body.append([DSN[r["dataset"]], r["contrast"].replace("-", "$-$"), r["n_paired"], num(r["delta"], sign=True), ci(r["ci"]),
                 f"{r['n_b_better']}/{r['n_a_better']}", r["n_identical_evidence"],
                 f"{num(r['informative_delta'], sign=True)} ({r['informative_n']})", num(r["coverage_delta"], sign=True)])
emit("tab_pilot_primary", ["Data", "Contrast", "$n$", "$\\Delta$EM", "95\\% CI", "+/$-$", "Ident.", "Inform. $\\Delta$ ($n$)", "$\\Delta$Cov."],
     body, "Exploratory pilot: primary contrasts under Protocol~A (identical facts). $\\Delta$EM is the paired difference "
     "(EM of the first-named minus the second-named representation); +/$-$ counts questions where only the first-named / "
     "only the second-named is correct; "
     "Ident.\\ counts byte-identical evidence pairs; Inform.\\ is the estimate on the remaining pairs; $\\Delta$Cov.\\ is the "
     "paired difference in answered rate. Source: \\texttt{C\\_exp1\\_contrasts.csv}.", "tab:pilot-primary", "@{}llrrlrrlr@{}",
     star=True)

# T-confirmatory
conf = contrast_rows("F_exp1")
if conf:
    body = []
    for r in conf:
        body.append([DSN[r["dataset"]], r["contrast"].replace("-", "$-$"), r["n_paired"], num(r["delta"], 3, sign=True),
                     ci(r["ci"], 3), num(r["p_boot"], 3), num(r["p_holm"], 3), f"{r['n_b_better']}/{r['n_a_better']}",
                     r["n_identical_evidence"], f"{num(r['informative_delta'], 3, sign=True)}", num(r["coverage_delta"], 3, sign=True),
                     "yes" if r.get("equivalent_within_0.02") == "True" else "no"])
    emit("tab_confirmatory", ["Data", "Contrast", "$n$", "$\\Delta$EM", "95\\% CI", "$p$", "$p_{\\text{Holm}}$", "+/$-$", "Ident.",
                              "Inform. $\\Delta$", "$\\Delta$Cov.", "Equiv."],
         body, "Confirmatory test of the six pre-specified primary contrasts (Protocol~A, EM, disjoint sample; "
         "\\texttt{docs/CONFIRMATORY\\_PROTOCOL.md}). $p$: two-sided paired bootstrap; $p_{\\text{Holm}}$: Holm-adjusted over the "
         "six tests. Equiv.: 90\\% CI inside $\\pm0.02$ (pre-specified secondary check). Source: \\texttt{F\\_exp1\\_contrasts.csv}.",
         "tab:confirmatory", "@{}llrrlrrrrrrl@{}", star=True, size="\\footnotesize")

# T-absolute (Protocol A, all datasets, pilot 350)
ab = rows("C_exp1_absolute.csv")
body = []
for ds in ["musique", "2wikimultihopqa", "hotpotqa", "hover", "fever"]:
    rr = {r["representation"]: r for r in ab if r["dataset"] == ds and r["setting"] == "A"}
    if not rr:
        continue
    cells = [DSN[ds]]
    for rep in REPS:
        r = rr.get(rep)
        cells.append("--" if not r or r["score"] in ("", None) else f"{float(r['score']):.2f} ({float(r['coverage']):.2f})")
    body.append(cells)
emit("tab_absolute_A", ["Data"] + REPS, body,
     "Exploratory pilot, Protocol~A: EM (QA) or verdict accuracy (HoVer, FEVER), with coverage (answered rate) in parentheses, "
     "for the same facts in seven representations. $n$=100 (MuSiQue, 2Wiki) or 50. R3 is unavailable without a reasoning order. "
     "Source: \\texttt{C\\_exp1\\_absolute.csv}.", "tab:absolute", "@{}l" + "c" * len(REPS) + "@{}", star=True, size="\\footnotesize")

# T-protocol B accounting + EM (primary datasets; R0 R1 R5 R4)
acc = rows("C_exp1_protocol_accounting.csv")
abs_by = {(r["dataset"], r["setting"], r["representation"]): r for r in ab}
body = []
for ds in ["musique", "2wikimultihopqa"]:
    for sett in ["A", "B 1.0x per_representation", "B 1.0x shared", "B 0.5x per_representation", "B 0.5x shared"]:
        for rep in ["R0", "R1", "R5", "R4"]:
            for r in acc:
                kv = dict(x.split("=", 1) for x in r["condition"].split(",") if "=" in x)
                s = "A" if kv.get("protocol") == "A" else f"B {kv.get('budget', '').replace('content:', '')}x {kv.get('policy')}"
                if r["dataset"] == ds and s == sett and kv.get("representation") == rep:
                    a = abs_by.get((ds, sett, rep), {})
                    body.append([DSN[ds], sett.replace("per_representation", "per-rep.").replace("x ", "$\\times$ "), rep,
                                 num(r.get("facts_kept_frac")) if r.get("facts_kept_frac") else "1.00",
                                 num(r["overhead_tokens"], 0), num(r["evidence_tokens"], 0),
                                 num(r.get("answer_bearing_dropped")) if r.get("answer_bearing_dropped") else "0.00",
                                 num(r["answer_in_evidence"]), num(a.get("score")), num(a.get("coverage"))])
    body.append("MID")
body = body[:-1]
emit("tab_budget", ["Data", "Setting", "Rep.", "Kept", "Ovh.", "Tok.", "Ans.\\ drop", "Ans.\\ in ev.", "EM", "Cov."], body,
     "Information accounting under Protocol~A and Protocol~B (budget $\\beta\\times$ the content tokens of the fact set). "
     "Kept: fraction of facts shown; Ovh./Tok.: mean overhead and evidence tokens; Ans.\\ drop: answer-bearing facts cut per "
     "question; Ans.\\ in ev.: answer string present in the block. Source: \\texttt{C\\_exp1\\_protocol\\_accounting.csv}, "
     "\\texttt{C\\_exp1\\_absolute.csv}.", "tab:budget", "@{}lllrrrrrrr@{}", star=True, size="\\footnotesize")

# T-exp0
e0 = rows("A_exp0_absolute.csv")
body = []
for ds in ["musique", "2wikimultihopqa"]:
    for r in e0:
        if r["dataset"] == ds:
            body.append([DSN[ds], r["system"], num(r["score"]), ci(json.dumps(json.loads(r["score_ci"]))), num(r["f1"]),
                         num(r["coverage"]), num(r["evidence_tokens"], 0), num(r["n_units_mean"], 1), num(r["answer_in_evidence"]),
                         num(r["latency_s_mean"])])
    body.append("MID")
body = body[:-1]
emit("tab_exp0", ["Data", "Sys.", "EM", "95\\% CI", "F1", "Cov.", "Tok.", "Units", "Ans.\\ in ev.", "Lat.\\,(s)"], body,
     "Experiment~0, retrieved evidence (exploratory, $n$=100 per dataset). Tok.: mean evidence tokens; Units: items shown; "
     "Lat.: answer-generation latency (claim extraction for B2--B4 is not included). B4 is our reconstruction of EG-RAG. "
     "Source: \\texttt{A\\_exp0\\_absolute.csv}.", "tab:exp0", "@{}llrlrrrrrr@{}", star=True, size="\\footnotesize")

# T-exp2 (QA datasets, rate 0.4; label-preserving deltas or answer-change/abstention)
e2 = rows("C_exp2_sensitivity.csv")
body = []
for ds in ["musique", "2wikimultihopqa", "hotpotqa"]:
    for rep in ["R1", "R4"]:
        for P in ["P1", "P2", "P3", "P4", "P5", "P6"]:
            for r in e2:
                if r["dataset"] == ds and r["representation"] == rep and r["perturbation"] == P and float(r["rate"]) == 0.4:
                    par = json.loads(r["params"]) if r["params"] else {}
                    lab = P + ("" if not par else " " + ",".join(str(v) for v in par.values()))
                    pres = int(r["n_label_preserved"])
                    body.append([DSN[ds], rep, lab, r["n_pairs"], str(pres),
                                 num(r["delta_label_preserved"], sign=True) if pres else "--",
                                 ci(r["ci"]) if pres else "--", num(r["answer_changed_rate"]),
                                 f"{num(r['abstention_rate_base'])}$\\to${num(r['abstention_rate'])}"])
        body.append("MID")
body = body[:-1]
emit("tab_exp2", ["Data", "Rep.", "Perturbation", "$n$", "Lab.-pres.", "$\\Delta$EM", "95\\% CI", "Ans.\\ changed", "Abstention"], body,
     "Experiment~2 at rate 0.4 (exploratory). $\\Delta$EM is computed only on label-preserving records without introduced "
     "answers (Lab.-pres.); P1 and P6 can remove the answer, so only answer-change and abstention rates are given. "
     "Source: \\texttt{C\\_exp2\\_sensitivity.csv}.", "tab:exp2", "@{}lllrrrlrl@{}", star=True, size="\\footnotesize")
print("tables written to", OUT)

# T-confirmatory secondary contrasts (descriptive; outside the Holm family) with abstention decomposition
if conf:
    dec = {(r["dataset"], r["contrast"]): r for r in rows("F_exp1_decomposition_exploratory.csv")}
    body = []
    for r in contrast_rows("F_exp1", contrasts=("R2-R1", "R3-R5", "R4P-R4")):
        body.append([DSN[r["dataset"]], r["contrast"].replace("-", "$-$"), r["n_paired"], num(r["delta"], 3, sign=True),
                     ci(r["ci"], 3), r["n_identical_evidence"], num(r["coverage_delta"], 3, sign=True)])
    emit("tab_confirm_secondary", ["Data", "Contrast", "$n$", "$\\Delta$EM", "95\\% CI", "Ident.", "$\\Delta$Cov."], body,
         "Secondary contrasts on the confirmatory sample (pre-specified as secondary; not part of the tested family, so "
         "descriptive). Source: \\texttt{F\\_exp1\\_contrasts.csv}.", "tab:confirm-secondary", "@{}llrrlrr@{}")
    body = []
    for (ds, con), r in sorted(dec.items()):
        if con not in ("R1-R0", "R5-R1", "R4-R5", "R4P-R4"):
            continue
        body.append([DSN[ds], con.replace("-", "$-$"), num(r["delta_primary_metric"], 3, sign=True),
                     num(r["contrib_both_answered"], 3, sign=True),
                     f"{num(float(r['contrib_only_b_answered']) + float(r['contrib_only_a_answered']), 3, sign=True)}",
                     f"{r['n_only_a_answered']}/{r['n_only_b_answered']}", r["n_neither_answered"]])
    emit("tab_decomposition", ["Data", "Contrast", "$\\Delta$EM", "both ans.", "one abstains", "abst.\\ only first / only second",
                               "neither"], body,
         "Exploratory decomposition of each paired EM difference on the confirmatory sample (added after the confirmatory "
         "result). \\emph{both ans.}: contribution of questions answered under both representations; \\emph{one abstains}: "
         "contribution of questions answered under only one. The columns sum to $\\Delta$EM. Source: "
         "\\texttt{F\\_exp1\\_decomposition\\_exploratory.csv}.", "tab:decomposition", "@{}llrrrrr@{}", size="\\footnotesize")
    pr = rows("F_exp1_r4p_relations_exploratory_paired.csv")
    body = [[DSN[r["dataset"]], "yes" if "has" in r["subset"] else "no", r["n_questions"], num(r["abstention_R4"]),
             num(r["abstention_R4P"]), num(r["em_R4"]), num(r["em_R4P"])] for r in pr]
    emit("tab_r4p_contradictions", ["Data", "R4P shows CONTRADICTS", "$n$", "Abst.\\ R4", "Abst.\\ R4P", "EM R4", "EM R4P"], body,
         "Exploratory: the same questions under derived relations (R4) and predicted relations (R4P), split by whether "
         "the predicted block contains at least one \\texttt{CONTRADICTS} line (an input property). Source: "
         "\\texttt{F\\_exp1\\_r4p\\_relations\\_exploratory\\_paired.csv}.", "tab:r4p", "@{}lcrrrrr@{}", size="\\footnotesize")
print("extra tables written")
