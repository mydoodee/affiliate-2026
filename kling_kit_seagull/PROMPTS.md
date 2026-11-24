# ชุดสร้างละครสั้น "ขยับปากคุยกันจริง" (Kling AI / Google Flow) — #05 Seagull 1.2L

ไฟล์ภาพและเสียงทั้งหมดรวมไว้ในโฟลเดอร์นี้แล้ว (`d:\9.Code\shopee_ai\kling_kit_seagull\`)

---

## วิธีทำใน Kling AI (https://klingai.com — มีเครดิตฟรี!)

> **ตั้งค่าทุกช็อตเหมือนกัน**: Mode = **Image to Video** | Aspect Ratio = **9:16** | Duration = **5s** (หรือ **10s** สำหรับช็อต 2)

### ช็อตที่ 1: สามีบ่นคิวยาว (เซฟไฟล์ที่เจนเสร็จชื่อ `shot1.mp4`)
1. อัปโหลดรูป: **`01_scene1_husband.jpg`**
2. วาง Prompt นี้:
```text
Realistic handheld Thai commercial drama in a sunny modern kitchen. The Thai husband in the light-blue office shirt looks frustratedly at his wristwatch, shakes his empty white mug slightly, and talks expressively toward his wife with natural facial movements. The Thai wife in the cream linen top laughs playfully with arms crossed. Warm golden morning sunlight, natural motion, smooth camera push-in, no text, no watermarks.
```
3. พอเจนคลิป 5 วิเสร็จ → กดปุ่ม **`Lip-Sync`** ใต้คลิป → เลือกหน้า **ผู้ชาย (สามี)** → เลือก **Upload Local Audio** → อัปโหลดไฟล์ **`audio_01_husband.mp3`** → กด Generate แล้วดาวน์โหลดเซฟเป็น **`rendered\shot1.mp4`**

---

### ช็อตที่ 2: ภรรยาเทถั่วเหลืองกดปุ่มเดียว (เซฟชื่อ `shot2.mp4`)
1. อัปโหลดรูป: **`02_scene2_wife_pour.jpg`**
2. วาง Prompt นี้:
```text
Realistic Thai kitchen commercial scene. The cheerful Thai wife in the cream linen top smiles confidently while pouring golden soybeans and clear water smoothly into the cream electric soy milk maker on the wooden counter, then points cheerfully at the appliance while talking to her husband. The husband in the light-blue shirt leans in watching with surprised curiosity. Warm morning sunlight, smooth natural movement, no text.
```
3. พอเจนคลิปเสร็จ (แนะนำ 10s หรือ 5s) → กด **`Lip-Sync`** → เลือกหน้า **ผู้หญิง (ภรรยา)** → อัปโหลดไฟล์ **`audio_02_wife.mp3`** → ดาวน์โหลดเซฟเป็น **`rendered\shot2.mp4`**

---

### ช็อตที่ 3: เทน้ำเต้าหู้ร้อนๆ ควันกรุ่น (เซฟชื่อ `shot3.mp4` — ไม่ต้องทำ Lip-Sync!)
1. อัปโหลดรูป: **`03_scene3_soymilk_pour.jpg`**
2. วาง Prompt นี้:
```text
Ultra-appetizing commercial food close-up in golden morning sunlight. The sleek cream soy milk maker pitcher smoothly pours silky, rich, steaming hot soy milk into the clear glass mug on the wooden kitchen counter. Gentle wisps of white steam rise gracefully from the warm mug. Slow cinematic camera push-in, crisp detail, realistic liquid physics, no text.
```
3. ดาวน์โหลดเซฟเป็น **`rendered\shot3.mp4`** *(ช็อตนี้ไม่ต้องทำ Lip-Sync เดี๋ยวสคริปต์ผมใส่เสียงพากย์ `audio_03_soymilk.mp3` + ซับ + ดนตรี + ฉากปิด Seagull ขาว–ส้มให้เองเลย!)*

---

## (ทางเลือก) ถ้าใช้ Google Flow / Veo 3 (มีเสียงพูดภาษาไทยในตัว!)
สามารถใช้รูปเดิม `01`, `02`, `03` แล้วต่อท้าย Prompt แต่ละช็อตด้วยประโยคนี้เพื่อให้ตัวละครพูดไทยออกมาเองได้เลย:
- **ช็อต 1 ต่อท้าย**: `The husband speaks natural expressive Bangkok Thai: "โอ๊ย สายแล้วเนี่ย น้ำเต้าหู้ปากซอยคิวยาว แถมหวานตัดขาอีก!"`
- **ช็อต 2 ต่อท้าย**: `The wife speaks cheerful natural Bangkok Thai: "เลิกต่อคิวได้แล้วพ่อคุณ แค่ใส่ถั่วกับน้ำ กดปุ่มเดียวจบ!"`
- **ช็อต 3 ต่อท้าย**: `Warm female Thai voiceover says smoothly: "ทั้งปั่นทั้งต้มอัตโนมัติ เนื้อเนียนไม่ต้องกรองกาก ทำได้ตั้งแปดเมนู!"`

---

## ขั้นสุดท้าย: ให้ผมตัดต่อปิดจบ 1080p อัตโนมัติ!
แค่เอาไฟล์ **`shot1.mp4`**, **`shot2.mp4`**, **`shot3.mp4`** ไปวางในโฟลเดอร์:
`d:\9.Code\shopee_ai\kling_kit_seagull\rendered\`
แล้วพิมพ์บอกผมว่า **"วางคลิปแล้ว"** — ผมจะตัดต่อรวม 3 ช็อต + ใส่ซับไทยแยกสี + ดนตรีตอนเช้า + ฉากปิดขาว–ส้ม **Seagull ฿1,287** และส่งขึ้น **iPhone 12 Mobile Hub** ให้ทันทีครับ!
