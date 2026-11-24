import json
import os
import subprocess
import sys

BASE_DIR = r"d:\9.Code\shopee_ai"
KIT_DIR = os.path.join(BASE_DIR, "kling_kit_seagull")
RENDER_DIR = os.path.join(KIT_DIR, "rendered")
VID_DIR = os.path.join(BASE_DIR, "videos")
TMP_DIR = os.path.join(KIT_DIR, "tmp_out")
MANIFEST_PATH = os.path.join(VID_DIR, "manifest.json")
ENDCARD_BG = os.path.join(VID_DIR, "drama_01", "bg5.png")
BGM_WAV = os.path.join(VID_DIR, "drama_01", "bgm_morning.wav")
os.makedirs(TMP_DIR, exist_ok=True)


def get_dur(path: str) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            text=True,
        ).strip()
    )


def has_audio(path: str) -> bool:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", path],
        text=True,
    ).strip()
    return bool(out)


def fmt_t(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = min(99, int(round((sec - int(sec)) * 100)))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def normalize_shot(src_mp4: str, out_mp4: str, fallback_audio: str | None = None):
    """Normalize any Kling/Flow shot to 1080x1920 30fps stereo 44.1kHz, adding fallback voice if silent."""
    if has_audio(src_mp4):
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-i", src_mp4,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            out_mp4,
        ])
    elif fallback_audio and os.path.exists(fallback_audio):
        dur = max(get_dur(src_mp4), get_dur(fallback_audio))
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error",
            "-stream_loop", "-1", "-i", src_mp4,
            "-i", fallback_audio,
            "-t", f"{dur:.2f}",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-shortest", out_mp4,
        ])
    else:
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error",
            "-i", src_mp4,
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-shortest", out_mp4,
        ])


def build_endcard(out_mp4: str, cta_audio: str):
    dur = round(get_dur(cta_audio) + 0.6, 2)
    subprocess.check_call([
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-i", ENDCARD_BG,
        "-i", cta_audio,
        "-vf", "scale=1080:1920,fps=30,format=yuv420p",
        "-t", str(dur),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        out_mp4,
    ])


def main():
    shots = [
        ("shot1.mp4", os.path.join(KIT_DIR, "audio_01_husband.mp3")),
        ("shot2.mp4", os.path.join(KIT_DIR, "audio_02_wife.mp3")),
        ("shot3.mp4", os.path.join(KIT_DIR, "audio_03_soymilk.mp3")),
    ]
    missing = [s for s, _ in shots if not os.path.exists(os.path.join(RENDER_DIR, s))]
    if missing:
        print("Missing clips in rendered/:", missing, file=sys.stderr)
        sys.exit(1)

    norm_clips = []
    for idx, (fname, fallback_a) in enumerate(shots, 1):
        src = os.path.join(RENDER_DIR, fname)
        dst = os.path.join(TMP_DIR, f"norm{idx}.mp4")
        print(f"Normalizing {fname} (has_audio={has_audio(src)})...")
        normalize_shot(src, dst, fallback_a)
        norm_clips.append(dst)

    endcard = os.path.join(TMP_DIR, "norm4_endcard.mp4")
    build_endcard(endcard, os.path.join(KIT_DIR, "audio_05_cta.mp3"))
    norm_clips.append(endcard)

    durs = [get_dur(c) for c in norm_clips]
    xfade = 0.25
    starts = [0.0]
    for i in range(1, len(durs)):
        starts.append(round(starts[i - 1] + durs[i - 1] - xfade, 3))
    total = round(starts[-1] + durs[-1], 3)

    # Build clean 2-color Thai drama subtitles + End-Card typography
    ass_path = os.path.join(TMP_DIR, "kling_sub.ass")
    s1, s2, s3, s4 = starts
    d1, d2, d3, d4 = durs
    ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopHook,Leelawadee UI,62,&H00FFFFFF,&H00FFFFFF,&H00121212,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,8,60,60,235,1
Style: SubMain,Leelawadee UI,54,&H00FFFFFF,&H00FFFFFF,&H00101010,&HB0000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,395,1
Style: EndHeader,Leelawadee UI,60,&H00FFFFFF,&H00FFFFFF,&H001A2A55,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,8,60,60,210,1
Style: PriceBig,Leelawadee UI,78,&H00234EF0,&H00234EF0,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: SubDark,Leelawadee UI,44,&H00222222,&H00222222,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: CtaWhite,Leelawadee UI,46,&H00FFFFFF,&H00FFFFFF,&H00112266,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 2,{fmt_t(s1)},{fmt_t(s1+d1-0.1)},TopHook,,0,0,0,,{{\\c&H00D4FF&}}น้ำเต้าหู้ปากซอยคิวยาว{{\\c&H00FFFFFF&}}\\Nแถมหวานตัดขา?!
Dialogue: 1,{fmt_t(s1+0.1)},{fmt_t(s1+d1-0.1)},SubMain,,0,0,0,,{{\\c&H0055D8FF&}}[สามี] {{\\c&H00FFFFFF&}}โอ๊ย สายแล้วเนี่ย! คิวยาวแถมหวานตัดขา!
Dialogue: 2,{fmt_t(s2)},{fmt_t(s2+d2-0.1)},TopHook,,0,0,0,,{{\\c&H0099CCFF&}}เลิกต่อคิวได้แล้ว!{{\\c&H00FFFFFF&}}\\Nใส่ถั่ว+น้ำ กดปุ่มเดียวจบ
Dialogue: 1,{fmt_t(s2+0.1)},{fmt_t(s2+d2-0.1)},SubMain,,0,0,0,,{{\\c&H0099B8FF&}}[ภรรยา] {{\\c&H00FFFFFF&}}แค่ใส่ถั่วเหลือง+น้ำเปล่า กดปุ่มเดียวจบ!
Dialogue: 2,{fmt_t(s3)},{fmt_t(s3+d3-0.1)},TopHook,,0,0,0,,{{\\c&H00D4FF&}}ทั้งปั่นทั้งต้มอัตโนมัติ{{\\c&H00FFFFFF&}}\\Nทำได้ตั้ง 8 เมนู!
Dialogue: 1,{fmt_t(s3+0.1)},{fmt_t(s3+d3-0.1)},SubMain,,0,0,0,,{{\\c&H0099B8FF&}}[ภรรยา] {{\\c&H00FFFFFF&}}เนื้อเนียนนุ่มไม่ต้องกรองกาก ทำได้ 8 เมนู!
Dialogue: 2,{fmt_t(s4)},{fmt_t(s4+d4)},EndHeader,,0,0,0,,Seagull เครื่องทำน้ำเต้าหู้ 1.2L\\N{{\\c&H00AAEEFF&}}รุ่น 8 in 1 (สีครีม)
Dialogue: 3,{fmt_t(s4+0.05)},{fmt_t(s4+d4)},PriceBig,,0,0,0,,{{\\pos(540,1220)}}฿1,287 {{\\fs42\\c&H00444444&}}| ★ 4.9 (ขายแล้ว 30k+)
Dialogue: 1,{fmt_t(s4+0.1)},{fmt_t(s4+d4)},SubDark,,0,0,0,,{{\\pos(540,1375)}}แบรนด์นกนางนวลแท้ • ทำน้ำเต้าหู้ โจ๊ก ซุป จบในเครื่องเดียว
Dialogue: 3,{fmt_t(s4+0.1)},{fmt_t(s4+d4)},CtaWhite,,0,0,0,,{{\\pos(540,1520)}}กดตะกร้า / ลิงก์หน้าโปรไฟล์ เบอร์ #05
"""
    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(ass_content)
    ass_esc = ass_path.replace("\\", "/").replace(":", "\\:")

    final_mp4 = os.path.join(VID_DIR, "drama_live_kling_seagull.mp4")
    fc = (
        f"[0:v][1:v]xfade=transition=fade:duration={xfade}:offset={starts[1]}[v01];"
        f"[v01][2:v]xfade=transition=fade:duration={xfade}:offset={starts[2]}[v02];"
        f"[v02][3:v]xfade=transition=fade:duration={xfade}:offset={starts[3]}[v03];"
        f"[v03]ass='{ass_esc}',format=yuv420p[vout];"
        f"[0:a][1:a]acrossfade=d={xfade}[a01];"
        f"[a01][2:a]acrossfade=d={xfade}[a02];"
        f"[a02][3:a]acrossfade=d={xfade}[adlg];"
        f"[4:a]volume=0.38[bgm];"
        f"[adlg][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[aout]"
    )
    subprocess.check_call([
        "ffmpeg", "-y", "-v", "error",
        "-i", norm_clips[0], "-i", norm_clips[1], "-i", norm_clips[2], "-i", norm_clips[3],
        "-stream_loop", "-1", "-i", BGM_WAV,
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-movflags", "+faststart",
        final_mp4,
    ])

    items = []
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            items = json.load(f)
    new_item = {
        "id": "kling_drama01_seagull",
        "title": "[ละครสั้น Kling ขยับปากจริง!] #05 Seagull เครื่องทำน้ำเต้าหู้ 1.2L",
        "filename": "drama_live_kling_seagull.mp4",
        "price": "฿1,287",
        "commission": "คอม Shopee Video 10.4% (฿134) • Lazada 17% (฿238!)",
        "note": "คลิปละครสั้นขยับตัว+ขยับปากคุยกันจริง (ตัดต่อรวม 3 ช็อต + ซับไทย + ฉากปิด Seagull ขาว–ส้มเรียบร้อย)",
        "caption": "เบื่อต่อคิวน้ำเต้าหู้ตอนเช้าแถมหวานเจี๊ยบ! ดูวิธีจบปัญหาในปุ่มเดียว 🥛 เครื่อง Seagull 8 in 1 พิกัดตะกร้า/ลิงก์หน้าโปรไฟล์ #05 #เครื่องทำน้ำเต้าหู้ #รีวิวของดี #ของใช้ในครัว",
        "affiliate_link": "https://s.shopee.co.th/4fy0Eq7MIA",
        "product_link": "https://shopee.co.th/product/1485671971/40215480650",
    }
    items = [new_item] + [x for x in items if x["id"] != new_item["id"]]
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"DONE! Saved: {final_mp4} ({os.path.getsize(final_mp4)/(1024*1024):.2f} MB, {total:.2f}s)")


if __name__ == "__main__":
    main()
