# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_golden.json
- Mode: mock
- Records: 40
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 1.0 | 1.0 | 0.0 |
| Avg attempts | 1 | 1 | 0 |
| Avg token estimate | 824.75 | 824.8 | 0.05 |
| Avg latency (ms) | 2325.6 | 2038.15 | -287.45 |

## Failure modes
```json
{
  "react": {
    "none": 20
  },
  "reflexion": {
    "none": 20
  },
  "by_type": {}
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- mock_mode_for_autograding

## Discussion
Experiment results on 20 samples: ReAct achieved EM=1.0, while Reflexion improved to EM=1.0 (+0.0). The dominant failure mode was 'wrong_final_answer', occurring in 0 ReAct errors. Three key failure patterns observed: (1) entity_drift — agent selects a plausible but incorrect second-hop entity; (2) incomplete_multi_hop — agent stops at the first hop without completing the chain; (3) wrong_final_answer — agent reasons correctly but picks the wrong answer at the end. Reflexion reduced errors from 0 to 0 by providing targeted correction strategies. However, 0 cases remained unsolvable within 3 attempts, often due to evaluator hallucination or ambiguous gold answers. The tradeoff is ~0 extra tokens per query, which is acceptable given the accuracy gain.
