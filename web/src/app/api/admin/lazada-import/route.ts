import { NextRequest, NextResponse } from "next/server";
import { isAdminAuthenticated } from "@/lib/auth";
import { getProducts, upsertProduct } from "@/lib/db";
import {
  extractLazadaItemId,
  fetchLazadaProductsByIds,
  generateLazadaLinksByIds,
} from "@/lib/lazada";

export const dynamic = "force-dynamic";

interface ParsedInputRow {
  lazadaId: string;
  brandOverride: string;
  category: string;
  shopeeUrl: string;
  shopeePrice: number;
  codeOverride: string;
}

function guessCategory(title: string, brand: string): string {
  const s = `${title} ${brand}`.toLowerCase();
  if (/กล้อง|cctv|wifi|4g|camera|wiodo/.test(s)) return "cctv";
  if (/หม้อ|กระทะ|เต้าหู้|กาต้ม|ปั่น|ทอดไร้น้ำมัน|seagull|locknlock|เตา/.test(s)) return "kitchen";
  if (/nivea|serum|เซรั่ม|โลชั่น|กันแดด|la roche|blanc|โปรตีน|baam|ผิว|แชมพู|ครีม|มิลค์|beauty/.test(s))
    return "beauty";
  if (/power bank|พาวเวอร์แบงค์|eloop|หูฟัง|สายชาร์จ|พัดลม.*พกพา|xiaomi|นาฬิกา|gadget/.test(s))
    return "gadget";
  return "home";
}

function formatSalesBadge(sales7d: number, commRate: number): string {
  const pct = Math.round(commRate * 100);
  if (sales7d >= 500) return `ฮิต ${sales7d.toLocaleString()}/สัปดาห์`;
  if (pct >= 12) return "Official Store";
  if (sales7d >= 50) return "ขายดีติดเทรนด์";
  return "Lazada API สด";
}

export async function POST(req: NextRequest) {
  if (!(await isAdminAuthenticated())) {
    return NextResponse.json(
      { ok: false, message: "กรุณาเข้าสู่ระบบแอดมินก่อน" },
      { status: 401 }
    );
  }

  try {
    const body = await req.json();
    const rawText = String(body.lines || "").trim();
    const defaultCategory = String(body.defaultCategory || "auto").trim();
    const defaultBrand = String(body.defaultBrand || "").trim();

    if (!rawText) {
      return NextResponse.json(
        { ok: false, message: "กรุณาวาง Lazada Item ID หรือลิงก์สินค้าอย่างน้อย 1 บรรทัด" },
        { status: 400 }
      );
    }

    // Supported line formats:
    // 1) 4831884381
    // 2) https://www.lazada.co.th/products/...-i4831884381.html
    // 3) 4831884381 | https://s.shopee.co.th/xxx | 520 | Breeze | home
    // 4) #08 | 5852773665  (update existing code)
    const parsedRows: ParsedInputRow[] = [];
    for (const line of rawText.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("# ")) continue;
      const parts = trimmed.split("|").map((x) => x.trim());

      let codeOverride = "";
      let firstCol = parts[0] || "";
      let offset = 0;

      if (/^#?\d{1,3}$/.test(firstCol) && parts.length >= 2) {
        codeOverride = firstCol.replace(/^#/, "").padStart(2, "0");
        firstCol = parts[1];
        offset = 1;
      }

      const lazadaId = extractLazadaItemId(firstCol);
      if (!lazadaId) continue;

      parsedRows.push({
        lazadaId,
        codeOverride,
        shopeeUrl: parts[1 + offset] || "",
        shopeePrice: Number((parts[2 + offset] || "").replace(/[^0-9.]/g, "")) || 0,
        brandOverride: parts[3 + offset] || defaultBrand,
        category: parts[4 + offset] || defaultCategory,
      });
    }

    if (!parsedRows.length) {
      return NextResponse.json(
        {
          ok: false,
          message: "ไม่พบ Lazada Item ID ที่ถูกต้อง (เช่น 4831884381 หรือลิงก์ที่มี -i4831884381)",
        },
        { status: 400 }
      );
    }

    const ids = parsedRows.map((r) => r.lazadaId);
    const [feedMap, linkMap, existingProducts] = await Promise.all([
      fetchLazadaProductsByIds(ids),
      generateLazadaLinksByIds(ids),
      getProducts(),
    ]);

    const existingByCode = new Map(existingProducts.map((p) => [p.code, p]));
    const existingByLazadaId = new Map(
      existingProducts
        .filter((p) => p.lazada_item_id)
        .map((p) => [String(p.lazada_item_id).trim(), p])
    );

    let maxCodeNum = existingProducts.reduce((mx, p) => {
      const n = Number(p.code);
      return Number.isFinite(n) && n > mx ? n : mx;
    }, 0);

    const imported: Array<{
      code: string;
      brand: string;
      title: string;
      lazadaPrice: number;
      shopeePrice: number;
      lazadaUrl: string;
      commissionPct: number;
    }> = [];
    const skipped: string[] = [];

    for (const row of parsedRows) {
      const feed = feedMap.get(row.lazadaId);
      const linkInfo = linkMap.get(row.lazadaId);

      if (!feed && !linkInfo) {
        skipped.push(`${row.lazadaId} (ไม่พบใน Lazada Affiliate Feed)`);
        continue;
      }

      const existing =
        (row.codeOverride ? existingByCode.get(row.codeOverride) : undefined) ||
        existingByLazadaId.get(row.lazadaId);

      let code = existing?.code || row.codeOverride;
      if (!code) {
        maxCodeNum += 1;
        code = String(maxCodeNum).padStart(2, "0");
      }

      const brand = row.brandOverride || existing?.brand || feed?.brandName || "Lazada Mall";
      const title = existing?.title || feed?.productName || `สินค้า Lazada #${row.lazadaId}`;
      const lazadaPrice = feed?.discountPrice || existing?.lazada_price || 0;
      const shopeePrice = row.shopeePrice || existing?.shopee_price || 0;
      const shopeeUrl = row.shopeeUrl || existing?.shopee_url || "";
      const lazadaUrl = linkInfo?.promotionLink || existing?.lazada_url || "";

      const prices = [shopeePrice, lazadaPrice].filter((n) => n > 0);
      const minP = prices.length ? Math.min(...prices) : 0;
      const maxP = prices.length ? Math.max(...prices) : 0;
      const priceDisplay =
        minP > 0
          ? maxP > minP
            ? `฿${minP.toLocaleString()} – ฿${maxP.toLocaleString()}`
            : `฿${minP.toLocaleString()}`
          : existing?.price_display || "เช็กราคา";

      const category =
        row.category && row.category !== "auto"
          ? row.category
          : existing?.category || guessCategory(title, brand);

      const soldText =
        existing?.sold_text ||
        (feed && feed.sales7d > 0 ? `ขาย ${feed.sales7d.toLocaleString()} ชิ้น/7 วัน` : "ร้านทางการ Lazada");

      await upsertProduct({
        code,
        brand,
        title,
        description:
          existing?.description ||
          `${brand} ร้านทางการบน Lazada (ซิงค์ราคาสดผ่าน Lazada Open API อัตโนมัติทุกวัน)`,
        price_display: priceDisplay,
        price_num: minP,
        shopee_price: shopeePrice,
        lazada_price: lazadaPrice,
        sold_text: soldText,
        sold_num: existing?.sold_num || (feed?.sales7d ? feed.sales7d * 4 : 0),
        rating: existing?.rating || "4.9",
        category,
        badge:
          existing?.badge ||
          formatSalesBadge(feed?.sales7d ?? 0, feed?.totalCommissionRate ?? 0),
        image_url: existing?.image_url || feed?.imageUrl || "",
        shopee_url: shopeeUrl,
        lazada_url: lazadaUrl,
        shopee_item_id: existing?.shopee_item_id || "",
        lazada_item_id: row.lazadaId,
        has_video: existing?.has_video || false,
        sort_order: existing?.sort_order || Number(code) || 100,
      });

      imported.push({
        code,
        brand,
        title,
        lazadaPrice,
        shopeePrice,
        lazadaUrl,
        commissionPct: Math.round((feed?.totalCommissionRate ?? 0) * 100),
      });
    }

    return NextResponse.json({
      ok: true,
      importedCount: imported.length,
      imported,
      skipped,
      message: `ดูดสินค้าจาก Lazada API + สร้างลิงก์สำเร็จ ${imported.length} รายการ${
        skipped.length ? ` (ข้าม ${skipped.length} รายการ)` : ""
      }`,
    });
  } catch (err) {
    return NextResponse.json(
      { ok: false, message: err instanceof Error ? err.message : "นำเข้าไม่สำเร็จ" },
      { status: 500 }
    );
  }
}
