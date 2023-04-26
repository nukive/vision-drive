cd src/arduino

arduino-cli compile -b arduino:avr:uno driver_module

arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM0 driver_module