from cobs import cobs
import serial
import time

filename = "can.pcad"

cfile = open(filename, "wb")

cfile.write(bytearray(b'\xd4\xc3\xb2\xa1'))
cfile.write(bytearray(b'\x02\x00\x04\x00'))
cfile.write(bytearray(b'\x00\x00\x00\x00'))
cfile.write(bytearray(b'\x00\x00\x00\x00'))
cfile.write(bytearray(b'\x00\x00\x04\x00'))
cfile.write(bytearray(b'\xe3\x00\x00\x00'))

def C_Init(port = "COM5", Br = 9600):
    global c_ser
    c_ser = serial.Serial(port, Br)
    c_ser.set_buffer_size(rx_size = 12800, tx_size = 12800)

def checkIntegrity(p):
    b = bytearray(p)
    if len(b) < 24:
        return False
    # incl_le and orig_len must be the same
    # they contain can packet length, not
    # the whole packet length which is longer
    incl_len = int.from_bytes(b[8:12], byteorder='little', signed=False)
    orig_len = int.from_bytes(b[12:16], byteorder='little', signed=False)
    l = int.from_bytes(b[20:21], byteorder='little', signed=False)
    print("incl_len: "+str(incl_len))
    print("length: "+str(l))
    print("pkg len: "+str(len(b)))
    #if len(b) < 24:
    #    return False
    #if incl_len != orig_len:
    #    return False
    #if len+8 != len(b):
    #    return False
    if 8+l != incl_len:
        print(l)
        return False
    return True

def findDelimiter(delimiter = 0x00):
    global c_ser
    value = c_ser.read(1)
    while value[0] != delimiter:
        value = c_ser.read(1)

C_Init("COM9", 115200)
timeout = 0
counter = 0
sani = 0

time.sleep(2)

findDelimiter()
print("\n\nInizio lettura")

while counter < 50:

    pacchetto = bytearray()

    value = c_ser.read(1)
    while value[0] != 0x00:
        pacchetto.append(value[0])
        value = c_ser.read(1)

    print("Lettura terminata")
    if len(pacchetto) > 2:
        dec = cobs.decode(pacchetto)
        if checkIntegrity(dec):
            sani+=1
            print("Pacchetto ##SANO##! n:" +str(sani))
            cfile.write(dec)
            print(dec[0:4].hex() + ' ' + dec[4:8].hex() + ' ' + dec[8:12].hex() + ' ' + dec[12:16].hex() + ' ' + dec[16:len(dec)].hex() )
        else:
            print("Pacchetto rotto!")
            print(pacchetto.hex())
            print(dec.hex())
    else:
        print("Lunghezza pacchetto inferiore a minima!")
    counter = counter + 1

cfile.close()