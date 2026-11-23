import { NextRequest, NextResponse } from "next/server";
import { getProductByCode, getTravelDealByCode, recordClick } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ code: string }> }
) {
  const { code } = await context.params;
  const searchParams = request.nextUrl.searchParams;
  const type = searchParams.get("t") || "product";
  const platform = (searchParams.get("p") || "shopee").toLowerCase();
  const referrer = request.headers.get("referer") || "";

  if (type === "travel") {
    const deal = await getTravelDealByCode(code);
    if (!deal) {
      return NextResponse.redirect(new URL("/travel", request.url));
    }
    await recordClick("travel", deal.code, "accesstrade", referrer);
    return NextResponse.redirect(deal.affiliate_url, { status: 307 });
  }

  const product = await getProductByCode(code);
  if (!product) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  const targetUrl =
    platform === "lazada" && product.lazada_url
      ? product.lazada_url
      : product.shopee_url || product.lazada_url;

  if (!targetUrl) {
    return NextResponse.redirect(new URL(`/p/${encodeURIComponent(product.code)}`, request.url));
  }

  await recordClick("product", product.code, platform, referrer);
  return NextResponse.redirect(targetUrl, { status: 307 });
}
