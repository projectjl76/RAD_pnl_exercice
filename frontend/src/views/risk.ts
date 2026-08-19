import { api } from "../api/client";
import type { RiskByBook, RiskStatus } from "../api/types";

const METRICS = [
  "DV01",
  "Spread01",
  "CS01_USD",
  "JTD_USD",
  "Delta_USD",
  "Gamma_USD",
  "Vega_USD",
  "Theta_USD",
] as const;

export async function renderRisk(container: HTMLElement) {
  container.innerHTML = `<p class="loading">Loading risk…</p>`;

  try {
    const risk = await api.getRisk();
    container.innerHTML = buildTable(risk);
  } catch (err) {
    container.innerHTML = `<p class="error">Impossible to load risk : ${(err as Error).message}</p>`;
  }
}

function formatValue(v: number | undefined): string {
  if (v === undefined || v === 0) return "—";
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(v);
}

function statusClass(status: RiskStatus | undefined): string {
  if (status === "warning") return "status-warning";
  if (status === "breach") return "status-breach";
  if (status === "ok") return "status-ok";
  return "";
}

function buildTable(rows: RiskByBook[]): string {
  if (rows.length === 0) {
    return `<p>No risk data found.</p>`;
  }

  return `
    <table class="data-table">
      <thead>
        <tr>
          <th>Book</th>
          ${METRICS.map((m) => `<th>${m}</th>`).join("")}
        </tr>
      </thead>
      <tbody>
        ${rows
          .map(
            (row) => `
          <tr>
            <td>${row.book_id}</td>
            ${METRICS.map((m) => {
              const value = (row as any)[m] as number | undefined;
              const status = row._status?.[m];
              return `<td class="${statusClass(status)}">${formatValue(value)}</td>`;
            }).join("")}
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
  `;
}
