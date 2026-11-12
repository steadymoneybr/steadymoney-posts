"""Coloca a capa (capa-video.jpg) como 1º quadro do vídeo (0,1 s, imperceptível pra quem assiste).

Por quê: o Instagram e o TikTok usam o 1º quadro como capa quando a capa personalizada não é aplicada
(ex.: TikTok de conta pessoal ignora a capa enviada pelo Metricool). Assim o feed sempre mostra a capa da categoria.

Uso: python3 tools/capa_inicio.py posts/AAAA-MM-DD-slug/capa-video.jpg posts/AAAA-MM-DD-slug/video.mp4
(Rode uma vez só, depois de gerar o vídeo final. Sobrescreve o video.mp4.)
"""
import shutil, subprocess, sys

capa, video = sys.argv[1], sys.argv[2]
tmp = video + '.tmp.mp4'
D = 0.1
fc = (f'[0:v]scale=1080:1920,fps=30,format=yuv420p,setsar=1[c];[1:v]fps=30,format=yuv420p,setsar=1[v];'
      f'anullsrc=r=48000:cl=stereo,atrim=0:{D}[s];[1:a]aresample=48000[a];'
      f'[c][s][v][a]concat=n=2:v=1:a=1[ov][oa]')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-t', str(D), '-i', capa, '-i', video,
                '-filter_complex', fc, '-map', '[ov]', '-map', '[oa]', '-c:v', 'libx264', '-preset', 'veryfast',
                '-crf', '20', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', tmp], check=True)
shutil.move(tmp, video)
print(f'{video}: capa no 1º quadro')
