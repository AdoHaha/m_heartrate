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

    uart.init(19200, rx = 0, tx = 26, timeout = 4000)
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


class BluetoothSender():
    new_data_Rri = False
    Rri = 0
    error = 0
    new_data_error = False
    def __init__(self):
            
            ble = bluetooth.BLE()
            self.uart_b = BLESimplePeripheral(ble)
            self.uart_b.on_write(self.nothing)
    def nothing(self,v):
        print(v)
    def raw_send(self, raw_bytes):
            try:
                if self.uart_b.is_connected():

                    self.uart_b.send(raw_bytes)
            except:
                pass
    def save_Rri(self,Rri):
        self.Rri = Rri
        self.new_data_Rri = True
    def save_error(self,error):
        self.error = error
        self.new_data_error = True
        
        
    def send_heartrate_packet(self,raw_data):
        """sends raw data with timestamp and Rri if it was available
        if new Rri is not available self.new_data will be set to 0
        """
        
        precise_time = get_time_ns()
 
        self.raw_send(struct.pack("QII",precise_time, self.new_data_Rri and self.Rri, self.new_data_error and self.error) + raw_data)
        self.new_data_Rri = False
        self.new_data_error = False
        
        
    def send_bluetooth(self,Rri,error):
       if self.uart_b.is_connected():
        #p.send("hello")
        try:
            #new_time = get_time_ns()
            precise_time = get_time_ns()
            

            #no_send = heart_signal >= 4096

            
            #if not no_send:
                #uart_b.send(struct.pack("QI",precise_time,heart_signal)) 
            self.uart_b.send(struct.pack("QIb",precise_time,Rri, int(error)))

            #old_time = new_time
            #old_heart_signal = heart_signal
        except Exception as e:
            #time.sleep(0.003)
            #try:
            #    uart_b.send(struct.pack("QI",precise_time,heart_signal))
            #except:
            #    pass
            print(e,"error",Rri,precise_time, error)
            #print(number)
            
       else:
            pass
            #print("not connected")
    

    

def main_program():
    error = False
    sweeppptr = 0
    uart = setup_heart_uart()
    ble_sender = BluetoothSender()
    
    
    from ulab import numpy as np
    
    
    framerate = 50
    all_readings = np.empty(framerate, dtype= np.uint16)
    
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
                        print("error case", number)
                        error_f = True
                        ble_sender.save_error(error_f)

                        continue
                    if number[1] == "-":
                        ble_sender.save_error(-1*int(number[1:]))

                        pass
                        #print("error")
                    else:
                        
                        simple_Rri = int(number[1:])
                        print(error)
                        #ble_sender.send_bluetooth(simple_Rri, error)
                        ble_sender.save_Rri(simple_Rri) # will save but not send the Rri, will be sent during the transfer of heartbyte data
                        print(simple_Rri)
                        #heartrate = 60000.0 / float(number[1:])

                else: #just the heartbyte
                    
                    all_readings[sweeppptr] = int(number)
                    sweeppptr +=1
                    
                    
                    #print(sweeppptr)
                    if (sweeppptr < framerate):
                        continue
                    else:
                        sweeppptr = 0
                        print(len(all_readings.tobytes()))
                        ble_sender.send_heartrate_packet(all_readings.tobytes())
                        #ble_sender.raw_send(all_readings.tobytes())

                        try:
                            
                            heart_signal = int(number)
                            
                            error =  heart_signal >= 4096 or heart_signal == 0 # have some measure of error
                            
                            #print(result)
                        except:
                            error = True
                            continue
                    

            except UnicodeError:
                print("UnicodeError")
                

main_program()
#except Exception as e:
#    print(e)
#   print("finished");

