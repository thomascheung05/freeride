import asyncio
from bleak import BleakClient # type: ignore
import struct




DEVICE_ID = "7CA0DD25-9E34-CF6F-3230-683A4A8974CD"
CHAR_UUID = "00002A63-0000-1000-8000-00805f9b34fb"  # KICKR SNAP Power Measurement
WHEEL_CIRCUMFERENCE = 2.105 

prev_crank_revs = None
prev_crank_event_time = None
prev_wheel_revs = None
prev_wheel_event_time = None
def notification_handler(sender, data):
    global prev_crank_revs, prev_crank_event_time, prev_wheel_revs, prev_wheel_event_time

    # Convert to bytes for parsing
    b = bytearray(data)
    
    # 1️⃣ Flags (2 bytes)
    flags = struct.unpack_from("<H", b, 0)[0]

    # 2️⃣ Instantaneous power (2 bytes, signed)
    power_watts = struct.unpack_from("<h", b, 2)[0]

    offset = 4
    accumulated_torque = None
    crank_revs = None
    last_crank_event_time = None
    cadence_rpm = None
    speed_kmh = None

    # 3️⃣ Check for optional fields based on flags
    if flags & 0x01:  # Pedal Power Balance present (skip for now)
        pedal_balance = struct.unpack_from("<B", b, offset)[0]
        offset += 1

    if flags & 0x02:  # Accumulated Torque present
        accumulated_torque = struct.unpack_from("<H", b, offset)[0] / 32.0  # Nm
        offset += 2

    if flags & 0x04:  # Wheel Revolution Data present
        wheel_revs, last_wheel_event_time = struct.unpack_from("<LH", b, offset)
        offset += 6
        # Calculate speed
        if prev_wheel_revs is not None and prev_wheel_event_time is not None:
            delta_revs = wheel_revs - prev_wheel_revs
            delta_time_sec = (last_wheel_event_time - prev_wheel_event_time) / 1024
            if delta_time_sec > 0:
                speed_m_s = (delta_revs * WHEEL_CIRCUMFERENCE) / delta_time_sec
                speed_kmh = speed_m_s * 3.6
        prev_wheel_revs = wheel_revs
        prev_wheel_event_time = last_wheel_event_time

    if flags & 0x08:  # Crank Revolution Data present
        crank_revs, last_crank_event_time = struct.unpack_from("<HH", b, offset)
        offset += 4
        # Calculate cadence
        if prev_crank_revs is not None and prev_crank_event_time is not None:
            delta_revs = crank_revs - prev_crank_revs
            delta_time_sec = (last_crank_event_time - prev_crank_event_time) / 1024
            if delta_time_sec > 0:
                cadence_rpm = (delta_revs / delta_time_sec) * 60
        prev_crank_revs = crank_revs
        prev_crank_event_time = last_crank_event_time

    # Print all parsed variables
    print(f"Flags: {flags}")
    print(f"Power (W): {power_watts}")
    if accumulated_torque is not None:
        print(f"Torque (Nm): {accumulated_torque}")
    if crank_revs is not None:
        print(f"Crank Revs: {crank_revs}")
        print(f"Last Crank Event Time: {last_crank_event_time}")
    if cadence_rpm is not None:
        print(f"Cadence (RPM): {cadence_rpm:.2f}")
    if wheel_revs is not None:
        print(f"Wheel Revs: {wheel_revs}")
        print(f"Last Wheel Event Time: {last_wheel_event_time}")
    if speed_kmh is not None:
        print(f"Speed (km/h): {speed_kmh:.2f}")
    print("-" * 30)


async def fx_connect_to_device():
    print("Trying to connect to KICKR SNAP...")

    async with BleakClient(DEVICE_ID) as client:
        if client.is_connected:
            print("Connected to KICKR SNAP!")
            # Subscribe to notifications
            await client.start_notify(CHAR_UUID, notification_handler)
            print("Subscribed to notifications. Waiting for data...")
            
            # Keep the program running to receive notifications
            await asyncio.sleep(30)  # Adjust the duration as needed
            await client.stop_notify(CHAR_UUID)
        else:
            print("Failed to connect.")

# Run the async function
asyncio.run(fx_connect_to_device())





# def notification_handler(sender, data):
#     """This will be called every time the device sends a notification."""
#     print(data)

# async def fx_connect_to_device():
#     print("Trying to connect to KICKR SNAP...")

#     async with BleakClient(DEVICE_ID) as client:
#         if client.is_connected:
#             print("Connected to KICKR SNAP!")
#         else:
#             print("Failed to connect.")






# import asyncio
# from bleak import BleakClient # type: ignore

# # --- UUIDs ---
# UUID_CYCLING_POWER = "00002A63-0000-1000-8000-00805f9b34fb"  # Power Measurement
# UUID_CSC_MEASUREMENT = "00002A5B-0000-1000-8000-00805f9b34fb"  # Speed/Cadence

# # If 0x2A5B does NOT exist, fall back to YOUR custom UUID:
# UUID_WAHOO_SPEED = "A026E037-0A7D-4AB3-97FA-F1500F9FEB8B"    # From LightBlue

# def power_handler(sender, data):
#     # data = BLE bytes from 0x2A63
#     # Format: flags (2 bytes), instantaneous power (2 bytes, little endian)
#     watts = int.from_bytes(data[2:4], byteorder="little", signed=True)
#     print(f"Power: {watts} W")

# def speed_handler(sender, data):
#     # CSC Measurement format:
#     # flags (1 byte)
#     flags = data[0]

#     wheel_rev_present = flags & 0x01

#     if wheel_rev_present:
#         # next fields:
#         # Cumulative Wheel Revolutions (4 bytes)
#         wheel_rev = int.from_bytes(data[1:5], byteorder="little")

#         # Last Wheel Event Time (2 bytes, 1/1024s units)
#         event_time = int.from_bytes(data[5:7], byteorder="little")

#         print(f"Speed-raw: rev={wheel_rev}, event={event_time}")

#     else:
#         print("Speed: wheel revolution data not present")

# async def main():
#     address = "7CA0DD25-9E34-CF6F-3230-683A4A8974CD"  # Your KICKR SNAP

#     print("Connecting to KICKR SNAP...")
#     async with BleakClient(address) as client:
#         print("Connected!")

#         services = client.services

#         # Determine which speed characteristic exists
#         if UUID_CSC_MEASUREMENT in [c.uuid for s in services for c in s.characteristics]:
#             speed_uuid = UUID_CSC_MEASUREMENT
#             print("Using CSC speed characteristic (0x2A5B)")
#         else:
#             speed_uuid = UUID_WAHOO_SPEED
#             print("Using Wahoo vendor speed UUID")

#         # Subscribe to notifications
#         await client.start_notify(UUID_CYCLING_POWER, power_handler)
#         await client.start_notify(speed_uuid, speed_handler)

#         print("Subscribed to power + speed. Listening...")

#         while True:
#             await asyncio.sleep(1)

# asyncio.run(main())

