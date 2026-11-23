import math
import os
import struct
import subprocess
import wave
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

OUT_DIR = r"d:\9.Code\shopee_ai\videos"
TMP_DIR = os.path.join(OUT_DIR, "tmp")
os.makedirs(TMP_DIR, exist_ok=True)

SCENE1_SRC = r"C:\Users\it\.gemini\antigravity\brain\45d904a1-debb-4386-93fd-0458e8fa7b73\scene1_problem_1795407656260.jpg"
SCENE2_SRC = r"C:\Users\it\.gemini\antigravity\brain\45d904a1-debb-4386-93fd-0458e8fa7b73\scene2_camera_1795407695329.jpg"

W, H = 1080, 1920
FPS = 30


def fit_cover(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    sw, sh = img.size
    scale = max(target_w / sw, target_h / sh)
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - target_w) // 2
    top = (nh - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def add_vignette_and_bars(img: Image.Image, top_dark=0.55, bot_dark=0.62) -> Image.Image:
    base = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = overlay.load()
    for y in range(H):
        if y < 520:
            t = 1.0 - (y / 520.0)
            a = int(255 * top_dark * (t ** 1.4))
            for x in range(W):
                px[x, y] = (10, 12, 18, a)
        elif y > 1180:
            t = (y - 1180) / (H - 1180)
            a = int(255 * bot_dark * (t ** 1.3))
            for x in range(W):
                px[x, y] = (10, 12, 18, a)
    return Image.alpha_composite(base, overlay).convert("RGB")


def build_scene_images():
    im1 = Image.open(SCENE1_SRC).convert("RGB")
    im2 = Image.open(SCENE2_SRC).convert("RGB")

    # Scene 1: Twilight Thai house & orchard gate (problem/hook)
    s1 = add_vignette_and_bars(fit_cover(im1, W, H), top_dark=0.50, bot_dark=0.65)
    s1_path = os.path.join(TMP_DIR, "bg1.png")
    s1.save(s1_path, quality=95)

    # Scene 2: Hero 4G Dual-Lens Camera in rain
    s2 = add_vignette_and_bars(fit_cover(im2, W, H), top_dark=0.48, bot_dark=0.68)
    s2_path = os.path.join(TMP_DIR, "bg2.png")
    s2.save(s2_path, quality=95)

    # Scene 3: Smartphone Night-Vision Dual-Screen Live Feed Mockup
    bg3 = fit_cover(im2, W, H).filter(ImageFilter.GaussianBlur(28))
    bg3 = ImageEnhance.Brightness(bg3).enhance(0.32).convert("RGBA")

    # Phone body dimensions (centered nicely in middle safe zone y=340..1240)
    pw, ph = 640, 880
    px0 = (W - pw) // 2
    py0 = 350

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [px0 - 10, py0 + 18, px0 + pw + 10, py0 + ph + 28],
        radius=58,
        fill=(0, 0, 0, 170),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    bg3 = Image.alpha_composite(bg3, shadow)

    phone_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(phone_layer)
    # Metallic bezel
    pd.rounded_rectangle(
        [px0, py0, px0 + pw, py0 + ph],
        radius=52,
        fill=(24, 28, 36, 255),
        outline=(95, 105, 120, 255),
        width=5,
    )

    # Screen inner area
    pad = 22
    sx0, sy0, sx1, sy1 = px0 + pad, py0 + pad, px0 + pw - pad, py0 + ph - pad
    sw_in, sh_in = sx1 - sx0, sy1 - sy0
    pd.rounded_rectangle([sx0, sy0, sx1, sy1], radius=36, fill=(14, 18, 24, 255))

    # Brightened full-color night vision feeds from scene 1
    nv_base = ImageEnhance.Brightness(im1).enhance(1.85)
    nv_base = ImageEnhance.Contrast(nv_base).enhance(1.18)
    nv_base = ImageEnhance.Color(nv_base).enhance(1.25)

    # Top CAM 1: Wide view of house & orchard gate
    cam_h = (sh_in - 96) // 2
    cam1 = fit_cover(nv_base.crop((0, int(im1.height * 0.25), im1.width, int(im1.height * 0.85))), sw_in - 24, cam_h)
    # Bottom CAM 2: Close-up zoomed view of gate & entrance
    cam2 = fit_cover(
        nv_base.crop((int(im1.width * 0.22), int(im1.height * 0.45), int(im1.width * 0.96), int(im1.height * 0.84))),
        sw_in - 24,
        cam_h,
    )

    # Paste both camera feeds into rounded panels
    def paste_rounded(target, src_im, x, y, r=18):
        mask = Image.new("L", src_im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, src_im.width, src_im.height], radius=r, fill=255)
        target.paste(src_im.convert("RGBA"), (x, y), mask)

    c1_y = sy0 + 54
    c2_y = c1_y + cam_h + 18
    paste_rounded(phone_layer, cam1, sx0 + 12, c1_y, r=18)
    paste_rounded(phone_layer, cam2, sx0 + 12, c2_y, r=18)

    # Dynamic island notch
    pd.rounded_rectangle([W // 2 - 72, sy0 + 12, W // 2 + 72, sy0 + 36], radius=12, fill=(8, 10, 14, 255))

    # Clean LIVE / CAM2 indicators baked onto the phone screen so they track zoom 100%
    from PIL import ImageFont
    try:
        tag_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 22)
    except Exception:
        tag_font = ImageFont.load_default()
    pd.rounded_rectangle([sx0 + 26, c1_y + 14, sx0 + 132, c1_y + 46], radius=14, fill=(220, 38, 38, 235))
    pd.ellipse([sx0 + 36, c1_y + 23, sx0 + 50, c1_y + 37], fill=(255, 255, 255, 255))
    pd.text((sx0 + 58, c1_y + 18), "LIVE", fill=(255, 255, 255, 255), font=tag_font)
    pd.rounded_rectangle([sx0 + 26, c2_y + 14, sx0 + 138, c2_y + 46], radius=14, fill=(16, 185, 129, 235))
    pd.ellipse([sx0 + 36, c2_y + 23, sx0 + 50, c2_y + 37], fill=(255, 255, 255, 255))
    pd.text((sx0 + 56, c2_y + 18), "CAM2", fill=(255, 255, 255, 255), font=tag_font)

    s3 = Image.alpha_composite(bg3, phone_layer).convert("RGB")
    s3_path = os.path.join(TMP_DIR, "bg3.png")
    s3.save(s3_path, quality=95)

    # Scene 4: Energetic Shopee-Orange Commercial CTA Card
    s4 = Image.new("RGB", (W, H))
    px4 = s4.load()
    for y in range(H):
        t = y / (H - 1)
        # Warm deep orange-red top -> vibrant Shopee orange mid -> dark rich charcoal bottom
        if t < 0.62:
            u = t / 0.62
            r = int(215 + (248 - 215) * u)
            g = int(52 + (105 - 52) * u)
            b = int(24 + (44 - 24) * u)
        else:
            u = (t - 0.62) / 0.38
            r = int(248 + (28 - 248) * u)
            g = int(105 + (24 - 105) * u)
            b = int(44 + (28 - 44) * u)
        for x in range(W):
            px4[x, y] = (r, g, b)

    s4_rgba = s4.convert("RGBA")
    # Spotlight hero crop of the camera (positioned below top title with clean breathing room)
    cam_crop = im2.crop((int(im2.width * 0.12), int(im2.height * 0.22), int(im2.width * 0.88), int(im2.height * 0.70)))
    hero_w, hero_h = 720, 680
    hero = fit_cover(cam_crop, hero_w, hero_h)

    hx0, hy0 = (W - hero_w) // 2, 405
    # Drop shadow + crisp white border card
    card_shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(card_shadow).rounded_rectangle(
        [hx0 - 18, hy0 + 18, hx0 + hero_w + 18, hy0 + hero_h + 30],
        radius=48,
        fill=(0, 0, 0, 140),
    )
    card_shadow = card_shadow.filter(ImageFilter.GaussianBlur(24))
    s4_rgba = Image.alpha_composite(s4_rgba, card_shadow)

    frame_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame_layer)
    fd.rounded_rectangle(
        [hx0 - 14, hy0 - 14, hx0 + hero_w + 14, hy0 + hero_h + 14],
        radius=44,
        fill=(255, 255, 255, 255),
    )
    paste_rounded(frame_layer, hero, hx0, hy0, r=34)

    # Price highlight ribbon box (background graphic for crisp ASS price text)
    fd.rounded_rectangle([140, 1135, W - 140, 1285], radius=32, fill=(255, 255, 255, 245))
    # Bright CTA pill box (safe zone y=1480..1585 above Shopee basket)
    fd.rounded_rectangle([150, 1485, W - 150, 1590], radius=52, fill=(238, 77, 45, 255), outline=(255, 230, 140, 255), width=5)

    s4_final = Image.alpha_composite(s4_rgba, frame_layer).convert("RGB")
    s4_path = os.path.join(TMP_DIR, "bg4.png")
    s4_final.save(s4_path, quality=95)

    return [s1_path, s2_path, s3_path, s4_path]


def generate_soft_bgm(wav_path: str, duration_sec: float, sr: int = 44100):
    """Generate a clean, pleasant, copyright-free warm upbeat lo-fi synth bed."""
    chords = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [220.00, 261.63, 329.63, 392.00],  # Am7
        [174.61, 220.00, 261.63, 329.63],  # Fmaj7
        [196.00, 246.94, 293.66, 392.00],  # G6
    ]
    total_samples = int(duration_sec * sr)
    chord_dur = 2.0
    beat_dur = 0.5  # 120 BPM subtle pulse

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

            # Warm pad
            pad = sum(math.sin(2.0 * math.pi * f * t) for f in chord) / len(chord)
            # Gentle soft bass pluck on beat
            local_b = t % beat_dur
            pulse = math.exp(-local_b * 10.0) * math.sin(2.0 * math.pi * (chord[0] * 0.5) * t)

            # Master fade in/out
            fade = min(1.0, t / 0.6) * min(1.0, max(0.0, (duration_sec - t) / 1.2))
            sample = (0.55 * pad * env_c + 0.35 * pulse) * 0.11 * fade
            val = max(-32767, min(32767, int(sample * 32767)))
            buf += struct.pack("<h", val)
            if len(buf) >= 16384:
                wf.writeframes(buf)
                buf.clear()
        if buf:
            wf.writeframes(buf)


def get_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
        text=True,
    ).strip()
    return float(out)


def fmt_ass_time(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass_file(ass_path: str, starts: list[float], durs: list[float]):
    """Build native HarfBuzz/libass Thai subtitles + top hooks + price/CTA graphics."""
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopHook,Leelawadee UI,66,&H00FFFFFF,&H00FFFFFF,&H00121212,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,8,60,60,150,1
Style: TopBadge,Leelawadee UI,44,&H00121212,&H00121212,&H0000D4FF,&H0000D4FF,-1,0,0,0,100,100,0,0,3,18,0,8,80,80,145,1
Style: SubMain,Leelawadee UI,58,&H00FFFFFF,&H00FFFFFF,&H00101010,&HB0000000,-1,0,0,0,100,100,0,0,1,5,3,2,65,65,390,1
Style: PriceBig,Leelawadee UI,82,&H002D4DEE,&H002D4DEE,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: CtaBtn,Leelawadee UI,54,&H00FFFFFF,&H00FFFFFF,&H00112288,&H00000000,-1,0,0,0,100,100,0,0,1,3,2,5,60,60,0,1
Style: CamTag,Leelawadee UI,26,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []

    def add_ev(layer, start, end, style, text):
        lines.append(f"Dialogue: {layer},{fmt_ass_time(start)},{fmt_ass_time(end)},{style},,0,0,0,,{text}")

    # Scene 1
    s1, d1 = starts[0], durs[0]
    add_ev(2, s1, s1 + d1 - 0.15, "TopHook", r"{\c&H00D4FF&}ไม่มี Wi-Fi{\c&H00FFFFFF&}\Nก็ติดกล้องดูสวนได้!")
    add_ev(1, s1 + 0.1, s1 + 2.9, "SubMain", r"สวน ไร่นา หรือหน้าบ้าน{\c&H00D4FF&} ไม่มี Wi-Fi{\c&H00FFFFFF&}")
    add_ev(1, s1 + 2.9, s1 + d1 - 0.1, "SubMain", r"อยากติดกล้องดูผ่านมือถือ\N{\c&H00D4FF&}สามร้อยกว่าบาทจบเลย!")

    # Scene 2
    s2, d2 = starts[1], durs[1]
    add_ev(2, s2, s2 + d2 - 0.15, "TopHook", r"{\c&H00D4FF&}ใส่ซิม 4G เลนส์คู่{\c&H00FFFFFF&}\Nกันน้ำ IP67")
    add_ev(1, s2 + 0.1, s2 + 3.4, "SubMain", r"กล้องใส่ซิม 4G {\c&H00D4FF&}เลนส์คู่{\c&H00FFFFFF&}\Nดูได้ 2 มุมพร้อมกัน")
    add_ev(1, s2 + 3.4, s2 + d2 - 0.1, "SubMain", r"กันน้ำ {\c&H00D4FF&}IP67{\c&H00FFFFFF&}\Nตากแดดตากฝนได้สบาย")

    # Scene 3
    s3, d3 = starts[2], durs[2]
    add_ev(2, s3, s3 + d3 - 0.15, "TopHook", r"{\c&H00D4FF&}กลางคืนภาพสีชัด{\c&H00FFFFFF&}\Nดูสดผ่านมือถือ")
    add_ev(1, s3 + 0.1, s3 + 2.6, "SubMain", r"กลางคืน{\c&H00D4FF&}ภาพสีชัด{\c&H00FFFFFF&}\Nสั่งหมุนดูรอบทิศได้")
    add_ev(1, s3 + 2.6, s3 + d3 - 0.1, "SubMain", r"อยู่ที่ไหนก็ดูสดผ่านแอป\N{\c&H00D4FF&}อุ่นใจ 24 ชม.")

    # Scene 4
    s4, d4 = starts[3], durs[3]
    add_ev(2, s4, s4 + d4, "TopHook", r"{\an8\pos(540,140)\c&H00FFFFFF&}กล้อง 4G เลนส์คู่\N{\c&H00D4FF&}USEE S15-4G")
    # Price inside white rounded card (y=1210)
    add_ev(3, s4 + 0.05, s4 + d4, "PriceBig", r"{\pos(540,1210)}฿351  {\fs46\c&H00333333&}|  ★ 4.9 (ขายแล้ว 9,000+)")
    # Short subtitle above CTA
    add_ev(1, s4 + 0.1, s4 + d4, "SubMain", r"{\pos(540,1385)\fs46}รีวิว 4.9 ดาว คุ้มมากสำหรับติดดูสวน/บ้าน")
    # CTA text centered inside orange pill (y=1538)
    add_ev(3, s4 + 0.1, s4 + d4, "CtaBtn", r"{\pos(540,1538)}กดตะกร้าส้ม / ลิงก์เช็กโปรเลย!")

    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(header + "\n".join(lines) + "\n")


def main():
    print("1) Building 4 crisp vertical 1080x1920 scene assets...")
    bgs = build_scene_images()

    mp3s = [os.path.join(TMP_DIR, f"scene{i}.mp3") for i in range(1, 5)]
    audio_durs = [get_duration(m) for m in mp3s]
    pad_after = [0.35, 0.35, 0.35, 0.70]
    scene_durs = [round(a + p, 2) for a, p in zip(audio_durs, pad_after)]
    xfade = 0.35

    # Calculate exact visual start timestamps accounting for xfade overlap
    starts = [0.0]
    for i in range(1, 4):
        starts.append(round(starts[i - 1] + scene_durs[i - 1] - xfade, 3))
    total_dur = round(starts[-1] + scene_durs[-1], 3)
    print(f"Scene durations: {scene_durs}, starts: {starts}, total: {total_dur}s")

    # 2) Build per-scene Ken Burns MP4 clips (smooth 30fps zoom/pan)
    print("2) Rendering smooth Ken Burns clips...")
    clips = []
    zoom_exprs = [
        # Scene 1: gentle zoom in on house & gate
        f"scale=1240:-1,zoompan=z='min(zoom+0.00055,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        # Scene 2: gentle zoom in slightly upper-center on dual lenses
        f"scale=1240:-1,zoompan=z='min(zoom+0.00060,1.12)':x='iw/2-(iw/zoom/2)':y='ih*0.46-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        # Scene 3: subtle zoom out / settle on phone demo
        f"scale=1240:-1,zoompan=z='max(1.06-0.00035*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        # Scene 4: ultra-gentle pulse zoom on CTA card
        f"scale=1160:-1,zoompan=z='min(zoom+0.00025,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
    ]

    for i, (bg, dur, zexpr) in enumerate(zip(bgs, scene_durs, zoom_exprs)):
        frames = int(round(dur * FPS))
        out_clip = os.path.join(TMP_DIR, f"clip{i+1}.mp4")
        vf = zexpr.format(frames=frames) + ",format=yuv420p"
        subprocess.check_call(
            [
                "ffmpeg", "-y", "-v", "error",
                "-loop", "1", "-i", bg,
                "-vf", vf,
                "-t", str(dur),
                "-r", str(FPS),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                out_clip,
            ]
        )
        clips.append(out_clip)

    # 3) Concatenate video with smooth xfade crossfades + burn ASS Thai subtitles
    print("3) Building Thai ASS subtitles & compositing video...")
    ass_path = os.path.join(TMP_DIR, "captions.ass")
    build_ass_file(ass_path, starts, scene_durs)

    # Escape path for FFmpeg ass filter on Windows
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")

    silent_vid = os.path.join(TMP_DIR, "visual_only.mp4")
    filter_complex = (
        f"[0:v][1:v]xfade=transition=fade:duration={xfade}:offset={starts[1]}[v01];"
        f"[v01][2:v]xfade=transition=fade:duration={xfade}:offset={starts[2]}[v02];"
        f"[v02][3:v]xfade=transition=fade:duration={xfade}:offset={starts[3]}[v03];"
        f"[v03]ass='{ass_escaped}',format=yuv420p[vout]"
    )
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", clips[0], "-i", clips[1], "-i", clips[2], "-i", clips[3],
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-r", str(FPS),
            silent_vid,
        ]
    )

    # 4) Mix voiceovers (aligned to exact visual starts!) + soft copyright-free BGM
    print("4) Mixing Thai AI voiceover + soft background beat...")
    bgm_wav = os.path.join(TMP_DIR, "bgm.wav")
    generate_soft_bgm(bgm_wav, total_dur + 0.5)

    final_mp4 = os.path.join(OUT_DIR, "promo_01_cctv_4g_usee.mp4")
    delays_ms = [int(round((s + 0.08) * 1000)) for s in starts]
    audio_fc = (
        f"[1:a]adelay={delays_ms[0]}|{delays_ms[0]},volume=1.35[a1];"
        f"[2:a]adelay={delays_ms[1]}|{delays_ms[1]},volume=1.35[a2];"
        f"[3:a]adelay={delays_ms[2]}|{delays_ms[2]},volume=1.35[a3];"
        f"[4:a]adelay={delays_ms[3]}|{delays_ms[3]},volume=1.35[a4];"
        f"[5:a]volume=0.55[bgm];"
        f"[a1][a2][a3][a4][bgm]amix=inputs=5:duration=longest:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.95[aout]"
    )
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", silent_vid,
            "-i", mp3s[0], "-i", mp3s[1], "-i", mp3s[2], "-i", mp3s[3],
            "-i", bgm_wav,
            "-filter_complex", audio_fc,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-shortest",
            "-movflags", "+faststart",
            final_mp4,
        ]
    )

    # 5) Extract 4 verification frames (1 from each scene) to inspect visually
    for idx, s in enumerate(starts):
        t = round(s + 1.5, 2)
        frame_out = os.path.join(TMP_DIR, f"preview_scene{idx+1}.jpg")
        subprocess.check_call(
            ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", final_mp4, "-frames:v", "1", "-q:v", "3", frame_out]
        )

    size_mb = os.path.getsize(final_mp4) / (1024 * 1024)
    print(f"DONE! Saved: {final_mp4} ({size_mb:.2f} MB, {total_dur:.2f}s)")


if __name__ == "__main__":
    main()
