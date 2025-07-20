import frappe
import stripe

@frappe.whitelist(allow_guest=True)
def create_payment_intent():
    import json
    data = json.loads(frappe.request.data)
    payment_method_id = data.get("payment_method_id")
    amount = int(data.get("amount", 0))

    if not payment_method_id or not amount:
        frappe.throw("Missing required data.")

    stripe.api_key = frappe.conf.get("stripe_secret_key")

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="kes",
            payment_method=payment_method_id,
            confirmation_method="manual",
            confirm=True,
        )
        return {
            "client_secret": intent.client_secret,
            "status": intent.status,
        }
    except stripe.error.StripeError as e:
        frappe.log_error(str(e), "Stripe Error")
        frappe.throw(str(e))
