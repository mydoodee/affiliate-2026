# Babman Affiliate 2026 (`@mybabman` / `@mydoodee`)

โปรเจกต์รวมระบบ Affiliate Multi-Platform (**Shopee • Lazada • TikTok Shop • ACCESSTRADE Thailand**) พร้อมหน้าร้านออนไลน์และเครื่องมือผลิตคลิปแนวตั้ง `9:16`

- **Live Storefront**: https://mybabman-picks.vercel.app
- **New Year Travel & Insurance Hub**: https://mybabman-picks.vercel.app/#travel

## โครงสร้างไฟล์หลัก
- `index.html` & `public_store/index.html` — เว็บหน้าร้านรวมสินค้า Shopee/Lazada (`#01–#10`) และดีลท่องเที่ยว/ประกัน (`T01–T07`)
- `mobile_hub.py` — Local Wi-Fi Hub สำหรับโหลดคลิป Full HD 1080p และก๊อปแคปชันเข้า iPhone 12
- `build_cctv_video.py`, `build_antiant_video.py`, `build_zinsano_video.py`, `build_tiktok_batch.py` — สคริปต์สร้างวิดีโอแนวตั้ง `1080x1920` พร้อมเสียงพากย์ไทย (`edge-tts`) และซับไทย (`libass`)
- `trending_products_nov2026.csv`, `lazada_links_nov2026.csv`, `accesstrade_travel_links.csv` — ฐานข้อมูลสินค้าและลิงก์ Affiliate ทั้ง 3 เครือข่าย
- `posted_log.md`, `ready_to_post_pack.md`, `shopee_video_playbook.md` — บันทึกการลงคลิปและคู่มือคอนเทนต์
