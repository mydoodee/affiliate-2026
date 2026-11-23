import type { Metadata } from "next";
import {
  ArrowUpRight,
  Building2,
  Car,
  CreditCard,
  Globe,
  Plane,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { getTravelDeals } from "@/lib/db";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "ดีลเที่ยวปีใหม่ 2027 & เช็กเบี้ยประกันออนไลน์",
  description:
    "รวมลิงก์ตรงจาก Trip.com, Traveloka, Airalo eSIM, MSIG ประกันเดินทาง และ SCB protect ประกันรถยนต์",
};

function DealIcon({ iconKey }: { iconKey: string }) {
  const cls = "h-5 w-5 text-[#f04e23]";
  switch (iconKey) {
    case "hotel":
      return <Building2 className={cls} />;
    case "plane":
      return <Plane className={cls} />;
    case "esim":
      return <Globe className={cls} />;
    case "car":
      return <Car className={cls} />;
    case "card":
      return <CreditCard className={cls} />;
    default:
      return <ShieldCheck className={cls} />;
  }
}

export default async function TravelPage() {
  const deals = await getTravelDeals();

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6 sm:py-8">
        {/* Clean White & Orange Travel Hero */}
        <section className="relative overflow-hidden rounded-3xl border border-orange-100 bg-white p-6 shadow-sm sm:p-9">
          <div
            className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full opacity-60 blur-3xl"
            style={{ background: "radial-gradient(circle, #ffd6c4 0%, transparent 70%)" }}
          />
          <div className="relative z-10 max-w-2xl">
            <div className="mb-3 inline-flex items-center gap-1.5 rounded-full border border-orange-200/80 bg-[#fff4f0] px-3 py-1 text-xs font-semibold text-[#f04e23]">
              <Sparkles className="h-3.5 w-3.5" />
              New Year 2027 Travel &amp; Protection Hub
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-neutral-900 sm:text-3xl">
              ดีลเที่ยวปีใหม่ &amp; <span className="text-[#f04e23]">เช็กเบี้ยประกันออนไลน์</span>
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-neutral-600 sm:text-[15px]">
              ลิงก์ตรงจากผู้ให้บริการชั้นนำอย่างเป็นทางการ ไม่มีค่าใช้จ่ายเพิ่มเติม เลือกจองโรงแรม
              รถเช่า ซื้อ eSIM เที่ยวต่างประเทศ หรือเปรียบเทียบเบี้ยประกันเดินทางและประกันรถยนต์ได้ทันที
            </p>
          </div>
        </section>

        {/* Deals Grid */}
        <section className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {deals.map((deal) => (
            <article
              key={deal.code}
              className="group flex flex-col justify-between rounded-2xl border border-neutral-200/80 bg-white p-5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-orange-200 hover:shadow-md"
            >
              <div>
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-orange-100 bg-[#fff4f0]">
                    <DealIcon iconKey={deal.icon_key} />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="rounded-md bg-neutral-100 px-2 py-0.5 text-[11px] font-bold text-neutral-700">
                        {deal.code}
                      </span>
                      <span className="truncate rounded-md bg-[#fff4f0] px-2 py-0.5 text-[11px] font-semibold text-[#f04e23]">
                        {deal.category}
                      </span>
                    </div>
                    <div className="mt-1 truncate text-xs text-neutral-500">
                      {deal.highlight}
                    </div>
                  </div>
                </div>

                <h2 className="text-base font-bold leading-snug text-neutral-900 group-hover:text-[#f04e23] transition-colors">
                  {deal.title}
                </h2>
                <p className="mt-2 text-xs leading-relaxed text-neutral-600 sm:text-[13px]">
                  {deal.description}
                </p>
              </div>

              <div className="mt-5 border-t border-neutral-100 pt-4">
                <a
                  href={`/go/${encodeURIComponent(deal.code)}?t=travel`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex w-full items-center justify-center gap-1.5 rounded-xl bg-[#f04e23] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#d93f16]"
                >
                  <span>{deal.cta_text}</span>
                  <ArrowUpRight className="h-4 w-4" />
                </a>
              </div>
            </article>
          ))}
        </section>
      </main>
      <Footer />
    </div>
  );
}
