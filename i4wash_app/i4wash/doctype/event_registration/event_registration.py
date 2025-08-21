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


def eur(amount):
    return f"EUR {amount:,.2f}"

def before_insert(doc, method):
    # Assign autonamed invoice number to custom field
    doc.invoice_number = doc.name  

    
def before_save(doc, method):
    # Fees in KES
    applicant_fee_kes = 35000
    booth_fee_kes = 50000
    attendee_fee_kes = 35000

    # Fees in EUR
    applicant_fee_eur = 300
    booth_fee_eur = 460
    attendee_fee_eur = 300

    # Totals in KES
    total_booth_kes = (doc.booth_count or 0) * booth_fee_kes
    total_attendee_kes = len(doc.attendees or []) * attendee_fee_kes
    total_kes = applicant_fee_kes + total_booth_kes + total_attendee_kes

    # Totals in EUR
    total_booth_eur = (doc.booth_count or 0) * booth_fee_eur
    total_attendee_eur = len(doc.attendees or []) * attendee_fee_eur
    total_eur = applicant_fee_eur + total_booth_eur + total_attendee_eur

    # Set values on document
    doc.total_amount_kes = total_kes
    doc.total_amount_eur = total_eur

def after_insert(doc, method):
    doc.invoice_number = doc.name
    """Send confirmation email after registration is created with attached PDF summary."""
    if not doc.email:
        return

    # Encode logo to Base64 (replace path with your uploaded logo's path in your app)
    logo_path = os.path.join(frappe.get_site_path(), "public", "files", "IMG_1347.PNG")
    with open(logo_path, "rb") as logo_file:
        logo_base64 = base64.b64encode(logo_file.read()).decode()

    # ----------------------------
    # KES Payment Calculation
    # ----------------------------
    applicant_fee_kes = 35000
    booth_fee_kes = 50000
    attendee_fee_kes = 35000

    total_booth_kes = (
        (doc.booth_count or 0) * booth_fee_kes
    )
    total_attendee_kes = (
        len(doc.attendees or []) * attendee_fee_kes
    )
    total_kes = (
        applicant_fee_kes +
        total_booth_kes +
        total_attendee_kes
    )

    #---------------------------------
    # EUR equivalents (fixed values)
    #----------------------------------
    applicant_fee_eur = 300
    booth_fee_eur = 460
    attendee_fee_eur = 300

    total_booth_eur = (
        (doc.booth_count or 0) * booth_fee_eur
    )
    total_attendee_eur = (
        len(doc.attendees or []) * attendee_fee_eur
    )
    total_eur = (
        applicant_fee_eur +
        total_booth_eur +
        total_attendee_eur
    )

    frappe.db.set_value("Event Registration", doc.name, "total_amount", total_kes)
    frappe.db.set_value("Event Registration", doc.name, "total_amount_eur", total_eur)

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
                margin: 40px;
                color: #333;
                }}
                h1 {{
                text-align: center;
                margin-bottom: 20px;
                }}
                .flex-header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
                }}
                .bold {{        
                font-weight: bold;
                }}
                table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                }}
                table th, table td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
                }}
                table th {{
                background: #f4f4f4;
                }}
                .totals {{
                float: right;
                width: 300px;
                margin-top: 20px;
                }}
                .totals td {{
                padding: 8px;
                }}
                .highlight {{
                background: #eaeaea;
                padding: 10px;
                font-weight: bold;
                }}
                .footer {{
                text-align: center;
                font-size: 12px;
                margin-top: 30px;
                color: #666;
                }}
                .page-break {{
                page-break-before: always; 
                break-before: page;
                }}
            </style>
        </head>
        <body>
            <h1>INVOICE</h1>

            <table style="width:100%; margin-bottom:20px; border:none;">
                <tr style="border: none;">
                    <td style="text-align:left; vertical-align:top; border: none;">
                        <p><span class="bold">Quercus Group</span></p>
                        <p>I4WASH Marketplace forum<br>
                        5<sup>th</sup>– 8<sup>th</sup> November 2025,<br>
                        Malindi<br>
                        Kenya.</p>
                    </td>
                    <td style="text-align:right; vertical-align:top; border: none;">
                        <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="max-height:60px"><br>
                        <p>Invoice no: {doc.invoice_number} <br>
                        Invoice date: {frappe.utils.formatdate(doc.creation, "dd MMM yyyy")}<br>
                        Our reference: Mariam Njoroge<br>
                        Their reference: <span class="bold">{doc.full_name}, {doc.organization}</span></p>
                    </td>
                </tr>
            </table>

            <table>
                <tr>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Amount (KES)</th>
                    <th>Amount (EUR)</th>
                </tr>
                <tr>
                    <td><b>Applicant fee</b></td>
                    <td>1</td>
                    <td>{kes(applicant_fee_kes)}</td>
                    <td>{eur(applicant_fee_eur)}</td>
                </tr>
                <tr>
                    <td>Booth Fee</td>
                    <td>{doc.booth_count or 0}</td>
                    <td>{kes(total_booth_kes)}</td>
                    <td>{eur(total_booth_eur)}</td>
                </tr>
                <tr>
                    <td>Attendee Fee</td>
                    <td>{len(doc.attendees or [])}</td>
                    <td>{kes(total_attendee_kes)}</td>
                    <td>{eur(total_attendee_eur)}</td>
                </tr>
            </table>

            <table class="totals">
                <tr>
                    <td class="bold">Subtotal</td>
                    <td>{kes(total_kes)}</td>
                    <td>{eur(total_eur)}</td>
                </tr>
                <tr>
                    <td class="bold">VAT (0%)</td>
                    <td>0</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td class="bold">Total</td>
                    <td class="bold">{kes(total_kes)}</td>
                    <td class="bold">{eur(total_eur)}</td>
                </tr>
            </table>
            <div style="clear: both;"></div>
            <div class="page-break"></div>

            <p><span class="bold">Terms of payment:</span><br>
            - Should be paid <span class="bold">within 7 days on the date on this invoice.</span><br>
            - All transfer fees are to be paid by the client<br>
            - Regarding VAT, the supplied services are subject to reverse charge in the country of receipt.<br>
            - When paying by bank transfer, please state your <span class="bold">organization name</span>
            </p>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: rgba(203, 201, 159, 1);">
                    <td colspan="2">Payment instructions:</td>
                </tr>
                <tr style="background-color: rgba(203, 201, 159, 1);">
                    <td colspan="2"><p style="padding:10px;">Payment can be made in either cash, cash transfer or even cheque to either of accounts below:</p></td>
                </tr>
                <tr style="background: rgba(236, 236, 221, 0.05);">
                    <td>
                        <p><span class="bold">Payment in KES:</span><br>
                        Account name: Quercus Group Ltd.<br>
                        Bank: NCBA<br>
                        Account no: 7494880018<br>
                        Bank Address: 30437-00100<br>
                        Branch code: 07000<br>
                        Swift code: CBAFKENX</p>
                        <p>For MPESA Payments, Kindly use Paybill number <br> <b>880100</b> and use the above details.</p>
                    </td>
                    <td>
                        <p><span class="bold">Payment in Euros:</span><br>
                        Account name: Quercus Group Ltd.<br>
                        Bank: NCBA<br>
                        Account no: 7494880023<br>
                        Bank Address: 30437-00100<br>
                        Branch code: 07000<br>
                        Swift code: CBAFKENX</p>
                    </td>
                </tr>
            </table>

            <p style="margin-top:30px;">
                Co – organizing team,<br>
                Innovate for WASH Forum<br>
                +254723341220
            </p>

            <div class="footer">
                Quercus Group Ltd | Pin: P051526263L | C/O Climate Innovation Center, Ole Sangale Road, Madaraka Estate<br>
                Box 59857 - 00200 Nairobi, Kenya | www.quercus-group.com | info@quercus-group.com
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