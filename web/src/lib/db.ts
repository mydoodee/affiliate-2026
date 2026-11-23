import { neon } from "@neondatabase/serverless";
import { SEED_PRODUCTS, SEED_TRAVEL_DEALS } from "./seed-data";
import type { ClickStats, Product, TravelDeal } from "./types";

function getDbUrl(): string | undefined {
  return (
    process.env.DATABASE_URL ||
    process.env.POSTGRES_URL ||
    process.env.NEON_DATABASE_URL
  );
}

export function isDbConfigured(): boolean {
  return Boolean(getDbUrl());
}

function getSql() {
  const url = getDbUrl();
  if (!url) return null;
  return neon(url);
}

export async function initAndSeedDb(): Promise<{
  ok: boolean;
  message: string;
  seededProducts?: number;
  seededTravel?: number;
}> {
  const sql = getSql();
  if (!sql) {
    return {
      ok: false,
      message: "ยังไม่ได้ตั้งค่า DATABASE_URL (กรุณาเชื่อมต่อ Neon PostgreSQL ใน Vercel หรือ .env.local)",
    };
  }

  await sql`
    CREATE TABLE IF NOT EXISTS products (
      id SERIAL PRIMARY KEY,
      code VARCHAR(24) UNIQUE NOT NULL,
      title TEXT NOT NULL,
      description TEXT NOT NULL DEFAULT '',
      price_display VARCHAR(64) NOT NULL,
      price_num INTEGER NOT NULL DEFAULT 0,
      sold_text VARCHAR(64) NOT NULL DEFAULT '',
      sold_num INTEGER NOT NULL DEFAULT 0,
      rating VARCHAR(16) NOT NULL DEFAULT '4.9',
      category VARCHAR(48) NOT NULL DEFAULT 'home',
      badge VARCHAR(64) NOT NULL DEFAULT '',
      image_url TEXT NOT NULL DEFAULT '',
      shopee_url TEXT NOT NULL DEFAULT '',
      lazada_url TEXT NOT NULL DEFAULT '',
      has_video BOOLEAN NOT NULL DEFAULT FALSE,
      clicks_shopee INTEGER NOT NULL DEFAULT 0,
      clicks_lazada INTEGER NOT NULL DEFAULT 0,
      sort_order INTEGER NOT NULL DEFAULT 100,
      is_active BOOLEAN NOT NULL DEFAULT TRUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  `;

  await sql`
    CREATE TABLE IF NOT EXISTS travel_deals (
      id SERIAL PRIMARY KEY,
      code VARCHAR(24) UNIQUE NOT NULL,
      title TEXT NOT NULL,
      description TEXT NOT NULL DEFAULT '',
      category VARCHAR(64) NOT NULL DEFAULT '',
      highlight VARCHAR(128) NOT NULL DEFAULT '',
      cta_text VARCHAR(64) NOT NULL DEFAULT 'เช็กราคาเลย',
      affiliate_url TEXT NOT NULL,
      icon_key VARCHAR(32) NOT NULL DEFAULT 'hotel',
      clicks INTEGER NOT NULL DEFAULT 0,
      sort_order INTEGER NOT NULL DEFAULT 100,
      is_active BOOLEAN NOT NULL DEFAULT TRUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  `;

  await sql`
    CREATE TABLE IF NOT EXISTS click_logs (
      id SERIAL PRIMARY KEY,
      target_type VARCHAR(24) NOT NULL,
      code VARCHAR(24) NOT NULL,
      platform VARCHAR(32) NOT NULL,
      referrer TEXT NOT NULL DEFAULT '',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  `;

  for (const p of SEED_PRODUCTS) {
    await sql`
      INSERT INTO products (
        code, title, description, price_display, price_num, sold_text, sold_num,
        rating, category, badge, image_url, shopee_url, lazada_url, has_video, sort_order
      ) VALUES (
        ${p.code}, ${p.title}, ${p.description}, ${p.price_display}, ${p.price_num},
        ${p.sold_text}, ${p.sold_num}, ${p.rating}, ${p.category}, ${p.badge},
        ${p.image_url}, ${p.shopee_url}, ${p.lazada_url}, ${p.has_video}, ${p.sort_order}
      )
      ON CONFLICT (code) DO NOTHING
    `;
  }

  for (const t of SEED_TRAVEL_DEALS) {
    await sql`
      INSERT INTO travel_deals (
        code, title, description, category, highlight, cta_text, affiliate_url, icon_key, sort_order
      ) VALUES (
        ${t.code}, ${t.title}, ${t.description}, ${t.category}, ${t.highlight},
        ${t.cta_text}, ${t.affiliate_url}, ${t.icon_key}, ${t.sort_order}
      )
      ON CONFLICT (code) DO NOTHING
    `;
  }

  return {
    ok: true,
    message: "สร้างตาราง Neon PostgreSQL และนำเข้าข้อมูลเริ่มต้นเรียบร้อยแล้ว",
    seededProducts: SEED_PRODUCTS.length,
    seededTravel: SEED_TRAVEL_DEALS.length,
  };
}

export async function getProducts(): Promise<Product[]> {
  const sql = getSql();
  if (!sql) return SEED_PRODUCTS;
  try {
    const rows = await sql`
      SELECT id, code, title, description, price_display, price_num, sold_text, sold_num,
             rating, category, badge, image_url, shopee_url, lazada_url, has_video,
             clicks_shopee, clicks_lazada, sort_order, is_active
      FROM products
      WHERE is_active = TRUE
      ORDER BY sort_order ASC, id ASC
    `;
    if (!rows.length) return SEED_PRODUCTS;
    return rows as unknown as Product[];
  } catch {
    return SEED_PRODUCTS;
  }
}

export async function getProductByCode(code: string): Promise<Product | null> {
  const clean = code.trim();
  const sql = getSql();
  if (sql) {
    try {
      const rows = await sql`
        SELECT id, code, title, description, price_display, price_num, sold_text, sold_num,
               rating, category, badge, image_url, shopee_url, lazada_url, has_video,
               clicks_shopee, clicks_lazada, sort_order, is_active
        FROM products
        WHERE code = ${clean}
        LIMIT 1
      `;
      if (rows.length) return rows[0] as unknown as Product;
    } catch {
      // fall back to seed
    }
  }
  return SEED_PRODUCTS.find((p) => p.code === clean) ?? null;
}

export async function getTravelDeals(): Promise<TravelDeal[]> {
  const sql = getSql();
  if (!sql) return SEED_TRAVEL_DEALS;
  try {
    const rows = await sql`
      SELECT id, code, title, description, category, highlight, cta_text, affiliate_url,
             icon_key, clicks, sort_order, is_active
      FROM travel_deals
      WHERE is_active = TRUE
      ORDER BY sort_order ASC, id ASC
    `;
    if (!rows.length) return SEED_TRAVEL_DEALS;
    return rows as unknown as TravelDeal[];
  } catch {
    return SEED_TRAVEL_DEALS;
  }
}

export async function getTravelDealByCode(code: string): Promise<TravelDeal | null> {
  const clean = code.trim().toUpperCase();
  const sql = getSql();
  if (sql) {
    try {
      const rows = await sql`
        SELECT id, code, title, description, category, highlight, cta_text, affiliate_url,
               icon_key, clicks, sort_order, is_active
        FROM travel_deals
        WHERE UPPER(code) = ${clean}
        LIMIT 1
      `;
      if (rows.length) return rows[0] as unknown as TravelDeal;
    } catch {
      // fall back
    }
  }
  return SEED_TRAVEL_DEALS.find((t) => t.code.toUpperCase() === clean) ?? null;
}

export async function recordClick(
  targetType: "product" | "travel",
  code: string,
  platform: string,
  referrer: string
): Promise<void> {
  const sql = getSql();
  if (!sql) return;
  try {
    await sql`
      INSERT INTO click_logs (target_type, code, platform, referrer)
      VALUES (${targetType}, ${code}, ${platform}, ${referrer.slice(0, 240)})
    `;
    if (targetType === "product") {
      if (platform === "lazada") {
        await sql`UPDATE products SET clicks_lazada = clicks_lazada + 1 WHERE code = ${code}`;
      } else {
        await sql`UPDATE products SET clicks_shopee = clicks_shopee + 1 WHERE code = ${code}`;
      }
    } else {
      await sql`UPDATE travel_deals SET clicks = clicks + 1 WHERE UPPER(code) = ${code.toUpperCase()}`;
    }
  } catch {
    // Non-blocking: never break user redirect
  }
}

export async function upsertProduct(p: Omit<Product, "id" | "clicks_shopee" | "clicks_lazada">): Promise<void> {
  const sql = getSql();
  if (!sql) throw new Error("DATABASE_URL is not configured");
  await sql`
    INSERT INTO products (
      code, title, description, price_display, price_num, sold_text, sold_num,
      rating, category, badge, image_url, shopee_url, lazada_url, has_video, sort_order
    ) VALUES (
      ${p.code}, ${p.title}, ${p.description}, ${p.price_display}, ${p.price_num},
      ${p.sold_text}, ${p.sold_num}, ${p.rating}, ${p.category}, ${p.badge},
      ${p.image_url}, ${p.shopee_url}, ${p.lazada_url}, ${p.has_video}, ${p.sort_order}
    )
    ON CONFLICT (code) DO UPDATE SET
      title = EXCLUDED.title,
      description = EXCLUDED.description,
      price_display = EXCLUDED.price_display,
      price_num = EXCLUDED.price_num,
      sold_text = EXCLUDED.sold_text,
      sold_num = EXCLUDED.sold_num,
      rating = EXCLUDED.rating,
      category = EXCLUDED.category,
      badge = EXCLUDED.badge,
      image_url = CASE WHEN EXCLUDED.image_url <> '' THEN EXCLUDED.image_url ELSE products.image_url END,
      shopee_url = CASE WHEN EXCLUDED.shopee_url <> '' THEN EXCLUDED.shopee_url ELSE products.shopee_url END,
      lazada_url = CASE WHEN EXCLUDED.lazada_url <> '' THEN EXCLUDED.lazada_url ELSE products.lazada_url END,
      has_video = EXCLUDED.has_video,
      sort_order = EXCLUDED.sort_order,
      updated_at = NOW()
  `;
}

export async function deleteProductByCode(code: string): Promise<void> {
  const sql = getSql();
  if (!sql) throw new Error("DATABASE_URL is not configured");
  await sql`DELETE FROM products WHERE code = ${code}`;
}

export async function getClickStats(): Promise<ClickStats> {
  const sql = getSql();
  if (!sql) {
    return {
      connected: false,
      totalProducts: SEED_PRODUCTS.length,
      totalTravelDeals: SEED_TRAVEL_DEALS.length,
      shopeeClicks: 0,
      lazadaClicks: 0,
      travelClicks: 0,
    };
  }
  try {
    const [pRow] = await sql`
      SELECT COUNT(*)::int AS cnt,
             COALESCE(SUM(clicks_shopee), 0)::int AS sh,
             COALESCE(SUM(clicks_lazada), 0)::int AS lz
      FROM products WHERE is_active = TRUE
    `;
    const [tRow] = await sql`
      SELECT COUNT(*)::int AS cnt,
             COALESCE(SUM(clicks), 0)::int AS tc
      FROM travel_deals WHERE is_active = TRUE
    `;
    return {
      connected: true,
      totalProducts: pRow?.cnt ?? 0,
      totalTravelDeals: tRow?.cnt ?? 0,
      shopeeClicks: pRow?.sh ?? 0,
      lazadaClicks: pRow?.lz ?? 0,
      travelClicks: tRow?.tc ?? 0,
    };
  } catch {
    return {
      connected: false,
      totalProducts: SEED_PRODUCTS.length,
      totalTravelDeals: SEED_TRAVEL_DEALS.length,
      shopeeClicks: 0,
      lazadaClicks: 0,
      travelClicks: 0,
    };
  }
}
