# Como escrever o roteiro do Steady (`steady.json`)

Gerador: `python3 tools/steady.py posts/AAAA-MM-DD-slug/steady.json posts/AAAA-MM-DD-slug/video.mp4`
(rode antes com `--check` e abra cada `video-check*.jpg` com Read). Exemplos: `assets/steady/piloto.json`
(piloto aprovado) e `posts/_teste-steady-5-perguntas/steady.json`.

## Estrutura
- `destaques`: palavras da legenda que ficam em dourado (sem pontuação; minúsculas ou não, tanto faz).
- `cenas`: lista em ordem. Cada cena:
  - `dur` (s): ~3,5 a 5,5. Vídeo total entre 35 e 50 s.
  - `legenda`: trechos curtos (2 a 4 palavras, no máx. ~22 caracteres), aparecem um por vez.
  - `pill` (opcional): etiqueta no topo, ex. "PASSO 1", "PERGUNTA 3".
  - `personagem`: `img`, `x` (centro, padrão 540), `h` (altura, padrão 1000; use ~880 quando divide a tela com objeto), `anim`: `bob` (padrão), `shake` (susto), `jump`, `grow`, `still`.
  - `objetos`: lista de `{img, x, w, y (base, padrão 1430), delay, pulse (instante do pulo), brilho (true = estrelinhas no pulse), chao}`.
  - `efeitos`: `interrogacao {x,y}`, `coracoes` (cena do "curte o vídeo"), `chuva {img}` (objeto voando), `poeira {de:[x,y] na imagem original]}`, `envelopes`, `cofrinho`.
  - `placa` (só com P16): texto escrito na placa. O gerador centraliza e gira junto com a inclinação da placa. Confira no check.
- Uma cena final de 0,5 s igual à primeira é adicionada sozinha (loop).

## Banco (assets/steady, fundo verde)
Poses: P01 frente, P03 pensativo, P04 confuso (coçando a cabeça), P05 assustado, P07 comemorando (pulando),
P08 apontando pra direita, P09 ideia (dedo pra cima), P10 joinha (piscando), P11 braços cruzados (suave),
P12 lendo papel, P13 carteira vazia, P14 celular (surpreso), P16 placa em branco, P18 relaxado na poltrona, P19 recibo comprido.
Objetos: O01 moeda, O02 pilha de moedas, O03 nota, O06 cofrinho, O07/O08/O09 envelopes (casa/cadeado/estrela),
O11 sacola de compras, O12 calendário, O13 cartão de crédito.

## Regras
- Mesmo conteúdo do carrossel do dia (os 5 pontos), linguagem falada e curta. Regras da marca valem igual.
- Personagem sozinho: centro. Com objeto: personagem em x≈260–300 (h 880) e objeto em x≈780.
- Nada sobreposto: objeto não pode cobrir mão/rosto do Steady; confira nos checks.
- Termine com a cena "Segue a Steady Money pra aprender isso de vez." e coloque uma cena de "curte o vídeo" no meio.
- Texto em superfície (placa/papel) sempre centrado e com a mesma inclinação da superfície.
