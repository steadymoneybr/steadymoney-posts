# Steady Money — rotina diária de posts

> **Tarefa da G5 Delay?** Siga `g5/G5.md` e ignore este arquivo (as regras abaixo são só da Steady Money).

Este repositório guarda as artes dos posts do Instagram/TikTok da Steady Money (@steadymoneybr).
As imagens ficam públicas via `https://raw.githubusercontent.com/steadymoneybr/steadymoney-posts/main/<caminho>` e o Metricool puxa por esse link.

## Fluxo diário (tarefa agendada das 11h)

Formato (decidido pelo Vini em 29/10/2026): **Instagram recebe o carrossel; TikTok recebe o vídeo animado do mesmo conteúdo.** Os dois saem às 19h.

Todos os vídeos do TikTok usam a trilha padrão aprovada pelo Vini (`assets/trilha-padrao.m4a`, instrumental leve, 110 BPM, volume baixo). O `tools/video.py` já aplica sozinho. Não trocar a música sem ele pedir.

1. Escolha o primeiro tema com status `pendente` em `temas.md`.
2. Escreva um carrossel de 4 slides: capa + 3 slides internos (o último com a pergunta para comentar). Os PDFs dos cursos NÃO ficam aqui: este repositório é público, então nunca suba cursos ou material pago. Use conhecimento geral correto e confira fatos que mudam (taxas, regras de IR, limites do FGC) com uma busca na web antes de afirmar.
3. Crie `posts/AAAA-MM-DD-slug/spec.json` no mesmo formato de `posts/2026-10-29-ordem-mercado-limitada/spec.json` e gere carrossel e vídeo:
   `python3 tools/render.py posts/AAAA-MM-DD-slug/spec.json posts/AAAA-MM-DD-slug`
   `python3 tools/video.py posts/AAAA-MM-DD-slug/spec.json posts/AAAA-MM-DD-slug/video.mp4`
4. Abra cada PNG e cada `video-check*.jpg` com Read e confira: nada cortado ou sobreposto, bullets idealmente em 1 linha (no máximo 2), sem erro de português. Não suba os `video-check*.jpg` (apague antes do commit).
4b. **Revisão independente (obrigatória):** escreva a legenda em `posts/AAAA-MM-DD-slug/legenda.txt` e chame um agente separado (ferramenta Agent, `subagent_type: general-purpose`) que NÃO viu a criação, passando só: "Siga as instruções de REVISAO.md e revise o post em posts/AAAA-MM-DD-slug/ (repositório em <caminho do clone>)." Se o veredito for AJUSTAR ou REPROVADO, corrija, gere de novo e rode a revisão outra vez (no máximo 3 rodadas). Se depois de 3 rodadas ainda houver problema, siga em frente e avise o Vini do que ficou pendente. Na mensagem de aprovação, inclua uma linha "✅ Revisado" (ou o que o revisor apontou e não foi resolvido). Se a ferramenta Agent não existir na sessão, faça você mesmo a revisão do REVISAO.md item por item antes de enviar.
5. Faça commit e push dos `.jpg` dos slides e do `video.mp4` (git user: `Claude <noreply@anthropic.com>`), confirme que os links raw respondem 200. **No Metricool use sempre os `.jpg`** para imagens: o TikTok recusa PNG.
6. Crie DOIS posts no Metricool (blogId `7725288`), ambos como **rascunho** (`draft: true`) para HOJE às **19:00 America/Sao_Paulo**:
   - Instagram: providers `instagram`, media = os 4 `.jpg`, `instagramData.type = POST`.
   - TikTok: providers `tiktok`, media = o `video.mp4`, `tiktokData` com `title` curto, `privacyOption PUBLIC_TO_EVERYONE`.
   A legenda é a mesma nos dois.
7. Envie ao Vini (SendUserFile com os 4 slides e o vídeo + SendUserMessage com a legenda) e peça aprovação. Mensagem curta, sem resumo extra no final.
8. Quando ele responder "aprovado": `updateScheduledPost` com `draft: false` nos dois posts (mantendo todo o resto). Depois do horário de publicação, se tiver como, confira com `getScheduledPosts` se algum status ficou `ERROR` e avise o Vini se ficou. Se pedir ajuste: ajuste, gere de novo, suba e atualize os posts (continuam rascunho até aprovar).
9. Marque o tema como `publicado AAAA-MM-DD` em `temas.md` e faça commit/push.

## Regras da marca (obrigatórias)

- Conteúdo 100% educativo. Nunca recomendar ativo, corretora, fundo ou aposta. Nunca prometer lucro ou rendimento.
- **Nunca mencionar apostas esportivas** no feed, legenda ou hashtags.
- Linguagem simples, direta, tom informal ("pra", "você"). Tratar o leitor por "você".
- Não citar os cursos nem "link na bio" até o Vini avisar que as vendas na Eduzz começaram.

## Visual (o render.py já aplica)

- Fundo creme `#FBF9F4`, azul-marinho `#1B2A41`, dourado `#9C7A3C`, divisórias `#DED8C9`.
- Títulos em Lora Bold; textos em DejaVu Sans; frase de fechamento em Lora itálico cinza.
- Capa: etiqueta "EDUCAÇÃO FINANCEIRA", título serifado grande, subtítulo de 2 linhas, logo de barras, "Arraste para o lado →", "STEADY MONEY".
- Slides internos: etiqueta "N DE 3 — TEMA", palavra/número grande, subtítulo em caixa alta, 3–4 bullets dourados, frase em itálico (slides 2 e 3) ou CTA "💬 Comenta aqui embaixo:" (slide 4).

## Padrão da legenda (igual aos posts já publicados)

```
<Pergunta/tema do post> 👆

<1 linha de contexto>:

1️⃣ <ponto 1>

2️⃣ <ponto 2>

3️⃣ <ponto 3>

<Frase de fechamento com a ideia central>

💬 Comenta aí: <pergunta>?

Salva esse post pra <motivo> 📎

#EducaçãoFinanceira #<Tema> #<Tema> #FinançasPessoais #DicasFinanceiras
```

Sempre 5 hashtags em CamelCase com acento. Sem linha de aviso/disclaimer no final.
