import os
import sys
import json
from dotenv import load_dotenv
import httpx

# Load .env
load_dotenv()

PIPEDRIVE_TOKEN = os.getenv("PIPEDRIVE_ACCESS_TOKEN")
PIPEDRIVE_DOMAIN = "jeppe-sandbox"  # Change if needed

if not PIPEDRIVE_TOKEN:
    print("No PIPEDRIVE_ACCESS_TOKEN found in .env")
    sys.exit(1)

# Decrypt if needed (copied from main logic)
if PIPEDRIVE_TOKEN.startswith("v1u:"):
    access_token = PIPEDRIVE_TOKEN
else:
    import re

    is_base64 = (
        bool(re.fullmatch(r"[A-Za-z0-9_\-]+=*", PIPEDRIVE_TOKEN))
        and len(PIPEDRIVE_TOKEN) > 60
    )
    if is_base64:
        sys.path.append(os.path.join(os.path.dirname(__file__), "app", "lib"))
        from encryption import token_encryption

        access_token = token_encryption.decrypt_token(PIPEDRIVE_TOKEN)
    else:
        access_token = PIPEDRIVE_TOKEN

# Email to check (hardcoded or via CLI)
if len(sys.argv) > 1:
    email = sys.argv[1]
else:
    email = "peter.hansen@microsoft.com"  # Default for testing

print(f"\n🔍 Checking for contact with email: {email}\n")

url = f"https://{PIPEDRIVE_DOMAIN}.pipedrive.com/api/v2/persons/search"
headers = {"Authorization": f"Bearer {access_token}"}
params = {"term": email, "fields": "email"}

with httpx.Client() as client:
    resp = client.get(url, headers=headers, params=params)
    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
        print("\nRaw response:")
        print(json.dumps(data, indent=2))
        found = False
        items = data.get("data", {}).get("items", [])
        for item in items:
            person = item.get("item", {})
            print(f"\nPerson: {person.get('name')} (ID: {person.get('id')})")
            emails = person.get("emails", [])
            for e in emails:
                print(f"  Email: {e.get('value')}")
                if e.get("value", "").lower() == email.lower():
                    found = True
        if found:
            print(f"\n✅ Email {email} FOUND in Pipedrive.")
        else:
            print(f"\n❌ Email {email} NOT found in Pipedrive.")
    except Exception as e:
        print(f"Error parsing response: {e}")
