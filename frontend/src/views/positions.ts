import { api } from "../api/client";
import type { PositionByBook } from "../api/types";

export async function renderPositions(container: HTMLElement) {
  container.innerHTML = `<p class="loading">Loading positions…</p>`;

  try {
    const positions = await api.getPositions();
    container.innerHTML = buildTable(positions);
  } catch (err) {
    container.innerHTML = `<p class="error">Impossible to load the positions : ${(err as Error).message}</p>`;
  }
}

function formatUsd(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function buildTable(rows: PositionByBook[]): string {
  if (rows.length === 0) {
    return `<p>No position found.</p>`;
  }

  return `
    <table class="data-table">
      <thead>
        <tr>
          <th>Book</th>
          <th>Asset class</th>
          <th># Trades</th>
          <th>Gross exposure (USD)</th>
          <th>Net exposure (USD)</th>
        </tr>
      </thead>
      <tbody>
        ${rows
          .map(
            (row) => `
          <tr>
            <td>${row.book_id}</td>
            <td>${row.asset_class}</td>
            <td>${row.trade_count}</td>
            <td>${formatUsd(row.gross_exposure_usd)}</td>
            <td>${formatUsd(row.net_exposure_usd)}</td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
    <p class="note">
      USD Exposure.
    </p>
  `;
}
