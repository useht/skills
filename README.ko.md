# HyperTeams 스킬

Claude Code 스킬을 내놓기 전에 세 가지로 잽니다 — 스킬을 켜고, 끄고, 스킬 없이 그 일의 원문(공식 문서·법령 같은 것)을 붙여 준 상대와 견줍니다. 원문만 줘도 되는 스킬이라면 낼 까닭이 없기 때문입니다.

## 지금 상태

| 스킬 | 하는 일 | 켬 | 원문을 받은 상대 | 차이(95% 구간) | 결과 |
|---|---|---|---|---|---|
| [plugin-eval-field-notes](plugins/plugin-eval-field-notes/) | `claude plugin eval` 을 돌리고 읽을 때 공식 문서에 없는 함정(Windows 셸, `-j` 동시 실행 때 비용 겹침, 판정관 결과, 켬/끔 팔 설계) | 0.825 | 0.183 | +0.64 [+0.54, +0.77] | 원문 상대를 이김 — 판정관 민감, 다른 공개 스킬과는 아직 안 견줌 |
| plugin-eval-field-notes 대 [채움: 설치 1위 스킬·찾은 가장 강한 스킬] | 같은 일 | [채움] | [채움] | [채움] | [채움] |
| kr-vat-filing · kr-payroll · eu-product-compliance | 부가세·4대보험·EU 리콜 | 1.000 · 1.000 · 0.838 | 0.976 · 1.000 · 0.928 | +0.02 · +0.00 · −0.09 | 되돌림 — 원문 상대를 넘지 못함 |

관문 세트 값입니다(사례 5개 또는 7개 × 3회). 확인 세트와 두 판정관 표는 [benchmarks/](benchmarks/README.md)에 있습니다.

**판정관 민감**: 같은 답을 Sonnet 과 Opus 두 판정관으로 다시 매겼을 때 기준별 판정이 실행마다 83~91% 맞았습니다. 미리 정한 95% 에 못 미쳐, 이 숫자는 '한 판정관의 채점'으로 읽어 주세요. 두 판정관 모두에서 두 세트 모두 원문 상대보다 높았다(구간 아래끝 > 0)는 것까지가 주장입니다. 사람이 매긴 정답과 대 본 적은 없습니다.

## 설치

```
/plugin marketplace add useht/skills
/plugin install plugin-eval-field-notes@hyperteams
```

## 진 결과도 남깁니다

원문 상대를 넘지 못해 되돌린 스킬은 [benchmarks/REJECTED.md](benchmarks/REJECTED.md) 에 그때 수치와 그때 기준 그대로 둡니다. 우리 스킬이 지는 사례를 찾으면 [반례 이슈](.github/ISSUE_TEMPLATE/counterexample.yml)로 알려 주세요 — 다시 재서 위 숫자를 고칩니다.

MIT. Claude·Anthropic 은 Anthropic, PBC 의 상표이며 이 저장소는 Anthropic 과 관계가 없습니다.
