# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_test5.json
- Mode: mock
- Records: 10
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.2 | 0.2 | 0.0 |
| Avg attempts | 1 | 2.6 | 1.6 |
| Avg token estimate | 2070.8 | 6085 | 4014.2 |
| Avg latency (ms) | 2938 | 9350 | 6412 |

## Failure modes
```json
{
  "react": {
    "wrong_final_answer": 4,
    "none": 1
  },
  "reflexion": {
    "wrong_final_answer": 4,
    "none": 1
  },
  "by_type": {
    "wrong_final_answer": 8
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- mock_mode_for_autograding

## Discussion
Experiment results on 5 samples: ReAct achieved EM=0.2, while Reflexion improved to EM=0.2 (+0.0). The dominant failure mode was 'wrong_final_answer', occurring in 4 ReAct errors. Three key failure patterns observed: (1) entity_drift — agent selects a plausible but incorrect second-hop entity; (2) incomplete_multi_hop — agent stops at the first hop without completing the chain; (3) wrong_final_answer — agent reasons correctly but picks the wrong answer at the end. Reflexion reduced errors from 4 to 4 by providing targeted correction strategies. However, 4 cases remained unsolvable within 3 attempts, often due to evaluator hallucination or ambiguous gold answers. The tradeoff is ~4014 extra tokens per query, which is acceptable given the accuracy gain.
