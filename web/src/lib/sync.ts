import crypto from "crypto";
import { neon, type NeonQueryFunction } from "@neondatabase/serverless";
import type { SyncStatusInfo } from "./types";

type SqlClient = NeonQueryFunction<false, false>;

function getDbUrl(): string | undefined {
  return (
    process.env.DATABASE_URL ||
    process.env.POSTGRES_URL ||
    process.env.NEON_DATABASE_URL
  );
}

export function getSyncEnvStatus() {
  const shopeeConfigured = Boolean(
    process.env.SHOPEE_APP_ID && process.env.SHOPEE_APP_SECRET
  );
  const lazadaConfigured = Boolean(
    process.env.LAZADA_APP_KEY &&
      process.env.LAZADA_APP_SECRET &&
      process.env.LAZADA_USER_TOKEN
  );
  return { shopeeConfigured, lazadaConfigured };
}

export async function getSyncStatus(): Promise<SyncStatusInfo> {
  const { shopeeConfigured, lazadaConfigured } = getSyncEnvStatus();
  const url = getDbUrl();
  if (!url) {
    return {
      shopeeConfigured,
      lazadaConfigured,
      lastSyncAt: null,
      lastSyncMessage: null,
    };
  }
  try {
    const sql = neon(url);
    const rows = await sql`
      SELECT created_at, message
      FROM sync_logs
      ORDER BY created_at DESC
      LIMIT 1
    `;
    if (rows.length) {
      return {
        shopeeConfigured,
        lazadaConfigured,
        lastSyncAt: String(rows[0].created_at),
        lastSyncMessage: String(rows[0].message ?? ""),
      };
    }
  } catch {
    // Table may not exist yet before initDb
  }
  return {
    shopeeConfigured,
    lazadaConfigured,
    lastSyncAt: null,
    lastSyncMessage: null,
  };
}

function formatSold(n: number): string {
  if (!Number.isFinite(n) || n <= 0) return "";
  if (n >= 1000) return `ขายแล้ว ${Math.floor(n / 1000).toLocaleString()}k+`;
  return `ขายแล้ว ${n.toLocaleString()}`;
}

function signLazadaParams(
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

async function syncShopeeProducts(
  sql: SqlClient
): Promise<{ updated: number; errors: string[] }> {
  const appId = process.env.SHOPEE_APP_ID?.trim();
  const appSecret = process.env.SHOPEE_APP_SECRET?.trim();
  if (!appId || !appSecret) return { updated: 0, errors: [] };

  const products = await sql`
    SELECT code, shopee_item_id, COALESCE(lazada_price, 0) AS lazada_price
    FROM products
    WHERE is_active = TRUE AND shopee_item_id <> ''
  `;

  let updated = 0;
  const errors: string[] = [];

  for (const row of products) {
    const itemId = Number(row.shopee_item_id);
    if (!Number.isFinite(itemId) || itemId <= 0) continue;

    const query = `query { productOfferV2(itemId: ${itemId}, limit: 1) { nodes { itemId productName priceMin priceMax sales ratingStar imageUrl } } }`;
    const payload = JSON.stringify({ query });
    const ts = Math.floor(Date.now() / 1000);
    const sig = crypto
      .createHash("sha256")
      .update(`${appId}${ts}${payload}${appSecret}`)
      .digest("hex");

    try {
      const res = await fetch("https://open-api.affiliate.shopee.co.th/graphql", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `SHA256 Credential=${appId}, Timestamp=${ts}, Signature=${sig}`,
        },
        body: payload,
      });
      const json = await res.json();
      const node = json?.data?.productOfferV2?.nodes?.[0];
      if (!node) continue;

      const pMin = Math.round(Number(node.priceMin || 0));
      const lzP = Number(row.lazada_price || 0);
      const minP = lzP > 0 ? Math.min(pMin, lzP) : pMin;
      const maxP = lzP > 0 ? Math.max(pMin, lzP) : Math.round(Number(node.priceMax || pMin));
      const priceDisplay =
        minP > 0
          ? maxP > minP
            ? `฿${minP.toLocaleString()} – ฿${maxP.toLocaleString()}`
            : `฿${minP.toLocaleString()}`
          : "";
      const soldNum = Number(node.sales || 0);
      const soldText = formatSold(soldNum);
      const rating = node.ratingStar ? Number(node.ratingStar).toFixed(1) : "";
      const imgUrl = typeof node.imageUrl === "string" ? node.imageUrl : "";

      if (pMin > 0) {
        await sql`
          UPDATE products
          SET shopee_price = ${pMin},
              price_num = ${minP},
              price_display = ${priceDisplay},
              sold_num = CASE WHEN ${soldNum} > 0 THEN ${soldNum} ELSE sold_num END,
              sold_text = CASE WHEN ${soldText} <> '' THEN ${soldText} ELSE sold_text END,
              rating = CASE WHEN ${rating} <> '' THEN ${rating} ELSE rating END,
              image_url = CASE WHEN ${imgUrl} <> '' THEN ${imgUrl} ELSE image_url END,
              last_synced_at = NOW(),
              updated_at = NOW()
          WHERE code = ${String(row.code)}
        `;
        updated += 1;
      }
    } catch (err) {
      errors.push(
        `Shopee #${row.code}: ${err instanceof Error ? err.message : "fetch failed"}`
      );
    }
  }

  return { updated, errors };
}

async function syncLazadaProducts(
  sql: SqlClient
): Promise<{ updated: number; errors: string[] }> {
  const appKey = process.env.LAZADA_APP_KEY?.trim();
  const appSecret = process.env.LAZADA_APP_SECRET?.trim();
  const userToken = process.env.LAZADA_USER_TOKEN?.trim();
  if (!appKey || !appSecret || !userToken) return { updated: 0, errors: [] };

  const products = await sql`
    SELECT code, lazada_item_id, price_num, COALESCE(shopee_price, 0) AS shopee_price
    FROM products
    WHERE is_active = TRUE AND lazada_item_id <> ''
  `;

  if (!products.length) return { updated: 0, errors: [] };

  const itemIds = products
    .map((p) => String(p.lazada_item_id).trim())
    .filter(Boolean);

  const apiPath = "/marketing/product/feed";
  const params: Record<string, string> = {
    app_key: appKey,
    sign_method: "sha256",
    timestamp: String(Date.now()),
    userToken,
    offerType: "1",
    productIds: JSON.stringify(itemIds),
    page: "1",
    limit: "50",
  };
  params.sign = signLazadaParams(apiPath, params, appSecret);

  const qs = new URLSearchParams(params).toString();
  let updated = 0;
  const errors: string[] = [];

  try {
    const res = await fetch(`https://api.lazada.co.th/rest${apiPath}?${qs}`, {
      method: "GET",
    });
    const json = await res.json();
    if (json?.code && String(json.code) !== "0") {
      errors.push(`Lazada API (${json.code}): ${String(json.message ?? "error")}`);
      return { updated, errors };
    }
    const list: Array<Record<string, unknown>> =
      json?.result?.data ?? json?.data ?? [];

    if (!Array.isArray(list)) {
      if (json?.message) errors.push(`Lazada API: ${String(json.message)}`);
      return { updated, errors };
    }

    const byId = new Map<string, Record<string, unknown>>();
    for (const item of list) {
      const pid = String(item.productId ?? item.itemId ?? "");
      if (pid) byId.set(pid, item);
    }

    for (const row of products) {
      const match = byId.get(String(row.lazada_item_id).trim());
      if (!match) continue;
      if (match.outOfStock === true) {
        errors.push(`Lazada #${row.code} สินค้าหมดชั่วคราว`);
      }
      const discountPrice = Math.round(
        Number(match.discountPrice ?? match.price ?? 0)
      );
      if (discountPrice <= 0) continue;

      // Recompute range accurately from shopee_price + live Lazada discountPrice
      const shP = Number(row.shopee_price || 0);
      const minP = shP > 0 ? Math.min(shP, discountPrice) : discountPrice;
      const maxP = shP > 0 ? Math.max(shP, discountPrice) : discountPrice;
      const priceDisplay =
        maxP > minP
          ? `฿${minP.toLocaleString()} – ฿${maxP.toLocaleString()}`
          : `฿${minP.toLocaleString()}`;

      await sql`
        UPDATE products
        SET lazada_price = ${discountPrice},
            price_num = ${minP},
            price_display = ${priceDisplay},
            last_synced_at = NOW(),
            updated_at = NOW()
        WHERE code = ${String(row.code)}
      `;
      updated += 1;
    }
  } catch (err) {
    errors.push(
      `Lazada API: ${err instanceof Error ? err.message : "fetch failed"}`
    );
  }

  return { updated, errors };
}

export async function runFullProductSync(trigger: "cron" | "manual"): Promise<{
  ok: boolean;
  updated: number;
  message: string;
  shopeeUpdated: number;
  lazadaUpdated: number;
}> {
  const url = getDbUrl();
  if (!url) {
    return {
      ok: false,
      updated: 0,
      shopeeUpdated: 0,
      lazadaUpdated: 0,
      message: "ยังไม่ได้เชื่อมต่อ Neon PostgreSQL (DATABASE_URL)",
    };
  }

  const sql = neon(url);
  const { shopeeConfigured, lazadaConfigured } = getSyncEnvStatus();

  if (!shopeeConfigured && !lazadaConfigured) {
    const msg =
      "ฐานข้อมูล Neon พร้อมแล้ว แต่ยังรอคีย์ Lazada Open API (Pending) หรือ Shopee Open API ใน Vercel Env Vars";
    try {
      await sql`
        INSERT INTO sync_logs (source, status, updated_count, message)
        VALUES (${trigger}, 'waiting_keys', 0, ${msg})
      `;
    } catch {
      // ignore if sync_logs not initialized
    }
    return {
      ok: true,
      updated: 0,
      shopeeUpdated: 0,
      lazadaUpdated: 0,
      message: msg,
    };
  }

  const [sh, lz] = await Promise.all([
    syncShopeeProducts(sql),
    syncLazadaProducts(sql),
  ]);

  const totalUpdated = sh.updated + lz.updated;
  const allErrors = [...sh.errors, ...lz.errors];
  const status = allErrors.length ? "partial" : "success";
  const message = allErrors.length
    ? `ซิงค์สำเร็จ ${totalUpdated} รายการ (Shopee ${sh.updated}, Lazada ${lz.updated}) • พบข้อสังเกต: ${allErrors.slice(0, 2).join("; ")}`
    : `ซิงค์ราคาล่าสุดสำเร็จ ${totalUpdated} รายการ (Shopee ${sh.updated}, Lazada ${lz.updated})`;

  try {
    await sql`
      INSERT INTO sync_logs (source, status, updated_count, message)
      VALUES (${trigger}, ${status}, ${totalUpdated}, ${message})
    `;
  } catch {
    // non-blocking
  }

  return {
    ok: true,
    updated: totalUpdated,
    shopeeUpdated: sh.updated,
    lazadaUpdated: lz.updated,
    message,
  };
}
