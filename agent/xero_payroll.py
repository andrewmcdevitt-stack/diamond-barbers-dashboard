"""
xero_payroll.py
---------------
Fetches the most recent posted payroll from all Xero organisations and:
  1. Saves summary to data/xero_payroll.json  (for the dashboard)
  2. Generates a PDF report
  3. Emails the PDF to admin@diamondbarbers.com.au

Run with:  python agent/xero_payroll.py
Requires:  data/xero_token.json  (created by python agent/xero_auth.py)
"""

import asyncio
import base64
import json
import os
import re
import smtplib
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from email import encoders as email_encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

DATA_DIR     = Path(__file__).parent.parent / "data"
TOKEN_FILE   = DATA_DIR / "xero_token.json"
OUTPUT_JSON  = DATA_DIR / "xero_payroll.json"

CLIENT_ID    = os.environ["XERO_CLIENT_ID"]
CLIENT_SECRET = os.environ["XERO_CLIENT_SECRET"]
EMAIL_HOST   = os.environ.get("EMAIL_HOST", "mail.diamondbarbers.com.au")
EMAIL_FROM   = "claude@diamondbarbers.com.au"
EMAIL_TO     = "admin@diamondbarbers.com.au"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

# Short display names for each Xero org
ORG_SHORT_NAMES = {
    "Diamond Barbers Pty Ltd":        "Darwin CBD",
    "D.B. Parap Pty Ltd":             "Parap",
    "DB WULGURU PTY LTD":             "Wulguru",
    "DIAMOND BARBERS CAIRNS PTY LTD": "Cairns",
}

# Display order for the report
ORG_ORDER = ["Darwin CBD", "Parap", "Wulguru", "Cairns"]


# ── Token management ──────────────────────────────────────────────────────────

def load_token():
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            f"Token file not found: {TOKEN_FILE}\n"
            "Run:  python agent/xero_auth.py"
        )
    return json.loads(TOKEN_FILE.read_text())


def refresh_token(token_data):
    """Exchange refresh token for a new access token and save it."""
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "refresh_token": token_data["refresh_token"],
    }).encode()
    req = urllib.request.Request(
        "https://identity.xero.com/connect/token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req) as resp:
        new_token = json.loads(resp.read())

    # Preserve the tenant list
    new_token["tenants"] = token_data.get("tenants", [])
    TOKEN_FILE.write_text(json.dumps(new_token, indent=2))
    print("  Token refreshed and saved.")
    return new_token


def get_valid_token():
    token = load_token()
    token = refresh_token(token)   # Always refresh — access tokens expire after 30 min
    return token


# ── Xero API helper ───────────────────────────────────────────────────────────

def xero_get(path, tenant_id, access_token):
    req = urllib.request.Request(
        f"https://api.xero.com{path}",
        headers={
            "Authorization":  f"Bearer {access_token}",
            "Xero-Tenant-Id": tenant_id,
            "Accept":         "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# ── Date helpers ──────────────────────────────────────────────────────────────

def parse_xero_date(date_str):
    """Parse Xero /Date(ms)/ format or ISO date string → date object."""
    if not date_str:
        return None
    m = re.match(r"/Date\((\d+)", str(date_str))
    if m:
        ms = int(m.group(1))
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date()
    try:
        return datetime.fromisoformat(str(date_str)[:10]).date()
    except Exception:
        return None


def fmt_period(start_date, end_date):
    """Format '8 Jan – 14 Jan 2024' from two date objects."""
    if not start_date or not end_date:
        return ""
    return f"{start_date.day} {start_date.strftime('%b')} – {end_date.day} {end_date.strftime('%b %Y')}"


# ── Payroll fetching ──────────────────────────────────────────────────────────

def fetch_org_payroll(tenant_id, tenant_name, access_token):
    """Fetch the most recent posted payroll run for one organisation."""
    short_name = ORG_SHORT_NAMES.get(tenant_name, tenant_name)
    print(f"  Fetching payroll for: {tenant_name} ({short_name})")

    try:
        data = xero_get("/payroll.xro/1.0/PayRuns", tenant_id, access_token)
    except Exception as e:
        print(f"    ERROR fetching PayRuns: {e}")
        return None

    pay_runs = data.get("PayRuns", [])
    if not pay_runs:
        print(f"    No pay runs found.")
        return None

    # Prefer POSTED runs; fall back to any
    posted = [r for r in pay_runs if r.get("PayRunStatus") == "POSTED"] or pay_runs

    def run_sort_key(r):
        d = parse_xero_date(r.get("PaymentDate") or r.get("PayRunPeriodEndDate", ""))
        from datetime import date
        return d or date.min

    posted.sort(key=run_sort_key, reverse=True)
    latest     = posted[0]
    pay_run_id = latest.get("PayRunID")

    # Fetch PayRun detail to get dates and payslip stubs (names, net, tax)
    try:
        detail = xero_get(f"/payroll.xro/1.0/PayRuns/{pay_run_id}", tenant_id, access_token)
        run    = detail.get("PayRuns", [{}])[0]
    except Exception as e:
        print(f"    ERROR fetching PayRun detail: {e}")
        run = latest

    payslip_stubs = run.get("Payslips", [])
    start_date    = parse_xero_date(run.get("PayRunPeriodStartDate", ""))
    end_date      = parse_xero_date(run.get("PayRunPeriodEndDate", ""))
    payment_date  = parse_xero_date(run.get("PaymentDate", ""))

    print(f"    Period: {start_date} – {end_date}  |  Payslips: {len(payslip_stubs)}")

    # PayRun-level aggregates (the most reliable source)
    # Xero exposes Tax and NetPay at the run level; GrossWages is not available
    run_net = float(run.get("NetPay", 0) or 0)
    run_tax = float(run.get("Tax", 0) or 0)
    # Derive gross: in most cases Gross = Net + PAYG Tax (no salary sacrifice assumed)
    run_gross = round(run_net + run_tax, 2)

    # Per-employee net pay from payslip stubs (name + NetPay is reliable)
    employees = []
    for stub in payslip_stubs:
        first = stub.get("FirstName", "")
        last  = stub.get("LastName", "")
        name  = f"{first} {last}".strip() or "Unknown"
        net   = float(stub.get("NetPay", 0) or 0)
        employees.append({"name": name, "net_pay": round(net, 2)})

    employees.sort(key=lambda e: e["name"])

    gross_total = run_gross
    tax_total   = round(run_tax, 2)
    net_total   = round(run_net, 2)
    # Super = 11.5% of gross wages (FY2025-26 Super Guarantee rate)
    super_total = round(run_gross * 0.115, 2)

    print(f"    Gross: ${gross_total:,.2f}  |  Net: ${net_total:,.2f}  |  Tax: ${tax_total:,.2f}  |  Super (est): ${super_total:,.2f}")

    return {
        "org":              tenant_name,
        "short_name":       short_name,
        "pay_period_start": str(start_date)   if start_date   else "",
        "pay_period_end":   str(end_date)     if end_date     else "",
        "payment_date":     str(payment_date) if payment_date else "",
        "gross_wages":      gross_total,
        "tax":              tax_total,
        "net_pay":          net_total,
        "super":            super_total,
        "employee_count":   len(employees),
        "employees":        employees,
    }


# ── HTML report builder ───────────────────────────────────────────────────────

def build_report_html(locations, generated_at, period_str):
    total_gross = sum(l["gross_wages"]    for l in locations)
    total_tax   = sum(l["tax"]            for l in locations)
    total_net   = sum(l["net_pay"]        for l in locations)
    total_super = sum(l["super"]          for l in locations)
    total_emp   = sum(l["employee_count"] for l in locations)

    rows = ""
    for loc in locations:
        rows += f"""
        <tr>
            <td>{loc['short_name']}</td>
            <td class="num">{loc['employee_count']}</td>
            <td class="num">${loc['gross_wages']:,.2f}</td>
            <td class="num">${loc['tax']:,.2f}</td>
            <td class="num">${loc['net_pay']:,.2f}</td>
            <td class="num">${loc['super']:,.2f}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 11px; padding: 20px; color: #1a1a1a; }}
  h1   {{ font-size: 16px; margin: 0 0 4px; }}
  .sub {{ font-size: 12px; color: #555; margin-bottom: 18px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th   {{ background: #1a1a1a; color: #fff; padding: 6px 10px; text-align: left;
           font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; }}
  th.num, td.num {{ text-align: right; }}
  td   {{ padding: 5px 10px; border-bottom: 1px solid #e0e0e0; }}
  tr:nth-child(even) td {{ background: #f9f9f9; }}
  .total td {{ font-weight: bold; background: #f0f0f0; border-top: 2px solid #333; }}
  .foot {{ margin-top: 14px; font-size: 9px; color: #888; text-align: right; }}
</style>
</head>
<body>
  <h1>Diamond Barbers — Weekly Payroll Summary</h1>
  <div class="sub">Pay period: {period_str}</div>
  <table>
    <thead>
      <tr>
        <th>Location</th>
        <th class="num">Employees</th>
        <th class="num">Gross Wages</th>
        <th class="num">PAYG Tax</th>
        <th class="num">Net Pay</th>
        <th class="num">Super</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr class="total">
        <td>TOTAL</td>
        <td class="num">{total_emp}</td>
        <td class="num">${total_gross:,.2f}</td>
        <td class="num">${total_tax:,.2f}</td>
        <td class="num">${total_net:,.2f}</td>
        <td class="num">${total_super:,.2f}</td>
      </tr>
    </tbody>
  </table>
  <div class="foot">Generated {generated_at} · Diamond Barbers Payroll</div>
</body>
</html>"""


# ── PDF generation ────────────────────────────────────────────────────────────

async def generate_pdf(html_content, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page    = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        await page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"},
        )
        await browser.close()
    print(f"  PDF saved: {output_path.name}")


# ── Email ─────────────────────────────────────────────────────────────────────

def send_email(pdf_path, subject):
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO

    msg.attach(MIMEText(
        f"Please find attached the weekly payroll summary.\n\nDiamond Barbers",
        "plain"
    ))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    email_encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{pdf_path.name}"')
    msg.attach(part)

    with smtplib.SMTP(EMAIL_HOST, 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    print(f"  Email sent to {EMAIL_TO}")


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print("Loading Xero token...")
    token        = get_valid_token()
    access_token = token["access_token"]
    tenants      = token.get("tenants", [])

    if not tenants:
        print("ERROR: No tenants in token file. Run:  python agent/xero_auth.py")
        return

    print(f"Found {len(tenants)} organisations.\n")

    # Fetch payroll for all orgs
    locations = []
    for tenant in tenants:
        result = fetch_org_payroll(tenant["id"], tenant["name"], access_token)
        if result:
            locations.append(result)

    if not locations:
        print("No payroll data returned from any organisation.")
        return

    # Sort into display order
    def sort_key(loc):
        try:
            return ORG_ORDER.index(loc["short_name"])
        except ValueError:
            return 99

    locations.sort(key=sort_key)

    # Build period string from first location
    period_str = ""
    try:
        start = datetime.fromisoformat(locations[0]["pay_period_start"])
        end   = datetime.fromisoformat(locations[0]["pay_period_end"])
        period_str = fmt_period(start.date(), end.date())
    except Exception:
        period_str = locations[0].get("pay_period_end", "")

    darwin_tz    = timezone(timedelta(hours=9, minutes=30))
    generated_at = datetime.now(darwin_tz).strftime("%d %b %Y %H:%M")

    totals = {
        "gross_wages":    round(sum(l["gross_wages"]    for l in locations), 2),
        "tax":            round(sum(l["tax"]            for l in locations), 2),
        "net_pay":        round(sum(l["net_pay"]        for l in locations), 2),
        "super":          round(sum(l["super"]          for l in locations), 2),
        "employee_count": sum(l["employee_count"]       for l in locations),
    }

    # 1 — Save JSON for dashboard
    DATA_DIR.mkdir(exist_ok=True)
    output = {
        "generated_at": generated_at,
        "pay_period":   period_str,
        "locations":    locations,
        "totals":       totals,
    }
    OUTPUT_JSON.write_text(json.dumps(output, indent=2))
    print(f"\nSaved {OUTPUT_JSON.name}")

    # 2 — Generate PDF
    html     = build_report_html(locations, generated_at, period_str)
    end_slug = locations[0]["pay_period_end"].replace("-", "") if locations else "report"
    pdf_path = DATA_DIR / f"payroll_{end_slug}.pdf"
    await generate_pdf(html, pdf_path)

    # 3 — Email
    subject = f"Weekly Payroll Summary — {period_str}"
    send_email(pdf_path, subject)

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
