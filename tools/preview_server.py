from __future__ import annotations

import html
import json
from datetime import date, datetime
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import psycopg2
from psycopg2.extras import RealDictCursor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PORT = 8000


def load_env() -> dict[str, str]:
    env_path = PROJECT_ROOT / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


ENV = load_env()


def db_rows(sql: str, params: dict[str, object] | None = None) -> list[dict[str, object]]:
    connection = psycopg2.connect(
        host=ENV.get("POSTGRES_HOST", "localhost"),
        port=ENV.get("POSTGRES_PORT", "5432"),
        dbname=ENV.get("POSTGRES_DB", "retail_warehouse"),
        user=ENV.get("POSTGRES_USER", "postgres"),
        password=ENV.get("POSTGRES_PASSWORD", ""),
    )
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params or {})
            return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


def convert_json(value: object) -> object:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def as_float(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def as_int(value: object) -> int:
    if value is None:
        return 0
    return int(value)


def money(value: object) -> str:
    amount = as_float(value)
    if abs(amount) >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    if abs(amount) >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    return f"${amount:,.2f}"


def number(value: object) -> str:
    return f"{as_float(value):,.0f}"


def pct(value: object) -> str:
    if value is None:
        return "n/a"
    return f"{as_float(value):,.1f}%"


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


def layout(title: str, active: str, content: str) -> str:
    nav_items = [
        ("/", "Overview", "overview"),
        ("/sales-overview", "Sales", "sales"),
        ("/top-products?limit=15", "Products", "products"),
        ("/store-performance?limit=20", "Stores", "stores"),
        ("/health", "Health", "health"),
    ]
    nav_html = "\n".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for href, label, key in nav_items
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root {{
      --ink: #18212f;
      --muted: #647184;
      --line: #d7dee8;
      --panel: #ffffff;
      --canvas: #f3f6f8;
      --teal: #0f766e;
      --coral: #c2412d;
      --amber: #b7791f;
      --violet: #6d5bd0;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--canvas);
      color: var(--ink);
      font-family: Segoe UI, Arial, sans-serif;
      line-height: 1.45;
    }}
    header {{
      background: #ffffff;
      border-bottom: 1px solid var(--line);
      padding: 18px 28px;
      position: sticky;
      top: 0;
      z-index: 1;
    }}
    .topbar {{
      align-items: center;
      display: flex;
      gap: 20px;
      justify-content: space-between;
      margin: 0 auto;
      max-width: 1180px;
    }}
    .brand strong {{ display: block; font-size: 20px; }}
    .brand span {{ color: var(--muted); font-size: 13px; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    nav a {{
      border: 1px solid transparent;
      border-radius: 6px;
      color: var(--ink);
      padding: 8px 10px;
      text-decoration: none;
    }}
    nav a.active, nav a:hover {{
      background: #e7f3f1;
      border-color: #b9ddd8;
      color: #0f5f59;
    }}
    main {{
      margin: 0 auto;
      max-width: 1180px;
      padding: 28px;
    }}
    h1 {{ font-size: 34px; letter-spacing: 0; margin: 0 0 8px; }}
    h2 {{ font-size: 19px; margin: 0 0 14px; }}
    p {{ color: var(--muted); margin: 0; }}
    .section {{ margin-top: 24px; }}
    .grid {{ display: grid; gap: 16px; }}
    .grid.kpis {{ grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
    .grid.two {{ grid-template-columns: minmax(0, 1.45fr) minmax(320px, .85fr); }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .kpi-label {{ color: var(--muted); font-size: 13px; }}
    .kpi-value {{ font-size: 26px; font-weight: 750; margin-top: 6px; }}
    .kpi-note {{ color: var(--muted); font-size: 12px; margin-top: 8px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px 8px; text-align: left; }}
    th {{ color: var(--muted); font-size: 12px; font-weight: 650; text-transform: uppercase; }}
    td.num, th.num {{ text-align: right; }}
    .bars {{ display: grid; gap: 10px; }}
    .bar-row {{
      align-items: center;
      display: grid;
      gap: 10px;
      grid-template-columns: 92px 1fr 88px;
    }}
    .track {{ background: #edf1f5; border-radius: 6px; height: 12px; overflow: hidden; }}
    .fill {{ background: var(--teal); height: 100%; }}
    .fill.alt {{ background: var(--coral); }}
    .fill.warn {{ background: var(--amber); }}
    .pill {{
      background: #eef2f7;
      border-radius: 999px;
      color: #475569;
      display: inline-block;
      font-size: 12px;
      padding: 3px 8px;
    }}
    .muted {{ color: var(--muted); }}
    .hero {{
      align-items: end;
      display: grid;
      gap: 18px;
      grid-template-columns: minmax(0, 1fr) auto;
    }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .button {{
      background: var(--ink);
      border-radius: 6px;
      color: #ffffff;
      padding: 9px 12px;
      text-decoration: none;
    }}
    .button.secondary {{ background: #ffffff; border: 1px solid var(--line); color: var(--ink); }}
    @media (max-width: 900px) {{
      .grid.two, .hero {{ grid-template-columns: 1fr; }}
      main {{ padding: 18px; }}
      header {{ padding: 14px 18px; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .bar-row {{ grid-template-columns: 76px 1fr 74px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <div class="brand"><strong>Retail Intelligence Platform</strong><span>PostgreSQL marts running locally</span></div>
      <nav>{nav_html}</nav>
    </div>
  </header>
  <main>{content}</main>
</body>
</html>"""


def dashboard_summary() -> dict[str, object]:
    return db_rows(
        """
        SELECT
            ROUND(SUM(total_revenue), 2) AS total_revenue,
            SUM(total_orders)::integer AS total_orders,
            ROUND(SUM(total_quantity), 2) AS total_quantity,
            ROUND(SUM(total_revenue) / NULLIF(SUM(total_orders), 0), 2) AS average_order_value,
            COUNT(*)::integer AS monthly_rows
        FROM marts.sales_overview
        """
    )[0]


def render_kpis(summary: dict[str, object]) -> str:
    return f"""
<section class="section grid kpis">
  <div class="card"><div class="kpi-label">Total revenue</div><div class="kpi-value">{money(summary["total_revenue"])}</div><div class="kpi-note">Across both source systems</div></div>
  <div class="card"><div class="kpi-label">Orders and observations</div><div class="kpi-value">{number(summary["total_orders"])}</div><div class="kpi-note">Invoices plus Walmart weekly records</div></div>
  <div class="card"><div class="kpi-label">Known units sold</div><div class="kpi-value">{number(summary["total_quantity"])}</div><div class="kpi-note">Online Retail quantity only</div></div>
  <div class="card"><div class="kpi-label">Average order value</div><div class="kpi-value">{money(summary["average_order_value"])}</div><div class="kpi-note">Revenue divided by order count</div></div>
</section>"""


def monthly_sales_rows() -> list[dict[str, object]]:
    return db_rows(
        """
        SELECT
            month_start_date,
            year,
            month,
            source_system,
            total_revenue,
            total_orders,
            average_order_value,
            revenue_growth_pct
        FROM marts.sales_overview
        ORDER BY month_start_date DESC, source_system
        LIMIT 16
        """
    )


def render_monthly_bars(rows: list[dict[str, object]]) -> str:
    chart_rows = list(reversed(rows[-12:]))
    max_revenue = max((as_float(row["total_revenue"]) for row in chart_rows), default=1.0)
    bars = []
    for row in chart_rows:
        width = max(2, as_float(row["total_revenue"]) / max_revenue * 100)
        label = f"{row['year']}-{int(row['month']):02d}"
        color_class = "alt" if row["source_system"] == "online_retail" else ""
        bars.append(
            f"""<div class="bar-row"><span>{esc(label)}</span><div class="track"><div class="fill {color_class}" style="width:{width:.1f}%"></div></div><strong>{money(row["total_revenue"])}</strong></div>"""
        )
    return "\n".join(bars)


def render_sales_page() -> str:
    summary = dashboard_summary()
    rows = monthly_sales_rows()
    table_rows = "\n".join(
        f"""<tr><td>{esc(row["month_start_date"])}</td><td>{esc(row["source_system"])}</td><td class="num">{money(row["total_revenue"])}</td><td class="num">{number(row["total_orders"])}</td><td class="num">{money(row["average_order_value"])}</td><td class="num">{pct(row["revenue_growth_pct"])}</td></tr>"""
        for row in rows
    )
    content = f"""
<section class="hero">
  <div>
    <h1>Sales Overview</h1>
    <p>Monthly revenue, order volume, and growth from the live marts schema.</p>
  </div>
  <div class="actions"><a class="button secondary" href="/sales-overview?format=json">JSON</a><a class="button" href="/">Dashboard</a></div>
</section>
{render_kpis(summary)}
<section class="section grid two">
  <div class="card">
    <h2>Recent monthly revenue</h2>
    <div class="bars">{render_monthly_bars(rows)}</div>
  </div>
  <div class="card">
    <h2>Model status</h2>
    <p>Warehouse and marts are live. FastAPI can take over once the Python dependency install finishes successfully.</p>
    <table>
      <tr><th>Layer</th><th>Status</th></tr>
      <tr><td>Raw</td><td><span class="pill">loaded</span></td></tr>
      <tr><td>Warehouse</td><td><span class="pill">812,977 fact rows</span></td></tr>
      <tr><td>Marts</td><td><span class="pill">ready</span></td></tr>
    </table>
  </div>
</section>
<section class="section card">
  <h2>Latest monthly rows</h2>
  <table>
    <tr><th>Month</th><th>Source</th><th class="num">Revenue</th><th class="num">Orders</th><th class="num">AOV</th><th class="num">Growth</th></tr>
    {table_rows}
  </table>
</section>"""
    return layout("Sales Overview", "sales", content)


def product_rows(limit: int) -> list[dict[str, object]]:
    return db_rows(
        """
        SELECT
            product_name,
            source_system,
            sales_rows,
            quantity_sold,
            total_revenue,
            revenue_rank,
            performance_band
        FROM marts.product_performance
        ORDER BY total_revenue DESC, product_name
        LIMIT %(limit)s
        """,
        {"limit": limit},
    )


def render_products_page(limit: int) -> str:
    rows = product_rows(limit)
    max_revenue = max((as_float(row["total_revenue"]) for row in rows), default=1.0)
    bar_rows = []
    table_rows = []
    for row in rows:
        width = max(2, as_float(row["total_revenue"]) / max_revenue * 100)
        bar_rows.append(
            f"""<div class="bar-row"><span>{esc(row["product_name"])}</span><div class="track"><div class="fill warn" style="width:{width:.1f}%"></div></div><strong>{money(row["total_revenue"])}</strong></div>"""
        )
        table_rows.append(
            f"""<tr><td>{esc(row["product_name"])}</td><td>{esc(row["source_system"])}</td><td class="num">{number(row["sales_rows"])}</td><td class="num">{money(row["total_revenue"])}</td><td>{esc(row["performance_band"])}</td></tr>"""
        )
    content = f"""
<section class="hero">
  <div><h1>Product Performance</h1><p>Top products and Walmart departments ranked by revenue.</p></div>
  <div class="actions"><a class="button secondary" href="/top-products?limit={limit}&format=json">JSON</a><a class="button" href="/sales-overview">Sales</a></div>
</section>
<section class="section grid two">
  <div class="card"><h2>Revenue leaders</h2><div class="bars">{''.join(bar_rows[:10])}</div></div>
  <div class="card"><h2>Portfolio signal</h2><p>This view proves the marts layer can serve business-facing ranking analysis without report-side SQL.</p></div>
</section>
<section class="section card">
  <h2>Ranked table</h2>
  <table><tr><th>Product</th><th>Source</th><th class="num">Rows</th><th class="num">Revenue</th><th>Band</th></tr>{''.join(table_rows)}</table>
</section>"""
    return layout("Product Performance", "products", content)


def store_rows(limit: int) -> list[dict[str, object]]:
    return db_rows(
        """
        SELECT
            store_id,
            store_name,
            store_type,
            store_size,
            source_system,
            sales_rows,
            total_revenue,
            holiday_revenue,
            non_holiday_revenue,
            sales_per_store_size,
            store_revenue_rank
        FROM marts.store_performance
        ORDER BY total_revenue DESC, store_name
        LIMIT %(limit)s
        """,
        {"limit": limit},
    )


def render_stores_page(limit: int) -> str:
    rows = store_rows(limit)
    max_revenue = max((as_float(row["total_revenue"]) for row in rows), default=1.0)
    bar_rows = []
    table_rows = []
    for row in rows:
        width = max(2, as_float(row["total_revenue"]) / max_revenue * 100)
        bar_rows.append(
            f"""<div class="bar-row"><span>{esc(row["store_name"])}</span><div class="track"><div class="fill" style="width:{width:.1f}%"></div></div><strong>{money(row["total_revenue"])}</strong></div>"""
        )
        table_rows.append(
            f"""<tr><td>{esc(row["store_name"])}</td><td>{esc(row["store_type"])}</td><td class="num">{number(row["store_size"])}</td><td class="num">{money(row["total_revenue"])}</td><td class="num">{money(row["holiday_revenue"])}</td><td class="num">{as_float(row["sales_per_store_size"]):,.2f}</td></tr>"""
        )
    content = f"""
<section class="hero">
  <div><h1>Store Performance</h1><p>Walmart store ranking, holiday revenue, and productivity by store size.</p></div>
  <div class="actions"><a class="button secondary" href="/store-performance?limit={limit}&format=json">JSON</a><a class="button" href="/top-products?limit=15">Products</a></div>
</section>
<section class="section grid two">
  <div class="card"><h2>Store revenue ranking</h2><div class="bars">{''.join(bar_rows[:12])}</div></div>
  <div class="card"><h2>Operational lens</h2><p>Store size and holiday revenue are modeled in marts so Power BI can focus on decisions instead of joins.</p></div>
</section>
<section class="section card">
  <h2>Store detail</h2>
  <table><tr><th>Store</th><th>Type</th><th class="num">Size</th><th class="num">Revenue</th><th class="num">Holiday</th><th class="num">Revenue / size</th></tr>{''.join(table_rows)}</table>
</section>"""
    return layout("Store Performance", "stores", content)


def render_home() -> str:
    counts = db_rows(
        """
        SELECT 'warehouse.fact_sales' AS object_name, COUNT(*) AS row_count
        FROM warehouse.fact_sales
        UNION ALL
        SELECT 'marts.forecasting_base', COUNT(*)
        FROM marts.forecasting_base
        UNION ALL
        SELECT 'marts.sales_overview', COUNT(*)
        FROM marts.sales_overview
        ORDER BY object_name
        """
    )
    summary = dashboard_summary()
    rows_html = "\n".join(
        f"<tr><td>{esc(row['object_name'])}</td><td class=\"num\">{int(row['row_count']):,}</td></tr>"
        for row in counts
    )
    content = f"""
<section class="hero">
  <div>
    <h1>Retail Intelligence Platform</h1>
    <p>Live PostgreSQL dashboard preview for the completed analytics project.</p>
  </div>
  <div class="actions"><a class="button" href="/sales-overview">Open sales dashboard</a><a class="button secondary" href="/top-products?limit=15">Products</a></div>
</section>
{render_kpis(summary)}
<section class="section grid two">
  <div class="card">
    <h2>Verified database objects</h2>
    <table><tr><th>Object</th><th class="num">Rows</th></tr>{rows_html}</table>
  </div>
  <div class="card">
    <h2>Project layers</h2>
    <table>
      <tr><th>Layer</th><th>Status</th></tr>
      <tr><td>Raw ETL</td><td><span class="pill">verified</span></td></tr>
      <tr><td>Warehouse</td><td><span class="pill">star schema</span></td></tr>
      <tr><td>Marts</td><td><span class="pill">dashboard-ready</span></td></tr>
      <tr><td>API</td><td><span class="pill">preview running</span></td></tr>
    </table>
  </div>
</section>"""
    return layout("Retail Intelligence Platform", "overview", content)


class PreviewHandler(BaseHTTPRequestHandler):
    def wants_json(self, parsed_query: dict[str, list[str]]) -> bool:
        if parsed_query.get("format", [""])[0].lower() == "json":
            return True
        accept = self.headers.get("Accept", "")
        return "application/json" in accept and "text/html" not in accept

    def send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, default=convert_json, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, payload: str, status: int = 200) -> None:
        body = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path in {"/", "/index.html"}:
                self.send_html(render_home())
                return

            if parsed.path == "/health":
                row = db_rows("SELECT current_database() AS database_name")[0]
                payload = {"status": "ok", "database": row["database_name"]}
                if self.wants_json(query):
                    self.send_json(payload)
                    return
                content = f"""<section class="hero"><div><h1>System Health</h1><p>Database connection is live.</p></div><div class="actions"><a class="button" href="/">Dashboard</a></div></section><section class="section card"><table><tr><th>Status</th><th>Database</th></tr><tr><td><span class="pill">{esc(payload["status"])}</span></td><td>{esc(payload["database"])}</td></tr></table></section>"""
                self.send_html(layout("System Health", "health", content))
                return

            if parsed.path == "/sales-overview":
                payload = dashboard_summary()
                if self.wants_json(query):
                    self.send_json(payload)
                    return
                self.send_html(render_sales_page())
                return

            if parsed.path == "/top-products":
                limit = int(query.get("limit", ["15"])[0])
                limit = max(1, min(limit, 50))
                if self.wants_json(query):
                    self.send_json(product_rows(limit))
                    return
                self.send_html(render_products_page(limit))
                return

            if parsed.path == "/store-performance":
                limit = int(query.get("limit", ["20"])[0])
                limit = max(1, min(limit, 100))
                if self.wants_json(query):
                    self.send_json(store_rows(limit))
                    return
                self.send_html(render_stores_page(limit))
                return

            self.send_json({"detail": "Not found"}, status=404)
        except Exception as exc:
            self.send_json({"status": "error", "detail": str(exc)}, status=500)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), PreviewHandler)
    print(f"Preview server running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
