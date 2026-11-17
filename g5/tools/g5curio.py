"""G5 Delay — posts de CURIOSIDADE do futebol (Vini, 17/11/2026).

Gera, a partir de um spec.json com "formato": "curiosidade":
  - carrossel 1080x1350 (slide1..5 .png/.jpg): capa com o gancho + 4 slides "N de 4" (o último com o CTA);
  - video.mp4 1080x1920 DINÂMICO (15–20 s): frases curtas em "beats" de ~1,5–2,6 s, texto gigante
    entrando com zoom/punch, flash entre cortes, barra de progresso no topo e trilha padrão;
  - story.jpg (1º quadro do vídeo, 9:16) e video-check*.jpg (um por beat, só para conferência; não subir).

Uso:
  python3 g5/tools/g5curio.py g5/posts/AAAA-MM-DD-slug/spec.json
  python3 g5/tools/g5curio.py g5/posts/AAAA-MM-DD-slug/spec.json --video-only
      (dia de ANÁLISE: o carrossel vem do g5render.py; este comando refaz só o video.mp4/story.jpg
       no estilo dinâmico a partir do bloco "beats" do spec da análise, e não mexe nos slides)

Formato do spec (ver g5/exemplo-curiosidade/spec.json):
{
 "formato": "curiosidade",
 "tag": "Curiosidade · Copa do Mundo",      # etiqueta do topo
 "kicker": "Recorde que ninguém bateu",       # linha laranja da capa
 "hook": "13 gols<br>em 1 Copa.",            # gancho grande da capa (número chocante)
 "lead": "Frase de apoio de 1–2 linhas.",
 "date": "17.11.2026",
 "source": "FIFA / ge",
 "slides": [ {"tag": "1 de 4 · O feito", "big": "13", "title": "gols em 6 jogos", "text": "..."}, ... ],
 "cta": "Alguém bate esse recorde?",
 "beats": [ {"big": "13 GOLS", "small": "em uma única Copa"}, ... ],   # vídeo: 6–9 beats, o 1º é o gancho
 "theme": "escuro|claro|laranja"            # opcional; sem ele segue o rodízio do g5render
}
"""
import asyncio, json, os, shutil, subprocess, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from g5render import FONTS, THEMES, theme_vars, auto_theme, TRACK  # noqa: E402

CSS = FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
:root{--s:1;--o:1;--fl:0;--pg:0}
body{width:1080px;height:var(--H);background:var(--bg);color:var(--fg);font-family:BC,'DejaVu Sans',sans-serif;position:relative;overflow:hidden}
.grid{position:absolute;inset:0;background-image:linear-gradient(var(--gridc) 1px,transparent 1px),linear-gradient(90deg,var(--gridc) 1px,transparent 1px);background-size:54px 54px}
.pad{position:absolute;inset:0;padding:var(--PT) 80px 84px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:30px;letter-spacing:4px;text-transform:uppercase;color:var(--mut)}
.logo{color:var(--fg);font-weight:900;letter-spacing:2px;font-size:38px}
.logo b{color:var(--acc)}
.stripe{height:10px;width:140px;background:var(--acc);margin:44px 0 30px}
.kicker{font-weight:700;font-size:34px;letter-spacing:5px;text-transform:uppercase;color:var(--acc)}
.hook{font-weight:900;font-size:150px;line-height:.92;text-transform:uppercase;margin-top:40px}
.lead{font-weight:400;font-size:46px;line-height:1.22;color:var(--sub);margin-top:44px;max-width:920px}
.big{font-weight:900;font-size:240px;line-height:.9;color:var(--acc)}
h2{font-weight:800;font-size:76px;line-height:1;text-transform:uppercase;margin-top:18px}
.text{font-weight:400;font-size:44px;line-height:1.28;color:var(--sub);margin-top:44px;border-left:8px solid var(--acc);padding-left:28px}
.cta{font-weight:800;font-size:52px;text-transform:uppercase;line-height:1.05;color:var(--fg)}
.w{color:var(--acc)}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:30px;font-weight:600;font-size:28px;letter-spacing:3px;text-transform:uppercase;color:var(--faint)}
.foot > span:last-child{white-space:nowrap}
/* vídeo */
.bar{position:absolute;left:0;top:0;height:14px;width:calc(var(--pg) * 100%);background:var(--acc)}
.vtop{position:absolute;left:80px;right:80px;top:330px;display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:32px;letter-spacing:4px;text-transform:uppercase;color:var(--mut)}
.stage{position:absolute;left:80px;right:80px;top:470px;bottom:420px;display:flex;flex-direction:column;justify-content:center}
.vb{font-weight:900;line-height:.9;text-transform:uppercase;transform:scale(var(--s));transform-origin:left center;opacity:var(--o)}
.vs{font-weight:600;font-size:58px;line-height:1.15;color:var(--sub);margin-top:36px;opacity:var(--o2,1);transform:translateY(calc((1 - var(--o2,1)) * 24px))}
.flash{position:absolute;inset:0;background:#FFFFFF;opacity:var(--fl)}
.vfoot{position:absolute;left:80px;right:80px;bottom:330px;display:flex;justify-content:space-between;font-weight:700;font-size:30px;letter-spacing:4px;text-transform:uppercase;color:var(--faint)}
"""


def head(tag):
    return f"<div class=grid></div><div class=pad><div class=top><span class=logo>G5<b>.</b>DELAY</span><span>{tag}</span></div>"


def cover(spec):
    kick = f"<div class=kicker>{spec['kicker']}</div>" if spec.get('kicker') else ''
    return head(spec.get('tag', 'Curiosidade')) + f"""<div class=stripe></div>{kick}
<div class=hook>{spec['hook']}</div><p class=lead>{spec.get('lead', '')}</p>
<div class=foot><span>Arrasta pro lado →</span><span>{spec.get('date', '')}</span></div></div>"""


def inner(spec, s, last):
    foot_left = (f"<span class=cta>{spec.get('cta', 'Sabia dessa?')}<br><span class=w>Comenta aí.</span></span>"
                 if last else f"<span>Fonte: {spec.get('source', '')}</span>")
    big = f"<div class=big>{s['big']}</div>" if s.get('big') else ''
    return head(s['tag']) + f"""<div class=stripe></div>{big}<h2>{s.get('title', '')}</h2>
<p class=text>{s.get('text', '')}</p>
<div class=foot>{foot_left}<span>G5 Delay</span></div></div>"""


def beat_size(txt):
    n = max(len(l) for l in txt.replace('<br>', '\n').split('\n'))
    return 210 if n <= 7 else 170 if n <= 10 else 136 if n <= 13 else 112 if n <= 17 else 92


def beat_html(spec, b, i, n):
    size = b.get('size') or beat_size(b['big'])
    small = f"<div class=vs>{b['small']}</div>" if b.get('small') else ''
    color = "color:var(--acc)" if b.get('acc', i == 0 or i == n - 1) else ''
    return f"""<div class=grid></div><div class=bar></div>
<div class=vtop><span class=logo>G5<b>.</b>DELAY</span><span>{spec.get('vtag', spec.get('tag', 'Curiosidade'))}</span></div>
<div class=stage><div class=vb style='font-size:{size}px;{color}'>{b['big']}</div>{small}</div>
<div class=vfoot><span>{'Segue a G5' if i == n - 1 else 'Curiosidade'}</span><span>@g5delay</span></div>
<div class=flash></div>"""


def beat_dur(b, first):
    words = len((b.get('big', '') + ' ' + b.get('small', '')).replace('<br>', ' ').split())
    d = 0.9 + 0.2 * words
    if first:
        d = max(d, 2.0)
    return round(min(max(d, 1.4), 2.6), 2)


# Vídeo colorido (Vini, 17/11/2026: "muito escuro"): cada beat troca de fundo, nunca o escuro.
VPAL = {
    'laranja': dict(bg='#FF5A1F', fg='#FFFFFF', sub='#FFE9DF', mut='#FFD6C4', faint='#FFE3D6', acc='#111417', gridc='rgba(255,255,255,.08)'),
    'creme':   dict(bg='#F3EFE6', fg='#111417', sub='#3A4047', mut='#5D646B', faint='#80868C', acc='#E8490F', gridc='rgba(17,20,23,.05)'),
    'azul':    dict(bg='#1F5CFF', fg='#FFFFFF', sub='#DDE6FF', mut='#C3D3FF', faint='#C3D3FF', acc='#FFD23F', gridc='rgba(255,255,255,.08)'),
    'amarelo': dict(bg='#FFD23F', fg='#111417', sub='#3B3420', mut='#5A4E22', faint='#6B5D28', acc='#1F5CFF', gridc='rgba(17,20,23,.06)'),
    'verde':   dict(bg='#14C670', fg='#0B1F14', sub='#0F3A23', mut='#145A35', faint='#145A35', acc='#FFFFFF', gridc='rgba(11,31,20,.07)'),
}
VORDEM = ['laranja', 'creme', 'azul', 'amarelo', 'verde', 'creme']


def vvars(i):
    pal = VPAL[VORDEM[i % len(VORDEM)]]
    return ';'.join(f'--{k}:{v}' for k, v in pal.items())


def doc(body, H, PT, theme, beat=None):
    if beat is not None:
        return f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body style='--H:{H}px;--PT:{PT}px;{vvars(beat)}'>{body}</body></html>"

    return f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body style='--H:{H}px;--PT:{PT}px;{theme_vars(theme)}'>{body}</body></html>"


async def render(spec_path, video_only=False):
    spec = json.load(open(spec_path))
    auto_theme(spec, spec_path)
    th = spec.get('theme')
    out = os.path.dirname(os.path.abspath(spec_path))
    from PIL import Image
    frames_dir = os.path.join(out, '_frames')
    shutil.rmtree(frames_dir, ignore_errors=True); os.makedirs(frames_dir)
    pages = [] if video_only else [cover(spec)] + [inner(spec, s, i == len(spec['slides']) - 1) for i, s in enumerate(spec['slides'])]
    beats = spec['beats']
    n = len(beats)
    durs = [beat_dur(b, i == 0) for i, b in enumerate(beats)]
    total = sum(durs)
    fps = 30
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={'width': 1080, 'height': 1350})
        for i, body in enumerate(pages, 1):
            await pg.set_content(doc(body, 1350, 84, th)); await pg.wait_for_timeout(200)
            png = os.path.join(out, f'slide{i}.png'); await pg.screenshot(path=png)
            Image.open(png).convert('RGB').save(png[:-4] + '.jpg', 'JPEG', quality=92, optimize=True)
        pv = await br.new_page(viewport={'width': 1080, 'height': 1920})
        listing = []; k = 0; t0 = 0.0
        for i, b in enumerate(beats):
            await pv.set_content(doc(beat_html(spec, b, i, n), 1920, 0, th, beat=i)); await pv.wait_for_timeout(150)
            nf = int(round(durs[i] * fps))
            anim = 0 if i == 0 else 7          # 1º beat já aparece pronto no quadro 0 (capa/gancho)
            for f in range(nf):
                if f < anim:
                    t = (f + 1) / anim; e = 1 - (1 - t) ** 3
                    s, o, fl = 1.18 - 0.18 * e, min(1, 0.2 + e), max(0, 0.55 * (1 - t * 1.6))
                else:
                    tt = (f - anim) / max(1, nf - anim)
                    s, o, fl = 1 + 0.03 * tt, 1, 0          # leve zoom contínuo pra não ficar parado
                o2 = 1 if i == 0 else min(1, max(0, (f - 6) / 8))
                pgv = (t0 + f / fps) / total
                await pv.evaluate(
                    f"const r=document.documentElement.style;r.setProperty('--s','{s:.4f}');r.setProperty('--o','{o:.3f}');"
                    f"r.setProperty('--fl','{fl:.3f}');r.setProperty('--pg','{pgv:.4f}');r.setProperty('--o2','{o2:.3f}')")
                # quadros idênticos na parte parada: captura a cada 2 quadros para acelerar
                if f < anim + 10 or f % 2 == 0 or f == nf - 1:
                    fp = os.path.join(frames_dir, f'{k:05d}.png'); await pv.screenshot(path=fp); k += 1
                    listing.append([fp, 1 / fps])
                else:
                    listing[-1][1] += 1 / fps
                if i == 0 and f == 0:
                    Image.open(fp).convert('RGB').save(os.path.join(out, 'story.jpg'), quality=92)
            Image.open(listing[-1][0]).convert('RGB').save(os.path.join(out, f'video-check{i + 1}.jpg'), quality=80)
            t0 += durs[i]
        await br.close()
    lst = os.path.join(frames_dir, 'list.txt')
    with open(lst, 'w') as f:
        for fp, d in listing:
            f.write(f"file '{fp}'\nduration {d:.4f}\n")
        f.write(f"file '{listing[-1][0]}'\n")
    vid = os.path.join(out, 'video.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst]
    if os.path.exists(TRACK):
        cmd += ['-stream_loop', '-1', '-i', TRACK, '-filter_complex',
                f'[1:a]atrim=0:{total:.2f},afade=t=out:st={max(0, total - 1.5):.2f}:d=1.5,loudnorm=I=-22:TP=-4:LRA=7[a]',
                '-map', '0:v', '-map', '[a]', '-c:a', 'aac', '-b:a', '160k']
    cmd += ['-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
            '-movflags', '+faststart', '-t', f'{total:.2f}', vid]
    subprocess.run(cmd, check=True)
    shutil.rmtree(frames_dir, ignore_errors=True)
    print(f'ok: {len(pages)} slides, {n} beats, vídeo {total:.1f}s -> {out}')
    if not 14 <= total <= 22:
        print(f'ATENÇÃO: vídeo com {total:.1f}s; o alvo é 15–20 s (ajuste o nº de beats ou o texto).')


if __name__ == '__main__':
    asyncio.run(render(sys.argv[1], video_only='--video-only' in sys.argv))
