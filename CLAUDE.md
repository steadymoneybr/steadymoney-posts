# Steady Money — rotina diária de posts

> **Tarefa da G5 Delay?** Siga `g5/G5.md` e ignore este arquivo (as regras abaixo são só da Steady Money).

Este repositório guarda as artes dos posts do Instagram/TikTok da Steady Money (@steadymoneybr).
As imagens ficam públicas via `https://raw.githubusercontent.com/steadymoneybr/steadymoney-posts/main/<caminho>` e o Metricool puxa por esse link.

## Fluxo diário (tarefa agendada das 11h20)

> **APROVAÇÃO PERMANENTE (Vini, 08/11/2026):** até o Vini avisar o contrário, todo conteúdo que passar na revisão independente (veredito APROVADO) está aprovado. Crie os dois posts já agendados (`draft: false`) no horário do dia, marque o tema como publicado, faça commit/push e mande ao Vini os slides, o vídeo e a legenda só para ciência ("✅ Revisado · já agendado para HH:MM"). Se a revisão não passar depois das rodadas, aí sim crie como rascunho e peça aprovação dizendo o que ficou pendente. Isso substitui os passos 6–8 (rascunho/esperar "aprovado") abaixo.

Formato (decidido pelo Vini em 29/10/2026): **Instagram recebe o carrossel; TikTok recebe o vídeo animado do mesmo conteúdo.**

**Horário (decidido pelo Vini em 01/11/2026):** dias úteis às **19:00**; **sábados, domingos e feriados nacionais às 14:00** (America/Sao_Paulo). Em todo este arquivo, "o horário do dia" é esse.
Feriados nacionais: 02/11/2026, 15/11/2026, 20/11/2026, 25/12/2026, 01/01/2027, 08/02/2027 e 09/02/2027 (Carnaval), 26/03/2027 (Sexta-feira Santa), 21/04/2027, 01/05/2027, 27/05/2027 (Corpus Christi), 07/09/2027, 12/10/2027, 02/11/2027, 15/11/2027, 20/11/2027, 25/12/2027. Atualize a lista no fim de 2027.

Todos os vídeos do TikTok usam a trilha padrão aprovada pelo Vini (`assets/trilha-padrao.m4a`, instrumental leve, 110 BPM, volume baixo). O `tools/video.py` já aplica sozinho. Não trocar a música sem ele pedir.

1. Escolha o primeiro tema com status `pendente` em `temas.md`.
2. Escreva um carrossel de **6 slides** (decidido pelo Vini em 01/11/2026): capa + 5 slides internos com etiqueta "N DE 5 — TEMA", um ponto por slide, e o último interno fecha com a pergunta para comentar. Use o espaço extra para exemplos práticos, não para encher linguiça. Os PDFs dos cursos NÃO ficam aqui: este repositório é público, então nunca suba cursos ou material pago. Use conhecimento geral correto e confira fatos que mudam (taxas, regras de IR, limites do FGC) com uma busca na web antes de afirmar.
3. Crie `posts/AAAA-MM-DD-slug/spec.json` no mesmo formato de `posts/2026-10-29-ordem-mercado-limitada/spec.json` e gere carrossel e vídeo:
   `python3 tools/render.py posts/AAAA-MM-DD-slug/spec.json posts/AAAA-MM-DD-slug`
   `python3 tools/video.py posts/AAAA-MM-DD-slug/spec.json posts/AAAA-MM-DD-slug/video.mp4`
4. Abra cada PNG e cada `video-check*.jpg` com Read e confira: nada cortado ou sobreposto, bullets idealmente em 1 linha (no máximo 2), sem erro de português. Não suba os `video-check*.jpg` (apague antes do commit).
4b. **Revisão independente (obrigatória):** escreva a legenda em `posts/AAAA-MM-DD-slug/legenda.txt` e chame um agente separado (ferramenta Agent, `subagent_type: general-purpose`) que NÃO viu a criação, passando só: "Siga as instruções de REVISAO.md e revise o post em posts/AAAA-MM-DD-slug/ (repositório em <caminho do clone>)." Se o veredito for AJUSTAR ou REPROVADO, corrija, gere de novo e rode a revisão outra vez (no máximo 3 rodadas). Se depois de 3 rodadas ainda houver problema, siga em frente e avise o Vini do que ficou pendente. Na mensagem de aprovação, inclua uma linha "✅ Revisado" (ou o que o revisor apontou e não foi resolvido). Se a ferramenta Agent não existir na sessão, faça você mesmo a revisão do REVISAO.md item por item antes de enviar.
5. Faça commit e push dos `.jpg` dos slides e do `video.mp4` (git user: `Claude <noreply@anthropic.com>`), confirme que os links raw respondem 200. **No Metricool use sempre os `.jpg`** para imagens: o TikTok recusa PNG.
6. Crie DOIS posts no Metricool (blogId `7725288`), ambos como **rascunho** (`draft: true`) para HOJE no **horário do dia** (19:00 em dia útil, 14:00 em fim de semana/feriado, America/Sao_Paulo):
   - Instagram: providers `instagram`, media = os 6 `.jpg` na ordem, `instagramData.type = POST`.
   - TikTok: providers `tiktok`, media = o `video.mp4`, `tiktokData` com `title` curto, `privacyOption PUBLIC_TO_EVERYONE`.
   A legenda é a mesma nos dois.
7. Envie ao Vini (SendUserFile com os 6 slides e o vídeo + SendUserMessage com a legenda) e peça aprovação. Mensagem curta, sem resumo extra no final.
8. Quando ele responder "aprovado": `updateScheduledPost` com `draft: false` nos dois posts (mantendo todo o resto). Depois do horário de publicação, se tiver como, confira com `getScheduledPosts` se algum status ficou `ERROR` e avise o Vini se ficou. Se pedir ajuste: ajuste, gere de novo, suba e atualize os posts (continuam rascunho até aprovar).
9. Marque o tema como `publicado AAAA-MM-DD` em `temas.md` e faça commit/push.

## Vídeo do TikTok: formato aprovado pelo Vini em 02/11/2026

- **Slides do vídeo enxutos:** o `tools/video.py` mostra só palavra grande + subtítulo + frase final (os bullets ficam só no carrossel), com tempo de leitura automático (~4s por slide). Final: "Educação financeira sem enrolação." / "Segue a gente.". Não mudar sem ele pedir.
- **Abertura com cena de IA (gancho de ~5s):** as cenas ficam em `assets/cenas/` (vídeos 9:16 gerados pelo Vini no PixVerse/Veo; o nome do arquivo diz o tema, ex.: `sm-piramide-desmoronando.mp4`). Se existir uma cena que combine com o tema do dia, adicione no `spec.json`:
  `"hook": {"clip": "assets/cenas/<arquivo>.mp4", "kicker": "<etiqueta curta, 2-3 palavras>", "l1": "<frase curta>", "l2": "<virada curta>"}`
  O `video.py` corta a marca d'água do topo, aplica degradê, etiqueta dourada, `l1` em Lora branco e `l2` em itálico dourado (aparece aos 2,5s). Padrão aprovado: kicker "Alerta de golpe", l1 "Parece ótimo.", l2 "Até desmoronar.". Cada linha precisa caber em 1 linha (máx. ~18 caracteres); tom de manchete, nada de texto amador ou caixa colorida. Confira o `video-check0.jpg` (a cena não pode brigar com o texto).
  Se nenhuma cena combinar, faça o vídeo sem `hook` e, na mensagem ao Vini, mande 1 prompt pronto para ele gerar a cena no PixVerse (inglês, assunto → ação → câmera → estilo "cute 3D animation", 9:16, 5s, negative prompt: `text, letters, words, logos, watermark, brand names, realistic human faces, blurry, distorted, low quality`) com o nome de arquivo sugerido `sm-<tema>.mp4`.

## Vídeo com o Steady (intercalado no TikTok, decidido pelo Vini em 05/11/2026)

**Status: ATIVO** (o Vini aprovou o vídeo de teste `posts/_teste-steady-5-perguntas/` em 06/11/2026; use-o como referência de estilo).
Quando ATIVO: o TikTok alterna os formatos. Olhe a pasta de post mais recente em `posts/` (ignorando as que começam com `_`): se ela tem `steady.json`, hoje é o formato de slides acima; se não tem, hoje é o Steady.
No dia do Steady: o carrossel do Instagram continua igual; para o TikTok escreva `posts/AAAA-MM-DD-slug/steady.json` com os mesmos 5 pontos, seguindo `assets/steady/README-roteiro.md`, e gere
`python3 tools/steady.py posts/AAAA-MM-DD-slug/steady.json posts/AAAA-MM-DD-slug/video.mp4 --check` (confira cada `video-check*.jpg`) e depois sem `--check`. Sem cena de IA (hook) e sem prompt de PixVerse nesses dias. O revisor confere os quadros do mesmo jeito. Por enquanto só legenda + trilha padrão (narração com voz do ElevenLabs entra quando o Vini mandar a chave de API).

## Regras da marca (obrigatórias)

- Conteúdo 100% educativo. Nunca recomendar ativo, corretora, fundo ou aposta. Nunca prometer lucro ou rendimento.
- **Nunca mencionar apostas esportivas** no feed, legenda ou hashtags.
- Linguagem simples, direta, tom informal ("pra", "você"). Tratar o leitor por "você".
- Não citar os cursos nem "link na bio" até o Vini avisar que as vendas na Eduzz começaram.

## Visual (o render.py já aplica)

- Fundo creme `#FBF9F4`, azul-marinho `#1B2A41`, dourado `#9C7A3C`, divisórias `#DED8C9`.
- Títulos em Lora Bold; textos em DejaVu Sans; frase de fechamento em Lora itálico cinza.
- Capa: etiqueta "EDUCAÇÃO FINANCEIRA", título serifado grande, subtítulo de 2 linhas, logo de barras, "Arraste para o lado →", "STEADY MONEY".
- **Títulos de comparação (decidido pelo Vini em 03/11/2026, vale sempre):** quando o título comparar duas coisas e couber inteiro em 1 linha, pode ficar tudo junto (ex.: `"Papel x Tijolo"`). Se precisar quebrar linha, o "x" fica sozinho na linha do meio, em 3 linhas simétricas (ex.: `"FII de tijolo<br>x<br>FII de papel"`). Nunca deixar o "x" colado numa das linhas quebradas (ex.: "FII de tijolo<br>x FII de papel"). Vale para a capa do carrossel e do vídeo.
- Slides internos: etiqueta "N DE 5 — TEMA", palavra/número grande, subtítulo em caixa alta, 3–4 bullets dourados, frase em itálico (slides 2 a 5) ou CTA "💬 Comenta aqui embaixo:" (slide 6).

## Padrão da legenda (igual aos posts já publicados)

```
<Pergunta/tema do post> 👆

<1 linha de contexto>:

1️⃣ <ponto 1>

2️⃣ <ponto 2>

3️⃣ <ponto 3>

4️⃣ <ponto 4>

5️⃣ <ponto 5>

<Frase de fechamento com a ideia central>

💬 Comenta aí: <pergunta>?

Salva esse post pra <motivo> 📎

#EducaçãoFinanceira #<Tema> #<Tema> #FinançasPessoais #DicasFinanceiras
```

Sempre 5 hashtags em CamelCase com acento. Sem linha de aviso/disclaimer no final.
