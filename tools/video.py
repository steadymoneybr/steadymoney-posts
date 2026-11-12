"""Gera o vídeo vertical (9:16) do TikTok a partir do mesmo spec.json do carrossel.

Uso: python3 tools/video.py posts/AAAA-MM-DD-slug/spec.json posts/AAAA-MM-DD-slug/video.mp4
"""
import json, math, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from categorias import cat, label, rgb

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
    def __init__(s, bg=CREAM):
        s.im = Image.new('RGBA', (W, H), bg + (255,))

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


fTag = F(DJB, 30); fSub = F(DJB, 34); fBody = F(DJ, 40); fIt = F(LORAI, 54, 'Italic'); fBrand = F(LORA, 44, 'Bold')


def tag(fr, txt, t, col=GOLD):
    a, dy = appear(t, 0.05)
    fr.text(txt.upper(), fTag, col, 300, a, dy, spacing=7)
    w = 220 * ease((t - 0.2) / 0.5); fr.rect((W / 2 - w / 2, 352, W / 2 + w / 2, 356), col, a)


def bars(fr, cx, y, a, scale=1.0, grow=1.0, dark=NAVY):
    hs = [90, 128, 108, 86]; cols = [dark, GOLD, dark, dark]
    bw = int(34 * scale); gap = int(14 * scale); tot = 4 * bw + 3 * gap; x0 = cx - tot / 2
    for i, (h, c) in enumerate(zip(hs, cols)):
        hh = h * scale * ease(grow - i * 0.12)
        x = x0 + i * (bw + gap); fr.rect((x, y - hh, x + bw, y), c, a, r=int(5 * scale))
    fr.rect((x0 - 10 * scale, y + 8 * scale, x0 + tot + 10 * scale, y + 13 * scale), dark, a)


def cover_scene(s):
    c = cat(s); cT = rgb(c['title']); cVS = rgb(c['vs']); cS = rgb(c['sub']); cTag = rgb(c['tag']); cBar = rgb(c['bar']); cInk = rgb(c['ink']); bg = rgb(c['bg'])
    confronto = (s.get('category') or '') == 'confronto'
    title = clean(s['title']); sub = clean(s.get('sub', ''))
    nexp = title.count('\n') + 1  # respeita as quebras <br> do título
    fT = fit(title, LORA, 'Bold', 120, 70, 940, nexp if nexp > 1 else 4)
    tl = wrap(title, fT, 940); sl = wrap(sub, fBody, 900)

    def line(fr, ln, y, a, dy):
        words = ln.split(' ')
        if not confronto or 'x' not in words:
            fr.text(ln, fT, cT, y, a, dy); return
        parts = []  # destaca o "x" em dourado
        for i, w_ in enumerate(words):
            parts.append(w_ + (' ' if i < len(words) - 1 else ''))
        widths = [_meas.textlength(p, font=fT) for p in parts]; x = (W - sum(widths)) / 2
        for p, w in zip(parts, widths):
            fr.text(p, fT, cVS if p.strip() == 'x' else cT, y, a, dy, x=x); x += w

    def draw(t):
        fr = Fr(bg); tag(fr, label(s), t, cTag)
        y = 520
        lh = int(fT.size * 1.18)
        for i, ln in enumerate(tl):
            a, dy = appear(t, 0.3 + i * 0.15); line(fr, ln, y, a, dy); y += lh
        y += 50
        for ln in sl:
            a, dy = appear(t, 0.8); fr.text(ln, fBody, cS, y, a, dy); y += 62
        by = max(y + 260, 1250)
        bars(fr, W / 2, by, ease((t - 1.1) / 0.4), 1.3, (t - 1.1) / 0.9, cBar)
        fr.text('STEADY MONEY', fBrand, cInk, max(1500, by + 70), 0.9 * ease((t - 1.3) / 0.5))
        return fr
    return draw, 4.0


def save_cover(spec, path):
    """Capa do Reel/TikTok (1080x1920) igual à capa do vídeo, já com a categoria. Use como videoThumbnailUrl."""
    s = next(x for x in spec['slides'] if x['type'] == 'cover')
    cover_scene(s)[0](3.9).im.convert('RGB').save(path, 'JPEG', quality=92)


def inner_scene(s):
    """Versão vídeo: só o essencial (palavra grande, subtítulo e frase final). Os bullets ficam no carrossel."""
    big = clean(s['big']); sub = clean(s.get('sub', '')).upper()
    fB = fit(big, LORA, 'Bold', 150, 80, 940, 2)
    bl = wrap(big, fB, 940); subl = wrap(sub, fSub, 900)
    foot = clean(s.get('quote') or s.get('cta') or '')
    footf = F(LORAI, 64, 'Italic') if s.get('quote') else F(DJB, 50)
    footl = wrap(foot, footf, 900)
    words = len((big + ' ' + sub + ' ' + foot).split())
    dur = max(3.6, 1.3 + words * 0.19)  # tempo de leitura confortável

    def draw(t):
        fr = Fr(); tag(fr, s.get('tag', ''), t)
        y = 560
        for ln in bl:
            a, dy = appear(t, 0.25); fr.text(ln, fB, NAVY, y, a, dy); y += int(fB.size * 1.15)
        y += 30
        for ln in subl:
            a, dy = appear(t, 0.5); fr.text(ln, fSub, GOLD, y, a, dy, spacing=3); y += 54
        y += 70
        fr.rect((390, y, 690, y + 3), LINE, ease((t - 0.8) / 0.4)); y += 90
        for ln in footl:
            a, dy = appear(t, 1.1); fr.text(ln, footf, MUTED if s.get('quote') else NAVY, y, a, dy); y += int(footf.size * 1.35)
        fr.text('STEADY MONEY', fBrand, NAVY, 1500, 0.9)
        return fr
    return draw, dur


def end_scene():
    fM = F(LORA, 64, 'Bold')

    def draw(t):
        fr = Fr()
        bars(fr, W / 2, 760, ease(t / 0.4), 1.8, t / 0.9)
        a, dy = appear(t, 0.6); fr.text('STEADY MONEY', fM, NAVY, 820, a, dy)
        a, dy = appear(t, 1.0); fr.text('Educação financeira sem enrolação.', fBody, TEXT, 1000, a, dy)
        fr.text('Segue a gente.', fBody, TEXT, 1062, a, dy)
        return fr
    return draw, 3.0


def add_music(out, dur):
    """Coloca a trilha padrão (assets/trilha-padrao.m4a) baixinha, com fade no final."""
    import os, shutil
    track = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'trilha-padrao.m4a')
    if not os.path.exists(track):
        return
    tmp = out + '.tmp.mp4'
    fa = max(0, dur - 2.0)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-stream_loop', '-1', '-i', track,
                    '-filter_complex', f'[1:a]atrim=0:{dur},afade=t=out:st={fa}:d=2,loudnorm=I=-25:TP=-5:LRA=7[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', tmp], check=True)
    shutil.move(tmp, out)


def hook_clip(h, out):
    """Abertura com cena de IA (spec["hook"]): cena 9:16 cortada (tira marca d'água do topo), degradê escuro,
    etiqueta dourada, título em Lora branco e 2ª linha em Lora itálico dourado-claro."""
    import os, tempfile
    from PIL import ImageFilter
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    clip = os.path.join(root, h['clip']); tmp = tempfile.mkdtemp()
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for y in range(1000):
        d.line([(0, y), (W, y)], fill=(15, 22, 36, int(235 * (1 - y / 1000) ** 1.3)))
    g.save(f'{tmp}/g.png')

    def layer(txt, f, col, y, sp=0, name='x', rule=False):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh = im.copy()
        for tgt, c, o in ((sh, (0, 0, 0, 170), 5), (im, col + (255,), 0)):
            dd = ImageDraw.Draw(tgt)
            w = sum(dd.textlength(ch, font=f) + sp for ch in txt) - sp; x = (W - w) / 2
            for ch in txt:
                dd.text((x, y + o), ch, font=f, fill=c); x += dd.textlength(ch, font=f) + sp
        im = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), im)
        if rule:
            ImageDraw.Draw(im).rectangle((W / 2 - 60, y + 52, W / 2 + 60, y + 55), fill=col + (255,))
        im.save(f'{tmp}/{name}.png')
    layer(h.get('kicker', '').upper(), F(DJB, 32), (217, 182, 106), 170, 8, 'k', True)
    fl1 = fit(h['l1'], LORA, 'Bold', 104, 70, 960, 1); layer(h['l1'], fl1, CREAM, 270, 0, 'a')
    fl2 = fit(h.get('l2', ''), LORAI, 'Italic', 96, 64, 960, 1); layer(h.get('l2', ''), fl2, (240, 214, 150), 400, 0, 'b')
    dur = float(h.get('dur', 5.0)); t2 = float(h.get('l2_at', 2.5))
    fc = (f'[0:v]scale=-2:2060,crop=1080:1920:(iw-1080)/2:ih-1920,fps={FPS},trim=0:{dur},setpts=PTS-STARTPTS[v];'
          f'[2]format=rgba,fade=in:st=0.2:d=0.4:alpha=1[k];[3]format=rgba,fade=in:st=0.5:d=0.5:alpha=1[a];'
          f'[4]format=rgba,fade=in:st={t2}:d=0.4:alpha=1[b];[v][1]overlay[v1];[v1][k]overlay[v2];[v2][a]overlay[v3];'
          f'[v3][b]overlay,format=yuv420p[o]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', clip] + sum([['-loop', '1', '-i', f'{tmp}/{n}.png'] for n in 'gkab'], []) +
                   ['-filter_complex', fc, '-map', '[o]', '-t', str(dur), '-an', '-c:v', 'libx264', '-preset', 'veryfast',
                    '-crf', '20', '-r', str(FPS), out], check=True)
    return dur


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
    if spec.get('hook'):  # abertura com cena de IA na frente do vídeo
        import os, shutil
        hk = out + '.hook.mp4'; body = out + '.body.mp4'; shutil.move(out, body)
        total += hook_clip(spec['hook'], hk)
        lst = out + '.txt'; open(lst, 'w').write(f"file '{os.path.abspath(hk)}'\nfile '{os.path.abspath(body)}'\n")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                        '-movflags', '+faststart', out], check=True)
        for f_ in (hk, body, lst):
            os.remove(f_)
        fr = out.rsplit('.', 1)[0] + '-check0.jpg'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '3.5', '-i', out, '-frames:v', '1', fr], check=True)
    add_music(out, total)
    # quadros de conferência: o fim de cada cena
    for i, (fn, d) in enumerate(scenes):
        fn(d - 0.05).im.convert('RGB').save(out.rsplit('.', 1)[0] + f'-check{i + 1}.jpg', quality=80)
    save_cover(spec, _os.path.join(_os.path.dirname(out) or '.', 'capa-video.jpg'))
    print(f'{out}: {total:.1f}s')


if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[3] == '--capa':  # só a capa (ex.: dia do Steady): video.py spec.json capa-video.jpg --capa
        save_cover(json.load(open(sys.argv[1])), sys.argv[2])
    else:
        main(sys.argv[1], sys.argv[2])
