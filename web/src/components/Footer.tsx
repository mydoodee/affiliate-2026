import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export function Footer() {
  const partners = [
    "Shopee",
    "Lazada",
    "Trip.com",
    "Traveloka",
    "Airalo",
    "MSIG",
    "SCB protect",
  ];

  return (
    <footer className="mt-16 border-t border-neutral-200/80 bg-white">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#f04e23] text-xs font-bold text-white">
              BM
            </div>
            <div>
              <div className="flex items-center gap-1 text-sm font-bold text-neutral-900">
                Babman Picks
                <ShieldCheck className="h-3.5 w-3.5 text-[#f04e23]" />
              </div>
              <p className="text-xs text-neutral-500">
                คัดสรรสินค้าคุณภาพ &amp; ดีลท่องเที่ยวจากพันธมิตรทางการ
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-xs font-semibold text-neutral-500">
            {partners.map((name) => (
              <span key={name} className="hover:text-[#f04e23] transition-colors">
                {name}
              </span>
            ))}
          </div>
        </div>

        <div className="mt-8 flex flex-col items-center justify-between gap-3 border-t border-neutral-100 pt-6 text-xs text-neutral-400 sm:flex-row">
          <p>
            ลิงก์ Affiliate อย่างเป็นทางการ • ราคาและโค้ดส่วนลดอัปเดตตามหน้าร้านค้าผู้ให้บริการ
          </p>
          <div className="flex items-center gap-4">
            <a
              href="https://www.tiktok.com/@mybabman"
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-neutral-500 hover:text-[#f04e23]"
            >
              TikTok @mybabman
            </a>
            <Link href="/admin" className="font-medium text-neutral-500 hover:text-[#f04e23]">
              Admin
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
