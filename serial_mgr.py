from fernet import Fernet 
import json

KEY = b"bW8k0iO_bekfUW-e90nuxzKRr5dx6Bn1J0DsXNSKWAo="
cipher = Fernet(KEY)
data = {
    "first_run": True,
    "first_run_date": "2026-06-04",
    "activated": False,
    "logged-in": None,
    "users":{
        "admin" : "salah123",
        "seller" : "modeer123"
    }
}

json_text = json.dumps(data)
encrypted = cipher.encrypt(json_text.encode())
with open("file_mgr.dat", "wb") as file:
    file.write(encrypted)