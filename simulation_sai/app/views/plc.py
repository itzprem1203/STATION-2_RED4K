import os
import json
import time
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pymodbus.client import ModbusTcpClient
from django.views.decorators.http import require_http_methods
import traceback

# ---------------- PLC Configuration ---------------- #
PLC_IP = "192.168.3.250"
PLC_PORT = 502
SLAVE_ID = 1
SCAN_START = 0
SCAN_END = 500
BATCH_SIZE = 10
SCAN_DELAY = 0.1#econds

# ---------------- File Path ---------------- #
ACTIVE_COILS_FILE = os.path.join(os.path.dirname(__file__), "../../active_coils.json")

# ---------------- Save Active Coils ---------------- #
def save_active_coils(addresses):
    with open(ACTIVE_COILS_FILE, "w") as f:
        json.dump({"active_coils": addresses}, f)

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

    global shift_change_trigger
    global latest_counts
    global wrote_accept, wrote_reject, wrote_rework
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    if client.connect():
        print("✅ Connected to PLC")
        try:
            while True:
                if shift_change_trigger:
                    print("🔁 Shift change trigger detected! Writing to coil 99")
                    write_result = client.write_coil(99, True, slave=SLAVE_ID)
                    if write_result and not write_result.isError():
                        print("✅ Successfully wrote True to coil 99")
                    else:
                        print("❌ Failed to write to coil 99")

                    # Step 2: Wait for short pulse (e.g., 0.5s)
                    time.sleep(1)

                    # Step 3: Write False to coil 99
                    result_off = client.write_coil(99, False, slave=SLAVE_ID)
                    if result_off and not result_off.isError():
                        print("✅ Coil 99 reset to False (pulse end)")
                    else:
                        print("❌ Failed to reset coil 99 to False")    

                    shift_change_trigger = False  # ✅ Reset trigger

                    if latest_counts:
                        print("🔁 Shift change trigger detected! Writing to coil 99")
                        write_counts = client.write_coil(99, True, slave=SLAVE_ID)
                        if write_counts and not write_counts.isError():
                            print("✅ Successfully wrote True to coil 99")
                        else:
                            print("❌ Failed to write to coil 99")

                        # Step 2: Wait for short pulse (e.g., 0.5s)
                        time.sleep(1)

                        # Step 3: Write False to coil 99
                        result_counts = client.write_coil(99, False, slave=SLAVE_ID)
                        if result_counts and not result_counts.isError():
                            print("✅ Coil 99 reset to False (pulse end)")
                        else:
                            print("❌ Failed to reset coil 99 to False")    

                        latest_counts = False  # ✅ Reset trigger



                active = []

                
                for addr in range(SCAN_START, SCAN_END + 1, BATCH_SIZE):
                    count = min(BATCH_SIZE, SCAN_END - addr + 1)
                    result = safe_read_coils(client, addr, count)
                    if result and not result.isError():
                        for i, val in enumerate(result.bits):
                            if val:
                                abs_addr = addr + i
                                active.append(abs_addr)
                                print(f"✅ address {abs_addr} = 1")

                                if abs_addr == 73:
                                    # print("🎯 Detected coil 73 is active! Writing to coil 98...")
                                    write_result = client.write_coil(98, True, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        # print("✅ Successfully wrote value 1 to coil 98")
                                        pass
                                    else:
                                        print("❌ Failed to write to address 98")
                                


                                if abs_addr == 74:
                                    # print("🎯 Detected coil 73 is active! Writing to coil 98...")

                                    write_result = client.write_coil(92, True, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        # print("✅ Successfully wrote value 1 to coil 98")
                                        pass
                                    else:
                                        print("❌ Failed to write to address 98") 

                                if abs_addr == 75:
                                    # print("🎯 Detected coil 73 is active! Writing to coil 98...")
                                    write_result = client.write_coil(92, False, slave=SLAVE_ID)
                                    write_result = client.write_coil(93, True, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        # print("✅ Successfully wrote value 1 to coil 93")
                                        pass
                                    else:
                                        print("❌ Failed to write to address 98")              


                                if abs_addr == 76:
                                    # print("🎯 Detected coil 73 is active! Writing to coil 98...")
                                    write_result = client.write_coil(93, False, slave=SLAVE_ID)
                                    write_result = client.write_coil(94, True, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        # print("✅ Successfully wrote value 1 to coil 94")
                                        pass
                                    else:
                                        print("❌ Failed to write to address 98")

                                if abs_addr == 77:
                                    # print("🎯 Detected coil 73 is active! Writing to coil 98...")
                                    write_result = client.write_coil(94, False, slave=SLAVE_ID)
                                    write_result = client.write_coil(95, True, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        # print("✅ Successfully wrote value 1 to coil 95")
                                        pass
                                    else:
                                        print("❌ Failed to write to address 98")

                                if abs_addr == 81:
                                    print("🎯 Detected coil 73 is active! Writing to coil 98...")
                                    write_result = client.write_coil(95, False, slave=SLAVE_ID)
                                    def delayed_write_96():
                                        write_result = client.write_coil(96, True, slave=SLAVE_ID)
                                        if write_result and not write_result.isError():
                                            # print("✅ Delayed: Successfully wrote value 1 to coil 96 after 5 seconds")
                                            pass
                                        else:
                                            print("❌ Delayed: Failed to write to coil 96")

                                    threading.Timer(5.0, delayed_write_96).start()                


                                if abs_addr == 83:
                                    # print("🎯 Detected coil 73 is active! Writing to coil 98...")
                                    
                                    def delayed_write_97():
                                        write_result = client.write_coil(97, True, slave=SLAVE_ID)
                                        if write_result and not write_result.isError():
                                            # print("✅ Delayed: Successfully wrote value 1 to coil 96 after 5 seconds")
                                            pass
                                        else:
                                            print("❌ Delayed: Failed to write to coil 96")

                                    threading.Timer(5.0, delayed_write_97).start()

                                if abs_addr != 81:    
                                    write_result = client.write_coil(96, False, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        # print("✅ Successfully wrote value 1 to coil 96")
                                        pass
                                    else:
                                        print("❌ Failed to write to address 98")


                                if abs_addr != 83: 
                                    write_result = client.write_coil(97, False, slave=SLAVE_ID)
                                    if write_result and not write_result.isError():
                                        # print("✅ Successfully wrote value 1 to coil 96")
                                        pass
                                    else:
                                        print("❌ Failed to write to address 98")

                                if abs_addr == 116:
                                    # Reset ACCEPT / REWORK / REJECT output coils
                                    write_result = client.write_coil(90, False, slave=SLAVE_ID)
                                    write_result = client.write_coil(91, False, slave=SLAVE_ID)

                                    if write_result and not write_result.isError():
                                        print("✅ Coil 116 triggered → Reset REJECT & REWORK coils (90, 91)")
                                    else:
                                        print("❌ Failed to reset coil 90 or 91")

                                    # ✅ Reset write flags for new part
                                    wrote_accept = False
                                    wrote_rework = False
                                    wrote_reject = False
                                    print("🔄 Reset status write flags for new part")
               

                                        

                                if abs_addr == 115:
                                    print("🎯 Detected coil 72 is active! Writing to appropriate coil...")

                                    # Write only once for each status
                                    if latest_status == "ACCEPT" and not wrote_accept:
                                        status_result = client.write_coil(89, True, slave=SLAVE_ID)
                                        if status_result and not status_result.isError():
                                            print("✅ ACCEPT: Wrote value 1 to coil 89")
                                            wrote_accept = True
                                            wrote_rework = False
                                            wrote_reject = False
                                        else:
                                            print("❌ Failed to write to coil 89")

                                    elif latest_status == "REWORK" and not wrote_rework:
                                        status_result = client.write_coil(91, True, slave=SLAVE_ID)
                                        if status_result and not status_result.isError():
                                            print("✅ REWORK: Wrote value 1 to coil 91")
                                            wrote_rework = True
                                            wrote_accept = False
                                            wrote_reject = False
                                        else:
                                            print("❌ Failed to write to coil 91")

                                    elif latest_status == "REJECT" and not wrote_reject:
                                        status_result = client.write_coil(90, True, slave=SLAVE_ID)
                                        if status_result and not status_result.isError():
                                            print("✅ REJECT: Wrote value 1 to coil 90")
                                            wrote_reject = True
                                            wrote_accept = False
                                            wrote_rework = False
                                        else:
                                            print("❌ Failed to write to coil 90")



                                        

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
