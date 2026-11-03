"""Vídeo animado com o mascote Steady (formato aprovado pelo Vini em 03/11/2026, simulação do piloto).
Uso: python3 tools/steady_video.py assets/steady assets/trilha-padrao.m4a <saida.mp4> [--check]
As cenas e legendas estão na lista SCENES no fim do arquivo."""
import sys, math, random, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ASSETS, TRACK, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CHECK = '--check' in sys.argv
W, H, FPS = 1080, 1920, 30
CREME = (251, 249, 244); NAVY = (27, 42, 65); GOLD = (156, 122, 60); GOLD_L = (226, 182, 84)
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'

def font(size, var=b'Bold'):
    f = ImageFont.truetype(LORA, size)
    try: f.set_variation_by_name(var)
    except Exception: pass
    return f

F_CAP = font(96); F_PILL = font(40); F_BRAND = font(34); F_Q = font(150)

# ---------- recorte do fundo verde ----------
_cache = {}
def cut(name):
    if name in _cache: return _cache[name]
    im = np.array(Image.open(os.path.join(ASSETS, name)).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    d = g - np.maximum(r, b)
    a = np.clip(1 - (d - 35) / 70, 0, 1)
    a[a < 0.25] = 0                      # limpa manchas fracas do fundo
    g2 = np.minimum(g, np.maximum(r, b) + 8)  # tira o reflexo verde das bordas
    rgba = np.dstack([r, g2, b, a * 255]).astype(np.uint8)
    img = Image.fromarray(rgba, 'RGBA')
    # remove ilhas pequenas: mantém só pixels com alfa forte num raio
    al = img.split()[3].filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(5))
    img.putalpha(Image.fromarray(np.minimum(np.array(img.split()[3]), np.array(al))))
    bb = img.getbbox(); img = img.crop(bb); img.info['bb'] = bb
    _cache[name] = img
    return img

_scaled = {}
def sized(name, h=None, w=None):
    k = (name, h, w)
    if k in _scaled: return _scaled[k]
    im = cut(name)
    if h: s = h / im.height
    else: s = w / im.width
    out = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
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

def pill(canvas, n, t):
    k = back(t / 0.35)
    txt = f'PASSO {n}'
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

# ---------- cenas ----------
CHAR_H = 1000; FLOOR = 1430

def s_wallet(c, t, d):
    img = sized('P13.png', h=CHAR_H)
    bob = math.sin(t * 2.2) * 4
    place(c, img, W / 2, FLOOR + bob, floor=True)
    bb = cut('P13.png').info['bb']; x0 = W / 2 - img.width / 2; sc = img.height / cut('P13.png').height
    wx, wy = x0 + (655 - bb[0]) * sc, FLOOR - img.height + (450 - bb[1]) * sc  # boca da carteira
    for i in range(5):
        tt = (t * 0.9 + i * 0.37) % 1.6
        if tt < 1.2:
            p = puff(int(18 + tt * 22))
            place(c, p, wx + math.sin(i * 1.7 + tt * 3) * 30, wy - tt * 160, alpha=max(0, 1 - tt / 1.2))

def s_think(c, t, d):
    place(c, sized('P03.png', h=CHAR_H), W / 2, FLOOR + math.sin(t * 2) * 4, floor=True)
    k = back((t - 0.6) / 0.4)
    if k > 0.02:
        q = Image.new('RGBA', (200, 220), (0, 0, 0, 0))
        ImageDraw.Draw(q).text((100, 110), '?', font=F_Q, fill=NAVY, anchor='mm')
        place(c, q, 860, 560 + math.sin(t * 3) * 10, scale=k, rot=-10)

def s_notes(c, t, d):
    shadow(c, W / 2, FLOOR, 400)
    note = sized('O03.png', w=230)
    rnd = random.Random(3)
    for i in range(7):
        ang = rnd.uniform(0, 2 * math.pi); sp = rnd.uniform(500, 800); t0 = i * 0.18
        tt = max(0.0, t - t0)
        if tt <= 0: continue
        x = W / 2 + math.cos(ang) * sp * tt; y = 900 + math.sin(ang) * sp * tt * 0.8 - 120 * tt
        place(c, note, x, y, rot=tt * 260 * (1 if i % 2 else -1), alpha=min(1, tt * 4))
    place(c, sized('P04.png', h=CHAR_H), W / 2, FLOOR)

def s_read(c, t, d):
    pill(c, 1, t)
    place(c, sized('P12.png', h=CHAR_H), W / 2, FLOOR + math.sin(t * 2) * 4, floor=True)

def s_receipt(c, t, d):
    pill(c, 2, t)
    img = sized('P19.png', h=CHAR_H)
    k = ease(t / 0.6)
    place(c, img, W / 2 + 20, FLOOR, floor=True, scale=0.94 + 0.06 * k)

def s_like(c, t, d):
    place(c, sized('P05.png', h=CHAR_H), W / 2, FLOOR + math.sin(t * 6) * 3, floor=True)
    rnd = random.Random(5)
    for i in range(6):
        t0 = 1.2 + i * 0.22; tt = t - t0
        if tt <= 0: continue
        x = 820 + rnd.uniform(-110, 110) + math.sin(tt * 4 + i) * 35
        place(c, HEART, x, 1250 - tt * 420, scale=0.6 + 0.4 * back(tt / 0.3), alpha=max(0, 1 - tt / 1.6))

def envelopes(c, t, hits):
    names = ['O07.png', 'O08.png', 'O09.png']; ys = [700, 1010, 1320]
    coin = sized('O01.png', w=90)
    for i, (n, y) in enumerate(zip(names, ys)):
        k = back((t - 0.15 * i) / 0.4)
        h = hits[i]
        pulse = 1 + 0.12 * max(0, 1 - abs(t - h - 0.35) / 0.25) if h is not None else 1
        if k > 0.02:
            place(c, sized(n, w=270), 810, y, scale=k * pulse)
        if h is not None and h <= t < h + 0.45:
            tt = (t - h) / 0.45
            place(c, coin, 810, y - 230 + tt * 120, alpha=1 - max(0, tt - 0.7) / 0.3)

def s_split(c, t, d, hits=(2.6, 3.4, 4.2)):
    pill(c, 3, t)
    place(c, sized('P08.png', h=880), 330, FLOOR, floor=True)
    envelopes(c, t, hits)

def s_piggy(c, t, d):
    pill(c, 4, t)
    pig = sized('O06.png', w=440); bag = sized('O11.png', w=330); coin = sized('O01.png', w=110)
    k1 = back(t / 0.4); k2 = back((t - 1.6) / 0.4)
    place(c, pig, 360, 1330, floor=True, scale=max(0.05, k1))
    tt = (t - 0.5) / 0.7
    if 0 <= tt <= 1:
        place(c, coin, 400, 760 + ease(tt) * 300, rot=tt * 180, alpha=1 - max(0, tt - 0.85) / 0.15)
    if 1.0 < t < 1.4:
        place(c, sized('O01.png', w=60), 400, 1010, alpha=1 - (t - 1.0) / 0.4, scale=1 + (t - 1.0))
    if k2 > 0.02:
        place(c, bag, 800, 1330, floor=True, scale=k2)
    # seta "primeiro -> depois"
    ka = ease((t - 2.0) / 0.5)
    if ka > 0:
        d_ = ImageDraw.Draw(c); x1, x2 = 560, 560 + 120 * ka
        d_.line((x1, 1120, x2, 1120), fill=NAVY, width=12)
        if ka > 0.9: d_.polygon([(x2 + 30, 1120), (x2 - 5, 1095), (x2 - 5, 1145)], fill=NAVY)

def s_calendar(c, t, d):
    pill(c, 5, t)
    place(c, sized('P01.png', h=860), 300, FLOOR, floor=True)
    cal = sized('O12.png', w=520)
    k = back(t / 0.45)
    pulse = 1 + 0.08 * max(0, 1 - abs(t - 1.8) / 0.3)
    place(c, cal, 740, 1300, scale=max(0.05, k) * pulse, floor=True)
    if t > 1.6:  # brilho no check
        tt = t - 1.6; d_ = ImageDraw.Draw(c); cx, cy = 740, 1300 - cal.height * 0.47
        for j in range(8):
            a = j * math.pi / 4; r1 = 60 + tt * 80; r2 = r1 + 30
            al = int(255 * max(0, 1 - tt / 0.8))
            if al > 0:
                d_.line((cx + math.cos(a) * r1, cy + math.sin(a) * r1, cx + math.cos(a) * r2, cy + math.sin(a) * r2), fill=GOLD_L + (al,), width=8)

def s_balance(c, t, d):
    place(c, sized('P01.png', h=CHAR_H), W / 2, FLOOR + math.sin(t * 2) * 4, floor=True)
    k1 = back((t - 0.3) / 0.4); k2 = back((t - 0.7) / 0.4)
    if k1 > 0.02: place(c, sized('O06.png', w=260), 190, FLOOR, floor=True, scale=k1)
    if k2 > 0.02: place(c, sized('O11.png', w=230), 890, FLOOR, floor=True, scale=k2)

def s_path(c, t, d):
    place(c, sized('P08.png', h=900), 290, FLOOR, floor=True)
    pts = [(640, 1430, 120), (760, 1270, 150), (870, 1080, 190), (960, 860, 230)]
    for i, (x, y, w) in enumerate(pts):
        k = back((t - 0.4 - i * 0.35) / 0.4)
        if k > 0.02: place(c, sized('O02.png', w=w), x, y, scale=k, floor=True)

def s_cta(c, t, d):
    place(c, sized('P08.png', h=CHAR_H), W / 2, FLOOR + math.sin(t * 2) * 4, floor=True)

def s_loop(c, t, d):
    place(c, sized('P13.png', h=CHAR_H), W / 2, FLOOR, floor=True)

HL = {'40', 'segundos', 'salário', 'destino.', 'Passo', 'um:', 'dois:', 'três:', 'quatro:', 'cinco:',
      'curte', 'reserva', 'Steady', 'Money', 'privar.'}
SCENES = [
    (s_wallet, 4.2, ['Em 40 segundos', 'você vai entender', 'por que seu salário', 'some antes', 'do fim do mês.']),
    (s_think, 3.6, ['E não,', 'o problema', 'quase nunca é', 'ganhar pouco.']),
    (s_notes, 3.0, ['É dinheiro', 'sem destino.']),
    (s_read, 3.8, ['Passo um:', 'anota tudo', 'que entra no mês.']),
    (s_receipt, 4.4, ['Passo dois:', 'anota tudo que sai,', 'até o cafezinho', 'e o delivery.']),
    (s_like, 3.6, ['Se você já', 'se assustou', 'com essa conta,', 'curte o vídeo.']),
    (s_split, 5.0, ['Passo três:', 'dá um destino', 'pra cada real:', 'contas,', 'reserva', 'e lazer.']),
    (s_piggy, 4.8, ['Passo quatro:', 'separa a reserva', 'no dia que', 'o salário cai,', 'não no fim do mês.']),
    (s_calendar, 3.8, ['Passo cinco:', 'uma vez por mês,', 'revisa e ajusta.']),
    (s_balance, 3.4, ['Organizar dinheiro', 'não é sobre', 'se privar.']),
    (s_path, 3.6, ['É sobre saber', 'pra onde', 'ele vai.']),
    (s_cta, 3.6, ['Segue a', 'Steady Money', 'pra aprender', 'isso de vez.']),
    (s_loop, 0.5, []),
]

def chunk_times(chunks, dur):
    if not chunks: return []
    wts = [max(2, len(ch.split())) + 0.6 for ch in chunks]; tot = sum(wts); out = []; acc = 0.15
    usable = dur - 0.3
    for ch, w in zip(chunks, wts):
        dd = usable * w / tot; out.append((acc, acc + dd, ch)); acc += dd
    return out

def caption(c, text, age):
    k = back(age / 0.16)
    words = text.split(); sp = F_CAP.getlength(' ')
    widths = [F_CAP.getlength(w) for w in words]; tw = sum(widths) + sp * (len(words) - 1)
    pad = 30; layer = Image.new('RGBA', (int(tw + pad * 2), 170), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    x = pad
    for w_, ww in zip(words, widths):
        fill = GOLD_L if w_ in HL else (255, 255, 255)
        d.text((x + 4, 92), w_, font=F_CAP, fill=(0, 0, 0, 90), anchor='lm')
        d.text((x, 85), w_, font=F_CAP, fill=fill, anchor='lm', stroke_width=9, stroke_fill=NAVY)
        x += ww + sp
    if layer.width > W - 60:
        s = (W - 60) / layer.width; layer = layer.resize((int(layer.width * s), int(layer.height * s)), Image.LANCZOS)
    place(c, layer, W / 2, 1700, scale=max(0.05, 0.85 + 0.15 * k))

def render():
    total = sum(d for _, d, _ in SCENES)
    nfr = int(round(total * FPS))
    starts = []; acc = 0
    for s in SCENES: starts.append(acc); acc += s[1]
    caps = []
    for (fn, dur, chunks), st in zip(SCENES, starts):
        caps += [(st + a, st + b, txt) for a, b, txt in chunk_times(chunks, dur)]
    tmp = OUT + '.noaudio.mp4'
    proc = None
    if not CHECK:
        proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                                 '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                                 '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    def scene_frame(i, t):
        fn, dur, _ = SCENES[i]
        c = BG.copy(); fn(c, t, dur)
        z = 1 + 0.045 * (t / dur)  # zoom lento
        if z > 1.001:
            cw, ch = W / z, H / z; c = c.crop((int((W - cw) / 2), int((H - ch) / 2 + 40 * (z - 1)), int((W + cw) / 2), int((H + ch) / 2 + 40 * (z - 1)))).resize((W, H), Image.BILINEAR)
        return c
    checks = [1.0, 5.5, 9.0, 12.5, 17.0, 21.5, 26.8, 30.0, 34.5, 38.0, 42.0, 45.0]
    TR = 0.2
    for f in range(nfr):
        T = f / FPS
        if CHECK and not any(abs(T - x) < 0.5 / FPS for x in checks): continue
        i = max(j for j, st in enumerate(starts) if st <= T + 1e-9)
        t = T - starts[i]
        frame = scene_frame(i, t)
        if i > 0 and t < TR:  # transição com desfoque
            prev = scene_frame(i - 1, SCENES[i - 1][1] + t).filter(ImageFilter.GaussianBlur(14 * t / TR))
            frame = Image.blend(prev, frame.filter(ImageFilter.GaussianBlur(14 * (1 - t / TR))), t / TR)
        for a, b, txt in caps:
            if a <= T < b: caption(frame, txt, T - a)
        rgb = frame.convert('RGB')
        if CHECK:
            rgb.save(OUT.replace('.mp4', f'-check{checks.index(min(checks, key=lambda x: abs(x - T)))}.jpg'), quality=85)
        else:
            proc.stdin.write(rgb.tobytes())
    if CHECK: return
    proc.stdin.close(); proc.wait()
    fa = total - 2
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-i', TRACK, '-filter_complex',
                    f'[1:a]atrim=0:{total},afade=t=in:d=0.5,afade=t=out:st={fa}:d=2,loudnorm=I=-20:TP=-3:LRA=7[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', OUT], check=True)
    os.remove(tmp)
    print('ok', total, 's')

render()
