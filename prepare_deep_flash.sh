ESPPORT=${1-/dev/ttyUSB0}

esptool.py --port $ESPPORT erase_flash
esptool.py -p $ESPPORT -b 115200 --before default_reset --after hard_reset --chip esp32 write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 deep_system/bootloader/bootloader.bin 0x8000 deep_system/partition_table/partition-table.bin 0x10000 deep_system/micropython.bin

#./deploy.sh $ESPPORT
