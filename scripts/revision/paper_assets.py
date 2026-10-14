"""Revision-1 paper tables and figures, generated only from result CSVs (no hand-typed numbers).
    python scripts/revision/paper_assets.py <revision_dir> <paper_dir>
<revision_dir> contains audit/, controls/, analysis/, retrieval/, noabst/ (whatever exists)."""
import csv
import json
import re
import sys
from pathlib import Path

R = Path(sys.argv[1])
P = Path(sys.argv[2])
(P / "tables").mkdir(parents=True, exist_ok=True)
(P / "figures").mkdir(parents=True, exist_ok=True)
DSN = {"musique": "MuSiQue", "2wikimultihopqa": "2Wiki", "hotpotqa": "HotpotQA"}
R2 = R.parent / "revision2"  # revision-2 outputs


def rows(p):
    p = R / p
    return list(csv.DictReader(open(p))) if p.exists() and p.stat().st_size else []


def rows2(p):
    p = R2 / p
    return list(csv.DictReader(open(p))) if p.exists() and p.stat().st_size else []


def f(x, nd=3, sign=True):
    if x in ("", None):
        return "--"
    return f"{float(x):+.{nd}f}" if sign else f"{float(x):.{nd}f}"


def ci(x, nd=3):
    if not x:
        return "--"
    a, b = json.loads(x) if isinstance(x, str) else x
    return f"[{a:+.{nd}f}, {b:+.{nd}f}]"


def emit(name, header, body, caption, label, colspec, star=True, size="\\footnotesize"):
    # let long source paths in captions break after each slash
    caption = re.sub(r"\\texttt\{([^}]*/[^}]*)\}", lambda m: "\\texttt{" + m.group(1).replace("/", "/\\allowbreak ") + "}", caption)
    env = "table*" if star else "table"
    t = [f"\\begin{{{env}}}[t]", "\\centering", size, "\\begin{adjustbox}{max width=\\linewidth}", f"\\begin{{tabular}}{{{colspec}}}",
         "\\toprule", " & ".join(header) + " \\\\", "\\midrule"]
    for r in body:
        t.append("\\midrule" if r == "MID" else " & ".join(r) + " \\\\")
    t += ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", f"\\caption{{{caption}}}", f"\\label{{{label}}}", f"\\end{{{env}}}"]
    (P / "tables" / f"{name}.tex").write_text("\n".join(t) + "\n")
    with open(P / "tables" / f"{name}.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows([r for r in body if r != "MID"])


# ------------------------------------------------------------------ fixed-order relation controls
CTRL = [("R4P_FO-R4P_FO_NC", "contradiction lines (on vs.\\ off), derived order"),
        ("R4P_FO-R4N_FO", "typed vs.\\ neutral labels for all lines, same pairs"),
        ("R4N_FO-R5", "neutral lines vs.\\ none (count/overhead only)"),
        ("R5P-R5", "predicted vs.\\ derived order, no lines"),
        ("R4P-R4P_FO", "predicted vs.\\ derived order, predicted lines"),
        ("R4P-R4", "original R4P$-$R4 (order and lines)")]
ctrl = {(r["dataset"], r["contrast"]): r for r in rows("controls/relation_control_effects.csv") if r.get("d_em")}
if ctrl:
    body = []
    for con, desc in CTRL:
        cells = [desc]
        for ds in ("2wikimultihopqa", "musique"):
            r = ctrl.get((ds, con))
            cells += ([f(r["d_em"]), ci(r["d_em_ci"]), f(r["d_abst"]), r["n_identical_prompts"]] if r else ["--"] * 4)
        body.append(cells)
        if con == "R4P_FO-R4P_FO_NC":
            # revision-2 targeted controls (B - A of an r2 contrast "A>B" = first minus second)
            c2 = {(r["dataset"], r["contrast"]): r for r in rows2("r2/controls2.csv") if r["stratum"] == "all"}
            for key, desc2 in (("R4P_FO_CN>R4P_FO", "contradiction label vs.\\ neutral label, those lines only"),
                               ("R4P_FO_NCPAD>R4P_FO", "contradiction lines vs.\\ equal-count filler lines")):
                cells2 = [desc2]
                for ds in ("2wikimultihopqa", "musique"):
                    r = c2.get((ds, key))
                    cells2 += ([f(r["d_em"]), ci(r["d_em_ci"]), f(r["d_abst"]), r["n_identical_prompts"]] if r else ["--"] * 4)
                if c2:
                    body.append(cells2)
    emit("tab_controls", ["Factor changed (first $-$ second)", "2Wiki $\\Delta$EM", "95\\% CI", "$\\Delta$Abst.", "Ident.",
                          "MuSiQue $\\Delta$EM", "95\\% CI", "$\\Delta$Abst.", "Ident."], body,
         "Fixed-order relation controls on the confirmatory questions (exploratory interventions designed after the confirmatory "
         "result; $n$=3{,}232 2Wiki, 1{,}744 MuSiQue). Each row changes one factor on identical facts. $\\Delta$Abst.: paired change in "
         "the abstention rate; Ident.: byte-identical prompt pairs (questions without contradiction lines for rows 1--3). Sources: "
         "\\texttt{revision/controls/relation\\_control\\_effects.csv}, \\texttt{revision2/r2/controls2.csv}.",
         "tab:controls", "@{}lrlrrrlrr@{}")
    strata = [r for r in rows("controls/relation_control_strata.csv")
              if r["contrast"] == "R4P_FO-R4P_FO_NC" and r["stratum"].startswith("n_contra_lines")]
    body = []
    for ds in ("2wikimultihopqa", "musique"):
        for r in strata:
            if r["dataset"] == ds:
                body.append([DSN[ds], r["stratum"].split("=")[1], r["n"], f(r["d_em"]), ci(r["d_em_ci"]), f(r["d_abst"]), ci(r["d_abst_ci"])])
        body.append("MID")
    emit("tab_controls_strata", ["Data", "Contradiction lines", "$n$", "$\\Delta$EM", "95\\% CI", "$\\Delta$Abst.", "95\\% CI"], body[:-1],
         "Effect of showing the predicted \\texttt{CONTRADICTS} lines (R4P\\_FO$-$R4P\\_FO\\_NC) by the number of such lines in the "
         "prompt (exploratory). With no contradiction lines the two prompts are identical. Source: "
         "\\texttt{revision/controls/relation\\_control\\_strata.csv}.", "tab:controls-strata", "@{}llrrlrl@{}", star=True)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "font.family": "serif", "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    labels = ["contradiction lines on vs. off", "typed vs. neutral labels\n(all lines, same pairs)", "neutral lines vs. none",
              "predicted vs. derived order\n(no lines)", "predicted vs. derived order\n(predicted lines)", "R4P − R4 (original)"]
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.5), sharey=True)
    for ax, (metric, title) in zip(axes, (("d_em", "Δ EM"), ("d_abst", "Δ abstention rate"))):
        for k, (con, _) in enumerate(CTRL):
            for j, (ds, col) in enumerate((("2wikimultihopqa", "#2b5d8a"), ("musique", "#a3241e"))):
                r = ctrl.get((ds, con))
                if not r:
                    continue
                v = float(r[metric])
                lo, hi = json.loads(r[f"{metric}_ci"])
                y = len(CTRL) - 1 - k + (0.14 if j == 0 else -0.14)
                ax.errorbar(v, y, xerr=[[v - lo], [hi - v]], fmt="o", ms=3, capsize=2, color=col,
                            label=DSN[ds] if k == 0 else None)
        ax.axvline(0, color="gray", lw=0.5)
        ax.set_title(title, fontsize=8)
        ax.grid(axis="x", lw=0.3, alpha=0.5)
    axes[0].set_yticks(range(len(CTRL)), labels[::-1], fontsize=6.5)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, fontsize=7, frameon=False, bbox_to_anchor=(0.55, -0.04))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(P / "figures" / "fig_controls.pdf", bbox_inches="tight")
    fig.savefig(P / "figures" / "fig_controls.png", bbox_inches="tight", dpi=200)
    plt.close(fig)

# ------------------------------------------------------------------ transitions (confirmatory + controls)
tr = rows("analysis/F_exp1_transitions.csv") + rows("controls/controls_transitions.csv")
want = [("R0", "R1", "sentence items vs.\\ passages"), ("R1", "R5", "graph order vs.\\ dataset order"),
        ("R5", "R4", "derived relation lines vs.\\ none"), ("R4", "R4P", "R4P vs.\\ R4 (original)"),
        ("R4P_FO_NC", "R4P_FO", "contradiction lines on vs.\\ off")]
body = []
for ds in ("2wikimultihopqa", "musique"):
    for a, b, desc in want:
        r = next((x for x in tr if x["dataset"] == ds and x["a"] == a and x["b"] == b), None)
        if r:
            body.append([DSN[ds], desc, r["n"], f(r["d_em"]), f(r["d_abst"]), f(r["d_wrong"]),
                         f"{f(r['d_acc_given_both_answered'])} {ci(r['d_acc_given_both_answered_ci'])}",
                         f"{r['C_to_A']}/{r['A_to_C']}", f"{r['C_to_W']}/{r['W_to_C']}", f"{r['W_to_A']}/{r['A_to_W']}"])
    body.append("MID")
if body:
    emit("tab_transitions", ["Data", "Change (second vs.\\ first)", "$n$", "$\\Delta$EM", "$\\Delta$Abst.", "$\\Delta$Wrong",
                             "$\\Delta$Acc.\\ | both answered", "C$\\to$A / A$\\to$C", "C$\\to$W / W$\\to$C", "W$\\to$A / A$\\to$W"], body[:-1],
         "Question-level outcome transitions (C correct, W answered and wrong, A not answered) between paired conditions on the "
         "confirmatory questions (exploratory decomposition). $\\Delta$Acc.\\ | both answered: accuracy difference among questions "
         "answered under both conditions, with 95\\% CI. Sources: \\texttt{revision/analysis/F\\_exp1\\_transitions.csv}, "
         "\\texttt{revision/controls/controls\\_transitions.csv}.", "tab:transitions", "@{}llrrrrlrrr@{}")

# ------------------------------------------------------------------ retrieval
rc = rows("retrieval/retrieval_contrasts.csv")
if rc:
    names = {"R1-R0": "R1$-$R0", "R5-R1": "R5$-$R1", "R4-R5": "R4$-$R5", "R4P-R4": "R4P$-$R4", "R4P-R4P_NC": "contradiction lines on$-$off",
             "R4P_FO-R5": "R4P\\_FO$-$R5"}
    body = []
    for ds in ("musique", "2wikimultihopqa"):
        for s in ("A", "B 1.0x per_representation"):
            for con, nm in names.items():
                r = next((x for x in rc if x["dataset"] == ds and x["setting"] == s and x["contrast"] == con and x["stratum"] == "all"), None)
                if r:
                    body.append([DSN[ds], "A" if s == "A" else "B 1.0$\\times$", nm, r["n"], r["n_identical_prompts"],
                                 f(r["d_em"]), ci(r["d_em_ci"]), f(r["d_abst"]),
                                 f"{float(r['tokens_a']):.0f}$\\to${float(r['tokens_b']):.0f}"])
        body.append("MID")
    emit("tab_retrieval", ["Data", "Prot.", "Contrast", "$n$", "Ident.", "$\\Delta$EM", "95\\% CI", "$\\Delta$Abst.", "Tokens"], body[:-1],
         "Retrieved evidence (exploratory, fresh disjoint sample of 500 questions per dataset): every representation renders the same "
         "four reranked passages; R4/R5 use annotation-derived edges restricted to retrieved sentence pairs (oracle structure on real "
         "retrieval). Protocol B: budget $1.0\\times$ content tokens, per-representation policy. Source: "
         "\\texttt{revision/retrieval/retrieval\\_contrasts.csv}.", "tab:retrieval", "@{}lllrrrlrr@{}")
    body = []
    for ds in ("musique", "2wikimultihopqa"):
        for con, nm in names.items():
            r = next((x for x in rc if x["dataset"] == ds and x["setting"] == "A" and x["contrast"] == con and x["stratum"] == "all"), None)
            if r:
                body.append([DSN[ds], nm, r["n_identical_prompts"], f(r["d_em"]), ci(r["d_em_ci"]), f(r["d_abst"])])
        body.append("MID")
    emit("tab_retrieval_main", ["Data", "Contrast", "Ident.", "$\\Delta$EM", "95\\% CI", "$\\Delta$Abst."], body[:-1],
         "Retrieved evidence, Protocol~A (exploratory; fresh disjoint sample, $n$=500 per dataset; all representations render the "
         "same four reranked passages). Ident.: byte-identical prompt pairs. Full table with Protocol~B in Appendix~\\ref{app:revision}. "
         "Source: \\texttt{revision/retrieval/retrieval\\_contrasts.csv}.", "tab:retrieval-main", "@{}llrrlr@{}", star=True)
    body = []
    for ds in ("musique", "2wikimultihopqa"):
        for con in ("R1-R0", "R4P-R4P_NC"):
            for st in ("retrieval=complete", "retrieval=partial", "retrieval=none", "distractor_heavy=True", "long_evidence=True"):
                r = next((x for x in rc if x["dataset"] == ds and x["setting"] == "A" and x["contrast"] == con and x["stratum"] == st), None)
                if r:
                    body.append([DSN[ds], names[con], st.replace("_", " ").replace("=", ": "), r["n"], f(r["d_em"]), ci(r["d_em_ci"]),
                                 f(r["d_abst"])])
        body.append("MID")
    emit("tab_retrieval_strata", ["Data", "Contrast", "Stratum", "$n$", "$\\Delta$EM", "95\\% CI", "$\\Delta$Abst."], body[:-1],
         "Retrieved evidence, Protocol A, by retrospective retrieval outcome (gold labels used only to stratify). Exploratory; small "
         "strata have wide intervals. Source: \\texttt{revision/retrieval/retrieval\\_contrasts.csv}.", "tab:retrieval-strata",
         "@{}lllrrlr@{}")

# ------------------------------------------------------------------ prompt variant
nb = rows("noabst/noabst_contrasts.csv")
if nb:
    body = [[r["prompt"].replace("qa-v2", "\\texttt{qa-v2}").replace("noabst", "\\texttt{noabst}"),
             r["contrast"].replace("-", "$-$").replace("_", "\\_").replace("noabst", "\\texttt{noabst}").replace("qa$-$v2", "\\texttt{qa-v2}"),
             r["n"], f(r["d_em"]), ci(r["d_em_ci"]), f(r["d_abst"])]
            for r in nb if not r["contrast"].startswith("absolute")]
    emit("tab_noabst", ["Prompt", "Contrast", "$n$", "$\\Delta$EM", "95\\% CI", "$\\Delta$Abst."], body,
         "Prompt factor (exploratory, 1{,}000 confirmatory 2Wiki questions): the frozen prompt \\texttt{qa-v2} and the same prompt "
         "without the line offering \\emph{insufficient evidence} (\\texttt{noabst}); last rows give the prompt $\\times$ representation "
         "interaction. Source: \\texttt{revision/noabst/noabst\\_contrasts.csv}.", "tab:noabst", "@{}llrrlr@{}", star=True)

# ------------------------------------------------------------------ Exp0 costs
c0 = rows("analysis/C_exp0_costs.csv")
if c0:
    body = []
    for ds in ("musique", "2wikimultihopqa"):
        for r in c0:
            if r["dataset"] == ds:
                body.append([DSN[ds], r["system"], f(r["score"], 2, False), f(r["coverage"], 2, False), f(r["evidence_tokens"], 0, False),
                             f(r["units"], 1, False), f(r["gold_passage_recall"], 2, False), f(r["answer_in_evidence"], 2, False),
                             f(r["extraction_calls"], 1, False), f(r["total_latency_s"], 1, False),
                             f(r["b4_contradicts_share"], 2, False) if r.get("b4_contradicts_share") else "--"])
        body.append("MID")
    emit("tab_exp0_costs", ["Data", "Sys.", "EM", "Cov.", "Tok.", "Units", "Gold-pass.\\ rec.", "Ans.\\ in ev.", "Extr.\\ calls",
                            "Latency (s)", "CONTRA share"], body[:-1],
         "Experiment~0 with budgets and costs made explicit (pilot, $n$=100 per dataset). Budgets are \\emph{not} matched: B2/B3 show "
         "about three times the tokens of B0/B1; B4 selects at most 12 claims within 450 tokens. Latency includes LLM claim "
         "extraction (original-call latency for cached calls). CONTRA share: fraction of B4's predicted relations labelled "
         "\\texttt{CONTRADICTS}. Source: \\texttt{revision/analysis/C\\_exp0\\_costs.csv}.", "tab:exp0-costs", "@{}llrrrrrrrrr@{}")
print("assets written:", sorted(x.name for x in (P / "tables").glob("tab_*") if x.suffix == ".tex"))

# ------------------------------------------------------------------ contradiction triage (automatic, not judgements)
cs = R / "contradictions/contradictions_summary.json"
if cs.exists():
    d = json.loads(cs.read_text())
    tot = d["n_pairs"]
    names = {"auto:different_source_titles": "different source titles (different entities)",
             "auto:same_title_different_years": "same title, different years",
             "auto:same_title_different_numbers": "same title, different numbers",
             "auto:same_title_pronoun_initial": "same title, pronoun-initial sentence",
             "auto:same_title_other": "same title, other"}
    body = [[names[k], f"{d['auto_category_pairs'][k]:,}", f"{100 * d['auto_category_pairs'][k] / tot:.0f}\\%"] for k in names]
    body.append("MID")
    body.append(["all predicted contradiction pairs", f"{tot:,}", "100\\%"])
    emit("tab_contra_triage", ["Automatic triage (heuristic, not a judgement)", "Pairs", "Share"], body,
         f"Predicted \\texttt{{CONTRADICTS}} pairs on the confirmatory sample (R4P; {d['n_edges']:,} directed edges, "
         f"{d['n_edges_shown_to_reader']:,} rendered, {d['n_questions_with_contradicts']:,} questions). NLI confidence $\\geq$0.90 "
         f"(median {d['nli_confidence_quartiles']['median']:.3f}). Categories are heuristic triage for prioritising human "
         "verification. Source: \\texttt{revision/contradictions/contradictions\\_summary.json}.", "tab:contra-triage", "@{}lrr@{}", star=True)


# ------------------------------------------------------------------ confirmatory protocol 2 (frozen; untouched questions)
c2 = R2 / "confirm2/confirm2_summary.json"
if c2.exists():
    d = json.loads(c2.read_text())["datasets"]
    body = []
    for ds in ("2wikimultihopqa", "hotpotqa"):
        x = d[ds]
        pe, ab, al, ac = x["primary_em"], x["secondary_abstention"], x["secondary_em_all_questions"], x["acc_given_both_answered"]
        t = x["transitions_primary (off->on)"]
        p = lambda v: "$<$0.001" if v == 0 else f"{v:.3f}"  # noqa: E731
        body.append([DSN[ds], f"{x['n_primary_population']:,}/{x['n_questions']:,}", f(pe["delta"]), ci(pe["ci"]), p(pe["p_holm"]),
                     f(ab["delta"]), ci(ab["ci"]), f(al["delta"]), f(ac["delta"]),
                     f"{t.get('C->A', 0)}/{t.get('C->W', 0)}/{t.get('A->C', 0)}/{t.get('W->C', 0)}"])
    emit("tab_confirm2", ["Data", "$n$ (lines/all)", "$\\Delta$EM", "95\\% CI", "$p_{\\text{Holm}}$", "$\\Delta$Abst.", "95\\% CI",
                          "$\\Delta$EM all", "$\\Delta$Acc$\\mid$both", "C$\\to$A/C$\\to$W/A$\\to$C/W$\\to$C"], body,
         "Confirmatory test 2 (protocol frozen and published before sampling): showing the predicted \\texttt{CONTRADICTS} lines "
         "(R4P\\_FO) vs.\\ the same block without them (R4P\\_FO\\_NC), fixed order, on untouched questions. Primary population: "
         "questions with at least one rendered contradiction line (an input property); Holm over the two datasets. "
         "$\\Delta$EM all: secondary estimand over all questions (identical prompts contribute 0). "
         "$\\Delta$Acc$\\mid$both and transitions are descriptive. Source: \\texttt{revision2/confirm2/confirm2\\_summary.json}.",
         "tab:confirm2", "@{}lrrlrrlrrr@{}")

# ------------------------------------------------------------------ second reader (Mistral) vs Qwen, same questions
rd = {(r["dataset"], r["contrast"]): r for r in rows2("r2/reader2.csv") if r["stratum"] == "all"}
if rd:
    M = "@qa-v2@mistral"
    RC = [("R0>R1", "sentence items $-$ passages (R1$-$R0)"), ("R1>R5", "derived order (R5$-$R1)"),
          ("R5>R4", "derived relation lines (R4$-$R5)"), ("R4>R4P_FO", "predicted $-$ derived lines, fixed order"),
          ("R4P_FO_NC>R4P_FO", "contradiction lines on $-$ off")]
    body = []
    for ds in ("2wikimultihopqa", "musique"):
        for con, desc in RC:
            a, b = con.split(">")
            q, m = rd.get((ds, con)), rd.get((ds, f"{a}{M}>{b}{M}"))
            if not (q and m):
                continue
            body.append([DSN[ds], desc, f(q["d_em"]), ci(q["d_em_ci"]), f(q["d_abst"]),
                         f(m["d_em"]), ci(m["d_em_ci"]), f(m["d_abst"]), f(m["d_lenient"]), ci(m["d_lenient_ci"])])
        body.append("MID")
    base = {ds: rd.get((ds, f"R0{M}>R1{M}")) for ds in ("2wikimultihopqa", "musique")}
    lv = "; ".join(f"{DSN[ds]} R0: EM {float(r['em_a']):.2f}, lenient {float(r['lenient_a']):.2f}, abstained {float(r['abst_a']):.2f}"
                   for ds, r in base.items() if r)
    emit("tab_reader2", ["Data", "Contrast", "Qwen $\\Delta$EM", "95\\% CI", "$\\Delta$Abst.", "Mistral $\\Delta$EM", "95\\% CI",
                         "$\\Delta$Abst.", "$\\Delta$Lenient", "95\\% CI"], body[:-1],
         "Second reader (exploratory cross-model replication on the confirmatory questions; $n$=3{,}232 2Wiki, 1{,}744 MuSiQue): "
         "Qwen2.5-7B-Instruct and Mistral-7B-Instruct-v0.3 with the same prompt and evidence. Lenient: gold alias contained in the "
         f"answer (pre-specified before the Mistral run, because Mistral often answers in full sentences). Mistral levels: {lv}. "
         "Source: \\texttt{revision2/r2/reader2.csv}.", "tab:reader2", "@{}llrlrrlrrl@{}")

# ------------------------------------------------------------------ abstention policy: three prompts
pr = {r["contrast"]: r for r in rows2("r2/prompt3.csv") if r["stratum"] == "all"}
if pr:
    C, N = "@qa-v2-conservative", "@qa-v2-noabst"
    body = []
    for rep in ("R0", "R1", "R4", "R4P"):
        c, n = pr.get(f"{rep}>{rep}{C}"), pr.get(f"{rep}>{rep}{N}")
        if not (c and n):
            continue
        cell = lambda r, side: f"{float(r['em_' + side]):.3f} / {float(r['abst_' + side]):.3f} / {float(r['wrong_' + side]):.3f}"  # noqa: E731
        body.append([rep, cell(c, "a"), cell(c, "b"), cell(n, "b")])
    body.append("MID")
    for con, desc in (("R0>R1", "R1$-$R0"), ("R4>R4P", "R4P$-$R4")):
        cells = [desc]
        for suf in ("", C, N):
            a, b = con.split(">")
            r = pr.get(f"{a}{suf}>{b}{suf}")
            cells.append(f"{f(r['d_em'])} {ci(r['d_em_ci'])}" if r else "--")
        body.append(cells)
    for con, desc in (("R0>R1", "R1$-$R0"), ("R4>R4P", "R4P$-$R4")):
        a, b = con.split(">")
        rc, rn = pr.get(f"({con})-({a}{C}>{b}{C})"), pr.get(f"({con})-({a}{N}>{b}{N})")
        body.append([f"interaction, {desc}", "(qa-v2 $-$ variant)", f"{f(rc['d_em'])} {ci(rc['d_em_ci'])}" if rc else "--",
                     f"{f(rn['d_em'])} {ci(rn['d_em_ci'])}" if rn else "--"])
    emit("tab_prompt3", ["", "\\texttt{qa-v2} (frozen)", "conservative", "no abstention option"], body,
         "Abstention policy (exploratory; the same 1{,}000 confirmatory 2Wiki questions and evidence). Top: EM / abstention / "
         "wrong-answer rate per representation. Middle: within-prompt contrasts ($\\Delta$EM, 95\\% CI). Bottom: prompt $\\times$ "
         "representation interaction, (contrast under \\texttt{qa-v2}) $-$ (contrast under the variant). Conservative: the last line "
         "replaced by \\emph{If the evidence does not fully establish the answer, reply ``Answer: insufficient evidence''. Do not guess.} "
         "Source: \\texttt{revision2/r2/prompt3.csv}.", "tab:prompt3", "@{}llll@{}")

# ------------------------------------------------------------------ serialisation accounting and anchor strata
sa = rows2("serialization/serialization_accounting.csv")
if sa:
    order = ["R0", "R1", "R5", "R4", "R4P", "R4P_FO", "R4P_FO_NC", "R4N_FO"]
    body = []
    for ds in ("2wikimultihopqa", "musique"):
        for rep in order:
            r = next((x for x in sa if x["dataset"] == ds and x["representation"] == rep), None)
            if r:
                body.append([DSN[ds], rep.replace("_", "\\_"), r["input_tokens"], r["content_tokens"], r["overhead_tokens"],
                             r["facts"], r["relation_lines"], r["source_mentions"], r["identical_to_R1"], f(r["em"], 3, False),
                             f(r["abstained"], 3, False)])
        body.append("MID")
    emit("tab_serialisation", ["Data", "Rep.", "Input tok.", "Content tok.", "Overhead tok.", "Facts", "Rel.\\ lines",
                               "Titles shown", "$=$R1", "EM", "Abst."], body[:-1],
         "Serialisation accounting on the confirmatory questions (Protocol A, means per question). Content tokens are identical "
         "across representations by construction; overhead is identifiers, titles, headers and relation lines. Titles shown: source "
         "titles per prompt (once per passage in R0, once per item otherwise). $=$R1: questions whose evidence block is "
         "byte-identical to R1. Source: \\texttt{revision2/serialization/serialization\\_accounting.csv}.", "tab:serialisation",
         "@{}llrrrrrrrrr@{}")
an = rows2("serialization/anchor_strata.csv")
if an:
    body = [[DSN[r["dataset"]], r["edge_stratum"].replace("_", " ").replace("B derived ", "").replace("C derived ", ""),
             r["contrast"].replace("-", "$-$"), r["n"], r["n_identical"], f(r["d_em"]), ci(r["d_em_ci"]), f(r["d_abst"])]
            for r in an if r["edge_stratum"] != "no_edges"]
    emit("tab_anchor", ["Data", "Edge stratum", "Contrast", "$n$", "Ident.", "$\\Delta$EM", "95\\% CI", "$\\Delta$Abst."], body,
         "Derived structure by anchor quality (confirmatory questions; exploratory stratification by an input property). Exact anchor: "
         "every derived dependency is anchored to a sentence by exact string match; fallback: at least one endpoint is a fallback "
         "guess. Questions without derived edges (identical prompts) are omitted. Source: "
         "\\texttt{revision2/serialization/anchor\\_strata.csv}.", "tab:anchor", "@{}lllrrrlr@{}", star=True)
