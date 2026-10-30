"""Gera o carrossel (Instagram, 1080x1350) e o vídeo (TikTok, 1080x1920) da G5 Delay a partir de um spec.json.

Uso:
  python3 g5/tools/g5render.py g5/posts/AAAA-MM-DD-slug/spec.json

Saída na mesma pasta: slide1..N.png/.jpg, video.mp4 e video-check*.jpg (só para conferência; não subir).
"""
import asyncio, base64, json, os, shutil, subprocess, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
FONTDIR = os.path.join(HERE, '..', 'fonts')
TRACK = os.path.join(ROOT, 'assets', 'trilha-padrao.m4a')


def ff(w):
    with open(os.path.join(FONTDIR, f'barlow-condensed-latin-{w}-normal.woff2'), 'rb') as f:
        return base64.b64encode(f.read()).decode()


FONTS = ''.join(f"@font-face{{font-family:BC;font-weight:{w};src:url(data:font/woff2;base64,{ff(w)}) format('woff2')}}"
                for w in (400, 600, 700, 800, 900))

CSS = FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
:root{--p:1;--o:1}
body{width:1080px;height:var(--H);background:#111417;color:#F2F2EE;font-family:BC,'DejaVu Sans',sans-serif;position:relative;overflow:hidden}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:54px 54px}
.pad{position:absolute;inset:0;padding:var(--PT) 80px 84px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:30px;letter-spacing:4px;text-transform:uppercase;color:#9AA0A6}
.logo{color:#F2F2EE;font-weight:900;letter-spacing:2px;font-size:38px}
.logo b{color:#FF5A1F}
.stripe{height:10px;width:calc(140px * var(--p));background:#FF5A1F;margin:44px 0 30px}
.kicker{font-weight:700;font-size:34px;letter-spacing:5px;text-transform:uppercase;color:#FF5A1F}
h2{font-weight:800;font-size:88px;line-height:.98;text-transform:uppercase;margin-top:14px}
.lead{font-weight:400;font-size:44px;line-height:1.2;color:#C9CDD1;margin-top:30px;max-width:920px}
.score{display:grid;grid-template-columns:1fr auto auto auto 1fr;align-items:center;gap:22px;margin-top:56px}
.score .t{font-weight:800;font-size:56px;text-transform:uppercase;line-height:1}
.score .t.r{text-align:right}
.score .n{font-weight:900;font-size:170px;line-height:1}
.score .x{font-weight:400;font-size:70px;color:#5D646B}
.w{color:#FF5A1F!important}
.l{color:#F2F2EE}
.scorers{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:26px;font-weight:600;font-size:34px;line-height:1.35;color:#C9CDD1}
.scorers > div:last-child{text-align:right}
.scorers .lbl{font-weight:700;font-size:26px;letter-spacing:4px;color:#6E757C;text-transform:uppercase;margin-bottom:6px}
.bars{display:flex;flex-direction:column;gap:42px}
.row .lab{display:flex;justify-content:space-between;font-weight:700;font-size:40px;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px}
.row .lab span:nth-child(2){color:#9AA0A6;font-weight:600;font-size:30px;letter-spacing:3px;align-self:center;text-align:center}
.track{display:flex;height:30px;gap:6px}
.track div{height:100%}
.c0{background:#5D646B}.c1{background:#FF5A1F}
.teams{display:flex;justify-content:space-between;font-weight:700;font-size:30px;letter-spacing:3px;text-transform:uppercase;color:#9AA0A6;margin:36px 0 30px}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;font-weight:600;font-size:28px;letter-spacing:3px;text-transform:uppercase;color:#6E757C}
.big{font-weight:900;font-size:210px;line-height:.9}
.duo{display:flex;gap:60px;margin-top:46px;align-items:flex-end}
.duo .c{flex:1}
.duo .k{font-weight:700;font-size:34px;letter-spacing:3px;text-transform:uppercase;color:#9AA0A6;margin-top:10px}
.note{font-weight:400;font-size:40px;line-height:1.25;color:#C9CDD1;margin-top:46px;border-left:8px solid #FF5A1F;padding-left:28px}
.cta{font-weight:800;font-size:52px;text-transform:uppercase;line-height:1.05;color:#F2F2EE}
.fade{opacity:var(--o);transform:translateY(calc((1 - var(--o)) * 30px))}
"""


def esc(s):
    return str(s)


def head(tag):
    return f"<div class=grid></div><div class=pad><div class=top><span class=logo>G5<b>.</b>DELAY</span><span>{tag}</span></div>"


def winner(spec):
    hs, as_ = spec['hs'], spec['as']
    return 0 if hs > as_ else (1 if as_ > hs else -1)


def cover(spec):
    w = winner(spec)
    hc = 'w' if w == 0 else 'l'
    ac = 'w' if w == 1 else 'l'
    sh = '<br>'.join(spec.get('scorers', {}).get('home', [])) or '—'
    sa = '<br>'.join(spec.get('scorers', {}).get('away', [])) or '—'
    kick = f"<div class=kicker>{spec['kicker']}</div>" if spec.get('kicker') else ''
    return head(spec['comp']) + f"""<div class=stripe></div>{kick}
<div class=score><span class='t r {hc}'>{spec['home']}</span><span class='n {hc}'>{spec['hs']}</span><span class=x>×</span><span class='n {ac}'>{spec['as']}</span><span class='t {ac}'>{spec['away']}</span></div>
<div class='scorers fade'><div><div class=lbl>Gols</div>{sh}</div><div><div class=lbl>Gols</div>{sa}</div></div>
<h2 class=fade style='margin-top:56px'>{spec['hook']}</h2>
<p class='lead fade'>{spec.get('lead', '')}</p>
<div class=foot><span>Arrasta pro lado →</span><span>{spec['date']}</span></div></div>"""


def bars_slide(spec, s):
    w = winner(spec)
    hcls, acls = ('c1', 'c0') if w == 0 else ('c0', 'c1')
    rows = ''
    for r in s['rows']:
        label, a, b = r[0], r[1], r[2]
        suf = r[3] if len(r) > 3 else ''
        tot = (a + b) or 1
        pa, pb = a / tot * 100, b / tot * 100
        rows += (f"<div class=row><div class=lab><span>{a}{suf}</span><span>{label}</span><span>{b}{suf}</span></div>"
                 f"<div class=track><div class={hcls} style='width:calc({pa}% * var(--p))'></div>"
                 f"<div class={acls} style='width:calc({pb}% * var(--p))'></div></div></div>")
    hn = f"<span class={'w' if w == 0 else ''}>{spec['home']}</span>"
    an = f"<span class={'w' if w == 1 else ''}>{spec['away']}</span>"
    note = f"<p class='note fade'>{s['note']}</p>" if s.get('note') else ''
    return head(s['tag']) + f"""<div class=stripe></div><h2>{s['title']}</h2>
<div class=teams>{hn}{an}</div><div class=bars>{rows}</div>{note}
<div class=foot><span>Dados: {spec.get('source', 'Sofascore')}</span><span>G5 Delay</span></div></div>"""


def big_slide(spec, s, last):
    ca = 'w' if s.get('winner') == 'a' else ''
    cb = 'w' if s.get('winner') == 'b' else ''
    sa = "style='color:#5D646B'" if not ca else ''
    sb = "style='color:#5D646B'" if not cb else ''
    extra = f"<p class='lead fade' style='margin-top:36px'>{s['extra']}</p>" if s.get('extra') else ''
    foot_left = (f"<span class=cta>{spec.get('cta', 'Concorda com a leitura?')}<br><span class=w>Comenta aí.</span></span>"
                 if last else f"<span>Dados: {spec.get('source', 'Sofascore')}</span>")
    return head(s['tag']) + f"""<div class=stripe></div><div class=kicker>{s['kicker']}</div>
<div class=duo><div class=c><div class='big {ca}' {sa}>{s['a']}</div><div class='k {ca}'>{s.get('la', spec['home'])}</div></div>
<div class=c><div class='big {cb}' {sb}>{s['b']}</div><div class='k {cb}'>{s.get('lb', spec['away'])}</div></div></div>
<p class='note fade'>{s.get('note', '')}</p>{extra}
<div class=foot>{foot_left}<span>G5 Delay</span></div></div>"""


def bars_last_fix(html, spec, last):
    if not last:
        return html
    return html.replace(f"<span>Dados: {spec.get('source', 'Sofascore')}</span><span>G5 Delay</span>",
                        f"<span class=cta>{spec.get('cta', 'Concorda com a leitura?')}<br><span class=w>Comenta aí.</span></span><span>G5 Delay</span>")


def build(spec):
    pages = [cover(spec)]
    n = len(spec['slides'])
    for i, s in enumerate(spec['slides']):
        last = i == n - 1
        if s['type'] == 'bars':
            pages.append(bars_last_fix(bars_slide(spec, s), spec, last))
        else:
            pages.append(big_slide(spec, s, last))
    return pages


def doc(body, H, PT):
    return f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body style='--H:{H}px;--PT:{PT}px'>{body}</body></html>"


async def render(spec_path):
    spec = json.load(open(spec_path))
    out = os.path.dirname(os.path.abspath(spec_path))
    pages = build(spec)
    frames_dir = os.path.join(out, '_frames')
    shutil.rmtree(frames_dir, ignore_errors=True); os.makedirs(frames_dir)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # carrossel 4:5
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for i, body in enumerate(pages, 1):
            await pg.set_content(doc(body, 1350, 84)); await pg.wait_for_timeout(250)
            png = os.path.join(out, f'slide{i}.png')
            await pg.screenshot(path=png)
            from PIL import Image
            Image.open(png).convert('RGB').save(png[:-4] + '.jpg', 'JPEG', quality=92, optimize=True)
        # vídeo 9:16: anima barras/textos e segura
        pv = await b.new_page(viewport={'width': 1080, 'height': 1920})
        fps = 30; anim = 18; hold = [int(fps * 3.2)] + [int(fps * 4.2)] * (len(pages) - 1)
        k = 0
        listing = []
        for i, body in enumerate(pages):
            await pv.set_content(doc(body, 1920, 380)); await pv.wait_for_timeout(250)
            for f in range(anim):
                t = (f + 1) / anim
                e = 1 - (1 - t) ** 3
                await pv.evaluate(f"document.documentElement.style.setProperty('--p','{e}');document.documentElement.style.setProperty('--o','{e}')")
                fp = os.path.join(frames_dir, f'{k:05d}.png'); await pv.screenshot(path=fp); listing.append((fp, 1 / fps)); k += 1
            listing.append((fp, hold[i] / fps))
            from PIL import Image
            Image.open(fp).convert('RGB').save(os.path.join(out, f'video-check{i + 1}.jpg'), quality=80)
        await b.close()
    lst = os.path.join(frames_dir, 'list.txt')
    with open(lst, 'w') as f:
        for fp, d in listing:
            f.write(f"file '{fp}'\nduration {d:.4f}\n")
        f.write(f"file '{listing[-1][0]}'\n")
    total = sum(d for _, d in listing)
    vid = os.path.join(out, 'video.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst]
    if os.path.exists(TRACK):
        cmd += ['-stream_loop', '-1', '-i', TRACK, '-filter_complex',
                f'[1:a]atrim=0:{total:.2f},afade=t=out:st={max(0, total - 2):.2f}:d=2,loudnorm=I=-25:TP=-5:LRA=7[a]',
                '-map', '0:v', '-map', '[a]', '-c:a', 'aac', '-b:a', '160k']
    cmd += ['-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
            '-movflags', '+faststart', '-t', f'{total:.2f}', vid]
    subprocess.run(cmd, check=True)
    shutil.rmtree(frames_dir, ignore_errors=True)
    print(f'ok: {len(pages)} slides, vídeo {total:.1f}s -> {out}')


if __name__ == '__main__':
    asyncio.run(render(sys.argv[1]))
