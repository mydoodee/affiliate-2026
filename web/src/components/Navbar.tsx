"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Plane, Scale, ShieldCheck, SlidersHorizontal } from "lucide-react";

export function Navbar() {
  const pathname = usePathname();

  const navLinks = [
    { href: "/", label: "เทียบราคา", icon: Scale },
    { href: "/travel", label: "ดีลเที่ยว", icon: Plane },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-neutral-200/80 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5 group">
          <img
            src="/logo.svg"
            alt="Babman Picks Logo"
            width={38}
            height={38}
            className="h-9.5 w-9.5 rounded-xl shadow-sm shadow-orange-500/20 transition-transform group-hover:scale-105"
          />
          <div className="leading-tight">
            <div className="flex items-center gap-1.5 text-[15px] font-bold tracking-tight text-neutral-900">
              Babman Picks
              <ShieldCheck className="h-4 w-4 text-[#f04e23]" />
            </div>
            <div className="text-[11px] font-medium text-neutral-500">
              เทียบราคา Shopee vs Lazada
            </div>
          </div>
        </Link>

        <nav className="flex items-center gap-1.5 sm:gap-2">
          {navLinks.map(({ href, label, icon: Icon }) => {
            const active =
              href === "/"
                ? pathname === "/" || pathname.startsWith("/p/")
                : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`inline-flex items-center gap-1.5 rounded-full px-3.5 py-2 text-xs sm:text-sm font-semibold transition-all ${
                  active
                    ? "bg-[#f04e23] text-white shadow-sm shadow-orange-500/25"
                    : "text-neutral-600 hover:bg-orange-50 hover:text-[#f04e23]"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </Link>
            );
          })}
          <Link
            href="/admin"
            title="จัดการสินค้า / Neon DB"
            className={`hidden sm:inline-flex items-center gap-1 rounded-full border px-3 py-2 text-xs font-medium transition-colors ${
              pathname.startsWith("/admin")
                ? "border-orange-300 bg-orange-50 text-[#f04e23]"
                : "border-neutral-200 text-neutral-500 hover:border-orange-200 hover:text-[#f04e23]"
            }`}
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            <span>Admin</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
