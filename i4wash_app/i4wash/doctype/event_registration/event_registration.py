# Copyright (c) 2025, M&M devs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EventRegistration(Document):
    pass

def after_insert(doc, method):
    """Send confirmation email after registration is created."""
    if not doc.email:
        return

    subject = "Thank You for Registering - Malindi 2025"
    message = f"""
        <p>Dear {doc.full_name},</p>
        <p>Thank you for registering for the Malindi 2025 Event.</p>
        <p><strong>Registration Summary:</strong></p>
        <ul>
            <li><b>Full Name:</b> {doc.full_name}</li>
            <li><b>Email:</b> {doc.email}</li>
            <li><b>Phone Number:</b> {doc.phone_number or 'N/A'}</li>
            <li><b>Organization:</b> {doc.organization or 'N/A'}</li>
            <li><b>Designation:</b> {doc.designation or 'N/A'}</li>
            <li><b>Presentation Ready:</b> {"Yes" if doc.has_presentation else "No"}</li>
            <li><b>Wants Booth:</b> {"Yes" if doc.wants_booth else "No"}</li>
            <li><b>Booth Count:</b> {doc.booth_count or 0}</li>
			<li><b>Attendees: {"Yes"doc.has_attendees}</b></li>
        </ul>
        <p>We look forward to your participation!</p>
		<p>Please find attached a document containing the full detailed summary and payment details<p>
        <p>Best regards,<br>Malindi 2025 Team</p>
    """

    try:
        frappe.sendmail(
            recipients=[doc.email],
            subject=subject,
            message=message
        )
    except Exception as e:
        frappe.log_error(f"Failed to send registration email: {str(e)}", "Event Registration Email Error")