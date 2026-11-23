-- Neon Serverless PostgreSQL Schema for @mybabman Affiliate Storefront
-- Free tier (500 MB) easily supports 100,000+ products & click analytics

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
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_active_sort ON products(is_active, sort_order, id);

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
);

CREATE TABLE IF NOT EXISTS click_logs (
  id SERIAL PRIMARY KEY,
  target_type VARCHAR(24) NOT NULL,
  code VARCHAR(24) NOT NULL,
  platform VARCHAR(32) NOT NULL,
  referrer TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_click_logs_created ON click_logs(created_at DESC);
