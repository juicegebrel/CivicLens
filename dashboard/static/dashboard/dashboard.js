(function () {
  const cfg = window.CIVICLENS;
  const peso = n => "₱" + Math.round(n).toLocaleString("en-PH");
  const el = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
  const NS = "http://www.w3.org/2000/svg";

  function drawDonut(stats) {
    const svg = el("donut");
    svg.innerHTML = "";
    const ring = document.createElementNS(NS, "circle");
    ring.setAttribute("cx", 21); ring.setAttribute("cy", 21); ring.setAttribute("r", 15.915);
    ring.setAttribute("fill", "none"); ring.setAttribute("stroke", "#e6eae2"); ring.setAttribute("stroke-width", 6);
    svg.appendChild(ring);
    let offset = 25; // start at 12 o'clock
    stats.statuses.forEach(s => {
      if (!s.count || !stats.total) return;
      const pct = (s.count / stats.total) * 100;
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("cx", 21); c.setAttribute("cy", 21); c.setAttribute("r", 15.915);
      c.setAttribute("fill", "none"); c.setAttribute("stroke", s.color); c.setAttribute("stroke-width", 6);
      c.setAttribute("stroke-dasharray", pct + " " + (100 - pct));
      c.setAttribute("stroke-dashoffset", offset);
      const t = document.createElementNS(NS, "title");
      t.textContent = s.label + ": " + s.count;
      c.appendChild(t);
      svg.appendChild(c);
      offset -= pct;
    });
    svg.setAttribute("aria-label", stats.statuses.map(s => s.label + " " + s.count).join(", "));
  }

  function render(stats) {
    el("total").textContent = stats.total;
    el("k-progress").textContent = stats.avg_progress + "%";
    el("k-done").textContent = stats.statuses.find(s => s.key === "completed").count;
    el("k-budget").textContent = peso(stats.total_budget);
    el("k-spent").textContent = peso(stats.completed_budget);
    el("asof").textContent = "As of " + stats.as_of;
    drawDonut(stats);

    el("legend").innerHTML = stats.statuses.map(s =>
      `<li><a href="${cfg.list}?status=${s.key}"><span class="sw" style="background:${s.color}"></span>${esc(s.label)}</a><span class="n"><strong>${s.count}</strong></span></li>`
    ).join("");

    const max = Math.max(1, ...stats.categories.map(c => c.total));
    el("cats").innerHTML = stats.categories.map(c => {
      const segs = stats.statuses.filter(s => c.by_status[s.key]).map(s =>
        `<span title="${esc(s.label)}: ${c.by_status[s.key]}" style="width:${(c.by_status[s.key] / max) * 100}%;background:${s.color}"></span>`
      ).join("");
      return `<div class="cat"><a href="${cfg.list}?category=${encodeURIComponent(c.slug)}"><span>${esc(c.name)}</span><strong>${c.total}</strong></a><div class="stack-bar">${segs}</div></div>`;
    }).join("") || '<p class="empty">No projects yet.</p>';

    el("recent").innerHTML = stats.recent.map(r =>
      `<li><a href="${cfg.detail}${encodeURIComponent(r.code)}/"><strong>${esc(r.title)}</strong></a><span class="muted">${esc(r.barangay)}</span>` +
      `<span class="badge"><span class="sw" style="background:${r.color};width:8px;height:8px"></span>${esc(r.status)}</span><span class="muted when">${esc(r.when)}</span></li>`
    ).join("") || '<li class="empty">No updates yet.</li>';
  }

  render(JSON.parse(el("stats-data").textContent));

  // Refresh every 30 seconds so the dashboard stays current without a reload.
  setInterval(() => {
    fetch(cfg.api, {headers: {"Accept": "application/json"}})
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(render)
      .catch(() => {});
  }, 30000);
})();
