# Copyright (c) 2025, M&M devs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
import os
import base64


class EventRegistration(Document):
    pass


def kes(amount):
    return f"KES {amount:,.2f}"


def after_insert(doc, method):
    """Send confirmation email after registration is created with attached PDF summary."""
    if not doc.email:
        return

    # Encode logo to Base64 (replace path with your uploaded logo's path in your app)
    logo_path = os.path.join(frappe.get_site_path(), "public", "files", "IMG_1347.PNG")
    with open(logo_path, "rb") as logo_file:
        logo_base64 = base64.b64encode(logo_file.read()).decode()

    # ----------------------------
    # Payment Calculation
    # ----------------------------
    applicant_fee = 35000
    booth_fee = 50000
    attendee_fee = 35000

    total_amount = (
        applicant_fee +
        (doc.booth_count or 0) * booth_fee +
        len(doc.attendees or []) * attendee_fee
    )

    # ----------------------------
    # Build Attendees List for PDF
    # ----------------------------
    attendees_html = ""
    if getattr(doc, "attendees", []):
        attendees_html = "<ul>"
        for attendee in doc.attendees:
            attendees_html += f"<li><b>{attendee.full_name}</b> — {attendee.email}, {attendee.attendee_phone_number or 'N/A'}, {attendee.attendee_organization or 'N/A'}</li>"
        attendees_html += "</ul>"
    else:
        attendees_html = "<p>No attendees added</p>"

    # ----------------------------
    # PDF HTML Content
    # ----------------------------
    pdf_html = f"""
    <html>
    <head>
        <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 12pt;
                    color: #333;
                    margin: 40px;
                }}
                h1, h2, h3 {{
                    color: #003366;
                }}
                .logo {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}
                th, td {{
                    border: 1px solid #ccc;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f0f0f0;
                }}
                .section-title {{
                    color: #2e7d32;
                    font-weight: bold;
                    margin-top: 20px;
                }}
                #bank-payment {{
                    background-color: rgb(203,201,159);
                }}
                #bank-payment-instructions {{
                    background-color: rgb(236,236,221);
                }}
        </style>
    </head>
    <body>
        <div class="logo">
            <img src="data:image/png;base64,{logo_base64}" width="150" />
        </div>
        
        <h3>Due Payment</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Description</th>
                <th>Amount (KES)</th>
            </tr>
            <tr>
                <td>Applicant Fee</td>
                <td>{kes(applicant_fee)}</td>
            </tr>
            <tr>
                <td>Booth Fee ({doc.booth_count or 0} x {kes(booth_fee)})</td>
                <td>{kes((doc.booth_count or 0) * booth_fee)}</td>
            </tr>
            <tr>
                <td>Attendee Fee ({len(doc.attendees or [])} x {kes(attendee_fee)})</td>
                <td>{kes(len(doc.attendees or []) * attendee_fee)}</td>
            </tr>
            <tr>
                <th>Total</th>
                <th>{kes(total_amount)}</th>
            </tr>
        </table>
        <h3>Payment Details</h3>
        <h4><u>Terms of Payment</u></h4>
        <ul>
            <li> Should be paid <b><u>within 7 days on the date on this invoice.</u></b></li>
            <li>All transfer fees are to be paid by the client.</li>
            <li>Regarding VAT, the supplied services are subject to reverse charge in the country of receipt.</li>
            <li> When paying by bank transfer, please state your <b><u>organization name.</u></b></li>
        </ul>
        <table>
            <tr id="bank-payment">
                <td>
                    <h4>Bank Payment Instructions:</h4>
                    <p>Payment can be made in either</p>
                    <p>cash, cash transfer or even cheque to either of accounts below:</p>
                </td>
                <td></td>
            </tr>
            <tr id="bank-payment-instructions">
                <td>
                    <p>
                        <b><u>Payment in KES:</u></b><br>
                        <b>Account Name:</b> Quercus Group Ltd.<br>
                        <b>Account No:</b> 7494880018<br>
                        <b>Bank:</b> NCBA<br>
                        <b>Bank Address:</b> 30437-00100<br>
                        <b>Branch code:</b> 07000<br>
                        <b>SWIFT Code:</b> CBAFKENX<br>
                    </p>
                </td>
                <td>
                    <p>
                        <b><u>Payment in Euros:</u></b><br>
                        <b>Account Name:</b> Quercus Group Ltd.<br>
                        <b>Account No:</b> 7494880023<br>
                        <b>Bank:</b> NCBA<br>
                        <b>Bank Address:</b> 30437-00100<br>
                        <b>Branch code:</b> 07000<br>
                        <b>SWIFT Code:</b> CBAFKENX<br>
                    </p>
                </td>
            </tr>
        </table>
       <div style="text-align: justify;">
            <p>
                Yours faithfully,
                <br>Co – organizing team,
                <br>Innovate for WASH Forum – Malindi
                <br>+254723341220
            </p>
            <p>
                Quercus Group Ltd | Pin: P051526263L | C/O Climate Innovation Center, Ole Sangale Road, Madaraka Estate <br>
                Box 59857 - 00200 Nairobi, Kenya | www.quercus-group.com | info@quercus-group.com
            </p>
        </div>
    </body>
    </html>

    """

    # Generate PDF from HTML
    pdf_content = get_pdf(pdf_html)

    # ----------------------------
    # Email Message
    # ----------------------------
    subject = "Thank You for Registering - Malindi 2025"
    message = f"""
        <p>Dear {doc.full_name},</p>
        <p>Thank you for registering for the Malindi 2025 Event.</p>
        <hr>
        <h2>Registration Summary - Malindi 2025</h2>
        <p><b>Full Name:</b> {doc.full_name}</p>
        <p><b>Email:</b> {doc.email}</p>
        <p><b>Phone Number:</b> {doc.phone_number or 'N/A'}</p>
        <p><b>Organization:</b> {doc.organization or 'N/A'}</p>
        <p><b>Designation:</b> {doc.designation or 'N/A'}</p>
        <p><b>Presentation Ready:</b> {'Yes' if doc.has_presentation else 'No'}</p>
        <p><b>Wants Booth:</b> {'Yes' if doc.wants_booth else 'No'}</p>
        <p><b>Booth Count:</b> {doc.booth_count or 0}</p>
        <p><b>Attendees:</b></p>
        {attendees_html}
        <p>Please Find attached the payment details and payment summary </p>
        <p>Best regards,<br>Malindi 2025 Team</p>
    """

    try:
        frappe.sendmail(
            recipients=[doc.email],
            subject=subject,
            message=message,
            attachments=[{
                "fname": f"Registration_{doc.name}.pdf",
                "fcontent": pdf_content
            }],
            now=True  # send immediately
        )
    except Exception as e:
        frappe.log_error(f"Failed to send registration email: {str(e)}", "Event Registration Email Error")