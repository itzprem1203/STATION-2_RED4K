import os
import json
import time
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pymodbus.client import ModbusTcpClient
from django.views.decorators.http import require_http_methods
import traceback
from datetime import datetime

# ---------------- PLC Configuration ---------------- #
PLC_IP = "192.168.3.250"
PLC_PORT = 502
SLAVE_ID = 1
SCAN_START = 0
SCAN_END = 500
BATCH_SIZE = 10
SCAN_DELAY = 0.01  # Read every 10ms instead of 100ms
#econds

client = None


# ---------------- File Path ---------------- #
ACTIVE_COILS_FILE = os.path.join(os.path.dirname(__file__), "../../active_coils.json")

REGISTER_VALUE_FILE = os.path.join(os.path.dirname(__file__), "../../register_value.json")


# ---------------- Save Active Coils ---------------- #
def save_active_coils(addresses):
    with open(ACTIVE_COILS_FILE, "w") as f:
        json.dump({"active_coils": addresses}, f)


def save_register_value(value):
    with open(REGISTER_VALUE_FILE, "w") as f:
        json.dump({"register_value": value}, f)


# ---------------- Safe Read ---------------- #
def safe_read_coils(client, address, count):
    try:
        return client.read_coils(address, count=count, slave=SLAVE_ID)
    except Exception as e:
        print(f"❌ Error reading coils at {address}: {e}")
        return None

# ---------------- Continuous Reader ---------------- #

found_72 = False
found_88 = False
wrote_accept = False
wrote_reject = False
wrote_rework = False
latest_counts = False

def read_coils_loop():
    global client
    global shift_change_trigger
    global latest_counts
    global wrote_accept, wrote_reject, wrote_rework
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    if client.connect():
        print("✅ Connected to PLC")

        try:
            while True:
                active = []

                # Read coils
                for addr in range(SCAN_START, SCAN_END + 1, BATCH_SIZE):
                    count = min(BATCH_SIZE, SCAN_END - addr + 1)
                    result = safe_read_coils(client, addr, count)
                    if result and not result.isError():
                        for i, val in enumerate(result.bits):
                            if val:
                                abs_addr = addr + i
                                active.append(abs_addr)
                                # print(f"✅ address {abs_addr} = 1")

                                if abs_addr == 74:
                                    time.sleep(4)  # Wait 4 seconds
                                    write_result = client.write_coil(113, True, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        pass
                                    else:
                                        print("❌ Failed to write to address 98")

                                # if abs_addr != 74:

                                #     write_result = client.write_coil(113, False, slave=SLAVE_ID)
                                #     if write_result and not write_result.isError():
                                #         pass
                                #     else:
                                #         print("❌ Failed to write to address 98")        

                                if abs_addr == 65:
                                    write_result = client.write_coil(104, True, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        pass
                                    else:
                                        print("❌ Failed to write to address 104")

                                if abs_addr == 67:
                                    write_result = client.write_coil(105, True, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        pass
                                    else:
                                        print("❌ Failed to write to address 105")

                save_active_coils(active)

                time.sleep(SCAN_DELAY)

        except Exception as e:
            print("⛔ PLC loop error:", e)
        finally:
            client.close()
            print("🔌 Disconnected")
    else:
        print("❌ PLC connection failed")


threading.Thread(target=read_coils_loop, daemon=True).start()





def read_d1003_loop():
    global client
    while True:
        try:
            if client and client.connected:
                reg_result = client.read_holding_registers(1003, 2, slave=SLAVE_ID)
                if reg_result and not reg_result.isError():
                    from pymodbus.payload import BinaryPayloadDecoder
                    from pymodbus.constants import Endian

                    decoder = BinaryPayloadDecoder.fromRegisters(
                        reg_result.registers,
                        byteorder=Endian.BIG,
                        wordorder=Endian.BIG
                    )
                    reg_value = decoder.decode_16bit_uint()
                    # print(f"📊 {datetime.now().strftime('%H:%M:%S.%f')[:-3]} → D1003 = {reg_value}")
                    save_register_value(reg_value)
            else:
                print("⚠️ PLC not connected, skipping D1003 read.")
        except Exception as e:
            print("⛔ Error reading D1003:", e)

        time.sleep(0.01)

threading.Thread(target=read_d1003_loop, daemon=True).start()


@csrf_exempt
def get_register_value(request):
    if request.method == "GET":
        try:
            with open(REGISTER_VALUE_FILE, "r") as f:
                data = json.load(f)
                return JsonResponse(data)
        except FileNotFoundError:
            return JsonResponse({"register_value": None})




@csrf_exempt
def send_counts_to_plc(request):
    global client

    try:
        data = json.loads(request.body)
        accept = int(data.get("accept", 0))
        reject = int(data.get("reject", 0))
        rework = int(data.get("rework", 0))

        # 📌 Debug: Show what will be written
        print(f"🔢 Writing to PLC → Accept: {accept}, Reject: {reject}, Rework: {rework}")

        # Ensure the PLC connection is active
        if client is None or not client.connected:
            return JsonResponse({"error": "PLC connection not available"}, status=500)

        # ✅ Write values and confirm
        res1 = client.write_register(1100, accept, slave=SLAVE_ID)
        if res1 and not res1.isError():
            print(f"✅ Successfully wrote {accept} to register 1100")
        else:
            print(f"❌ Failed to write {accept} to register 1100")

        res2 = client.write_register(1102, reject, slave=SLAVE_ID)
        if res2 and not res2.isError():
            print(f"✅ Successfully wrote {reject} to register 1102")
        else:
            print(f"❌ Failed to write {reject} to register 1102")

        res3 = client.write_register(1104, rework, slave=SLAVE_ID)
        if res3 and not res3.isError():
            print(f"✅ Successfully wrote {rework} to register 1104")
        else:
            print(f"❌ Failed to write {rework} to register 1104")

        return JsonResponse({"status": "success"})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# shared trigger
shift_change_trigger = False  # this will be accessed in the loop

@csrf_exempt
def reset_counter(request):
    global shift_change_trigger
    if request.method == "POST":
        print("🔄 Reset counter triggered from frontend")
        shift_change_trigger = True
        return JsonResponse({"status": "triggered"})
    return JsonResponse({"status": "only POST allowed"})


# ---------------- GET View to Send Coil Status ---------------- #
# def get_plc_status(request):
#     try:
#         with open(ACTIVE_COILS_FILE, "r") as f:
#             data = json.load(f)
#             return JsonResponse(data)
#     except FileNotFoundError:
#         return JsonResponse({"active_coils": []})
    

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_plc_status(request):
    if request.method == "GET":
        try:
            with open(ACTIVE_COILS_FILE, "r") as f:
                data = json.load(f)
                return JsonResponse(data)
        except FileNotFoundError:
            return JsonResponse({"active_coils": []})

   

# ---------------- POST View to Write Coil ---------------- #
@csrf_exempt
@require_http_methods(["POST"])
def write_coil(request):
    try:
        if request.method == "POST":
            import json
            data = json.loads(request.body)

            address =97
            value = True

            print(f"🔧 Writing coil {address} with value {value}...")

            client = ModbusTcpClient("192.168.3.250", port=502)
            if not client.connect():
                print("🚫 Failed to connect to PLC.")
                return JsonResponse({"status": "error", "message": "PLC connection failed"}, status=500)

            result = client.write_coil(address, value)
            client.close()

            if result.isError():
                print("❌ Write error:", result)
                return JsonResponse({"status": "error", "message": "Write failed"}, status=500)

            return JsonResponse({"status": "success", "message": f"Value written to coil {address}"})

        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    except Exception as e:
        print("🔥 Exception in write_coil:", e)
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)}, status=500)




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

latest_status = None  # Global or thread-safe variable to share with your loop
latest_counts = None  # Global or thread-safe variable to share with your loop

@csrf_exempt
def post_part_status(request):
    global latest_status
    global latest_counts
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status = data.get('status')
            counts = data.get('counts')
            if status:
                latest_status = status  # ✅ Save status to use in PLC loop
                print(f"📥 Received part status: {status}")
                return JsonResponse({'message': 'Status received'}, status=200)
            if counts:
                latest_counts = counts  # ✅ Save status to use in PLC loop
                print(f"📥 Received part statusdddddddddddddddddddddddddddddddddddddd: {counts}")
                return JsonResponse({'message': 'Status received'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt
def shift_change_alert(request):
    global shift_change_trigger  # ✅ Declare global to set it
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            shift = data.get("shift")
            message = data.get("message")
            timestamp = data.get("timestamp")

            print(f"📢 Shift Change Alert Received:")
            print(f"➡️ Shift: {shift}")
            print(f"🕒 Time: {timestamp}")
            print(f"📝 Message: {message}")

            # ✅ Set flag to trigger PLC write
            shift_change_trigger = True

            return JsonResponse({"status": "Shift change received", "shift": shift})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)
