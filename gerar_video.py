import asyncio
import math
import os
import subprocess
import wave
import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Configurações do vídeo e áudio
LARGURA, ALTURA = 1280, 720
FPS = 24
SAMPLE_RATE = 44100

VOZ_1 = "pt-BR-AntonioNeural"     # Voz masculina calma
VOZ_2 = "pt-BR-FranciscaNeural"   # Voz feminina calma

# Roteiro dinâmico em diálogo para o canal Tempo Diário
ROTEIRO = [
    {
        "personagem": 1,
        "texto": "Ei... posso te fazer uma pergunta sincera? Se você visse alguém caído na estrada hoje... você pararia, ou fingiria que não viu?",
    },
    {
        "personagem": 2,
        "texto": "Nossa, que pergunta forte... Que a paz de Deus esteja com você. Seja muito bem-vindo ao Tempo Diário.",
    },
    {
        "personagem": 1,
        "texto": "Sabe... na Bíblia, um homem foi assaltado, ferido e deixado sozinho à beira de um caminho deserto.",
    },
    {
        "personagem": 2,
        "texto": "E pessoas religiosas e importantes passaram por ele... olharam para a sua dor, mas atravessaram para o outro lado e seguiram adiante.",
    },
    {
        "personagem": 1,
        "texto": "Até que veio um samaritano. Alguém de quem ninguém esperava nada... e ele parou.",
    },
    {
        "personagem": 2,
        "texto": "Ele sentiu compaixão de verdade. Cuidou das feridas daquele homem e o levou para um lugar seguro.",
    },
    {
        "personagem": 1,
        "texto": "O recado de Deus para o seu dia hoje é simples... amor não é só sentimento. Amor é atitude.",
    },
    {
        "personagem": 2,
        "texto": "Não passe direto pela dor de ninguém. Que Deus te abençoe e te use muito hoje. Tenha um excelente dia.",
    },
]


async def sintetizar_falas():
    for i, item in enumerate(ROTEIRO):
        voz = VOZ_1 if item["personagem"] == 1 else VOZ_2
        pitch = "-6Hz" if item["personagem"] == 1 else "-3Hz"
        rate = "-16%"
        mp3_path = f"temp_fala_{i}.mp3"

        for tentativa in range(3):
            try:
                comunicador = edge_tts.Communicate(
                    item["texto"], voz, rate=rate, pitch=pitch
                )
                await comunicador.save(mp3_path)
                break
            except Exception as e:
                if tentativa == 2:
                    raise e
                await asyncio.sleep(2)


def mp3_para_array(mp3_path, wav_path):
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", mp3_path,
            "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "wav", wav_path
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    with wave.open(wav_path, "rb") as wf:
        raw = wf.readframes(wf.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def criar_fundo_asmr(total_amostras):
    t = np.linspace(0, total_amostras / SAMPLE_RATE, total_amostras, dtype=np.float32)
    # Acorde calmo (Dó maior com 7ª e 9ª)
    freqs = [130.81, 196.00, 246.94, 293.66, 329.63]
    pad = np.zeros(total_amostras, dtype=np.float32)
    for f in freqs:
        pad += np.sin(2.0 * np.pi * f * t)
    pad /= len(freqs)

    # Respiração lenta no volume do som ambiente
    lfo = 0.65 + 0.35 * np.sin(2.0 * np.pi * 0.12 * t)
    pad = pad * lfo * 0.045

    # Fade in e fade out suaves
    fade_in = min(int(SAMPLE_RATE * 2.0), total_amostras)
    fade_out = min(int(SAMPLE_RATE * 2.5), total_amostras)
    pad[:fade_in] *= np.linspace(0.0, 1.0, fade_in, dtype=np.float32)
    pad[-fade_out:] *= np.linspace(1.0, 0.0, fade_out, dtype=np.float32)
    return pad


def carregar_fonte(tamanho, negrito=False):
    caminhos = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if negrito else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for c in caminhos:
        if os.path.exists(c):
            return ImageFont.truetype(c, tamanho)
    return ImageFont.load_default()


def quebrar_texto(draw, texto, fonte, largura_max):
    palavras = texto.split()
    linhas = []
    atual = ""
    for p in palavras:
        teste = f"{atual} {p}".strip()
        bbox = draw.textbbox((0, 0), teste, font=fonte)
        if (bbox[2] - bbox[0]) <= largura_max:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def criar_cenario_base():
    img = Image.new("RGB", (LARGURA, ALTURA))
    draw = ImageDraw.Draw(img)

    # Céu gradiente suave de entardecer
    for y in range(ALTURA):
        r = int(28 + (95 - 28) * (y / ALTURA))
        g = int(32 + (78 - 32) * (y / ALTURA))
        b = int(68 + (115 - 68) * (y / ALTURA))
        draw.line([(0, y), (LARGURA, y)], fill=(r, g, b))

    # Brilho suave no horizonte
    draw.ellipse([480, 260, 800, 580], fill=(112, 92, 128))
    draw.ellipse([540, 310, 740, 510], fill=(155, 118, 138))

    # Colinas suaves no fundo e na frente
    draw.ellipse([-150, 460, 850, 820], fill=(42, 54, 72))
    draw.ellipse([450, 470, 1450, 840], fill=(35, 45, 64))
    draw.rectangle([0, 515, LARGURA, ALTURA], fill=(32, 41, 58))
    return img


def desenhar_bonequinho(draw, cx, cy, cor_roupa, cor_pele, cor_cabelo, falando, boca_aberta, piscando, tempo, eh_feminino=False):
    borda = (35, 34, 48)
    balanco = math.sin(tempo * 7.0) * (5.0 if falando else 1.2)
    cy = int(cy + balanco)

    # Sombra suave no chão
    draw.ellipse([cx - 75, 505, cx + 75, 530], fill=(22, 28, 42))

    # Corpinho redondinho
    draw.ellipse([cx - 64, cy + 55, cx + 64, cy + 165], fill=cor_roupa, outline=borda, width=5)

    # Mãozinhas redondas
    mao_y = cy + 105 - (int(abs(math.sin(tempo * 5.0)) * 12) if falando else 0)
    draw.ellipse([cx - 74, mao_y, cx - 44, mao_y + 30], fill=cor_pele, outline=borda, width=4)
    draw.ellipse([cx + 44, mao_y, cx + 74, mao_y + 30], fill=cor_pele, outline=borda, width=4)

    # Cabelo atrás (se feminino)
    if eh_feminino:
        draw.ellipse([cx - 98, cy - 90, cx + 98, cy + 75], fill=cor_cabelo, outline=borda, width=5)

    # Cabeça bem redondinha
    r = 88
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cor_pele, outline=borda, width=5)

    # Cabelinho no topo
    if eh_feminino:
        draw.chord([cx - 88, cy - 94, cx + 88, cy - 10], start=185, end=355, fill=cor_cabelo, outline=borda, width=4)
    else:
        draw.chord([cx - 84, cy - 95, cx + 84, cy - 22], start=185, end=355, fill=cor_cabelo, outline=borda, width=4)
        draw.ellipse([cx - 18, cy - 105, cx + 24, cy - 75], fill=cor_cabelo, outline=borda, width=4)

    # Bochechas rosadas
    draw.ellipse([cx - 62, cy + 10, cx - 36, cy + 28], fill=(247, 168, 168))
    draw.ellipse([cx + 36, cy + 10, cx + 62, cy + 28], fill=(247, 168, 168))

    # Olhos
    for ox in (cx - 32, cx + 32):
        oy = cy - 12
        if piscando:
            draw.line([(ox - 12, oy), (ox + 12, oy)], fill=borda, width=5)
        else:
            draw.ellipse([ox - 13, oy - 16, ox + 13, oy + 16], fill=(255, 255, 255), outline=borda, width=4)
            draw.ellipse([ox - 7, oy - 9, ox + 7, oy + 9], fill=borda)
            draw.ellipse([ox - 4, oy - 7, ox + 1, oy - 2], fill=(255, 255, 255))

    # Boca (abre proporcional ao volume da voz)
    by = cy + 32
    if falando and boca_aberta > 0.08:
        abertura = int(6 + min(boca_aberta, 1.0) * 20)
        draw.ellipse([cx - 16, by - abertura // 2, cx + 16, by + abertura], fill=(165, 68, 78), outline=borda, width=4)
        if abertura > 12:
            draw.chord([cx - 10, by + 2, cx + 10, by + abertura - 2], start=0, end=180, fill=(235, 130, 140))
    else:
        draw.arc([cx - 16, by - 6, cx + 16, by + 12], start=15, end=165, fill=borda, width=4)


def main():
    print("1. Gerando vozes ASMR...")
    asyncio.run(sintetizar_falas())

    pausa_inicial = int(SAMPLE_RATE * 0.7)
    pausa_entre = int(SAMPLE_RATE * 0.45)
    pausa_final = int(SAMPLE_RATE * 1.4)

    partes_audio = [np.zeros(pausa_inicial, dtype=np.float32)]
    segmentos = []
    pos_atual = pausa_inicial

    for i, item in enumerate(ROTEIRO):
        mp3_path = f"temp_fala_{i}.mp3"
        wav_path = f"temp_fala_{i}.wav"
        arr = mp3_para_array(mp3_path, wav_path)

        inicio_s = pos_atual / SAMPLE_RATE
        fim_s = (pos_atual + len(arr)) / SAMPLE_RATE
        segmentos.append({
            "inicio": inicio_s,
            "fim": fim_s,
            "personagem": item["personagem"],
            "texto": item["texto"],
            "inicio_amostra": pos_atual,
            "fim_amostra": pos_atual + len(arr),
        })

        partes_audio.append(arr)
        pos_atual += len(arr)

        if i < len(ROTEIRO) - 1:
            partes_audio.append(np.zeros(pausa_entre, dtype=np.float32))
            pos_atual += pausa_entre

    partes_audio.append(np.zeros(pausa_final, dtype=np.float32))
    voz_completa = np.concatenate(partes_audio)

    # Normaliza suavemente e mistura trilha ASMR
    pico = np.max(np.abs(voz_completa))
    if pico > 0:
        voz_completa = (voz_completa / pico) * 0.85

    trilha = criar_fundo_asmr(len(voz_completa))
    audio_final = np.clip(voz_completa + trilha, -0.98, 0.98)

    with wave.open("temp_audio_final.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((audio_final * 32767.0).astype(np.int16).tobytes())

    duracao_total = len(audio_final) / SAMPLE_RATE
    total_frames = int(math.ceil(duracao_total * FPS))
    print(f"2. Renderizando {total_frames} frames ({duracao_total:.1f}s)...")

    cenario = criar_cenario_base()
    fonte_legenda = carregar_fonte(28, negrito=True)
    fonte_canal = carregar_fonte(20, negrito=True)

    # Partículas suaves no fundo
    rng = np.random.default_rng(42)
    particulas = [
        (rng.uniform(40, LARGURA - 40), rng.uniform(50, 460), rng.uniform(0.5, 1.5), rng.uniform(0, 6.28))
        for _ in range(24)
    ]

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{LARGURA}x{ALTURA}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-i", "temp_audio_final.wav",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        "video.mp4",
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    amostras_por_frame = SAMPLE_RATE // FPS

    for frame_idx in range(total_frames):
        t = frame_idx / FPS
        frame = cenario.copy().convert("RGBA")
        overlay = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)

        # Desenha vagalumes / luzinhas suaves
        for px, py, vel, fase in particulas:
            x_p = (px + math.sin(t * 0.4 * vel + fase) * 18) % LARGURA
            y_p = py + math.cos(t * 0.6 * vel + fase) * 10
            alpha = int(70 + 60 * math.sin(t * 1.5 + fase))
            ov_draw.ellipse([x_p - 3, y_p - 3, x_p + 3, y_p + 3], fill=(255, 232, 179, alpha))

        # Identifica quem está falando neste instante
        seg_atual = None
        for seg in segmentos:
            if seg["inicio"] <= t <= seg["fim"]:
                seg_atual = seg
                break

        # Amplitude do áudio no frame atual para sincronia labial
        a_ini = int(t * SAMPLE_RATE)
        a_fim = min(a_ini + amostras_por_frame, len(voz_completa))
        rms = float(np.sqrt(np.mean(voz_completa[a_ini:a_fim] ** 2))) if a_fim > a_ini else 0.0
        boca = min(rms * 5.2, 1.0)

        p1_falando = seg_atual is not None and seg_atual["personagem"] == 1
        p2_falando = seg_atual is not None and seg_atual["personagem"] == 2

        piscando_1 = (t % 3.7) < 0.14
        piscando_2 = ((t + 1.4) % 4.1) < 0.14

        # Badge do canal no topo
        ov_draw.rounded_rectangle([32, 24, 295, 64], radius=20, fill=(20, 22, 36, 150))
        ov_draw.text((52, 33), "Tempo Diário  •  @tempodiario", font=fonte_canal, fill=(255, 224, 170, 235))

        frame = Image.alpha_composite(frame, overlay).convert("RGB")
        draw = ImageDraw.Draw(frame)

        # Desenha os 2 bonequinhos
        desenhar_bonequinho(
            draw, cx=390, cy=350,
            cor_roupa=(107, 163, 214),
            cor_pele=(255, 224, 189),
            cor_cabelo=(61, 52, 74),
            falando=p1_falando,
            boca_aberta=boca if p1_falando else 0.0,
            piscando=piscando_1,
            tempo=t,
            eh_feminino=False,
        )
        desenhar_bonequinho(
            draw, cx=890, cy=355,
            cor_roupa=(155, 138, 196),
            cor_pele=(250, 212, 192),
            cor_cabelo=(74, 53, 49),
            falando=p2_falando,
            boca_aberta=boca if p2_falando else 0.0,
            piscando=piscando_2,
            tempo=t,
            eh_feminino=True,
        )

        # Caixa de legenda no rodapé
        if seg_atual is not None:
            linhas = quebrar_texto(draw, seg_atual["texto"], fonte_legenda, 1080)
            alt_linha = 38
            alt_caixa = len(linhas) * alt_linha + 28
            y_topo = ALTURA - alt_caixa - 24

            frame_rgba = frame.convert("RGBA")
            leg_ov = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
            leg_draw = ImageDraw.Draw(leg_ov)
            leg_draw.rounded_rectangle(
                [70, y_topo, LARGURA - 70, ALTURA - 24],
                radius=22,
                fill=(18, 20, 34, 190),
            )
            for idx_l, linha in enumerate(linhas):
                bbox = leg_draw.textbbox((0, 0), linha, font=fonte_legenda)
                larg_l = bbox[2] - bbox[0]
                x_l = (LARGURA - larg_l) // 2
                y_l = y_topo + 14 + idx_l * alt_linha
                leg_draw.text((x_l, y_l), linha, font=fonte_legenda, fill=(255, 255, 255, 245))

            frame = Image.alpha_composite(frame_rgba, leg_ov).convert("RGB")

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()

    # Limpa arquivos temporários
    for f in os.listdir("."):
        if f.startswith("temp_"):
            os.remove(f)
    print("3. Vídeo video.mp4 gerado com sucesso!")


if __name__ == "__main__":
    main()
