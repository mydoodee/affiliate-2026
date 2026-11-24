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
    BASE_DIR,
    MANIFEST_PATH,
    MODEL,
    VID_DIR,
    load_api_key,
    probe_duration,
    run_omni_interaction,
    sanitize_err,
    upload_and_wait,
)

OMNI_DIR = os.path.join(VID_DIR, "omni_drama_02")
os.makedirs(OMNI_DIR, exist_ok=True)

HERO_REF_IMG = os.path.join(OMNI_DIR, "hero_safe_glam.jpg")
BLANC_REAL_PNG = os.path.join(OMNI_DIR, "blanc_real.png")
BLANC_BOTTLE_CROP = os.path.join(OMNI_DIR, "blanc_bottle_crop.png")
ENDCARD_BG = os.path.join(OMNI_DIR, "endcard_bg.png")


def prepare_assets():
    # 1. Clean crop of ONLY the frosted white Blanc Nature pump bottle (no promo text)
    im = Image.open(BLANC_REAL_PNG).convert("RGB")
    bottle = im.crop((650, 145, 985, 705))
    bottle.save(BLANC_BOTTLE_CROP, "PNG")
    print(f"Saved clean bottle ref: {BLANC_BOTTLE_CROP} ({bottle.size})")

    # 2. Build crisp 1080x1920 White-Orange End-Card background with real product photo
    W, H = 1080, 1920
    canvas = Image.new("RGB", (W, H), (250, 249, 247))
    draw = ImageDraw.Draw(canvas)

    # Top warm orange header band
    draw.rectangle([0, 0, W, 470], fill=(240, 78, 35))

    # Subtle drop shadow + white rounded card holding real 1024x1024 Blanc Nature photo
    card_x0, card_y0, card_x1, card_y1 = 150, 410, 930, 1190
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([card_x0 + 6, card_y0 + 16, card_x1 + 6, card_y1 + 16], radius=44, fill=(0, 0, 0, 38))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=44, fill=(255, 255, 255))

    prod_sq = im.resize((716, 716), Image.Resampling.LANCZOS)
    mask = Image.new("L", (716, 716), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 716, 716], radius=32, fill=255)
    canvas.paste(prod_sq, (card_x0 + 32, card_y0 + 32), mask)

    # Clean info card pill below photo
    draw.rounded_rectangle([120, 1245, 960, 1415], radius=32, fill=(255, 255, 255), outline=(252, 210, 195), width=4)
    # Soft subtle bottom pill (non-salesy, funny tag)
    draw.rounded_rectangle([150, 1525, 930, 1645], radius=60, fill=(240, 78, 35))

    canvas.save(ENDCARD_BG, "PNG")
    print(f"Saved End-Card background: {ENDCARD_BG}")


def build_endcard_clip(out_path: str, duration: float = 3.5):
    ass_path = os.path.join(OMNI_DIR, "endcard_blanc.ass")
    dur_ts = f"0:00:0{duration:.2f}"
    ass_text = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EndHeader,Leelawadee UI,64,&H00FFFFFF,&H00FFFFFF,&H00182448,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,8,60,60,185,1
Style: BrandBig,Leelawadee UI,54,&H00234EF0,&H00234EF0,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: SubDark,Leelawadee UI,40,&H00333333,&H00333333,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: TagWhite,Leelawadee UI,44,&H00FFFFFF,&H00FFFFFF,&H00112266,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 2,0:00:00.00,{dur_ts},EndHeader,,0,0,0,,อู่ซ่อมรถ...\\N{{\\c&H00BBEEFF&}}แต่ช่างซ่อมหน้า!
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
        "id": "omni_drama02_blanc_garage",
        "title": "[ละครตลกหักมุม! อู่ซ่อมรถแต่ช่างซ่อมหน้า] #09 Blanc Nature เซรั่มรูขุมขน",
        "filename": "drama_live_02_blanc_garage.mp4",
        "price": "฿590",
        "commission": "คอม Shopee Video 15% (฿88.50/ขวด) • ขายแล้ว 40k+",
        "note": "ละครตลกหักมุมไม่ฮาร์ดเซล (เจนด้วย Gemini Omni 1.2 Flash) นางฟ้าหน้าอู่ + แก๊งช่าง 5 คน • ใช้ได้ทั้ง TikTok, Shopee Video, FB Reels!",
        "caption": "อู่ซ่อมรถ... แต่ช่างซ่อมหน้า! 😂 นี่คนหรือฝากระโปรงเคลือบแก้ว ✨ #09 #BlancNature #เซรั่มรูขุมขน #คลิปตลก #รีวิวของดี",
        "affiliate_link": "https://s.shopee.co.th/4LL9qFcocB",
        "product_link": "https://shopee.co.th/product/1333923052/29761544584",
    }
    items = [new_item] + [x for x in items if x["id"] != new_item["id"]]
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def main():
    prepare_assets()
    key = load_api_key()
    client = genai.Client(
        api_key=key,
        http_options=types.HttpOptions(api_version="v1beta", timeout=300 * 1000),
    )

    try:
        u1, m1 = upload_and_wait(client, HERO_REF_IMG)
        u2, m2 = upload_and_wait(client, BLANC_BOTTLE_CROP)

        prompt_turn1 = (
            "Use the first image as the starting frame, and use the second image as the product reference for the frosted white skincare pump bottle with green text 'Blanc Nature'. "
            "Create a hilarious, cinematic 15-second Thai vertical comedy short film in the same bright sunlit Bangkok auto repair garage with the blue 'AUTO SERVICE' sign and red tool chest. "
            "[0-4.5s] Starting smoothly from the first image, the gorgeous smiling Thai woman in the chic fitted white off-shoulder ribbed top and high-waisted denim shorts walks confidently in breezy slow-motion past the open auto garage, sunlight glowing off her porcelain smooth skin and flowing hair, accompanied by dreamy heavenly romantic music. Suddenly a record-scratch stops the music as the Thai mechanic in navy uniform working under the white car hood freezes, drops his metal wrench onto the concrete with a loud clang, and shouts in lively natural Bangkok Thai with clear lip-sync: "
            "\"เฮ้ย! หยุดซ่อมก่อน นางฟ้ามาเว้ย!\" "
            "[4.5-9.5s] Quick energetic comedic cut inside the garage: 4 to 5 cheerful young Thai male mechanics in matching navy-blue shop uniforms drop their tools and scramble excitedly to the garage entrance, crowding together comically (one nearly tips off a stool, another bumps the doorframe) staring wide-eyed at her. Mechanic 2 points in pure awe and speaks lively natural Thai with clear lip-sync: "
            "\"โห... ดูผิวเขาดิ นี่คนหรือฝากระโปรงเคลือบแก้ววะ!\" "
            "[9.5-13.6s] Punchy comedy close-up on the mechanics: Mechanic 2 squints intensely asking seriously in Thai: "
            "\"ผิวแบบนี้ ใช้ฟิลเตอร์อะไรวะ?\" "
            "Mechanic 3 beside him replies deadpan in crisp Thai with clear lip-sync: "
            "\"ฟิลเตอร์ที่ไหนเล่า นี่ของจริง!\" "
            "[13.6-15s] All the other mechanics whip their heads toward Mechanic 3 with dramatic shocked faces and a comical sting sound. No spoken words in the final 1.4 seconds. No on-screen text, no captions, no watermarks."
        )

        inter1 = run_omni_interaction(
            client,
            "Turn 1: 15s 9:16 720p Thai Garage Comedy Twist",
            model=MODEL,
            input=[
                {"type": "image", "uri": u1, "mime_type": m1},
                {"type": "image", "uri": u2, "mime_type": m2},
                {"type": "text", "text": prompt_turn1},
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
            raise RuntimeError("Turn 1 returned no output_video URI")
        part1_path = os.path.join(OMNI_DIR, "omni_t1.mp4")
        with open(part1_path, "wb") as f:
            f.write(client.files.download(file=out1.uri))
        dur1 = probe_duration(part1_path)
        print(f"Saved Turn 1: {part1_path} ({os.path.getsize(part1_path)/(1024*1024):.2f} MB, {dur1:.2f}s)")

        prompt_turn2 = (
            "Extend this comedy video seamlessly for 10 seconds in the same sunlit Bangkok auto repair garage. "
            "[0-4.8s] Dramatic comedic reveal: Mechanic 3 slowly pulls the exact frosted white glass pump bottle with green 'Blanc Nature' label (from the reference image) out of his navy mechanic shirt pocket, shining a bright mechanic flashlight onto the bottle like unveiling a luxury supercar part, grinning proudly as he speaks clear natural Bangkok Thai with clear lip-sync: "
            "\"แบลงก์ เนเจอร์ ไนอะซินาไมด์ สิบห้าเปอร์เซ็นต์... ซ่อมหน้าก่อน เครื่องยนต์ค่อยว่ากัน!\" "
            "The other mechanics behind him gasp together in unison: \"โหหหห!\" "
            "[4.8-8.4s] Quick playful cut to the gorgeous smiling Thai woman from the beginning standing outside the garage, glancing playfully at the camera and holding up the exact frosted white Blanc Nature pump bottle casually beside her flawless glowing cheek, speaking naturally and charmingly (not like a pushy ad): "
            "\"เคล็ดลับก็ขวดนี้แหละค่ะ!\" "
            "Instantly, Mechanic 4 pops his grinning head right into the side of the frame holding a grease rag and says eagerly in funny Thai: "
            "\"พี่ครับ! ขอเบิกเป็นค่าอะไหล่ประจำเดือนด้วยครับ!\" "
            "[8.4-10s] The woman and all the mechanics burst out laughing and give enthusiastic thumbs-up together as upbeat playful Thai comedy music resolves cleanly. No spoken words in the final 1.6 seconds. No on-screen text, no captions, no watermarks."
        )

        inter2 = run_omni_interaction(
            client,
            "Turn 2: Extend +10s Blanc Nature Reveal & Mechanic Punchline",
            model=MODEL,
            previous_interaction_id=inter1.id,
            input=[
                {"type": "image", "uri": u2, "mime_type": m2},
                {"type": "text", "text": prompt_turn2},
            ],
            response_format={
                "type": "video",
                "delivery": "uri",
                "aspect_ratio": "9:16",
                "resolution": "720p",
                "duration": "10s",
            },
        )
        out2 = inter2.output_video
        if not out2 or not out2.uri:
            raise RuntimeError("Turn 2 returned no output_video URI")
        part2_path = os.path.join(OMNI_DIR, "omni_t2.mp4")
        with open(part2_path, "wb") as f:
            f.write(client.files.download(file=out2.uri))
        dur2 = probe_duration(part2_path)
        print(f"Saved Turn 2: {part2_path} ({os.path.getsize(part2_path)/(1024*1024):.2f} MB, {dur2:.2f}s)")

        # Normalize live video (25s) to 1080x1920 30fps stereo
        norm_omni = os.path.join(OMNI_DIR, "omni_norm.mp4")
        src_full = part2_path if dur2 >= dur1 + 3.0 else part1_path
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-i", src_full,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            norm_omni,
        ])

        dur_omni = probe_duration(norm_omni)
        endcard_path = os.path.join(OMNI_DIR, "endcard.mp4")
        build_endcard_clip(endcard_path, duration=3.5)

        final_mp4 = os.path.join(VID_DIR, "drama_live_02_blanc_garage.mp4")
        off_end = max(1.0, round(dur_omni - 0.35, 3))
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error",
            "-i", norm_omni, "-i", endcard_path,
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration=0.35:offset={off_end},format=yuv420p[vout];"
            f"[0:a][1:a]acrossfade=d=0.35[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "30",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-movflags", "+faststart",
            final_mp4,
        ])

        # Automatic Audio QA Transcription
        qa_mp3 = os.path.join(OMNI_DIR, "qa_audio.mp3")
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-i", final_mp4,
            "-vn", "-ac", "1", "-ar", "16000", qa_mp3,
        ])
        with open(qa_mp3, "rb") as af:
            audio_bytes = af.read()
        tr = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3"),
                "Transcribe every spoken Thai line in this comedy video with exact [start_sec - end_sec] timestamps and speaker, and explicitly report if ANY word is cut off, garbled, or abruptly silenced.",
            ],
        )
        print("\n--- AUDIO QA TRANSCRIPT ---")
        print(tr.text)

        # Extract 6 QA frames
        final_dur = probe_duration(final_mp4)
        for idx, frac in enumerate([0.05, 0.25, 0.45, 0.62, 0.78, 0.94]):
            t = round(final_dur * frac, 2)
            subprocess.check_call([
                "ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", final_mp4,
                "-frames:v", "1", "-q:v", "3", os.path.join(OMNI_DIR, f"qa_{idx+1}.jpg"),
            ])

        update_manifest()
        print(
            f"\nSUCCESS! Final Garage Comedy Drama: {final_mp4} "
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
