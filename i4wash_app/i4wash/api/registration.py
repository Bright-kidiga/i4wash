import frappe
from frappe.utils.file_manager import save_file

@frappe.whitelist(allow_guest=True)
def create_event_registration():
    data = frappe.request.get_json()

    if not data:
        frappe.throw("No data received")

    # Step 1: Create Event Registration Document
    reg = frappe.get_doc({
        "doctype": "Event Registration",
        "full_name": data.get("fullName"),
        "email": data.get("email"),
        "phone_number": data.get("phone"),
        "organization": data.get("organization"),
        "designation": data.get("designation"),
        "has_presentation": "Yes" if data.get("presentationReady") == "Yes" else "No",
        "wants_booth": data.get("exhibitionBoothNeeded") or "No",
        "booth_count": data.get("exhibitionBoothCount") or 0,
        "has_attendees": "Yes" if data.get("attendees") else "No",
        "attendees": [
            {
                "full_name": att.get("fullName"),
                "email": att.get("email"),
                "attendee_phone_number": att.get("attendeePhone"),
                "organization": att.get("organization"),
            }
            for att in data.get("attendees", [])
        ]
    })

    reg.insert(ignore_permissions=True)

    # Step 2: Attach Presentation File (optional)
    if data.get("presentationFile"):
        content = frappe.utils.decode_base64(data["presentationFile"]["base64"])
        save_file(
            fname=data["presentationFile"]["filename"],
            content=content,
            dt="Event Registration",
            dn=reg.name,
            decode=False,
            is_private=True
        )

    frappe.db.commit()

    return {
        "status": "success",
        "registration_id": reg.name
    }