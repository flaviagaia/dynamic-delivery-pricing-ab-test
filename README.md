# dynamic-delivery-pricing-ab-test

## Português

`dynamic-delivery-pricing-ab-test` é um projeto de experimento de produto inspirado em uma pergunta clássica de cientista de dados da DoorDash: **como desenhar e avaliar uma nova estratégia de precificação de entrega**.

O projeto simula um teste A/B entre:

- `control`
  - política atual de taxa de entrega
- `treatment`
  - política dinâmica com desconto para sessões mais sensíveis a preço e leve ajuste em contexto de pico

## Objetivo analítico

O problema de pricing em delivery não é “cobrar mais” nem “cobrar menos”. O problema correto é equilibrar:

- conversão;
- margem unitária;
- cancelamento;
- saúde do marketplace.

Por isso, a métrica principal aqui não é fee média e nem order rate isoladamente. A métrica principal é:

- `contribution_margin_per_session`

Ela captura o efeito conjunto de:

- taxa cobrada;
- probabilidade de conversão;
- pedidos concluídos de fato;
- custo variável operacional.

## Base de dados

O runtime do projeto usa uma base sintética, porque experimentos reais de pricing de delivery não costumam ser públicos.

Referência pública usada:

- [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

Essa referência é usada apenas para inspirar variáveis comportamentais de marketplace, como:

- distância;
- tempo de pico;
- sensibilidade a tarifa;
- relação entre preço e demanda.

## O que o projeto faz

1. gera sessões sintéticas de checkout;
2. randomiza sessões entre `control` e `treatment`;
3. calcula a margem de contribuição por sessão;
4. mede conversão, cancelamento e pedidos concluídos;
5. estima lift absoluto, lift relativo e intervalo de confiança;
6. segmenta impacto por:
   - região
   - segmento de usuário
7. devolve recomendação final de rollout.

## Desenho experimental

### Unidade de randomização

- `checkout_session`

### Hipótese de produto

- reduzir fee em alguns contextos pode melhorar conversão;
- mas o experimento só é bom se a melhoria de demanda compensar a erosão de monetização unitária.

### Pergunta causal principal

- a nova política de delivery fee melhora `contribution_margin_per_session`?

## Métrica principal

- `contribution_margin_per_session`

## Métricas secundárias

- `net_completed_order_rate`
- `avg_delivery_fee`

## Guardrails

- `checkout_conversion_rate`
- `cancellation_rate`

Esses guardrails são importantes porque pricing pode:

- melhorar top-of-funnel;
- mas atrair pedidos economicamente ruins;
- ou aumentar cancelamento se a política gerar mismatch entre preço, expectativa e operação.

## Estrutura dos dados

Cada linha representa uma sessão de checkout com campos como:

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

Semântica analítica dos campos principais:

- `delivery_fee`
  - preço exposto ao cliente
- `variable_cost`
  - custo operacional variável para atender a sessão convertida
- `gross_revenue`
  - monetização bruta da plataforma naquela sessão
- `contribution_margin`
  - métrica econômica final usada no benchmark

## Técnicas utilizadas

- simulação de experimento A/B
- pricing experimentation
- medição de lift absoluto e relativo
- intervalo de confiança aproximado por diferença de médias
- análise de heterogeneidade por segmento
- decisão de lançamento com guardrails

## Ferramentas e bibliotecas

- `Python`
- `csv`
- `json`
- `math`
- `pathlib`
- `random`
- `unittest`

## Contrato do relatório

O artefato [pricing_experiment_report.json](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/data/processed/pricing_experiment_report.json) expõe:

- desenho do experimento
- primary metric
- secondary metrics
- guardrails
- análise por região
- análise por segmento de usuário
- decisão final `ship_treatment` ou `needs_iteration`

## Arquivos principais

- [main.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/main.py)
- [src/data_factory.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/src/data_factory.py)
- [src/modeling.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/src/modeling.py)
- [tests/test_project.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/tests/test_project.py)

## Resultados esperados do MVP

O treatment foi desenhado para:

- melhorar `contribution_margin_per_session`;
- preservar conversão em níveis aceitáveis;
- não aumentar cancelamento de forma relevante.

## Resultados atuais

- `dataset_source = synthetic_dynamic_delivery_pricing_experiment`
- `session_count = 1500`
- `variant_counts = {'control': 741, 'treatment': 759}`
- `primary_metric_contribution_margin_per_session absolute_lift = -0.1969`
- `primary_metric_contribution_margin_per_session ci = [-0.3816, -0.0122]`
- `guardrail_checkout_conversion_rate absolute_lift = 0.034`
- `guardrail_cancellation_rate absolute_lift = 0.0098`
- `decision = needs_iteration`

## Leitura esperada do experimento

Este projeto foi desenhado para permitir dois desfechos plausíveis:

- `ship_treatment`
- `needs_iteration`

Isso é intencional. Em pricing, uma boa análise não é “provar que o tratamento ganhou”, e sim mostrar se o ganho econômico realmente se sustenta depois de considerar conversão e cancelamento.

Leitura honesta:

- o tratamento melhora levemente a conversão;
- mas o desconto implícito corrói margem demais;
- o segmento `price_sensitive` ainda perde contribuição, mesmo com maior acessibilidade de preço;
- então a decisão correta neste sample é **iterar a política**, não lançar direto.

## Artefatos gerados

- [data/raw/pricing_sessions.csv](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/data/raw/pricing_sessions.csv)
- [data/raw/public_dataset_reference.json](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/data/raw/public_dataset_reference.json)
- [data/processed/pricing_experiment_report.json](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/dynamic-delivery-pricing-ab-test/data/processed/pricing_experiment_report.json)

## Como executar

```bash
python3 main.py
python3 -m unittest discover -s tests -v
python3 -m py_compile main.py src/data_factory.py src/modeling.py tests/test_project.py
```

## Como defender em entrevista

> Eu desenharia o experimento com randomização por sessão de checkout, usaria contribution margin por sessão exposta como métrica principal e manteria conversão e cancelamento como guardrails. Esse projeto implementa exatamente essa lógica e mostra como decidir se uma estratégia dinâmica de delivery fee melhora o negócio sem machucar o marketplace.

## English

`dynamic-delivery-pricing-ab-test` is a marketplace experimentation project designed around a common DoorDash-style data science question: **how to test and evaluate a new delivery pricing strategy**.

The repository simulates a pricing A/B test, optimizes for contribution margin per exposed session, tracks conversion and cancellations as guardrails, and returns a final launch recommendation.
