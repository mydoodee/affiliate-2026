export interface Product {
  id?: number;
  code: string;
  title: string;
  description: string;
  price_display: string;
  price_num: number;
  sold_text: string;
  sold_num: number;
  rating: string;
  category: "cctv" | "home" | "kitchen" | "beauty" | "gadget" | string;
  badge: string;
  image_url: string;
  shopee_url: string;
  lazada_url: string;
  has_video: boolean;
  clicks_shopee: number;
  clicks_lazada: number;
  sort_order: number;
  is_active?: boolean;
}

export interface TravelDeal {
  id?: number;
  code: string;
  title: string;
  description: string;
  category: string;
  highlight: string;
  cta_text: string;
  affiliate_url: string;
  icon_key: "hotel" | "plane" | "esim" | "shield" | "car" | "card" | string;
  clicks: number;
  sort_order: number;
  is_active?: boolean;
}

export interface ClickStats {
  connected: boolean;
  totalProducts: number;
  totalTravelDeals: number;
  shopeeClicks: number;
  lazadaClicks: number;
  travelClicks: number;
}
