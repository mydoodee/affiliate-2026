import os
import subprocess
import sys
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
from build_drama_wife_garage import (
    MECH_REF_IMG,
    OMNI_DIR,
    build_endcard_clip,
    transcribe_audio,
    update_manifest,
)

P1_PATH = os.path.join(OMNI_DIR, "wife_p1_15s.mp4")
PROVEN_WOMAN_UPPER = os.path.join(VID_DIR, "omni_drama_02", "hero_upper_ref.jpg")


def main():
    key = load_api_key()
    client = genai.Client(
        api_key=key,
        http_options=types.HttpOptions(api_version="v1beta", timeout=300 * 1000),
    )

    try:
        u_mech, m_mech = upload_and_wait(client, MECH_REF_IMG)
        u_wup, m_wup = upload_and_wait(client, PROVEN_WOMAN_UPPER)

        prompt_p2 = (
            "Use the first image as the starting frame of the four young Thai mechanics in matching navy-blue uniforms at the sunlit garage doorway, "
            "and use the second image as the character reference for the smiling Thai wife in the white off-shoulder top (without holding any bottle). "
            "Pure lighthearted Thai comedy sitcom inside the same sunny auto repair garage, no product bottle shown. "
            "[0-4.5s] Starting from the first image, the mechanics comically scatter back inside—Mechanic 1 ducks behind a stack of rubber tires. The smiling Thai wife strolls into the garage doorway asking sweetly in clear Thai: "
            "\"พี่คะ เห็นสามีหนูไหมคะ?\" "
            "Instantly, the three mechanic friends freeze and point straight at Mechanic 1 behind the tires in unison! "
            "[4.5-7.2s] The wife walks over to Mechanic 1 behind the tires smiling playfully and says in Thai: "
            "\"กลับบ้านค่ะ!\" "
            "Mechanic 1 pops up grinning sheepishly and answers sweetly in Thai: "
            "\"จ๋าาา... ที่รัก\" "
            "[7.2-10.6s] Funny twist: the wife turns to the three mechanic friends with a bright sweet smile and says clearly in Thai: "
            "\"ส่วนพวกพี่ เงินที่ยืมไป คืนด้วยนะคะ!\" "
            "The three mechanics freeze shocked; Mechanic 2 exclaims in lively Thai: "
            "\"อ้าว! พวกเราซวยด้วยเหรอ!\" "
            "[10.6-12.0s] All three mechanics laughingly run back inside the garage while everyone bursts out laughing with upbeat Thai sitcom music. No spoken words in the final 1.4 seconds. No on-screen text, no captions, no watermarks."
        )

        inter2 = run_omni_interaction(
            client,
            "Part 2 (12s, proven refs): Hide & Point -> Go Home -> Debt Collection Twist!",
            model=MODEL,
            input=[
                {"type": "image", "uri": u_mech, "mime_type": m_mech},
                {"type": "image", "uri": u_wup, "mime_type": m_wup},
                {"type": "text", "text": prompt_p2},
            ],
            response_format={
                "type": "video",
                "delivery": "uri",
                "aspect_ratio": "9:16",
                "resolution": "720p",
                "duration": "12s",
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

        n1 = os.path.join(OMNI_DIR, "n1.mp4")
        n2 = os.path.join(OMNI_DIR, "n2.mp4")
        for src, dst in [(P1_PATH, n1), (p2_path, n2)]:
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
