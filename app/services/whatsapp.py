import requests

# Placeholder for WhatsApp API endpoint and token
WHATSAPP_API_URL = "https://api.whatsapp.com/send"
WHATSAPP_API_TOKEN = "YOUR_API_TOKEN"

def send_whatsapp_message(phone_number: str, message: str) -> bool:
    """
    Send a WhatsApp message to the given phone number.
    Replace this implementation with actual API integration.
    """
    # Example payload for a generic WhatsApp API (replace with real API details)
    payload = {
        "to": phone_number,
        "message": message
    }
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    # Simulate sending (replace with: requests.post(WHATSAPP_API_URL, json=payload, headers=headers))
    print(f"Sending WhatsApp message to {phone_number}: {message}")
    # Uncomment below for real API call
    # response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    # return response.status_code == 200
    return True

def send_new_order_message(phone_number: str, order_id: int, client_name: str) -> bool:
    message = f"Hello {client_name}, your order #{order_id} has been received! Thank you for shopping with us."
    return send_whatsapp_message(phone_number, message)

def send_quotation_message(phone_number: str, quotation_details: str, client_name: str) -> bool:
    message = f"Hello {client_name}, here is your quotation: {quotation_details}"
    return send_whatsapp_message(phone_number, message)

def send_promotion_message(phone_number: str, promotion_details: str, client_name: str) -> bool:
    message = f"Hi {client_name}, check out our latest promotion: {promotion_details}"
    return send_whatsapp_message(phone_number, message)
