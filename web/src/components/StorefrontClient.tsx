"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  CheckCircle2,
  ExternalLink,
  Plane,
  PlayCircle,
  Search,
  Sparkles,
  Star,
} from "lucide-react";
import type { Product } from "@/lib/types";

const CATEGORIES = [
  { key: "all", label: "ทั้งหมด" },
  { key: "video", label: "มีคลิปรีวิว" },
  { key: "cctv", label: "กล้องวงจรปิด" },
  { key: "home", label: "บ้าน & ช่าง" },
  { key: "kitchen", label: "เครื่องครัว" },
  { key: "beauty", label: "บิวตี้ & สุขภาพ" },
  { key: "gadget", label: "แกดเจ็ต" },
];

const PAGE_SIZE = 24;

export function StorefrontClient({ products }: { products: Product[] }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [sortBy, setSortBy] = useState<"featured" | "bestseller" | "price_asc" | "price_desc">(
    "featured"
  );
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = products.filter((p) => {
      const matchCat =
        category === "all" ||
        (category === "video" ? p.has_video : p.category === category);
      const matchQ =
        !q ||
        p.code.toLowerCase().includes(q) ||
        p.title.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.badge.toLowerCase().includes(q);
      return matchCat && matchQ;
    });

    const sorted = [...list];
    if (sortBy === "bestseller") sorted.sort((a, b) => b.sold_num - a.sold_num);
    else if (sortBy === "price_asc") sorted.sort((a, b) => a.price_num - b.price_num);
    else if (sortBy === "price_desc") sorted.sort((a, b) => b.price_num - a.price_num);
    else sorted.sort((a, b) => a.sort_order - b.sort_order);
    return sorted;
  }, [products, query, category, sortBy]);

  const visibleProducts = filtered.slice(0, visibleCount);
  const hasMore = visibleCount < filtered.length;

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
      {/* Premium White & Orange Hero */}
      <section className="relative overflow-hidden rounded-3xl border border-orange-100 bg-white p-6 shadow-sm sm:p-9">
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full opacity-60 blur-3xl"
          style={{ background: "radial-gradient(circle, #ffd6c4 0%, transparent 70%)" }}
        />
        <div className="relative z-10 flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
          <div className="max-w-xl">
            <div className="mb-3 inline-flex items-center gap-1.5 rounded-full border border-orange-200/80 bg-[#fff4f0] px-3 py-1 text-xs font-semibold text-[#f04e23]">
              <Sparkles className="h-3.5 w-3.5" />
              คัดเฉพาะร้านทางการ รีวิว 4.8–4.9 ดาว
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-neutral-900 sm:text-3xl">
              พิกัดของดีใช้จริง <span className="text-[#f04e23]">@mybabman</span>
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-neutral-600 sm:text-[15px]">
              ดูคลิปจาก TikTok หรือ Shopee Video แล้วหาของไม่เจอ? ค้นหาตาม{" "}
              <strong className="font-semibold text-neutral-900">เบอร์สินค้า (#01–#10)</strong>{" "}
              เทียบราคาและเก็บโค้ดลดหน้าร้านแท้ได้ทั้ง Shopee และ Lazada
            </p>
            <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs font-medium text-neutral-500">
              <span className="inline-flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-[#f04e23]" />
                ลิงก์ตรง Official Store
              </span>
              <span className="inline-flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-[#f04e23]" />
                อัปเดตสินค้าทุกสัปดาห์ ({products.length} รายการ)
              </span>
            </div>
          </div>

          {/* Highlighted New Year Travel Callout Card */}
          <Link
            href="/travel"
            className="group flex items-center justify-between gap-4 rounded-2xl border border-orange-200/70 bg-gradient-to-br from-[#fff7f4] to-white p-4 transition-all hover:border-[#f04e23]/50 hover:shadow-md sm:p-5 lg:w-80 shrink-0"
          >
            <div>
              <div className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-[#f04e23]">
                <Plane className="h-3.5 w-3.5" />
                New Year 2027
              </div>
              <div className="mt-1 text-sm font-bold text-neutral-900">
                ดีลเที่ยวปีใหม่ &amp; ประกันออนไลน์
              </div>
              <p className="mt-0.5 text-xs text-neutral-500">
                Trip.com · Traveloka · Klook · Airalo · MSIG · SCB
              </p>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#f04e23] text-white transition-transform group-hover:translate-x-0.5">
              <ArrowRight className="h-4 w-4" />
            </div>
          </Link>
        </div>
      </section>

      {/* Search, Sort & Category Controls */}
      <section className="mt-6 space-y-3.5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
            <input
              type="search"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setVisibleCount(PAGE_SIZE);
              }}
              placeholder="ค้นหาชื่อสินค้า หรือพิมพ์เบอร์ เช่น 01, กล้อง, เจลกำจัดมด..."
              className="w-full rounded-2xl border border-neutral-200 bg-white py-3 pl-11 pr-4 text-sm text-neutral-900 shadow-xs outline-none transition-all placeholder:text-neutral-400 focus:border-[#f04e23] focus:ring-4 focus:ring-orange-500/10"
            />
          </div>

          <div className="flex items-center justify-between gap-2 sm:justify-end">
            <span className="text-xs font-medium text-neutral-500 sm:hidden">
              พบ {filtered.length} รายการ
            </span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              aria-label="เรียงลำดับสินค้า"
              className="rounded-2xl border border-neutral-200 bg-white px-4 py-3 text-xs sm:text-sm font-medium text-neutral-700 shadow-xs outline-none focus:border-[#f04e23]"
            >
              <option value="featured">เรียงตาม: แนะนำ</option>
              <option value="bestseller">ยอดขายสูงสุด</option>
              <option value="price_asc">ราคา: ต่ำ → สูง</option>
              <option value="price_desc">ราคา: สูง → ต่ำ</option>
            </select>
          </div>
        </div>

        {/* Category Chips */}
        <div className="no-scrollbar flex items-center gap-2 overflow-x-auto pb-1">
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
                className={`shrink-0 rounded-full px-4 py-2 text-xs sm:text-[13px] font-semibold transition-all cursor-pointer ${
                  active
                    ? "bg-[#f04e23] text-white shadow-sm shadow-orange-500/20"
                    : "border border-neutral-200/90 bg-white text-neutral-600 hover:border-orange-200 hover:text-[#f04e23]"
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>
      </section>

      {/* Product Grid: 2 cols mobile / 3 cols md / 4 cols lg */}
      {visibleProducts.length === 0 ? (
        <div className="mt-10 rounded-3xl border border-dashed border-neutral-300 bg-white py-16 text-center">
          <p className="text-sm font-semibold text-neutral-700">ไม่พบสินค้าที่ตรงกับคำค้นหา</p>
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setCategory("all");
            }}
            className="mt-3 rounded-full bg-[#fff4f0] px-4 py-2 text-xs font-semibold text-[#f04e23] hover:bg-orange-100"
          >
            ล้างตัวกรองทั้งหมด
          </button>
        </div>
      ) : (
        <section className="mt-5 grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 lg:grid-cols-4">
          {visibleProducts.map((p) => (
            <article
              key={p.code}
              className="group flex flex-col justify-between overflow-hidden rounded-2xl border border-neutral-200/80 bg-white shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-orange-200 hover:shadow-md"
            >
              <div>
                {/* 1:1 Crisp Real Product Image */}
                <Link
                  href={`/p/${encodeURIComponent(p.code)}`}
                  className="relative block aspect-square w-full overflow-hidden bg-neutral-50"
                >
                  {p.image_url ? (
                    <img
                      src={p.image_url}
                      alt={p.title}
                      loading="lazy"
                      className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center bg-orange-50/50 text-2xl font-bold text-[#f04e23]">
                      #{p.code}
                    </div>
                  )}

                  {/* Top Left Number Pill */}
                  <span className="absolute left-2.5 top-2.5 rounded-lg bg-white/95 px-2 py-0.5 text-[11px] font-bold text-neutral-900 shadow-xs backdrop-blur-xs">
                    #{p.code}
                  </span>

                  {/* Top Right Video / Hot Badge */}
                  {p.has_video ? (
                    <span className="absolute right-2.5 top-2.5 inline-flex items-center gap-1 rounded-lg bg-[#f04e23] px-2 py-0.5 text-[10px] font-semibold text-white shadow-xs">
                      <PlayCircle className="h-3 w-3" />
                      รีวิว
                    </span>
                  ) : p.badge ? (
                    <span className="absolute right-2.5 top-2.5 rounded-lg bg-orange-50/95 px-2 py-0.5 text-[10px] font-semibold text-[#f04e23] backdrop-blur-xs">
                      {p.badge}
                    </span>
                  ) : null}
                </Link>

                {/* Content */}
                <div className="p-3 sm:p-3.5">
                  <div className="mb-1.5 flex items-center justify-between gap-1 text-[11px]">
                    <span className="inline-flex items-center gap-0.5 font-semibold text-amber-600">
                      <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                      {p.rating}
                    </span>
                    <span className="truncate text-neutral-400">{p.sold_text}</span>
                  </div>

                  <Link href={`/p/${encodeURIComponent(p.code)}`}>
                    <h2 className="line-clamp-2 min-h-[2.6rem] text-[13px] font-semibold leading-snug text-neutral-900 transition-colors group-hover:text-[#f04e23] sm:text-sm">
                      {p.title}
                    </h2>
                  </Link>
                </div>
              </div>

              {/* Price & Dual Platform CTAs */}
              <div className="border-t border-neutral-100 p-3 pt-2.5 sm:p-3.5 sm:pt-3">
                <div className="mb-2.5 text-base font-bold tabular-nums text-[#f04e23] sm:text-[17px]">
                  {p.price_display}
                </div>

                <div className="flex flex-col gap-1.5 sm:flex-row">
                  {p.shopee_url && (
                    <a
                      href={`/go/${encodeURIComponent(p.code)}?p=shopee`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex flex-1 items-center justify-center gap-1 rounded-xl bg-[#f04e23] px-2.5 py-2 text-xs font-semibold text-white transition-colors hover:bg-[#d93f16]"
                    >
                      <span>Shopee</span>
                      <ExternalLink className="h-3 w-3 opacity-80" />
                    </a>
                  )}
                  {p.lazada_url && (
                    <a
                      href={`/go/${encodeURIComponent(p.code)}?p=lazada`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex flex-1 items-center justify-center gap-1 rounded-xl border border-neutral-200 bg-white px-2.5 py-2 text-xs font-semibold text-neutral-800 transition-colors hover:border-[#1d2b64] hover:bg-[#1d2b64] hover:text-white"
                    >
                      <span>Lazada</span>
                      <ExternalLink className="h-3 w-3 opacity-70" />
                    </a>
                  )}
                </div>
              </div>
            </article>
          ))}
        </section>
      )}

      {/* Pagination / Load More (for scaling to 1,000+ products cleanly) */}
      {hasMore && (
        <div className="mt-8 text-center">
          <button
            type="button"
            onClick={() => setVisibleCount((n) => n + PAGE_SIZE)}
            className="inline-flex items-center gap-2 rounded-full border border-orange-200 bg-white px-6 py-2.5 text-sm font-semibold text-[#f04e23] shadow-xs transition-all hover:bg-[#fff4f0] cursor-pointer"
          >
            โหลดสินค้าเพิ่ม ({filtered.length - visibleCount} รายการ)
          </button>
        </div>
      )}
    </div>
  );
}
