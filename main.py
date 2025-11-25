import asyncio                      # Manage bluetoth notifications without blocking 
from bleak import BleakClient       # type: ignore # BLE client 
import struct                       # parse raw bytes into integers/floats using specified binary formats




DEVICE_ID = "7CA0DD25-9E34-CF6F-3230-683A4A8974CD"          # ID of device
CHAR_UUID = "00002A63-0000-1000-8000-00805f9b34fb"          # BLE characteristic UUID to subsribe to, 00002A63 is cycling power  
WHEEL_CIRCUMFERENCE = 2.105                         # Bike wheel circumference
prev_crank_revs = None
prev_crank_event_time = None
prev_wheel_revs = None
prev_wheel_event_time = None



def notification_handler(sender, data): # sender is characteristic handle/ID given by bleak, data is the raw bytes we get from the machine
    global prev_crank_revs, prev_crank_event_time, prev_wheel_revs, prev_wheel_event_time       # it will read and write variables in the global envs 

    # Convert to bytes for parsing
    b = bytearray(data)                                         # Convert the data we get from machine into bytearray meaning we can now index the bytes that the machine sends us 
    
    # Flags (2 bytes)
    flags = struct.unpack_from("<H", b, 0)[0]                   # Reads the first two bytes as an Unsigned 16-bit integer, a number stored in 16 bit format that is only positive, this value tell us what data is available in the data packet being sent by the machine 

    # Instantaneous power (2 bytes, signed)
    power_watts = struct.unpack_from("<h", b, 2)[0]             # Reads the next two bytes as Signed 16-bit integer, a number stored in 16 bit format that is positive or negative, the highest bit is the sign bit  

    offset = 4                                                  # This is to keep track where we are in the data string from the machine, we used 2 bits for flag and two for power_watts so we are now at 4 
    accumulated_torque = None                                   # set to none and only fills is the data is present 
    crank_revs = None
    last_crank_event_time = None
    cadence_rpm = None
    speed_kmh = None

    # Check for optional fields based on flags
    # if flags & 0x01:  # Pedal Power Balance present (skip for now)
    #     pedal_balance = struct.unpack_from("<B", b, offset)[0]
    #     offset += 1

    # if flags & 0x02:  # This checks if accumulated torque is present in the data, if yes it unpacks it and moves the offset up 2
    #     accumulated_torque = struct.unpack_from("<H", b, offset)[0] / 32.0  # Nm
    #     offset += 2

    if flags & 0x04:  # This checks if the wheel revolution data is present and if yes it unpacks it and moves the offest by 6
        wheel_revs, last_wheel_event_time = struct.unpack_from("<LH", b, offset)
        offset += 6
        
        # Calculate speed
        print("-" * 30)
        print(f'Prev_wheel_revs:{prev_wheel_revs}')
        print(f'prev_wheel_event_time:{prev_wheel_event_time}')
        print("-" * 15)
        print(f'wheel_revs:{wheel_revs}')
        print(f'last_wheel_event_time:{last_wheel_event_time}')
        print("-" * 30)
        print(prev_wheel_revs, prev_wheel_event_time)
        if prev_wheel_revs is not None and prev_wheel_event_time is not None:
            delta_revs = wheel_revs - prev_wheel_revs
            delta_time_sec = (last_wheel_event_time - prev_wheel_event_time) / 1024
            if delta_time_sec > 0:
                speed_m_s = (delta_revs * WHEEL_CIRCUMFERENCE) / delta_time_sec
                speed_kmh = speed_m_s * 3.6
        prev_wheel_revs = wheel_revs
        prev_wheel_event_time = last_wheel_event_time # i think because last_wheel_event_time is such a mslal time number that it rounds it to seconds and its alays 0 making the speed value error (divide by 0) and causing it not to display, my theory for now

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
    # print(f"Flags: {flags}")
    # print(f"Power (W): {power_watts}")
    # if accumulated_torque is not None:
    #     print(f"Torque (Nm): {accumulated_torque}")
    # if crank_revs is not None:
    #     print(f"Crank Revs: {crank_revs}")
    #     print(f"Last Crank Event Time: {last_crank_event_time}")
    # if cadence_rpm is not None:
    #     print(f"Cadence (RPM): {cadence_rpm:.2f}")
    # if wheel_revs is not None:
    #     print(f"Wheel Revs: {wheel_revs}")
    #     print(f"Last Wheel Event Time: {last_wheel_event_time}")
    # if speed_kmh is not None:
    #     print(f"Speed (km/h): {speed_kmh:.2f}")
    # print("-" * 30)


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




































# NOTIFICATION SENDER FUNCTION THAT ONLY SENDS THE RAW BYTES DATA STRING
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




