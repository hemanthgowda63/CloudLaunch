"use strict";

const REFRESH_INTERVAL_MS = 5000;
const elements = {
  connection: document.querySelector("#connection"),
  lastUpdated: document.querySelector("#last-updated"),
  errorBanner: document.querySelector("#error-banner"),
  apiState: document.querySelector("#api-state"),
  cpuCores: document.querySelector("#cpu-cores"),
};

function formatBytes(bytes) {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`;
}

function setMetric(name, metric, detail) {
  const percent = Math.max(0, Math.min(100, Number(metric.percent) || 0));
  document.querySelector(`#${name}-value`).textContent = percent.toFixed(1);
  document.querySelector(`#${name}-meter`).style.width = `${percent}%`;
  document.querySelector(`#${name}-detail`).textContent = detail;
}

async function refreshDashboard() {
  try {
    const [metricsResponse, statusResponse] = await Promise.all([
      fetch("/api/metrics", { cache: "no-store" }),
      fetch("/api/status", { cache: "no-store" }),
    ]);
    if (!metricsResponse.ok || !statusResponse.ok) {
      throw new Error("The API returned an unsuccessful response.");
    }
    const [metrics, status] = await Promise.all([metricsResponse.json(), statusResponse.json()]);
    setMetric("cpu", metrics.cpu, `${metrics.cpu.cores} logical CPU cores`);
    setMetric("memory", metrics.memory, `${formatBytes(metrics.memory.used_bytes)} of ${formatBytes(metrics.memory.total_bytes)} used`);
    setMetric("disk", metrics.disk, `${formatBytes(metrics.disk.used_bytes)} of ${formatBytes(metrics.disk.total_bytes)} used · ${metrics.disk.path}`);
    elements.cpuCores.textContent = metrics.cpu.cores;
    elements.apiState.textContent = `Running · uptime ${Math.floor(status.uptime_seconds)}s`;
    elements.lastUpdated.textContent = new Date(metrics.timestamp).toLocaleTimeString();
    elements.connection.textContent = "Live";
    elements.connection.classList.add("is-live");
    elements.errorBanner.hidden = true;
  } catch (error) {
    console.error("Dashboard refresh failed:", error);
    elements.connection.textContent = "Offline";
    elements.connection.classList.remove("is-live");
    elements.apiState.textContent = "Unable to reach the local API";
    elements.errorBanner.hidden = false;
  }
}

refreshDashboard();
window.setInterval(refreshDashboard, REFRESH_INTERVAL_MS);
