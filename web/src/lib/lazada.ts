import crypto from "crypto";

export interface LazadaFeedItem {
  productId: string;
  productName: string;
  brandName: string;
  discountPrice: number;
  imageUrl: string;
  sales7d: number;
  totalCommissionRate: number;
  outOfStock: boolean;
  sellerName: string;
}

export interface LazadaLinkItem {
  productId: string;
  promotionLink: string;
  commission: string;
}

function getLazadaCreds() {
  const appKey = process.env.LAZADA_APP_KEY?.trim();
  const appSecret = process.env.LAZADA_APP_SECRET?.trim();
  const userToken = process.env.LAZADA_USER_TOKEN?.trim();
  if (!appKey || !appSecret || !userToken) {
    throw new Error("ยังไม่ได้ตั้งค่าคีย์ Lazada Open API ในระบบ");
  }
  return { appKey, appSecret, userToken };
}

export function signLazadaParams(
  apiPath: string,
  params: Record<string, string>,
  appSecret: string
): string {
  const sortedKeys = Object.keys(params).sort();
  let base = apiPath;
  for (const k of sortedKeys) {
    base += `${k}${params[k]}`;
  }
  return crypto
    .createHmac("sha256", appSecret)
    .update(base, "utf8")
    .digest("hex")
    .toUpperCase();
}

async function callLazadaOpenApi(
  apiPath: string,
  extraParams: Record<string, string>
): Promise<Record<string, unknown>> {
  const { appKey, appSecret, userToken } = getLazadaCreds();
  const params: Record<string, string> = {
    app_key: appKey,
    sign_method: "sha256",
    timestamp: String(Date.now()),
    userToken,
    ...extraParams,
  };
  params.sign = signLazadaParams(apiPath, params, appSecret);
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`https://api.lazada.co.th/rest${apiPath}?${qs}`, {
    method: "GET",
  });
  const json = (await res.json()) as Record<string, unknown>;
  if (json?.code && String(json.code) !== "0") {
    throw new Error(`Lazada API (${String(json.code)}): ${String(json.message ?? "error")}`);
  }
  return json;
}

export function extractLazadaItemId(raw: string): string {
  const s = raw.trim();
  if (/^\d{6,14}$/.test(s)) return s;
  const m =
    s.match(/-i(\d{6,14})/i) ||
    s.match(/itemId=(\d{6,14})/i) ||
    s.match(/productId=(\d{6,14})/i);
  return m ? m[1] : "";
}

export async function fetchLazadaProductsByIds(
  ids: string[]
): Promise<Map<string, LazadaFeedItem>> {
  const map = new Map<string, LazadaFeedItem>();
  const unique = Array.from(new Set(ids.filter(Boolean)));
  if (!unique.length) return map;

  // Chunk into batches of 30
  for (let i = 0; i < unique.length; i += 30) {
    const batch = unique.slice(i, i + 30);
    const json = await callLazadaOpenApi("/marketing/product/feed", {
      offerType: "1",
      productIds: JSON.stringify(batch),
      page: "1",
      limit: "50",
    });
    const resultObj = json.result as Record<string, unknown> | undefined;
    const list = (resultObj?.data ?? json.data ?? []) as Array<Record<string, unknown>>;
    if (!Array.isArray(list)) continue;

    for (const item of list) {
      const pid = String(item.productId ?? item.itemId ?? "");
      if (!pid) continue;
      const pics = Array.isArray(item.pictures) ? item.pictures : [];
      const firstPic = typeof pics[0] === "string" ? pics[0] : "";
      const brandRaw = String(item.brandName ?? "").trim();
      const brandName =
        brandRaw && brandRaw.toLowerCase() !== "no brand" ? brandRaw : "";

      map.set(pid, {
        productId: pid,
        productName: String(item.productName ?? "").trim(),
        brandName,
        discountPrice: Math.round(Number(item.discountPrice ?? item.price ?? 0)),
        imageUrl: firstPic,
        sales7d: Number(item.sales7d ?? 0),
        totalCommissionRate: Number(item.totalCommissionRate ?? 0),
        outOfStock: Boolean(item.outOfStock),
        sellerName: String(item.sellerName ?? "").trim(),
      });
    }
  }

  return map;
}

export async function generateLazadaLinksByIds(
  ids: string[]
): Promise<Map<string, LazadaLinkItem>> {
  const map = new Map<string, LazadaLinkItem>();
  const unique = Array.from(new Set(ids.filter(Boolean)));
  if (!unique.length) return map;

  // Batch up to 20 IDs per call
  for (let i = 0; i < unique.length; i += 20) {
    const batch = unique.slice(i, i + 20);
    const json = await callLazadaOpenApi("/marketing/getlink", {
      inputType: "productId",
      inputValue: batch.join(","),
    });
    const resultObj = json.result as Record<string, unknown> | undefined;
    const dataObj = (resultObj?.data ?? json.data) as Record<string, unknown> | undefined;
    const list = (dataObj?.productBatchGetLinkInfoList ?? []) as Array<Record<string, unknown>>;
    if (!Array.isArray(list)) continue;

    for (const row of list) {
      const pid = String(row.productId ?? "");
      const link = String(
        row.bonusPromotionLink || row.regularPromotionLink || row.promotionLink || ""
      ).trim();
      if (!pid || !link) continue;
      map.set(pid, {
        productId: pid,
        promotionLink: link,
        commission: String(row.bonusCommission || row.regularCommission || ""),
      });
    }
  }

  return map;
}
