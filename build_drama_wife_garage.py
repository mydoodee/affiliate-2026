import json
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFilter
from google import genai
from google.genai import errors, types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

sys.path.insert(0, r"d:\9.Code\shopee_ai")
from build_live_drama_omni import (
    MANIFEST_PATH,
    MODEL,
    VID_DIR,
    load_api_key,
    probe_duration,
    run_omni_interaction,
    sanitize_err,
    upload_and_wait,
)

OMNI_DIR = os.path.join(VID_DIR, "omni_drama_03")
os.makedirs(OMNI_DIR, exist_ok=True)

HERO_REF_IMG = os.path.join(VID_DIR, "omni_drama_02", "hero_safe_glam.jpg")
MECH_REF_IMG = os.path.join(VID_DIR, "omni_drama_02", "t1_f4.jpg")
BLANC_REAL_PNG = os.path.join(VID_DIR, "omni_drama_02", "blanc_real.png")
ENDCARD_BG = os.path.join(OMNI_DIR, "endcard_bg.png")


def build_endcard_bg():
    im = Image.open(BLANC_REAL_PNG).convert("RGB")
    W, H = 1080, 1920
    canvas = Image.new("RGB", (W, H), (250, 249, 247))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, W, 470], fill=(240, 78, 35))

    card_x0, card_y0, card_x1, card_y1 = 150, 410, 930, 1190
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [card_x0 + 6, card_y0 + 16, card_x1 + 6, card_y1 + 16],
        radius=44,
        fill=(0, 0, 0, 38),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=44, fill=(255, 255, 255))

    prod_sq = im.resize((716, 716), Image.Resampling.LANCZOS)
    mask = Image.new("L", (716, 716), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 716, 716], radius=32, fill=255)
    canvas.paste(prod_sq, (card_x0 + 32, card_y0 + 32), mask)

    draw.rounded_rectangle([120, 1245, 960, 1415], radius=32, fill=(255, 255, 255), outline=(252, 210, 195), width=4)
    draw.rounded_rectangle([150, 1525, 930, 1645], radius=60, fill=(240, 78, 35))
    canvas.save(ENDCARD_BG, "PNG")


def build_endcard_clip(out_path: str, duration: float = 3.5):
    build_endcard_bg()
    ass_path = os.path.join(OMNI_DIR, "endcard_wife.ass")
    dur_ts = f"0:00:0{duration:.2f}"
    ass_text = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EndHeader,Leelawadee UI,62,&H00FFFFFF,&H00FFFFFF,&H00182448,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,8,60,60,185,1
Style: BrandBig,Leelawadee UI,54,&H00234EF0,&H00234EF0,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: SubDark,Leelawadee UI,40,&H00333333,&H00333333,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: TagWhite,Leelawadee UI,44,&H00FFFFFF,&H00FFFFFF,&H00112266,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 2,0:00:00.00,{dur_ts},EndHeader,,0,0,0,,หน้าใสจนเมียจำได้!\\N{{\\c&H00BBEEFF&}}เคล็ดลับผิวเนียนของนางฟ้า
Dialogue: 3,0:00:00.00,{dur_ts},BrandBig,,0,0,0,,{{\\pos(540,1300)}}Blanc Nature Pore Ampoule
Dialogue: 1,0:00:00.00,{dur_ts},SubDark,,0,0,0,,{{\\pos(540,1372)}}15% Niacinamide • กระชับรูขุมขน คุมมัน (★ 4.9)
Dialogue: 3,0:00:00.00,{dur_ts},TagWhite,,0,0,0,,{{\\pos(540,1585)}}ของแท้ขายดี 40,000+ ขวด • เบอร์ #09
"""
    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(ass_text)
    ass_esc = ass_path.replace("\\", "/").replace(":", "\\:")
    subprocess.check_call([
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-i", ENDCARD_BG,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vf", f"scale=1080:1920,ass='{ass_esc}',format=yuv420p",
        "-t", str(duration), "-r", "30",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-shortest", out_path,
    ])


def update_manifest():
    items = []
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            items = json.load(f)
    new_item = {
        "id": "omni_drama03_wife_garage",
        "title": "[ละครตลกหักมุมซ้ำ! นั่นเมียมึง + ทวงหนี้เพื่อนช่าง!] #09 Blanc Nature",
        "filename": "drama_live_03_wife_garage.mp4",
        "price": "฿590",
        "commission": "คอม Shopee Video 15% (฿88.50/ขวด) • ขายแล้ว 40k+",
        "note": "ละครตลกอู่ซ่อมรถล้วนๆ ไม่มีขายของในบท (ขึ้นป้าย Blanc Nature ตอนท้ายคลีนๆ) เหมาะสุดสำหรับปั่นยอดวิว TikTok / FB Reels / Shopee Video!",
        "caption": "วิ่งออกไปดูนางฟ้าหน้าอู่... สรุปซวยยกแก๊ง! 😂 หักมุมสองชั้น #คลิปตลก #ละครสั้น #อู่ซ่อมรถ #09 #BlancNature",
        "affiliate_link": "https://s.shopee.co.th/4LL9qFcocB",
        "product_link": "https://shopee.co.th/product/1333923052/29761544584",
    }
    items = [new_item] + [x for x in items if x["id"] != new_item["id"]]
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def transcribe_audio(client: genai.Client, mp4_path: str, tag: str) -> str:
    mp3 = os.path.join(OMNI_DIR, f"qa_{tag}.mp3")
    subprocess.check_call([
        "ffmpeg", "-y", "-v", "error", "-i", mp4_path,
        "-vn", "-ac", "1", "-ar", "16000", mp3,
    ])
    with open(mp3, "rb") as f:
        b = f.read()
    r = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            types.Part.from_bytes(data=b, mime_type="audio/mp3"),
            "Transcribe every spoken Thai line with exact [start_sec - end_sec] timestamps (to 0.1s) and explicitly note whether ANY word is cut off or abruptly silenced.",
        ],
    )
    print(f"\n--- AUDIO QA ({tag}) ---")
    print(r.text)
    return r.text


def main():
    key = load_api_key()
    client = genai.Client(
        api_key=key,
        http_options=types.HttpOptions(api_version="v1beta", timeout=300 * 1000),
    )

    try:
        u_hero, m_hero = upload_and_wait(client, HERO_REF_IMG)
        u_mech, m_mech = upload_and_wait(client, MECH_REF_IMG)

        # PART 1 (15s): Scene 1 (Angel walks past) + Scene 2 (4 mechanics rush out) + Scene 3 ("That's your wife!")
        prompt_p1 = (
            "Use the first image as the starting frame of the smiling Thai woman walking past the sunlit 'AUTO SERVICE' garage, "
            "and use the second image as the character reference for the four cheerful young Thai male mechanics in matching navy-blue shop uniforms inside the same garage. "
            "Pure lighthearted Thai TV sitcom comedy, no product bottle shown. "
            "[0-4.5s] Starting smoothly from the first image, the smiling Thai woman in the white off-shoulder top and denim shorts walks gracefully in slow-motion past the sunny garage entrance with breezy hair and dreamy romantic music. Inside the garage, Mechanic 1 pauses fixing a car, drops his wrench playfully with a metallic clang, and calls out in lively natural Bangkok Thai with clear lip-sync: "
            "\"เฮ้ย! หยุดก่อน! นางฟ้ามา!\" "
            "[4.5-9.0s] Quick fun cut: the four young Thai mechanics in navy uniforms hurry enthusiastically to the garage entrance, crowding together comically with wide amazed eyes. Mechanic 2 exclaims in natural Thai: "
            "\"โอ้โห! คนอะไรสวยขนาดนี้!\" "
            "Mechanic 3 whispers playfully in Thai: "
            "\"เบาๆ สิ เดี๋ยวเขาได้ยิน!\" "
            "[9.0-13.6s] Mechanic 1 fixes his hair with a proud goofy grin, stepping forward to say hello. Suddenly Mechanic 4 beside him blinks in comic realization, taps Mechanic 1's shoulder urgently, and says in surprised Thai: "
            "\"ซวยแล้วพวกเรา... นั่นเมียพี่นี่หว่า!\" "
            "[13.6-15.0s] Funny comedic close-up of Mechanic 1 freezing with wide comical cartoon-like surprised eyes as a playful sitcom sting sound plays. No spoken words in the final 1.4 seconds. No on-screen text, no captions, no watermarks."
        )

        inter1 = run_omni_interaction(
            client,
            "Part 1 (15s): Angel Walks Past -> Mechanics Rush -> That's Your Wife!",
            model=MODEL,
            input=[
                {"type": "image", "uri": u_hero, "mime_type": m_hero},
                {"type": "image", "uri": u_mech, "mime_type": m_mech},
                {"type": "text", "text": prompt_p1},
            ],
            response_format={
                "type": "video",
                "delivery": "uri",
                "aspect_ratio": "9:16",
                "resolution": "720p",
                "duration": "15s",
            },
        )
        out1 = inter1.output_video
        if not out1 or not out1.uri:
            raise RuntimeError("Part 1 returned no output_video URI")
        p1_path = os.path.join(OMNI_DIR, "wife_p1_15s.mp4")
        with open(p1_path, "wb") as f:
            f.write(client.files.download(file=out1.uri))
        dur1 = probe_duration(p1_path)
        print(f"Saved Part 1: {p1_path} ({os.path.getsize(p1_path)/(1024*1024):.2f} MB, {dur1:.2f}s)")
        transcribe_audio(client, p1_path, "p1")

        # Extract exact end frame of Part 1 (t=14.3s) + safe upper-body portrait of woman from Part 1 (t=1.2s)
        p1_end_frame = os.path.join(OMNI_DIR, "p1_end_frame.jpg")
        p1_woman_frame = os.path.join(OMNI_DIR, "p1_woman_raw.jpg")
        p1_woman_upper = os.path.join(OMNI_DIR, "p1_woman_upper.jpg")
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-ss", "14.3", "-i", p1_path,
            "-frames:v", "1", "-q:v", "2", p1_end_frame,
        ])
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-ss", "1.2", "-i", p1_path,
            "-frames:v", "1", "-q:v", "2", p1_woman_frame,
        ])
        imw = Image.open(p1_woman_frame).convert("RGB")
        ww, wh = imw.size
        imw.crop((0, int(wh * 0.06), ww, int(wh * 0.62))).save(p1_woman_upper, "JPEG", quality=95)

        u_p1end, m_p1end = upload_and_wait(client, p1_end_frame)
        u_wup, m_wup = upload_and_wait(client, p1_woman_upper)

        # PART 2 (15s): Scene 4 (Hide & point!) + Scene 5 (Double twist: debt collection!)
        prompt_p2 = (
            "Use the first image as the starting frame inside the sunlit Thai auto repair garage, "
            "use the second image as the character reference for the four navy-uniformed Thai mechanics, "
            "and use the third image as the character reference for the smiling Thai wife in the white off-shoulder top. "
            "Pure lighthearted Thai TV sitcom comedy, no product bottle shown. "
            "[0-5.2s] Starting from the first image, funny sitcom slapstick begins: the four mechanics comically hurry back inside the garage—one pretends to check a car tire, one ducks down to tie his shoe, and Mechanic 1 hilariously crouches behind a stack of rubber tires. The smiling Thai wife from the third image strolls casually into the garage entrance with hands on her hips and asks sweetly in crisp natural Thai: "
            "\"พี่คะ เห็นสามีหนูไหมคะ?\" "
            "Instantly, all three mechanic friends freeze and point straight at Mechanic 1 hiding behind the tires in unison! "
            "[5.2-8.8s] The wife walks over to Mechanic 1 behind the tires with an amused teasing smile and says cheerfully in Thai: "
            "\"กลับบ้านค่ะ!\" "
            "Mechanic 1 immediately stands up grinning sheepishly and answers sweetly in Thai: "
            "\"จ๋าาา... ที่รัก\" "
            "[8.8-13.5s] Funny double twist: the wife turns to the three mechanic friends with a bright playful smile and speaks clear natural Thai: "
            "\"ส่วนพวกพี่ เงินที่ยืมสามีหนูไป คืนด้วยนะคะ!\" "
            "The three mechanics freeze with funny surprised faces; Mechanic 2 exclaims in lively Thai: "
            "\"อ้าว! พวกเราซวยด้วยเหรอเนี่ย!\" "
            "[13.5-15.0s] All three mechanics laughingly jog away inside the garage while the wife chuckles and upbeat Thai sitcom comedy music resolves happily. No spoken words in the final 1.5 seconds. No on-screen text, no captions, no watermarks."
        )

        inter2 = run_omni_interaction(
            client,
            "Part 2 (15s): Hide & Betray -> Go Home -> Pay Back Borrowed Money Twist!",
            model=MODEL,
            input=[
                {"type": "image", "uri": u_p1end, "mime_type": m_p1end},
                {"type": "image", "uri": u_mech, "mime_type": m_mech},
                {"type": "image", "uri": u_wup, "mime_type": m_wup},
                {"type": "text", "text": prompt_p2},
            ],
            response_format={
                "type": "video",
                "delivery": "uri",
                "aspect_ratio": "9:16",
                "resolution": "720p",
                "duration": "15s",
            },
        )
        out2 = inter2.output_video
        if not out2 or not out2.uri:
            raise RuntimeError("Part 2 returned no output_video URI")
        p2_path = os.path.join(OMNI_DIR, "wife_p2_15s.mp4")
        with open(p2_path, "wb") as f:
            f.write(client.files.download(file=out2.uri))
        dur2 = probe_duration(p2_path)
        print(f"Saved Part 2: {p2_path} ({os.path.getsize(p2_path)/(1024*1024):.2f} MB, {dur2:.2f}s)")
        transcribe_audio(client, p2_path, "p2")

        # Normalize Part 1 + Part 2 to 1080x1920 30fps stereo + smooth splice + 3.5s clean Blanc Nature End-Card
        n1 = os.path.join(OMNI_DIR, "n1.mp4")
        n2 = os.path.join(OMNI_DIR, "n2.mp4")
        for src, dst in [(p1_path, n1), (p2_path, n2)]:
            subprocess.check_call([
                "ffmpeg", "-y", "-v", "error", "-i", src,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                dst,
            ])

        d_n1 = probe_duration(n1)
        spliced = os.path.join(OMNI_DIR, "spliced.mp4")
        off_12 = round(d_n1 - 0.12, 3)
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error",
            "-i", n1, "-i", n2,
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration=0.12:offset={off_12},format=yuv420p[vout];"
            f"[0:a][1:a]acrossfade=d=0.12[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            spliced,
        ])

        d_sp = probe_duration(spliced)
        endcard_path = os.path.join(OMNI_DIR, "endcard.mp4")
        build_endcard_clip(endcard_path, duration=3.5)

        final_mp4 = os.path.join(VID_DIR, "drama_live_03_wife_garage.mp4")
        off_end = round(d_sp - 0.35, 3)
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error",
            "-i", spliced, "-i", endcard_path,
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration=0.35:offset={off_end},format=yuv420p[vout];"
            f"[0:a][1:a]acrossfade=d=0.35[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "30",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-movflags", "+faststart",
            final_mp4,
        ])

        transcribe_audio(client, final_mp4, "final")

        final_dur = probe_duration(final_mp4)
        for idx, frac in enumerate([0.06, 0.25, 0.42, 0.56, 0.72, 0.84, 0.95]):
            t = round(final_dur * frac, 2)
            subprocess.check_call([
                "ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", final_mp4,
                "-frames:v", "1", "-q:v", "3", os.path.join(OMNI_DIR, f"qa_{idx+1}.jpg"),
            ])

        update_manifest()
        print(
            f"\nSUCCESS! Final Wife-Twist Garage Comedy: {final_mp4} "
            f"({os.path.getsize(final_mp4)/(1024*1024):.2f} MB, {final_dur:.2f}s)"
        )
    except errors.APIError as e:
        print("API_ERROR:", sanitize_err(e, key), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("ERROR:", sanitize_err(e, key), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
