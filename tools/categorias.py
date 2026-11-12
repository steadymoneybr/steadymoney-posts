"""Categorias de capa (decididas pelo Vini em 12/11/2026).

No spec.json, a capa ganha "category": confronto | mito | golpe | conceito (padrão: conceito).
A etiqueta da capa vira o rótulo da categoria (a menos que "tag" traga outro texto que não seja "Educação Financeira").
"""
CATS = {
    # rótulo, cor do título, cor do "x", fundo, cor do subtítulo, cor da etiqueta, cor das barras escuras, cor do texto da marca
    'confronto': dict(label='Qual a diferença?', title='#1B2A41', vs='#9C7A3C', bg='#FBF9F4', sub='#2B2B2B', tag='#9C7A3C', bar='#1B2A41', ink='#1B2A41'),
    'mito':      dict(label='Mito ou verdade?',  title='#9C7A3C', vs='#9C7A3C', bg='#FBF9F4', sub='#2B2B2B', tag='#1B2A41', bar='#1B2A41', ink='#1B2A41'),
    'golpe':     dict(label='Alerta de golpe',   title='#FBF9F4', vs='#D9B66A', bg='#1B2A41', sub='#DCD6C8', tag='#D9B66A', bar='#FBF9F4', ink='#FBF9F4'),
    'conceito':  dict(label='Entenda',           title='#1B2A41', vs='#9C7A3C', bg='#FBF9F4', sub='#2B2B2B', tag='#9C7A3C', bar='#1B2A41', ink='#1B2A41'),
}


def cat(s):
    return CATS.get((s.get('category') or 'conceito').lower(), CATS['conceito'])


def label(s):
    t = (s.get('tag') or '').strip()
    if not t or t.lower() in ('educação financeira', 'educacao financeira'):
        return cat(s)['label']
    return t


def rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
