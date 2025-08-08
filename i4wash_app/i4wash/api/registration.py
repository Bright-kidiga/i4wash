import frappe
from frappe.utils.file_manager import save_file
import base64

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
                "attendee_organization": att.get("attendeeOrganization"),
            }
            for att in data.get("attendees", [])
        ]
    })

    reg.insert(ignore_permissions=True)

    # Step 2: Attach Presentation File (optional)
    if data.get("presentationFile"):
        # Extract file extension
        original_filename = data["presentationFile"]["filename"]
        ext = original_filename.split('.')[-1].lower()

        # Validate extension
        allowed_extensions = ["pdf", "ppt", "pptx"]
        if ext not in allowed_extensions:
            frappe.throw("Only PDF, PPT, and PPTX files are allowed for presentation uploads.")

        # Format custom filename
        org_name = (reg.organization or "UnknownOrg").strip().replace(" ", "_")
        custom_filename = f"{org_name}-Malindi_2025.{ext}"

        # Decode and save file
        content = base64.b64decode(data["presentationFile"]["base64"])
        save_file(
            fname=custom_filename,
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
