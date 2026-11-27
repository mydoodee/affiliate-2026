"use client";

import { useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  CheckCircle2,
  ExternalLink,
  Plane,
  PlayCircle,
  Scale,
  Search,
  Sparkles,
  Star,
  Store,
  Tag,
  Trophy,
  X,
  Zap,
} from "lucide-react";
import type { Product } from "@/lib/types";

const CATEGORIES = [
  { key: "all", label: "ทุกหมวด" },
  { key: "compare", label: "เทียบ 2 เจ้า" },
  { key: "video", label: "มีคลิปรีวิว" },
  { key: "cctv", label: "กล้องวงจรปิด" },
  { key: "home", label: "บ้าน & ช่าง" },
  { key: "kitchen", label: "เครื่องครัว" },
  { key: "beauty", label: "บิวตี้ & สุขภาพ" },
  { key: "gadget", label: "แกดเจ็ต" },
];

const PAGE_SIZE = 24;

function getPriceMeta(p: Product) {
  const sh = p.shopee_price > 0 ? p.shopee_price : p.shopee_url ? p.price_num : 0;
  const lz = p.lazada_price > 0 ? p.lazada_price : 0;
  const bothPriced = Boolean(p.shopee_url && p.lazada_url && sh > 0 && lz > 0);
  const diff = bothPriced ? Math.abs(sh - lz) : 0;
  let winner: "shopee" | "lazada" | "tie" | "single" = "single";
  if (bothPriced) {
    if (lz < sh) winner = "lazada";
    else if (sh < lz) winner = "shopee";
    else winner = "tie";
  }
  const bestPrice = bothPriced ? Math.min(sh, lz) : sh || lz || p.price_num;
  return { sh, lz, bothPriced, diff, winner, bestPrice };
}

export function StorefrontClient({ products }: { products: Product[] }) {
  const [query, setQuery] = useState("");
  const [selectedBrand, setSelectedBrand] = useState<string>("all");
  const [category, setCategory] = useState("all");
  const [sortBy, setSortBy] = useState<"featured" | "savings" | "price_asc" | "bestseller">(
    "featured"
  );
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const [brandSheetOpen, setBrandSheetOpen] = useState(false);
  const [brandSearch, setBrandSearch] = useState("");
  const listSectionRef = useRef<HTMLElement | null>(null);

  // Build dynamic brand index with counts & max savings
  const brands = useMemo(() => {
    const map = new Map<
      string,
      { name: string; count: number; dualCount: number; maxSavings: number; sampleImg: string }
    >();
    for (const p of products) {
      const name = (p.brand || "อื่นๆ").trim();
      const meta = getPriceMeta(p);
      const cur = map.get(name) ?? {
        name,
        count: 0,
        dualCount: 0,
        maxSavings: 0,
        sampleImg: p.image_url,
      };
      cur.count += 1;
      if (meta.bothPriced) cur.dualCount += 1;
      if (meta.diff > cur.maxSavings) cur.maxSavings = meta.diff;
      if (!cur.sampleImg && p.image_url) cur.sampleImg = p.image_url;
      map.set(name, cur);
    }
    return Array.from(map.values()).sort(
      (a, b) => b.dualCount - a.dualCount || b.maxSavings - a.maxSavings || b.count - a.count
    );
  }, [products]);

  const dualTotal = useMemo(
    () => products.filter((p) => getPriceMeta(p).bothPriced).length,
    [products]
  );

  const filteredBrandsForSheet = useMemo(() => {
    const q = brandSearch.trim().toLowerCase();
    if (!q) return brands;
    return brands.filter((b) => b.name.toLowerCase().includes(q));
  }, [brands, brandSearch]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = products.filter((p) => {
      const brandName = (p.brand || "อื่นๆ").trim();
      const meta = getPriceMeta(p);
      const matchBrand = selectedBrand === "all" || brandName === selectedBrand;
      const matchCat =
        category === "all" ||
        (category === "compare"
          ? meta.bothPriced
          : category === "video"
          ? p.has_video
          : p.category === category);
      const matchQ =
        !q ||
        p.code.toLowerCase().includes(q) ||
        brandName.toLowerCase().includes(q) ||
        p.title.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.badge.toLowerCase().includes(q);
      return matchBrand && matchCat && matchQ;
    });

    const sorted = [...list];
    if (sortBy === "savings") {
      sorted.sort((a, b) => getPriceMeta(b).diff - getPriceMeta(a).diff);
    } else if (sortBy === "bestseller") {
      sorted.sort((a, b) => b.sold_num - a.sold_num);
    } else if (sortBy === "price_asc") {
      sorted.sort((a, b) => getPriceMeta(a).bestPrice - getPriceMeta(b).bestPrice);
    } else {
      sorted.sort((a, b) => a.sort_order - b.sort_order);
    }
    return sorted;
  }, [products, query, selectedBrand, category, sortBy]);

  const visibleProducts = filtered.slice(0, visibleCount);
  const hasMore = visibleCount < filtered.length;

  function pickBrand(name: string) {
    setSelectedBrand(name);
    setVisibleCount(PAGE_SIZE);
    setBrandSheetOpen(false);
    setBrandSearch("");
    setTimeout(() => {
      listSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 60);
  }

  return (
    <div className="mx-auto max-w-6xl px-3.5 pb-24 pt-4 sm:px-6 sm:pb-12 sm:pt-7">
      {/* Mobile-First Price Comparison Hero */}
      <section className="relative overflow-hidden rounded-3xl border border-orange-100 bg-white p-5 shadow-xs sm:p-8">
        <div
          className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full opacity-55 blur-3xl"
          style={{ background: "radial-gradient(circle, #ffd6c4 0%, transparent 70%)" }}
        />
        <div className="relative z-10 flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
          <div className="max-w-xl">
            <div className="mb-2.5 inline-flex items-center gap-1.5 rounded-full border border-orange-200/80 bg-[#fff4f0] px-3 py-1 text-[11px] font-bold text-[#f04e23] sm:text-xs">
              <Zap className="h-3.5 w-3.5 fill-[#f04e23]" />
              เทียบราคา 2 เจ้าใหญ่ • ซิงค์ Lazada API สดทุกเช้า 06:00 น.
            </div>
            <h1 className="text-[22px] font-bold leading-snug tracking-tight text-neutral-900 sm:text-3xl">
              เช็กราคา <span className="text-[#f04e23]">Shopee</span> vs{" "}
              <span className="text-[#101d6b]">Lazada</span> ของแท้ก่อนกดซื้อ
            </h1>
            <p className="mt-2 text-[13px] leading-relaxed text-neutral-600 sm:text-[15px]">
              กดเลือก <strong className="font-semibold text-neutral-900">1 แบรนด์</strong>{" "}
              ระบบเทียบราคา 2 แพลตฟอร์มให้ดูทันที เจ้าไหนถูกกว่ากดซื้อร้านทางการได้เลย
            </p>

            {/* Primary Mobile Thumb CTA + Travel Shortcut */}
            <div className="mt-4 flex flex-col gap-2.5 sm:flex-row sm:items-center">
              <button
                type="button"
                onClick={() => setBrandSheetOpen(true)}
                className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#f04e23] px-5 py-3.5 text-sm font-bold text-white shadow-sm shadow-orange-500/25 transition-all active:scale-[0.99] hover:bg-[#d93f16] sm:w-auto cursor-pointer"
              >
                <Scale className="h-4 w-4" />
                <span>กดเลือกแบรนด์เทียบราคา ({brands.length} แบรนด์)</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setSelectedBrand("all");
                  setCategory("compare");
                  setSortBy("savings");
                  listSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
                }}
                className="inline-flex w-full items-center justify-center gap-1.5 rounded-2xl border border-emerald-200 bg-emerald-50/70 px-4 py-3 text-xs font-bold text-emerald-700 transition-colors hover:bg-emerald-100 sm:w-auto sm:text-sm cursor-pointer"
              >
                <Trophy className="h-4 w-4" />
                <span>ดูรุ่นที่เทียบ 2 เจ้าได้ทันที ({dualTotal})</span>
              </button>
            </div>
          </div>

          {/* Compact Travel Deal Banner */}
          <Link
            href="/travel"
            className="group flex shrink-0 items-center justify-between gap-3 rounded-2xl border border-orange-200/70 bg-gradient-to-br from-[#fff7f4] to-white p-3.5 transition-all hover:border-[#f04e23]/50 hover:shadow-sm sm:p-4 lg:w-76"
          >
            <div>
              <div className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-[#f04e23]">
                <Plane className="h-3 w-3" />
                เทียบดีลเที่ยว &amp; ประกัน
              </div>
              <div className="mt-0.5 text-[13px] font-bold text-neutral-900">
                Trip · Traveloka · Klook · MSIG
              </div>
              <p className="text-[11px] text-neutral-500">เช็กราคาโรงแรม ตั๋ว &amp; ประกัน 8 เจ้า</p>
            </div>
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#f04e23] text-white transition-transform group-hover:translate-x-0.5">
              <ArrowRight className="h-4 w-4" />
            </div>
          </Link>
        </div>

        {/* 3-Step Mini How-To Strip (Ultra-clear on mobile) */}
        <div className="mt-5 grid grid-cols-3 gap-2 border-t border-neutral-100 pt-4 text-center sm:text-left">
          <div className="flex flex-col items-center gap-1 sm:flex-row sm:items-center sm:gap-2">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-orange-100 text-[11px] font-bold text-[#f04e23]">
              1
            </span>
            <span className="text-[11px] font-semibold text-neutral-700 sm:text-xs">
              เลือกแบรนด์
            </span>
          </div>
          <div className="flex flex-col items-center gap-1 sm:flex-row sm:items-center sm:gap-2">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100 text-[11px] font-bold text-[#101d6b]">
              2
            </span>
            <span className="text-[11px] font-semibold text-neutral-700 sm:text-xs">
              เทียบราคา 2 เจ้า
            </span>
          </div>
          <div className="flex flex-col items-center gap-1 sm:flex-row sm:items-center sm:gap-2">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-[11px] font-bold text-emerald-700">
              3
            </span>
            <span className="text-[11px] font-semibold text-neutral-700 sm:text-xs">
              กดซื้อร้านถูกสุด
            </span>
          </div>
        </div>
      </section>

      {/* Step 1: Horizontal Swipeable Brand Selector Strip */}
      <section className="mt-5">
        <div className="mb-2.5 flex items-center justify-between">
          <h2 className="flex items-center gap-1.5 text-sm font-bold text-neutral-900">
            <Store className="h-4 w-4 text-[#f04e23]" />
            เลือกแบรนด์เพื่อเทียบราคา
          </h2>
          <button
            type="button"
            onClick={() => setBrandSheetOpen(true)}
            className="text-xs font-semibold text-[#f04e23] hover:underline cursor-pointer"
          >
            ดูทั้งหมด ({brands.length}) →
          </button>
        </div>

        <div className="no-scrollbar flex items-stretch gap-2 overflow-x-auto pb-1.5">
          <button
            type="button"
            onClick={() => {
              setSelectedBrand("all");
              setVisibleCount(PAGE_SIZE);
            }}
            className={`flex shrink-0 flex-col justify-center rounded-2xl border px-3.5 py-2.5 text-left transition-all cursor-pointer ${
              selectedBrand === "all"
                ? "border-[#f04e23] bg-[#f04e23] text-white shadow-sm shadow-orange-500/20"
                : "border-neutral-200 bg-white text-neutral-800 hover:border-orange-200"
            }`}
          >
            <span className="text-xs font-bold">ทุกแบรนด์</span>
            <span
              className={`text-[10px] ${
                selectedBrand === "all" ? "text-orange-100" : "text-neutral-400"
              }`}
            >
              {products.length} รุ่น
            </span>
          </button>

          {brands.map((b) => {
            const active = selectedBrand === b.name;
            return (
              <button
                key={b.name}
                type="button"
                onClick={() => {
                  setSelectedBrand(b.name);
                  setVisibleCount(PAGE_SIZE);
                }}
                className={`flex shrink-0 items-center gap-2.5 rounded-2xl border px-3 py-2 text-left transition-all cursor-pointer ${
                  active
                    ? "border-[#f04e23] bg-[#fff4f0] text-[#f04e23] ring-2 ring-[#f04e23]/20"
                    : "border-neutral-200/90 bg-white text-neutral-800 hover:border-orange-200"
                }`}
              >
                {b.sampleImg ? (
                  <img
                    src={b.sampleImg}
                    alt={b.name}
                    className="h-8 w-8 shrink-0 rounded-lg border border-neutral-100 object-cover bg-neutral-50"
                  />
                ) : (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-orange-50 text-xs font-bold text-[#f04e23]">
                    {b.name.slice(0, 2)}
                  </div>
                )}
                <div className="leading-tight">
                  <div className="text-xs font-bold whitespace-nowrap">{b.name}</div>
                  <div className="mt-0.5 flex items-center gap-1.5 text-[10px]">
                    <span className="text-neutral-500">{b.count} รุ่น</span>
                    {b.maxSavings > 0 && (
                      <span className="rounded-md bg-emerald-50 px-1.5 py-0.5 font-bold text-emerald-700">
                        ต่าง ฿{b.maxSavings.toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* Search, Sort & Category Controls */}
      <section ref={listSectionRef} className="mt-4 scroll-mt-20 space-y-3">
        <div className="flex flex-col gap-2.5 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
            <input
              id="product-search"
              name="q"
              type="search"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setVisibleCount(PAGE_SIZE);
              }}
              placeholder="ค้นหาแบรนด์หรือรุ่น เช่น Seagull, NIVEA"
              className="w-full rounded-2xl border border-neutral-200 bg-white py-2.5 pl-10 pr-4 text-sm text-neutral-900 shadow-xs outline-none transition-all placeholder:text-neutral-400 focus:border-[#f04e23] focus:ring-4 focus:ring-orange-500/10"
            />
          </div>

          <div className="flex items-center justify-between gap-2 sm:justify-end">
            <span className="text-xs font-semibold text-neutral-500">
              {selectedBrand !== "all" ? `แบรนด์ ${selectedBrand} • ` : ""}
              {filtered.length} รุ่น
            </span>
            <select
              id="product-sort"
              name="sort"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              aria-label="เรียงลำดับสินค้า"
              className="rounded-xl border border-neutral-200 bg-white px-3 py-2 text-xs font-semibold text-neutral-700 shadow-xs outline-none focus:border-[#f04e23]"
            >
              <option value="featured">เรียง: แนะนำ</option>
              <option value="savings">ส่วนต่างราคาเยอะสุด</option>
              <option value="price_asc">ราคาถูกสุดก่อน</option>
              <option value="bestseller">ยอดขายสูงสุด</option>
            </select>
          </div>
        </div>

        {/* Category Chips + Active Brand Reset */}
        <div className="no-scrollbar flex items-center gap-1.5 overflow-x-auto pb-1">
          {selectedBrand !== "all" && (
            <button
              type="button"
              onClick={() => setSelectedBrand("all")}
              className="inline-flex shrink-0 items-center gap-1 rounded-full bg-neutral-900 px-3 py-1.5 text-xs font-bold text-white cursor-pointer"
            >
              <Tag className="h-3 w-3" />
              {selectedBrand}
              <X className="h-3 w-3 opacity-80" />
            </button>
          )}
          {CATEGORIES.map((cat) => {
            const active = category === cat.key;
            return (
              <button
                key={cat.key}
                type="button"
                onClick={() => {
                  setCategory(cat.key);
                  setVisibleCount(PAGE_SIZE);
                }}
                className={`shrink-0 rounded-full px-3.5 py-1.5 text-xs font-semibold transition-all cursor-pointer ${
                  active
                    ? "bg-[#f04e23] text-white shadow-xs"
                    : "border border-neutral-200/90 bg-white text-neutral-600 hover:border-orange-200 hover:text-[#f04e23]"
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>
      </section>

      {/* Step 2: Mobile-First Side-by-Side Comparison Cards (1-col mobile, 2-col desktop) */}
      {visibleProducts.length === 0 ? (
        <div className="mt-8 rounded-3xl border border-dashed border-neutral-300 bg-white py-14 text-center">
          <p className="text-sm font-semibold text-neutral-700">ไม่พบสินค้าที่ตรงกับตัวกรอง</p>
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setSelectedBrand("all");
              setCategory("all");
            }}
            className="mt-3 rounded-full bg-[#fff4f0] px-4 py-2 text-xs font-semibold text-[#f04e23] hover:bg-orange-100 cursor-pointer"
          >
            แสดงสินค้าทั้งหมด
          </button>
        </div>
      ) : (
        <section className="mt-4 grid grid-cols-1 gap-3.5 lg:grid-cols-2 lg:gap-4">
          {visibleProducts.map((p) => {
            const meta = getPriceMeta(p);
            const brandLabel = (p.brand || "ร้านแท้").trim();

            return (
              <article
                key={p.code}
                className="flex flex-col justify-between overflow-hidden rounded-2xl border border-neutral-200/90 bg-white p-3.5 shadow-xs transition-all hover:border-orange-200 hover:shadow-md sm:p-4"
              >
                {/* Top Product Info Row */}
                <div className="flex gap-3">
                  <Link
                    href={`/p/${encodeURIComponent(p.code)}`}
                    className="relative h-24 w-24 shrink-0 overflow-hidden rounded-xl border border-neutral-100 bg-neutral-50 sm:h-28 sm:w-28"
                  >
                    {p.image_url ? (
                      <img
                        src={p.image_url}
                        alt={p.title}
                        loading="lazy"
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center bg-orange-50 text-lg font-bold text-[#f04e23]">
                        #{p.code}
                      </div>
                    )}
                    <span className="absolute left-1.5 top-1.5 rounded-md bg-white/95 px-1.5 py-0.5 text-[10px] font-bold text-neutral-900 shadow-xs">
                      #{p.code}
                    </span>
                    {p.has_video && (
                      <span className="absolute bottom-1.5 left-1.5 inline-flex items-center gap-0.5 rounded-md bg-[#f04e23] px-1.5 py-0.5 text-[9px] font-bold text-white">
                        <PlayCircle className="h-2.5 w-2.5" />
                        รีวิว
                      </span>
                    )}
                  </Link>

                  <div className="min-w-0 flex-1">
                    {/* Brand + Rating + Savings Winner Pill */}
                    <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
                      <button
                        type="button"
                        onClick={() => pickBrand(brandLabel)}
                        className="rounded-md bg-neutral-100 px-2 py-0.5 font-bold text-neutral-700 hover:bg-orange-50 hover:text-[#f04e23] cursor-pointer"
                      >
                        {brandLabel}
                      </button>
                      <span className="inline-flex items-center gap-0.5 font-semibold text-amber-600">
                        <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                        {p.rating}
                      </span>
                      {p.sold_text && (
                        <span className="truncate text-neutral-400">{p.sold_text}</span>
                      )}
                    </div>

                    <Link href={`/p/${encodeURIComponent(p.code)}`}>
                      <h3 className="mt-1 line-clamp-2 text-[14px] font-bold leading-snug text-neutral-900 hover:text-[#f04e23] sm:text-[15px]">
                        {p.title}
                      </h3>
                    </Link>

                    {/* Winner / Savings Highlight */}
                    <div className="mt-2">
                      {meta.winner === "lazada" && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-[11px] font-bold text-emerald-700 border border-emerald-200/80">
                          <Sparkles className="h-3 w-3" />
                          Lazada ถูกกว่า ฿{meta.diff.toLocaleString()}
                        </span>
                      )}
                      {meta.winner === "shopee" && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-[11px] font-bold text-emerald-700 border border-emerald-200/80">
                          <Sparkles className="h-3 w-3" />
                          Shopee ถูกกว่า ฿{meta.diff.toLocaleString()}
                        </span>
                      )}
                      {meta.winner === "tie" && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-2.5 py-0.5 text-[11px] font-semibold text-neutral-600">
                          <Scale className="h-3 w-3" />
                          ราคาเท่ากัน ฿{meta.bestPrice.toLocaleString()} (เทียบโค้ดลดได้เลย)
                        </span>
                      )}
                      {meta.winner === "single" && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-orange-50/80 px-2.5 py-0.5 text-[11px] font-medium text-neutral-600">
                          <CheckCircle2 className="h-3 w-3 text-[#f04e23]" />
                          ร้านแท้ Shopee (กำลังเพิ่มลิงก์ Lazada)
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Bottom Side-by-Side Battle Box (Shopee vs Lazada) */}
                <div className="mt-3.5 grid grid-cols-2 gap-2.5 border-t border-neutral-100 pt-3">
                  {/* Shopee Column */}
                  <div
                    className={`flex flex-col justify-between rounded-xl border p-2.5 transition-all ${
                      meta.winner === "shopee"
                        ? "border-emerald-400 bg-emerald-50/40 ring-1 ring-emerald-400/40"
                        : "border-orange-100 bg-[#fffaf8]"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-[11px] font-bold text-[#f04e23]">Shopee</span>
                      {meta.winner === "shopee" && (
                        <span className="rounded-md bg-emerald-600 px-1.5 py-0.5 text-[9px] font-bold text-white">
                          ถูกสุด!
                        </span>
                      )}
                    </div>
                    <div className="my-1.5 text-lg font-extrabold tabular-nums text-neutral-900 sm:text-xl">
                      {meta.sh > 0 ? `฿${meta.sh.toLocaleString()}` : "เช็กราคา"}
                    </div>
                    {p.shopee_url ? (
                      <a
                        href={`/go/${encodeURIComponent(p.code)}?p=shopee`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex min-h-[38px] w-full items-center justify-center gap-1 rounded-lg bg-[#f04e23] px-2.5 py-2 text-xs font-bold text-white transition-colors active:scale-[0.98] hover:bg-[#d93f16]"
                      >
                        <span>ซื้อ Shopee</span>
                        <ExternalLink className="h-3 w-3 opacity-85" />
                      </a>
                    ) : (
                      <span className="inline-flex min-h-[38px] items-center justify-center rounded-lg bg-neutral-100 text-[11px] font-medium text-neutral-400">
                        ยังไม่มีลิงก์
                      </span>
                    )}
                  </div>

                  {/* Lazada Column */}
                  <div
                    className={`flex flex-col justify-between rounded-xl border p-2.5 transition-all ${
                      meta.winner === "lazada"
                        ? "border-emerald-400 bg-emerald-50/40 ring-1 ring-emerald-400/40"
                        : p.lazada_url
                        ? "border-indigo-100 bg-[#f7f8ff]"
                        : "border-dashed border-neutral-200 bg-neutral-50/60"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-[#101d6b]">
                        Lazada
                        {p.lazada_item_id && (
                          <span
                            title="ซิงค์ราคาสดจาก Lazada Open API"
                            className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500"
                          />
                        )}
                      </span>
                      {meta.winner === "lazada" ? (
                        <span className="rounded-md bg-emerald-600 px-1.5 py-0.5 text-[9px] font-bold text-white">
                          ถูกสุด!
                        </span>
                      ) : p.lazada_item_id ? (
                        <span className="text-[9px] font-semibold text-emerald-700">API สด</span>
                      ) : null}
                    </div>
                    <div className="my-1.5 text-lg font-extrabold tabular-nums text-neutral-900 sm:text-xl">
                      {meta.lz > 0 ? (
                        `฿${meta.lz.toLocaleString()}`
                      ) : p.lazada_url ? (
                        "เช็กราคา"
                      ) : (
                        <span className="text-xs font-medium text-neutral-400">รอเพิ่มลิงก์</span>
                      )}
                    </div>
                    {p.lazada_url ? (
                      <a
                        href={`/go/${encodeURIComponent(p.code)}?p=lazada`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex min-h-[38px] w-full items-center justify-center gap-1 rounded-lg bg-[#101d6b] px-2.5 py-2 text-xs font-bold text-white transition-colors active:scale-[0.98] hover:bg-[#0b144d]"
                      >
                        <span>ซื้อ Lazada</span>
                        <ExternalLink className="h-3 w-3 opacity-85" />
                      </a>
                    ) : (
                      <Link
                        href={`/p/${encodeURIComponent(p.code)}`}
                        className="inline-flex min-h-[38px] w-full items-center justify-center rounded-lg border border-neutral-200 bg-white px-2.5 py-2 text-[11px] font-semibold text-neutral-500 hover:border-neutral-300"
                      >
                        ดูรายละเอียด
                      </Link>
                    )}
                  </div>
                </div>
              </article>
            );
          })}
        </section>
      )}

      {/* Load More */}
      {hasMore && (
        <div className="mt-7 text-center">
          <button
            type="button"
            onClick={() => setVisibleCount((n) => n + PAGE_SIZE)}
            className="inline-flex items-center gap-2 rounded-full border border-orange-200 bg-white px-6 py-2.5 text-sm font-semibold text-[#f04e23] shadow-xs hover:bg-[#fff4f0] cursor-pointer"
          >
            โหลดสินค้าเพิ่ม ({filtered.length - visibleCount} รายการ)
          </button>
        </div>
      )}

      {/* Affiliate Policy Disclaimer */}
      <p className="mt-7 rounded-2xl border border-neutral-200/70 bg-white px-4 py-3 text-center text-[11px] leading-relaxed text-neutral-500">
        ราคาที่แสดงเป็นราคาอ้างอิงจากหน้าร้านทางการ (ฝั่ง Lazada ซิงค์อัตโนมัติผ่าน Lazada Open API ทุกวัน 06:00 น.)
        ราคาสุทธิอาจลดเพิ่มได้อีกตามคูปองส่งฟรีและโค้ดส่วนลดของแต่ละแพลตฟอร์ม กรุณาตรวจสอบราคาหน้าตะกร้าก่อนชำระเงิน
      </p>

      {/* Mobile Sticky Bottom Action Bar (Native App Feel!) */}
      <div className="fixed inset-x-0 bottom-0 z-40 border-t border-neutral-200/90 bg-white/95 px-3 py-2 backdrop-blur-md md:hidden">
        <div className="mx-auto grid max-w-md grid-cols-3 gap-2">
          <button
            type="button"
            onClick={() => {
              setSelectedBrand("all");
              setCategory("all");
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
            className={`flex flex-col items-center justify-center gap-0.5 rounded-xl py-1.5 text-[11px] font-bold cursor-pointer ${
              selectedBrand === "all" && !brandSheetOpen
                ? "bg-[#fff4f0] text-[#f04e23]"
                : "text-neutral-600"
            }`}
          >
            <Scale className="h-4 w-4" />
            <span>เทียบราคา</span>
          </button>

          <button
            type="button"
            onClick={() => setBrandSheetOpen(true)}
            className="flex flex-col items-center justify-center gap-0.5 rounded-xl bg-[#f04e23] py-1.5 text-[11px] font-bold text-white shadow-xs cursor-pointer"
          >
            <Store className="h-4 w-4" />
            <span>เลือกแบรนด์</span>
          </button>

          <Link
            href="/travel"
            className="flex flex-col items-center justify-center gap-0.5 rounded-xl py-1.5 text-[11px] font-bold text-neutral-600"
          >
            <Plane className="h-4 w-4" />
            <span>ดีลเที่ยว</span>
          </Link>
        </div>
      </div>

      {/* Mobile Bottom Sheet / Desktop Modal: Brand Picker */}
      {brandSheetOpen && (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/45 backdrop-blur-[2px] sm:items-center sm:p-4"
          onClick={() => setBrandSheetOpen(false)}
        >
          <div
            className="flex max-h-[82vh] w-full max-w-lg flex-col overflow-hidden rounded-t-3xl bg-white shadow-2xl sm:rounded-3xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Sheet Drag Handle (mobile visual cue) */}
            <div className="flex justify-center pt-2.5 sm:hidden">
              <div className="h-1.5 w-10 rounded-full bg-neutral-200" />
            </div>

            <div className="flex items-center justify-between border-b border-neutral-100 px-5 py-3.5">
              <div>
                <h3 className="text-base font-bold text-neutral-900">
                  เลือกแบรนด์ที่อยากเทียบราคา
                </h3>
                <p className="text-xs text-neutral-500">
                  กดเลือก 1 แบรนด์เพื่อดูราคาชนกัน Shopee vs Lazada
                </p>
              </div>
              <button
                type="button"
                onClick={() => setBrandSheetOpen(false)}
                className="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-100 text-neutral-600 hover:bg-neutral-200 cursor-pointer"
                aria-label="ปิด"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="px-5 pt-3">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
                <input
                  type="search"
                  value={brandSearch}
                  onChange={(e) => setBrandSearch(e.target.value)}
                  placeholder="พิมพ์ชื่อแบรนด์ เช่น Seagull, NIVEA, ZINSANO..."
                  className="w-full rounded-xl border border-neutral-200 bg-[#faf9f7] py-2.5 pl-10 pr-3 text-sm outline-none focus:border-[#f04e23] focus:bg-white"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2.5 overflow-y-auto p-5">
              <button
                type="button"
                onClick={() => pickBrand("all")}
                className={`col-span-2 flex items-center justify-between rounded-2xl border p-3.5 text-left transition-all cursor-pointer ${
                  selectedBrand === "all"
                    ? "border-[#f04e23] bg-[#fff4f0] text-[#f04e23]"
                    : "border-neutral-200 bg-white hover:border-orange-200"
                }`}
              >
                <div>
                  <div className="text-sm font-bold">ดูทุกแบรนด์ทั้งหมด</div>
                  <div className="text-xs text-neutral-500">
                    รวม {products.length} รุ่น (เทียบ 2 เจ้าได้ทันที {dualTotal} รุ่น)
                  </div>
                </div>
                <ArrowRight className="h-4 w-4" />
              </button>

              {filteredBrandsForSheet.map((b) => {
                const active = selectedBrand === b.name;
                return (
                  <button
                    key={b.name}
                    type="button"
                    onClick={() => pickBrand(b.name)}
                    className={`flex items-center gap-2.5 rounded-2xl border p-3 text-left transition-all cursor-pointer ${
                      active
                        ? "border-[#f04e23] bg-[#fff4f0] ring-2 ring-[#f04e23]/20"
                        : "border-neutral-200 bg-white hover:border-orange-200"
                    }`}
                  >
                    {b.sampleImg ? (
                      <img
                        src={b.sampleImg}
                        alt={b.name}
                        className="h-10 w-10 shrink-0 rounded-xl border border-neutral-100 object-cover bg-neutral-50"
                      />
                    ) : (
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-orange-50 text-xs font-bold text-[#f04e23]">
                        {b.name.slice(0, 2)}
                      </div>
                    )}
                    <div className="min-w-0">
                      <div className="truncate text-xs font-bold text-neutral-900">{b.name}</div>
                      <div className="text-[11px] text-neutral-500">{b.count} รุ่น</div>
                      {b.maxSavings > 0 && (
                        <div className="mt-0.5 text-[10px] font-bold text-emerald-700">
                          ต่างสูงสุด ฿{b.maxSavings.toLocaleString()}
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
