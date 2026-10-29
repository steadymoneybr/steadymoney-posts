import json, sys, asyncio
from playwright.async_api import async_playwright

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1080px;background:#FBF9F4;font-family:'DejaVu Sans',sans-serif;color:#2B2B2B;
display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.tag{color:#9C7A3C;font-weight:700;font-size:21px;letter-spacing:6px;text-transform:uppercase}
.tagline{width:200px;height:3px;background:#9C7A3C;margin:22px auto 0}
.serif{font-family:'Lora',serif;font-weight:700;color:#1B2A41}
.ctitle{font-size:92px;line-height:1.08;margin-top:90px}
.csub{font-size:32px;line-height:1.35;margin-top:34px;color:#2B2B2B}
.bars{display:flex;align-items:flex-end;gap:12px;margin-top:60px;padding:0 8px 6px;border-bottom:4px solid #1B2A41}
.bars div{width:34px;border-radius:5px;background:#1B2A41}
.swipe{font-weight:700;font-size:26px;color:#1B2A41;margin-top:38px;letter-spacing:1px}
.brand{font-family:'Lora',serif;font-weight:700;font-size:27px;color:#1B2A41;margin-top:22px;letter-spacing:.5px}
.big{font-size:118px;line-height:1.05;margin-top:46px}
.sub{font-weight:700;font-size:30px;letter-spacing:2px;color:#1B2A41;margin-top:22px;text-transform:uppercase;padding:0 90px;line-height:1.3}
.rule{width:680px;height:2px;background:#DED8C9;margin:40px 0}
ul{list-style:none;width:680px;text-align:left}
li{font-size:28px;line-height:1.35;margin:0 0 26px 38px;position:relative}
li:before{content:'';position:absolute;left:-38px;top:13px;width:13px;height:13px;border-radius:50%;background:#9C7A3C}
.quote{font-family:'Lora',serif;font-style:italic;font-size:27px;color:#777;line-height:1.4}
.cta{font-size:28px;line-height:1.4}
.cta b{color:#1B2A41}
"""

def cover(s):
    return f"""<div class=tag>{s['tag']}</div><div class=tagline></div>
<div class='serif ctitle'>{s['title']}</div><div class=csub>{s['sub']}</div>
<div class=bars><div style='height:62px'></div><div style='height:86px;background:#9C7A3C'></div><div style='height:76px'></div><div style='height:60px'></div></div>
<div class=swipe>Arraste para o lado →</div><div class=brand>STEADY MONEY</div>"""

def inner(s):
    lis=''.join(f'<li>{b}</li>' for b in s['bullets'])
    foot = f"<div class=quote>{s['quote']}</div>" if 'quote' in s else f"<div class=cta>{s['cta']}</div>"
    return f"""<div class=tag>{s['tag']}</div><div class='serif big'>{s['big']}</div><div class=sub>{s['sub']}</div>
<div class=rule></div><ul>{lis}</ul><div class=rule style='margin-top:14px'></div>{foot}<div class=brand>STEADY MONEY</div>"""

async def main(spec, outdir):
    data=json.load(open(spec))
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1080,'height':1080})
        for i,s in enumerate(data['slides'],1):
            body = cover(s) if s['type']=='cover' else inner(s)
            await pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>")
            await pg.wait_for_timeout(200)
            await pg.screenshot(path=f"{outdir}/slide{i}.png")
        await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2]))
