# Banco de imagens do Steady (mascote da Steady Money)

Personagem: bonequinho de palito, cabeça redonda branca, 3 fios de cabelo, sobrancelhas grossas,
óculos redondos finos, camiseta azul-marinho #1B2A41 (até a cintura), bermuda cinza-médio #8A8F96,
mãos brancas de cartoon, pés ovais pretos. Gerado pelo Vini no Gemini, fundo verde chroma #00FF00 (1024x1024).
Prompts completos: doc "Piloto de vídeo animado — Steady Money", aba "Banco de imagens".

## Onde paramos (03/11/2026)

Aprovadas: P01 (frente = referência principal), P03 pensativo, P04 confuso, P05 assustado, P08 apontando,
P12 lendo papel, P13 carteira vazia (com mariposa), P19 recibo comprido (pés grandes e manga longa, aceitável);
O01 moeda, O02 pilha de moedas, O03 nota, O06 cofrinho, O07/O08/O09 envelopes (casa/cadeado/estrela),
O11 sacola, O12 calendário. P19 refeita em 05/11 com pés menores (a anterior ficou em P19-v1.png).

Pendentes (o Vini estourou o limite do Gemini e vai terminar quando liberar):
- P18 relaxado na poltrona: versão de 05/11 salva (aceitável; bermuda virou 'tubos' na perna cruzada e apareceu uma orelha; o Vini pode refazer).
- Depois: montar o vídeo piloto ("Por que seu salário some antes do fim do mês"), 12 cenas, legenda palavra por palavra + trilha padrão; narração ainda não definida (versão só legenda é o plano B).

Notas técnicas: recorte por chroma (verdor g-max(r,b)); limpar manchas claras no topo de P12/O09;
poeira da P13 e folha da maçã da O11 ficam semitransparentes (animar poeira à parte).
Vistas 2-4 (3/4, perfil, costas) foram abandonadas: o Gemini não gira bem o boneco.

## Simulação (03/11/2026)
`tools/steady_video.py` gera o piloto (47s, só legenda + trilha padrão). O Vini aprovou o estilo ("ficou ótimo").
Próximos passos: ele termina P18/P10 (e o ajuste da P19), depois decidir a narração.

## Narração (decidido pelo Vini em 03/11/2026)
Quando ele mandar as poses restantes (P18, P10 e o ajuste da P19): montar o piloto em 2 versões para comparar,
(a) só legenda + trilha padrão e (b) com voz de IA (ex.: ElevenLabs; ele precisa passar a chave de API).
Se usar voz de IA, marcar o vídeo como conteúdo de IA no TikTok (isAigc).

## Poses completas (05/11/2026)
P10 joinha (cena 9, calendário) e P18 poltrona (cena 10) entraram no `steady_video.py`. Versão (a) do piloto (só legenda + trilha) gerada e enviada ao Vini. Versão (b) com voz de IA aguarda a chave de API.
