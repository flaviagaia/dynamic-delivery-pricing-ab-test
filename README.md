# dynamic-delivery-pricing-ab-test

## Português

### Visão geral

`dynamic-delivery-pricing-ab-test` é um projeto de experimentação de pricing para marketplace, inspirado em uma pergunta clássica de entrevista: **como desenhar e avaliar uma nova estratégia de precificação de entrega**.

O experimento compara:

- `control`
  - política atual de taxa de entrega
- `treatment`
  - política dinâmica com desconto para sessões mais sensíveis a preço e leve ajuste em pico

### Objetivo analítico

O problema correto de pricing não é “cobrar mais” nem “cobrar menos”. O objetivo é equilibrar:

- conversão;
- margem unitária;
- cancelamento;
- saúde do marketplace.

### Desenho experimental

- unidade de randomização: `checkout_session`
- hipótese principal:
  - uma política mais segmentada pode melhorar eficiência econômica por sessão

### Métrica principal

- `contribution_margin_per_session`

### Métricas secundárias

- `net_completed_order_rate`
- `avg_delivery_fee`

### Guardrails

- `checkout_conversion_rate`
- `cancellation_rate`

### Estrutura dos dados

Cada linha representa uma sessão com campos como:

- `session_id`
- `user_id`
- `region`
- `user_segment`
- `device`
- `variant`
- `peak_hour`
- `rainy_weather`
- `trip_distance_km`
- `order_subtotal`
- `delivery_fee`
- `variable_cost`
- `converted_order`
- `cancelled_order`
- `net_completed_order`
- `gross_revenue`
- `contribution_margin`

### Técnicas utilizadas

- simulação de experimento A/B
- pricing experimentation
- medição de lift absoluto e relativo
- intervalo de confiança aproximado por diferença de médias
- análise de heterogeneidade por segmento
- decisão de rollout com guardrails

### Ferramentas e bibliotecas

- `Python`
- `csv`
- `json`
- `math`
- `pathlib`
- `random`
- `unittest`

### Contrato do relatório

O artefato [pricing_experiment_report.json](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/data/processed/pricing_experiment_report.json) expõe:

- desenho do experimento
- primary metric
- secondary metrics
- guardrails
- análise por região
- análise por segmento
- decisão final

### Resultados atuais

- `dataset_source = synthetic_dynamic_delivery_pricing_experiment`
- `session_count = 1500`
- `variant_counts = {'control': 741, 'treatment': 759}`
- `primary_metric_contribution_margin_per_session absolute_lift = -0.1969`
- `primary_metric_contribution_margin_per_session ci = [-0.3816, -0.0122]`
- `guardrail_checkout_conversion_rate absolute_lift = 0.034`
- `guardrail_cancellation_rate absolute_lift = 0.0098`
- `decision = needs_iteration`

Leitura honesta:

- a política melhora levemente a conversão;
- mas corrói margem demais;
- o segmento `price_sensitive` segue perdendo contribuição;
- então a decisão correta é iterar, não lançar.

### Arquivos principais

- [main.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/main.py)
- [src/data_factory.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/src/data_factory.py)
- [src/modeling.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/src/modeling.py)
- [tests/test_project.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/tests/test_project.py)

### Como executar

```bash
python3 main.py
python3 -m unittest discover -s tests -v
python3 -m py_compile main.py src/data_factory.py src/modeling.py tests/test_project.py
```

### Como defender em entrevista

> Eu desenharia o experimento com randomização por sessão de checkout, usaria contribution margin por sessão exposta como métrica principal e manteria conversão e cancelamento como guardrails. O ponto central é provar se a política melhora a economia do marketplace, não só a demanda.

## English

### Overview

`dynamic-delivery-pricing-ab-test` is a marketplace pricing experimentation project built around a common interview question: **how to design and evaluate a new delivery pricing strategy**.

The experiment compares:

- `control`
  - current delivery-fee policy
- `treatment`
  - dynamic policy with discounts for more price-sensitive sessions and mild peak adjustment

### Analytical objective

The real pricing problem is not simply “charge more” or “charge less.” The objective is to balance:

- conversion;
- unit economics;
- cancellations;
- overall marketplace health.

### Experimental design

- unit of randomization: `checkout_session`
- core hypothesis:
  - a more segmented policy can improve per-session economic efficiency

### Primary metric

- `contribution_margin_per_session`

### Secondary metrics

- `net_completed_order_rate`
- `avg_delivery_fee`

### Guardrails

- `checkout_conversion_rate`
- `cancellation_rate`

### Data structure

Each row represents one session with fields such as:

- `session_id`
- `user_id`
- `region`
- `user_segment`
- `device`
- `variant`
- `peak_hour`
- `rainy_weather`
- `trip_distance_km`
- `order_subtotal`
- `delivery_fee`
- `variable_cost`
- `converted_order`
- `cancelled_order`
- `net_completed_order`
- `gross_revenue`
- `contribution_margin`

### Techniques used

- A/B experiment simulation
- pricing experimentation
- absolute and relative lift
- approximate confidence interval using difference in means
- heterogeneous effect analysis by segment
- rollout decision with guardrails

### Tools and libraries

- `Python`
- `csv`
- `json`
- `math`
- `pathlib`
- `random`
- `unittest`

### Report contract

The artifact [pricing_experiment_report.json](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/data/processed/pricing_experiment_report.json) includes:

- experiment design
- primary metric
- secondary metrics
- guardrails
- regional analysis
- user-segment analysis
- final decision

### Current results

- `dataset_source = synthetic_dynamic_delivery_pricing_experiment`
- `session_count = 1500`
- `variant_counts = {'control': 741, 'treatment': 759}`
- `primary_metric_contribution_margin_per_session absolute_lift = -0.1969`
- `primary_metric_contribution_margin_per_session ci = [-0.3816, -0.0122]`
- `guardrail_checkout_conversion_rate absolute_lift = 0.034`
- `guardrail_cancellation_rate absolute_lift = 0.0098`
- `decision = needs_iteration`

### Main files

- [main.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/main.py)
- [src/data_factory.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/src/data_factory.py)
- [src/modeling.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/src/modeling.py)
- [tests/test_project.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/tests/test_project.py)

### How to run

```bash
python3 main.py
python3 -m unittest discover -s tests -v
python3 -m py_compile main.py src/data_factory.py src/modeling.py tests/test_project.py
```

### Interview framing

> I would randomize at the checkout-session level, use contribution margin per exposed session as the primary metric, and keep conversion and cancellation as guardrails. The key question is whether the policy improves marketplace economics, not just demand.
