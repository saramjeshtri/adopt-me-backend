import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM     = os.getenv("MAIL_FROM", "")


def send_surrender_rejection_email(
    to_email: str,
    owner_name: str,
    species: str,
    reason: str,
) -> bool:
    """
    Sends a rejection email to the pet owner when their surrender request is refused.
    Returns True on success, False on failure.
    """
    if not MAIL_USERNAME or not MAIL_PASSWORD or not to_email:
        return False

    subject = "Bashkia Tiranë — Kërkesa juaj për dorëzim kafshë"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff;">

      <!-- Header -->
      <div style="background: #dc2626; padding: 28px 32px; border-radius: 12px 12px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 20px; font-weight: 700;">
          🐾 Më Adopto — Bashkia Tiranë
        </h1>
        <p style="color: rgba(255,255,255,0.8); margin: 6px 0 0; font-size: 13px;">
          Njoftim për kërkesën tuaj
        </p>
      </div>

      <!-- Body -->
      <div style="padding: 32px; background: #f9fafb; border-radius: 0 0 12px 12px;">
        <p style="color: #374151; font-size: 15px; margin: 0 0 16px;">
          I/E nderuar <strong>{owner_name}</strong>,
        </p>
        <p style="color: #374151; font-size: 14px; line-height: 1.6; margin: 0 0 16px;">
          Faleminderit që na kontaktuat lidhur me <strong>{species}</strong>-n tuaj/tuajën.
          Kërkesa juaj për dorëzim u shqyrtua me kujdes nga stafi ynë.
        </p>
        <p style="color: #374151; font-size: 14px; line-height: 1.6; margin: 0 0 20px;">
          Fatkeqësisht, në këtë moment nuk mundemi ta pranojmë kërkesën tuaj.
        </p>

        <!-- Reason box -->
        <div style="background: #fee2e2; border-left: 4px solid #dc2626; border-radius: 8px; padding: 16px 20px; margin: 0 0 24px;">
          <p style="color: #991b1b; font-size: 13px; font-weight: 600; margin: 0 0 6px; text-transform: uppercase; letter-spacing: 0.5px;">
            Arsyeja
          </p>
          <p style="color: #7f1d1d; font-size: 14px; margin: 0; line-height: 1.6;">
            {reason}
          </p>
        </div>

        <p style="color: #6b7280; font-size: 13px; line-height: 1.6; margin: 0 0 24px;">
          Nëse keni pyetje ose dëshironi të diskutoni situatën, mund të na kontaktoni
          drejtpërdrejt në adresën tonë ose të vizitoni faqen tonë.
        </p>

        <!-- CTA -->
        <div style="text-align: center; margin: 24px 0;">
          <a href="http://localhost:5173/kontakt"
             style="background: #dc2626; color: white; padding: 12px 28px; border-radius: 999px;
                    text-decoration: none; font-size: 14px; font-weight: 600; display: inline-block;">
            Na kontaktoni
          </a>
        </div>

        <!-- Footer -->
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;" />
        <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">
          Bashkia Tiranë · Mbrojtja e kafshëve · meadopto@tirana.al
        </p>
      </div>
    </div>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Më Adopto — Bashkia Tiranë <{MAIL_FROM}>"
        msg["To"]      = to_email

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send rejection email: {e}")
        return False