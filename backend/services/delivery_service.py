"""
delivery_service.py
Sends the NEXUS morning digest to Slack and/or email.
Both channels are optional — missing config silently skips that channel.
Never raises — all errors are caught and logged.
"""
import httpx
import smtplib
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from backend.config import get_settings

settings = get_settings()


async def deliver_digest(project_id: str, digest_text: str, project_name: str = "Your Project") -> dict:
    """
    Deliver the morning digest to all configured channels.
    Returns a dict showing which channels succeeded.
    """
    results = {
        "slack": False,
        "email": False,
        "in_app": True     # Always true — this is handled by WebSocket separately
    }

    # Run both deliveries concurrently
    tasks = []
    if settings.slack_webhook_url:
        tasks.append(_send_slack(digest_text, project_name))
    if settings.smtp_user and settings.digest_email_to:
        tasks.append(_send_email(digest_text, project_name))

    if tasks:
        outcomes = await asyncio.gather(*tasks, return_exceptions=True)
        if settings.slack_webhook_url:
            results["slack"] = outcomes[0] is True
        if settings.smtp_user and settings.digest_email_to:
            idx = 1 if settings.slack_webhook_url else 0
            results["email"] = outcomes[idx] is True

    delivered = [k for k, v in results.items() if v]
    print(f"[Digest] Delivered via: {', '.join(delivered)}")
    return results


async def _send_slack(digest_text: str, project_name: str) -> bool:
    """
    Send digest to Slack via incoming webhook.
    Format: clean Slack markdown with sections.
    """
    try:
        # Format digest for Slack — use Slack's block kit for clean rendering
        today = datetime.now().strftime("%A, %B %d")
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"NEXUS Morning Brief — {today}"
                }
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"*Project:* {project_name}  |  Powered by Hindsight Memory"}]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": digest_text}
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"<http://localhost:5173/agent|Open NEXUS> to ask follow-up questions  |  <http://localhost:5173/report|View full report>"
                }]
            }
        ]

        payload = {
            "blocks": blocks,
            "text": f"NEXUS Morning Brief — {today}"   # fallback for notifications
        }

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                settings.slack_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if r.status_code == 200 and r.text == "ok":
                print(f"[Digest] Slack: delivered to webhook")
                return True
            else:
                print(f"[Digest] Slack: failed — {r.status_code} {r.text}")
                return False

    except Exception as e:
        print(f"[Digest] Slack error: {e}")
        return False


async def _send_email(digest_text: str, project_name: str) -> bool:
    """
    Send digest via SMTP. Works with Gmail App Passwords, SendGrid, etc.
    Sends both plain text and HTML versions.
    """
    try:
        recipients = [e.strip() for e in settings.digest_email_to.split(",") if e.strip()]
        if not recipients:
            return False

        today = datetime.now().strftime("%A, %B %d, %Y")
        subject = f"NEXUS Morning Brief — {project_name} — {today}"

        # Build HTML email
        html_body = _build_email_html(digest_text, project_name, today)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.digest_email_from
        msg["To"] = ", ".join(recipients)

        # Plain text fallback
        plain = MIMEText(
            f"NEXUS Morning Brief — {today}\nProject: {project_name}\n\n{digest_text}\n\n"
            f"Open NEXUS: http://localhost:5173/agent",
            "plain"
        )
        html = MIMEText(html_body, "html")

        msg.attach(plain)
        msg.attach(html)   # HTML is preferred when supported

        # Send via SMTP (run in thread to avoid blocking async loop)
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _smtp_send(msg, recipients)
        )
        print(f"[Digest] Email: delivered to {len(recipients)} recipients")
        return True

    except Exception as e:
        print(f"[Digest] Email error: {e}")
        return False


def _smtp_send(msg, recipients):
    """Synchronous SMTP send — called via executor."""
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.digest_email_from, recipients, msg.as_string())


def _build_email_html(digest_text: str, project_name: str, today: str) -> str:
    """
    Build a clean HTML email template for the morning digest.
    Works in Gmail, Outlook, Apple Mail.
    """
    # Convert digest line breaks to paragraphs
    paragraphs = "".join(
        f"<p style='margin:0 0 12px 0;line-height:1.6'>{p.strip()}</p>"
        for p in digest_text.split("\n\n") if p.strip()
    )

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#F8FAFC;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif">
  <div style="max-width:600px;margin:24px auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1)">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1A3A6B,#2563EB);padding:28px 32px">
      <div style="color:#93C5FD;font-size:13px;font-weight:600;margin-bottom:6px;letter-spacing:0.05em">
        NEXUS AI PROJECT MANAGER
      </div>
      <h1 style="color:#ffffff;font-size:22px;margin:0 0 4px 0;font-weight:700">
        Morning Brief
      </h1>
      <div style="color:#BFDBFE;font-size:14px">{today} &nbsp;|&nbsp; {project_name}</div>
    </div>

    <!-- Digest content -->
    <div style="padding:28px 32px;color:#1E293B;font-size:15px">
      {paragraphs}
    </div>

    <!-- CTA buttons -->
    <div style="padding:0 32px 24px;display:flex;gap:12px">
      <a href="http://localhost:5173/agent"
         style="display:inline-block;background:#2563EB;color:#ffffff;text-decoration:none;
                padding:10px 20px;border-radius:6px;font-size:14px;font-weight:600">
        Talk to NEXUS
      </a>
      <a href="http://localhost:5173/report"
         style="display:inline-block;background:#F1F5F9;color:#1E293B;text-decoration:none;
                padding:10px 20px;border-radius:6px;font-size:14px;font-weight:600">
        View Full Report
      </a>
    </div>

    <!-- Footer -->
    <div style="background:#F8FAFC;padding:16px 32px;border-top:1px solid #E2E8F0">
      <p style="margin:0;font-size:12px;color:#94A3B8;line-height:1.5">
        Sent by NEXUS &nbsp;|&nbsp; Powered by Hindsight Memory (Vectorize) &nbsp;|&nbsp;
        <a href="http://localhost:5173" style="color:#2563EB;text-decoration:none">Open Dashboard</a>
      </p>
    </div>

  </div>
</body>
</html>"""
