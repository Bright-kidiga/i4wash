import frappe
import re

def clean_input(text):
    return re.sub(r"[^\w\s\-]", "", text or "")

@frappe.whitelist(allow_guest=True)
def contact_sponsor(**kwargs):
    fullName = kwargs.get("fullName")
    email = kwargs.get("email")
    organization = kwargs.get("organization")
    role = kwargs.get("role", "sponsor")
    message = kwargs.get("message")

    if not fullName or not email or not message:
        frappe.throw("Missing required fields")

    safe_name = clean_input(fullName)
    safe_organization = clean_input(organization)
    safe_role = clean_input(role)

    # Get default recipient from Email Account, fallback to admin@example.com
    default_recipient = frappe.db.get_value(
        "Email Account",
        {"default_outgoing": 1},
        "email_id"
    ) or "admin@example.com"

    subject = f"{safe_role.capitalize()} Inquiry: {safe_organization or safe_name}"
    safe_message_html = (message or "").replace("\n", "<br>")

    body = f"""
        <p><strong>Name:</strong> {safe_name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Organization:</strong> {safe_organization or "Not provided"}</p>
        <p><strong>Role:</strong> {safe_role.capitalize()}</p>
        <p><strong>Message:</strong></p>
        <p>{safe_message_html}</p>
    """

    # Send email
    frappe.sendmail(
        recipients=[default_recipient],
        subject=subject,
        message=body,
        reply_to=email,
        now=True
    )

    # Save to Doctype if not exists
    existing = frappe.db.exists(
        "Sponsors and Conveners",
        {"email": email, "role": safe_role.capitalize()}
    )

    if not existing:
        doc = frappe.get_doc({
            "doctype": "Sponsors and Conveners",
            "full_name": fullName,
            "email": email,
            "organization": organization,
            "role": safe_role.capitalize()
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        message_out = "Email sent and contact saved."
    else:
        message_out = "Email sent. Contact already exists."

    return {"status": "success", "message": message_out}