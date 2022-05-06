import bluetooth
from bluetooth_simple.ble_simple_peripheral import *

import machine

#from m5stack import *

#lcd.clear(lcd.BLACK)
#lcd.text(lcd.CENTER, lcd.CENTER, 'user app')


def setup_heart_uart():
    # Set uart port and tx rx
    uart = machine.UART(1)

    # Set part baud and data bits, Parity bits, stop bits
    #uart.init(19200, tx= 0,rx = 26)#, bits, parity, stop)

    uart.init(19200, rx = 0, tx = 26)
    uart_out_buf = bytearray(1)
    uart.write("@OF30")
    uart_out_buf = 0x0a
    uart.write(b'\x0a')
    uart.write("@RG2")
    uart_out_buf = 0x0a
    uart.write(b'\x0a')
    
    
    return uart
def internet_set_time():
    try:    
        import usocket as socket
    except:
        import socket
    try:
        import ustruct as struct
    except:
        import struct

    # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
    NTP_DELTA = 3155673600

    # The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
    host = "pool.ntp.org"

    print("setting up time")
    
    
    def time():
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        addr = socket.getaddrinfo(host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(1)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
        finally:
            s.close()
        val = struct.unpack("!I", msg[40:44])[0]
        return val - NTP_DELTA


    # There's currently no timezone support in MicroPython, and the RTC is set in UTC time.
    
    
    def settime():
        t = time()
        import machine
        import utime

        tm = utime.gmtime(t)
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
        print(machine.RTC().datetime())
    settime()
    
    
def connect_internet_set_time(network_name = "igor_test",password = "mywifikey"):
    import network
    from network import WLAN
    wlan = WLAN(network.STA_IF)
    wlan.active(True)   
    nets = wlan.scan()


    if not wlan.isconnected():
        print(nets)

        for net in nets:

            if net[0].decode() == network_name:
                print('Network found!')
                wlan.connect(net[0].decode(),  password)
                while not wlan.isconnected():
                    machine.idle() # save power while waiting
                print('WLAN connection succeeded!')


                break
    try:
        internet_set_time()
    except:
        "could not set time"

import time        
        
def get_time_ns():
    return time.time_ns()



### import bluetooth
from bluetooth_simple.ble_simple_peripheral import *

import struct
def make_heartrate_frame(heartrate):
    precise_time = get_time_ns()
    packed = struct.pack("II",precise_time,heartrate)
    return packed


def main_program():
    sweeppptr = 0
    uart = setup_heart_uart()
    ble = bluetooth.BLE()
    uart_b = BLESimplePeripheral(ble)
    try:
        connect_internet_set_time()
    except:
        pass
    old_time = get_time_ns()
    
    nN = 0
    old_heart_signal = 0
    no_send = False
    while True:
        result = uart.readline()
        nN += 1
        if result:
            try:
                number = result.decode().strip()
                
                if len(number) == 0:
                    continue
                
                #if nN%10 == 0:
                
                        
                if number[0] == "#": #special case
                    #print(result)
                    if len(number) <2:
                        print("error case")
                        continue
                    if number[1] == "-":
                        pass
                        #print("error")
                    else:
                        heartrate = 60000.0 / float(number[1:])

                else: #just the heartbyte
                    sweeppptr +=1
                    #print(sweeppptr)
                    if (sweeppptr < 8):
                        continue
                    else:
                        sweeppptr = 0
                    try:
                    
                        heart_signal = int(number)
                        print(heart_signal)
                    except:
                        continue
                    

                    if uart_b.is_connected():
                        #p.send("hello")
                        try:
                            new_time = get_time_ns()
                            precise_time = get_time_ns()
                            

                            no_send = heart_signal >= 4096

                            
                            if not no_send:
                                #uart_b.send(struct.pack("QI",precise_time,heart_signal))
                                uart_b.send(struct.pack("QI",precise_time,heart_signal))

                            old_time = new_time
                            old_heart_signal = heart_signal
                        except Exception as e:
                            time.sleep(0.003)
                            try:
                                uart_b.send(struct.pack("QI",precise_time,heart_signal))
                            except:
                                pass
                            print(e,"error",heart_signal,precise_time)
                            #print(number)
                            
                    else:
                        pass
                        #print("not connected")
                    
            except UnicodeError:
                print("UnicodeError")
                

main_program()
#except Exception as e:
#    print(e)
#   print("finished");

