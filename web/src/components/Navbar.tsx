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
        <Link href="/" className="flex min-w-0 items-center gap-2 group sm:gap-2.5">
          <img
            src="/logo.svg"
            alt="Babman Picks Logo"
            width={38}
            height={38}
            className="h-9 w-9 shrink-0 rounded-xl shadow-sm shadow-orange-500/20 transition-transform group-hover:scale-105 sm:h-9.5 sm:w-9.5"
          />
          <div className="min-w-0 leading-tight">
            <div className="flex items-center gap-1 text-[14px] font-bold tracking-tight text-neutral-900 whitespace-nowrap sm:text-[15px]">
              Babman Picks
              <ShieldCheck className="h-3.5 w-3.5 shrink-0 text-[#f04e23] sm:h-4 sm:w-4" />
            </div>
            <div className="truncate text-[10px] font-medium text-neutral-500 sm:text-[11px]">
              Shopee vs Lazada
            </div>
          </div>
        </Link>

        <nav className="flex shrink-0 items-center gap-1 sm:gap-2">
          {navLinks.map(({ href, label, icon: Icon }) => {
            const active =
              href === "/"
                ? pathname === "/" || pathname.startsWith("/p/")
                : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`inline-flex shrink-0 items-center gap-1 whitespace-nowrap rounded-full px-2.5 py-1.5 text-[11px] font-semibold transition-all sm:gap-1.5 sm:px-3.5 sm:py-2 sm:text-sm ${
                  active
                    ? "bg-[#f04e23] text-white shadow-sm shadow-orange-500/25"
                    : "text-neutral-600 hover:bg-orange-50 hover:text-[#f04e23]"
                }`}
              >
                <Icon className="h-3.5 w-3.5 shrink-0 sm:h-4 sm:w-4" />
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
