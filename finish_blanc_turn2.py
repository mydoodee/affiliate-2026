import os
import subprocess
import sys
from PIL import Image
from google import genai
from google.genai import errors, types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

sys.path.insert(0, r"d:\9.Code\shopee_ai")
from build_live_drama_omni import (
    MODEL,
    VID_DIR,
    load_api_key,
    probe_duration,
    run_omni_interaction,
    sanitize_err,
    upload_and_wait,
)
from build_drama_blanc_garage import (
    BLANC_BOTTLE_CROP,
    OMNI_DIR,
    build_endcard_clip,
    update_manifest,
)

PART1_MP4 = os.path.join(OMNI_DIR, "omni_t1.mp4")
T1_F1 = os.path.join(OMNI_DIR, "t1_f1.jpg")
T1_F4 = os.path.join(OMNI_DIR, "t1_f4.jpg")
HERO_UPPER_REF = os.path.join(OMNI_DIR, "hero_upper_ref.jpg")


def main():
    # Crop upper-body portrait from Turn 1 frame 1 (safe framing, exact face + white off-shoulder top + bottle)
    im1 = Image.open(T1_F1).convert("RGB")
    w, h = im1.size
    im1.crop((0, int(h * 0.08), w, int(h * 0.62))).save(HERO_UPPER_REF, "JPEG", quality=95)
    print(f"Saved upper portrait ref: {HERO_UPPER_REF}")

    key = load_api_key()
    client = genai.Client(
        api_key=key,
        http_options=types.HttpOptions(api_version="v1beta", timeout=300 * 1000),
    )

    try:
        u_mech, m_mech = upload_and_wait(client, T1_F4)
        u_prod, m_prod = upload_and_wait(client, BLANC_BOTTLE_CROP)
        u_hero, m_hero = upload_and_wait(client, HERO_UPPER_REF)

        prompt_part2 = (
            "Use the first image as the starting frame showing the four young Thai auto mechanics in matching navy-blue uniforms at the garage doorway. "
            "Use the second image as the product reference for the frosted white pump bottle labeled 'Blanc Nature', and use the third image as the character reference for the smiling Thai woman in the white off-shoulder top. "
            "Create a hilarious 10-second Thai comedy continuation in the same sunlit Bangkok auto repair garage. "
            "[0-4.8s] Starting from the first image, the mechanic standing on the right grins proudly, pulls the exact frosted white 'Blanc Nature' pump bottle out of his navy uniform pocket, and shines a small mechanic flashlight onto the bottle like unveiling a luxury supercar part, speaking clear lively Thai with natural lip-sync: "
            "\"แบลงก์ เนเจอร์ ไนอะซินาไมด์ สิบห้าเปอร์เซ็นต์... ซ่อมหน้าก่อน เครื่องยนต์ค่อยว่ากัน!\" "
            "The other three mechanics gasp together amazed: \"โหหหห!\" "
            "[4.8-8.3s] Quick cheerful medium close-up cut to the smiling Thai woman from the third image standing outside the garage, holding the frosted white Blanc Nature bottle casually near her glowing smooth cheek and laughing warmly as she speaks natural Thai: "
            "\"เคล็ดลับก็ขวดนี้แหละค่ะ!\" "
            "Right away, one cheerful mechanic pops his smiling head into the side of the frame raising his hand politely and joking in funny Thai: "
            "\"พี่ครับ ขอเบิกเป็นค่าอะไหล่ประจำเดือนด้วยครับ!\" "
            "[8.3-10s] The woman and the mechanics laugh joyfully and give friendly thumbs-up together as upbeat playful comedy music resolves cleanly. "
            "No spoken words in the final 1.7 seconds. No on-screen text, no captions, no watermarks."
        )

        inter2 = run_omni_interaction(
            client,
            "Part 2 (Standalone 10s R2V): Blanc Nature Reveal & Mechanic Punchline",
            model=MODEL,
            input=[
                {"type": "image", "uri": u_mech, "mime_type": m_mech},
                {"type": "image", "uri": u_prod, "mime_type": m_prod},
                {"type": "image", "uri": u_hero, "mime_type": m_hero},
                {"type": "text", "text": prompt_part2},
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
            raise RuntimeError("Part 2 returned no output_video URI")

        part2_path = os.path.join(OMNI_DIR, "omni_part2_10s.mp4")
        with open(part2_path, "wb") as f:
            f.write(client.files.download(file=out2.uri))
        dur2 = probe_duration(part2_path)
        print(f"Saved Part 2: {part2_path} ({os.path.getsize(part2_path)/(1024*1024):.2f} MB, {dur2:.2f}s)")

        # Splice tightened Part 1 (0.0 -> 11.2s, zero cutoffs) + Part 2 (0.0 -> end) + 3.5s End-Card
        seg_a = os.path.join(OMNI_DIR, "seg_a.mp4")
        seg_b = os.path.join(OMNI_DIR, "seg_b.mp4")
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-i", PART1_MP4,
            "-t", "11.2",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            seg_a,
        ])
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-i", part2_path,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            seg_b,
        ])

        dur_a = probe_duration(seg_a)
        spliced = os.path.join(OMNI_DIR, "omni_spliced.mp4")
        off_ab = round(dur_a - 0.12, 3)
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error",
            "-i", seg_a, "-i", seg_b,
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration=0.12:offset={off_ab},format=yuv420p[vout];"
            f"[0:a][1:a]acrossfade=d=0.12[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            spliced,
        ])

        dur_spliced = probe_duration(spliced)
        endcard_path = os.path.join(OMNI_DIR, "endcard.mp4")
        build_endcard_clip(endcard_path, duration=3.5)

        final_mp4 = os.path.join(VID_DIR, "drama_live_02_blanc_garage.mp4")
        off_end = max(1.0, round(dur_spliced - 0.35, 3))
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

        # Final Audio QA
        qa_mp3 = os.path.join(OMNI_DIR, "final_qa_audio.mp3")
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-i", final_mp4,
            "-vn", "-ac", "1", "-ar", "16000", qa_mp3,
        ])
        with open(qa_mp3, "rb") as af:
            fb = af.read()
        tr_final = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Part.from_bytes(data=fb, mime_type="audio/mp3"),
                "Transcribe every spoken Thai sentence in this final video with [start - end] timestamps and verify whether ANY word is cut off or abruptly silenced.",
            ],
        )
        print("\n--- FINAL AUDIO QA ---")
        print(tr_final.text)

        final_dur = probe_duration(final_mp4)
        for idx, frac in enumerate([0.06, 0.25, 0.44, 0.58, 0.76, 0.94]):
            t = round(final_dur * frac, 2)
            subprocess.check_call([
                "ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", final_mp4,
                "-frames:v", "1", "-q:v", "3", os.path.join(OMNI_DIR, f"qa_final_{idx+1}.jpg"),
            ])

        update_manifest()
        print(
            f"\nSUCCESS! Final Blanc Garage Comedy: {final_mp4} "
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
