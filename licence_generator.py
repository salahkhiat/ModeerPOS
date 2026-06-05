import hashlib

app_key = "bW8k0iO_bekfUW-e90nuxzKRr5dx6Bn1J0DsXNSKWAo="
machine_id = input("MACHINE ID: ")


expected_serial = f"{app_key}{machine_id}"

hashed_serial = hashlib.md5(
    expected_serial.encode()
).hexdigest()

print("expected serial: ")
print(hashed_serial)
