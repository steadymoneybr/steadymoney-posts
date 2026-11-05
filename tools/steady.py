"""Vídeo animado com o mascote Steady, montado a partir de um roteiro (steady.json).

Uso: python3 tools/steady.py posts/AAAA-MM-DD-slug/steady.json posts/AAAA-MM-DD-slug/video.mp4 [--check]
  --check  só salva um quadro do meio de cada cena (video-check<N>.jpg) para conferir com Read.

Formato do roteiro (ver assets/steady/README-roteiro.md):
{
  "destaques": ["palavras", "em", "dourado"],
  "cenas": [
    {"dur": 3.6, "legenda": ["trecho 1", "trecho 2"], "pill": "PERGUNTA 1",
     "personagem": {"img": "P03.png", "x": 540, "h": 1000, "anim": "bob"},
     "objetos": [{"img": "O12.png", "x": 780, "w": 520, "y": 1300, "delay": 0, "pulse": 1.8, "brilho": true}],
     "efeitos": [{"tipo": "interrogacao"}],
     "placa": "12%"}
  ]
}
Imagens em assets/steady/ (fundo verde chroma). Trilha padrão em assets/trilha-padrao.m4a.
"""
import sys, math, random, subprocess, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets', 'steady')
TRACK = os.path.join(ROOT, 'assets', 'trilha-padrao.m4a')
W, H, FPS = 1080, 1920, 30
CREME = (251, 249, 244); NAVY = (27, 42, 65); GOLD = (156, 122, 60); GOLD_L = (226, 182, 84)
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
CHAR_H = 1000; FLOOR = 1430; TR = 0.2

# Superfícies onde dá pra escrever (coordenadas na imagem original 1024x1024).
# ang = inclinação em graus (positivo = sentido horário); o texto gira junto e fica centrado.
SURFACES = {'P16.png': dict(ang=3.6, cx=381, cy=494, maxw=250, maxh=180)}


def font(size, var=b'Bold'):
    f = ImageFont.truetype(LORA, size)
    try: f.set_variation_by_name(var)
    except Exception: pass
    return f

F_CAP = font(96); F_PILL = font(40); F_BRAND = font(34); F_Q = font(150)

# ---------- recorte do fundo verde ----------
_cache = {}
def cut(name, text=None):
    key = (name, text)
    if key in _cache: return _cache[key]
    im = np.array(Image.open(os.path.join(ASSETS, name)).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    d = g - np.maximum(r, b)
    a = np.clip(1 - (d - 35) / 70, 0, 1)
    a[a < 0.25] = 0
    g2 = np.minimum(g, np.maximum(r, b) + 8)
    img = Image.fromarray(np.dstack([r, g2, b, a * 255]).astype(np.uint8), 'RGBA')
    al = img.split()[3].filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(5))
    img.putalpha(Image.fromarray(np.minimum(np.array(img.split()[3]), np.array(al))))
    if text:
        write_on_surface(img, name, text)
    bb = img.getbbox(); img = img.crop(bb); img.info['bb'] = bb
    _cache[key] = img
    return img


def write_on_surface(img, name, text):
    s = SURFACES[name]
    size = 170
    while size > 40:
        f = font(size)
        tmp = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
        x0, y0, x1, y1 = tmp.multiline_textbbox((0, 0), text, font=f, align='center', spacing=size * 0.15)
        if x1 - x0 <= s['maxw'] and y1 - y0 <= s['maxh']: break
        size -= 6
    L = Image.new('RGBA', (700, 700), (0, 0, 0, 0))
    ImageDraw.Draw(L).multiline_text((350, 350), text, font=f, fill=NAVY + (255,), anchor='mm',
                                     align='center', spacing=size * 0.15)
    L = L.rotate(-s['ang'], resample=Image.BICUBIC)
    img.alpha_composite(L, (int(s['cx'] - 350), int(s['cy'] - 350)))


_scaled = {}
def sized(name, h=None, w=None, text=None):
    k = (name, h, w, text)
    if k in _scaled: return _scaled[k]
    im = cut(name, text)
    s = h / im.height if h else w / im.width
    out = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    out.info['bb'] = im.info['bb']; out.info['s'] = s
    _scaled[k] = out
    return out

# ---------- fundo ----------
def make_bg():
    rnd = np.random.default_rng(7)
    base = np.ones((H, W, 3)) * np.array(CREME)
    noise = rnd.normal(0, 3.2, (H // 2, W // 2))
    noise = np.array(Image.fromarray(noise.astype(np.float32)).resize((W, H), Image.BICUBIC))
    base += noise[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    vig = ((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2
    base -= vig[..., None] * 28
    bg = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(bg)
    d.text((W / 2, 150), 'STEADY MONEY', font=F_BRAND, fill=NAVY + (150,), anchor='mm')
    d.line((W / 2 - 70, 185, W / 2 + 70, 185), fill=GOLD + (170,), width=3)
    return bg
BG = make_bg()

def shadow(canvas, cx, y, w):
    sh = Image.new('RGBA', (int(w) + 80, 120), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((40, 30, int(w) + 40, 90), fill=(60, 50, 30, 45))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    canvas.alpha_composite(sh, (int(cx - w / 2 - 40), int(y - 60)))

def place(canvas, img, cx, bottom, alpha=1.0, rot=0, scale=1.0, floor=False):
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = img.split()[3].point(lambda v: int(v * alpha)); img = img.copy(); img.putalpha(a)
    if floor: shadow(canvas, cx, bottom, img.width * 0.75)
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(bottom - img.height)))

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def back(x):
    x = max(0.0, min(1.0, x)); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def pill(canvas, txt, t):
    k = back(t / 0.35)
    tw = F_PILL.getlength(txt)
    pw, ph = int(tw + 70), 74
    p = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=37, fill=NAVY)
    d.text((pw / 2, ph / 2 + 2), txt, font=F_PILL, fill=(255, 255, 255), anchor='mm')
    if k > 0.01:
        place(canvas, p, W / 2, 330 + ph, scale=max(0.05, k))

def heart(size, color=(214, 82, 82)):
    s = 4; im = Image.new('RGBA', (size * s, size * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    S = size * s; r = S * 0.27
    d.ellipse((S * 0.08, S * 0.12, S * 0.08 + 2 * r, S * 0.12 + 2 * r), fill=color, outline=(20, 20, 20), width=s * 3)
    d.ellipse((S * 0.92 - 2 * r, S * 0.12, S * 0.92, S * 0.12 + 2 * r), fill=color, outline=(20, 20, 20), width=s * 3)
    d.polygon([(S * 0.1, S * 0.42), (S * 0.9, S * 0.42), (S * 0.5, S * 0.92)], fill=color)
    d.line([(S * 0.1, S * 0.45), (S * 0.5, S * 0.92), (S * 0.9, S * 0.45)], fill=(20, 20, 20), width=s * 3)
    return im.resize((size, size), Image.LANCZOS)
HEART = heart(110)

def puff(r):
    im = Image.new('RGBA', (r * 2, r * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((0, 0, r * 2 - 1, r * 2 - 1), fill=(200, 196, 186, 200))
    return im.filter(ImageFilter.GaussianBlur(3))

def sparkle(c, cx, cy, tt):
    d_ = ImageDraw.Draw(c)
    for j in range(8):
        a = j * math.pi / 4; r1 = 60 + tt * 80; r2 = r1 + 30
        al = int(255 * max(0, 1 - tt / 0.8))
        if al > 0:
            d_.line((cx + math.cos(a) * r1, cy + math.sin(a) * r1, cx + math.cos(a) * r2, cy + math.sin(a) * r2),
                    fill=GOLD_L + (al,), width=8)

# ---------- personagem ----------
def char_pos(ch, t):
    x = ch.get('x', W / 2); anim = ch.get('anim', 'bob'); dy = 0; sc = 1.0
    if anim == 'bob': dy = math.sin(t * 2) * 4
    elif anim == 'shake': dy = math.sin(t * 6) * 3
    elif anim == 'jump': dy = -abs(math.sin(t * 4)) * 40
    elif anim == 'grow': sc = 0.94 + 0.06 * ease(t / 0.6)
    return x, FLOOR + ch.get('dy', 0) + dy, sc

def draw_char(c, ch, t, text=None):
    img = sized(ch['img'], h=ch.get('h', CHAR_H), text=text)
    x, y, sc = char_pos(ch, t)
    place(c, img, x, y, floor=True, scale=sc)
    return img, x, y

def src_to_dest(img, x, y, sx, sy):
    bb = img.info['bb']; s = img.info['s']
    return x - img.width / 2 + (sx - bb[0]) * s, y - img.height + (sy - bb[1]) * s

# ---------- efeitos ----------
def fx_interrogacao(c, e, t, d, ctx):
    k = back((t - e.get('delay', 0.6)) / 0.4)
    if k > 0.02:
        q = Image.new('RGBA', (200, 220), (0, 0, 0, 0))
        ImageDraw.Draw(q).text((100, 110), '?', font=F_Q, fill=NAVY, anchor='mm')
        place(c, q, e.get('x', 860), e.get('y', 560) + math.sin(t * 3) * 10, scale=k, rot=-10)

def fx_coracoes(c, e, t, d, ctx):
    rnd = random.Random(5)
    for i in range(6):
        tt = t - (e.get('delay', 1.2) + i * 0.22)
        if tt <= 0: continue
        x = e.get('x', 820) + rnd.uniform(-110, 110) + math.sin(tt * 4 + i) * 35
        place(c, HEART, x, 1250 - tt * 420, scale=0.6 + 0.4 * back(tt / 0.3), alpha=max(0, 1 - tt / 1.6))

def fx_poeira(c, e, t, d, ctx):
    img, x, y = ctx['char']
    wx, wy = src_to_dest(img, x, y, *e['de'])
    for i in range(5):
        tt = (t * 0.9 + i * 0.37) % 1.6
        if tt < 1.2:
            place(c, puff(int(18 + tt * 22)), wx + math.sin(i * 1.7 + tt * 3) * 30, wy - tt * 160, alpha=max(0, 1 - tt / 1.2))

def fx_chuva(c, e, t, d, ctx):
    shadow(c, W / 2, FLOOR, 400)
    obj = sized(e['img'], w=e.get('w', 230)); rnd = random.Random(3)
    for i in range(e.get('n', 7)):
        ang = rnd.uniform(0, 2 * math.pi); sp = rnd.uniform(500, 800); tt = max(0.0, t - i * 0.18)
        if tt <= 0: continue
        px = W / 2 + math.cos(ang) * sp * tt; py = 900 + math.sin(ang) * sp * tt * 0.8 - 120 * tt
        place(c, obj, px, py, rot=tt * 260 * (1 if i % 2 else -1), alpha=min(1, tt * 4))

def fx_envelopes(c, e, t, d, ctx):
    names = e.get('imgs', ['O07.png', 'O08.png', 'O09.png']); ys = [700, 1010, 1320]
    hits = e.get('hits', [2.6, 3.4, 4.2]); coin = sized('O01.png', w=90); x = e.get('x', 810)
    for i, (n, y) in enumerate(zip(names, ys)):
        k = back((t - 0.15 * i) / 0.4); h = hits[i]
        pulse = 1 + 0.12 * max(0, 1 - abs(t - h - 0.35) / 0.25)
        if k > 0.02: place(c, sized(n, w=270), x, y, scale=k * pulse)
        if h <= t < h + 0.45:
            tt = (t - h) / 0.45
            place(c, coin, x, y - 230 + tt * 120, alpha=1 - max(0, tt - 0.7) / 0.3)

def fx_cofrinho(c, e, t, d, ctx):
    pig = sized('O06.png', w=440); bag = sized('O11.png', w=330); coin = sized('O01.png', w=110)
    k1 = back(t / 0.4); k2 = back((t - 1.6) / 0.4)
    place(c, pig, 360, 1330, floor=True, scale=max(0.05, k1))
    tt = (t - 0.5) / 0.7
    if 0 <= tt <= 1:
        place(c, coin, 400, 760 + ease(tt) * 300, rot=tt * 180, alpha=1 - max(0, tt - 0.85) / 0.15)
    if 1.0 < t < 1.4:
        place(c, sized('O01.png', w=60), 400, 1010, alpha=1 - (t - 1.0) / 0.4, scale=1 + (t - 1.0))
    if k2 > 0.02: place(c, bag, 800, 1330, floor=True, scale=k2)
    ka = ease((t - 2.0) / 0.5)
    if ka > 0:
        d_ = ImageDraw.Draw(c); x1, x2 = 560, 560 + 120 * ka
        d_.line((x1, 1120, x2, 1120), fill=NAVY, width=12)
        if ka > 0.9: d_.polygon([(x2 + 30, 1120), (x2 - 5, 1095), (x2 - 5, 1145)], fill=NAVY)

FX = {'interrogacao': fx_interrogacao, 'coracoes': fx_coracoes, 'poeira': fx_poeira, 'chuva': fx_chuva,
      'envelopes': fx_envelopes, 'cofrinho': fx_cofrinho}

# ---------- cena ----------
def draw_scene(c, sc, t):
    d = sc['dur']; ctx = {}
    if sc.get('pill'): pill(c, sc['pill'], t)
    for e in sc.get('efeitos', []):
        if e['tipo'] in ('chuva', 'cofrinho'): FX[e['tipo']](c, e, t, d, ctx)
    if sc.get('personagem'):
        ctx['char'] = draw_char(c, sc['personagem'], t, text=sc.get('placa'))
    for o in sc.get('objetos', []):
        k = back((t - o.get('delay', 0)) / 0.4)
        p = o.get('pulse'); pulse = 1 + 0.08 * max(0, 1 - abs(t - p) / 0.3) if p is not None else 1
        if k > 0.02:
            img = sized(o['img'], w=o.get('w', 260))
            place(c, img, o['x'], o.get('y', FLOOR), floor=o.get('chao', True), scale=max(0.05, k) * pulse)
            if o.get('brilho') and p is not None and t > p - 0.2:
                sparkle(c, o['x'], o.get('y', FLOOR) - img.height * 0.47, t - p + 0.2)
    for e in sc.get('efeitos', []):
        if e['tipo'] not in ('chuva', 'cofrinho'): FX[e['tipo']](c, e, t, d, ctx)

def chunk_times(chunks, dur):
    if not chunks: return []
    wts = [max(2, len(ch.split())) + 0.6 for ch in chunks]; tot = sum(wts); out = []; acc = 0.15
    usable = dur - 0.3
    for ch, w in zip(chunks, wts):
        dd = usable * w / tot; out.append((acc, acc + dd, ch)); acc += dd
    return out

def caption(c, text, age, HL):
    k = back(age / 0.16)
    words = text.split(); sp = F_CAP.getlength(' ')
    widths = [F_CAP.getlength(w) for w in words]; tw = sum(widths) + sp * (len(words) - 1)
    pad = 30; layer = Image.new('RGBA', (int(tw + pad * 2), 170), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    x = pad
    for w_, ww in zip(words, widths):
        fill = GOLD_L if w_.strip('.,:;!?').lower() in HL else (255, 255, 255)
        d.text((x + 4, 92), w_, font=F_CAP, fill=(0, 0, 0, 90), anchor='lm')
        d.text((x, 85), w_, font=F_CAP, fill=fill, anchor='lm', stroke_width=9, stroke_fill=NAVY)
        x += ww + sp
    if layer.width > W - 60:
        s = (W - 60) / layer.width; layer = layer.resize((int(layer.width * s), int(layer.height * s)), Image.LANCZOS)
    place(c, layer, W / 2, 1700, scale=max(0.05, 0.85 + 0.15 * k))

def render(spec, out, check):
    scenes = list(spec['cenas'])
    first = scenes[0].get('personagem')
    if first:  # meio segundo final igual ao começo, pro vídeo emendar no loop
        scenes.append({'dur': 0.5, 'legenda': [], 'personagem': dict(first, anim='still'), 'placa': scenes[0].get('placa')})
    HL = {w.strip('.,:;!?').lower() for w in spec.get('destaques', [])}
    total = sum(s['dur'] for s in scenes); nfr = int(round(total * FPS))
    starts = []; acc = 0
    for s in scenes: starts.append(acc); acc += s['dur']
    caps = []
    for s, st in zip(scenes, starts):
        caps += [(st + a, st + b, txt) for a, b, txt in chunk_times(s.get('legenda', []), s['dur'])]
    def scene_frame(i, t):
        sc = scenes[i]; c = BG.copy(); draw_scene(c, sc, t)
        z = 1 + 0.045 * (t / sc['dur'])
        if z > 1.001:
            cw, ch = W / z, H / z
            c = c.crop((int((W - cw) / 2), int((H - ch) / 2 + 40 * (z - 1)), int((W + cw) / 2), int((H + ch) / 2 + 40 * (z - 1)))).resize((W, H), Image.BILINEAR)
        return c
    def full_frame(T):
        i = max(j for j, st in enumerate(starts) if st <= T + 1e-9); t = T - starts[i]
        frame = scene_frame(i, t)
        if i > 0 and t < TR:
            prev = scene_frame(i - 1, scenes[i - 1]['dur'] + t).filter(ImageFilter.GaussianBlur(14 * t / TR))
            frame = Image.blend(prev, frame.filter(ImageFilter.GaussianBlur(14 * (1 - t / TR))), t / TR)
        for a, b, txt in caps:
            if a <= T < b: caption(frame, txt, T - a, HL)
        return frame.convert('RGB')
    if check:
        for i, (s, st) in enumerate(zip(scenes[:-1] if first else scenes, starts)):
            # quadro no meio da última legenda da cena (mostra a cena já montada)
            ct = chunk_times(s.get('legenda', []), s['dur'])
            T = st + (ct[-1][0] + 0.25 if ct else s['dur'] / 2)
            full_frame(T).save(out.replace('.mp4', f'-check{i}.jpg').replace('video-check', 'video-check'), quality=85)
        print('check ok', len(scenes), 'cenas', round(total, 1), 's'); return
    tmp = out + '.noaudio.mp4'
    proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                             '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for f in range(nfr):
        proc.stdin.write(full_frame(f / FPS).tobytes())
    proc.stdin.close(); proc.wait()
    fa = total - 2
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-i', TRACK, '-filter_complex',
                    f'[1:a]atrim=0:{total},afade=t=in:d=0.5,afade=t=out:st={fa}:d=2,loudnorm=I=-20:TP=-3:LRA=7[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', out], check=True)
    os.remove(tmp)
    print(out + ':', round(total, 1), 's')

if __name__ == '__main__':
    spec_path, out = sys.argv[1], sys.argv[2]
    render(json.load(open(spec_path)), out, '--check' in sys.argv)
