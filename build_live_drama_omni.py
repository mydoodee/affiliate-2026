import json
import os
import re
import subprocess
import sys
import time
from google import genai
from google.genai import errors, types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

BASE_DIR = r"d:\9.Code\shopee_ai"
VID_DIR = os.path.join(BASE_DIR, "videos")
OMNI_DIR = os.path.join(VID_DIR, "omni_drama_01")
MANIFEST_PATH = os.path.join(VID_DIR, "manifest.json")
os.makedirs(OMNI_DIR, exist_ok=True)

S1_IMG = os.path.join(BASE_DIR, "kling_kit_seagull", "01_scene1_husband.jpg")
S2_IMG = os.path.join(BASE_DIR, "kling_kit_seagull", "02_scene2_wife_pour.jpg")
S3_IMG = os.path.join(BASE_DIR, "kling_kit_seagull", "03_scene3_soymilk_pour.jpg")
REAL_PROD = os.path.join(VID_DIR, "drama_01", "seagull_real.webp")
ENDCARD_BG = os.path.join(VID_DIR, "drama_01", "bg5.png")

MODEL = "gemini-omni-1.2-flash"


def load_api_key() -> str:
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):].strip()
                if line.startswith("GEMINI_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        os.environ["GEMINI_API_KEY"] = val
                        return val
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"].strip()
    raise RuntimeError("GEMINI_API_KEY not found in .env or environment")


def sanitize_err(err: Exception, key: str) -> str:
    s = str(err)
    if key and len(key) >= 8:
        s = s.replace(key, "[REDACTED]")
    s = re.sub(r"AIza[0-9A-Za-z_\-]{25,}", "[REDACTED]", s)
    s = re.sub(r"AQ\.[0-9A-Za-z_\-]{20,}", "[REDACTED]", s)
    return s[:700]


def upload_and_wait(client: genai.Client, path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing required asset: {path}")
    print(f"Uploading {os.path.basename(path)}...")
    f = client.files.upload(file=path)
    name = f.name
    for _ in range(60):
        info = client.files.get(name=name)
        state = getattr(info.state, "name", str(info.state)).upper()
        if state == "ACTIVE":
            uri = (
                f"https://generativelanguage.googleapis.com/{name}"
                if not str(info.uri).startswith("http")
                else info.uri.split("?")[0]
            )
            mime = info.mime_type or "image/jpeg"
            print(f"  ACTIVE: {name} ({mime})")
            return uri, mime
        if state == "FAILED":
            raise RuntimeError(f"File processing failed: {name}")
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for file {name}")


def run_omni_interaction(client: genai.Client, label: str, **kwargs):
    """Run interactions.create in background mode and poll until completed/failed."""
    print(f"\n=== {label} ===")
    inter = client.interactions.create(background=True, **kwargs)
    inter_id = inter.id
    status = getattr(inter, "status", "unknown")
    print(f"  Started interaction_id={inter_id} | initial status={status}")
    t0 = time.time()
    max_wait = 900  # 15 minutes max per turn
    while True:
        status_str = str(getattr(inter, "status", "")).lower()
        elapsed = int(time.time() - t0)
        if status_str in ("completed", "complete", "succeeded"):
            print(f"  COMPLETED in {elapsed}s! (id={inter_id})")
            return inter
        if status_str in ("failed", "cancelled", "canceled", "expired"):
            err_obj = getattr(inter, "errors", None) or getattr(inter, "error", None)
            raise RuntimeError(f"{label} failed after {elapsed}s (status={status_str}): {err_obj}")
        if elapsed >= max_wait:
            raise TimeoutError(f"{label} timed out after {elapsed}s (last status={status_str})")
        time.sleep(5)
        inter = client.interactions.get(id=inter_id)
        if elapsed % 15 < 5:
            print(f"  [{elapsed}s] status={getattr(inter, 'status', 'unknown')}...")


def probe_duration(path: str) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        text=True,
    ).strip()
    return float(out)


def build_endcard_clip(out_path: str, duration: float = 3.8):
    """Build a crisp 1080x1920 White-Orange Seagull CTA end-card matching the live video."""
    ass_path = os.path.join(OMNI_DIR, "endcard.ass")
    dur_ts = f"0:00:0{duration:.2f}"
    ass_text = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EndHeader,Leelawadee UI,60,&H00FFFFFF,&H00FFFFFF,&H001A2A55,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,8,60,60,210,1
Style: PriceBig,Leelawadee UI,78,&H00234EF0,&H00234EF0,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: SubDark,Leelawadee UI,44,&H00222222,&H00222222,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: CtaWhite,Leelawadee UI,46,&H00FFFFFF,&H00FFFFFF,&H00112266,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 2,0:00:00.00,{dur_ts},EndHeader,,0,0,0,,Seagull เครื่องทำน้ำเต้าหู้ 1.2L\\N{{\\c&H00AAEEFF&}}รุ่น 8 in 1 (สีครีม)
Dialogue: 3,0:00:00.00,{dur_ts},PriceBig,,0,0,0,,{{\\pos(540,1220)}}฿1,287 {{\\fs42\\c&H00444444&}}| ★ 4.9 (ขายแล้ว 30k+)
Dialogue: 1,0:00:00.00,{dur_ts},SubDark,,0,0,0,,{{\\pos(540,1375)}}แบรนด์นกนางนวลแท้ • ทำน้ำเต้าหู้ โจ๊ก ซุป จบในเครื่องเดียว
Dialogue: 3,0:00:00.00,{dur_ts},CtaWhite,,0,0,0,,{{\\pos(540,1520)}}กดตะกร้า / ลิงก์หน้าโปรไฟล์ เบอร์ #05
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
        "id": "omni_drama01_seagull",
        "title": "[ละครสั้น AI ขยับปากคุยกันจริง!] #05 Seagull เครื่องทำน้ำเต้าหู้ 1.2L",
        "filename": "drama_live_01_seagull.mp4",
        "price": "฿1,287",
        "commission": "คอม Shopee Video 10.4% (฿134) • Lazada 17% (฿238!)",
        "note": "เจนด้วย Gemini Omni 1.2 Flash (Full HD 1080p) ตัวละครสามี-ภรรยาขยับตัวและพูดภาษาไทยโต้ตอบกันจริง! ใช้ได้ทั้ง TikTok และ Shopee Video",
        "caption": "เบื่อต่อคิวน้ำเต้าหู้ตอนเช้าแถมหวานเจี๊ยบ! ดูวิธีจบปัญหาในปุ่มเดียว 🥛 เครื่อง Seagull 8 in 1 พิกัดตะกร้า/ลิงก์หน้าโปรไฟล์ #05 #เครื่องทำน้ำเต้าหู้ #รีวิวของดี #ของใช้ในครัว",
        "affiliate_link": "https://s.shopee.co.th/4fy0Eq7MIA",
        "product_link": "https://shopee.co.th/product/1485671971/40215480650",
    }
    items = [new_item] + [x for x in items if x["id"] != new_item["id"]]
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def main():
    key = load_api_key()
    client = genai.Client(
        api_key=key,
        http_options=types.HttpOptions(api_version="v1beta", timeout=300 * 1000),
    )

    from PIL import Image
    prod_png = os.path.join(OMNI_DIR, "seagull_real.png")
    if not os.path.exists(prod_png):
        Image.open(REAL_PROD).convert("RGB").save(prod_png)

    try:
        u1, m1 = upload_and_wait(client, S1_IMG)
        u2, m2 = upload_and_wait(client, S2_IMG)
        u3, m3 = upload_and_wait(client, S3_IMG)
        u4, m4 = upload_and_wait(client, prod_png)

        prompt_turn1 = (
            "Use the first image as the starting frame, and use the second, third, and fourth images as visual references "
            "for character consistency, pouring action, and the cream electric soy milk maker appliance. "
            "Create a natural, lively 15-second Thai vertical mini-drama commercial in the same bright sunny modern Thai kitchen. "
            "[0-5s] Starting from the first image, the Thai husband in the light-blue office shirt checks his wristwatch with an annoyed, rushed expression, shakes his empty mug, and speaks natural expressive Bangkok Thai with clear lip-sync: "
            "\"โอ๊ย สายแล้วเนี่ย น้ำเต้าหู้ปากซอยคิวยาว แถมหวานตัดขาอีก!\" "
            "His Thai wife in the cream linen top chuckles playfully with her arms crossed. "
            "[5-10s] Cut to a medium shot matching the second reference image: the wife steps forward smiling confidently, pours golden soybeans and clear water into the sleek cream electric soy milk maker from the fourth reference image on the wooden counter, taps one button on the front panel, and speaks cheerful natural Thai with clear lip-sync: "
            "\"เลิกต่อคิวได้แล้วพ่อคุณ แค่ใส่ถั่วกับน้ำ กดปุ่มเดียวจบ!\" The husband leans in watching curiously. "
            "[10-15s] Cut to a gorgeous close-up matching the third reference image: steaming hot silky soy milk pours smoothly from the cream pitcher into a clear glass mug in golden morning sunlight as the wife speaks warmly off-camera in natural Thai: "
            "\"ทั้งปั่นทั้งต้มอัตโนมัติ เนื้อเนียนไม่ต้องกรองกาก ทำได้ตั้งแปดเมนู!\" "
            "Sound design: warm light morning acoustic background music, gentle pouring liquid sound, natural crisp Thai conversation audio. No on-screen text, no captions, no watermarks."
        )

        inter1 = run_omni_interaction(
            client,
            "Turn 1: 15s 9:16 1080p Live Thai Couple Drama",
            model=MODEL,
            input=[
                {"type": "image", "uri": u1, "mime_type": m1},
                {"type": "image", "uri": u2, "mime_type": m2},
                {"type": "image", "uri": u3, "mime_type": m3},
                {"type": "image", "uri": u4, "mime_type": m4},
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
        part1_path = os.path.join(OMNI_DIR, "omni_turn1_15s.mp4")
        with open(part1_path, "wb") as f:
            f.write(client.files.download(file=out1.uri))
        dur1 = probe_duration(part1_path)
        print(f"Saved Turn 1: {part1_path} ({os.path.getsize(part1_path)/(1024*1024):.2f} MB, {dur1:.2f}s)")

        prompt_turn2 = (
            "Extend this video seamlessly for 8 seconds. "
            "[0-5s] Cut to a warm medium reaction shot in the same sunlit Thai kitchen: the Thai husband in the light-blue office shirt lifts the steaming glass mug of fresh soy milk, takes a delighted sip, his eyes widen with genuine amazement as he gives an enthusiastic thumbs-up and speaks natural excited Bangkok Thai with clear lip-sync: "
            "\"เฮ้ย หอมมันเนียนกว่าเจ้าดังอีก คุมหวานได้ แถมประหยัดเยอะเลย!\" His wife in the cream linen top laughs happily beside him. "
            "[5-8s] The wife smiles warmly at the camera, gesturing proudly to the sleek cream electric soy milk maker from the reference image on the counter, speaking friendly natural Thai with clear lip-sync: "
            "\"ของแท้ขายไปแล้วสามหมื่นเครื่อง กดตะกร้าหรือลิงก์หน้าโปรไฟล์ได้เลยจ้า!\" "
            "Warm cheerful morning acoustic music resolves gently. No on-screen text, no captions, no watermarks."
        )

        inter2 = run_omni_interaction(
            client,
            "Turn 2: Extend +8s Husband Reaction & Wife CTA",
            model=MODEL,
            previous_interaction_id=inter1.id,
            input=[
                {"type": "image", "uri": u4, "mime_type": m4},
                {"type": "text", "text": prompt_turn2},
            ],
            response_format={
                "type": "video",
                "delivery": "uri",
                "aspect_ratio": "9:16",
                "resolution": "720p",
                "duration": "8s",
            },
        )
        out2 = inter2.output_video
        if not out2 or not out2.uri:
            raise RuntimeError("Turn 2 returned no output_video URI")
        part2_path = os.path.join(OMNI_DIR, "omni_turn2_ext.mp4")
        with open(part2_path, "wb") as f:
            f.write(client.files.download(file=out2.uri))
        dur2 = probe_duration(part2_path)
        print(f"Saved Turn 2: {part2_path} ({os.path.getsize(part2_path)/(1024*1024):.2f} MB, {dur2:.2f}s)")

        # Normalize & assemble depending on whether Turn 2 is already full combined video or delta extension
        norm_omni = os.path.join(OMNI_DIR, "omni_norm.mp4")
        if dur2 >= dur1 + 3.0:
            print(f"Turn 2 contains full extended clip ({dur2:.2f}s). Using directly.")
            subprocess.check_call([
                "ffmpeg", "-y", "-v", "error", "-i", part2_path,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                norm_omni,
            ])
        else:
            print(f"Turn 2 is a standalone segment ({dur2:.2f}s). Concatenating Turn 1 + Turn 2.")
            n1 = os.path.join(OMNI_DIR, "n1.mp4")
            n2 = os.path.join(OMNI_DIR, "n2.mp4")
            for src, dst in [(part1_path, n1), (part2_path, n2)]:
                subprocess.check_call([
                    "ffmpeg", "-y", "-v", "error", "-i", src,
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                    dst,
                ])
            subprocess.check_call([
                "ffmpeg", "-y", "-v", "error",
                "-i", n1, "-i", n2,
                "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                norm_omni,
            ])

        dur_omni = probe_duration(norm_omni)
        endcard_path = os.path.join(OMNI_DIR, "endcard.mp4")
        build_endcard_clip(endcard_path, duration=3.8)

        final_mp4 = os.path.join(VID_DIR, "drama_live_01_seagull.mp4")
        xfade_offset = max(1.0, round(dur_omni - 0.35, 3))
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error",
            "-i", norm_omni, "-i", endcard_path,
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration=0.35:offset={xfade_offset},format=yuv420p[vout];"
            f"[0:a][1:a]acrossfade=d=0.35[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "30",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-movflags", "+faststart",
            final_mp4,
        ])

        final_dur = probe_duration(final_mp4)
        for idx, frac in enumerate([0.08, 0.28, 0.48, 0.68, 0.80, 0.94]):
            t = round(final_dur * frac, 2)
            subprocess.check_call([
                "ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", final_mp4,
                "-frames:v", "1", "-q:v", "3", os.path.join(OMNI_DIR, f"qa_{idx+1}.jpg"),
            ])

        update_manifest()
        print(
            f"\nSUCCESS! Final Live-Action Thai Drama: {final_mp4} "
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
