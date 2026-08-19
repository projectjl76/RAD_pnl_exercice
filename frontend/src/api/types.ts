// Types reflétant la forme réelle des réponses de l'API backend
// (voir backend/app/services pour la logique qui les produit).

export interface PositionByBook {
  book_id: string;
  trade_count: number;
  asset_class: string;
  gross_exposure_usd: number;
  net_exposure_usd: number;
}

export type RiskStatus = "ok" | "warning" | "breach" | "n/a";

export interface RiskByBook {
  book_id: string;
  DV01?: number;
  Duration?: number;
  Spread01?: number;
  CS01_USD?: number;
  JTD_USD?: number;
  Delta_USD?: number;
  Gamma_USD?: number;
  Vega_USD?: number;
  Theta_USD?: number;
  _status: Record<string, RiskStatus>;
}

export interface DailyPnlByBook {
  book_id: string;
  daily_pnl_usd: number;
  as_of_date: string;
  prior_date: string;
}

export interface PnlWarning {
  _warnings: string[];
}

export type DailyPnlResponse = (DailyPnlByBook | PnlWarning)[];
