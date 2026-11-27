"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  CheckCircle2,
  Database,
  ImagePlus,
  LogOut,
  MousePointerClick,
  Pencil,
  Plane,
  Plus,
  RefreshCw,
  ShoppingBag,
  Trash2,
  Upload,
  Zap,
} from "lucide-react";
import type { ClickStats, Product, SyncStatusInfo, TravelDeal } from "@/lib/types";

function compressImageToDataUrl(file: File, maxDim = 512): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        const scale = Math.min(1, maxDim / Math.max(img.width, img.height));
        const w = Math.max(1, Math.round(img.width * scale));
        const h = Math.max(1, Math.round(img.height * scale));
        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        if (!ctx) return reject(new Error("Canvas unavailable"));
        ctx.drawImage(img, 0, 0, w, h);
        const isPng = file.type === "image/png" || file.type === "image/webp";
        const out = isPng
          ? canvas.toDataURL("image/webp", 0.88)
          : canvas.toDataURL("image/jpeg", 0.86);
        resolve(out);
      };
      img.onerror = () => reject(new Error("ไม่สามารถอ่านไฟล์รูปได้"));
      img.src = String(reader.result);
    };
    reader.onerror = () => reject(new Error("ไม่สามารถโหลดไฟล์ได้"));
    reader.readAsDataURL(file);
  });
}

export function AdminClient({
  initialAuthed,
  initialStats,
  initialProducts,
  initialTravelDeals,
  initialSyncStatus,
}: {
  initialAuthed: boolean;
  initialStats: ClickStats;
  initialProducts: Product[];
  initialTravelDeals: TravelDeal[];
  initialSyncStatus: SyncStatusInfo;
}) {
  const router = useRouter();
  const [authed, setAuthed] = useState(initialAuthed);
  const [syncStatus, setSyncStatus] = useState<SyncStatusInfo>(initialSyncStatus);
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");

  const [tab, setTab] = useState<"products" | "travel">("products");
  const [products, setProducts] = useState<Product[]>(initialProducts);
  const [travelDeals, setTravelDeals] = useState<TravelDeal[]>(initialTravelDeals);
  const [statusMsg, setStatusMsg] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const [lazadaBulkText, setLazadaBulkText] = useState("");
  const [lazadaBulkBrand, setLazadaBulkBrand] = useState("");
  const [lazadaBulkCategory, setLazadaBulkCategory] = useState("auto");
  const [lazadaImportResults, setLazadaImportResults] = useState<
    Array<{
      code: string;
      brand: string;
      title: string;
      lazadaPrice: number;
      shopeePrice: number;
      lazadaUrl: string;
      commissionPct: number;
    }>
  >([]);

  const [form, setForm] = useState({
    code: "",
    brand: "",
    title: "",
    description: "",
    price_display: "",
    price_num: "",
    shopee_price: "",
    lazada_price: "",
    sold_text: "",
    rating: "4.9",
    category: "home",
    badge: "",
    image_url: "",
    shopee_url: "",
    lazada_url: "",
    lazada_item_id: "",
    has_video: false,
  });

  const [travelForm, setTravelForm] = useState({
    code: "",
    title: "",
    description: "",
    category: "จองที่พัก & เที่ยวบิน",
    highlight: "",
    cta_text: "เช็กโปรโมชัน",
    affiliate_url: "",
    logo_url: "",
    icon_key: "hotel",
    sort_order: "10",
  });

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setLoginError("");
    try {
      const res = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!data.ok) {
        setLoginError(data.message || "เข้าสู่ระบบไม่สำเร็จ");
      } else {
        setAuthed(true);
        router.refresh();
        const [pRes, tRes] = await Promise.all([
          fetch("/api/admin/products"),
          fetch("/api/admin/travel"),
        ]);
        const pData = await pRes.json();
        const tData = await tRes.json();
        if (pData.products) setProducts(pData.products);
        if (tData.deals) setTravelDeals(tData.deals);
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    await fetch("/api/admin/logout", { method: "POST" });
    setAuthed(false);
    setPassword("");
    router.refresh();
  }

  if (!authed) {
    return (
      <div className="mx-auto flex max-w-md flex-col justify-center px-4 py-16">
        <div className="rounded-3xl border border-orange-100 bg-white p-7 shadow-sm">
          <div className="mx-auto mb-4 flex items-center justify-center">
            <img
              src="/logo.svg"
              alt="Babman Picks Logo"
              width={52}
              height={52}
              className="h-13 w-13 rounded-2xl shadow-sm shadow-orange-500/20"
            />
          </div>
          <h1 className="text-center text-lg font-bold text-neutral-900">
            เข้าสู่ระบบแอดมิน Babman Picks
          </h1>
          <p className="mt-1 text-center text-xs text-neutral-500">
            จัดการสินค้า โลโก้ดีลเที่ยว และเชื่อมต่อฐานข้อมูล Neon PostgreSQL
          </p>

          <form onSubmit={handleLogin} className="mt-6 space-y-3.5">
            <div>
              <label className="mb-1 block text-xs font-semibold text-neutral-700">
                ชื่อผู้ใช้ (Username)
              </label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                className="w-full rounded-xl border border-neutral-200 px-3.5 py-2.5 text-sm outline-none focus:border-[#f04e23] focus:ring-4 focus:ring-orange-500/10"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-neutral-700">
                รหัสผ่าน (Password)
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                placeholder="กรอกรหัสผ่านแอดมิน"
                className="w-full rounded-xl border border-neutral-200 px-3.5 py-2.5 text-sm outline-none focus:border-[#f04e23] focus:ring-4 focus:ring-orange-500/10"
              />
            </div>

            {loginError && (
              <p className="rounded-xl bg-red-50 px-3 py-2 text-xs font-semibold text-red-600">
                {loginError}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-[#f04e23] py-3 text-sm font-bold text-white shadow-sm shadow-orange-500/20 transition-colors hover:bg-[#d93f16] disabled:opacity-50 cursor-pointer"
            >
              {loading ? "กำลังตรวจสอบ..." : "เข้าสู่ระบบ"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  async function runSyncNow() {
    setLoading(true);
    setStatusMsg("");
    try {
      const res = await fetch("/api/admin/sync", { method: "POST" });
      const data = await res.json();
      setStatusMsg(data.message || (data.ok ? "ซิงค์สำเร็จ" : "เกิดข้อผิดพลาด"));
      const [sRes, pRes] = await Promise.all([
        fetch("/api/admin/sync"),
        fetch("/api/admin/products"),
      ]);
      const sData = await sRes.json();
      const pData = await pRes.json();
      if (sData.status) setSyncStatus(sData.status);
      if (pData.products) setProducts(pData.products);
      router.refresh();
    } finally {
      setLoading(false);
    }
  }

  async function initDb() {
    setLoading(true);
    setStatusMsg("");
    try {
      const res = await fetch("/api/admin/init", { method: "POST" });
      const data = await res.json();
      setStatusMsg(data.message || (data.ok ? "สำเร็จ" : "เกิดข้อผิดพลาด"));
      if (data.ok) {
        const [pRes, tRes] = await Promise.all([
          fetch("/api/admin/products"),
          fetch("/api/admin/travel"),
        ]);
        const pData = await pRes.json();
        const tData = await tRes.json();
        if (pData.products) setProducts(pData.products);
        if (tData.deals) setTravelDeals(tData.deals);
        router.refresh();
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleLazadaBulkImport(e: React.FormEvent) {
    e.preventDefault();
    if (!lazadaBulkText.trim()) return;
    setLoading(true);
    setStatusMsg("");
    setLazadaImportResults([]);
    try {
      const res = await fetch("/api/admin/lazada-import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lines: lazadaBulkText,
          defaultBrand: lazadaBulkBrand,
          defaultCategory: lazadaBulkCategory,
        }),
      });
      const data = await res.json();
      setStatusMsg(data.message || (data.ok ? "นำเข้าสำเร็จ" : "นำเข้าไม่สำเร็จ"));
      if (data.ok) {
        setLazadaImportResults(data.imported || []);
        setLazadaBulkText("");
        const listRes = await fetch("/api/admin/products");
        const listData = await listRes.json();
        if (listData.products) setProducts(listData.products);
        router.refresh();
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          price_num: Number(form.price_num) || 0,
          shopee_price: Number(form.shopee_price) || 0,
          lazada_price: Number(form.lazada_price) || 0,
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
      }
    } finally {
      setLoading(false);
    }
  }

  async function saveTravel(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setStatusMsg("");
    try {
      const res = await fetch("/api/admin/travel", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...travelForm,
          sort_order: Number(travelForm.sort_order) || 50,
        }),
      });
      const data = await res.json();
      if (!data.ok) {
        setStatusMsg(`ผิดพลาด: ${data.message}`);
      } else {
        setStatusMsg(`บันทึกดีล ${travelForm.code} พร้อมโลโก้เรียบร้อยแล้ว`);
        const listRes = await fetch("/api/admin/travel");
        const listData = await listRes.json();
        if (listData.deals) setTravelDeals(listData.deals);
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleProductImgFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const dataUrl = await compressImageToDataUrl(file, 640);
      setForm((f) => ({ ...f, image_url: dataUrl }));
      setStatusMsg("เตรียมรูปสินค้าเรียบร้อย — กดปุ่มบันทึกสินค้าเพื่อเซฟลง Neon DB");
    } catch (err) {
      setStatusMsg(err instanceof Error ? err.message : "อัปโหลดรูปไม่สำเร็จ");
    }
  }

  async function handleTravelLogoFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const dataUrl = await compressImageToDataUrl(file, 360);
      setTravelForm((f) => ({ ...f, logo_url: dataUrl }));
      setStatusMsg("เตรียมโลโก้เรียบร้อย — กดปุ่มบันทึกดีลเที่ยวเพื่อเซฟลง Neon DB");
    } catch (err) {
      setStatusMsg(err instanceof Error ? err.message : "อัปโหลดโลโก้ไม่สำเร็จ");
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
    const idx = (names: string[]) =>
      headers.findIndex((h) => names.some((n) => h.includes(n)));

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
      const rawCode = (iCode >= 0 ? c[iCode] : String(n + 1))
        .replace("#", "")
        .padStart(2, "0");
      const priceNum =
        Number((iPrice >= 0 ? c[iPrice] : "0").replace(/[^0-9.]/g, "")) || 0;
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items }),
      });
      const data = await res.json();
      setStatusMsg(
        data.ok
          ? `นำเข้าจาก CSV สำเร็จ ${data.saved} รายการ`
          : `ผิดพลาด: ${data.message}`
      );
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

  async function removeTravelDeal(code: string) {
    if (!confirm(`ลบดีล ${code} ออกจาก Neon DB?`)) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/travel?code=${encodeURIComponent(code)}`, {
        method: "DELETE",
      });
      const data = await res.json();
      if (data.ok) {
        setTravelDeals((prev) => prev.filter((d) => d.code !== code));
        setStatusMsg(`ลบดีล ${code} แล้ว`);
      } else {
        setStatusMsg(`ผิดพลาด: ${data.message}`);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 space-y-6">
      {/* Top Status & Controls */}
      <div className="rounded-3xl border border-orange-100 bg-white p-6 shadow-xs">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-xl font-bold text-neutral-900">
              Admin Dashboard • Babman Picks
            </h1>
            <p className="mt-1 text-xs text-neutral-500">
              จัดการสินค้า โลโก้หน้าเที่ยว &amp; ประกัน นำเข้า CSV และดูยอดคลิก Neon PostgreSQL
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold ${
                initialStats.connected
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-orange-50 text-[#f04e23]"
              }`}
            >
              <Database className="h-3.5 w-3.5" />
              {initialStats.connected
                ? "เชื่อมต่อ Neon DB แล้ว"
                : "โหมดตั้งต้น (ยังไม่เชื่อม Neon)"}
            </span>
            <button
              type="button"
              onClick={runSyncNow}
              disabled={loading}
              className="inline-flex items-center gap-1.5 rounded-xl border border-orange-200 bg-[#fff4f0] px-3.5 py-2 text-xs font-semibold text-[#f04e23] hover:bg-orange-100 disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
              ซิงค์ราคาล่าสุด
            </button>
            <button
              type="button"
              onClick={initDb}
              disabled={loading}
              className="rounded-xl bg-[#f04e23] px-3.5 py-2 text-xs font-semibold text-white hover:bg-[#d93f16] disabled:opacity-50 cursor-pointer"
            >
              สร้างตาราง &amp; Seed DB
            </button>
            <button
              type="button"
              onClick={handleLogout}
              className="inline-flex items-center gap-1 rounded-xl border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-600 hover:bg-neutral-50 cursor-pointer"
            >
              <LogOut className="h-3.5 w-3.5" />
              ออก
            </button>
          </div>
        </div>

        {/* Metrics */}
        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-2xl border border-neutral-100 bg-[#faf9f7] p-3.5">
            <div className="text-[11px] font-medium text-neutral-500">สินค้า / ดีลเที่ยว</div>
            <div className="mt-1 text-2xl font-bold text-neutral-900">
              {products.length} / {travelDeals.length}
            </div>
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

        {/* Auto-Sync API Status Strip */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-neutral-100 bg-[#faf9f7] px-4 py-3 text-xs">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-bold text-neutral-700">Auto-Sync ทุกวัน 06:00 น.:</span>
            <span
              className={`rounded-full px-2.5 py-0.5 font-semibold ${
                syncStatus.lazadaConfigured
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-amber-50 text-amber-700"
              }`}
            >
              Lazada API: {syncStatus.lazadaConfigured ? "พร้อมซิงค์" : "รออนุมัติคีย์"}
            </span>
            <span
              className={`rounded-full px-2.5 py-0.5 font-semibold ${
                syncStatus.shopeeConfigured
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-amber-50 text-amber-700"
              }`}
            >
              Shopee API: {syncStatus.shopeeConfigured ? "พร้อมซิงค์" : "รอปลดล็อกสิทธิ์"}
            </span>
          </div>
          {syncStatus.lastSyncMessage && (
            <span className="text-[11px] text-neutral-500 truncate max-w-md">
              ล่าสุด: {syncStatus.lastSyncMessage}
            </span>
          )}
        </div>

        {statusMsg && (
          <div className="mt-4 inline-flex items-center gap-1.5 rounded-xl bg-orange-50 px-3.5 py-2 text-xs font-semibold text-[#f04e23]">
            <CheckCircle2 className="h-4 w-4" /> {statusMsg}
          </div>
        )}
      </div>

      {/* Mode Switcher */}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setTab("products")}
          className={`inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-xs font-bold cursor-pointer ${
            tab === "products"
              ? "bg-[#f04e23] text-white"
              : "border border-neutral-200 bg-white text-neutral-600"
          }`}
        >
          <ShoppingBag className="h-3.5 w-3.5" />
          จัดการสินค้า ({products.length})
        </button>
        <button
          type="button"
          onClick={() => setTab("travel")}
          className={`inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-xs font-bold cursor-pointer ${
            tab === "travel"
              ? "bg-[#f04e23] text-white"
              : "border border-neutral-200 bg-white text-neutral-600"
          }`}
        >
          <Plane className="h-3.5 w-3.5" />
          จัดการดีลเที่ยว &amp; อัปโหลดโลโก้ ({travelDeals.length})
        </button>
      </div>

      {tab === "products" ? (
        <>
          {/* Fast Lazada Open API Bulk Auto-Importer */}
          <form
            onSubmit={handleLazadaBulkImport}
            className="rounded-3xl border border-indigo-100 bg-gradient-to-br from-[#f6f8ff] to-white p-5 shadow-xs sm:p-6"
          >
            <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
              <div>
                <h2 className="flex items-center gap-1.5 text-sm font-bold text-[#101d6b]">
                  <Zap className="h-4 w-4 fill-[#101d6b]" />
                  ดูดสินค้า Lazada ทีละหลายตัว (Auto-GetLink ผ่าน Lazada API)
                </h2>
                <p className="mt-0.5 text-xs text-neutral-500">
                  วางเลข Lazada Item ID หรือ URL สินค้า (บรรทัดละ 1 ตัว) → ระบบดึงรูป แบรนด์ ราคาสด + เสกลิงก์{" "}
                  <code className="rounded bg-indigo-50 px-1 text-[#101d6b]">s.lazada.co.th</code>{" "}
                  ให้อัตโนมัติทันที
                </p>
              </div>
              <span className="inline-flex shrink-0 items-center rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-bold text-emerald-700">
                รองรับทีละ 20–50 รายการ
              </span>
            </div>

            <textarea
              rows={4}
              value={lazadaBulkText}
              onChange={(e) => setLazadaBulkText(e.target.value)}
              placeholder={`ตัวอย่างการวาง (บรรทัดละ 1 สินค้า):\n4831884381\nhttps://www.lazada.co.th/products/...-i16373052678.html\n4831884381 | https://s.shopee.co.th/xxx | 520 | Breeze | home\n#08 | 5852773665   (จับคู่เติมลิงก์ Lazada ให้สินค้าเบอร์เดิม)`}
              className="mt-3 w-full rounded-2xl border border-indigo-200/80 bg-white p-3 font-mono text-xs text-neutral-800 outline-none placeholder:font-sans placeholder:text-neutral-400 focus:border-[#101d6b] focus:ring-4 focus:ring-indigo-500/10"
            />

            <div className="mt-3 flex flex-col gap-2.5 sm:flex-row sm:items-center">
              <input
                value={lazadaBulkBrand}
                onChange={(e) => setLazadaBulkBrand(e.target.value)}
                placeholder="ชื่อแบรนด์ (เว้นว่างให้ดึงจาก Lazada อัตโนมัติ)"
                className="flex-1 rounded-xl border border-neutral-200 bg-white px-3 py-2 text-xs outline-none focus:border-[#101d6b]"
              />
              <select
                value={lazadaBulkCategory}
                onChange={(e) => setLazadaBulkCategory(e.target.value)}
                className="rounded-xl border border-neutral-200 bg-white px-3 py-2 text-xs outline-none focus:border-[#101d6b]"
              >
                <option value="auto">หมวดหมู่: แยกให้อัตโนมัติ</option>
                <option value="home">บ้าน &amp; ช่าง</option>
                <option value="kitchen">เครื่องครัว</option>
                <option value="beauty">บิวตี้ &amp; สุขภาพ</option>
                <option value="cctv">กล้องวงจรปิด</option>
                <option value="gadget">แกดเจ็ต</option>
              </select>
              <button
                type="submit"
                disabled={loading || !lazadaBulkText.trim()}
                className="inline-flex shrink-0 items-center justify-center gap-1.5 rounded-xl bg-[#101d6b] px-4 py-2.5 text-xs font-bold text-white shadow-xs transition-colors hover:bg-[#0b144d] disabled:opacity-50 cursor-pointer"
              >
                <Zap className="h-3.5 w-3.5" />
                {loading ? "กำลังดึงข้อมูล..." : "ดูดสินค้า + เสกลิงก์เลย"}
              </button>
            </div>

            {lazadaImportResults.length > 0 && (
              <div className="mt-3 space-y-1.5 rounded-2xl border border-emerald-200 bg-emerald-50/50 p-3 text-xs">
                <div className="font-bold text-emerald-800">
                  นำเข้าสำเร็จ {lazadaImportResults.length} รายการ:
                </div>
                {lazadaImportResults.map((item) => (
                  <div
                    key={item.code}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-white px-2.5 py-1.5 text-[11px]"
                  >
                    <span className="font-semibold text-neutral-900 truncate max-w-md">
                      #{item.code} [{item.brand}] {item.title}
                    </span>
                    <span className="font-bold text-[#101d6b]">
                      ฿{item.lazadaPrice.toLocaleString()} (คอมฯ {item.commissionPct}%)
                    </span>
                  </div>
                ))}
              </div>
            )}
          </form>

          <div className="grid gap-6 lg:grid-cols-3">
            <form
              onSubmit={saveProduct}
              className="space-y-3 rounded-3xl border border-neutral-200/80 bg-white p-6 shadow-xs lg:col-span-2"
            >
              <h2 className="flex items-center gap-1.5 text-sm font-bold text-neutral-900">
                <Plus className="h-4 w-4 text-[#f04e23]" /> เพิ่ม / แก้ไขสินค้า
              </h2>
              <div className="grid gap-3 sm:grid-cols-4">
                <input
                  required
                  value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                  placeholder="เบอร์ เช่น 11"
                  className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
                />
                <input
                  value={form.brand}
                  onChange={(e) => setForm({ ...form, brand: e.target.value })}
                  placeholder="แบรนด์ เช่น Seagull, NIVEA"
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
              <div className="grid gap-3 sm:grid-cols-4">
                <input
                  type="number"
                  value={form.shopee_price}
                  onChange={(e) => setForm({ ...form, shopee_price: e.target.value })}
                  placeholder="ราคา Shopee (฿)"
                  className="rounded-xl border border-orange-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
                />
                <input
                  type="number"
                  value={form.lazada_price}
                  onChange={(e) => setForm({ ...form, lazada_price: e.target.value })}
                  placeholder="ราคา Lazada (฿)"
                  className="rounded-xl border border-indigo-200 px-3 py-2 text-xs outline-none focus:border-[#101d6b]"
                />
                <input
                  value={form.lazada_item_id}
                  onChange={(e) => setForm({ ...form, lazada_item_id: e.target.value })}
                  placeholder="Lazada Item ID (ซิงค์ API)"
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
                <div className="flex items-center gap-2">
                  <input
                    value={form.image_url}
                    onChange={(e) => setForm({ ...form, image_url: e.target.value })}
                    placeholder="วาง URL รูป หรือกดอัปโหลด →"
                    className="flex-1 rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
                  />
                  <label className="inline-flex shrink-0 cursor-pointer items-center gap-1 rounded-xl border border-orange-200 bg-[#fff4f0] px-3 py-2 text-xs font-semibold text-[#f04e23] hover:bg-orange-100">
                    <ImagePlus className="h-3.5 w-3.5" />
                    <span>อัปโหลด</span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleProductImgFile}
                      className="hidden"
                    />
                  </label>
                </div>
                <input
                  value={form.sold_text}
                  onChange={(e) => setForm({ ...form, sold_text: e.target.value })}
                  placeholder="ยอดขาย เช่น ขายแล้ว 10,000+"
                  className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
                />
              </div>
              {form.image_url && (
                <div className="flex items-center gap-3 rounded-xl border border-neutral-100 bg-[#faf9f7] p-2">
                  <img
                    src={form.image_url}
                    alt="preview"
                    className="h-12 w-12 rounded-lg object-cover border border-neutral-200 bg-white"
                  />
                  <span className="text-[11px] text-neutral-500">ตัวอย่างรูปสินค้าที่จะแสดง</span>
                </div>
              )}
              <div className="grid gap-3 sm:grid-cols-2">
                <input
                  value={form.shopee_url}
                  onChange={(e) => setForm({ ...form, shopee_url: e.target.value })}
                  placeholder="ลิงก์ Shopee Affiliate"
                  className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
                />
                <input
                  value={form.lazada_url}
                  onChange={(e) => setForm({ ...form, lazada_url: e.target.value })}
                  placeholder="ลิงก์ Lazada Affiliate"
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
                  <Upload className="h-4 w-4 text-[#f04e23]" /> นำเข้าทีละเยอะๆ (CSV)
                </h2>
                <p className="mt-2 text-xs leading-relaxed text-neutral-500">
                  อัปโหลดไฟล์ CSV จาก Shopee/Lazada เพื่อนำเข้าสินค้าเข้า Neon PostgreSQL ทีละร้อย/พันรายการ
                </p>
                <label className="mt-4 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-orange-200 bg-[#fffaf8] p-6 text-center hover:bg-[#fff4f0]">
                  <Upload className="h-6 w-6 text-[#f04e23]" />
                  <span className="mt-2 text-xs font-semibold text-[#f04e23]">
                    เลือกไฟล์ .CSV เพื่อนำเข้า
                  </span>
                  <input type="file" accept=".csv" onChange={handleCsvUpload} className="hidden" />
                </label>
              </div>
              <p className="mt-4 text-[11px] text-neutral-400">
                เคล็ดลับ: กดปุ่มดินสอในตารางด้านล่างเพื่อดึงสินค้าเดิมมาแก้รูปหรือลิงก์ได้ทันที
              </p>
            </div>
          </div>

          <div className="overflow-hidden rounded-3xl border border-neutral-200/80 bg-white shadow-xs">
            <div className="border-b border-neutral-100 px-6 py-4 text-sm font-bold text-neutral-900">
              รายการสินค้า ({products.length})
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#faf9f7] text-neutral-500">
                  <tr>
                    <th className="px-4 py-3">รูป</th>
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
                      <td className="px-4 py-2.5">
                        {p.image_url ? (
                          <img
                            src={p.image_url}
                            alt={p.title}
                            className="h-9 w-9 rounded-lg object-cover border border-neutral-200"
                          />
                        ) : (
                          <div className="h-9 w-9 rounded-lg bg-orange-50" />
                        )}
                      </td>
                      <td className="px-4 py-2.5 font-bold text-neutral-700">#{p.code}</td>
                      <td className="max-w-xs truncate px-4 py-2.5 font-medium text-neutral-900">
                        {p.brand && (
                          <span className="mr-1.5 rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] font-bold text-neutral-600">
                            {p.brand}
                          </span>
                        )}
                        {p.title}
                      </td>
                      <td className="px-4 py-2.5 font-semibold whitespace-nowrap">
                        <span className="text-[#f04e23]">
                          {p.shopee_price > 0 ? `SH ฿${p.shopee_price.toLocaleString()}` : "—"}
                        </span>
                        <span className="mx-1 text-neutral-300">/</span>
                        <span className="text-[#101d6b]">
                          {p.lazada_price > 0 ? `LZ ฿${p.lazada_price.toLocaleString()}` : "—"}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-neutral-500">
                        {p.clicks_shopee} / {p.clicks_lazada}
                      </td>
                      <td className="px-4 py-2.5 text-right whitespace-nowrap">
                        <button
                          type="button"
                          onClick={() =>
                            setForm({
                              code: p.code,
                              brand: p.brand || "",
                              title: p.title,
                              description: p.description,
                              price_display: p.price_display,
                              price_num: String(p.price_num),
                              shopee_price: p.shopee_price ? String(p.shopee_price) : "",
                              lazada_price: p.lazada_price ? String(p.lazada_price) : "",
                              sold_text: p.sold_text,
                              rating: p.rating,
                              category: p.category,
                              badge: p.badge,
                              image_url: p.image_url,
                              shopee_url: p.shopee_url,
                              lazada_url: p.lazada_url,
                              lazada_item_id: p.lazada_item_id || "",
                              has_video: p.has_video,
                            })
                          }
                          className="mr-1 inline-flex items-center rounded-lg px-2 py-1 text-neutral-500 hover:bg-orange-50 hover:text-[#f04e23] cursor-pointer"
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => removeProduct(p.code)}
                          className="inline-flex items-center rounded-lg px-2 py-1 text-neutral-400 hover:bg-red-50 hover:text-red-600 cursor-pointer"
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
        </>
      ) : (
        <>
          {/* Travel & Insurance Deal Editor + Logo Uploader */}
          <form
            onSubmit={saveTravel}
            className="space-y-3 rounded-3xl border border-neutral-200/80 bg-white p-6 shadow-xs"
          >
            <h2 className="flex items-center gap-1.5 text-sm font-bold text-neutral-900">
              <ImagePlus className="h-4 w-4 text-[#f04e23]" /> เพิ่ม / แก้ไขดีลเที่ยว &amp; อัปโหลดโลโก้แบรนด์
            </h2>
            <div className="grid gap-3 sm:grid-cols-3">
              <input
                required
                value={travelForm.code}
                onChange={(e) => setTravelForm({ ...travelForm, code: e.target.value })}
                placeholder="รหัส เช่น T01 หรือ T08"
                className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
              />
              <input
                required
                value={travelForm.title}
                onChange={(e) => setTravelForm({ ...travelForm, title: e.target.value })}
                placeholder="ชื่อดีล เช่น Gother — จองโรงแรมลดแรง"
                className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23] sm:col-span-2"
              />
            </div>
            <textarea
              rows={2}
              value={travelForm.description}
              onChange={(e) => setTravelForm({ ...travelForm, description: e.target.value })}
              placeholder="คำอธิบายดีล"
              className="w-full rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
            />
            <div className="grid gap-3 sm:grid-cols-3">
              <input
                value={travelForm.category}
                onChange={(e) => setTravelForm({ ...travelForm, category: e.target.value })}
                placeholder="หมวด เช่น จองที่พัก"
                className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
              />
              <input
                value={travelForm.highlight}
                onChange={(e) => setTravelForm({ ...travelForm, highlight: e.target.value })}
                placeholder="จุดเด่น เช่น โรงแรม • รถเช่า"
                className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
              />
              <input
                value={travelForm.cta_text}
                onChange={(e) => setTravelForm({ ...travelForm, cta_text: e.target.value })}
                placeholder="ข้อความปุ่ม เช่น เช็กราคา Gother"
                className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
              />
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <input
                required
                value={travelForm.affiliate_url}
                onChange={(e) => setTravelForm({ ...travelForm, affiliate_url: e.target.value })}
                placeholder="ลิงก์ Affiliate (https://atth.me/...)"
                className="rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
              />
              <div className="flex items-center gap-2">
                <input
                  value={travelForm.logo_url}
                  onChange={(e) => setTravelForm({ ...travelForm, logo_url: e.target.value })}
                  placeholder="URL โลโก้ หรือกดอัปโหลดรูป →"
                  className="flex-1 rounded-xl border border-neutral-200 px-3 py-2 text-xs outline-none focus:border-[#f04e23]"
                />
                <label className="inline-flex shrink-0 cursor-pointer items-center gap-1 rounded-xl border border-orange-200 bg-[#fff4f0] px-3 py-2 text-xs font-semibold text-[#f04e23] hover:bg-orange-100">
                  <ImagePlus className="h-3.5 w-3.5" />
                  <span>อัปโหลดโลโก้</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleTravelLogoFile}
                    className="hidden"
                  />
                </label>
              </div>
            </div>
            {travelForm.logo_url && (
              <div className="flex items-center gap-3 rounded-xl border border-neutral-100 bg-[#faf9f7] p-2.5">
                <img
                  src={travelForm.logo_url}
                  alt="logo preview"
                  className="h-12 w-12 rounded-xl border border-neutral-200 bg-white p-1 object-contain"
                />
                <span className="text-[11px] text-neutral-500">ตัวอย่างโลโก้ที่จะแสดงบนหน้า /travel</span>
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-[#f04e23] px-5 py-2.5 text-xs font-bold text-white hover:bg-[#d93f16] disabled:opacity-50 cursor-pointer"
            >
              บันทึกดีลเที่ยว &amp; โลโก้ลง Neon DB
            </button>
          </form>

          {/* Existing Travel Deals Table */}
          <div className="overflow-hidden rounded-3xl border border-neutral-200/80 bg-white shadow-xs">
            <div className="border-b border-neutral-100 px-6 py-4 text-sm font-bold text-neutral-900">
              ดีลเที่ยว &amp; ประกันทั้งหมด ({travelDeals.length}) — กดปุ่มดินสอเพื่อเปลี่ยนโลโก้ได้ทันที
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#faf9f7] text-neutral-500">
                  <tr>
                    <th className="px-4 py-3">โลโก้</th>
                    <th className="px-4 py-3">รหัส</th>
                    <th className="px-4 py-3">ชื่อดีล</th>
                    <th className="px-4 py-3">คลิก</th>
                    <th className="px-4 py-3 text-right">จัดการ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100">
                  {travelDeals.map((d) => (
                    <tr key={d.code} className="hover:bg-orange-50/30">
                      <td className="px-4 py-2.5">
                        {d.logo_url ? (
                          <img
                            src={d.logo_url}
                            alt={d.title}
                            className="h-10 w-10 rounded-xl border border-neutral-200 bg-white p-1 object-contain"
                          />
                        ) : (
                          <div className="h-10 w-10 rounded-xl bg-orange-50" />
                        )}
                      </td>
                      <td className="px-4 py-2.5 font-bold text-neutral-700">{d.code}</td>
                      <td className="max-w-xs truncate px-4 py-2.5 font-medium text-neutral-900">
                        {d.title}
                      </td>
                      <td className="px-4 py-2.5 text-neutral-500">{d.clicks}</td>
                      <td className="px-4 py-2.5 text-right whitespace-nowrap">
                        <button
                          type="button"
                          onClick={() =>
                            setTravelForm({
                              code: d.code,
                              title: d.title,
                              description: d.description,
                              category: d.category,
                              highlight: d.highlight,
                              cta_text: d.cta_text,
                              affiliate_url: d.affiliate_url,
                              logo_url: d.logo_url,
                              icon_key: d.icon_key,
                              sort_order: String(d.sort_order),
                            })
                          }
                          className="mr-1 inline-flex items-center rounded-lg px-2 py-1 text-neutral-500 hover:bg-orange-50 hover:text-[#f04e23] cursor-pointer"
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => removeTravelDeal(d.code)}
                          className="inline-flex items-center rounded-lg px-2 py-1 text-neutral-400 hover:bg-red-50 hover:text-red-600 cursor-pointer"
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
        </>
      )}
    </div>
  );
}
