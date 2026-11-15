"""Narração com voz de IA (ElevenLabs), usada pelo video.py e pelo steady.py.

- Chave: variável de ambiente ELEVENLABS_API_KEY (NUNCA no repositório, que é público).
- Voz padrão: Lucas (escolhida pelo Vini em 15/11/2026). Troque só se ele pedir.
- Cache: cada trecho gerado fica em <pasta do post>/.narracao/<hash>.mp3 (fora do git), para não gastar
  crédito de novo quando o vídeo é gerado outra vez com o mesmo texto.
"""
import hashlib, json, os, subprocess, urllib.request

VOICE_ID = '7lu3ze7orhWaNeSPowWx'  # Lucas - Engaging, Captivating and Kind (pt-BR)
MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.45, 'similarity_boost': 0.8, 'style': 0.25, 'use_speaker_boost': True}


def ativa():
    return bool(os.environ.get('ELEVENLABS_API_KEY'))


def tts(texto, pasta):
    """Gera (ou pega do cache) o mp3 de um trecho e devolve o caminho."""
    cache = os.path.join(pasta, '.narracao'); os.makedirs(cache, exist_ok=True)
    h = hashlib.sha1(f'{VOICE_ID}|{MODEL}|{json.dumps(SETTINGS)}|{texto}'.encode()).hexdigest()[:16]
    out = os.path.join(cache, h + '.mp3')
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return out
    body = json.dumps({'text': texto, 'model_id': MODEL, 'voice_settings': SETTINGS, 'language_code': 'pt'}).encode()
    req = urllib.request.Request(
        f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128', data=body,
        headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json'})
    try:
        data = urllib.request.urlopen(req, timeout=90).read()
    except urllib.error.HTTPError as e:
        if e.code == 400 and b'language_code' in e.read():  # modelo sem language_code: tenta sem
            req.data = json.dumps({'text': texto, 'model_id': MODEL, 'voice_settings': SETTINGS}).encode()
            data = urllib.request.urlopen(req, timeout=90).read()
        else:
            raise
    open(out, 'wb').write(data)
    return out


def duracao(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def mixar(video, out, falas, total, trilha):
    """Junta o vídeo mudo com as falas [(inicio_s, mp3)] e a trilha padrão bem baixinha por baixo da voz."""
    ins = ['-i', video, '-stream_loop', '-1', '-i', trilha]
    fc = [f'[1:a]atrim=0:{total},afade=t=in:d=0.4,afade=t=out:st={max(0, total - 2)}:d=2,volume=0.10,aresample=44100[m]']
    labels = []
    for i, (t0, mp3) in enumerate(falas):
        ins += ['-i', mp3]; ms = int(t0 * 1000)
        fc.append(f'[{i + 2}:a]aresample=44100,adelay={ms}|{ms},apad[v{i}]'); labels.append(f'[v{i}]')
    fc.append(f'{"".join(labels)}amix=inputs={len(labels)}:normalize=0,atrim=0:{total}[voz]')
    fc.append('[voz]loudnorm=I=-15:TP=-1.5:LRA=9,aresample=44100[vz]')  # loudnorm sai em 192 kHz: volta pra 44,1
    fc.append('[vz][m]amix=inputs=2:normalize=0:duration=longest,atrim=0:' + str(total) + '[a]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins +
                   ['-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac',
                    '-b:a', '160k', '-t', str(total), '-movflags', '+faststart', out], check=True)
