# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_100.json
- Mode: mock
- Records: 200
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.77 | 0.9 | 0.13 |
| Avg attempts | 1 | 1.35 | 0.35 |
| Avg token estimate | 1797.6 | 2604.06 | 806.46 |
| Avg latency (ms) | 6945.88 | 5053.59 | -1892.29 |

## Failure modes
```json
{
  "react": {
    "none": 77,
    "wrong_final_answer": 23
  },
  "reflexion": {
    "none": 90,
    "wrong_final_answer": 10
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- mock_mode_for_autograding

## Discussion
Reflexion helps when the first attempt stops after the first hop or drifts to a wrong second-hop entity. The tradeoff is higher attempts, token cost, and latency. In a real report, students should explain when the reflection memory was useful, which failure modes remained, and whether evaluator quality limited gains.
