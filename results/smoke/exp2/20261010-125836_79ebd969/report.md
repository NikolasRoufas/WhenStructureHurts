# exp2 - run 20261010-125836_79ebd969

> **SMOKE TEST - software/pipeline validation only.** Sample sizes are tiny and the model is a
> 0.5B development model. Nothing here is evidence for or against any hypothesis.

- status: completed
- model: {'model_id': 'Qwen/Qwen2.5-0.5B-Instruct', 'revision': '7ae557604adf67be50417f59c2c2f167def9a775'}
- code: git=None tree=2a186c4f24aa
- wall clock: 101.08 s; uncached generations: 113
- records: 480

## Per-condition summary (coverage-adjusted, question-level means; conditional in parentheses)

| dataset | condition | n_q | unavail | coverage | F1 | EM | verdict | cit.valid | cit.recall | support cov | grounded NLI | ev.tok | lat s | top failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| 2wikimultihopqa | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| 2wikimultihopqa | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.078 (0.078) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 559.000 | 1.190 | wrong_answer |
| 2wikimultihopqa | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.078 (0.078) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 569.000 | 1.259 | wrong_answer |
| 2wikimultihopqa | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| 2wikimultihopqa | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| 2wikimultihopqa | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 346.667 | 0.749 | wrong_answer |
| 2wikimultihopqa | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 356.667 | 0.799 | wrong_answer |
| 2wikimultihopqa | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| 2wikimultihopqa | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| 2wikimultihopqa | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| 2wikimultihopqa | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| 2wikimultihopqa | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| 2wikimultihopqa | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| 2wikimultihopqa | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 0.333 | 0.000 | 364.000 | 0.801 | wrong_answer |
| 2wikimultihopqa | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.333 | 0.000 | 374.000 | 0.844 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P1,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P1,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P1,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 0.500 | 0.000 | 337.000 | 0.819 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P1,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 0.500 | 0.000 | 340.333 | 0.823 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P2,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P2,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P2,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| 2wikimultihopqa | params={},perturbation=P2,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 391.333 | 0.859 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P3,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P3,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P3,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.583 (0.583) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.833 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P3,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.529 (0.529) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.131 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P7,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P7,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| 2wikimultihopqa | params={},perturbation=P7,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| 2wikimultihopqa | params={},perturbation=P7,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 56.000 | 0.395 | wrong_answer |
| fever | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 56.000 | 0.395 | wrong_answer |
| fever | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 1 | 2 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.500 | 0.000 | 75.000 | 0.349 | wrong_answer |
| fever | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 1 | 2 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.500 | 0.000 | 75.000 | 0.349 | wrong_answer |
| fever | params={},perturbation=P1,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={},perturbation=P1,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={},perturbation=P1,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 0.250 | 0.000 | 33.500 | 0.344 | wrong_answer |
| fever | params={},perturbation=P1,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 0.250 | 0.000 | 33.500 | 0.344 | wrong_answer |
| fever | params={},perturbation=P2,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={},perturbation=P2,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={},perturbation=P2,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | params={},perturbation=P2,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | params={},perturbation=P3,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={},perturbation=P3,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={},perturbation=P3,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 1 | 2 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 95.000 | 0.430 | wrong_answer |
| fever | params={},perturbation=P3,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 1 | 2 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 95.000 | 0.430 | wrong_answer |
| fever | params={},perturbation=P7,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={},perturbation=P7,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | params={},perturbation=P7,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | params={},perturbation=P7,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hotpotqa | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hotpotqa | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.089 | missing_citation |
| hotpotqa | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.357 (0.357) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 626.000 | 1.075 | wrong_answer |
| hotpotqa | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 633.000 | 1.072 | wrong_answer |
| hotpotqa | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hotpotqa | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.089 | missing_citation |
| hotpotqa | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 389.333 | 0.841 | missing_citation |
| hotpotqa | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 396.000 | 0.864 | missing_citation |
| hotpotqa | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hotpotqa | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.089 | missing_citation |
| hotpotqa | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 1 | 2 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 790.000 | 1.093 | wrong_answer |
| hotpotqa | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 1 | 2 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 800.000 | 1.179 | wrong_answer |
| hotpotqa | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hotpotqa | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.089 | missing_citation |
| hotpotqa | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 0.333 | 0.000 | 393.000 | 0.748 | wrong_answer |
| hotpotqa | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 0.333 | 0.000 | 399.667 | 0.747 | wrong_answer |
| hotpotqa | params={},perturbation=P1,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hotpotqa | params={},perturbation=P1,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.089 | missing_citation |
| hotpotqa | params={},perturbation=P1,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.500 | 0.000 | 363.000 | 0.878 | wrong_answer |
| hotpotqa | params={},perturbation=P1,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.500 | 0.000 | 363.000 | 0.878 | wrong_answer |
| hotpotqa | params={},perturbation=P2,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hotpotqa | params={},perturbation=P2,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.089 | missing_citation |
| hotpotqa | params={},perturbation=P2,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hotpotqa | params={},perturbation=P2,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 0.000 | 483.500 | 0.949 | wrong_answer |
| hotpotqa | params={},perturbation=P3,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hotpotqa | params={},perturbation=P3,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.089 | missing_citation |
| hotpotqa | params={},perturbation=P3,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 0.767 | wrong_answer |
| hotpotqa | params={},perturbation=P3,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.201 | wrong_answer |
| hotpotqa | params={},perturbation=P7,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hotpotqa | params={},perturbation=P7,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.089 | missing_citation |
| hotpotqa | params={},perturbation=P7,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hotpotqa | params={},perturbation=P7,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 459.333 | 0.720 | wrong_answer |
| hover | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 459.333 | 0.728 | wrong_answer |
| hover | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 279.667 | 0.535 | wrong_answer |
| hover | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 279.667 | 0.535 | wrong_answer |
| hover | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 1 | 2 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | - | 323.000 | 0.598 | wrong_answer |
| hover | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 1 | 2 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | - | 323.000 | 0.598 | wrong_answer |
| hover | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.389 | 0.000 | 273.000 | 0.552 | wrong_answer |
| hover | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.389 | 0.000 | 273.000 | 0.552 | wrong_answer |
| hover | params={},perturbation=P1,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={},perturbation=P1,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={},perturbation=P1,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.389 | 0.000 | 196.333 | 0.461 | wrong_answer |
| hover | params={},perturbation=P1,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.389 | 0.000 | 196.333 | 0.461 | wrong_answer |
| hover | params={},perturbation=P2,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={},perturbation=P2,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={},perturbation=P2,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | params={},perturbation=P2,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | params={},perturbation=P3,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={},perturbation=P3,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={},perturbation=P3,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.596 | wrong_answer |
| hover | params={},perturbation=P3,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.596 | wrong_answer |
| hover | params={},perturbation=P7,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={},perturbation=P7,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | params={},perturbation=P7,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | params={},perturbation=P7,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| musique | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.700 | missing_citation |
| musique | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |
| musique | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 541.000 | 1.021 | wrong_answer |
| musique | params={"mode": "hard"},perturbation=P4,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 558.667 | 1.037 | wrong_answer |
| musique | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.700 | missing_citation |
| musique | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |
| musique | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.467 (0.467) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 335.667 | 0.735 | wrong_answer |
| musique | params={"mode": "strip"},perturbation=P5,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 352.000 | 0.766 | wrong_answer |
| musique | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.700 | missing_citation |
| musique | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |
| musique | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 1 | 2 | 1.000 | 1.000 (1.000) | 1.000 (1.000) | - | - | 0.000 | 1.000 | 0.000 | 504.000 | 0.902 | missing_citation |
| musique | params={"op": "negation"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 1 | 2 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 533.000 | 1.118 | wrong_answer |
| musique | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.700 | missing_citation |
| musique | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |
| musique | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 358.000 | 0.770 | missing_citation |
| musique | params={"op": "temporal"},perturbation=P6,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 374.333 | 0.885 | wrong_answer |
| musique | params={},perturbation=P1,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.700 | missing_citation |
| musique | params={},perturbation=P1,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |
| musique | params={},perturbation=P1,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | 1.000 | 0.167 | 1.000 | 0.000 | 303.667 | 1.370 | missing_citation |
| musique | params={},perturbation=P1,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | 1.000 | 0.167 | 1.000 | 0.000 | 307.000 | 1.324 | missing_citation |
| musique | params={},perturbation=P2,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.700 | missing_citation |
| musique | params={},perturbation=P2,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |
| musique | params={},perturbation=P2,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| musique | params={},perturbation=P2,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 397.333 | 0.800 | wrong_answer |
| musique | params={},perturbation=P3,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.700 | missing_citation |
| musique | params={},perturbation=P3,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |
| musique | params={},perturbation=P3,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 1.011 | missing_citation |
| musique | params={},perturbation=P3,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.836 | wrong_answer |
| musique | params={},perturbation=P7,pseed=0,rate=0.0,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.700 | missing_citation |
| musique | params={},perturbation=P7,pseed=0,rate=0.0,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |
| musique | params={},perturbation=P7,pseed=0,rate=0.4,representation=R1,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| musique | params={},perturbation=P7,pseed=0,rate=0.4,representation=R4,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |

## Perturbation sensitivity (vs. each question's unperturbed record)

| dataset | rep | P | params | rate | n | mean k | label effects | answer changed | abstain (base->pert) |
|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | R1 | P1 | {} | 0.4 | 3 | 1.000 | {'not_guaranteed': 2, 'answer_removed': 1} | 0.333 | 0.000->0.000 |
| 2wikimultihopqa | R1 | P3 | {} | 0.4 | 3 | 3.667 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| 2wikimultihopqa | R1 | P4 | {"mode": "hard"} | 0.4 | 3 | 3.667 | {'preserved': 3} | 0.667 | 0.000->0.000 |
| 2wikimultihopqa | R1 | P5 | {"mode": "strip"} | 0.4 | 3 | 3.667 | {'preserved': 3} | 0.000 | 0.000->0.000 |
| 2wikimultihopqa | R1 | P6 | {"op": "temporal"} | 0.4 | 3 | 2.000 | {'not_guaranteed': 2, 'answer_removed': 1} | 0.000 | 0.000->0.000 |
| 2wikimultihopqa | R4 | P1 | {} | 0.4 | 3 | 1.000 | {'not_guaranteed': 2, 'answer_removed': 1} | 0.667 | 0.000->0.000 |
| 2wikimultihopqa | R4 | P2 | {} | 0.4 | 3 | 1.000 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| 2wikimultihopqa | R4 | P3 | {} | 0.4 | 3 | 3.667 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| 2wikimultihopqa | R4 | P4 | {"mode": "hard"} | 0.4 | 3 | 3.667 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| 2wikimultihopqa | R4 | P5 | {"mode": "strip"} | 0.4 | 3 | 3.667 | {'preserved': 3} | 0.667 | 0.000->0.000 |
| 2wikimultihopqa | R4 | P6 | {"op": "temporal"} | 0.4 | 3 | 2.000 | {'not_guaranteed': 2, 'answer_removed': 1} | 0.667 | 0.000->0.000 |
| fever | R1 | P1 | {} | 0.4 | 2 | 1.000 | {'not_guaranteed': 2} | 0.000 | 0.000->0.000 |
| fever | R1 | P3 | {} | 0.4 | 1 | 0.000 | {'preserved': 1} | 0.000 | 0.000->0.000 |
| fever | R1 | P5 | {"mode": "strip"} | 0.4 | 2 | 1.000 | {'preserved': 2} | 0.000 | 0.000->0.000 |
| fever | R1 | P6 | {"op": "temporal"} | 0.4 | 1 | 1.000 | {'not_guaranteed': 1} | 0.000 | 0.000->0.000 |
| fever | R4 | P1 | {} | 0.4 | 2 | 1.000 | {'not_guaranteed': 2} | 0.000 | 0.000->0.000 |
| fever | R4 | P3 | {} | 0.4 | 1 | 0.000 | {'preserved': 1} | 0.000 | 0.000->0.000 |
| fever | R4 | P5 | {"mode": "strip"} | 0.4 | 2 | 1.000 | {'preserved': 2} | 0.000 | 0.000->0.000 |
| fever | R4 | P6 | {"op": "temporal"} | 0.4 | 1 | 1.000 | {'not_guaranteed': 1} | 0.000 | 0.000->0.000 |
| hotpotqa | R1 | P1 | {} | 0.4 | 3 | 1.000 | {'answer_removed': 2, 'not_guaranteed': 1} | 0.333 | 0.000->0.000 |
| hotpotqa | R1 | P3 | {} | 0.4 | 3 | 4.333 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| hotpotqa | R1 | P4 | {"mode": "hard"} | 0.4 | 3 | 4.333 | {'preserved': 3} | 0.667 | 0.000->0.000 |
| hotpotqa | R1 | P5 | {"mode": "strip"} | 0.4 | 3 | 4.333 | {'preserved': 3} | 0.000 | 0.000->0.000 |
| hotpotqa | R1 | P6 | {"op": "negation"} | 0.4 | 1 | 1.000 | {'not_guaranteed': 1} | 0.000 | 0.000->0.000 |
| hotpotqa | R1 | P6 | {"op": "temporal"} | 0.4 | 3 | 2.000 | {'answer_removed': 2, 'not_guaranteed': 1} | 0.333 | 0.000->0.000 |
| hotpotqa | R4 | P1 | {} | 0.4 | 3 | 1.000 | {'answer_removed': 2, 'not_guaranteed': 1} | 0.333 | 0.000->0.000 |
| hotpotqa | R4 | P2 | {} | 0.4 | 2 | 1.000 | {'preserved': 2} | 0.500 | 0.000->0.000 |
| hotpotqa | R4 | P3 | {} | 0.4 | 3 | 4.333 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| hotpotqa | R4 | P4 | {"mode": "hard"} | 0.4 | 3 | 4.333 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| hotpotqa | R4 | P5 | {"mode": "strip"} | 0.4 | 3 | 4.333 | {'preserved': 3} | 0.000 | 0.000->0.000 |
| hotpotqa | R4 | P6 | {"op": "negation"} | 0.4 | 1 | 1.000 | {'not_guaranteed': 1} | 0.000 | 0.000->0.000 |
| hotpotqa | R4 | P6 | {"op": "temporal"} | 0.4 | 3 | 2.000 | {'answer_removed': 2, 'not_guaranteed': 1} | 0.333 | 0.000->0.000 |
| hover | R1 | P1 | {} | 0.4 | 3 | 1.667 | {'not_guaranteed': 3} | 0.333 | 0.000->0.000 |
| hover | R1 | P3 | {} | 0.4 | 3 | 3.333 | {'preserved': 3} | 0.000 | 0.000->0.000 |
| hover | R1 | P4 | {"mode": "hard"} | 0.4 | 3 | 3.333 | {'preserved': 3} | 0.000 | 0.000->0.000 |
| hover | R1 | P5 | {"mode": "strip"} | 0.4 | 3 | 3.333 | {'preserved': 3} | 0.000 | 0.000->0.000 |
| hover | R1 | P6 | {"op": "negation"} | 0.4 | 1 | 1.000 | {'not_guaranteed': 1} | 0.000 | 0.000->0.000 |
| hover | R1 | P6 | {"op": "temporal"} | 0.4 | 3 | 2.000 | {'not_guaranteed': 3} | 0.000 | 0.000->0.000 |
| hover | R4 | P1 | {} | 0.4 | 3 | 1.667 | {'not_guaranteed': 3} | 0.333 | 0.000->0.000 |
| hover | R4 | P3 | {} | 0.4 | 3 | 3.333 | {'preserved': 3} | 0.000 | 0.000->0.000 |
| hover | R4 | P4 | {"mode": "hard"} | 0.4 | 3 | 3.333 | {'preserved': 3} | 0.000 | 0.000->0.000 |
| hover | R4 | P5 | {"mode": "strip"} | 0.4 | 3 | 3.333 | {'preserved': 3} | 0.000 | 0.000->0.000 |
| hover | R4 | P6 | {"op": "negation"} | 0.4 | 1 | 1.000 | {'not_guaranteed': 1} | 0.000 | 0.000->0.000 |
| hover | R4 | P6 | {"op": "temporal"} | 0.4 | 3 | 2.000 | {'not_guaranteed': 3} | 0.000 | 0.000->0.000 |
| musique | R1 | P1 | {} | 0.4 | 3 | 2.000 | {'answer_removed': 1, 'not_guaranteed': 2} | 0.333 | 0.000->0.000 |
| musique | R1 | P3 | {} | 0.4 | 3 | 4.667 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| musique | R1 | P4 | {"mode": "hard"} | 0.4 | 3 | 4.667 | {'preserved': 3} | 0.667 | 0.000->0.000 |
| musique | R1 | P5 | {"mode": "strip"} | 0.4 | 3 | 4.667 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| musique | R1 | P6 | {"op": "negation"} | 0.4 | 1 | 1.000 | {'not_guaranteed': 1} | 0.000 | 0.000->0.000 |
| musique | R1 | P6 | {"op": "temporal"} | 0.4 | 3 | 2.667 | {'not_guaranteed': 3} | 0.333 | 0.000->0.000 |
| musique | R4 | P1 | {} | 0.4 | 3 | 2.000 | {'answer_removed': 1, 'not_guaranteed': 2} | 1.000 | 0.000->0.000 |
| musique | R4 | P2 | {} | 0.4 | 3 | 1.333 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| musique | R4 | P3 | {} | 0.4 | 3 | 4.667 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| musique | R4 | P4 | {"mode": "hard"} | 0.4 | 3 | 4.667 | {'preserved': 3} | 1.000 | 0.000->0.000 |
| musique | R4 | P5 | {"mode": "strip"} | 0.4 | 3 | 4.667 | {'preserved': 3} | 0.333 | 0.000->0.000 |
| musique | R4 | P6 | {"op": "negation"} | 0.4 | 1 | 1.000 | {'not_guaranteed': 1} | 0.000 | 0.000->0.000 |
| musique | R4 | P6 | {"op": "temporal"} | 0.4 | 3 | 2.667 | {'not_guaranteed': 3} | 0.000 | 0.000->0.000 |

Unavailable conditions are excluded from metric denominators and counted in 'unavail'.
All numbers can be recomputed with `wsh report <run_dir>`.
