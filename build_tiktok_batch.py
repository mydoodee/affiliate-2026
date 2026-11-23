import asyncio
import json
import os
import subprocess
import edge_tts
from PIL import Image, ImageDraw

BASE_DIR = r"d:\9.Code\shopee_ai"
VID_DIR = os.path.join(BASE_DIR, "videos")
MANIFEST_PATH = os.path.join(VID_DIR, "manifest.json")
W, H, FPS = 1080, 1920, 30


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


async def gen_tts_files():
    jobs = [
        (os.path.join(VID_DIR, "tmp", "scene4_tt.mp3"),
         "ราคาแค่สามร้อยห้าสิบเอ็ดบาท รีวิวสี่จุดเก้าดาว กดตะกร้าเหลือง หรือลิงก์หน้าโปรไฟล์ เบอร์หนึ่งได้เลยครับ"),
        (os.path.join(VID_DIR, "tmp_v2", "v2_s4_tt.mp3"),
         "ราคาแค่แปดสิบเก้าบาท ขายไปแล้วสองแสนกว่าหลอด กดตะกร้าเหลือง หรือลิงก์หน้าโปรไฟล์ เบอร์สองได้เลยครับ"),
        (os.path.join(VID_DIR, "tmp_v3", "v3_s4_tt.mp3"),
         "รีวิวสี่จุดเก้าดาว ร้านออฟฟิเชียล กดตะกร้าเหลือง หรือลิงก์หน้าโปรไฟล์ เบอร์สามได้เลยครับ"),
    ]
    for dst, text in jobs:
        comm = edge_tts.Communicate(text, voice="th-TH-NiwatNeural", rate="+8%")
        await comm.save(dst)
        print("TTS ready:", os.path.basename(dst), f"{get_duration(dst):.2f}s")


def recolor_cta_pill_to_tiktok_yellow(src_bg4: str, dst_bg4: str, pill_y0: int, pill_y1: int):
    im = Image.open(src_bg4).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    # Bright TikTok Yellow-Gold CTA pill with dark crisp outline
    d.rounded_rectangle(
        [110, pill_y0, W - 110, pill_y1],
        radius=52,
        fill=(250, 204, 21, 255),
        outline=(255, 255, 255, 255),
        width=6,
    )
    Image.alpha_composite(im, overlay).convert("RGB").save(dst_bg4, quality=95)


def build_tiktok_video(cfg: dict):
    tmp = cfg["tmp_dir"]
    print(f"\n=== Building {cfg['out_name']} ===")
    bg4_tt = os.path.join(tmp, "bg4_tt.png")
    recolor_cta_pill_to_tiktok_yellow(os.path.join(tmp, "bg4.png"), bg4_tt, cfg["pill_y0"], cfg["pill_y1"])

    mp3s = cfg["mp3s"]
    audio_durs = [get_duration(m) for m in mp3s]
    # Reuse clip1..3 exact durations from existing clips
    c1_3_durs = [get_duration(os.path.join(tmp, f"clip{i}.mp4")) for i in range(1, 4)]
    c4_dur = round(audio_durs[3] + 0.65, 2)
    scene_durs = c1_3_durs + [c4_dur]
    xfade = cfg["xfade"]

    starts = [0.0]
    for i in range(1, 4):
        starts.append(round(starts[i - 1] + scene_durs[i - 1] - xfade, 3))
    total_dur = round(starts[-1] + scene_durs[-1], 3)

    # Render only clip4_tt.mp4
    clip4_tt = os.path.join(tmp, "clip4_tt.mp4")
    frames = int(round(c4_dur * FPS))
    z = f"scale=1140:-1,zoompan=z='min(zoom+0.00022,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p"
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-v", "error",
            "-loop", "1", "-i", bg4_tt,
            "-vf", z, "-t", str(c4_dur), "-r", str(FPS),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            clip4_tt,
        ]
    )

    # Write TikTok ASS (safe top margin MarginV=235 + dark bold CTA text on yellow pill)
    ass_path = os.path.join(tmp, "captions_tt.ass")
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
Style: CtaDark,Leelawadee UI,46,&H00111111,&H00111111,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for layer, s, e, style, txt in cfg["build_events"](starts, scene_durs):
        ev.append(f"Dialogue: {layer},{fmt_ass_time(s)},{fmt_ass_time(e)},{style},,0,0,0,,{txt}")
    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(header + "\n".join(ev) + "\n")

    ass_esc = ass_path.replace("\\", "/").replace(":", "\\:")
    clips = [os.path.join(tmp, f"clip{i}.mp4") for i in range(1, 4)] + [clip4_tt]
    silent_vid = os.path.join(tmp, "visual_tt.mp4")
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
            "-filter_complex", fc, "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", str(FPS),
            silent_vid,
        ]
    )

    final_mp4 = os.path.join(VID_DIR, cfg["out_name"])
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
            "-i", cfg["bgm"],
            "-filter_complex", afc,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-shortest", "-movflags", "+faststart",
            final_mp4,
        ]
    )

    # Preview Scene 4 for visual QA
    preview_s4 = os.path.join(tmp, "preview_tt_s4.jpg")
    subprocess.check_call(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(round(starts[3] + 1.4, 2)), "-i", final_mp4, "-frames:v", "1", "-q:v", "3", preview_s4]
    )
    size_mb = os.path.getsize(final_mp4) / (1024 * 1024)
    print(f"DONE {cfg['out_name']} ({size_mb:.2f} MB, {total_dur:.2f}s)")


def ev_cctv(starts, durs):
    s1, s2, s3, s4 = starts
    d1, d2, d3, d4 = durs
    return [
        (2, s1, s1 + d1 - 0.15, "TopHook", r"{\c&H00D4FF&}ไม่มี Wi-Fi{\c&H00FFFFFF&}\Nก็ติดกล้องดูสวนได้!"),
        (1, s1 + 0.1, s1 + 2.9, "SubMain", r"สวน ไร่นา หรือหน้าบ้าน{\c&H00D4FF&} ไม่มี Wi-Fi{\c&H00FFFFFF&}"),
        (1, s1 + 2.9, s1 + d1 - 0.1, "SubMain", r"อยากติดกล้องดูผ่านมือถือ\N{\c&H00D4FF&}สามร้อยกว่าบาทจบเลย!"),
        (2, s2, s2 + d2 - 0.15, "TopHook", r"{\c&H00D4FF&}ใส่ซิม 4G เลนส์คู่{\c&H00FFFFFF&}\Nกันน้ำ IP67"),
        (1, s2 + 0.1, s2 + 3.4, "SubMain", r"กล้องใส่ซิม 4G {\c&H00D4FF&}เลนส์คู่{\c&H00FFFFFF&}\Nดูได้ 2 มุมพร้อมกัน"),
        (1, s2 + 3.4, s2 + d2 - 0.1, "SubMain", r"กันน้ำ {\c&H00D4FF&}IP67{\c&H00FFFFFF&}\Nตากแดดตากฝนได้สบาย"),
        (2, s3, s3 + d3 - 0.15, "TopHook", r"{\c&H00D4FF&}กลางคืนภาพสีชัด{\c&H00FFFFFF&}\Nดูสดผ่านมือถือ"),
        (1, s3 + 0.1, s3 + 2.6, "SubMain", r"กลางคืน{\c&H00D4FF&}ภาพสีชัด{\c&H00FFFFFF&}\Nสั่งหมุนดูรอบทิศได้"),
        (1, s3 + 2.6, s3 + d3 - 0.1, "SubMain", r"อยู่ที่ไหนก็ดูสดผ่านแอป\N{\c&H00D4FF&}อุ่นใจ 24 ชม."),
        (2, s4, s4 + d4, "TopHook", r"{\an8\pos(540,210)\c&H00FFFFFF&}กล้อง 4G เลนส์คู่\N{\c&H00D4FF&}USEE S15-4G"),
        (3, s4 + 0.05, s4 + d4, "PriceBig", r"{\pos(540,1210)}฿351  {\fs44\c&H00333333&}|  ★ 4.9 (ขายแล้ว 9,000+)"),
        (1, s4 + 0.1, s4 + d4, "SubMain", r"{\pos(540,1385)\fs44}กดตะกร้าเหลือง หรือลิงก์หน้าโปรไฟล์ เบอร์ #01"),
        (3, s4 + 0.1, s4 + d4, "CtaDark", r"{\pos(540,1538)}กดตะกร้าเหลือง / ลิงก์ Bio #01"),
    ]


def ev_antiant(starts, durs):
    s1, s2, s3, s4 = starts
    d1, d2, d3, d4 = durs
    return [
        (2, s1, s1 + d1 - 0.12, "TopHook", r"{\c&H00D4FF&}มดขึ้นครัว ฉีดยาไม่หาย{\c&H00FFFFFF&}\Nอย่าเพิ่งฉีดสเปรย์!"),
        (1, s1 + 0.08, s1 + d1 - 0.1, "SubMain", r"บ้านไหนมดขึ้นครัว\N{\c&H00D4FF&}ฉีดเท่าไหร่ก็กลับมาอีก!"),
        (2, s2, s2 + d2 - 0.12, "TopHook", r"{\c&H00D4FF&}เจลหยดล่อมด ANTIANT{\c&H00FFFFFF&}\Nจัดการถึงในรัง!"),
        (1, s2 + 0.08, s2 + 2.9, "SubMain", r"ฉีดสเปรย์ตายแค่ตัวที่เห็น\N{\c&H00D4FF&}แต่นางพญาในรังยังอยู่"),
        (1, s2 + 2.9, s2 + d2 - 0.1, "SubMain", r"ลองเปลี่ยนมาใช้{\c&H00D4FF&} เจลหยดล่อมด{\c&H00FFFFFF&}\NANTIANT แอนตี้แอนท์"),
        (2, s3, s3 + d3 - 0.12, "TopHook", r"{\c&H00D4FF&}หยดไว้ตรงทางเดินมด{\c&H00FFFFFF&}\N2-3 วันหายเกลี้ยง"),
        (1, s3 + 0.08, s3 + 3.0, "SubMain", r"มดจะคาบเจลกลับไป\N{\c&H00D4FF&}กินกันทั้งรัง!"),
        (1, s3 + 3.0, s3 + d3 - 0.1, "SubMain", r"2-3 วันหายเกลี้ยง\N{\c&H00D4FF&}ไม่มีกลิ่นฉุนเหมือนสเปรย์"),
        (2, s4, s4 + d4, "TopHook", r"{\c&H00FFFFFF&}เจลกำจัดมดของแท้\N{\c&H00D4FF&}ANTIANT แอนตี้แอนท์"),
        (3, s4 + 0.05, s4 + d4, "PriceBig", r"{\pos(540,1220)}฿89  {\fs44\c&H00333333&}|  ★ 4.9 (ขายแล้ว 200k+)"),
        (1, s4 + 0.1, s4 + d4, "SubMain", r"{\pos(540,1385)\fs44}กดตะกร้าเหลือง หรือลิงก์หน้าโปรไฟล์ เบอร์ #02"),
        (3, s4 + 0.1, s4 + d4, "CtaDark", r"{\pos(540,1533)}กดตะกร้าเหลือง / ลิงก์ Bio #02"),
    ]


def ev_zinsano(starts, durs):
    s1, s2, s3, s4 = starts
    d1, d2, d3, d4 = durs
    return [
        (2, s1, s1 + d1 - 0.12, "TopHook", r"{\c&H00D4FF&}คราบตะไคร่หน้าบ้าน{\c&H00FFFFFF&}\Nฉีดทีเดียวขาวเหมือนใหม่!"),
        (1, s1 + 0.08, s1 + d1 - 0.1, "SubMain", r"ขัดพื้นจนปวดหลังก็ไม่เกลี้ยง\N{\c&H00D4FF&}เจอ 120 บาร์ตัวนี้จบเลย!"),
        (2, s2, s2 + d2 - 0.12, "TopHook", r"{\c&H00D4FF&}ZINSANO 120 บาร์{\c&H00FFFFFF&}\Nรุ่น AMAZON ULTRA"),
        (1, s2 + 0.08, s2 + 3.0, "SubMain", r"เครื่องฉีดน้ำแรงดันสูง\N{\c&H00D4FF&}ZINSANO AMAZON ULTRA"),
        (1, s2 + 3.0, s2 + d2 - 0.1, "SubMain", r"แรงดันจัดเต็ม {\c&H00D4FF&}80–120 บาร์{\c&H00FFFFFF&}\Nแรงสะใจ สายช่างไว้ใจ"),
        (2, s3, s3 + d3 - 0.12, "TopHook", r"{\c&H00D4FF&}ล้างรถ • ล้างพื้น • ล้างแอร์{\c&H00FFFFFF&}\Nรับประกันศูนย์ 1 ปี"),
        (1, s3 + 0.08, s3 + 2.8, "SubMain", r"ใช้ได้ทั้งล้างรถ ฉีดพื้นโรงรถ\N{\c&H00D4FF&}ล้างแอร์ ล้างรั้วครบจบ"),
        (1, s3 + 2.8, s3 + d3 - 0.1, "SubMain", r"ตัวเครื่องทนทาน\N{\c&H00D4FF&}มีรับประกันศูนย์ 1 ปีเต็ม"),
        (2, s4, s4 + d4, "TopHook", r"{\c&H00FFFFFF&}ZINSANO Official\N{\c&H00D4FF&}AMAZON ULTRA 120 บาร์"),
        (3, s4 + 0.05, s4 + d4, "PriceBig", r"{\pos(540,1220)}฿2,590 {\fs42\c&H00333333&}| ★ 4.9 (ประกัน 1 ปี)"),
        (1, s4 + 0.1, s4 + d4, "SubMain", r"{\pos(540,1385)\fs44}กดตะกร้าเหลือง หรือลิงก์หน้าโปรไฟล์ เบอร์ #03"),
        (3, s4 + 0.1, s4 + d4, "CtaDark", r"{\pos(540,1533)}กดตะกร้าเหลือง / ลิงก์ Bio #03"),
    ]


def update_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        existing = json.load(f)
    existing_ids = {x["id"] for x in existing}
    tiktok_items = [
        {
            "id": "tt01_cctv",
            "title": "[TikTok] คลิป #01: กล้องวงจรปิดใส่ซิม 4G เลนส์คู่",
            "filename": "tiktok_01_cctv_4g.mp4",
            "price": "฿351",
            "commission": "TikTok ตะกร้าเหลือง / ลิงก์ Bio #01",
            "note": "เวอร์ชัน TikTok พูดว่า 'กดตะกร้าเหลือง / ลิงก์หน้าโปรไฟล์ เบอร์ #01' • ปักตะกร้าเหลืองสินค้า 'กล้องวงจรปิด 4G เลนส์คู่'",
            "caption": "ไม่มี Wi-Fi ก็ติดกล้องดูสวนได้! ใส่ซิม 4G เลนส์คู่ กันน้ำ IP67 ภาพสีกลางคืน กดตะกร้าเหลืองหรือลิงก์ Bio #01 #กล้องวงจรปิด #กล้อง4G #รีวิวของดี",
            "affiliate_link": "https://s.shopee.co.th/1qdorlaqMK",
            "product_link": "https://shopee.co.th/product/1256676370/26553605811"
        },
        {
            "id": "tt02_antiant",
            "title": "[TikTok] คลิป #02: เจลกำจัดมด ANTIANT",
            "filename": "tiktok_02_antiant_89.mp4",
            "price": "฿89",
            "commission": "TikTok ตะกร้าเหลือง / ลิงก์ Bio #02",
            "note": "เวอร์ชัน TikTok พูดว่า 'กดตะกร้าเหลือง / ลิงก์หน้าโปรไฟล์ เบอร์ #02' • ปักตะกร้าเหลืองสินค้า 'เจลกำจัดมด Antiant'",
            "caption": "มดขึ้นครัวฉีดสเปรย์ไม่หาย ลองเจลหยดล่อมด Antiant คาบกลับไปตายทั้งรังใน 2-3 วัน กดตะกร้าเหลืองหรือลิงก์ Bio #02 #กำจัดมด #ของใช้ในบ้าน #ป้ายยา",
            "affiliate_link": "https://s.shopee.co.th/AKcMzPQ9Dp",
            "product_link": "https://shopee.co.th/product/253175829/21685245804"
        },
        {
            "id": "tt03_zinsano",
            "title": "[TikTok] คลิป #03: ZINSANO เครื่องฉีดน้ำ 120 บาร์",
            "filename": "tiktok_03_zinsano_120bar.mp4",
            "price": "฿2,590",
            "commission": "TikTok ตะกร้าเหลือง / ลิงก์ Bio #03",
            "note": "เวอร์ชัน TikTok พูดว่า 'กดตะกร้าเหลือง / ลิงก์หน้าโปรไฟล์ เบอร์ #03' • ปักตะกร้าเหลืองสินค้า 'ZINSANO AMAZON ULTRA'",
            "caption": "คราบตะไคร่หน้าบ้านฉีดทีเดียวขาว! ZINSANO 120 บาร์ ล้างรถ ล้างพื้น ประกัน 1 ปี กดตะกร้าเหลืองหรือลิงก์ Bio #03 #เครื่องฉีดน้ำแรงดันสูง #ล้างรถ",
            "affiliate_link": "https://s.shopee.co.th/40iJRTvOLr",
            "product_link": "https://shopee.co.th/product/1103002459/25653050667"
        },
    ]
    merged = [x for x in tiktok_items if x["id"] not in existing_ids] + existing
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print("Updated manifest.json with 3 TikTok videos!")


def main():
    asyncio.run(gen_tts_files())
    configs = [
        {
            "out_name": "tiktok_01_cctv_4g.mp4",
            "tmp_dir": os.path.join(VID_DIR, "tmp"),
            "mp3s": [
                os.path.join(VID_DIR, "tmp", "scene1.mp3"),
                os.path.join(VID_DIR, "tmp", "scene2.mp3"),
                os.path.join(VID_DIR, "tmp", "scene3.mp3"),
                os.path.join(VID_DIR, "tmp", "scene4_tt.mp3"),
            ],
            "bgm": os.path.join(VID_DIR, "tmp", "bgm.wav"),
            "xfade": 0.35,
            "pill_y0": 1485,
            "pill_y1": 1590,
            "build_events": ev_cctv,
        },
        {
            "out_name": "tiktok_02_antiant_89.mp4",
            "tmp_dir": os.path.join(VID_DIR, "tmp_v2"),
            "mp3s": [
                os.path.join(VID_DIR, "tmp_v2", "v2_s1.mp3"),
                os.path.join(VID_DIR, "tmp_v2", "v2_s2.mp3"),
                os.path.join(VID_DIR, "tmp_v2", "v2_s3.mp3"),
                os.path.join(VID_DIR, "tmp_v2", "v2_s4_tt.mp3"),
            ],
            "bgm": os.path.join(VID_DIR, "tmp_v2", "bgm_v2.wav"),
            "xfade": 0.32,
            "pill_y0": 1480,
            "pill_y1": 1585,
            "build_events": ev_antiant,
        },
        {
            "out_name": "tiktok_03_zinsano_120bar.mp4",
            "tmp_dir": os.path.join(VID_DIR, "tmp_v3"),
            "mp3s": [
                os.path.join(VID_DIR, "tmp_v3", "v3_s1.mp3"),
                os.path.join(VID_DIR, "tmp_v3", "v3_s2.mp3"),
                os.path.join(VID_DIR, "tmp_v3", "v3_s3.mp3"),
                os.path.join(VID_DIR, "tmp_v3", "v3_s4_tt.mp3"),
            ],
            "bgm": os.path.join(VID_DIR, "tmp_v3", "bgm_v3.wav"),
            "xfade": 0.32,
            "pill_y0": 1480,
            "pill_y1": 1585,
            "build_events": ev_zinsano,
        },
    ]
    for cfg in configs:
        build_tiktok_video(cfg)
    update_manifest()


if __name__ == "__main__":
    main()
