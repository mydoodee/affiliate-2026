import json
import math
import os
import struct
import subprocess
import wave
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

BASE_DIR = r"d:\9.Code\shopee_ai"
VID_DIR = os.path.join(BASE_DIR, "videos")
TMP_DIR = os.path.join(VID_DIR, "drama_01")
MANIFEST_PATH = os.path.join(VID_DIR, "manifest.json")

S1_SRC = r"C:\Users\it\.gemini\antigravity\brain\45d904a1-debb-4386-93fd-0458e8fa7b73\drama_s1_problem_1795489769986.jpg"
S2_SRC = r"C:\Users\it\.gemini\antigravity\brain\45d904a1-debb-4386-93fd-0458e8fa7b73\drama_s2_solution_1795489788780.jpg"
S3_SRC = r"C:\Users\it\.gemini\antigravity\brain\45d904a1-debb-4386-93fd-0458e8fa7b73\drama_s3_magic_1795489817501.jpg"
REAL_PROD = os.path.join(TMP_DIR, "seagull_real.webp")

W, H, FPS = 1080, 1920, 30


def fit_cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    r = img.resize((nw, nh), Image.Resampling.LANCZOS)
    l = (nw - tw) // 2
    t = (nh - th) // 2
    return r.crop((l, t, l + tw, t + th))


def add_cinematic_vignette(img: Image.Image, top_dark=0.52, bot_dark=0.66) -> Image.Image:
    base = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = ov.load()
    for y in range(H):
        if y < 520:
            t = 1.0 - (y / 520.0)
            a = int(255 * top_dark * (t ** 1.35))
            for x in range(W):
                px[x, y] = (14, 12, 10, a)
        elif y > 1160:
            t = (y - 1160) / (H - 1160)
            a = int(255 * bot_dark * (t ** 1.25))
            for x in range(W):
                px[x, y] = (14, 12, 10, a)
    return Image.alpha_composite(base, ov).convert("RGB")


def paste_rounded(target: Image.Image, src: Image.Image, x: int, y: int, cw: int, ch: int, border=14, radius=38):
    base = target.convert("RGBA")
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [x - border - 8, y - border + 16, x + cw + border + 8, y + ch + border + 28],
        radius=radius + 8,
        fill=(15, 23, 42, 70),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    base = Image.alpha_composite(base, shadow)

    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle(
        [x - border, y - border, x + cw + border, y + ch + border],
        radius=radius + 6,
        fill=(255, 255, 255, 255),
        outline=(240, 224, 214, 255),
        width=3,
    )
    fitted = fit_cover(src.convert("RGB"), cw, ch).convert("RGBA")
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, ch], radius=radius, fill=255)
    frame.paste(fitted, (x, y), mask)
    return Image.alpha_composite(base, frame)


def build_scenes():
    im1 = Image.open(S1_SRC).convert("RGB")
    im2 = Image.open(S2_SRC).convert("RGB")
    im3 = Image.open(S3_SRC).convert("RGB")
    im_prod = Image.open(REAL_PROD).convert("RGB")

    # Scene 1: Frustrated Husband + Smirking Wife in sunlit kitchen
    s1 = add_cinematic_vignette(fit_cover(im1, W, H), 0.54, 0.68)
    p1 = os.path.join(TMP_DIR, "bg1.png")
    s1.save(p1, quality=95)

    # Scene 2: Wife pouring soybeans & water into sleek cream machine
    s2 = add_cinematic_vignette(fit_cover(im2, W, H), 0.54, 0.68)
    p2 = os.path.join(TMP_DIR, "bg2.png")
    s2.save(p2, quality=95)

    # Scene 3: Steaming silky soy milk pouring into glass mug
    s3 = add_cinematic_vignette(fit_cover(im3, W, H), 0.52, 0.68)
    p3 = os.path.join(TMP_DIR, "bg3.png")
    s3.save(p3, quality=95)

    # Scene 4: Warm Delighted Taste-Test Cut (tight cinematic crop on steaming mug + warm golden grade + floating happy couple cameo!)
    mug_crop = im3.crop((int(im3.width * 0.14), int(im3.height * 0.30), int(im3.width * 0.96), int(im3.height * 0.90)))
    s4_base = ImageEnhance.Color(fit_cover(mug_crop, W, H)).enhance(1.15)
    s4_base = add_cinematic_vignette(s4_base, 0.56, 0.72).convert("RGBA")

    # Circular smiling couple cameo badge on top-right below top hook
    couple_crop = im2.crop((int(im2.width * 0.08), int(im2.height * 0.26), int(im2.width * 0.94), int(im2.height * 0.62)))
    cameo_sz = 270
    cameo = fit_cover(couple_crop, cameo_sz, cameo_sz).convert("RGBA")
    cx, cy = W - cameo_sz - 65, 455
    mask = Image.new("L", (cameo_sz, cameo_sz), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, cameo_sz, cameo_sz], fill=255)
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([cx - 8, cy - 8, cx + cameo_sz + 8, cy + cameo_sz + 8], fill=(255, 255, 255, 245))
    ring.paste(cameo, (cx, cy), mask)
    s4_final = Image.alpha_composite(s4_base, ring).convert("RGB")
    p4 = os.path.join(TMP_DIR, "bg4.png")
    s4_final.save(p4, quality=95)

    # Scene 5: Premium White & Orange Editorial End-Card (matches Babman Picks website!)
    s5 = Image.new("RGB", (W, H))
    px5 = s5.load()
    for y in range(H):
        t = y / (H - 1)
        if t < 0.26:
            # Vibrant warm Shopee-orange top banner header
            u = t / 0.26
            r = int(232 + (246 - 232) * u)
            g = int(68 + (104 - 68) * u)
            b = int(30 + (48 - 30) * u)
        elif t < 0.78:
            # Crisp warm ivory/white middle studio canvas
            r, g, b = 250, 248, 245
        else:
            # Soft warm charcoal fade at very bottom for contrast
            u = (t - 0.78) / 0.22
            r = int(250 + (235 - 250) * u)
            g = int(248 + (232 - 248) * u)
            b = int(245 + (226 - 245) * u)
        for x in range(W):
            px5[x, y] = (r, g, b)

    s5_rgba = paste_rounded(s5, im_prod, (W - 650) // 2, 515, 650, 585, border=16, radius=36)
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ud = ImageDraw.Draw(ui)
    # Clean crisp price card with soft orange border
    ud.rounded_rectangle(
        [115, 1150, W - 115, 1290],
        radius=30,
        fill=(255, 255, 255, 255),
        outline=(240, 78, 35, 90),
        width=4,
    )
    # Bold orange CTA pill (safe zone y=1465..1575)
    ud.rounded_rectangle(
        [110, 1465, W - 110, 1575],
        radius=55,
        fill=(240, 78, 35, 255),
        outline=(255, 224, 178, 255),
        width=5,
    )
    s5_final = Image.alpha_composite(s5_rgba, ui).convert("RGB")
    p5 = os.path.join(TMP_DIR, "bg5.png")
    s5_final.save(p5, quality=95)

    return [p1, p2, p3, p4, p5]


def generate_morning_bgm(wav_path: str, duration_sec: float, sr: int = 44100):
    """Warm, cheerful morning acoustic-lofi chord bed (100% copyright-free)."""
    chords = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [293.66, 349.23, 440.00, 523.25],  # Dm7
        [329.63, 392.00, 493.88, 587.33],  # Em7
        [349.23, 440.00, 523.25, 659.25],  # Fmaj7
    ]
    total = int(duration_sec * sr)
    chord_dur = 1.8
    pluck_dur = 0.45
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        buf = bytearray()
        for i in range(total):
            t = i / sr
            ch = chords[int(t // chord_dur) % len(chords)]
            lc = t % chord_dur
            env_c = min(1.0, lc / 0.08) * min(1.0, (chord_dur - lc) / 0.14)
            pad = sum(math.sin(2.0 * math.pi * f * t) for f in ch) / len(ch)
            lp = t % pluck_dur
            idx_n = int(t // pluck_dur) % len(ch)
            pluck = math.exp(-lp * 9.5) * math.sin(2.0 * math.pi * ch[idx_n] * 2.0 * t)
            fade = min(1.0, t / 0.4) * min(1.0, max(0.0, (duration_sec - t) / 1.0))
            s = (0.50 * pad * env_c + 0.30 * pluck) * 0.105 * fade
            val = max(-32767, min(32767, int(s * 32767)))
            buf += struct.pack("<h", val)
            if len(buf) >= 16384:
                wf.writeframes(buf)
                buf.clear()
        if buf:
            wf.writeframes(buf)


def get_dur(p: str) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", p],
            text=True,
        ).strip()
    )


def fmt_t(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = min(99, int(round((sec - int(sec)) * 100)))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass(ass_path: str, starts: list[float], durs: list[float]):
    # Speaker color coding: Husband = Bright Warm Yellow (&H0050D8FF), Wife = Soft Coral-Pink (&H00A8B8FF) / White
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopHook,Leelawadee UI,62,&H00FFFFFF,&H00FFFFFF,&H00121212,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,8,60,60,235,1
Style: SubHusband,Leelawadee UI,54,&H00FFFFFF,&H00FFFFFF,&H00101010,&HB0000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,395,1
Style: SubWife,Leelawadee UI,54,&H00FFFFFF,&H00FFFFFF,&H00101010,&HB0000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,395,1
Style: EndHeader,Leelawadee UI,60,&H00FFFFFF,&H00FFFFFF,&H001A2A55,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,8,60,60,210,1
Style: PriceBig,Leelawadee UI,78,&H00234EF0,&H00234EF0,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: SubDark,Leelawadee UI,44,&H00222222,&H00222222,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: CtaWhite,Leelawadee UI,46,&H00FFFFFF,&H00FFFFFF,&H00112266,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []

    def add(layer, s, e, style, txt):
        ev.append(f"Dialogue: {layer},{fmt_t(s)},{fmt_t(e)},{style},,0,0,0,,{txt}")

    # Scene 1: Husband problem
    s1, d1 = starts[0], durs[0]
    add(2, s1, s1 + d1 - 0.1, "TopHook", r"{\c&H00D4FF&}น้ำเต้าหู้ปากซอยคิวยาว{\c&H00FFFFFF&}\Nแถมหวานตัดขา?!")
    add(1, s1 + 0.08, s1 + 2.5, "SubHusband", r"{\c&H0055D8FF&}[สามี] {\c&H00FFFFFF&}โอ๊ย สายแล้วเนี่ย!\Nจะแวะซื้อน้ำเต้าหู้ปากซอย")
    add(1, s1 + 2.5, s1 + d1 - 0.1, "SubHusband", r"{\c&H0055D8FF&}[สามี] {\c&H00FFFFFF&}คิวก็ยาวเป็นหางว่าว\Nแถม{\c&H0055D8FF&}หวานตัดขาอีก!")

    # Scene 2: Wife solution
    s2, d2 = starts[1], durs[1]
    add(2, s2, s2 + d2 - 0.1, "TopHook", r"{\c&H0099CCFF&}เลิกต่อคิวได้แล้ว!{\c&H00FFFFFF&}\Nใส่ถั่ว+น้ำ กดปุ่มเดียวจบ")
    add(1, s2 + 0.08, s2 + d2 * 0.38, "SubWife", r"{\c&H0099B8FF&}[ภรรยา] {\c&H00FFFFFF&}เลิกต่อคิวได้แล้วพ่อคุณ!")
    add(1, s2 + d2 * 0.38, s2 + d2 - 0.1, "SubWife", r"{\c&H0099B8FF&}[ภรรยา] {\c&H00FFFFFF&}แค่ใส่ถั่วเหลือง+น้ำเปล่า\Nลงเครื่อง Seagull {\c&H0055D8FF&}กดปุ่มเดียวจบ!")

    # Scene 3: Steaming magic pour
    s3, d3 = starts[2], durs[2]
    add(2, s3, s3 + d3 - 0.1, "TopHook", r"{\c&H00D4FF&}ทั้งปั่นทั้งต้มอัตโนมัติ{\c&H00FFFFFF&}\Nทำได้ตั้ง 8 เมนู!")
    add(1, s3 + 0.08, s3 + d3 * 0.52, "SubWife", r"{\c&H0099B8FF&}[ภรรยา] {\c&H00FFFFFF&}ทั้งปั่นทั้งต้มให้เอง\N{\c&H0055D8FF&}เนื้อเนียนนุ่มไม่ต้องกรองกาก")
    add(1, s3 + d3 * 0.52, s3 + d3 - 0.1, "SubWife", r"{\c&H0099B8FF&}[ภรรยา] {\c&H00FFFFFF&}ทำได้ตั้ง {\c&H0055D8FF&}8 เมนู{\c&H00FFFFFF&}\Nทั้งโจ๊ก ทั้งซุปข้าวโพดเลยนะ!")

    # Scene 4: Husband amazed reaction
    s4, d4 = starts[3], durs[3]
    add(2, s4, s4 + d4 - 0.1, "TopHook", r"{\c&H00D4FF&}หอมเนียนกว่าเจ้าดัง!{\c&H00FFFFFF&}\Nคุมหวานได้ + ประหยัดเยอะ")
    add(1, s4 + 0.08, s4 + d4 * 0.48, "SubHusband", r"{\c&H0055D8FF&}[สามี] {\c&H00FFFFFF&}เฮ้ย! หอมมันเนียนกว่า\N{\c&H0055D8FF&}เจ้าดังปากซอยอีก!")
    add(1, s4 + d4 * 0.48, s4 + d4 - 0.1, "SubHusband", r"{\c&H0055D8FF&}[สามี] {\c&H00FFFFFF&}ทำกินเองคุมหวานได้\Nแถม{\c&H0055D8FF&}ประหยัดไปตั้งเยอะ!")

    # Scene 5: Crisp White & Orange End-Card
    s5, d5 = starts[4], durs[4]
    add(2, s5, s5 + d5, "EndHeader", r"Seagull เครื่องทำน้ำเต้าหู้ 1.2L\N{\c&H00AAEEFF&}รุ่น 8 in 1 (สีครีม)")
    add(3, s5 + 0.05, s5 + d5, "PriceBig", r"{\pos(540,1220)}฿1,287 {\fs42\c&H00444444&}| ★ 4.9 (ขายแล้ว 30k+)")
    add(1, s5 + 0.1, s5 + d5, "SubDark", r"{\pos(540,1375)}แบรนด์นกนางนวลแท้ • ทำน้ำเต้าหู้ โจ๊ก ซุป จบในเครื่องเดียว")
    add(3, s5 + 0.1, s5 + d5, "CtaWhite", r"{\pos(540,1520)}กดตะกร้า / ลิงก์หน้าโปรไฟล์ เบอร์ #05")

    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(header + "\n".join(ev) + "\n")


def update_manifest():
    items = []
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            items = json.load(f)
    new_item = {
        "id": "drama01_seagull",
        "title": "[ละครสั้น 2 ตัวละคร] #05 Seagull เครื่องทำน้ำเต้าหู้ 1.2L",
        "filename": "drama_01_seagull_soymilk.mp4",
        "price": "฿1,287",
        "commission": "คอม Shopee Video 10.4% (฿134) • Lazada 17% (฿238!)",
        "note": "ละครสั้นสามี-ภรรยา (2 เสียง ชาย+หญิง) ใช้ได้ทั้ง TikTok และ Shopee Video! เปิดป้าย AI + เลือกปกฉากที่ 3 (เทน้ำเต้าหู้ร้อนๆ)",
        "caption": "เบื่อต่อคิวน้ำเต้าหู้ตอนเช้าแถมหวานเจี๊ยบ! ดูวิธีจบปัญหาในปุ่มเดียว 🥛 เครื่อง Seagull 8 in 1 พิกัดตะกร้า/ลิงก์หน้าโปรไฟล์ #05 #เครื่องทำน้ำเต้าหู้ #รีวิวของดี #ของใช้ในครัว",
        "affiliate_link": "https://s.shopee.co.th/4fy0Eq7MIA",
        "product_link": "https://shopee.co.th/product/1485671971/40215480650",
    }
    items = [new_item] + [x for x in items if x["id"] != new_item["id"]]
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def main():
    print("1) Preparing 5 cohesive drama scenes...")
    bgs = build_scenes()
    mp3s = [
        os.path.join(TMP_DIR, "d1_husband.mp3"),
        os.path.join(TMP_DIR, "d2_wife.mp3"),
        os.path.join(TMP_DIR, "d3_wife.mp3"),
        os.path.join(TMP_DIR, "d4_husband.mp3"),
        os.path.join(TMP_DIR, "d5_wife.mp3"),
    ]
    adurs = [get_dur(m) for m in mp3s]
    pads = [0.28, 0.28, 0.28, 0.30, 0.65]
    sdurs = [round(a + p, 2) for a, p in zip(adurs, pads)]
    xfade = 0.25

    starts = [0.0]
    for i in range(1, 5):
        starts.append(round(starts[i - 1] + sdurs[i - 1] - xfade, 3))
    total = round(starts[-1] + sdurs[-1], 3)
    print(f"Scene durs: {sdurs}, starts: {starts}, total: {total}s")

    print("2) Rendering smooth Ken Burns drama shots...")
    zooms = [
        # S1: Punch in toward husband's stressed watch check
        f"scale=1220:-1,zoompan=z='min(zoom+0.00055,1.09)':x='iw*0.46-(iw/zoom/2)':y='ih*0.48-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        # S2: Gentle pan & zoom toward wife pouring soybeans
        f"scale=1220:-1,zoompan=z='min(zoom+0.00050,1.08)':x='iw*0.54-(iw/zoom/2)':y='ih*0.50-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        # S3: Slow appetizing hero zoom on pouring steaming soy milk
        f"scale=1240:-1,zoompan=z='min(zoom+0.00060,1.11)':x='iw*0.52-(iw/zoom/2)':y='ih*0.54-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        # S4: Gentle settle zoom-out on steaming mug + couple cameo
        f"scale=1200:-1,zoompan=z='max(1.07-0.00035*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
        # S5: Clean subtle zoom on White-Orange end card
        f"scale=1130:-1,zoompan=z='min(zoom+0.00020,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={{frames}}:s={W}x{H}:fps={FPS}",
    ]
    clips = []
    for i, (bg, dur, z) in enumerate(zip(bgs, sdurs, zooms)):
        frames = int(round(dur * FPS))
        cpath = os.path.join(TMP_DIR, f"clip{i+1}.mp4")
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error",
            "-loop", "1", "-i", bg,
            "-vf", z.format(frames=frames) + ",format=yuv420p",
            "-t", str(dur), "-r", str(FPS),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            cpath,
        ])
        clips.append(cpath)

    print("3) Compositing 5 drama cuts + 2-color speaker subtitles...")
    ass_path = os.path.join(TMP_DIR, "drama_sub.ass")
    build_ass(ass_path, starts, sdurs)
    ass_esc = ass_path.replace("\\", "/").replace(":", "\\:")

    silent_vid = os.path.join(TMP_DIR, "drama_visual.mp4")
    fc = (
        f"[0:v][1:v]xfade=transition=fade:duration={xfade}:offset={starts[1]}[v01];"
        f"[v01][2:v]xfade=transition=fade:duration={xfade}:offset={starts[2]}[v02];"
        f"[v02][3:v]xfade=transition=fade:duration={xfade}:offset={starts[3]}[v03];"
        f"[v03][4:v]xfade=transition=fade:duration={xfade}:offset={starts[4]}[v04];"
        f"[v04]ass='{ass_esc}',format=yuv420p[vout]"
    )
    subprocess.check_call([
        "ffmpeg", "-y", "-v", "error",
        "-i", clips[0], "-i", clips[1], "-i", clips[2], "-i", clips[3], "-i", clips[4],
        "-filter_complex", fc, "-map", "[vout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", str(FPS),
        silent_vid,
    ])

    print("4) Mixing 2-actor dialogue + morning BGM...")
    bgm = os.path.join(TMP_DIR, "bgm_morning.wav")
    generate_morning_bgm(bgm, total + 0.5)
    final_mp4 = os.path.join(VID_DIR, "drama_01_seagull_soymilk.mp4")
    delays = [int(round((s + 0.06) * 1000)) for s in starts]
    afc = (
        f"[1:a]adelay={delays[0]}|{delays[0]},volume=1.35[a1];"
        f"[2:a]adelay={delays[1]}|{delays[1]},volume=1.40[a2];"
        f"[3:a]adelay={delays[2]}|{delays[2]},volume=1.40[a3];"
        f"[4:a]adelay={delays[3]}|{delays[3]},volume=1.35[a4];"
        f"[5:a]adelay={delays[4]}|{delays[4]},volume=1.40[a5];"
        f"[6:a]volume=0.52[bgm];"
        f"[a1][a2][a3][a4][a5][bgm]amix=inputs=6:duration=longest:dropout_transition=0:normalize=0,alimiter=limit=0.95[aout]"
    )
    subprocess.check_call([
        "ffmpeg", "-y", "-v", "error",
        "-i", silent_vid,
        "-i", mp3s[0], "-i", mp3s[1], "-i", mp3s[2], "-i", mp3s[3], "-i", mp3s[4],
        "-i", bgm,
        "-filter_complex", afc,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-shortest", "-movflags", "+faststart",
        final_mp4,
    ])

    for idx, s in enumerate(starts):
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error",
            "-ss", str(round(s + 1.4, 2)), "-i", final_mp4,
            "-frames:v", "1", "-q:v", "3",
            os.path.join(TMP_DIR, f"preview_s{idx+1}.jpg"),
        ])

    update_manifest()
    mb = os.path.getsize(final_mp4) / (1024 * 1024)
    print(f"DONE! {final_mp4} ({mb:.2f} MB, {total:.2f}s)")


if __name__ == "__main__":
    main()
