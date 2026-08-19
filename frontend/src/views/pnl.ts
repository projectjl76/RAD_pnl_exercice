import { api } from "../api/client";
import type { DailyPnlByBook, PnlWarning } from "../api/types";

export async function renderPnl(container: HTMLElement) {
  container.innerHTML = `<p class="loading">Loading PNL…</p>`;

  try {
    const pnl = await api.getDailyPnl();
    const rows = pnl.filter((r): r is DailyPnlByBook => "book_id" in r);
    const warningEntry = pnl.find((r): r is PnlWarning => "_warnings" in r);

    container.innerHTML = `
      ${buildTable(rows)}
      ${warningEntry ? buildWarnings(warningEntry) : ""}
    `;
  } catch (err) {
    container.innerHTML = `<p class="error">Impossible to load P&amp;L : ${(err as Error).message}</p>`;
  }
}

function formatUsd(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
    signDisplay: "always",
  }).format(value);
}

function buildTable(rows: DailyPnlByBook[]): string {
  if (rows.length === 0) {
    return `<p>Aucun PNL currently calculated.</p>`;
  }

  const { as_of_date, prior_date } = rows[0];

  return `
    <p class="note">PNL ${as_of_date} from ${prior_date}</p>
    <table class="data-table">
      <thead>
        <tr><th>Book</th><th>Daily PNL (USD)</th></tr>
      </thead>
      <tbody>
        ${rows
          .map(
            (row) => `
          <tr>
            <td>${row.book_id}</td>
            <td class="${row.daily_pnl_usd >= 0 ? "status-ok" : "status-breach"}">
              ${formatUsd(row.daily_pnl_usd)}
            </td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function buildWarnings(entry: PnlWarning): string {
  return `
    <div class="warnings">
      ${entry._warnings.map((w) => `<p class="warning-item">⚠ ${w}</p>`).join("")}
    </div>
  `;
}
