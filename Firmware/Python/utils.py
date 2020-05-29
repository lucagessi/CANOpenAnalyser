import serial
import time

print("Utils...")

def C_Init(port = "COM5", Br = 9600):
    global c_ser
    c_ser = serial.Serial(port, Br)


def ConvertiQuota(qb):
    # qb è bytearray di 4 bytes. Primi due 0,1. Ultimi 2,3
    # Converto in big endian. Prima posizione byte più significativo
    quota = bytearray(qb[2:4]) + bytearray(qb[0:2])
    quota = int.from_bytes(quota, byteorder='big', signed=True) 
    return quota

def ConvertiStato(sb):
    # qb è bytearray di 4 bytes. Primi due 0,1. Ultimi 2,3
    stato = int.from_bytes(sb, byteorder='big', signed=False) 
    return stato

def

# Modo è il valore diretto da scrivere: 4 = MM, 5 = INCH, 6 = DEG
def ImpostaModoVisuale(stazione = 8, modo = 4):
    global w_ser

    stazione = (stazione << 4) & 0xFF
    pkg = bytearray()
    pkg.append(0x01)
    pkg.append(0x06)
    pkg.append(stazione)
    pkg.append(0x14) 
    pkg.append(0x00)
    pkg.append(modo & 0xFF)
    CRC = CRC16(pkg)
    pkg.append(CRC & 0xff)
    pkg.append((CRC >> 8) & 0xff)
    w_ser.write(pkg)
    timeout = 0
    while (w_ser.in_waiting < 8) and timeout < 20:
        time.sleep(0.1)
        timeout = timeout+1
    
    rec_pkg = w_ser.read( w_ser.in_waiting )

    if rec_pkg == pkg:
        return True
    else:
        return False

def ImpostaTuttiOffset(offset = 0):
    global w_ser
    offset = int(offset * 100)
    pkg = bytearray()
    pkg.append(0x01)
    pkg.append(0x06)
    pkg.append(0x80)
    pkg.append(0x00) 
    # Stazione 1
    pkg.append((offset >> 8) & 0xff)
    pkg.append(offset & 0xff)
    pkg.append((offset >> 24) & 0xff)
    pkg.append((offset >> 16) & 0xff)
    # Stazione 2
    pkg.append((offset >> 8) & 0xff)
    pkg.append(offset & 0xff)
    pkg.append((offset >> 24) & 0xff)
    pkg.append((offset >> 16) & 0xff)
    # Stazione 3
    pkg.append((offset >> 8) & 0xff)
    pkg.append(offset & 0xff)
    pkg.append((offset >> 24) & 0xff)
    pkg.append((offset >> 16) & 0xff)
    CRC = CRC16(pkg)
    pkg.append(CRC & 0xff)
    pkg.append((CRC >> 8) & 0xff)
    w_ser.write(pkg)
    timeout = 0
    while (w_ser.in_waiting < 18) and timeout < 20:
        time.sleep(0.1)
        timeout = timeout+1

    rec_pkg = w_ser.read( w_ser.in_waiting )

    if rec_pkg == pkg:
        print("Offeset OK!")
        return True
    else:
        print("Errore")
        return False

def LeggiTutteStazioni(info = True):
    global w_ser
    pkg = bytearray()
    pkg.append(0x01)
    pkg.append(0x03)
    pkg.append(0x80)
    pkg.append(0x00)
    pkg.append(0x90) 
    pkg.append(0x18)
    w_ser.write(pkg)
    timeout = 0
    while (w_ser.in_waiting < 29) and timeout < 20:
        time.sleep(0.1)
        timeout = timeout+1

    rec_pkg = w_ser.read( w_ser.in_waiting )

    CRC = CRC16(rec_pkg, len(rec_pkg)-2)
    rec_CRC = rec_pkg[len(rec_pkg)-2] ^ (rec_pkg[len(rec_pkg)-1]<<8)
    if rec_CRC == CRC:
        stato_1 = ConvertiStato(bytearray(rec_pkg[7:9]))
        quota_1 = ConvertiQuota(bytearray(rec_pkg[3:7]))
        quota_2 = ConvertiQuota(bytearray(rec_pkg[9:12]))
        stato_2 = ConvertiStato(bytearray(rec_pkg[13:15]))
        quota_3 = ConvertiQuota(bytearray(rec_pkg[15:19]))
        stato_3 = ConvertiStato(bytearray(rec_pkg[19:21]))
        quota_4 = ConvertiQuota(bytearray(rec_pkg[21:25]))
        stato_4 = ConvertiStato(bytearray(rec_pkg[25:27]))
        risultato = {
            "esito"     : True,
            "stazione_1": {"quota" : quota_1,"stato" : stato_1},
            "stazione_2": {"quota" : quota_2,"stato" : stato_2},
            "stazione_3": {"quota" : quota_3,"stato" : stato_3},
            "stazione_4": {"quota" : quota_4,"stato" : stato_4},
        }
        if info :
            print("Quota 1: " + str(quota_1 / 100))
            print("Stato 1: " + hex(stato_1))
            print("Quota 2: " + str(quota_2 / 100))
            print("Stato 2: " + hex(stato_2))
            print("Quota 3: " + str(quota_3 / 100))
            print("Stato 3: " + hex(stato_3))
            print("Quota 4: " + str(quota_4 / 100))
            print("Stato 4: " + hex(stato_4))

        return risultato
    else:
        print("Errore CRC!")
        risultato = {
            "esito"     : False
        }
        return risultato
    