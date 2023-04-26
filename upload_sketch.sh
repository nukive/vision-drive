cd src/arduino

arduino-cli compile -b arduino:avr:uno driver_module
echo "Sketch compiled successfully !!!"

echo "Uploading sketch ..."

arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM0 driver_module
echo "Sketch uploaded to Arduino UNO successfully !!!"