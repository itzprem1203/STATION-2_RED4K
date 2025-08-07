from django.shortcuts import render

def zzz(request):
    return render(request, 'app/zzz.html')

# from pymodbus.client import ModbusTcpClient
# import time

# # Configuration
# PLC_IP = "192.168.3.250"
# PLC_PORT = 502
# SLAVE_ID = 1
# SCAN_START = 0
# SCAN_END = 500
# BATCH_SIZE = 10  # Read coils in batches of 10
# SCAN_DELAY = 1   # Seconds between full scans

# WRITE_COIL_ADDRESS = 90  # Address to write to
# WRITE_VALUE = False       # True = 1, False = 0

# def safe_read_coils(client, address, count):
#     try:
#         return client.read_coils(address, count=count, slave=SLAVE_ID)
#     except Exception as e:
#         print(f"❌ Error reading coils at {address}: {e}")
#         return None

# client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
# connected = client.connect()

# if connected:
#     print(f"✅ Connected to PLC at {PLC_IP}")

#     # Write value 1 to coil address 77
#     print(f"✍️ Writing value {int(WRITE_VALUE)} to coil address {WRITE_COIL_ADDRESS}...")
#     write_result = client.write_coil(WRITE_COIL_ADDRESS, WRITE_VALUE, slave=SLAVE_ID)
#     if not write_result.isError():
#         print(f"✅ Successfully wrote value to address {WRITE_COIL_ADDRESS}")
#     else:
#         print(f"❌ Failed to write to address {WRITE_COIL_ADDRESS}: {write_result}")

#     try:
#         while True:
#             print(f"\n🔍 Scanning coil addresses {SCAN_START} to {SCAN_END}...")
#             for addr in range(SCAN_START, SCAN_END + 1, BATCH_SIZE):
#                 count = min(BATCH_SIZE, SCAN_END - addr + 1)
#                 result = safe_read_coils(client, addr, count)
#                 if result and not result.isError():
#                     for i, val in enumerate(result.bits):
#                         if val:
#                             print(f"✅ address {addr + i} = 1")
#                 else:
#                     print(f"⚠️ No response or error at address {addr}")
#             print("-" * 40)
#             time.sleep(SCAN_DELAY)
#     except KeyboardInterrupt:
#         print("\n❌ Stopped by user.")
#     finally:
#         client.close()
#         print("🔌 Disconnected from PLC.")
# else:
#     print(f"❌ Could not connect to PLC at {PLC_IP}")
