# import asyncio
# from bleak import BleakClient

# # MACOS BLE device identifier (NOT a MAC address)
# DEVICE_ID = "7CA0DD25-9E34-CF6F-3230-683A4A8974CD"

# async def main():
#     print("Trying to connect to KICKR SNAP...")

#     async with BleakClient(DEVICE_ID) as client:
#         if client.is_connected:
#             print("Connected to KICKR SNAP!")
#         else:
#             print("Failed to connect.")

#     print("Done.")

# if __name__ == "__main__":
#     asyncio.run(main())
import asyncio
from bleak import BleakClient

# --- UUIDs ---
UUID_CYCLING_POWER = "00002A63-0000-1000-8000-00805f9b34fb"  # Power Measurement
UUID_CSC_MEASUREMENT = "00002A5B-0000-1000-8000-00805f9b34fb"  # Speed/Cadence

# If 0x2A5B does NOT exist, fall back to YOUR custom UUID:
UUID_WAHOO_SPEED = "A026E037-0A7D-4AB3-97FA-F1500F9FEB8B"    # From LightBlue

def power_handler(sender, data):
    # data = BLE bytes from 0x2A63
    # Format: flags (2 bytes), instantaneous power (2 bytes, little endian)
    watts = int.from_bytes(data[2:4], byteorder="little", signed=True)
    print(f"Power: {watts} W")

def speed_handler(sender, data):
    # CSC Measurement format:
    # flags (1 byte)
    flags = data[0]

    wheel_rev_present = flags & 0x01

    if wheel_rev_present:
        # next fields:
        # Cumulative Wheel Revolutions (4 bytes)
        wheel_rev = int.from_bytes(data[1:5], byteorder="little")

        # Last Wheel Event Time (2 bytes, 1/1024s units)
        event_time = int.from_bytes(data[5:7], byteorder="little")

        print(f"Speed-raw: rev={wheel_rev}, event={event_time}")

    else:
        print("Speed: wheel revolution data not present")

async def main():
    address = "7CA0DD25-9E34-CF6F-3230-683A4A8974CD"  # Your KICKR SNAP

    print("Connecting to KICKR SNAP...")
    async with BleakClient(address) as client:
        print("Connected!")

        services = client.services

        # Determine which speed characteristic exists
        if UUID_CSC_MEASUREMENT in [c.uuid for s in services for c in s.characteristics]:
            speed_uuid = UUID_CSC_MEASUREMENT
            print("Using CSC speed characteristic (0x2A5B)")
        else:
            speed_uuid = UUID_WAHOO_SPEED
            print("Using Wahoo vendor speed UUID")

        # Subscribe to notifications
        await client.start_notify(UUID_CYCLING_POWER, power_handler)
        await client.start_notify(speed_uuid, speed_handler)

        print("Subscribed to power + speed. Listening...")

        while True:
            await asyncio.sleep(1)

asyncio.run(main())

