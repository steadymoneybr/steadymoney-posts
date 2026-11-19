"""Story-resumo do dia (1080x1920, decidido pelo Vini em 16/11/2026).

Uma imagem só, no visual da categoria: etiqueta + título do tema, 3 pontos-chave e a chamada
"Veja ... completo no feed" (a API não deixa pôr figurinha de link, então a chamada é só texto).

Uso: python3 tools/story.py posts/AAAA-MM-DD-slug/spec.json posts/AAAA-MM-DD-slug/story.jpg --tipo reel|carrossel

Os 3 pontos vêm de spec["story"]["pontos"] (recomendado, até ~30 caracteres cada, 1 linha); se não houver,
usa o "sub" dos 3 primeiros slides internos. spec["story"]["cta"] troca a chamada padrão.
"""
import json, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from categorias import cat, label, rgb
from video import F, clean, wrap, LORA, LORAI, DJ, DJB

W, H = 1080, 1920
CTA = {'reel': 'Veja o vídeo completo no feed', 'carrossel': 'Veja o post completo no feed'}


def main(spec_path, out, tipo):
    spec = json.load(open(spec_path))
    cover = next(s for s in spec['slides'] if s['type'] == 'cover')
    c = cat(cover)
    bg, ink, tagc, titc, subc = rgb(c['bg']), rgb(c['ink']), rgb(c['tag']), rgb(c['title']), rgb(c['sub'])
    escuro = sum(bg) < 300
    gold = rgb('#D9B66A') if escuro else rgb('#9C7A3C')
    linha = (70, 86, 110) if escuro else rgb('#DED8C9')

    st = spec.get('story', {})
    pontos = st.get('pontos') or [clean(s.get('sub', '')) for s in spec['slides'] if s['type'] == 'inner'][:3]
    cta = st.get('cta') or CTA[tipo]

    im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im)

    def center(txt, font, y, fill, spacing=0):
        if spacing:
            w = sum(d.textlength(ch, font=font) for ch in txt) + spacing * (len(txt) - 1)
            x = (W - w) / 2
            for ch in txt:
                d.text((x, y), ch, font=font, fill=fill); x += d.textlength(ch, font=font) + spacing
        else:
            d.text(((W - d.textlength(txt, font=font)) / 2, y), txt, font=font, fill=fill)

    # Zona segura do story: nada importante acima de ~250 nem abaixo de ~1650 (barras do Instagram).
    y = 300
    center(label(cover).upper(), F(DJB, 34), y, tagc, spacing=7)
    d.rectangle((W / 2 - 90, y + 58, W / 2 + 90, y + 62), fill=tagc)

    # Título (mesmas quebras da capa, encolhe se precisar)
    titulo = clean(cover['title'])  # respeita as quebras (<br>) da capa e encolhe até cada linha caber
    for size in range(112, 60, -4):
        fT = F(LORA, size, 'Bold'); TL = wrap(titulo, fT, 920)
        if len(TL) == len(titulo.split('\n')):
            break
    y = 440
    for ln in TL:
        # "x" sozinho na linha (títulos de comparação) sai na cor do "x" da categoria, como na capa
        center(ln, fT, y, rgb(c.get('vs', c['title'])) if ln.strip().lower() == 'x' else titc); y += int(fT.size * 1.18)

    # 3 pontos
    y += 70
    d.rectangle((W / 2 - 150, y, W / 2 + 150, y + 3), fill=linha); y += 90
    fN = F(LORA, 54, 'Bold')
    for i, p in enumerate(pontos[:3], 1):
        for sz in (46, 44, 42, 40):  # tenta caber em 1 linha antes de quebrar
            fP = F(DJ, sz); L = wrap(clean(p), fP, 820)
            if len(L) == 1:
                break
        h = len(L) * 58
        cx, cy = 140, y + h / 2
        d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), outline=gold, width=4)
        n = str(i); d.text((cx - d.textlength(n, font=fN) / 2, cy - 36), n, font=fN, fill=gold)
        yy = y
        for ln in L:
            d.text((215, yy), ln, font=fP, fill=ink); yy += 58
        y += max(h, 90) + 60

    # Chamada pro feed (botão)
    fC = F(DJB, 42); tw = d.textlength(cta, font=fC)
    bw, bh = tw + 110, 108; bx, by = (W - bw) / 2, max(1440, y + 40)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=54, fill=gold)
    d.text(((W - tw) / 2, by + 30), cta, font=fC, fill=bg if escuro else rgb('#FBF9F4'))
    center('@steadymoneybr', F(DJ, 34), by + bh + 28, subc)

    im.save(out, 'JPEG', quality=92)
    print(out)


if __name__ == '__main__':
    a = sys.argv[1:]
    tipo = 'reel'
    if '--tipo' in a:
        i = a.index('--tipo'); tipo = a[i + 1]; del a[i:i + 2]
    main(a[0], a[1], tipo)
