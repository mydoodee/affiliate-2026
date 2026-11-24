import type { Metadata } from "next";
import { Sarabun } from "next/font/google";
import "./globals.css";

const sarabun = Sarabun({
  weight: ["400", "500", "600", "700", "800"],
  subsets: ["thai", "latin"],
  variable: "--font-sarabun",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://app.growkub.com"),
  title: {
    default: "Babman Picks • คัดสินค้าขายดี Shopee & Lazada และดีลเที่ยวปีใหม่ 2027",
    template: "%s | Babman Picks",
  },
  description:
    "รวมสินค้าขายดีรีวิว 4.8–4.9 ดาวจากร้านทางการ Shopee & Lazada พร้อมศูนย์รวมดีลจองที่พัก ตั๋วเครื่องบิน eSIM และประกันออนไลน์",
  openGraph: {
    url: "https://app.growkub.com",
    siteName: "Babman Picks",
    title: "Babman Picks • พิกัดของดีใช้จริง & ดีลเที่ยวปีใหม่ 2027",
    description:
      "เลือกช้อปสินค้าแนะนำตามเบอร์ #01–#10 เทียบราคา Shopee & Lazada และเช็กดีลเที่ยวปีใหม่จากค่ายทางการ",
    images: [{ url: "/logo.png", width: 512, height: 512, alt: "Babman Picks Logo" }],
    type: "website",
    locale: "th_TH",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="th" className={`${sarabun.variable} h-full antialiased`}>
      <body className="min-h-full bg-[#faf9f7] text-[#171717] font-sans selection:bg-orange-100 selection:text-orange-900">
        {children}
      </body>
    </html>
  );
}
