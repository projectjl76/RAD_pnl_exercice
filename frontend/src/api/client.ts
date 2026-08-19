import type { PositionByBook, RiskByBook, DailyPnlResponse } from "./types";

const API_BASE_URL = "http://localhost:8000/api";

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Erreur API ${response.status} sur ${path} : ${detail}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  getPositions: () => get<PositionByBook[]>("/positions/"),
  getRisk: () => get<RiskByBook[]>("/risk/"),
  getDailyPnl: () => get<DailyPnlResponse>("/pnl/daily"),
};
