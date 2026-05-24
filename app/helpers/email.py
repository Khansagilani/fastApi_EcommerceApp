import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

EMAIL_HOST     = os.getenv("EMAIL_HOST", "")
EMAIL_PORT     = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM     = os.getenv("EMAIL_FROM", EMAIL_USERNAME)
EMAIL_ENABLED  = bool(EMAIL_HOST and EMAIL_USERNAME and EMAIL_PASSWORD)


def send_email(to: str, subject: str, html_body: str) -> bool:
    if not EMAIL_ENABLED or not to:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Kairos <{EMAIL_FROM}>"
        msg["To"]      = to
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to, msg.as_string())
        return True
    except Exception:
        return False


def order_confirmation_email(to: str, order_id: int, total: float, items: list) -> None:
    rows = "".join(
        f"<tr><td style='padding:8px 12px;border-bottom:1px solid #f0e8e4'>{i['product_name']}"
        f"{' — ' + i['size'] if i.get('size') else ''}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #f0e8e4;text-align:center'>{i['quantity']}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #f0e8e4;text-align:right'>PKR {i['subtotal']:,.0f}</td></tr>"
        for i in items
    )
    html = f"""
    <div style="font-family:Georgia,serif;max-width:560px;margin:0 auto;background:#faf7f4;padding:40px 20px">
      <h1 style="font-size:28px;color:#c0516f;font-style:italic;text-align:center;margin-bottom:4px">Kairos</h1>
      <p style="text-align:center;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#7e6d68;margin-bottom:32px">Order Confirmation</p>
      <div style="background:white;border:1px solid #e0cfc8;padding:32px">
        <h2 style="font-size:18px;font-weight:400;color:#2a1e1e;margin-bottom:6px">Thank you for your order!</h2>
        <p style="font-size:13px;color:#7e6d68;margin-bottom:24px">Order <strong>#{ order_id }</strong> has been placed and is being processed.</p>
        <table style="width:100%;border-collapse:collapse;font-size:13px">
          <thead><tr style="background:#1c1414;color:rgba(255,255,255,.6)">
            <th style="padding:10px 12px;text-align:left;font-size:9px;letter-spacing:1.5px;text-transform:uppercase">Item</th>
            <th style="padding:10px 12px;text-align:center;font-size:9px;letter-spacing:1.5px;text-transform:uppercase">Qty</th>
            <th style="padding:10px 12px;text-align:right;font-size:9px;letter-spacing:1.5px;text-transform:uppercase">Price</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
        <div style="text-align:right;margin-top:16px;padding-top:12px;border-top:2px solid #c0516f">
          <strong style="font-size:16px;color:#c0516f">Total: PKR {total:,.0f}</strong>
        </div>
      </div>
      <p style="text-align:center;font-size:11px;color:#b5a59e;margin-top:24px">We'll be in touch shortly to confirm your order. For queries, WhatsApp us.</p>
    </div>"""
    send_email(to, f"Order #{order_id} Confirmed — Kairos", html)


def order_status_email(to: str, order_id: int, new_status: str) -> None:
    status_msg = {
        "paid":      "Your payment has been confirmed.",
        "shipped":   "Your order is on its way!",
        "delivered": "Your order has been delivered. We hope you love it!",
        "cancelled": "Your order has been cancelled.",
    }.get(new_status, f"Your order status has been updated to: {new_status}.")

    html = f"""
    <div style="font-family:Georgia,serif;max-width:560px;margin:0 auto;background:#faf7f4;padding:40px 20px">
      <h1 style="font-size:28px;color:#c0516f;font-style:italic;text-align:center;margin-bottom:4px">Kairos</h1>
      <p style="text-align:center;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#7e6d68;margin-bottom:32px">Order Update</p>
      <div style="background:white;border:1px solid #e0cfc8;padding:32px;text-align:center">
        <h2 style="font-size:18px;font-weight:400;color:#2a1e1e;margin-bottom:12px">Order #{order_id} — {new_status.upper()}</h2>
        <p style="font-size:14px;color:#2a1e1e">{status_msg}</p>
      </div>
    </div>"""
    send_email(to, f"Order #{order_id} Update — Kairos", html)
