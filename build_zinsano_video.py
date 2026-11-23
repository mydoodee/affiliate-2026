import math
import os
import struct
import subprocess
import urllib.request
import wave
from PIL import Image, ImageDraw, ImageFilter

OUT_DIR = r"d:\9.Code\shopee_ai\videos"
TMP_DIR = os.path.join(OUT_DIR, "tmp_v3")
os.makedirs(TMP_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30

IMG_URLS = {
    "main": "https://down-bs-th.img.susercontent.com/th-11134207-7r98z-lpov09alxgxcec.webp",
    "gal1": "https://down-bs-th.img.susercontent.com/th-11134207-7ra0l-mchb1d9fkrby70.webp",
    "gal2": "https://down-bs-th.img.susercontent.com/th-11134207-81ztq-mvr69sy9rh1e03.webp",
    "gal3": "https://down-bs-th.img.susercontent.com/th-11134207-7ra0l-mchb3e5oza723f.webp",
}


def download_images():
    paths = {}
    for k, url in IMG_URLS.items():
        dst = os.path.join(TMP_DIR, f"{k}.webp")
        if not os.path.exists(dst):
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r, open(dst, "wb") as f:
                f.write(r.read())
        paths[k] = dst
    return paths


def make_gradient_bg(top_rgb, mid_rgb, bot_rgb, mid_pos=0.58) -> Image.Image:
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        if t < mid_pos:
            u = t / mid_pos
            r = int(top_rgb[0] + (mid_rgb[0] - top_rgb[0]) * u)
            g = int(top_rgb[1] + (mid_rgb[1] - top_rgb[1]) * u)
            b = int(top_rgb[2] + (mid_rgb[2] - top_rgb[2]) * u)
        else:
            u = (t - mid_pos) / (1.0 - mid_pos)
            r = int(mid_rgb[0] + (bot_rgb[0] - mid_rgb[0]) * u)
            g = int(mid_rgb[1] + (bot_rgb[1] - mid_rgb[1]) * u)
            b = int(mid_rgb[2] + (bot_rgb[2] - mid_rgb[2]) * u)
        for x in range(W):
            px[x, y] = (r, g, b)
    return im


def fit_cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    r = img.resize((nw, nh), Image.Resampling.LANCZOS)
    l = (nw - tw) // 2
    t = (nh - th) // 2
    return r.crop((l, t, l + tw, t + th))


def paste_rounded_card(canvas: Image.Image, src: Image.Image, x: int, y: int, cw: int, ch: int, border=14, radius=38):
    base = canvas.convert("RGBA")
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [x - border - 6, y - border + 18, x + cw + border + 6, y + ch + border + 26],
        radius=radius + 8,
        fill=(0, 0, 0, 150),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    base = Image.alpha_composite(base, shadow)

    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle(
        [x - border, y - border, x + cw + border, y + ch + border],
        radius=radius + 6,
        fill=(255, 255, 255, 255),
    )
    fitted = fit_cover(src.convert("RGB"), cw, ch).convert("RGBA")
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, ch], radius=radius, fill=255)
    frame.paste(fitted, (x, y), mask)
    return Image.alpha_composite(base, frame)


def build_scenes(paths):
    im_main = Image.open(paths["main"])
    im_g1 = Image.open(paths["gal1"])
    im_g2 = Image.open(paths["gal2"])
    im_g3 = Image.open(paths["gal3"])

    # Scene 1: Problem/Hook — deep cobalt-slate water pressure vibe
    bg1 = make_gradient_bg((12, 34, 62), (24, 72, 120), (10, 18, 30))
    s1 = paste_rounded_card(bg1, im_g1, (W - 720) // 2, 515, 720, 720)
    s1_path = os.path.join(TMP_DIR, "bg1.png")
    s1.convert("RGB").save(s1_path, quality=95)

    # Scene 2: Hero ZINSANO 120 Bar machine — dark metallic blue-cyan studio
    bg2 = make_gradient_bg((16, 26, 44), (30, 58, 96), (12, 16, 24))
    s2 = paste_rounded_card(bg2, im_main, (W - 720) // 2, 515, 720, 720)
    s2_path = os.path.join(TMP_DIR, "bg2.png")
    s2.convert("RGB").save(s2_path, quality=95)

    # Scene 3: Versatility / Warranty — crisp steel-teal studio
    bg3 = make_gradient_bg((14, 44, 52), (26, 86, 98), (10, 22, 28))
    s3 = paste_rounded_card(bg3, im_g2, (W - 720) // 2, 515, 720, 720)
    s3_path = os.path.join(TMP_DIR, "bg3.png")
    s3.convert("RGB").save(s3_path, quality=95)

    # Scene 4: Shopee-Orange CTA Card
    bg4 = make_gradient_bg((212, 48, 22), (246, 102, 42), (24, 20, 24))
    s4 = paste_rounded_card(bg4, im_g3, (W - 640) // 2, 505, 640, 585)
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ud = ImageDraw.Draw(ui)
    ud.rounded_rectangle([120, 1150, W - 120, 1290], radius=32, fill=(255, 255, 255, 248))
    ud.rounded_rectangle([150, 1480, W - 150, 1585], radius=52, fill=(238, 77, 45, 255), outline=(255, 232, 140, 255), width=5)
    s4 = Image.alpha_composite(s4, ui)
    s4_path = os.path.join(TMP_DIR, "bg4.png")
    s4.convert("RGB").save(s4_path, quality=95)

    return [s1_path, s2_path, s3_path, s4_path]


def generate_soft_bgm(wav_path: str, duration_sec: float, sr: int = 44100):
    chords = [
        [220.00, 261.63, 329.63, 392.00],  # Am7
        [174.61, 220.00, 261.63, 329.63],  # Fmaj7
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [196.00, 246.94, 293.66, 392.00],  # G6
    ]
    total_samples = int(duration_sec * sr)
    chord_dur = 2.0
    beat_dur = 0.5
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        buf = bytearray()
        for i in range(total_samples):
            t = i / sr
            chord = chords[int(t // chord_dur) % len(chords)]
            local_c = t % chord_dur
            env_c = min(1.0, local_c / 0.12) * min(1.0, (chord_dur - local_c) / 0.15)
            pad = sum(math.sin(2.0 * math.pi * f * t) for f in chord) / len(chord)
            local_b = t % beat_dur
            pulse = math.exp(-local_b * 10.0) * math.sin(2.0 * math.pi * (chord[0] * 0.5) * t)
            fade = min(1.0, t / 0.5) * min(1.0, max(0.0, (duration_sec - t) / 1.0))
            sample = (0.50 * pad * env_c + 0.38 * pulse) * 0.11 * fade
            val = max(-32767, min(32767, int(sample * 32767)))
            buf += struct.pack("<h", val)
            if len(buf) >= 16384:
                wf.writeframes(buf)
                buf.clear()
        if buf:
            wf.writeframes(buf)


def get_duration(path: str) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            text=True,
        ).strip()
    )


def fmt_ass_time(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = min(99, int(round((sec - int(sec)) * 100)))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass(ass_path: str, starts: list[float], durs: list[float]):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopHook,Leelawadee UI,64,&H00FFFFFF,&H00FFFFFF,&H00121212,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,8,60,60,235,1
Style: SubMain,Leelawadee UI,56,&H00FFFFFF,&H00FFFFFF,&H00101010,&HB0000000,-1,0,0,0,100,100,0,0,1,5,3,2,65,65,395,1
Style: PriceBig,Leelawadee UI,78,&H002D4DEE,&H002D4DEE,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: CtaBtn,Leelawadee UI,54,&H00FFFFFF,&H00FFFFFF,&H00112288,&H00000000,-1,0,0,0,100,100,0,0,1,3,2,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []

    def add(layer, s, e, style, txt):
        ev.append(f"Dialogue: {layer},{fmt_ass_time(s)},{fmt_ass_time(e)},{style},,0,0,0,,{txt}")

    s1, d1 = starts[0], durs[0]
    add(2, s1, s1 + d1 - 0.12, "TopHook", r"{\c&H00D4FF&}คราบตะไคร่หน้าบ้าน{\c&H00FFFFFF&}\Nฉีดทีเดียวขาวเหมือนใหม่!")
    add(1, s1 + 0.08, s1 + d1 - 0.1, "SubMain", r"ขัดพื้นจนปวดหลังก็ไม่เกลี้ยง\N{\c&H00D4FF&}เจอ 120 บาร์ตัวนี้จบเลย!")

    s2, d2 = starts[1], durs[1]
    add(2, s2, s2 + d2 - 0.12, "TopHook", r"{\c&H00D4FF&}ZINSANO 120 บาร์{\c&H00FFFFFF&}\Nรุ่น AMAZON ULTRA")
    add(1, s2 + 0.08, s2 + 3.0, "SubMain", r"เครื่องฉีดน้ำแรงดันสูง\N{\c&H00D4FF&}ZINSANO AMAZON ULTRA")
    add(1, s2 + 3.0, s2 + d2 - 0.1, "SubMain", r"แรงดันจัดเต็ม {\c&H00D4FF&}80–120 บาร์{\c&H00FFFFFF&}\Nแรงสะใจ สายช่างไว้ใจ")

    s3, d3 = starts[2], durs[2]
    add(2, s3, s3 + d3 - 0.12, "TopHook", r"{\c&H00D4FF&}ล้างรถ • ล้างพื้น • ล้างแอร์{\c&H00FFFFFF&}\Nรับประกันศูนย์ 1 ปี")
    add(1, s3 + 0.08, s3 + 2.8, "SubMain", r"ใช้ได้ทั้งล้างรถ ฉีดพื้นโรงรถ\N{\c&H00D4FF&}ล้างแอร์ ล้างรั้วครบจบ")
    add(1, s3 + 2.8, s3 + d3 - 0.1, "SubMain", r"ตัวเครื่องทนทาน\N{\c&H00D4FF&}มีรับประกันศูนย์ 1 ปีเต็ม")

    s4, d4 = starts[3], durs[3]
    add(2, s4, s4 + d4, "TopHook", r"{\c&H00FFFFFF&}ZINSANO Official\N{\c&H00D4FF&}AMAZON ULTRA 120 บาร์")
    add(3, s4 + 0.05, s4 + d4, "PriceBig", r"{\pos(540,1220)}฿2,590 {\fs44\c&H00333333&}| ★ 4.9 (ประกัน 1 ปี)")
    add(1, s4 + 0.1, s4 + d4, "SubMain", r"{\pos(540,1385)\fs46}ร้าน Official แท้ 100% ใช้โค้ดลดวิดีโอได้!")
    add(3, s4 + 0.1, s4 + d4, "CtaBtn", r"{\pos(540,1533)}กดตะกร้าส้มเช็กโปรเลย!")

    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(header + "\n".join(ev) + "\n")


def main():
    print("1) Downloading official ZINSANO high-res product photos...")
    paths = download_images()
    print("2) Building 4 crisp vertical 1080x1920 scenes...")
    bgs = build_scenes(paths)

    mp3s = [os.path.join(TMP_DIR, f"v3_s{i}.mp3") for i in range(1, 5)]
    audio_durs = [get_duration(m) for m in mp3s]
    pad_after = [0.32, 0.35, 0.35, 0.65]
    scene_durs = [round(a + p, 2) for a, p in zip(audio_durs, pad_after)]
    xfade = 0.32

    starts = [0.0]
    for i in range(1, 4):
        starts.append(round(starts[i - 1] + scene_durs[i - 1] - xfade, 3))
    total_dur = round(starts[-1] + scene_durs[-1], 3)
    print(f"Scene durations: {scene_durs}, starts: {starts}, total: {total_dur}s")

    print("3) Rendering smooth Ken Burns clips...")
    clips = []
    zooms = [
        f"scale=1200:-1,zoompan=z='min(zoom+0.00050,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        f"scale=1200:-1,zoompan=z='min(zoom+0.00055,1.09)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        f"scale=1200:-1,zoompan=z='max(1.07-0.00035*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        f"scale=1140:-1,zoompan=z='min(zoom+0.00022,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
    ]
    for i, (bg, dur, z) in enumerate(zip(bgs, scene_durs, zooms)):
        frames = int(round(dur * FPS))
        out_clip = os.path.join(TMP_DIR, f"clip{i+1}.mp4")
        subprocess.check_call(
            [
                "ffmpeg", "-y", "-v", "error",
                "-loop", "1", "-i", bg,
                "-vf", z.format(frames=frames) + ",format=yuv420p",
                "-t", str(dur), "-r", str(FPS),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                out_clip,
            ]
        )
        clips.append(out_clip)

    print("4) Compositing crossfades + Thai subtitles...")
    ass_path = os.path.join(TMP_DIR, "captions_v3.ass")
    build_ass(ass_path, starts, scene_durs)
    ass_esc = ass_path.replace("\\", "/").replace(":", "\\:")

    silent_vid = os.path.join(TMP_DIR, "visual_only.mp4")
    fc = (
        f"[0:v][1:v]xfade=transition=fade:duration={xfade}:offset={starts[1]}[v01];"
        f"[v01][2:v]xfade=transition=fade:duration={xfade}:offset={starts[2]}[v02];"
        f"[v02][3:v]xfade=transition=fade:duration={xfade}:offset={starts[3]}[v03];"
        f"[v03]ass='{ass_esc}',format=yuv420p[vout]"
    )
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", clips[0], "-i", clips[1], "-i", clips[2], "-i", clips[3],
            "-filter_complex", fc,
            "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", str(FPS),
            silent_vid,
        ]
    )

    print("5) Mixing Thai voiceover + soft BGM...")
    bgm_wav = os.path.join(TMP_DIR, "bgm_v3.wav")
    generate_soft_bgm(bgm_wav, total_dur + 0.5)
    final_mp4 = os.path.join(OUT_DIR, "promo_03_zinsano_120bar.mp4")
    delays = [int(round((s + 0.08) * 1000)) for s in starts]
    afc = (
        f"[1:a]adelay={delays[0]}|{delays[0]},volume=1.35[a1];"
        f"[2:a]adelay={delays[1]}|{delays[1]},volume=1.35[a2];"
        f"[3:a]adelay={delays[2]}|{delays[2]},volume=1.35[a3];"
        f"[4:a]adelay={delays[3]}|{delays[3]},volume=1.35[a4];"
        f"[5:a]volume=0.55[bgm];"
        f"[a1][a2][a3][a4][bgm]amix=inputs=5:duration=longest:dropout_transition=0:normalize=0,alimiter=limit=0.95[aout]"
    )
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", silent_vid,
            "-i", mp3s[0], "-i", mp3s[1], "-i", mp3s[2], "-i", mp3s[3],
            "-i", bgm_wav,
            "-filter_complex", afc,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-shortest", "-movflags", "+faststart",
            final_mp4,
        ]
    )

    for idx, s in enumerate(starts):
        t = round(s + 1.4, 2)
        subprocess.check_call(
            ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", final_mp4, "-frames:v", "1", "-q:v", "3",
             os.path.join(TMP_DIR, f"preview_s{idx+1}.jpg")]
        )

    size_mb = os.path.getsize(final_mp4) / (1024 * 1024)
    print(f"DONE! Saved: {final_mp4} ({size_mb:.2f} MB, {total_dur:.2f}s)")


if __name__ == "__main__":
    main()
