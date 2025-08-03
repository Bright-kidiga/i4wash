# import frappe
# import requests
# import base64
# from frappe import _
# from frappe.utils import now_datetime
# from frappe import whitelist

# @frappe.whitelist(allow_guest=True)
# def initiate_stk_push(phone, amount, account_reference=None, transaction_desc=None):
#     # Validate inputs
#     if not phone.startswith("2547") or len(phone) != 12:
#         frappe.throw(_("Invalid phone number. Must start with 2547 and be 12 digits."))

#     site_config = frappe.get_site_config()
#     consumer_key = site_config.get("mpesa_consumer_key")
#     consumer_secret = site_config.get("mpesa_consumer_secret")
#     shortcode = site_config.get("mpesa_shortcode")
#     passkey = site_config.get("mpesa_passkey")

#     # Get access token
#     auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
#     response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
#     access_token = response.json().get("access_token")

#     # Generate password
#     from datetime import datetime
#     timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#     password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()

#     stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "BusinessShortCode": shortcode,
#         "Password": password,
#         "Timestamp": timestamp,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": int(amount),
#         "PartyA": phone,
#         "PartyB": shortcode,
#         "PhoneNumber": phone,
#         "CallBackURL": f"{frappe.utils.get_url()}/api/method/i4wash.api.mpesa.mpesa_callback",
#         "AccountReference": account_reference,
#         "TransactionDesc": transaction_desc
#     }

#     r = requests.post(stk_url, headers=headers, json=payload)
#     frappe.logger().info(f"STK Response: {r.text}")

#     return r.json()


# @frappe.whitelist(allow_guest=True)
# def mpesa_callback():
#     try:
#         data = frappe.local.form_dict
#         payload = json.loads(data.get("body"))
#         stk_callback = payload.get("Body", {}).get("stkCallback", {})

#         result_code = stk_callback.get("ResultCode")
#         checkout_request_id = stk_callback.get("CheckoutRequestID")
#         amount = None
#         phone = None

#         metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
#         for item in metadata:
#             if item["Name"] == "Amount":
#                 amount = item["Value"]
#             if item["Name"] == "PhoneNumber":
#                 phone = str(item["Value"])

#         frappe.logger("mpesa").info(f"Callback: ResultCode={result_code}, Phone={phone}, Amount={amount}")

#         if result_code == 0 and phone:
#             if frappe.db.exists("Registration", {"phone": phone}):
#                 doc = frappe.get_doc("Registration", {"phone": phone})
#                 doc.payment_status = "Paid"
#                 doc.save(ignore_permissions=True)
#                 frappe.logger("mpesa").info(f"Payment recorded for phone {phone}")
#             else:
#                 frappe.logger("mpesa").error(f"No Registration found for phone {phone}")
#         else:
#             frappe.logger("mpesa").error(f"Payment failed. ResultCode={result_code}")

#         return "OK"

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "MPesa Callback Error")
#         return "Error processing callback"


# i4wash_app/iwash/api/mpesa.py

import frappe
import requests
import json
import base64
from frappe import _

# Helper to get access token from Safaricom
def get_access_token():
    consumer_key = frappe.conf.get("mpesa_consumer_key")
    consumer_secret = frappe.conf.get("mpesa_consumer_secret")

    if not consumer_key or not consumer_secret:
        frappe.throw(_("Missing consumer credentials in site config"))

    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=(consumer_key, consumer_secret))

    if response.status_code != 200:
        frappe.log_error(response.text, "MPESA Token Error")
        frappe.throw(_("Failed to get access token from Safaricom"))

    try:
        return response.json().get("access_token")
    except Exception:
        frappe.log_error(response.text, "Invalid Token Response")
        frappe.throw(_("Invalid JSON in token response"))

@frappe.whitelist(allow_guest=True)
def initiate_stk_push(phone, amount, account_reference, transaction_desc):
    # Convert to 2547XXXXXXXX format
    phone = phone.replace("+", "").strip()
    if phone.startswith("07"):
        phone = "254" + phone[1:]

    # Load config
    business_short_code = frappe.conf.get("mpesa_shortcode")
    passkey = frappe.conf.get("mpesa_passkey")

    if not all([business_short_code, passkey]):
        frappe.throw(_("Missing MPESA settings in site config"))

    # Get access token using helper
    access_token = get_access_token()

    # Generate password
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": business_short_code,
        "PhoneNumber": phone,
        "CallBackURL": "http://www.i4wash.com:8000/api/method/i4wash_app.i4wash.api.payment_api.initiate_stk_push",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    response = requests.post(stk_url, json=payload, headers=headers)
    frappe.logger().info(f"STK Push Request: {json.dumps(payload)}")
    frappe.logger().info(f"STK Push Response: {response.text}")

    return response.json()