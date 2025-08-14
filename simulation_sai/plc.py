import time
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

# PLC connection settings
PLC_IP = "192.168.3.250"
PLC_PORT = 502
SLAVE_ID = 1

REGISTER_ADDRESS = 1003  # D1003
REGISTER_COUNT = 2       # 32-bit = 2 registers

def read_d1003_as_16bit_signed(client):
    result = client.read_holding_registers(REGISTER_ADDRESS, REGISTER_COUNT, slave=SLAVE_ID)
    if result and not result.isError():
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers,
            byteorder=Endian.BIG,        # Adjust based on PLC
            wordorder=Endian.BIG         # Try BIG or LITTLE if value is flipped
        )
        value = decoder.decode_16bit_int()
        return value
    else:
        print("❌ Failed to read holding registers")
        return None

def continuous_read():
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    if client.connect():
        print("✅ Connected to PLC. Starting continuous read of D1003...")
        try:
            while True:
                value = read_d1003_as_16bit_signed(client)
                if value is not None:
                    print(f"📊 D1003 (16-bit signed): {value}")
                time.sleep(1)  # 1 second delay
        except KeyboardInterrupt:
            print("🛑 Stopped by user.")
        finally:
            client.close()
    else:
        print("❌ Could not connect to PLC.")

# Run the loop
continuous_read()
