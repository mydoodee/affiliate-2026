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

sys.path.insert(0, r"d:\9.Code\shopee_ai")
from build_live_drama_omni import (
    BASE_DIR,
    OMNI_DIR,
    VID_DIR,
    MODEL,
    build_endcard_clip,
    load_api_key,
    probe_duration,
    run_omni_interaction,
    sanitize_err,
    update_manifest,
    upload_and_wait,
)

TURN1_ID = "v1_ChdrQ3NGYV91R0tfVFhnOFVQcC1QU3FRZxIXa0NzRmFfdUdLX1RYZzhVUHAtUFNxUWc"
PROD_PNG = os.path.join(OMNI_DIR, "seagull_real.png")


def main():
    key = load_api_key()
    client = genai.Client(
        api_key=key,
        http_options=types.HttpOptions(api_version="v1beta", timeout=300 * 1000),
    )

    try:
        u4, m4 = upload_and_wait(client, PROD_PNG)

        prompt_turn2_v2 = (
            "Extend this video seamlessly for 10 seconds. "
            "[0-4s] Cut immediately at 0s to a warm medium shot in the same sunlit Thai kitchen: "
            "the Thai husband in the light-blue office shirt lifts the steaming glass mug of fresh soy milk, "
            "takes a delighted sip, his eyes widen with genuine amazement, gives an enthusiastic thumbs-up, "
            "and speaks natural excited Bangkok Thai with clear lip-sync: "
            "\"เฮ้ย หอมมันเนียนกว่าเจ้าดังอีก คุมหวานได้ด้วย!\" "
            "[4-8s] His Thai wife in the cream linen top laughs happily beside him, smiles warmly at the camera, "
            "and gestures proudly to the sleek cream electric soy milk maker from the reference image on the wooden counter, "
            "speaking clear cheerful natural Thai with clear lip-sync at a brisk natural pace so she finishes every word cleanly before 8 seconds: "
            "\"ทำได้ตั้งแปดเมนู ของแท้ขายแล้วสามหมื่นเครื่อง กดตะกร้าเลยจ้า!\" "
            "[8-10s] Both husband and wife smile happily holding the mug beside the soy milk maker as warm cheerful morning acoustic music resolves smoothly. "
            "No spoken words in the final 2 seconds. No on-screen text, no captions, no watermarks."
        )

        inter2 = run_omni_interaction(
            client,
            "Turn 2 v2: Extend +10s Clean Full Dialogue & Breathing Room",
            model=MODEL,
            previous_interaction_id=TURN1_ID,
            input=[
                {"type": "image", "uri": u4, "mime_type": m4},
                {"type": "text", "text": prompt_turn2_v2},
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
            raise RuntimeError("Turn 2 v2 returned no output_video URI")

        raw_v2 = os.path.join(OMNI_DIR, "omni_turn2_v2.mp4")
        with open(raw_v2, "wb") as f:
            f.write(client.files.download(file=out2.uri))
        dur_v2 = probe_duration(raw_v2)
        print(f"Saved Turn 2 v2: {raw_v2} ({os.path.getsize(raw_v2)/(1024*1024):.2f} MB, {dur_v2:.2f}s)")

        # First transcribe raw_v2 audio from 13.0s to end so we pick the EXACT clean cut point!
        tail_mp3 = os.path.join(OMNI_DIR, "v2_tail_check.mp3")
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-ss", "12.0", "-i", raw_v2,
            "-vn", "-ac", "1", "-ar", "16000", tail_mp3,
        ])
        with open(tail_mp3, "rb") as af:
            audio_bytes = af.read()
        tr = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3"),
                "This audio starts at t=12.0s of the video. Transcribe every Thai phrase with exact [start - end] timestamps (both relative to 0.0s and +12.0s absolute). Note the exact second the husband begins speaking after the seam, and whether the wife finishes her final sentence cleanly.",
            ],
        )
        print("\n--- RAW V2 TAIL TRANSCRIPT (t >= 12.0s) ---")
        print(tr.text)

        # Also extract frames at 14.8, 15.0, 15.2, 15.4, 15.6 to confirm visual scene-cut timestamp
        for t_check in [13.6, 14.9, 15.1, 15.3, 15.6]:
            subprocess.check_call([
                "ffmpeg", "-y", "-v", "error", "-ss", str(t_check), "-i", raw_v2,
                "-frames:v", "1", "-q:v", "4",
                os.path.join(OMNI_DIR, f"seam_t{str(t_check).replace('.', '_')}.jpg"),
            ])

        # Clean splice: keep [0.00 -> 13.70] (ends cleanly after "เนื้อเนียนไม่ต้องกรองกาก")
        # and jump straight into [15.10 -> end] (new clean 10s Turn 2!)
        seg_a = os.path.join(OMNI_DIR, "seg_a.mp4")
        seg_b = os.path.join(OMNI_DIR, "seg_b.mp4")
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-i", raw_v2,
            "-t", "13.70",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            seg_a,
        ])
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-ss", "15.10", "-i", raw_v2,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            seg_b,
        ])

        dur_a = probe_duration(seg_a)
        spliced = os.path.join(OMNI_DIR, "omni_spliced_v2.mp4")
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
        build_endcard_clip(endcard_path, duration=3.8)

        final_mp4 = os.path.join(VID_DIR, "drama_live_01_seagull.mp4")
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

        # Verify final audio full transcript
        final_mp3 = os.path.join(OMNI_DIR, "final_v2_check.mp3")
        subprocess.check_call([
            "ffmpeg", "-y", "-v", "error", "-i", final_mp4,
            "-vn", "-ac", "1", "-ar", "16000", final_mp3,
        ])
        with open(final_mp3, "rb") as af:
            fb = af.read()
        tr_final = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Part.from_bytes(data=fb, mime_type="audio/mp3"),
                "Transcribe every spoken Thai sentence in this final video with [start - end] timestamps and explicitly verify whether ANY word is cut off or abruptly silenced.",
            ],
        )
        print("\n--- FINAL V2 AUDIO QA ---")
        print(tr_final.text)

        final_dur = probe_duration(final_mp4)
        for idx, frac in enumerate([0.10, 0.35, 0.56, 0.72, 0.84, 0.94]):
            t = round(final_dur * frac, 2)
            subprocess.check_call([
                "ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", final_mp4,
                "-frames:v", "1", "-q:v", "3", os.path.join(OMNI_DIR, f"qa_v2_{idx+1}.jpg"),
            ])

        update_manifest()
        print(
            f"\nSUCCESS V2! Final Polished Thai Drama: {final_mp4} "
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
