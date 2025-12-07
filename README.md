# freeride
An app to simulate indoor cylcing





NOTES






Now using tesseract for text recognizition of the bounding box info
I noticed powertoys has something that seems like it could do this  
    maybe that could be a better alternative - does it work on mac to?









Started using light blue to connect to BLE devices

This command made it so BLE devices are discoverable 
sudo pkill bluetoothd
Apparently its a Macos bluetooth daemon bug
Here is the chat gpt thread of me fixing it
https://chatgpt.com/c/692386a5-4288-832e-bfe8-40a6ead2446f


Light blue is saying this is my name and  UUID
KICKR SNAP B16C
7CA0DD25-9E34-CF6F-3230-683A4A8974CD


This is the output when I slowly sped up the power of the bike then stopped pedalling and let it go back down to normal
tom@thomass-MacBook-Pro freeride % python3 main.py
Trying to connect to KICKR SNAP...
Connected to KICKR SNAP!
Subscribed to notifications. Waiting for data...
bytearray(b'\x14\x00\x00\x00\x14\x95\xb3\x12\x00\x00\x0c\xc1')
bytearray(b'\x14\x00\x00\x00\x14\x95\xb4\x12\x00\x00\x18\xcd')
bytearray(b'\x14\x00\x00\x00\x14\x95\xb5\x12\x00\x00L\xd9')
bytearray(b'\x14\x00\x00\x00\x14\x95\xb5\x12\x00\x00L\xd9')
bytearray(b'\x14\x00\x00\x00\x14\x95\xb6\x12\x00\x009\xe5')
bytearray(b'\x14\x00\x00\x00\x14\x95\xb7\x12\x00\x00i\xf0')
bytearray(b'\x14\x00\x07\x00A\x95\xb8\x12\x00\x00m\xfa')
bytearray(b'\x14\x00\x14\x00\xb0\x95\xb9\x12\x00\x00\x1e\x03')
bytearray(b'\x14\x00#\x00c\x96\xba\x12\x00\x00)\x0b')
bytearray(b'\x14\x001\x00U\x97\xbb\x12\x00\x00\xe7\x12')
bytearray(b'\x14\x009\x00b\x98\xbc\x12\x00\x00N\x1a')
bytearray(b'\x14\x00=\x00q\x99\xbd\x12\x00\x00G!')
bytearray(b"\x14\x00@\x00\x81\x9a\xbe\x12\x00\x00\xf4\'")
bytearray(b'\x14\x00@\x00\x8d\x9b\xbf\x12\x00\x00\x85.')
bytearray(b'\x14\x006\x00v\x9d\xc1\x12\x00\x00\xc6;')
bytearray(b'\x14\x00$\x00\x1f\x9e\xc2\x12\x00\x00$C')
bytearray(b'\x14\x00\x16\x00\x91\x9e\xc3\x12\x00\x00CK')
bytearray(b'\x14\x00\x16\x00\x91\x9e\xc3\x12\x00\x00CK')
bytearray(b'\x14\x00\t\x00\xc5\x9e\xc4\x12\x00\x00HT')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc5\x12\x00\x00\x8b^')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc6\x12\x00\x00\xafj')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc6\x12\x00\x00\xafj')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc7\x12\x00\x00(z')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc7\x12\x00\x00(z')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc7\x12\x00\x00(z')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc8\x12\x00\x00\xd3\x92')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc8\x12\x00\x00\xd3\x92')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc8\x12\x00\x00\xd3\x92')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc8\x12\x00\x00\xd3\x92')
bytearray(b'\x14\x00\x00\x00\xc5\x9e\xc8\x12\x00\x00\xd3\x92')

Byte range	Field	Size	Notes
0–1	Flags	2 bytes	Bitmask describing which fields follow
2–3	Instantaneous Power	2 bytes (signed)	Watts
4–7	Cumulative Wheel Revolutions (optional)	4 bytes (uint32)	Only present if flag bit 2 (0x04) is set
8–9	Last Wheel Event Time (optional)	2 bytes (uint16)	Timestamp in 1/1024 seconds
10–11	Cumulative Crank Revolutions (optional)	2 bytes	Present only if flag bit 3 (0x08)
12–13	Last Crank Event Time (optional)	2 bytes	Only if flag bit 3 is set
