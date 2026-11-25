import asyncio
import math
import os
import re
import subprocess
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import imageio_ffmpeg

# ==========================================================
# CONFIGURAÇÕES DO CANAL E VOZES NEURAIS
# ==========================================================
CANAL_NOME = "TEMPO DIÁRIO"
CANAL_HANDLE = "@tempodiario"
ARQUIVO_SAIDA = "salomao_tempodiario.mp4"

LARGURA, ALTURA = 1080, 1920
FPS = 30
SAMPLE_RATE = 44100
PAUSA_ENTRE_BEATS = 0.06
PAUSA_ENTRE_CENAS = 0.12

VOZ_APRESENTADOR = "pt-BR-FabioNeural"   # Jovem, expressivo e dinâmico
VOZ_EPICA = "pt-BR-DonatoNeural"         # Grave e solene para citações bíblicas

# ==========================================================
# ROTEIRO COM BEATS DINÂMICOS (2 VOZES + 5 HUMORES)
# ==========================================================
CENAS = [
    {
        "id": "gancho",
        "titulo": "O MISTÉRIO DE SALOMÃO",
        "cor_topo": (14, 16, 40),
        "cor_base": (6, 8, 18),
        "cor_glow": (245, 183, 0),
        "destaque": (255, 209, 102),
        "beats": [
            {
                "voz": VOZ_APRESENTADOR, "rate": "+18%", "pitch": "+4Hz", "humor": "empolgado",
                "texto": "O homem mais sábio que já pisou na Terra...",
            },
            {
                "voz": VOZ_APRESENTADOR, "rate": "+14%", "pitch": "-2Hz", "humor": "choque",
                "texto": "terminou no inferno? A história de Salomão tem um final que quase ninguém percebeu.",
            },
        ],
    },
    {
        "id": "auge",
        "titulo": "GIBEOM • O AUGE",
        "cor_topo": (18, 30, 62),
        "cor_base": (8, 12, 24),
        "cor_glow": (255, 195, 30),
        "destaque": (255, 209, 102),
        "beats": [
            {
                "voz": VOZ_APRESENTADOR, "rate": "+18%", "pitch": "+3Hz", "humor": "empolgado",
                "texto": "Tudo começou em Gibeom. Em vez de dinheiro ou poder, Salomão pediu sabedoria.",
            },
            {
                "voz": VOZ_APRESENTADOR, "rate": "+20%", "pitch": "+5Hz", "humor": "empolgado",
                "texto": "Deus gostou tanto que deu tudo a ele: seiscentos e sessenta e seis talentos de ouro por ano, três mil provérbios e o templo mais glorioso do mundo!",
            },
        ],
    },
    {
        "id": "queda",
        "titulo": "1 REIS 11 • A QUEDA",
        "cor_topo": (48, 12, 30),
        "cor_base": (14, 6, 14),
        "cor_glow": (220, 38, 68),
        "destaque": (255, 89, 100),
        "beats": [
            {
                "voz": VOZ_APRESENTADOR, "rate": "+18%", "pitch": "+3Hz", "humor": "choque",
                "texto": "Mas a glória virou armadilha! A Bíblia diz que ele teve setecentas esposas e trezentas concubinas. Mil mulheres!",
            },
            {
                "voz": VOZ_APRESENTADOR, "rate": "+12%", "pitch": "-3Hz", "humor": "tenso",
                "texto": "E na velhice, elas desviaram o coração dele para deuses falsos, com altares proibidos em Jerusalém.",
            },
        ],
    },
    {
        "id": "ira",
        "titulo": "O REINO RASGADO",
        "cor_topo": (56, 16, 16),
        "cor_base": (14, 6, 8),
        "cor_glow": (255, 70, 50),
        "destaque": (255, 95, 75),
        "beats": [
            {
                "voz": VOZ_APRESENTADOR, "rate": "+14%", "pitch": "-2Hz", "humor": "tenso",
                "texto": "A resposta de Deus foi dura. Em Primeiro Reis capítulo onze, o Senhor se irou porque havia aparecido a Salomão duas vezes...",
            },
            {
                "voz": VOZ_EPICA, "rate": "+6%", "pitch": "-6Hz", "humor": "epico",
                "texto": "e avisou: o reino seria rasgado, tirando dez tribos da mão de sua família!",
            },
        ],
    },
    {
        "id": "silencio",
        "titulo": "O SILÊNCIO EM REIS",
        "cor_topo": (20, 22, 38),
        "cor_base": (8, 9, 15),
        "cor_glow": (120, 140, 200),
        "destaque": (150, 185, 255),
        "beats": [
            {
                "voz": VOZ_APRESENTADOR, "rate": "+12%", "pitch": "-2Hz", "humor": "misterio",
                "texto": "E aqui mora o susto. O livro de Reis conta a morte de Salomão sem registrar nenhum pedido de perdão.",
            },
            {
                "voz": VOZ_APRESENTADOR, "rate": "+16%", "pitch": "+2Hz", "humor": "choque",
                "texto": "E séculos depois, Neemias ainda usa Salomão como alerta de quem pecou gravemente!",
            },
        ],
    },
    {
        "id": "eclesiastes",
        "titulo": "PISTA 1 • ECLESIASTES",
        "cor_topo": (42, 28, 14),
        "cor_base": (14, 10, 6),
        "cor_glow": (255, 175, 65),
        "destaque": (255, 209, 102),
        "beats": [
            {
                "voz": VOZ_APRESENTADOR, "rate": "+18%", "pitch": "+4Hz", "humor": "misterio",
                "texto": "Então ele se perdeu para sempre? Espera! Olha para o livro de Eclesiastes. Um rei cansado no fim da vida chama todo aquele luxo de vaidade...",
            },
            {
                "voz": VOZ_EPICA, "rate": "+4%", "pitch": "-6Hz", "humor": "epico",
                "texto": "e fecha com uma frase: Teme a Deus e guarda os seus mandamentos!",
            },
        ],
    },
    {
        "id": "alianca",
        "titulo": "PISTA 2 • 2 SAMUEL 7",
        "cor_topo": (12, 38, 46),
        "cor_base": (6, 14, 20),
        "cor_glow": (46, 196, 182),
        "destaque": (72, 229, 214),
        "beats": [
            {
                "voz": VOZ_APRESENTADOR, "rate": "+16%", "pitch": "+2Hz", "humor": "convicto",
                "texto": "E tem uma segunda pista pesada em Segundo Samuel sete. Deus prometeu a Davi:",
            },
            {
                "voz": VOZ_EPICA, "rate": "+5%", "pitch": "-6Hz", "humor": "epico",
                "texto": "se ele pecar, eu o castigarei, mas a minha misericórdia não se apartará dele, como apartei de Saul.",
            },
        ],
    },
    {
        "id": "final",
        "titulo": "VEREDITO FINAL",
        "cor_topo": (18, 20, 46),
        "cor_base": (6, 8, 18),
        "cor_glow": (245, 183, 0),
        "destaque": (255, 209, 102),
        "beats": [
            {
                "voz": VOZ_APRESENTADOR, "rate": "+16%", "pitch": "+2Hz", "humor": "convicto",
                "texto": "A Bíblia não crava uma frase final, mas deixa o rastro do arrependimento e da aliança.",
            },
            {
                "voz": VOZ_APRESENTADOR, "rate": "+20%", "pitch": "+5Hz", "humor": "empolgado",
                "texto": "E aí, para você: Salomão foi salvo ou não? Comenta sim ou não e segue o Tempo Diário!",
            },
        ],
    },
]

_FONT_CACHE = {}


def carregar_fonte(tamanho):
    tamanho = max(12, int(tamanho))
    if tamanho in _FONT_CACHE:
        return _FONT_CACHE[tamanho]
    caminhos = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    fonte = None
    for p in caminhos:
        if os.path.exists(p):
            try:
                fonte = ImageFont.truetype(p, tamanho)
                break
            except Exception:
                pass
    if fonte is None:
        try:
            fonte = ImageFont.load_default(size=tamanho)
        except TypeError:
            fonte = ImageFont.load_default()
    _FONT_CACHE[tamanho] = fonte
    return fonte


def texto_largura(draw, txt, fonte):
    bbox = draw.textbbox((0, 0), txt, font=fonte)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def texto_centralizado(draw, x, y, txt, fonte, cor, stroke_w=0, stroke_c=(0, 0, 0)):
    w, h = texto_largura(draw, txt, fonte)
    draw.text(
        (x - w / 2, y - h / 2), txt, font=fonte, fill=cor,
        stroke_width=stroke_w, stroke_fill=stroke_c,
    )


def ease_out_cubic(x):
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3


def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1.0 + c3 * ((x - 1.0) ** 3) + c1 * ((x - 1.0) ** 2)


# ==========================================================
# SÍNTESE DE VOZ NEURAL COM FALLBACK SEGURO
# ==========================================================
async def sintetizar_beat(beat, mp3_path):
    tentativas = [
        {"voice": beat["voz"], "rate": beat["rate"], "pitch": beat["pitch"]},
        {"voice": beat["voz"], "rate": beat["rate"], "pitch": "+0Hz"},
        {"voice": "pt-BR-AntonioNeural", "rate": "+15%", "pitch": "+0Hz"},
    ]
    for cfg in tentativas:
        try:
            try:
                comm = edge_tts.Communicate(
                    beat["texto"], cfg["voice"], rate=cfg["rate"],
                    pitch=cfg["pitch"], boundary="WordBoundary"
                )
            except TypeError:
                comm = edge_tts.Communicate(
                    beat["texto"], cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"]
                )

            word_ev, sent_ev = [], []
            with open(mp3_path, "wb") as f:
                async for chunk in comm.stream():
                    ctype = chunk.get("type")
                    if ctype == "audio":
                        f.write(chunk["data"])
                    elif ctype == "WordBoundary":
                        word_ev.append({
                            "text": chunk["text"].strip(),
                            "start": chunk["offset"] / 10_000_000.0,
                            "dur": max(0.07, chunk["duration"] / 10_000_000.0),
                        })
                    elif ctype == "SentenceBoundary":
                        sent_ev.append({
                            "text": chunk["text"].strip(),
                            "start": chunk["offset"] / 10_000_000.0,
                            "dur": max(0.18, chunk["duration"] / 10_000_000.0),
                        })
            if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 500:
                return word_ev, sent_ev
        except Exception:
            continue
    raise RuntimeError(f"Falha ao sintetizar áudio para: {beat['texto']}")


def decodificar_mp3_pcm(ffmpeg_exe, mp3_path):
    cmd = [
        ffmpeg_exe, "-y", "-i", mp3_path,
        "-f", "s16le", "-ac", "1", "-ar", str(SAMPLE_RATE), "pipe:1",
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    return np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def construir_palavras_fallback(texto, duracao, sent_events):
    out = []
    if sent_events:
        for s in sent_events:
            tokens = s["text"].split()
            if not tokens:
                continue
            pesos = [max(2, len(re.sub(r"\W+", "", t))) for t in tokens]
            soma = sum(pesos)
            cur = s["start"]
            for t, p in zip(tokens, pesos):
                d = s["dur"] * (p / soma)
                out.append({"text": t, "start": cur, "dur": d})
                cur += d
    else:
        tokens = texto.split()
        pesos = [max(2, len(re.sub(r"\W+", "", t))) for t in tokens]
        soma = max(1, sum(pesos))
        cur, util = 0.04, max(0.4, duracao - 0.08)
        for t, p in zip(tokens, pesos):
            d = util * (p / soma)
            out.append({"text": t, "start": cur, "dur": d})
            cur += d
    return out


def agrupar_legendas(palavras):
    grupos, atual = [], []
    for p in palavras:
        atual.append(p)
        if len(atual) >= 3 or p["text"].endswith((".", "!", "?", ":", ";")):
            grupos.append({
                "start": atual[0]["start"],
                "end": atual[-1]["start"] + atual[-1]["dur"] + 0.08,
                "palavras": atual,
            })
            atual = []
    if atual:
        grupos.append({
            "start": atual[0]["start"],
            "end": atual[-1]["start"] + atual[-1]["dur"] + 0.1,
            "palavras": atual,
        })
    for i in range(len(grupos) - 1):
        if grupos[i]["end"] > grupos[i + 1]["start"]:
            grupos[i]["end"] = grupos[i + 1]["start"]
    return grupos


def gerar_trilha_e_sfx(duracao_total, inicios_cenas):
    n = int(duracao_total * SAMPLE_RATE)
    t = np.linspace(0, duracao_total, n, endpoint=False, dtype=np.float32)
    acordes = [
        (146.83, 220.00, 261.63),
        (116.54, 174.61, 233.08),
        (174.61, 220.00, 261.63),
        (130.81, 196.00, 261.63),
    ]
    pad = np.zeros(n, dtype=np.float32)
    for i in range(int(duracao_total / 4.0) + 1):
        i0 = int(i * 4.0 * SAMPLE_RATE)
        i1 = min(n, int((i + 1) * 4.0 * SAMPLE_RATE))
        if i0 >= n:
            break
        tt = t[i0:i1] - i * 4.0
        env = np.sin(np.pi * np.clip(tt / 4.0, 0, 1)) ** 0.35
        freqs = acordes[i % len(acordes)]
        bloco = (
            0.38 * np.sin(2 * np.pi * (freqs[0] / 2) * tt)
            + 0.28 * np.sin(2 * np.pi * freqs[0] * tt)
            + 0.18 * np.sin(2 * np.pi * freqs[1] * tt)
            + 0.16 * np.sin(2 * np.pi * freqs[2] * tt)
        )
        pad[i0:i1] += bloco * env

    beat_phase = t % 1.0
    pulso = np.exp(-beat_phase * 10.0) * np.sin(2 * np.pi * 56.0 * beat_phase) * 0.30

    sfx = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(7)
    for inicio in inicios_cenas:
        idx0 = int(inicio * SAMPLE_RATE)
        idx1 = min(n, idx0 + int(0.42 * SAMPLE_RATE))
        if idx0 >= n:
            break
        lt = np.linspace(0, (idx1 - idx0) / SAMPLE_RATE, idx1 - idx0, dtype=np.float32)
        boom = np.exp(-lt * 9.5) * np.sin(2 * np.pi * (98.0 - 48.0 * lt) * lt)
        ruido = rng.normal(0, 0.14, size=len(lt)).astype(np.float32) * np.exp(-lt * 13.0)
        sfx[idx0:idx1] += boom * 0.45 + ruido

    return pad * 0.10 + pulso * 0.09 + sfx * 0.25


# ==========================================================
# DESENHO DO APRESENTADOR E CENÁRIOS DINÂMICOS
# ==========================================================
def criar_fundo_cena(cor_topo, cor_base, cor_glow):
    y = np.linspace(0, 1, ALTURA, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, LARGURA, dtype=np.float32)[None, :]
    bg = np.zeros((ALTURA, LARGURA, 3), dtype=np.float32)
    for c in range(3):
        bg[:, :, c] = cor_topo[c] * (1 - y) + cor_base[c] * y
    dist = np.sqrt(((x - 0.5) * 1.15) ** 2 + ((y - 0.25) * 1.7) ** 2)
    glow = np.clip(1.0 - dist * 1.35, 0.0, 1.0) ** 2.1
    for c in range(3):
        bg[:, :, c] += glow * cor_glow[c] * 0.40
    vinheta = np.clip(1.0 - (((x - 0.5) * 1.5) ** 2 + ((y - 0.5) * 1.3) ** 2) * 0.35, 0.38, 1.0)
    bg *= vinheta[:, :, None]
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), mode="RGB")


def desenhar_raios_luz(draw, cx, cy, t, cor):
    ang_base = t * 0.25
    for i in range(10):
        a = ang_base + i * (math.pi * 2 / 10)
        a1, a2 = a - 0.09, a + 0.09
        p1 = (cx + math.cos(a1) * 820, cy + math.sin(a1) * 820)
        p2 = (cx + math.cos(a2) * 820, cy + math.sin(a2) * 820)
        draw.polygon([(cx, cy), p1, p2], fill=(*cor, 16))


def desenhar_coroa(draw, cx, cy, s, tilt=0.0, cor=(255, 204, 41)):
    pts = [(-55 * s, 20 * s), (-64 * s, -24 * s), (-28 * s, -4 * s), (0, -38 * s),
           (28 * s, -4 * s), (64 * s, -24 * s), (55 * s, 20 * s)]
    ca, sa = math.cos(tilt), math.sin(tilt)
    rot = [(cx + px * ca - py * sa, cy + px * sa + py * ca) for px, py in pts]
    draw.polygon(rot, fill=cor, outline=(30, 20, 10), width=max(2, int(4 * s)))


def desenhar_apresentador(draw, cx, cy, s, t, boca, humor):
    """Apresentador do Tempo Diário: aparece do segundo 0 até o fim com expressões."""
    cy += math.sin(t * 4.2) * 5 * s

    # Jaqueta moderna + detalhe dourado
    draw.polygon(
        [
            (cx - 145 * s, cy + 220 * s),
            (cx - 110 * s, cy + 50 * s),
            (cx + 110 * s, cy + 50 * s),
            (cx + 145 * s, cy + 220 * s),
        ],
        fill=(29, 39, 71),
        outline=(11, 14, 26),
        width=max(2, int(6 * s)),
    )
    draw.polygon(
        [(cx - 36 * s, cy + 50 * s), (cx + 36 * s, cy + 50 * s), (cx, cy + 142 * s)],
        fill=(245, 183, 0),
    )

    # Mãos gesticulando ao falar
    gesto_y = math.sin(t * 9.0) * 14 * s * (0.4 + boca)
    mao_e_x = cx + (-65 * s if humor == "misterio" else -135 * s)
    mao_e_y = cy + (55 * s + gesto_y if humor == "choque" else 75 * s if humor == "misterio" else 135 * s + gesto_y)
    mao_d_x = cx + (150 * s if humor in ("empolgado", "convicto") else 135 * s)
    mao_d_y = cy + (40 * s + gesto_y if humor == "empolgado" else 55 * s - gesto_y if humor == "choque" else 130 * s - gesto_y)

    for mx, my in [(mao_e_x, mao_e_y), (mao_d_x, mao_d_y)]:
        r = 25 * s
        draw.ellipse((mx - r, my - r, mx + r, my + r), fill=(234, 182, 140), outline=(26, 18, 13), width=max(2, int(5 * s)))

    # Rosto
    draw.ellipse(
        (cx - 76 * s, cy - 117 * s, cx + 76 * s, cy + 47 * s),
        fill=(234, 182, 140),
        outline=(25, 18, 13),
        width=max(2, int(6 * s)),
    )
    # Cabelo / Topete
    draw.polygon(
        [
            (cx - 76 * s, cy - 52 * s),
            (cx - 56 * s, cy - 125 * s),
            (cx + 12 * s, cy - 134 * s),
            (cx + 76 * s, cy - 115 * s),
            (cx + 78 * s, cy - 52 * s),
            (cx + 25 * s, cy - 82 * s),
            (cx - 22 * s, cy - 72 * s),
        ],
        fill=(28, 23, 27),
        outline=(12, 10, 13),
        width=max(2, int(5 * s)),
    )
    # Barba curta estilizada
    draw.arc((cx - 54 * s, cy - 20 * s, cx + 54 * s, cy + 52 * s), start=15, end=165, fill=(36, 29, 34), width=max(3, int(9 * s)))

    # Olhos expressivos + piscar
    piscar = (t % 3.1) > 2.97
    eye_s = 1.26 if humor == "choque" else 0.84 if humor == "tenso" else 1.0
    for side in (-1, 1):
        ox = cx + side * 29 * s
        oy = cy - 42 * s
        if piscar:
            draw.line((ox - 13 * s, oy, ox + 13 * s, oy), fill=(25, 18, 13), width=max(2, int(5 * s)))
        else:
            rx, ry = 13 * s * eye_s, 15 * s * eye_s
            draw.ellipse((ox - rx, oy - ry, ox + rx, oy + ry), fill=(255, 255, 255), outline=(25, 18, 13), width=max(2, int(3 * s)))
            lx = 3 * s if humor == "misterio" else 0
            draw.ellipse((ox + lx - 6 * s, oy - 6 * s, ox + lx + 6 * s, oy + 6 * s), fill=(24, 20, 26))

        brow_y = oy - (26 if humor == "choque" else 20) * s
        tilt_b = (7 * s) if humor in ("tenso", "epico") else (-6 * s) if humor == "choque" else (-3 * s)
        draw.line((ox - 16 * s, brow_y + side * tilt_b, ox + 16 * s, brow_y - side * tilt_b), fill=(28, 23, 27), width=max(2, int(6 * s)))

    # Boca lip-sync
    bh = max(4 * s, (4 + 17 * boca) * s)
    bw = (14 if humor == "choque" else 20) * s
    draw.ellipse((cx - bw, cy + 12 * s - bh, cx + bw, cy + 12 * s + bh), fill=(84, 19, 26), outline=(25, 15, 15), width=max(2, int(3 * s)))


def desenhar_badge_pop(draw, cx, cy, num_txt, rotulo, cor, t_cena, delay=0.0):
    dt = t_cena - delay
    if dt < 0:
        return
    s = ease_out_back(min(1.0, dt / 0.35))
    bw, bh = 720 * s, 150 * s
    if bw < 30 or bh < 30:
        return
    draw.rounded_rectangle((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), radius=26, fill=(12, 16, 30, 235), outline=cor, width=5)
    if s > 0.6:
        texto_centralizado(draw, cx, cy - 22 * s, num_txt, carregar_fonte(60 * s), cor, 6, (0, 0, 0))
        texto_centralizado(draw, cx, cy + 38 * s, rotulo, carregar_fonte(28 * s), (235, 238, 245))


def desenhar_palco_superior(draw, cena, prog, t_cena, t_global):
    cid, dest = cena["id"], cena["destaque"]
    if cid == "gancho":
        p = 1.0 + 0.09 * math.sin(t_global * 6.0)
        texto_centralizado(draw, 540, 355, "?", carregar_fonte(310 * p), dest, 10, (0, 0, 0))
        desenhar_coroa(draw, 540, 215 + math.sin(t_global * 4.0) * 10, 1.15, -0.14)
        texto_centralizado(draw, 540, 500, "CÉU OU INFERNO?", carregar_fonte(42), (255, 255, 255), 6, (0, 0, 0))
    elif cid == "auge":
        hs = ease_out_cubic(min(1.0, prog * 1.5))
        by = 520
        ty = min(by - 80, by - 220 * hs)
        draw.rectangle((330, ty, 750, by - 40), fill=(242, 224, 185), outline=(40, 30, 18), width=4)
        for sd in (-1, 1):
            px = 540 + sd * 135
            draw.rectangle((px - 20, ty - 8, px + 20, by - 36), fill=(245, 183, 0), outline=(55, 35, 10), width=4)
        draw.rounded_rectangle((495, min(by - 60, by - 135 * hs), 585, by - 40), radius=14, fill=(170, 115, 25), outline=(40, 25, 10), width=4)
        for m in range(6):
            my = 180 + ((t_global * 160 + m * 70) % 340)
            mx = 230 + m * 125
            draw.ellipse((mx - 16, my - 16, mx + 16, my + 16), fill=(255, 209, 102), outline=(92, 61, 0), width=3)
    elif cid == "queda":
        for ax in (280, 800):
            draw.rounded_rectangle((ax - 55, 390, ax + 55, 510), radius=8, fill=(61, 30, 51), outline=(20, 10, 16), width=4)
            ch = 35 + 15 * math.sin(t_global * 12 + ax)
            draw.ellipse((ax - 24, 380 - ch, ax + 24, 392), fill=(255, 85, 45, 225))
        desenhar_coroa(draw, 540, 320, 1.35, math.sin(t_global * 3) * 0.25 + 0.25, (185, 140, 40))
        texto_centralizado(draw, 540, 470, "IDOLATRIA", carregar_fonte(52), (255, 89, 100), 8, (0, 0, 0))
    elif cid == "ira":
        gap = ease_out_cubic(min(1.0, prog * 1.4)) * 115
        shk = math.sin(t_global * 44) * 8 * max(0.0, 1.0 - prog * 1.5)
        draw.polygon([(540 - gap + shk, 210), (380 - gap + shk, 250), (350 - gap + shk, 500), (525 - gap + shk, 490)], fill=(122, 31, 130), outline=(255, 209, 102), width=4)
        draw.polygon([(540 + gap + shk, 210), (700 + gap + shk, 250), (730 + gap + shk, 500), (555 + gap + shk, 490)], fill=(122, 31, 130), outline=(255, 209, 102), width=4)
        draw.line([(540 + shk, 170), (518 + shk, 330), (562 + shk, 345), (535 + shk, 520)], fill=(255, 80, 60), width=10)
    elif cid == "silencio":
        sl = max(0.15, ease_out_back(min(1.0, t_cena / 0.45)))
        draw.rounded_rectangle((350, 190, 730, 510), radius=26, fill=(224, 205, 168), outline=(95, 70, 40), width=6)
        draw.line((350, 350, 730, 350), fill=(165, 38, 48), width=14)
        r = 44 * sl
        draw.ellipse((540 - r, 350 - r, 540 + r, 350 + r), fill=(185, 32, 45))
        texto_centralizado(draw, 540, 265, "1 REIS 11", carregar_fonte(44), (55, 38, 22))
        texto_centralizado(draw, 540, 445, "SEM PEDIDO DE PERDÃO", carregar_fonte(28), (110, 40, 35))
    elif cid == "eclesiastes":
        draw.rounded_rectangle((270, 190, 810, 510), radius=22, fill=(242, 226, 188), outline=(140, 100, 45), width=6)
        texto_centralizado(draw, 540, 250, "ECLESIASTES 12:13", carregar_fonte(36), (95, 55, 20))
        texto_centralizado(draw, 540, 325, '"Vaidade de vaidades..."', carregar_fonte(36), (50, 38, 28))
        if prog > 0.45:
            texto_centralizado(draw, 540, 425, "TEME A DEUS!", carregar_fonte(56), (180, 55, 25), 2, (255, 235, 200))
    elif cid == "alianca":
        tilt = math.sin(t_global * 2.4) * 0.14
        cx, cy = 540, 340
        draw.line((cx, cy - 120, cx, cy + 160), fill=(245, 183, 0), width=12)
        dx, dy = 210 * math.cos(tilt), 210 * math.sin(tilt)
        draw.line((cx - dx, cy - 80 - dy, cx + dx, cy - 80 + dy), fill=(255, 215, 90), width=10)
        for sd, lbl, col in [(-1, "CASTIGO", (255, 95, 75)), (1, "GRAÇA", (72, 229, 214))]:
            px, py = cx + sd * dx, cy - 80 + sd * dy
            draw.line((px, py, px, py + 110), fill=(220, 220, 220), width=4)
            draw.rounded_rectangle((px - 105, py + 110, px + 105, py + 178), radius=16, fill=(18, 26, 36), outline=col, width=4)
            texto_centralizado(draw, px, py + 144, lbl, carregar_fonte(32), col)
    elif cid == "final":
        draw.rounded_rectangle((100, 195, 515, 485), radius=24, fill=(16, 48, 52, 235), outline=(72, 229, 214), width=5)
        texto_centralizado(draw, 307, 260, "SALVO", carregar_fonte(52), (72, 229, 214))
        texto_centralizado(draw, 307, 340, "Eclesiastes 12", carregar_fonte(30), (240, 245, 250))
        texto_centralizado(draw, 307, 405, "Aliança 2 Sm 7", carregar_fonte(30), (240, 245, 250))
        draw.rounded_rectangle((565, 195, 980, 485), radius=24, fill=(52, 18, 28, 235), outline=(255, 89, 100), width=5)
        texto_centralizado(draw, 772, 260, "INCERTO", carregar_fonte(52), (255, 89, 100))
        texto_centralizado(draw, 772, 340, "Silêncio em Reis", carregar_fonte(30), (240, 245, 250))
        texto_centralizado(draw, 772, 405, "Alerta Neemias", carregar_fonte(30), (240, 245, 250))


def desenhar_hud_e_legendas(draw, cena, t_global, dur_total, grupo):
    pct = min(1.0, max(0.0, t_global / dur_total))
    draw.rectangle((0, 0, LARGURA, 14), fill=(255, 255, 255, 35))
    draw.rectangle((0, 0, int(LARGURA * pct), 14), fill=cena["destaque"])

    draw.rounded_rectangle((65, 55, 410, 115), radius=24, fill=(0, 0, 0, 165), outline=(255, 255, 255, 70), width=2)
    texto_centralizado(draw, 237, 85, CANAL_HANDLE, carregar_fonte(34), (255, 209, 102))

    draw.rounded_rectangle((435, 55, 1015, 115), radius=24, fill=(0, 0, 0, 165), outline=(*cena["destaque"], 140), width=2)
    texto_centralizado(draw, 725, 85, cena["titulo"], carregar_fonte(29), (240, 242, 248))

    if grupo:
        f_norm, f_at = carregar_fonte(64), carregar_fonte(74)
        espaco = 22
        itens = []
        for p in grupo["palavras"]:
            ativo = p["start"] <= t_global <= (p["start"] + p["dur"] + 0.05)
            f = f_at if ativo else f_norm
            up = p["text"].upper()
            w, _ = texto_largura(draw, up, f)
            itens.append((w, ativo, f, up))
        tot = sum(x[0] for x in itens) + espaco * (len(itens) - 1)
        linhas = [itens[:len(itens) // 2], itens[len(itens) // 2:]] if (tot > 940 and len(itens) > 1) else [itens]
        y_base = 1480 if len(linhas) == 1 else 1430
        for li, linha in enumerate(linhas):
            lw = sum(x[0] for x in linha) + espaco * (len(linha) - 1)
            cx = (LARGURA - lw) / 2
            cy = y_base + li * 92
            for w, ativo, f, txt in linha:
                by = -6 if ativo else 0
                cor = cena["destaque"] if ativo else (255, 255, 255)
                draw.text((cx, cy + by), txt, font=f, fill=cor, stroke_width=10, stroke_fill=(0, 0, 0))
                cx += w + espaco


# ==========================================================
# PIPELINE PRINCIPAL
# ==========================================================
async def preparar_tudo(ffmpeg_exe):
    print("[1/4] Gerando 2 vozes neurais expressivas (FabioNeural + DonatoNeural)...")
    cenas_info, beats_timeline, audios_pcm, palavras_globais, inicios_cenas = [], [], [], [], []
    cursor = 0.0
    pausa_beat = np.zeros(int(PAUSA_ENTRE_BEATS * SAMPLE_RATE), dtype=np.float32)
    pausa_cena = np.zeros(int(PAUSA_ENTRE_CENAS * SAMPLE_RATE), dtype=np.float32)

    for idx, cena in enumerate(CENAS):
        inicio_cena = cursor
        inicios_cenas.append(inicio_cena)
        for b_idx, beat in enumerate(cena["beats"]):
            mp3_tmp = f"temp_c{idx}_b{b_idx}.mp3"
            word_ev, sent_ev = await sintetizar_beat(beat, mp3_tmp)
            pcm = decodificar_mp3_pcm(ffmpeg_exe, mp3_tmp)
            dur = len(pcm) / SAMPLE_RATE
            os.remove(mp3_tmp)

            if not word_ev:
                word_ev = construir_palavras_fallback(beat["texto"], dur, sent_ev)
            for w in word_ev:
                palavras_globais.append({"text": w["text"], "start": cursor + w["start"], "dur": w["dur"]})

            audios_pcm.append(pcm)
            audios_pcm.append(pausa_beat)
            beats_timeline.append({"start": cursor, "end": cursor + dur + PAUSA_ENTRE_BEATS, "humor": beat["humor"]})
            cursor += dur + PAUSA_ENTRE_BEATS

        audios_pcm.append(pausa_cena)
        cursor += PAUSA_ENTRE_CENAS
        cenas_info.append({
            **cena,
            "start": inicio_cena,
            "end": cursor,
            "fundo": criar_fundo_cena(cena["cor_topo"], cena["cor_base"], cena["cor_glow"]),
        })
        print(f"   - Cena {idx + 1}/{len(CENAS)} ({cena['id']}) ok!")

    dur_total = cursor + 0.35
    voz_full = np.concatenate(audios_pcm)
    pad_fim = np.zeros(max(0, int(dur_total * SAMPLE_RATE) - len(voz_full)), dtype=np.float32)
    voz_full = np.concatenate([voz_full, pad_fim])

    print("[2/4] Mixando trilha sonora + impactos...")
    bgm = gerar_trilha_e_sfx(dur_total, inicios_cenas)
    mix = np.tanh((voz_full * 0.95 + bgm) * 1.05)
    pcm16 = (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16)

    with wave.open("temp_audio.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm16.tobytes())

    return cenas_info, beats_timeline, dur_total, voz_full, agrupar_legendas(palavras_globais)


def renderizar_video(ffmpeg_exe, cenas_info, beats_timeline, dur_total, voz_full, grupos_legenda):
    total_frames = int(dur_total * FPS)
    print(f"[3/4] Renderizando {total_frames} frames ({dur_total:.1f}s @ {FPS}fps)...")
    cmd = [
        ffmpeg_exe, "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{LARGURA}x{ALTURA}", "-r", str(FPS), "-i", "pipe:0", "-i", "temp_audio.wav",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", ARQUIVO_SAIDA,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    idx_c, idx_b, idx_l = 0, 0, 0
    spf = SAMPLE_RATE // FPS

    try:
        for f in range(total_frames):
            t = f / FPS
            while idx_c < len(cenas_info) - 1 and t >= cenas_info[idx_c]["end"]:
                idx_c += 1
            while idx_b < len(beats_timeline) - 1 and t >= beats_timeline[idx_b]["end"]:
                idx_b += 1
            while idx_l < len(grupos_legenda) and t > grupos_legenda[idx_l]["end"]:
                idx_l += 1

            cena = cenas_info[idx_c]
            humor = beats_timeline[idx_b]["humor"]
            t_cena = max(0.0, t - cena["start"])
            dur_cena = max(0.01, cena["end"] - cena["start"])
            prog = min(1.0, t_cena / dur_cena)

            s0 = f * spf
            s1 = min(len(voz_full), s0 + spf)
            rms = float(np.sqrt(np.mean(voz_full[s0:s1] ** 2))) if s1 > s0 else 0.0
            boca = min(1.0, rms * 6.8)

            grupo_atual = None
            if idx_l < len(grupos_legenda):
                g = grupos_legenda[idx_l]
                if g["start"] <= t <= g["end"]:
                    grupo_atual = g

            overlay = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            desenhar_raios_luz(draw, 540, 400, t, cena["destaque"])
            for i in range(24):
                sx = (i * 197 + 53) % LARGURA
                py = ALTURA - ((t * (55 + (i % 5) * 24) + i * 113) % ALTURA)
                px = sx + math.sin(t * 1.8 + i) * 26
                r = 3 + (i % 4) * 2
                draw.ellipse((px - r, py - r, px + r, py + r), fill=(*cena["destaque"], 115))

            desenhar_palco_superior(draw, cena, prog, t_cena, t)

            zoom_p = 1.0 + 0.06 * math.exp(-t_cena * 9.0)
            desenhar_apresentador(draw, 540, 850, 1.48 * zoom_p, t, boca, humor)

            cid, dest = cena["id"], cena["destaque"]
            if cid == "gancho":
                desenhar_badge_pop(draw, 540, 1210, "FINAL SECRETO", "1 REIS 3 • 1 REIS 11", dest, t_cena, 1.2)
            elif cid == "auge":
                if prog < 0.55:
                    val = int(666 * ease_out_cubic(min(1.0, prog / 0.38)))
                    desenhar_badge_pop(draw, 540, 1210, f"{val} TALENTOS", "DE OURO POR ANO", dest, t_cena, 0.2)
                else:
                    val = int(3000 * ease_out_cubic(min(1.0, (prog - 0.55) / 0.22)))
                    desenhar_badge_pop(draw, 540, 1210, f"{val:,}".replace(",", "."), "PROVÉRBIOS ESCRITOS", dest, t_cena - dur_cena * 0.55, 0.0)
            elif cid == "queda":
                mul = int(1000 * ease_out_cubic(min(1.0, prog / 0.42)))
                desenhar_badge_pop(draw, 540, 1210, f"{mul:,}".replace(",", "."), "700 ESPOSAS + 300 CONCUBINAS", dest, t_cena, 0.15)
            elif cid == "ira":
                tri = int(10 * ease_out_cubic(min(1.0, prog / 0.5)))
                desenhar_badge_pop(draw, 540, 1210, f"{tri} DE 12 TRIBOS", "ARRANCADAS DA FAMÍLIA", dest, t_cena, 0.2)
            elif cid == "silencio":
                desenhar_badge_pop(draw, 540, 1210, "NEEMIAS 13:26", "LEMBRADO COMO ALERTA", dest, t_cena, 1.6)
            elif cid == "eclesiastes":
                desenhar_badge_pop(draw, 540, 1210, "ECLESIASTES 12:13", "ARREPENDIMENTO NO FIM?", dest, t_cena, 0.4)
            elif cid == "alianca":
                desenhar_badge_pop(draw, 540, 1210, "2 SAMUEL 7:15", "MISERICÓRDIA PROMETIDA", dest, t_cena, 0.2)
            elif cid == "final":
                desenhar_badge_pop(draw, 540, 1210, f"{CANAL_NOME} • COMENTA!", "SALVO? DIGITE SIM OU NÃO", dest, t_cena, 0.0)

            desenhar_hud_e_legendas(draw, cena, t, dur_total, grupo_atual)

            frame_rgba = Image.alpha_composite(cena["fundo"].convert("RGBA"), overlay)
            proc.stdin.write(frame_rgba.convert("RGB").tobytes())

            if (f + 1) % 150 == 0 or f + 1 == total_frames:
                print(f"   - Progresso: {f + 1}/{total_frames} frames ({(f + 1) * 100 // total_frames}%)")
    finally:
        if proc.stdin:
            proc.stdin.close()
        proc.wait()

    if os.path.exists("temp_audio.wav"):
        os.remove("temp_audio.wav")
    if proc.returncode != 0:
        raise RuntimeError("Erro ao codificar vídeo com FFmpeg.")
    print(f"[4/4] Vídeo pronto em: {os.path.abspath(ARQUIVO_SAIDA)}")


def main():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cenas_info, beats_tl, dur_total, voz_full, grupos_leg = asyncio.run(preparar_tudo(ffmpeg_exe))
    renderizar_video(ffmpeg_exe, cenas_info, beats_tl, dur_total, voz_full, grupos_leg)


if __name__ == "__main__":
    main()
