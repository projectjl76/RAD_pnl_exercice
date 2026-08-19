import "./style.css";
import { renderPositions } from "./views/positions";
import { renderPnl } from "./views/pnl";
import { renderRisk } from "./views/risk";

type Tab = "positions" | "pnl" | "risk";

const TAB_LABELS: Record<Tab, string> = {
  positions: "Positions",
  pnl: "P&L",
  risk: "Risk",
};

const app = document.querySelector<HTMLDivElement>("#app")!;

app.innerHTML = `
  <header>
    <h1>Desk Risk &amp; P&amp;L</h1>
    <p class="subtitle">Global Markets · Front Office — Prototype</p>
  </header>
  <nav id="tabs"></nav>
  <main id="content"></main>
`;

const tabsEl = document.querySelector<HTMLElement>("#tabs")!;
const contentEl = document.querySelector<HTMLElement>("#content")!;

const renderers: Record<Tab, (el: HTMLElement) => Promise<void>> = {
  positions: renderPositions,
  pnl: renderPnl,
  risk: renderRisk,
};

function setActiveTab(tab: Tab) {
  tabsEl.querySelectorAll("button").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-tab") === tab);
  });
  renderers[tab](contentEl);
}

tabsEl.innerHTML = (Object.keys(TAB_LABELS) as Tab[])
  .map((tab) => `<button data-tab="${tab}">${TAB_LABELS[tab]}</button>`)
  .join("");

tabsEl.querySelectorAll("button").forEach((btn) => {
  btn.addEventListener("click", () =>
    setActiveTab(btn.getAttribute("data-tab") as Tab)
  );
});

setActiveTab("positions");
