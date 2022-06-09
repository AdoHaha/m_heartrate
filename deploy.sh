#ampy --port /dev/ttyUSB0 put ble_advertising.py ble_simple_peripheral.py main.py mpu6050.py touch_monitor.py uart_service.py

ESPPORT=${1-/dev/ttyUSB0}

ampy --port $ESPPORT put on_controller/bluetooth_simple
ampy --port $ESPPORT put on_controller/lib

for ff in on_controller/main.py on_controller/setup.py
do
    echo $ff
    ampy --port $ESPPORT put $ff

done 
