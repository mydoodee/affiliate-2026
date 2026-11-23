import { NextRequest, NextResponse } from "next/server";
import { isAdminAuthenticated } from "@/lib/auth";
import { deleteProductByCode, getProducts, upsertProduct } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  if (!(await isAdminAuthenticated())) {
    return NextResponse.json({ ok: false, message: "Unauthorized" }, { status: 401 });
  }
  const products = await getProducts();
  return NextResponse.json({ ok: true, products });
}

export async function POST(req: NextRequest) {
  if (!(await isAdminAuthenticated())) {
    return NextResponse.json({ ok: false, message: "กรุณาเข้าสู่ระบบแอดมินก่อน" }, { status: 401 });
  }
  try {
    const body = await req.json();
    const items = Array.isArray(body.items) ? body.items : [body];
    let count = 0;
    for (const raw of items) {
      if (!raw?.code || !raw?.title) continue;
      await upsertProduct({
        code: String(raw.code).trim(),
        title: String(raw.title).trim(),
        description: String(raw.description || "").trim(),
        price_display: String(raw.price_display || `฿${raw.price_num || 0}`).trim(),
        price_num: Number(raw.price_num) || 0,
        sold_text: String(raw.sold_text || "").trim(),
        sold_num: Number(raw.sold_num) || 0,
        rating: String(raw.rating || "4.9").trim(),
        category: String(raw.category || "home").trim(),
        badge: String(raw.badge || "").trim(),
        image_url: String(raw.image_url || "").trim(),
        shopee_url: String(raw.shopee_url || "").trim(),
        lazada_url: String(raw.lazada_url || "").trim(),
        has_video: Boolean(raw.has_video),
        sort_order: Number(raw.sort_order) || 100,
      });
      count++;
    }
    return NextResponse.json({ ok: true, saved: count });
  } catch (err) {
    return NextResponse.json(
      { ok: false, message: err instanceof Error ? err.message : "Failed to save" },
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
    await deleteProductByCode(code);
    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json(
      { ok: false, message: err instanceof Error ? err.message : "Delete failed" },
      { status: 500 }
    );
  }
}
