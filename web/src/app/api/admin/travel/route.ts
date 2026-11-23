import { NextRequest, NextResponse } from "next/server";
import { isAdminAuthenticated } from "@/lib/auth";
import { deleteTravelDealByCode, getTravelDeals, upsertTravelDeal } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  if (!(await isAdminAuthenticated())) {
    return NextResponse.json({ ok: false, message: "Unauthorized" }, { status: 401 });
  }
  const deals = await getTravelDeals();
  return NextResponse.json({ ok: true, deals });
}

export async function POST(req: NextRequest) {
  if (!(await isAdminAuthenticated())) {
    return NextResponse.json({ ok: false, message: "กรุณาเข้าสู่ระบบแอดมินก่อน" }, { status: 401 });
  }
  try {
    const raw = await req.json();
    if (!raw?.code || !raw?.title || !raw?.affiliate_url) {
      return NextResponse.json(
        { ok: false, message: "กรุณากรอก รหัส, ชื่อดีล และลิงก์ Affiliate ให้ครบ" },
        { status: 400 }
      );
    }
    await upsertTravelDeal({
      code: String(raw.code).trim().toUpperCase(),
      title: String(raw.title).trim(),
      description: String(raw.description || "").trim(),
      category: String(raw.category || "ท่องเที่ยว").trim(),
      highlight: String(raw.highlight || "").trim(),
      cta_text: String(raw.cta_text || "เช็กโปรโมชัน").trim(),
      affiliate_url: String(raw.affiliate_url).trim(),
      logo_url: String(raw.logo_url || "").trim(),
      icon_key: String(raw.icon_key || "hotel").trim(),
      sort_order: Number(raw.sort_order) || 50,
    });
    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json(
      { ok: false, message: err instanceof Error ? err.message : "Failed to save deal" },
      { status: 500 }
    );
  }
}

export async function DELETE(req: NextRequest) {
  if (!(await isAdminAuthenticated())) {
    return NextResponse.json({ ok: false, message: "กรุณาเข้าสู่ระบบแอดมินก่อน" }, { status: 401 });
  }
  try {
    const code = req.nextUrl.searchParams.get("code");
    if (!code) {
      return NextResponse.json({ ok: false, message: "Missing code" }, { status: 400 });
    }
    await deleteTravelDealByCode(code);
    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json(
      { ok: false, message: err instanceof Error ? err.message : "Delete failed" },
      { status: 500 }
    );
  }
}
