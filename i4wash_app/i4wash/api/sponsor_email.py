# import frappe
# import re
# from frappe import _

# def clean_input(text):
#     # Remove any character that's not a letter, number, dash, or space
#     return re.sub(r"[^\w\s\-]", "", text or "")

# @frappe.whitelist(allow_guest=True)
# def contact_sponsor(fullName, email, organization, role, message):
#     safe_name = clean_input(fullName)
#     safe_organization = clean_input(organization)
#     safe_role = clean_input(role)

#     subject = f"{safe_role.capitalize()} Inquiry: {safe_organization or safe_name}"

#     body = f"""
#     <p><strong>Name:</strong> {safe_name}</p>
#     <p><strong>Email:</strong> {email}</p>
#     <p><strong>Organization:</strong> {safe_organization or "Not provided"}</p>
#     <p><strong>Role:</strong> {safe_role.capitalize()}</p>
#     <p><strong>Message:</strong></p>
#     <p>{message.replace('\n', '<br>')}</p>
#     """

#     frappe.sendmail(
#         recipients=["hekimalibrary@gmail.com"],
#         subject=subject,
#         message=body,
#         reply_to=email
#     )

#     return {"status": "success", "message": "Email sent"}

import frappe
import re
from frappe import _

def clean_input(text):
    return re.sub(r"[^\w\s\-]", "", text or "")

@frappe.whitelist(allow_guest=True)
def contact_sponsor(fullName, email, organization, role, message):
    safe_name = clean_input(fullName)
    safe_organization = clean_input(organization)
    safe_role = clean_input(role)

    # Step 1: Send the email
    subject = f"{safe_role.capitalize()} Inquiry: {safe_organization or safe_name}"
    safe_message_html = message.replace("\n", "<br>")
    body = f"""
        <p><strong>Name:</strong> {safe_name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Organization:</strong> {safe_organization or "Not provided"}</p>
        <p><strong>Role:</strong> {safe_role.capitalize()}</p>
        <p><strong>Message:</strong></p>
        <p>{safe_message_html}</p>
    """
    frappe.sendmail(
        recipients=["hekimalibrary@gmail.com"],
        subject=subject,
        message=body,
        reply_to=email
    )

    # Step 2: Save to Doctype
    existing = frappe.db.exists(
        "Sponsors and Conveners",
        {"email": email, "role": role.capitalize()}
    )

    if not existing:
        doc = frappe.get_doc({
            "doctype": "Sponsors and Conveners",
            "full_name": fullName,
            "email": email,
            "organization": organization,
            "role": role.capitalize()
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()

    if not existing:
        message = "Email sent and contact saved."
    else:
        message = "Email sent. Contact already exists."

    return {"status": "success", "message": message}