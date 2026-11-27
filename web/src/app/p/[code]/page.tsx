import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  ExternalLink,
  PlayCircle,
  ShieldCheck,
  Star,
} from "lucide-react";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { getProductByCode, getProducts } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ code: string }>;
}): Promise<Metadata> {
  const { code } = await params;
  const product = await getProductByCode(code);
  if (!product) return { title: "ไม่พบสินค้า" };
  return {
    title: `#${product.code} ${product.title}`,
    description: `${product.description} ราคาอ้างอิง ${product.price_display} (${product.sold_text})`,
    openGraph: {
      title: `#${product.code} ${product.title}`,
      description: product.description,
      images: product.image_url ? [product.image_url] : [],
    },
  };
}

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ code: string }>;
}) {
  const { code } = await params;
  const [product, allProducts] = await Promise.all([
    getProductByCode(code),
    getProducts(),
  ]);

  if (!product) notFound();

  const related = allProducts
    .filter((p) => p.code !== product.code)
    .slice(0, 4);

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 sm:px-6 sm:py-10">
        <Link
          href="/"
          className="mb-5 inline-flex items-center gap-1.5 text-xs font-semibold text-neutral-500 transition-colors hover:text-[#f04e23]"
        >
          <ArrowLeft className="h-4 w-4" />
          กลับไปดูสินค้าทั้งหมด
        </Link>

        <div className="grid gap-6 overflow-hidden rounded-3xl border border-neutral-200/80 bg-white p-5 shadow-sm sm:p-8 md:grid-cols-2 md:gap-10">
          {/* Square Product Photo */}
          <div className="relative aspect-square overflow-hidden rounded-2xl border border-neutral-100 bg-neutral-50">
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.title}
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center bg-orange-50 text-4xl font-bold text-[#f04e23]">
                #{product.code}
              </div>
            )}
            <span className="absolute left-3 top-3 rounded-xl bg-white/95 px-3 py-1 text-xs font-bold text-neutral-900 shadow-xs">
              เบอร์ #{product.code}
            </span>
            {product.has_video && (
              <span className="absolute right-3 top-3 inline-flex items-center gap-1 rounded-xl bg-[#f04e23] px-2.5 py-1 text-xs font-semibold text-white shadow-xs">
                <PlayCircle className="h-3.5 w-3.5" />
                มีคลิปรีวิว
              </span>
            )}
          </div>

          {/* Info & CTAs */}
          <div className="flex flex-col justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">
                  <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                  {product.rating} ดาว
                </span>
                {product.sold_text && (
                  <span className="rounded-full bg-neutral-100 px-2.5 py-1 font-medium text-neutral-600">
                    {product.sold_text}
                  </span>
                )}
                {product.badge && (
                  <span className="rounded-full bg-[#fff4f0] px-2.5 py-1 font-semibold text-[#f04e23]">
                    {product.badge}
                  </span>
                )}
              </div>

              <h1 className="mt-3 text-xl font-bold leading-snug text-neutral-900 sm:text-2xl">
                {product.title}
              </h1>

              <p className="mt-3 text-sm leading-relaxed text-neutral-600">
                {product.description}
              </p>

              <div className="mt-5 rounded-2xl border border-orange-100 bg-[#fffaf8] p-4">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-bold text-neutral-600">
                    เทียบราคา 2 เจ้าใหญ่ {product.brand ? `• ${product.brand}` : ""}
                  </span>
                  {product.shopee_price > 0 &&
                    product.lazada_price > 0 &&
                    product.shopee_price !== product.lazada_price && (
                      <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-[11px] font-bold text-emerald-800">
                        {product.lazada_price < product.shopee_price
                          ? `Lazada ถูกกว่า ฿${(product.shopee_price - product.lazada_price).toLocaleString()}`
                          : `Shopee ถูกกว่า ฿${(product.lazada_price - product.shopee_price).toLocaleString()}`}
                      </span>
                    )}
                </div>

                <div className="mt-3 grid grid-cols-2 gap-2.5">
                  <div className="rounded-xl border border-orange-200/80 bg-white p-3">
                    <div className="text-[11px] font-bold text-[#f04e23]">Shopee</div>
                    <div className="mt-0.5 text-2xl font-extrabold tabular-nums text-neutral-900">
                      {product.shopee_price > 0
                        ? `฿${product.shopee_price.toLocaleString()}`
                        : product.price_display}
                    </div>
                  </div>
                  <div className="rounded-xl border border-indigo-200/80 bg-white p-3">
                    <div className="text-[11px] font-bold text-[#101d6b]">
                      Lazada {product.lazada_item_id ? "• API สด" : ""}
                    </div>
                    <div className="mt-0.5 text-2xl font-extrabold tabular-nums text-neutral-900">
                      {product.lazada_price > 0
                        ? `฿${product.lazada_price.toLocaleString()}`
                        : product.lazada_url
                        ? "เช็กราคา"
                        : "—"}
                    </div>
                  </div>
                </div>

                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-neutral-500">
                  <span className="inline-flex items-center gap-1">
                    <ShieldCheck className="h-3.5 w-3.5 text-[#f04e23]" />
                    ลิงก์ตรงร้านทางการ
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <CheckCircle2 className="h-3.5 w-3.5 text-[#f04e23]" />
                    ใช้โค้ดส่งฟรี/ส่วนลดหน้าร้านได้
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-6 flex flex-col gap-2.5">
              {product.shopee_url && (
                <a
                  href={`/go/${encodeURIComponent(product.code)}?p=shopee`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#f04e23] px-5 py-3.5 text-sm font-bold text-white shadow-sm shadow-orange-500/20 transition-colors hover:bg-[#d93f16]"
                >
                  <span>เช็กราคา &amp; ซื้อที่ Shopee</span>
                  <ExternalLink className="h-4 w-4" />
                </a>
              )}
              {product.lazada_url && (
                <a
                  href={`/go/${encodeURIComponent(product.code)}?p=lazada`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-neutral-200 bg-white px-5 py-3.5 text-sm font-bold text-neutral-800 transition-colors hover:border-[#1d2b64] hover:bg-[#1d2b64] hover:text-white"
                >
                  <span>เทียบราคา &amp; ซื้อที่ Lazada</span>
                  <ExternalLink className="h-4 w-4" />
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Related Products */}
        <section className="mt-10">
          <h2 className="mb-4 text-base font-bold text-neutral-900">สินค้าขายดีอื่นที่น่าสนใจ</h2>
          <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
            {related.map((item) => (
              <Link
                key={item.code}
                href={`/p/${encodeURIComponent(item.code)}`}
                className="group overflow-hidden rounded-2xl border border-neutral-200/80 bg-white transition-all hover:border-orange-200 hover:shadow-sm"
              >
                <div className="aspect-square bg-neutral-50 overflow-hidden">
                  {item.image_url && (
                    <img
                      src={item.image_url}
                      alt={item.title}
                      loading="lazy"
                      className="h-full w-full object-cover transition-transform group-hover:scale-105"
                    />
                  )}
                </div>
                <div className="p-3">
                  <div className="text-[11px] font-bold text-neutral-400">#{item.code}</div>
                  <div className="mt-0.5 line-clamp-2 text-xs font-semibold text-neutral-800 group-hover:text-[#f04e23]">
                    {item.title}
                  </div>
                  <div className="mt-1.5 text-sm font-bold text-[#f04e23]">
                    {item.price_display}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
