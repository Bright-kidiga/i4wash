import frappe
import re
from frappe import _

def clean_input(text):
    # Remove any character that's not a letter, number, dash, or space
    return re.sub(r"[^\w\s\-]", "", text or "")

@frappe.whitelist(allow_guest=True)
def contact_sponsor(fullName, email, organization, role, message):
    safe_name = clean_input(fullName)
    safe_organization = clean_input(organization)
    safe_role = clean_input(role)

    subject = f"{safe_role.capitalize()} Inquiry: {safe_organization or safe_name}"

    body = f"""
    <p><strong>Name:</strong> {safe_name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Organization:</strong> {safe_organization or "Not provided"}</p>
    <p><strong>Role:</strong> {safe_role.capitalize()}</p>
    <p><strong>Message:</strong></p>
    <p>{message.replace('\n', '<br>')}</p>
    """

    frappe.sendmail(
        recipients=["hekimalibrary@gmail.com"],
        subject=subject,
        message=body,
        reply_to=email
    )

    return {"status": "success", "message": "Email sent"}