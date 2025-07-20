import frappe
import stripe

@frappe.whitelist(allow_guest=True)
def stripe_webhook():
    payload = frappe.request.data
    sig_header = frappe.request.headers.get('stripe-signature')
    webhook_secret = frappe.db.get_single_value("Stripe Settings", "webhook_secret")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except Exception:
        frappe.local.response.http_status_code = 400
        return "Invalid payload or signature"

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        docname = session['metadata'].get('docname')
        amount = int(session.get('amount_total', 0)) / 100
        payment_intent = session.get('payment_intent')

        if docname:
            reg_doc = frappe.get_doc("Event Registration", docname)
            reg_doc.payment_status = "Paid"
            reg_doc.amount_paid = amount
            reg_doc.payment_reference = payment_intent
            reg_doc.payment_method = "Stripe"
            reg_doc.save(ignore_permissions=True)
            frappe.db.commit()

    return "Success"
