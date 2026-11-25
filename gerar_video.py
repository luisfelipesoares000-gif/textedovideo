import asyncio
import math
import os
import subprocess
import wave
import edge_tts
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# CONFIGURAÇÕES DO VÍDEO
# ==========================================
LARGURA = 1080
ALTURA = 1920
FPS = 30
VOZ = "pt-BR-AntonioNeural"  # Voz masculina brasileira natural e envolvente
SAIDA_FINAL = "tempo_diario_final.mp4"

# Roteiro dividido por cenas (para mudar cenário, expressão e enquadramento)
CENAS = [
    {
        "texto": "Se você visse alguém caído na estrada hoje... você pararia para ajudar, ou fingiria que não viu?",
        "tema": "noite_estrada",
        "expressao": "serio",
        "enquadramento": "centro",
        "titulo_topo": ""
    },
    {
        "texto": "Que a paz de Deus esteja com você! Seja muito bem-vindo ao Tempo Diário.",
        "tema": "amanhecer",
        "expressao": "feliz",
        "enquadramento": "centro",
        "titulo_topo": "TEMPO DIÁRIO"
    },
    {
        "texto": "Na Bíblia, Jesus contou a história de um homem que foi assaltado, ferido, e deixado à beira de um caminho deserto.",
        "tema": "deserto",
        "expressao": "triste",
        "enquadramento": "canto",
        "titulo_topo": ""
    },
    {
        "texto": "Pessoas religiosas e importantes passaram por ele, olharam a sua dor... mas atravessaram para o outro lado e seguiram adiante.",
        "tema": "frio_passando",
        "expressao": "serio",
        "enquadramento": "centro",
        "titulo_topo": ""
    },
    {
        "texto": "Até que um samaritano, alguém de quem ninguém esperava nada, parou. Ele sentiu compaixão, cuidou das feridas daquele homem e o levou para um lugar seguro.",
        "tema": "esperanca",
        "expressao": "admirado",
        "enquadramento": "canto",
        "titulo_topo": ""
    },
    {
        "texto": "O recado de Deus para o seu dia hoje é simples: amor não é só sentimento, é atitude. Não passe direto pela dor de ninguém.",
        "tema": "luz_divina",
        "expressao": "firme",
        "enquadramento": "zoom_perto",
        "titulo_topo": "AMOR É ATITUDE"
    },
    {
        "texto": "Se essa palavra falou com você, deixe o seu amém nos comentários. Que Deus te abençoe e te use hoje. Tenha um excelente dia!",
        "tema": "amanhecer_final",
        "expressao": "feliz",
        "enquadramento": "centro",
        "titulo_topo": "DEIXE SEU AMÉM"
    }
]


def carregar_fonte(tamanho):
    caminhos = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for c in caminhos:
        if os.path.exists(c):
            return ImageFont.truetype(c, tamanho)
    return ImageFont.load_default()


FONTE_LEGENDA = carregar_fonte(66)
FONTE_TITULO = carregar_fonte(52)


async def gerar_audios():
    os.makedirs("temp_audio", exist_ok=True)
    arquivos_wav = []
    for i, cena in enumerate(CENAS):
        mp3_path = f"temp_audio/cena_{i}.mp3"
        wav_path = f"temp_audio/cena_{i}.wav"
        communicate = edge_tts.Communicate(cena["texto"], VOZ, rate="+4%")
        await communicate.save(mp3_path)
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "1", wav_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        arquivos_wav.append(wav_path)
    return arquivos_wav


def ler_envelope_audio(wav_path):
    with wave.open(wav_path, "rb") as wf:
        n_frames = wf.getnframes()
        framerate = wf.getframerate()
        raw = wf.readframes(n_frames)
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

    duracao = n_frames / float(framerate)
    total_video_frames = max(1, int(duracao * FPS))
    samples_por_frame = max(1, int(framerate / FPS))

    volumes = []
    for f in range(total_video_frames):
        ini = f * samples_por_frame
        fim = min(len(samples), ini + samples_por_frame)
        if ini < fim:
            rms = float(np.sqrt(np.mean(samples[ini:fim] ** 2)))
        else:
            rms = 0.0
        volumes.append(min(1.0, rms * 5.5))
    return duracao, volumes, samples, framerate


def gerar_trilha_suave(duracao_total, framerate=44100):
    t = np.linspace(0, duracao_total, int(duracao_total * framerate), endpoint=False)
    # Acordes quentes e suaves (Dó maior / Sol / Lá menor / Fá)
    acordes = [
        [130.81, 164.81, 196.00],
        [98.00, 146.83, 196.00],
        [110.00, 164.81, 220.00],
        [87.31, 130.81, 174.61],
    ]
    trilha = np.zeros_like(t)
    dur_bloco = 4.0
    for idx_t in range(len(t)):
        pass  # Vetorizado abaixo para ficar rápido

    bloco_idx = (t // dur_bloco).astype(int) % len(acordes)
    for b, freqs in enumerate(acordes):
        mask = (bloco_idx == b)
        if np.any(mask):
            tb = t[mask]
            onda = sum(np.sin(2 * np.pi * f * tb) for f in freqs) / len(freqs)
            trilha[mask] = onda

    # Fade in / Fade out e volume bem baixinho (8%)
    fade_samples = min(len(trilha) // 4, framerate * 2)
    trilha[:fade_samples] *= np.linspace(0, 1, fade_samples)
    trilha[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    return trilha * 0.065


def interpolar_cor(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def desenhar_fundo(tema, frame_idx, total_frames):
    img = Image.new("RGB", (LARGURA, ALTURA))
    draw = ImageDraw.Draw(img)

    paletas = {
        "noite_estrada": ((12, 16, 36), (32, 42, 78)),
        "amanhecer": ((28, 36, 68), (218, 128, 52)),
        "deserto": ((55, 28, 18), (186, 102, 45)),
        "frio_passando": ((18, 28, 42), (62, 82, 105)),
        "esperanca": ((48, 28, 14), (235, 168, 64)),
        "luz_divina": ((14, 14, 24), (82, 60, 28)),
        "amanhecer_final": ((30, 44, 82), (242, 160, 70)),
    }
    topo, base = paletas.get(tema, ((20, 24, 40), (60, 75, 110)))

    for y in range(0, ALTURA, 8):
        cor = interpolar_cor(topo, base, y / ALTURA)
        draw.rectangle([0, y, LARGURA, y + 8], fill=cor)

    # Elementos dinâmicos de cenário
    progresso = frame_idx / max(1, total_frames)

    if tema in ("noite_estrada", "deserto", "frio_passando"):
        # Estrada em perspectiva no fundo
        horizonte_y = int(ALTURA * 0.62)
        draw.polygon(
            [(LARGURA // 2 - 40, horizonte_y), (LARGURA // 2 + 40, horizonte_y),
             (LARGURA + 200, ALTURA), (-200, ALTURA)],
            fill=(25, 25, 32)
        )
        # Faixas da estrada se mexendo
        offset = (frame_idx * 12) % 160
        for d in range(0, 900, 160):
            y1 = horizonte_y + int((d + offset) * 0.8)
            y2 = y1 + 45
            if y1 < ALTURA:
                larg = 4 + int((y1 - horizonte_y) * 0.03)
                draw.rectangle([LARGURA // 2 - larg, y1, LARGURA // 2 + larg, min(ALTURA, y2)], fill=(210, 190, 120))

    if tema in ("amanhecer", "esperanca", "luz_divina", "amanhecer_final"):
        # Feixe de luz suave no fundo
        cx = LARGURA // 2 + int(math.sin(progresso * 3) * 30)
        overlay = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        odraw.polygon(
            [(cx - 90, 0), (cx + 90, 0), (cx + 420, ALTURA), (cx - 420, ALTURA)],
            fill=(255, 220, 130, 38)
        )
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Partículas flutuantes sutis para dinamismo
    np.random.seed(42)
    for p in range(22):
        px = int((np.random.randint(0, LARGURA) + frame_idx * (0.4 + (p % 3) * 0.3)) % LARGURA)
        py = int((np.random.randint(0, ALTURA) - frame_idx * (1.2 + (p % 4) * 0.5)) % ALTURA)
        r = 3 + (p % 4) * 2
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 240, 200))

    return img


def desenhar_bonequinho(img, cx, cy, escala, expressao, boca_aberta, piscando, frame_idx):
    # Camada RGBA para desenhar o bonequinho com sombra lateral perfeita
    camada = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
    draw = ImageDraw.Draw(camada)

    # Balanço suave de respiração
    balanco_y = math.sin(frame_idx * 0.14) * 8 * escala
    cy = int(cy + balanco_y)

    # 1. Corpo / Ombros (moletom/camisa estilizada)
    ombro_w = int(230 * escala)
    ombro_h = int(260 * escala)
    topo_corpo = cy + int(115 * escala)
    draw.rounded_rectangle(
        [cx - ombro_w, topo_corpo, cx + ombro_w, topo_corpo + ombro_h],
        radius=int(110 * escala),
        fill=(38, 46, 66, 255),
        outline=(15, 18, 26, 255),
        width=max(3, int(6 * escala))
    )
    # Sombra preta na lateral direita do corpo
    draw.chord(
        [cx - int(10 * escala), topo_corpo, cx + ombro_w, topo_corpo + ombro_h],
        start=-90, end=90,
        fill=(14, 16, 24, 175)
    )

    # 2. Cabeça redondinha (estilo Histórias com Caio)
    raio = int(145 * escala)
    cor_pele = (244, 212, 184, 255)
    draw.ellipse(
        [cx - raio, cy - raio, cx + raio, cy + raio],
        fill=cor_pele,
        outline=(18, 18, 22, 255),
        width=max(4, int(7 * escala))
    )

    # Sombra preta/escura dramática na lateral direita do rosto!
    sombra = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sombra)
    sdraw.ellipse([cx - raio, cy - raio, cx + raio, cy + raio], fill=(0, 0, 0, 0))
    # Máscara circular da cabeça para recortar a sombra certinha
    mask = Image.new("L", (LARGURA, ALTURA), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse([cx - raio + 4, cy - raio + 4, cx + raio - 4, cy + raio - 4], fill=255)

    sombra_forma = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
    sf_draw = ImageDraw.Draw(sombra_forma)
    sf_draw.ellipse(
        [cx + int(18 * escala), cy - raio - int(20 * escala), cx + raio + int(110 * escala), cy + raio + int(20 * escala)],
        fill=(18, 14, 22, 115)
    )
    camada.paste(sombra_forma, (0, 0), mask)

    # Cabelo simples estilizado no topo
    draw.chord(
        [cx - raio - int(4 * escala), cy - raio - int(14 * escala), cx + raio + int(4 * escala), cy - int(10 * escala)],
        start=185, end=355,
        fill=(26, 24, 30, 255)
    )

    # 3. Olhos (piscando ou abertos)
    olho_dx = int(52 * escala)
    olho_y = cy - int(12 * escala)
    olho_r = int(16 * escala)

    if piscando:
        for sx in (-1, 1):
            ox = cx + sx * olho_dx
            draw.line([ox - olho_r, olho_y, ox + olho_r, olho_y], fill=(20, 20, 24, 255), width=max(4, int(7 * escala)))
    else:
        for sx in (-1, 1):
            ox = cx + sx * olho_dx
            draw.ellipse([ox - olho_r, olho_y - int(olho_r * 1.15), ox + olho_r, olho_y + int(olho_r * 1.15)], fill=(20, 20, 26, 255))
            # Brilhinho vivo no olho
            br = max(3, int(5 * escala))
            draw.ellipse([ox - int(5 * escala), olho_y - int(8 * escala), ox - int(5 * escala) + br, olho_y - int(8 * escala) + br], fill=(255, 255, 255, 240))

    # 4. Sobrancelhas conforme expressão
    sob_y = olho_y - int(32 * escala)
    esp_sob = max(4, int(7 * escala))
    if expressao == "serio" or expressao == "firme":
        draw.line([cx - olho_dx - int(22 * escala), sob_y - int(6 * escala), cx - olho_dx + int(18 * escala), sob_y + int(6 * escala)], fill=(22, 20, 24, 255), width=esp_sob)
        draw.line([cx + olho_dx - int(18 * escala), sob_y + int(6 * escala), cx + olho_dx + int(22 * escala), sob_y - int(6 * escala)], fill=(22, 20, 24, 255), width=esp_sob)
    elif expressao == "triste":
        draw.line([cx - olho_dx - int(20 * escala), sob_y + int(7 * escala), cx - olho_dx + int(18 * escala), sob_y - int(7 * escala)], fill=(22, 20, 24, 255), width=esp_sob)
        draw.line([cx + olho_dx - int(18 * escala), sob_y - int(7 * escala), cx + olho_dx + int(20 * escala), sob_y + int(7 * escala)], fill=(22, 20, 24, 255), width=esp_sob)
    else:
        draw.arc([cx - olho_dx - int(22 * escala), sob_y - int(12 * escala), cx - olho_dx + int(22 * escala), sob_y + int(12 * escala)], 190, 350, fill=(22, 20, 24, 255), width=esp_sob)
        draw.arc([cx + olho_dx - int(22 * escala), sob_y - int(12 * escala), cx + olho_dx + int(22 * escala), sob_y + int(12 * escala)], 190, 350, fill=(22, 20, 24, 255), width=esp_sob)

    # 5. Boca sincronizada com o áudio
    boca_y = cy + int(62 * escala)
    boca_w = int(34 * escala)
    abertura = int(max(3, boca_aberta * 34) * escala)
    if boca_aberta > 0.14:
        draw.ellipse(
            [cx - boca_w, boca_y - abertura // 2, cx + boca_w, boca_y + abertura],
            fill=(45, 18, 22, 255),
            outline=(20, 18, 20, 255),
            width=max(3, int(5 * escala))
        )
        # Língua sutil
        draw.chord(
            [cx - int(boca_w * 0.6), boca_y, cx + int(boca_w * 0.6), boca_y + abertura],
            start=0, end=180,
            fill=(205, 95, 105, 255)
        )
    else:
        if expressao in ("feliz", "admirado"):
            draw.arc([cx - boca_w, boca_y - int(14 * escala), cx + boca_w, boca_y + int(22 * escala)], 15, 165, fill=(20, 18, 22, 255), width=max(4, int(6 * escala)))
        else:
            draw.line([cx - int(boca_w * 0.8), boca_y, cx + int(boca_w * 0.8), boca_y], fill=(20, 18, 22, 255), width=max(4, int(6 * escala)))

    return Image.alpha_composite(img.convert("RGBA"), camada).convert("RGB")


def desenhar_legenda_e_titulo(img, texto_cena, titulo_topo, progresso_cena):
    draw = ImageDraw.Draw(img)

    # Título chamativo no topo (quando houver)
    if titulo_topo:
        bbox = draw.textbbox((0, 0), titulo_topo, font=FONTE_TITULO)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (LARGURA - tw) // 2
        ty = 140
        draw.rounded_rectangle([tx - 36, ty - 20, tx + tw + 36, ty + th + 24], radius=24, fill=(245, 185, 50))
        draw.text((tx, ty), titulo_topo, font=FONTE_TITULO, fill=(18, 18, 22))

    # Quebra o texto da cena em blocos curtos (3 a 4 palavras por vez) para ficar dinâmico
    palavras = texto_cena.split()
    blocos = [" ".join(palavras[i:i + 4]) for i in range(0, len(palavras), 4)]
    idx_bloco = min(len(blocos) - 1, int(progresso_cena * len(blocos)))
    bloco_atual = blocos[idx_bloco].upper()

    # Quebra em até 2 linhas se ficar muito largo
    linhas = []
    linha_temp = ""
    for p in bloco_atual.split():
        teste = (linha_temp + " " + p).strip()
        if draw.textbbox((0, 0), teste, font=FONTE_LEGENDA)[2] < LARGURA - 120:
            linha_temp = teste
        else:
            linhas.append(linha_temp)
            linha_temp = p
    if linha_temp:
        linhas.append(linha_temp)

    y_base = int(ALTURA * 0.74)
    for l_idx, linha in enumerate(linhas):
        bbox = draw.textbbox((0, 0), linha, font=FONTE_LEGENDA)
        lw = bbox[2] - bbox[0]
        lx = (LARGURA - lw) // 2
        ly = y_base + l_idx * 85
        # Contorno preto grosso para leitura perfeita
        for dx in (-5, 0, 5):
            for dy in (-5, 0, 5):
                if dx != 0 or dy != 0:
                    draw.text((lx + dx, ly + dy), linha, font=FONTE_LEGENDA, fill=(0, 0, 0))
        cor_texto = (255, 225, 65) if l_idx % 2 == 0 else (255, 255, 255)
        draw.text((lx, ly), linha, font=FONTE_LEGENDA, fill=cor_texto)

    return img


def main():
    print("1. Gerando narração neural em português...")
    arquivos_wav = asyncio.run(gerar_audios())

    print("2. Processando áudio e renderizando cenas...")
    os.makedirs("temp_video", exist_ok=True)
    video_sem_audio = "temp_video/sem_audio.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(video_sem_audio, fourcc, FPS, (LARGURA, ALTURA))

    todas_amostras_voz = []
    framerate_global = 44100

    for idx_cena, (cena, wav_path) in enumerate(zip(CENAS, arquivos_wav)):
        duracao, volumes, samples, framerate = ler_envelope_audio(wav_path)
        framerate_global = framerate
        todas_amostras_voz.append(samples)

        total_frames = len(volumes)
        print(f"   Renderizando cena {idx_cena + 1}/{len(CENAS)} ({duracao:.1f}s)...")

        for f in range(total_frames):
            progresso = f / max(1, total_frames)
            img = desenhar_fundo(cena["tema"], f + idx_cena * 50, total_frames)

            # Enquadramento dinâmico (muda posição e zoom do bonequinho)
            enq = cena["enquadramento"]
            if enq == "canto":
                cx, cy, esc = int(LARGURA * 0.72), int(ALTURA * 0.50), 0.95 + 0.05 * progresso
            elif enq == "zoom_perto":
                cx, cy, esc = LARGURA // 2, int(ALTURA * 0.46), 1.32 + 0.08 * progresso
            else:
                cx, cy, esc = LARGURA // 2, int(ALTURA * 0.48), 1.12 + 0.06 * math.sin(progresso * math.pi)

            piscando = (f % 85) in (0, 1, 2)
            img = desenhar_bonequinho(img, cx, cy, esc, cena["expressao"], volumes[f], piscando, f)
            img = desenhar_legenda_e_titulo(img, cena["texto"], cena["titulo_topo"], progresso)

            frame_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            writer.write(frame_bgr)

    writer.release()

    print("3. Mixando voz + trilha sonora suave...")
    voz_completa = np.concatenate(todas_amostras_voz)
    dur_total = len(voz_completa) / float(framerate_global)
    trilha = gerar_trilha_suave(dur_total, framerate_global)
    mix = np.clip(voz_completa + trilha[:len(voz_completa)], -0.98, 0.98)
    mix_int16 = (mix * 32767).astype(np.int16)

    audio_mix_wav = "temp_audio/mix_final.wav"
    with wave.open(audio_mix_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate_global)
        wf.writeframes(mix_int16.tobytes())

    print("4. Gerando MP4 final compatível com celular, TikTok, Reels e Shorts...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_sem_audio,
        "-i", audio_mix_wav,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", SAIDA_FINAL
    ], check=True)

    print(f"Concluído! Vídeo salvo em: {SAIDA_FINAL}")


if __name__ == "__main__":
    main()
