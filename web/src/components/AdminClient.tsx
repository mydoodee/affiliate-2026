"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Database,
  MousePointerClick,
  Plus,
  Trash2,
  Upload,
} from "lucide-react";
import type { ClickStats, Product } from "@/lib/types";

export function AdminClient({
  initialStats,
  initialProducts,
}: {
  initialStats: ClickStats;
  initialProducts: Product[];
}) {
  const [adminPassword, setAdminPassword] = useState("");
  const [products, setProducts] = useState<Product[]>(initialProducts);
  const [statusMsg, setStatusMsg] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    code: "",
    title: "",
    description: "",
    price_display: "",
    price_num: "",
    sold_text: "",
    rating: "4.9",
    category: "home",
    badge: "",
    image_url: "",
    shopee_url: "",
    lazada_url: "",
    has_video: false,
  });

  async function initDb() {
    setLoading(true);
    setStatusMsg("");
    try {
      const res = await fetch("/api/admin/init", {
        method: "POST",
        headers: { "x-admin-password": adminPassword },
      });
      const data = await res.json();
      setStatusMsg(data.message || (data.ok ? "สำเร็จ" : "เกิดข้อผิดพลาด"));
      if (data.ok) {
        const listRes = await fetch("/api/admin/products");
        const listData = await listRes.json();
        if (listData.products) setProducts(listData.products);
      }
    } finally {
      setLoading(false);
    }
  }

  async function saveProduct(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setStatusMsg("");
    try {
      const res = await fetch("/api/admin/products", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-admin-password": adminPassword,
        },
        body: JSON.stringify({
          ...form,
          price_num: Number(form.price_num) || 0,
          sort_order: Number(form.code) || 100,
        }),
      });
      const data = await res.json();
      if (!data.ok) {
        setStatusMsg(`ผิดพลาด: ${data.message}`);
      } else {
        setStatusMsg(`บันทึกสินค้า #${form.code} เรียบร้อยแล้ว`);
        const listRes = await fetch("/api/admin/products");
        const listData = await listRes.json();
        if (listData.products) setProducts(listData.products);
        setForm({
          code: "",
          title: "",
          description: "",
          price_display: "",
          price_num: "",
          sold_text: "",
          rating: "4.9",
          category: "home",
          badge: "",
          image_url: "",
          shopee_url: "",
          lazada_url: "",
          has_video: false,
        });
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleCsvUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    const lines = text.split(/\r?\n/).filter((l) => l.trim());
    if (lines.length < 2) return;

    const parseRow = (row: string) => {
      const cols: string[] = [];
      let cur = "";
      let inQuote = false;
      for (let i = 0; i < row.length; i++) {
        const ch = row[i];
        if (ch === '"') inQuote = !inQuote;
        else if (ch === "," && !inQuote) {
          cols.push(cur.trim());
          cur = "";
        } else cur += ch;
      }
      cols.push(cur.trim());
      return cols;
    };

    const headers = parseRow(lines[0]).map((h) => h.toLowerCase());
    const idx = (names: string[]) => headers.findIndex((h) => names.some((n) => h.includes(n)));

    const iCode = idx(["code", "rank", "slot"]);
    const iTitle = idx(["product_name", "title", "name"]);
    const iPrice = idx(["price"]);
    const iSold = idx(["sold"]);
    const iRating = idx(["rating"]);
    const iShopee = idx(["affiliate_short_link", "shopee"]);
    const iLazada = idx(["lazada"]);
    const iImg = idx(["image"]);

    const items = lines.slice(1).map((line, n) => {
      const c = parseRow(line);
      const rawCode = (iCode >= 0 ? c[iCode] : String(n + 1)).replace("#", "").padStart(2, "0");
      const priceNum = Number((iPrice >= 0 ? c[iPrice] : "0").replace(/[^0-9.]/g, "")) || 0;
      return {
        code: rawCode,
        title: iTitle >= 0 ? c[iTitle] : `สินค้า #${rawCode}`,
        description: "",
        price_display: priceNum > 0 ? `฿${priceNum.toLocaleString()}` : "",
        price_num: priceNum,
        sold_text: iSold >= 0 && c[iSold] ? `ขายแล้ว ${c[iSold]}` : "",
        sold_num: 0,
        rating: iRating >= 0 && c[iRating] ? c[iRating] : "4.9",
        category: "home",
        badge: "นำเข้า CSV",
        image_url: iImg >= 0 ? c[iImg] : "",
        shopee_url: iShopee >= 0 ? c[iShopee] : "",
        lazada_url: iLazada >= 0 ? c[iLazada] : "",
        has_video: false,
        sort_order: n + 1,
      };
    });

    setLoading(true);
    try {
      const res = await fetch("/api/admin/products", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-admin-password": adminPassword,
        },
        body: JSON.stringify({ items }),
      });
      const data = await res.json();
      setStatusMsg(data.ok ? `นำเข้าจาก CSV สำเร็จ ${data.saved} รายการ` : `ผิดพลาด: ${data.message}`);
      if (data.ok) {
        const listRes = await fetch("/api/admin/products");
        const listData = await listRes.json();
        if (listData.products) setProducts(listData.products);
      }
    } finally {
      setLoading(false);
    }
  }

  async function removeProduct(code: string) {
    if (!confirm(`ลบสินค้า #${code} ออกจาก Neon DB?`)) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/products?code=${encodeURIComponent(code)}`, {
        method: "DELETE",
        headers: { "x-admin-password": adminPassword },
      });
      const data = await res.json();
      if (data.ok) {
        setProducts((prev) => prev.filter((p) => p.code !== code));
        setStatusMsg(`ลบสินค้า #${code} แล้ว`);
      } else {
        setStatusMsg(`ผิดพลาด: ${data.message}`);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 space-y-6">
      {/* Header & Neon DB Status */}
      <div className="rounded-3xl border border-orange-100 bg-white p-6 shadow-xs">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-xl font-bold text-neutral-900">
              จัดการสินค้า &amp; Neon PostgreSQL
            </h1>
            <p className="mt-1 text-xs text-neutral-500">
              เพิ่มสินค้าเดี่ยว นำเข้า CSV ทีละหลายร้อยชิ้น และติดตามยอดคลิก Shopee / Lazada / Travel
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold ${
                initialStats.connected
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-orange-50 text-[#f04e23]"
              }`}
            >
              <Database className="h-3.5 w-3.5" />
              {initialStats.connected ? "เชื่อมต่อ Neon DB แล้ว" : "โหมดข้อมูลตั้งต้น (ยังไม่เชื่อม Neon)"}
            </span>
            <button
              type="button"
              onClick={initDb}
              disabled={loading}
              className="rounded-xl bg-[#f04e23] px-4 py-2 text-xs font-semibold text-white hover:bg-[#d93f16] disabled:opacity-50 cursor-pointer"
            >
              สร้างตาราง &amp; Seed DB
            </button>
          </div>
        </div>

        {/* Stats Row */}
        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-2xl border border-neutral-100 bg-[#faf9f7] p-3.5">
            <div className="text-[11px] font-medium text-neutral-500">สินค้าทั้งหมด</div>
            <div className="mt-1 text-2xl font-bold text-neutral-900">{products.length}</div>
          </div>
          <div className="rounded-2xl border border-neutral-100 bg-[#fff7f4] p-3.5">
            <div className="flex items-center gap-1 text-[11px] font-medium text-[#f04e23]">
              <MousePointerClick className="h-3.5 w-3.5" /> คลิก Shopee
            </div>
            <div className="mt-1 text-2xl font-bold text-[#f04e23]">
              {initialStats.shopeeClicks}
            </div>
          </div>
          <div className="rounded-2xl border border-neutral-100 bg-[#faf9f7] p-3.5">
            <div className="text-[11px] font-medium text-neutral-500">คลิก Lazada</div>
            <div className="mt-1 text-2xl font-bold text-[#1d2b64]">
              {initialStats.lazadaClicks}
            </div>
          </div>
          <div className="rounded-2xl border border-neutral-100 bg-[#faf9f7] p-3.5">
            <div className="text-[11px] font-medium text-neutral-500">คลิกเที่ยว &amp; ประกัน</div>
            <div className="mt-1 text-2xl font-bold text-neutral-900">
              {initialStats.travelClicks}
            </div>
          </div>
        </div>

        <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center">
          <input
            type="password"
            value={adminPassword}
            onChange={(e) => setAdminPassword(e.target.value)}
            placeholder="รหัสผ่าน Admin (ถ้าตั้ง ADMIN_PASSWORD ใน Vercel)"
            className="w-full rounded-xl border border-neutral-200 px-3.5 py-2 text-xs outline-none focus:border-[#f04e23] sm:max-w-xs"
          />
          {statusMsg && (
            <span className="inline-flex items-center gap-1 text-xs font-semibold text-[#f04e23]">
              <CheckCircle2 className="h-4 w-4" /> {statusMsg}
            </span>
          )}
        </div>
      </div>

      {/* Add Single Product + CSV Bulk Import */}
      <div className="grid gap-6 lg:grid-cols-3">
        <form
          onSubmit={saveProduct}
          className="space-y-3 rounded-3xl border border-neutral-200/80 bg-white p-6 shadow-xs lg:col-span-2"
        >
          <h2 className="flex items-center gap-1.5 text-sm font-bold text-neutral-900">
            <Plus className="h-4 w-4 text-[#f04e23]" /> เพิ่ม / แก้ไขสินค้า (บันทึกลง Neon DB)
          </h2>
          <div className="grid gap-3 sm:grid-cols-3">
            <input
              required
              value={form.code}
              onChange={(e) => setForm({ ...form, code: e.target.value })}
              placeholder="เบอร์สินค้า เช่น 11"
              className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
            />
            <input
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="ชื่อสินค้า"
              className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23] sm:col-span-2"
            />
          </div>
          <textarea
            rows={2}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="คำอธิบายสั้นๆ จุดเด่นของสินค้า"
            className="w-full rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
          />
          <div className="grid gap-3 sm:grid-cols-3">
            <input
              value={form.price_display}
              onChange={(e) => setForm({ ...form, price_display: e.target.value })}
              placeholder="ราคาแสดงผล เช่น ฿490"
              className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
            />
            <input
              type="number"
              value={form.price_num}
              onChange={(e) => setForm({ ...form, price_num: e.target.value })}
              placeholder="ราคาตัวเลข เช่น 490"
              className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
            />
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
            >
              <option value="home">บ้าน &amp; ช่าง</option>
              <option value="cctv">กล้องวงจรปิด</option>
              <option value="kitchen">เครื่องครัว</option>
              <option value="beauty">บิวตี้ &amp; สุขภาพ</option>
              <option value="gadget">แกดเจ็ต</option>
            </select>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              value={form.image_url}
              onChange={(e) => setForm({ ...form, image_url: e.target.value })}
              placeholder="URL รูปสินค้า (.webp / .jpg)"
              className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
            />
            <input
              value={form.sold_text}
              onChange={(e) => setForm({ ...form, sold_text: e.target.value })}
              placeholder="ยอดขาย เช่น ขายแล้ว 10,000+"
              className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
            />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              value={form.shopee_url}
              onChange={(e) => setForm({ ...form, shopee_url: e.target.value })}
              placeholder="ลิงก์ Shopee Affiliate (https://s.shopee.co.th/...)"
              className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
            />
            <input
              value={form.lazada_url}
              onChange={(e) => setForm({ ...form, lazada_url: e.target.value })}
              placeholder="ลิงก์ Lazada Affiliate (https://s.lazada.co.th/...)"
              className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="rounded-xl bg-[#f04e23] px-5 py-2.5 text-xs font-bold text-white hover:bg-[#d93f16] disabled:opacity-50 cursor-pointer"
          >
            บันทึกสินค้าลง Neon DB
          </button>
        </form>

        {/* Bulk CSV Import */}
        <div className="flex flex-col justify-between rounded-3xl border border-neutral-200/80 bg-white p-6 shadow-xs">
          <div>
            <h2 className="flex items-center gap-1.5 text-sm font-bold text-neutral-900">
              <Upload className="h-4 w-4 text-[#f04e23]" /> นำเข้าสินค้าทีละเยอะๆ (CSV)
            </h2>
            <p className="mt-2 text-xs leading-relaxed text-neutral-500">
              อัปโหลดไฟล์ CSV อย่าง <code className="text-neutral-800">trending_products_nov2026.csv</code>{" "}
              หรือไฟล์ที่คัดจาก Shopee Product Feed เพื่อนำเข้า Neon PostgreSQL ทีละร้อย/พันรายการได้ทันที
            </p>
            <label className="mt-4 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-orange-200 bg-[#fffaf8] p-6 text-center transition-colors hover:bg-[#fff4f0]">
              <Upload className="h-6 w-6 text-[#f04e23]" />
              <span className="mt-2 text-xs font-semibold text-[#f04e23]">
                เลือกไฟล์ .CSV เพื่อนำเข้า
              </span>
              <input
                type="file"
                accept=".csv"
                onChange={handleCsvUpload}
                className="hidden"
              />
            </label>
          </div>
          <p className="mt-4 text-[11px] text-neutral-400">
            วิธีเชื่อม Neon ฟรี: ใน Vercel Dashboard → Storage → Create Database → เลือก Neon (Postgres) ระบบจะใส่ DATABASE_URL ให้อัตโนมัติ
          </p>
        </div>
      </div>

      {/* Product Table */}
      <div className="overflow-hidden rounded-3xl border border-neutral-200/80 bg-white shadow-xs">
        <div className="border-b border-neutral-100 px-6 py-4 text-sm font-bold text-neutral-900">
          รายการสินค้าทั้งหมด ({products.length})
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#faf9f7] text-neutral-500">
              <tr>
                <th className="px-4 py-3">เบอร์</th>
                <th className="px-4 py-3">สินค้า</th>
                <th className="px-4 py-3">ราคา</th>
                <th className="px-4 py-3">คลิก SH / LZ</th>
                <th className="px-4 py-3 text-right">จัดการ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {products.map((p) => (
                <tr key={p.code} className="hover:bg-orange-50/30">
                  <td className="px-4 py-3 font-bold text-neutral-700">#{p.code}</td>
                  <td className="max-w-xs truncate px-4 py-3 font-medium text-neutral-900">
                    {p.title}
                  </td>
                  <td className="px-4 py-3 font-semibold text-[#f04e23]">{p.price_display}</td>
                  <td className="px-4 py-3 text-neutral-500">
                    {p.clicks_shopee} / {p.clicks_lazada}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      type="button"
                      onClick={() => removeProduct(p.code)}
                      className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-neutral-400 hover:bg-red-50 hover:text-red-600 cursor-pointer"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
