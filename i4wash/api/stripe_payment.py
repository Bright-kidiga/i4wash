import frappe
import stripe
from frappe import _

@frappe.whitelist(allow_guest=True)
def card_payment(name_on_card, card_number, exp_month, exp_year, cvc, amount, currency):
    # Validate input
    if currency not in ["USD", "DKK"]:
        return {"success": False, "message": "Unsupported currency. Use KES or EUR."}

    try:
        # Get correct Stripe secret key
        stripe_key = frappe.conf.get("stripe_keys", {}).get(currency, {}).get("secret_key")
        if not stripe_key:
            return {"success": False, "message": f"Stripe key for {currency} not configured"}

        stripe.api_key = stripe_key

        # Step 1: Create payment method
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": card_number,
                "exp_month": int(exp_month),
                "exp_year": int(exp_year),
                "cvc": cvc
            },
            billing_details={
                "name": name_on_card
            }
        )

        # Step 2: Create a PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount) * 100,  # Stripe uses cents
            currency=currency.lower(),
            payment_method=payment_method.id,
            confirm=True
        )

        return {
            "success": True,
            "message": "Payment successful",
            "payment_intent_id": payment_intent.id,
            "currency": currency,
            "amount": amount
        }

    except stripe.error.CardError as e:
        return {"success": False, "message": f"Card error: {str(e)}"}
    except Exception as e:
        frappe.log_error(f"Stripe card error: {str(e)}", "Card Payment Error")
        return {"success": False, "message": f"Payment failed: {str(e)}"}
