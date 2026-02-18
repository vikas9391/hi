# api/views.py
import os
import requests
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from twilio.rest import Client

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP")  # e.g. 'whatsapp:+14155238886'

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

@api_view(['POST'])
def gemini_assistant(request):
    """
    Handles AI assistant requests: chat + actions (WhatsApp, call, etc.)
    """
    prompt = request.data.get("prompt")
    action = request.data.get("action", "chat")  # default = AI chat
    target = request.data.get("target")  # phone number for WhatsApp/call

    if not prompt:
        return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

    # 1️⃣ Handle AI chat (Gemini API)
    if action == "chat":
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
            data = response.json()
            reply = data['candidates'][0]['content']['parts'][0]['text']
            return Response({"reply": reply})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 2️⃣ Handle WhatsApp message
    elif action == "whatsapp" and target:
        try:
            msg = client.messages.create(
                body=prompt,
                from_=TWILIO_WHATSAPP,
                to=f"whatsapp:{target}"
            )
            return Response({"status": "sent", "sid": msg.sid})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3️⃣ Handle phone call
    elif action == "call" and target:
        try:
            call = client.calls.create(
                twiml=f'<Response><Say>{prompt}</Say></Response>',
                from_=os.getenv("TWILIO_PHONE"),
                to=target
            )
            return Response({"status": "call_started", "sid": call.sid})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response({"error": "Invalid action or missing target"}, status=status.HTTP_400_BAD_REQUEST)
