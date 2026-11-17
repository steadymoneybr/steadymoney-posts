# Base de pesquisa — Tráfego da Steady Money

Mantida pelo agente de tráfego (`TRAFEGO.md`). Seções fixas = o que sabemos hoje (atualize e substitua o que ficar velho). Diário = últimas 14 entradas.

## Benchmarks (infoproduto / educação financeira, Brasil, Meta Ads)
_Atualizado em 16/11/2026. Ainda não há fonte brasileira com dado de nicho e metodologia aberta; trate as faixas como referência, não meta._
- **CPM Brasil (todos os nichos):** mediana ~US$ 3,46 (jul/2025–jul/2026), com picos de US$ 6–7,45 em mai–jul/2026 e mínimo de US$ 1,77 (ago/2025). Fonte: Superads, base própria (>US$ 3 bi em gasto), 2026.
- **CPM infoproduto (BR):** projeção R$ 38 (faixa R$ 28–60). Fonte: Trafius, mai/2026 — sem base de dados citada, usar com cautela.
- **CTR Brasil (todos os nichos):** mediana mensal ~1,70% (faixa 0,58%–3,0%), jul/2025–jul/2026. Fonte: Superads, 2026. Regra de bolso: CTR (link) < 0,8% indica problema de criativo/oferta (Trafius, 2026, sem fonte).
- **Educação (EUA, referência):** campanha de tráfego CTR 1,45% / CPC US$ 0,86; campanha de leads CTR 1,86% / CPC US$ 1,65 / conversão 10,08% / CPL US$ 28,22. **Finanças (EUA, tráfego):** CTR 0,98% / CPC US$ 1,22 (o CPC mais caro da lista). Fonte: WordStream/LocaliQ 2025 (dados abr/2024–jun/2025, medianas).
- **Custo por conversa iniciada no WhatsApp (BR):** infoproduto R$ 5–15; e-commerce R$ 3–8; serviços locais R$ 8–25. Fonte: Trafius, abr/2026 (estimativa, sem base citada).
- **Página de vendas de curso online:** conversão mediana ~18,3% (Unbounce, edição 2021 — antigo). Abandono de checkout ~70,2% (Baymard, atualizado set/2025).
- **Conversa → venda no X1:** sem número com fonte ainda. Buscar de novo nas próximas segundas.

## Concorrentes e anúncios observados
_(formato · gancho · oferta · CTA · há quanto tempo no ar)_

## Criativos e ganchos em alta
_(o que funciona / o que está saturado)_

## Plataforma e políticas (Meta Ads, finanças, Click-to-WhatsApp)
- **Preço da API do WhatsApp (desde 01/10/2026):** mensagens de serviço (respostas livres de humano, automação ou IA de terceiros dentro da janela de 24h) passaram a ser cobradas por mensagem entregue: ~R$ 0,035 (US$ 0,0068) cada, com **1.000 grátis por número/mês**. Utilidade dentro da janela também passou a ser cobrada (~R$ 0,035); marketing ~R$ 0,32. Sem meio de pagamento cadastrado, a Meta não entrega mensagens de serviço. Fontes: Letalk (set/2026) e Yavendio (out/2026), citando o rate card da Meta de 01/10/2026.
- **Click-to-WhatsApp continua com janela grátis:** conversa iniciada pelo anúncio, com resposta da empresa em até 24h, abre janela de 72h de entrega gratuita (inclusive templates). Fontes: Letalk e Chatlabs, 2026 (Yavendio fala em "até 7 dias" — conflito; confirmar no doc da Meta).
- **WhatsApp Business App (celular, sem API):** não foi afetado pela cobrança (Letalk, Yavendio, 2026).
- Meta Business Agent (IA da própria Meta) cobra por token desde 01/08/2026: US$ 2 por milhão (Chatlabs, 2026).
- Implicação pro funil: o tráfego por anúncio CTWA mantém as mensagens grátis na janela; o custo novo pesa nos follow-ups fora da janela e em leads que chegam por orgânico. Entra no "custo da IA" da fórmula de CPA máximo.

## Oferta e conversa no X1 (abertura, qualificação, objeções, upsell)

## Estrutura e orçamento de teste

## Ideias de teste
_(hipótese · como testar · métrica de sucesso)_
- **Responder todo lead de anúncio em < 24h (de preferência em minutos):** hipótese: garante a janela grátis de 72h e aumenta a taxa de resposta. Como: o agente de IA responde na hora; medir tempo da 1ª resposta. Sucesso: 100% dos leads respondidos em < 24h e ≥ 60% respondendo de volta.
- **Corte inicial por custo por conversa:** hipótese: low ticket só se paga com conversa barata. Como: no 1º teste, matar criativo com custo por conversa > R$ 15 depois de ~R$ 30 gastos (teto da faixa de infoproduto, Trafius 2026). Sucesso: pelo menos 1 criativo abaixo de R$ 8 por conversa.
- **CTR mínimo como alarme:** criativo com CTR (link) < 0,8% após ~1.000 impressões vai para revisão de gancho. Sucesso: média dos criativos ≥ 1,5% (perto da mediana BR de 2026).

## Diário
- 2026-11-16 (seg, benchmarks): 1ª pesquisa. CPM Brasil mediano ~US$ 3,46 com alta no meio de 2026 (Superads); CTR BR ~1,7%. Custo por conversa de infoproduto estimado em R$ 5–15 (Trafius, sem base). Finanças tem CPC alto nos EUA (WordStream 2025). Desde 01/10/2026 a API do WhatsApp cobra ~R$ 0,035 por mensagem de serviço (1.000 grátis/mês), mas a janela de 72h do Click-to-WhatsApp segue grátis — responder o lead em < 24h é obrigatório. Falta número com fonte de conversa → venda no X1.
- 2026-11-16: base criada.
