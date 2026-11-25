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
# CONFIGURAÇÕES DO CANAL E DO VÍDEO
# ==========================================================
CANAL_NOME = "TEMPO DIÁRIO"
CANAL_HANDLE = "@tempodiario"
ARQUIVO_SAIDA = "salomao_tempodiario.mp4"

LARGURA, ALTURA = 1080, 1920
FPS = 30
SAMPLE_RATE = 44100
PAUSA_ENTRE_CENAS = 0.16

VOZ_TTS = "pt-BR-AntonioNeural"  # Voz masculina grave em PT-BR
VELOCIDADE_VOZ = "+15%"          # Ritmo dinâmico estilo TikTok/Reels

# ==========================================================
# ROTEIRO ESTRUTURADO POR CENAS
# ==========================================================
CENAS = [
    {
        "id": "gancho",
        "titulo": "O MISTÉRIO DE SALOMÃO",
        "cor_topo": (14, 16, 36),
        "cor_base": (6, 8, 18),
        "cor_glow": (245, 183, 0),
        "destaque": (255, 209, 102),
        "texto": (
            "O homem mais sábio que já pisou na Terra... "
            "terminou no inferno? A história de Salomão tem um final "
            "que quase ninguém percebeu."
        ),
    },
    {
        "id": "auge",
        "titulo": "GIBEOM • O AUGE",
        "cor_topo": (18, 28, 56),
        "cor_base": (8, 12, 24),
        "cor_glow": (255, 195, 30),
        "destaque": (255, 209, 102),
        "texto": (
            "Tudo começou em Gibeom. Em vez de dinheiro ou poder, "
            "Salomão pediu sabedoria. Deus gostou tanto que deu tudo a ele: "
            "seiscentos e sessenta e seis talentos de ouro por ano, "
            "três mil provérbios e o templo mais glorioso do mundo."
        ),
    },
    {
        "id": "queda",
        "titulo": "1 REIS 11 • A QUEDA",
        "cor_topo": (44, 12, 28),
        "cor_base": (14, 6, 14),
        "cor_glow": (220, 38, 68),
        "destaque": (255, 89, 100),
        "texto": (
            "Mas a glória virou armadilha. A Bíblia diz que ele teve "
            "setecentas esposas e trezentas concubinas. Mil mulheres! "
            "E na velhice, elas desviaram o coração dele para deuses falsos, "
            "com direito a altares proibidos em Jerusalém."
        ),
    },
    {
        "id": "ira",
        "titulo": "O REINO RASGADO",
        "cor_topo": (52, 16, 16),
        "cor_base": (14, 6, 8),
        "cor_glow": (255, 70, 50),
        "destaque": (255, 95, 75),
        "texto": (
            "A resposta de Deus foi dura. Em Primeiro Reis capítulo onze, "
            "o Senhor se irou porque havia aparecido a Salomão duas vezes, "
            "e avisou: o reino seria rasgado, tirando dez tribos da mão de sua família."
        ),
    },
    {
        "id": "silencio",
        "titulo": "O SILÊNCIO EM REIS",
        "cor_topo": (20, 22, 34),
        "cor_base": (8, 9, 15),
        "cor_glow": (120, 140, 200),
        "destaque": (150, 185, 255),
        "texto": (
            "E aqui mora o susto. O livro de Reis conta a morte de Salomão "
            "sem registrar nenhum pedido de perdão. E séculos depois, "
            "Neemias ainda usa Salomão como alerta de quem pecou gravemente."
        ),
    },
    {
        "id": "eclesiastes",
        "titulo": "PISTA 1 • ECLESIASTES",
        "cor_topo": (38, 26, 14),
        "cor_base": (14, 10, 6),
        "cor_glow": (255, 175, 65),
        "destaque": (255, 209, 102),
        "texto": (
            "Então ele se perdeu para sempre? Espera! Olha para o livro de Eclesiastes. "
            "Escrito por um rei cansado no fim da vida, ele chama todo aquele luxo "
            "de vaidade e fecha com uma frase: Teme a Deus e guarda os seus mandamentos."
        ),
    },
    {
        "id": "alianca",
        "titulo": "PISTA 2 • 2 SAMUEL 7",
        "cor_topo": (12, 36, 44),
        "cor_base": (6, 14, 20),
        "cor_glow": (46, 196, 182),
        "destaque": (72, 229, 214),
        "texto": (
            "E tem uma segunda pista pesada em Segundo Samuel sete. "
            "Deus prometeu a Davi sobre o filho dele: se ele pecar, eu o castigarei, "
            "mas a minha misericórdia não se apartará dele, como apartei de Saul."
        ),
    },
    {
        "id": "final",
        "titulo": "VEREDITO FINAL",
        "cor_topo": (16, 18, 40),
        "cor_base": (6, 8, 18),
        "cor_glow": (245, 183, 0),
        "destaque": (255, 209, 102),
        "texto": (
            "A Bíblia não crava uma frase final, mas deixa o rastro "
            "do arrependimento e da aliança. E aí, para você: "
            "Salomão foi salvo ou não? Comenta sim ou não e segue o Tempo Diário."
        ),
    },
]

# ==========================================================
# FONTES E UTILITÁRIOS DE TEXTO
# ==========================================================
_FONT_CACHE = {}


def carregar_fonte(tamanho):
    if tamanho in _FONT_CACHE:
        return _FONT_CACHE[tamanho]
    caminhos = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\impact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
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
        (x - w / 2, y - h / 2),
        txt,
        font=fonte,
        fill=cor,
        stroke_width=stroke_w,
        stroke_fill=stroke_c,
    )


def ease_out_cubic(x):
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3


# ==========================================================
# SÍNTESE DE VOZ + TIMESTAMPS POR PALAVRA (EDGE-TTS)
# ==========================================================
async def sintetizar_cena(idx, texto, mp3_path):
    try:
        comm = edge_tts.Communicate(
            texto, VOZ_TTS, rate=VELOCIDADE_VOZ, boundary="WordBoundary"
        )
    except TypeError:
        comm = edge_tts.Communicate(texto, VOZ_TTS, rate=VELOCIDADE_VOZ)

    word_events = []
    sent_events = []

    with open(mp3_path, "wb") as f:
        async for chunk in comm.stream():
            ctype = chunk.get("type")
            if ctype == "audio":
                f.write(chunk["data"])
            elif ctype == "WordBoundary":
                word_events.append(
                    {
                        "text": chunk["text"].strip(),
                        "start": chunk["offset"] / 10_000_000.0,
                        "dur": max(0.08, chunk["duration"] / 10_000_000.0),
                    }
                )
            elif ctype == "SentenceBoundary":
                sent_events.append(
                    {
                        "text": chunk["text"].strip(),
                        "start": chunk["offset"] / 10_000_000.0,
                        "dur": max(0.2, chunk["duration"] / 10_000_000.0),
                    }
                )

    return word_events, sent_events


def decodificar_mp3_pcm(ffmpeg_exe, mp3_path):
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        mp3_path,
        "-f",
        "s16le",
        "-ac",
        "1",
        "-ar",
        str(SAMPLE_RATE),
        "pipe:1",
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    audio = np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    return audio


def construir_palavras_fallback(texto, duracao_total, sent_events):
    palavras_out = []
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
                palavras_out.append({"text": t, "start": cur, "dur": d})
                cur += d
    else:
        tokens = texto.split()
        pesos = [max(2, len(re.sub(r"\W+", "", t))) for t in tokens]
        soma = max(1, sum(pesos))
        cur = 0.05
        util = max(0.5, duracao_total - 0.1)
        for t, p in zip(tokens, pesos):
            d = util * (p / soma)
            palavras_out.append({"text": t, "start": cur, "dur": d})
            cur += d
    return palavras_out


def agrupar_legendas(palavras_globais):
    """Agrupa palavras em blocos curtos (até 3 palavras ou fim de frase) estilo TikTok."""
    grupos = []
    atual = []
    for p in palavras_globais:
        atual.append(p)
        termina_frase = p["text"].endswith((".", "!", "?", ":", ";"))
        if len(atual) >= 3 or termina_frase:
            grupos.append(
                {
                    "start": atual[0]["start"],
                    "end": atual[-1]["start"] + atual[-1]["dur"] + 0.12,
                    "palavras": atual,
                }
            )
            atual = []
    if atual:
        grupos.append(
            {
                "start": atual[0]["start"],
                "end": atual[-1]["start"] + atual[-1]["dur"] + 0.15,
                "palavras": atual,
            }
        )
    # Evita sobreposição entre grupos
    for i in range(len(grupos) - 1):
        if grupos[i]["end"] > grupos[i + 1]["start"]:
            grupos[i]["end"] = grupos[i + 1]["start"]
    return grupos


# ==========================================================
# TRILHA SONORA E EFEITOS SONOROS PROCEDURAIS (NUMPY)
# ==========================================================
def gerar_trilha_e_sfx(duracao_total, inicios_cenas):
    n = int(duracao_total * SAMPLE_RATE)
    t = np.linspace(0, duracao_total, n, endpoint=False, dtype=np.float32)

    # Progressão cinematográfica em Ré menor (Dm - Bb - F - C)
    acordes = [
        (146.83, 220.00, 261.63),  # Dm7
        (116.54, 174.61, 233.08),  # Bb
        (174.61, 220.00, 261.63),  # F
        (130.81, 196.00, 261.63),  # C
    ]
    pad = np.zeros(n, dtype=np.float32)
    dur_acorde = 4.0
    for i in range(int(duracao_total / dur_acorde) + 1):
        i0 = int(i * dur_acorde * SAMPLE_RATE)
        i1 = min(n, int((i + 1) * dur_acorde * SAMPLE_RATE))
        if i0 >= n:
            break
        tt = t[i0:i1] - i * dur_acorde
        env = np.sin(np.pi * np.clip(tt / dur_acorde, 0, 1)) ** 0.35
        freqs = acordes[i % len(acordes)]
        bloco = (
            0.40 * np.sin(2 * np.pi * (freqs[0] / 2) * tt)
            + 0.28 * np.sin(2 * np.pi * freqs[0] * tt)
            + 0.18 * np.sin(2 * np.pi * freqs[1] * tt)
            + 0.14 * np.sin(2 * np.pi * freqs[2] * tt)
        )
        pad[i0:i1] += bloco * env

    # Pulso grave sutil (batida cardíaca a cada 1s)
    beat_phase = t % 1.0
    pulso = np.exp(-beat_phase * 10.0) * np.sin(2 * np.pi * 55.0 * beat_phase) * 0.32

    # Impacto / whoosh nas trocas de cena
    sfx = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(42)
    for inicio in inicios_cenas:
        idx0 = int(inicio * SAMPLE_RATE)
        dur_sfx = int(0.45 * SAMPLE_RATE)
        idx1 = min(n, idx0 + dur_sfx)
        if idx0 >= n:
            break
        lt = np.linspace(0, (idx1 - idx0) / SAMPLE_RATE, idx1 - idx0, dtype=np.float32)
        boom = np.exp(-lt * 9.0) * np.sin(2 * np.pi * (95.0 - 45.0 * lt) * lt)
        ruido = rng.normal(0, 0.12, size=len(lt)).astype(np.float32) * np.exp(-lt * 14.0)
        sfx[idx0:idx1] += (boom * 0.45 + ruido)

    return pad * 0.11 + pulso * 0.10 + sfx * 0.25


# ==========================================================
# RENDERIZADOR DE FUNDOS E ELEMENTOS 2D ESTILIZADOS
# ==========================================================
def criar_fundo_cena(cor_topo, cor_base, cor_glow):
    y = np.linspace(0, 1, ALTURA, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, LARGURA, dtype=np.float32)[None, :]

    bg = np.zeros((ALTURA, LARGURA, 3), dtype=np.float32)
    for c in range(3):
        bg[:, :, c] = cor_topo[c] * (1 - y) + cor_base[c] * y

    # Glow radial centralizado na área da ilustração
    dist = np.sqrt(((x - 0.5) * 1.15) ** 2 + ((y - 0.42) * 1.65) ** 2)
    glow = np.clip(1.0 - dist * 1.35, 0.0, 1.0) ** 2.2
    for c in range(3):
        bg[:, :, c] += glow * cor_glow[c] * 0.42

    # Vinheta escura nas bordas
    vinheta = np.clip(1.0 - (((x - 0.5) * 1.55) ** 2 + ((y - 0.5) * 1.35) ** 2) * 0.35, 0.35, 1.0)
    bg *= vinheta[:, :, None]

    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), mode="RGB")


def desenhar_particulas(draw, t, cor, qtd=22):
    for i in range(qtd):
        seed_x = (i * 197 + 53) % LARGURA
        vel = 45 + (i % 5) * 22
        y = ALTURA - ((t * vel + i * 113) % ALTURA)
        x = seed_x + math.sin(t * 1.6 + i) * 22
        r = 3 + (i % 4) * 2
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*cor, 110))


def desenhar_coroa(draw, cx, cy, s, inclinacao=0.0, cor=(255, 204, 41)):
    pts = [
        (-75 * s, 28 * s),
        (-88 * s, -34 * s),
        (-40 * s, -4 * s),
        (0, -52 * s),
        (40 * s, -4 * s),
        (88 * s, -34 * s),
        (75 * s, 28 * s),
    ]
    ca, sa = math.cos(inclinacao), math.sin(inclinacao)
    rot = [(cx + px * ca - py * sa, cy + px * sa + py * ca) for px, py in pts]
    draw.polygon(rot, fill=cor, outline=(30, 20, 10), width=max(2, int(5 * s)))
    # Joias na coroa
    for jx, jy, jc in [(0, -12 * s, (230, 57, 70)), (-42 * s, 8 * s, (46, 196, 182)), (42 * s, 8 * s, (46, 196, 182))]:
        rx = cx + jx * ca - jy * sa
        ry = cy + jx * sa + jy * ca
        r = 8 * s
        draw.ellipse((rx - r, ry - r, rx + r, ry + r), fill=jc)


def desenhar_salomao(draw, cx, cy, s, t, boca_aberta, modo="rei"):
    """Desenha personagem 2D estilizado de Salomão com respiração, piscar e lip-sync."""
    respiracao = math.sin(t * 2.8) * 6 * s
    cy += respiracao

    # Cores por fase da vida
    if modo == "velho":
        cor_manto = (92, 86, 98)
        cor_barba = (225, 228, 235)
        cor_pele = (228, 186, 152)
    elif modo == "pecado":
        cor_manto = (128, 26, 48)
        cor_barba = (42, 34, 38)
        cor_pele = (232, 184, 146)
    else:
        cor_manto = (102, 38, 130)
        cor_barba = (38, 28, 24)
        cor_pele = (238, 190, 150)

    # Sombra no chão
    draw.ellipse((cx - 150 * s, cy + 255 * s, cx + 150 * s, cy + 295 * s), fill=(0, 0, 0, 110))

    # Manto / Corpo
    draw.polygon(
        [
            (cx - 135 * s, cy + 265 * s),
            (cx - 95 * s, cy + 45 * s),
            (cx + 95 * s, cy + 45 * s),
            (cx + 135 * s, cy + 265 * s),
        ],
        fill=cor_manto,
        outline=(18, 14, 22),
        width=max(2, int(6 * s)),
    )
    # Faixa dourada real
    if modo != "velho":
        draw.polygon(
            [
                (cx - 26 * s, cy + 48 * s),
                (cx + 26 * s, cy + 48 * s),
                (cx + 40 * s, cy + 265 * s),
                (cx - 40 * s, cy + 265 * s),
            ],
            fill=(245, 183, 0),
        )

    # Cabeça
    draw.ellipse(
        (cx - 82 * s, cy - 115 * s, cx + 82 * s, cy + 55 * s),
        fill=cor_pele,
        outline=(25, 18, 15),
        width=max(2, int(6 * s)),
    )

    # Barba
    if modo != "jovem":
        draw.chord(
            (cx - 80 * s, cy - 30 * s, cx + 80 * s, cy + 95 * s),
            start=0,
            end=180,
            fill=cor_barba,
            outline=(20, 16, 18),
            width=max(2, int(4 * s)),
        )

    # Olhos (piscam a cada 3.4s)
    piscar = (t % 3.4) > 3.26
    for side in (-1, 1):
        ox = cx + side * 30 * s
        oy = cy - 38 * s
        if piscar:
            draw.line((ox - 12 * s, oy, ox + 12 * s, oy), fill=(25, 18, 15), width=max(2, int(5 * s)))
        else:
            draw.ellipse((ox - 11 * s, oy - 13 * s, ox + 11 * s, oy + 13 * s), fill=(255, 255, 255))
            draw.ellipse((ox - 5 * s, oy - 6 * s, ox + 5 * s, oy + 6 * s), fill=(24, 20, 26))
        # Sobrancelha expressiva
        inclin = 6 * s if modo in ("pecado", "velho") else -4 * s
        draw.line(
            (ox - 16 * s, oy - 22 * s + side * inclin, ox + 16 * s, oy - 22 * s - side * inclin),
            fill=cor_barba if modo != "jovem" else (40, 28, 22),
            width=max(2, int(6 * s)),
        )

    # Boca animada pelo volume real da narração
    boca_h = (4 + 16 * boca_aberta) * s
    boca_y = cy + 12 * s
    draw.ellipse(
        (cx - 18 * s, boca_y - boca_h / 2, cx + 18 * s, boca_y + boca_h / 2),
        fill=(65, 18, 22),
        outline=(25, 15, 15),
        width=max(2, int(3 * s)),
    )

    # Coroa (cai/entorta na queda, ausente na humildade de Eclesiastes)
    if modo == "jovem" or modo == "rei":
        desenhar_coroa(draw, cx, cy - 118 * s, s * 0.95, inclinacao=0.0)
    elif modo == "pecado":
        desenhar_coroa(draw, cx + 14 * s, cy - 112 * s, s * 0.92, inclinacao=0.24, cor=(185, 140, 40))


def desenhar_templo(draw, cx, cy, progresso):
    p = ease_out_cubic(progresso)
    h_scale = p
    base_y = cy + 210
    # Degraus
    for k in range(3):
        w = 340 - k * 34
        y0 = base_y - k * 24 * h_scale
        draw.rectangle((cx - w, y0 - 22, cx + w, y0), fill=(215, 185, 130), outline=(40, 30, 18), width=4)
    # Fachada
    top_y = base_y - 260 * h_scale
    draw.rectangle((cx - 240, top_y, cx + 240, base_y - 68), fill=(242, 224, 185), outline=(40, 30, 18), width=5)
    # Colunas douradas (Jaquim e Boaz)
    for side in (-1, 1):
        px = cx + side * 155
        draw.rectangle((px - 24, top_y - 10, px + 24, base_y - 68), fill=(245, 183, 0), outline=(55, 35, 10), width=4)
    # Porta do Santo Lugar
    draw.rounded_rectangle((cx - 58, base_y - 200 * h_scale, cx + 58, base_y - 68), radius=20, fill=(170, 115, 25), outline=(40, 25, 10), width=4)


def desenhar_badge_contador(draw, cx, cy, numero_txt, rotulo, cor_num, scale=1.0):
    w, h = int(680 * scale), int(155 * scale)
    draw.rounded_rectangle(
        (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2),
        radius=26,
        fill=(18, 22, 38, 225),
        outline=cor_num,
        width=5,
    )
    texto_centralizado(draw, cx, cy - 22 * scale, numero_txt, carregar_fonte(int(68 * scale)), cor_num, 4, (0, 0, 0))
    texto_centralizado(draw, cx, cy + 40 * scale, rotulo, carregar_fonte(int(30 * scale)), (235, 238, 245))


def desenhar_cena_especifica(draw, cena, prog, t_global, boca):
    cid = cena["id"]
    dest = cena["destaque"]

    if cid == "gancho":
        # Interrogação gigante pulsante atrás de Salomão
        pulse = 1.0 + 0.06 * math.sin(t_global * 5.0)
        texto_centralizado(draw, 540, 560, "?", carregar_fonte(int(520 * pulse)), (*dest, 75))
        desenhar_salomao(draw, 540, 740, 1.35, t_global, boca, modo="jovem")
        if prog > 0.25:
            desenhar_badge_contador(draw, 540, 1165, "SÁBIO... OU PERDIDO?", "1 REIS 3 • 1 REIS 11", dest, 0.92)

    elif cid == "auge":
        # Templo surgindo ao fundo + Salomão rei + contadores animados
        desenhar_templo(draw, 540, 540, min(1.0, prog * 1.4))
        desenhar_salomao(draw, 540, 820, 1.05, t_global, boca, modo="rei")
        if prog < 0.62:
            val = int(666 * ease_out_cubic(min(1.0, prog / 0.45)))
            desenhar_badge_contador(draw, 540, 1165, f"{val} TALENTOS", "DE OURO POR ANO", dest)
        else:
            val = int(3000 * ease_out_cubic(min(1.0, (prog - 0.62) / 0.25)))
            desenhar_badge_contador(draw, 540, 1165, f"{val:,}".replace(",", "."), "PROVÉRBIOS ESCRITOS", dest)

    elif cid == "queda":
        # Altares sombrios + Salomão desviado + contador até 1.000 mulheres
        for ax in (230, 850):
            draw.polygon([(ax - 70, 870), (ax + 70, 870), (ax + 45, 760), (ax - 45, 760)], fill=(58, 32, 48), outline=(20, 10, 16), width=4)
            chama = 32 + 12 * math.sin(t_global * 11 + ax)
            draw.ellipse((ax - 22, 740 - chama, ax + 22, 765), fill=(255, 95, 45, 200))
        desenhar_salomao(draw, 540, 770, 1.22, t_global, boca, modo="pecado")
        mulheres = int(1000 * ease_out_cubic(min(1.0, prog / 0.55)))
        desenhar_badge_contador(draw, 540, 1165, f"{mulheres:,}".replace(",", "."), "700 ESPOSAS + 300 CONCUBINAS", (255, 89, 100))

    elif cid == "ira":
        # Shake dramático + Manto rasgado em 2 partes + 10 tribos tiradas
        shake = math.sin(t_global * 42) * 10 * max(0.0, 1.0 - prog * 1.5)
        gap = ease_out_cubic(min(1.0, prog * 1.3)) * 135
        # Metade esquerda e direita do manto rasgado
        draw.polygon([(540 - gap + shake, 470), (360 - gap + shake, 520), (320 - gap + shake, 860), (520 - gap + shake, 850)], fill=(128, 32, 130), outline=(255, 209, 102), width=5)
        draw.polygon([(540 + gap + shake, 470), (720 + gap + shake, 520), (760 + gap + shake, 860), (560 + gap + shake, 850)], fill=(128, 32, 130), outline=(255, 209, 102), width=5)
        # Raio no centro
        draw.line([(540 + shake, 390), (515 + shake, 600), (565 + shake, 620), (535 + shake, 900)], fill=(255, 80, 60), width=12)
        tribos = int(10 * ease_out_cubic(min(1.0, prog / 0.65)))
        desenhar_badge_contador(draw, 540, 1165, f"{tribos} DE 12 TRIBOS", "ARRANCADAS DA LINHAGEM", (255, 95, 75))

    elif cid == "silencio":
        # Pergaminho fechado + selo vermelho + referência Neemias 13:26
        draw.rounded_rectangle((310, 470, 770, 930), radius=34, fill=(224, 205, 168), outline=(95, 70, 40), width=8)
        draw.line((310, 680, 770, 680), fill=(165, 38, 48), width=18)
        draw.ellipse((480, 620, 600, 740), fill=(185, 32, 45), outline=(90, 15, 20), width=6)
        texto_centralizado(draw, 540, 565, "1 REIS 11", carregar_fonte(52), (55, 38, 22))
        texto_centralizado(draw, 540, 815, "SEM ARREPENDIMENTO", carregar_fonte(34), (110, 40, 35))
        if prog > 0.48:
            desenhar_badge_contador(draw, 540, 1165, "NEEMIAS 13:26", "LEMBRADO COMO ALERTA", dest)

    elif cid == "eclesiastes":
        # Salomão velho escrevendo Eclesiastes + pergaminho iluminado
        desenhar_salomao(draw, 350, 760, 1.05, t_global, boca, modo="velho")
        # Pergaminho aberto à direita
        draw.rounded_rectangle((530, 480, 960, 960), radius=24, fill=(242, 226, 188), outline=(140, 100, 45), width=6)
        texto_centralizado(draw, 745, 560, "ECLESIASTES", carregar_fonte(40), (95, 55, 20))
        texto_centralizado(draw, 745, 650, '"Vaidade de', carregar_fonte(36), (50, 38, 28))
        texto_centralizado(draw, 745, 700, 'vaidades..."', carregar_fonte(36), (50, 38, 28))
        if prog > 0.55:
            texto_centralizado(draw, 745, 815, "TEME A DEUS", carregar_fonte(44), (180, 55, 25))
            texto_centralizado(draw, 745, 870, "Ecl. 12:13", carregar_fonte(32), (80, 60, 40))
        desenhar_badge_contador(draw, 540, 1165, "ARREPENDIMENTO?", "CONVERSÃO NA VELHICE", dest)

    elif cid == "alianca":
        # Balança Justiça vs Misericórdia (2 Samuel 7:14-15)
        tilt = math.sin(t_global * 2.2) * 0.14
        cx, cy = 540, 640
        draw.line((cx, cy - 160, cx, cy + 220), fill=(245, 183, 0), width=14)
        draw.rounded_rectangle((cx - 130, cy + 200, cx + 130, cy + 235), radius=10, fill=(245, 183, 0))
        dx, dy = 240 * math.cos(tilt), 240 * math.sin(tilt)
        draw.line((cx - dx, cy - 110 - dy, cx + dx, cy - 110 + dy), fill=(255, 215, 90), width=12)
        for lado, lbl, col in [(-1, "CASTIGO", (255, 95, 75)), (1, "GRAÇA", (72, 229, 214))]:
            px = cx + lado * dx
            py = cy - 110 + lado * dy
            draw.line((px, py, px, py + 150), fill=(220, 220, 220), width=5)
            draw.rounded_rectangle((px - 110, py + 150, px + 110, py + 230), radius=18, fill=(18, 26, 36), outline=col, width=5)
            texto_centralizado(draw, px, py + 190, lbl, carregar_fonte(34), col)
        desenhar_badge_contador(draw, 540, 1165, "2 SAMUEL 7:15", "ALIANÇA ETERNA COM DAVI", dest)

    elif cid == "final":
        # Card final comparativo + CTA @tempodiario
        draw.rounded_rectangle((90, 430, 520, 870), radius=28, fill=(16, 48, 52, 230), outline=(72, 229, 214), width=5)
        texto_centralizado(draw, 305, 515, "SALVO", carregar_fonte(58), (72, 229, 214))
        texto_centralizado(draw, 305, 620, "Eclesiastes 12", carregar_fonte(34), (240, 245, 250))
        texto_centralizado(draw, 305, 680, "+", carregar_fonte(38), (255, 209, 102))
        texto_centralizado(draw, 305, 740, "Aliança 2 Sm 7", carregar_fonte(34), (240, 245, 250))

        draw.rounded_rectangle((560, 430, 990, 870), radius=28, fill=(52, 18, 28, 230), outline=(255, 89, 100), width=5)
        texto_centralizado(draw, 775, 515, "INCERTO", carregar_fonte(58), (255, 89, 100))
        texto_centralizado(draw, 775, 620, "Silêncio em Reis", carregar_fonte(34), (240, 245, 250))
        texto_centralizado(draw, 775, 680, "+", carregar_fonte(38), (255, 209, 102))
        texto_centralizado(draw, 775, 740, "Alerta Neemias", carregar_fonte(34), (240, 245, 250))

        # Card do Canal Tempo Diário
        draw.rounded_rectangle((170, 920, 910, 1065), radius=30, fill=(245, 183, 0), outline=(255, 245, 200), width=5)
        texto_centralizado(draw, 540, 972, CANAL_NOME, carregar_fonte(52), (14, 14, 24))
        texto_centralizado(draw, 540, 1026, CANAL_HANDLE, carregar_fonte(34), (35, 30, 45))

        pulse = 1.0 + 0.04 * math.sin(t_global * 7.0)
        desenhar_badge_contador(draw, 540, 1185, "SALVO? SIM OU NÃO", "COMENTA AÍ E SEGUE O CANAL", dest, scale=0.95 * pulse)


def desenhar_hud_e_legendas(draw, cena, t_global, duracao_total, grupo_legenda):
    # Barra de progresso no topo
    pct = min(1.0, max(0.0, t_global / duracao_total))
    draw.rectangle((0, 0, LARGURA, 14), fill=(255, 255, 255, 35))
    draw.rectangle((0, 0, int(LARGURA * pct), 14), fill=cena["destaque"])

    # Tag superior do canal + capítulo
    draw.rounded_rectangle((70, 58, 410, 118), radius=24, fill=(0, 0, 0, 155), outline=(255, 255, 255, 70), width=2)
    texto_centralizado(draw, 240, 88, CANAL_HANDLE, carregar_fonte(34), (255, 209, 102))

    draw.rounded_rectangle((435, 58, 1010, 118), radius=24, fill=(0, 0, 0, 155), outline=(*cena["destaque"], 130), width=2)
    texto_centralizado(draw, 722, 88, cena["titulo"], carregar_fonte(30), (240, 242, 248))

    # Legenda palavra por palavra estilo Kaio/TikTok
    if grupo_legenda:
        palavras = grupo_legenda["palavras"]
        f_normal = carregar_fonte(66)
        f_ativo = carregar_fonte(74)
        espaco = 22
        larguras = []
        for p in palavras:
            ativo = p["start"] <= t_global <= (p["start"] + p["dur"] + 0.05)
            f = f_ativo if ativo else f_normal
            w, _ = texto_largura(draw, p["text"].upper(), f)
            larguras.append((w, ativo, f, p["text"].upper()))

        total_w = sum(item[0] for item in larguras) + espaco * (len(larguras) - 1)
        # Quebra em 2 linhas se ficar muito largo
        if total_w > 940 and len(larguras) > 1:
            meio = len(larguras) // 2
            linhas = [larguras[:meio], larguras[meio:]]
        else:
            linhas = [larguras]

        y_base = 1435 if len(linhas) == 1 else 1390
        for li, linha in enumerate(linhas):
            lw = sum(item[0] for item in linha) + espaco * (len(linha) - 1)
            cur_x = (LARGURA - lw) / 2
            y_linha = y_base + li * 92
            for w, ativo, f, txt in linha:
                cor = cena["destaque"] if ativo else (255, 255, 255)
                draw.text(
                    (cur_x, y_linha),
                    txt,
                    font=f,
                    fill=cor,
                    stroke_width=8,
                    stroke_fill=(0, 0, 0),
                )
                cur_x += w + espaco


# ==========================================================
# PIPELINE PRINCIPAL
# ==========================================================
async def preparar_tudo(ffmpeg_exe):
    print("[1/4] Gerando narração neural em PT-BR (edge-tts)...")
    cenas_info = []
    audios_pcm = []
    palavras_globais = []
    cursor_tempo = 0.0
    inicios_cenas = []

    pausa_samples = np.zeros(int(PAUSA_ENTRE_CENAS * SAMPLE_RATE), dtype=np.float32)

    for idx, cena in enumerate(CENAS):
        mp3_temp = f"temp_cena_{idx}.mp3"
        word_ev, sent_ev = await sintetizar_cena(idx, cena["texto"], mp3_temp)
        pcm = decodificar_mp3_pcm(ffmpeg_exe, mp3_temp)
        dur = len(pcm) / SAMPLE_RATE

        if not word_ev:
            word_ev = construir_palavras_fallback(cena["texto"], dur, sent_ev)

        inicio_cena = cursor_tempo
        inicios_cenas.append(inicio_cena)

        for w in word_ev:
            palavras_globais.append(
                {
                    "text": w["text"],
                    "start": inicio_cena + w["start"],
                    "dur": w["dur"],
                }
            )

        audios_pcm.append(pcm)
        audios_pcm.append(pausa_samples)
        cursor_tempo += dur + PAUSA_ENTRE_CENAS

        cenas_info.append(
            {
                **cena,
                "start": inicio_cena,
                "end": cursor_tempo,
                "fundo": criar_fundo_cena(cena["cor_topo"], cena["cor_base"], cena["cor_glow"]),
            }
        )
        os.remove(mp3_temp)
        print(f"   - Cena {idx + 1}/{len(CENAS)} ({cena['id']}): {dur:.2f}s")

    duracao_total = cursor_tempo + 0.4
    voz_full = np.concatenate(audios_pcm)
    pad_fim = np.zeros(max(0, int(duracao_total * SAMPLE_RATE) - len(voz_full)), dtype=np.float32)
    voz_full = np.concatenate([voz_full, pad_fim])

    print("[2/4] Mixando trilha sonora cinematográfica + efeitos sonoros...")
    bgm = gerar_trilha_e_sfx(duracao_total, inicios_cenas)
    mix = np.tanh((voz_full * 0.92 + bgm) * 1.05)
    pcm16 = (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16)

    with wave.open("temp_audio.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm16.tobytes())

    grupos_legenda = agrupar_legendas(palavras_globais)
    return cenas_info, duracao_total, voz_full, grupos_legenda


def renderizar_video(ffmpeg_exe, cenas_info, duracao_total, voz_full, grupos_legenda):
    total_frames = int(duracao_total * FPS)
    print(f"[3/4] Renderizando {total_frames} frames ({duracao_total:.1f}s @ {FPS}fps)...")

    cmd = [
        ffmpeg_exe,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{LARGURA}x{ALTURA}",
        "-r",
        str(FPS),
        "-i",
        "pipe:0",
        "-i",
        "temp_audio.wav",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        ARQUIVO_SAIDA,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    idx_cena = 0
    idx_leg = 0
    samples_por_frame = SAMPLE_RATE // FPS

    try:
        for f in range(total_frames):
            t = f / FPS
            while idx_cena < len(cenas_info) - 1 and t >= cenas_info[idx_cena]["end"]:
                idx_cena += 1
            cena = cenas_info[idx_cena]
            prog = (t - cena["start"]) / max(0.01, cena["end"] - cena["start"])

            # Calcula abertura da boca pela energia do áudio neste frame
            s0 = f * samples_por_frame
            s1 = min(len(voz_full), s0 + samples_por_frame)
            rms = float(np.sqrt(np.mean(voz_full[s0:s1] ** 2))) if s1 > s0 else 0.0
            boca = min(1.0, rms * 6.5)

            while idx_leg < len(grupos_legenda) and t > grupos_legenda[idx_leg]["end"]:
                idx_leg += 1
            grupo_atual = None
            if idx_leg < len(grupos_legenda):
                g = grupos_legenda[idx_leg]
                if g["start"] <= t <= g["end"]:
                    grupo_atual = g

            # Desenha overlay transparente sobre o fundo pré-calculado
            overlay = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            desenhar_particulas(draw, t, cena["destaque"])
            desenhar_cena_especifica(draw, cena, prog, t, boca)
            desenhar_hud_e_legendas(draw, cena, t, duracao_total, grupo_atual)

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
        raise RuntimeError("Erro ao codificar o vídeo com FFmpeg.")
    print(f"[4/4] Concluído! Vídeo salvo em: {os.path.abspath(ARQUIVO_SAIDA)}")


def main():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cenas_info, duracao_total, voz_full, grupos_legenda = asyncio.run(preparar_tudo(ffmpeg_exe))
    renderizar_video(ffmpeg_exe, cenas_info, duracao_total, voz_full, grupos_legenda)


if __name__ == "__main__":
    main()
