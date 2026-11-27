"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Plane, Scale, ShieldCheck } from "lucide-react";

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
        </nav>
      </div>
    </header>
  );
}
