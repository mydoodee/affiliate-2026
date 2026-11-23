import html
import json
import mimetypes
import os
import re
import socket
import urllib.parse
from datetime import datetime
from email.parser import BytesParser
from email.policy import default as email_default_policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = r"d:\9.Code\shopee_ai"
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
UPLOADS_DIR = os.path.join(BASE_DIR, "raw_uploads")
MANIFEST_PATH = os.path.join(VIDEOS_DIR, "manifest.json")
PORT = 8787

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)


def get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def load_manifest() -> list:
    if not os.path.exists(MANIFEST_PATH):
        return []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_html(lan_ip: str) -> str:
    items = load_manifest()
    cards_html = []
    for item in items:
        vid_id = html.escape(item["id"])
        title = html.escape(item["title"])
        filename = html.escape(item["filename"])
        price = html.escape(item["price"])
        comm = html.escape(item["commission"])
        caption = item["caption"]
        caption_esc = html.escape(caption)
        caption_js = json.dumps(caption, ensure_ascii=False)
        aff_link = html.escape(item["affiliate_link"])
        prod_link = html.escape(item["product_link"])
        status_note = html.escape(item.get("note", ""))
        filepath = os.path.join(VIDEOS_DIR, item["filename"])
        exists = os.path.exists(filepath)
        size_mb = f"{os.path.getsize(filepath)/(1024*1024):.1f} MB" if exists else "กำลังสร้าง..."
        dl_url = f"/download/{urllib.parse.quote(item['filename'])}"
        stream_url = f"/stream/{urllib.parse.quote(item['filename'])}"

        cards_html.append(f"""
        <article class="card" id="card-{vid_id}">
          <div class="card-head">
            <div>
              <span class="pill">{comm}</span>
              <span class="pill pill-gray">{size_mb} • 1080p</span>
            </div>
            <label class="done-toggle">
              <input type="checkbox" onchange="toggleDone('{vid_id}', this.checked)" id="chk-{vid_id}" />
              <span>โพสต์แล้ว</span>
            </label>
          </div>
          <h2>{title} <span class="price">{price}</span></h2>
          {f'<p class="note">{status_note}</p>' if status_note else ''}
          {f'<video controls playsinline preload="metadata" src="{stream_url}"></video>' if exists else '<div class="pending">กำลังเรนเดอร์ไฟล์...</div>'}
          <div class="caption-box">
            <div class="cap-label">แคปชันพร้อมวาง ({len(caption)}/150 ตัวอักษร):</div>
            <div class="cap-text">{caption_esc}</div>
          </div>
          <div class="btn-stack">
            <a class="btn btn-primary" href="{dl_url}" download="{filename}">1. ดาวน์โหลดคลิป Full HD (1080p)</a>
            <button class="btn btn-dark" onclick='copyText({caption_js}, this)'>2. ก๊อปแคปชัน (แตะ 1 ที)</button>
            <a class="btn btn-outline" href="{aff_link}" target="_blank" rel="noopener">3. เปิดสินค้าในแอป Shopee (กดหัวใจไว้ปักถุงส้ม)</a>
            <button class="btn btn-subtle" onclick='copyText({json.dumps(item["product_link"])}, this)'>ก๊อปลิงก์สินค้าต้นฉบับ</button>
          </div>
        </article>
        """)

    uploads = sorted(os.listdir(UPLOADS_DIR), reverse=True)
    uploads_html = (
        "".join(f"<li>{html.escape(u)}</li>" for u in uploads[:10])
        if uploads
        else "<li>ยังไม่มีคลิปถ่ายจริงที่อัปโหลดเข้ามา</li>"
    )

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>Babman iPhone 12 Hub • Shopee Video</title>
  <style>
    :root {{
      --orange: #ee4d2d;
      --orange-dark: #d73211;
      --bg: #f5f6fa;
      --card: #ffffff;
      --text: #111827;
      --muted: #6b7280;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Sarabun', 'Helvetica Neue', sans-serif;
      background: var(--bg);
      color: var(--text);
      padding-bottom: 48px;
    }}
    header {{
      background: linear-gradient(135deg, #ee4d2d, #ff7337);
      color: #fff;
      padding: 20px 16px;
      text-align: center;
      position: sticky;
      top: 0;
      z-index: 20;
      box-shadow: 0 2px 12px rgba(238, 77, 45, 0.25);
    }}
    header h1 {{ font-size: 1.2rem; font-weight: 700; }}
    header p {{ font-size: 0.82rem; opacity: 0.92; margin-top: 4px; }}
    .wrap {{ max-width: 560px; margin: 0 auto; padding: 14px; display: flex; flex-direction: column; gap: 16px; }}
    .tip-box {{
      background: #fff7ed;
      border: 1px solid #fed7aa;
      border-radius: 12px;
      padding: 12px 14px;
      font-size: 0.84rem;
      line-height: 1.45;
      color: #9a3412;
    }}
    .card {{
      background: var(--card);
      border-radius: 16px;
      padding: 16px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
      border: 1px solid #e5e7eb;
    }}
    .card.is-done {{ opacity: 0.65; border-color: #86efac; }}
    .card-head {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }}
    .pill {{
      display: inline-block;
      background: #fff1ed;
      color: var(--orange);
      font-size: 0.74rem;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 999px;
    }}
    .pill-gray {{ background: #f3f4f6; color: #374151; }}
    .done-toggle {{ font-size: 0.82rem; color: #16a34a; font-weight: 600; display: flex; align-items: center; gap: 5px; }}
    h2 {{ font-size: 1.05rem; margin-bottom: 6px; line-height: 1.35; }}
    .price {{ color: var(--orange); font-weight: 700; }}
    .note {{ font-size: 0.82rem; color: var(--muted); margin-bottom: 10px; }}
    video {{
      width: 100%;
      max-height: 360px;
      border-radius: 12px;
      background: #000;
      margin: 8px 0 12px;
    }}
    .caption-box {{
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 10px 12px;
      margin-bottom: 12px;
    }}
    .cap-label {{ font-size: 0.74rem; color: var(--muted); margin-bottom: 4px; font-weight: 600; }}
    .cap-text {{ font-size: 0.86rem; line-height: 1.45; word-break: break-word; }}
    .btn-stack {{ display: flex; flex-direction: column; gap: 8px; }}
    .btn {{
      display: block;
      width: 100%;
      text-align: center;
      text-decoration: none;
      border: none;
      border-radius: 11px;
      padding: 12px 14px;
      font-size: 0.92rem;
      font-weight: 600;
      cursor: pointer;
      font-family: inherit;
    }}
    .btn-primary {{ background: var(--orange); color: #fff; }}
    .btn-dark {{ background: #111827; color: #fff; }}
    .btn-outline {{ background: #fff; color: var(--orange); border: 1.5px solid var(--orange); }}
    .btn-subtle {{ background: #f3f4f6; color: #374151; font-size: 0.84rem; padding: 9px 12px; }}
    .upload-card h3 {{ font-size: 1rem; margin-bottom: 6px; }}
    .upload-card p {{ font-size: 0.83rem; color: var(--muted); margin-bottom: 10px; }}
    input[type="file"] {{ width: 100%; margin-bottom: 10px; font-size: 0.88rem; }}
    ul.up-list {{ margin-top: 10px; padding-left: 18px; font-size: 0.82rem; color: var(--muted); }}
    #toast {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      background: #111827;
      color: #fff;
      padding: 10px 18px;
      border-radius: 999px;
      font-size: 0.86rem;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s;
      z-index: 99;
    }}
    #toast.show {{ opacity: 1; }}
  </style>
</head>
<body>
  <header>
    <h1>📱 Babman Mobile Hub (Full HD 1080p)</h1>
    <p>Wi-Fi ตรงจากคอม ({lan_ip}:{PORT}) • ไม่โดน LINE บีบอัดภาพ</p>
  </header>
  <main class="wrap">
    <div class="tip-box">
      <strong>วิธีเซฟเข้าแอปรูปภาพบน iPhone 12 (Safari):</strong><br/>
      แตะปุ่ม <strong>1. ดาวน์โหลดคลิป Full HD</strong> → กด <strong>ดาวน์โหลด</strong> → แตะลูกศรดาวน์โหลดมุมล่างซ้าย/บนขวาใน Safari → เปิดวิดีโอ → กดปุ่มแชร์ → <strong>บันทึกวิดีโอ (Save Video)</strong>
    </div>

    {"".join(cards_html)}

    <section class="card upload-card">
      <h3>🎥 ส่งคลิปถ่ายสินค้าจริงจาก iPhone 12 → คอม</h3>
      <p>ถ่ายคลิปของจริงใกล้ตัว 10–15 วิ แล้วส่งขึ้นมาที่นี่ได้เลย เดี๋ยวผู้ช่วยเอาไปตัดต่อ + ใส่ซับไทย + พากย์เสียงให้ครับ</p>
      <form action="/upload" method="POST" enctype="multipart/form-data">
        <input type="file" name="video" accept="video/*,image/*" required />
        <button class="btn btn-dark" type="submit">ส่งไฟล์เข้าคอม (Full Quality)</button>
      </form>
      <ul class="up-list">{uploads_html}</ul>
    </section>
  </main>

  <div id="toast">คัดลอกเรียบร้อย ✓</div>

  <script>
    function showToast(msg) {{
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2000);
    }}
    function copyText(text, btn) {{
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(() => showToast('คัดลอกแล้ว ✓'));
      }} else {{
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast('คัดลอกแล้ว ✓');
      }}
    }}
    function toggleDone(id, checked) {{
      localStorage.setItem('posted_' + id, checked ? '1' : '0');
      const card = document.getElementById('card-' + id);
      if (card) card.classList.toggle('is-done', checked);
    }}
    window.addEventListener('DOMContentLoaded', () => {{
      document.querySelectorAll('[id^="chk-"]').forEach(chk => {{
        const id = chk.id.replace('chk-', '');
        if (localStorage.getItem('posted_' + id) === '1') {{
          chk.checked = true;
          const card = document.getElementById('card-' + id);
          if (card) card.classList.add('is-done');
        }}
      }});
    }});
  </script>
</body>
</html>"""


class HubHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _serve_video(self, filename: str, as_download: bool):
        safe_name = os.path.basename(urllib.parse.unquote(filename))
        filepath = os.path.join(VIDEOS_DIR, safe_name)
        if not os.path.isfile(filepath):
            self.send_error(404, "Video not found")
            return

        file_size = os.path.getsize(filepath)
        ctype = mimetypes.guess_type(filepath)[0] or "video/mp4"
        range_header = self.headers.get("Range")

        start, end = 0, file_size - 1
        status = 200
        if range_header and range_header.startswith("bytes="):
            parts = range_header.replace("bytes=", "").split("-")
            if parts[0]:
                start = int(parts[0])
            if len(parts) > 1 and parts[1]:
                end = int(parts[1])
            end = min(end, file_size - 1)
            status = 206

        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        if as_download:
            self.send_header("Content-Disposition", f'attachment; filename="{safe_name}"')
        self.end_headers()

        with open(filepath, "rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except BrokenPipeError:
                    break
                remaining -= len(chunk)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            body = build_html(get_lan_ip()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path.startswith("/download/"):
            self._serve_video(parsed.path[len("/download/"):], as_download=True)
        elif parsed.path.startswith("/stream/"):
            self._serve_video(parsed.path[len("/stream/"):], as_download=False)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/upload":
            self.send_error(404)
            return
        ctype = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in ctype:
            self.send_error(400, "Expected multipart/form-data")
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        header_bytes = f"Content-Type: {ctype}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
        msg = BytesParser(policy=email_default_policy).parsebytes(header_bytes + raw_body)

        saved = False
        if msg.is_multipart():
            for part in msg.iter_parts():
                cd = part.get("Content-Disposition", "")
                if 'name="video"' in cd:
                    orig_name = part.get_filename() or "iphone_clip.mp4"
                    orig_name = re.sub(r"[^a-zA-Z0-9._-]", "_", os.path.basename(orig_name))
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    out_path = os.path.join(UPLOADS_DIR, f"{ts}_{orig_name}")
                    payload = part.get_payload(decode=True)
                    if payload:
                        with open(out_path, "wb") as f:
                            f.write(payload)
                        saved = True
                        break
        if not saved:
            self.send_error(400, "No video uploaded")
            return
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    ip = get_lan_ip()
    print(f"Babman iPhone 12 Mobile Hub running at: http://{ip}:{PORT}")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), HubHandler)
    server.serve_forever()
