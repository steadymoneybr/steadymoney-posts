"""Gera o vídeo vertical (9:16) do TikTok a partir do mesmo spec.json do carrossel.

Uso: python3 tools/video.py posts/AAAA-MM-DD-slug/spec.json posts/AAAA-MM-DD-slug/video.mp4
"""
import json, math, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
CREAM = (251, 249, 244); NAVY = (27, 42, 65); GOLD = (156, 122, 60); LINE = (222, 216, 201)
TEXT = (43, 43, 43); MUTED = (119, 119, 119)
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
LORAI = '/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf'
DJB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
DJ = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def F(path, size, var=None):
    f = ImageFont.truetype(path, size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


def clean(s):
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = ''.join(c for c in s if ord(c) < 0x10000)  # tira emoji (a fonte não tem)
    return s.strip()


def ease(t):
    t = max(0, min(1, t)); return 1 - (1 - t) ** 3


def eio(t):
    t = max(0, min(1, t)); return 0.5 - 0.5 * math.cos(math.pi * t)


_meas = ImageDraw.Draw(Image.new('RGB', (10, 10)))


def wrap(text, font, maxw):
    out = []
    for para in text.split('\n'):
        cur = ''
        for w in para.split():
            t = (cur + ' ' + w).strip()
            if _meas.textlength(t, font=font) <= maxw:
                cur = t
            else:
                if cur:
                    out.append(cur)
                cur = w
        out.append(cur)
    return [l for l in out if l]


def fit(text, path, var, start, minsize, maxw, maxlines):
    size = start
    while size > minsize:
        f = F(path, size, var)
        if len(wrap(text, f, maxw)) <= maxlines and all(_meas.textlength(l, font=f) <= maxw for l in wrap(text, f, maxw)):
            return f
        size -= 6
    return F(path, minsize, var)


class Fr:
    def __init__(s):
        s.im = Image.new('RGBA', (W, H), CREAM + (255,))

    def _lay(s):
        return Image.new('RGBA', (W, H), (0, 0, 0, 0))

    def text(s, txt, f, col, y, a=1.0, dy=0, spacing=0, x=None):
        if a <= 0:
            return
        lay = s._lay(); d = ImageDraw.Draw(lay)
        if spacing:
            w = sum(d.textlength(c, font=f) + spacing for c in txt) - spacing
            xx = (W - w) / 2 if x is None else x
            for c in txt:
                d.text((xx, y + dy), c, font=f, fill=col + (int(255 * a),)); xx += d.textlength(c, font=f) + spacing
        else:
            w = d.textlength(txt, font=f); xx = (W - w) / 2 if x is None else x
            d.text((xx, y + dy), txt, font=f, fill=col + (int(255 * a),))
        s.im = Image.alpha_composite(s.im, lay)

    def rect(s, box, col, a=1.0, r=0):
        if a <= 0:
            return
        lay = s._lay(); d = ImageDraw.Draw(lay)
        if r:
            d.rounded_rectangle(box, radius=r, fill=col + (int(255 * a),))
        else:
            d.rectangle(box, fill=col + (int(255 * a),))
        s.im = Image.alpha_composite(s.im, lay)


def appear(t, start, dur=0.5):
    e = ease((t - start) / dur); return e, (1 - e) * 40


fTag = F(DJB, 30); fSub = F(DJB, 38); fBody = F(DJ, 44); fIt = F(LORAI, 54, 'Italic'); fBrand = F(LORA, 44, 'Bold')


def tag(fr, txt, t):
    a, dy = appear(t, 0.05)
    fr.text(txt.upper(), fTag, GOLD, 300, a, dy, spacing=7)
    w = 220 * ease((t - 0.2) / 0.5); fr.rect((W / 2 - w / 2, 352, W / 2 + w / 2, 356), GOLD, a)


def bars(fr, cx, y, a, scale=1.0, grow=1.0):
    hs = [90, 128, 108, 86]; cols = [NAVY, GOLD, NAVY, NAVY]
    bw = int(34 * scale); gap = int(14 * scale); tot = 4 * bw + 3 * gap; x0 = cx - tot / 2
    for i, (h, c) in enumerate(zip(hs, cols)):
        hh = h * scale * ease(grow - i * 0.12)
        x = x0 + i * (bw + gap); fr.rect((x, y - hh, x + bw, y), c, a, r=int(5 * scale))
    fr.rect((x0 - 10 * scale, y + 8 * scale, x0 + tot + 10 * scale, y + 13 * scale), NAVY, a)


def cover_scene(s):
    title = clean(s['title']); sub = clean(s.get('sub', ''))
    fT = fit(title, LORA, 'Bold', 120, 70, 940, 4)
    tl = wrap(title, fT, 940); sl = wrap(sub, fBody, 900)

    def draw(t):
        fr = Fr(); tag(fr, s.get('tag', 'Educação Financeira'), t)
        y = 520
        lh = int(fT.size * 1.18)
        for i, ln in enumerate(tl):
            a, dy = appear(t, 0.3 + i * 0.15); fr.text(ln, fT, NAVY, y, a, dy); y += lh
        y += 50
        for ln in sl:
            a, dy = appear(t, 0.8); fr.text(ln, fBody, TEXT, y, a, dy); y += 62
        bars(fr, W / 2, max(y + 260, 1250), ease((t - 1.1) / 0.4), 1.3, (t - 1.1) / 0.9)
        fr.text('STEADY MONEY', fBrand, NAVY, 1500, 0.9 * ease((t - 1.3) / 0.5))
        return fr
    return draw, 4.0


def inner_scene(s):
    big = clean(s['big']); sub = clean(s.get('sub', '')).upper()
    fB = fit(big, LORA, 'Bold', 150, 80, 940, 2)
    bl = wrap(big, fB, 940); subl = wrap(sub, fSub, 900)
    bullets = [wrap(clean(b), fBody, 760) for b in s.get('bullets', [])]
    foot = clean(s.get('quote') or s.get('cta') or '')
    footf = fIt if s.get('quote') else F(DJB, 44)
    footl = wrap(foot, footf, 900)
    nb = len(bullets)
    dur = 3.2 + 0.55 * nb

    def draw(t):
        fr = Fr(); tag(fr, s.get('tag', ''), t)
        y = 440
        for ln in bl:
            a, dy = appear(t, 0.25); fr.text(ln, fB, NAVY, y, a, dy); y += int(fB.size * 1.15)
        y += 20
        for ln in subl:
            a, dy = appear(t, 0.45); fr.text(ln, fSub, NAVY, y, a, dy, spacing=2); y += 54
        y += 40
        fr.rect((170, y, 910, y + 2), LINE, ease((t - 0.6) / 0.4)); y += 60
        for i, lines in enumerate(bullets):
            a, dy = appear(t, 0.9 + i * 0.5)
            fr.rect((175, y + 18, 193, y + 36), GOLD, a, r=9)
            for ln in lines:
                fr.text(ln, fBody, TEXT, y, a, dy, x=225); y += 58
            y += 34
        y += 30
        fs = 0.9 + nb * 0.5 + 0.3
        for ln in footl:
            a, dy = appear(t, fs); fr.text(ln, footf, MUTED if s.get('quote') else NAVY, y, a, dy); y += int(footf.size * 1.35)
        fr.text('STEADY MONEY', fBrand, NAVY, max(1500, y + 40), 0.9)
        return fr
    return draw, dur


def end_scene():
    fM = F(LORA, 64, 'Bold')

    def draw(t):
        fr = Fr()
        bars(fr, W / 2, 760, ease(t / 0.4), 1.8, t / 0.9)
        a, dy = appear(t, 0.6); fr.text('STEADY MONEY', fM, NAVY, 820, a, dy)
        a, dy = appear(t, 1.0); fr.text('Educação financeira', fBody, TEXT, 1000, a, dy)
        fr.text('sem enrolação. Segue a gente.', fBody, TEXT, 1062, a, dy)
        return fr
    return draw, 3.0


def main(spec_path, out):
    spec = json.load(open(spec_path))
    scenes = []
    for s in spec['slides']:
        scenes.append(cover_scene(s) if s['type'] == 'cover' else inner_scene(s))
    scenes.append(end_scene())
    XF = 0.35
    starts = []; acc = 0
    for _, d in scenes:
        starts.append(acc); acc += d - XF
    total = acc + XF; N = int(total * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                          '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for n in range(N):
        t = n / FPS
        act = [(i, t - st) for i, st in enumerate(starts) if 0 <= t - st < scenes[i][1]]
        if len(act) == 1:
            i, tt = act[0]; img = scenes[i][0](tt).im.convert('RGB')
        else:
            (i1, t1), (i2, t2) = act[0], act[-1]
            img = Image.blend(scenes[i1][0](t1).im.convert('RGB'), scenes[i2][0](t2).im.convert('RGB'), eio(t2 / XF))
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()
    # quadros de conferência: o fim de cada cena
    for i, (fn, d) in enumerate(scenes):
        fn(d - 0.05).im.convert('RGB').save(out.rsplit('.', 1)[0] + f'-check{i + 1}.jpg', quality=80)
    print(f'{out}: {total:.1f}s')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
