import pyvesc
import serial as serial

BRAKE_CURRENT = 15000


class Vesc:

    def __init__(self, serial_device: str, enabled=True):
        self.enabled = enabled
        if enabled:
            self.serial = serial.Serial(serial_device, baudrate=115200, timeout=0.05)

    tachometer = 0

    rpm = 0

    # Send speed command to VESC
    def send_speed_command(self, speed):
        if not self.enabled:
            return

            # noinspection PyArgumentList
        msg = pyvesc.SetDutyCycle(int(speed))
        packet = pyvesc.encode(msg)
        self.serial.write(packet)

    # Send brake commande to VESC
    def send_brake_command(self):
        if not self.enabled:
            return

            # noinspection PyArgumentList
        msg = pyvesc.SetCurrentBrake(BRAKE_CURRENT)
        packet = pyvesc.encode(msg)
        self.serial.write(packet)

    def request_data(self):
        if not self.enabled:
            return [0,0]

        # Request data from VESC
        self.serial.write(pyvesc.encode_request(pyvesc.GetValues))

        # Check if new data has been received from VESC
        if self.serial.in_waiting > 61:
            (response, consumed) = pyvesc.decode(self.serial.read(61))

            if response is not None:
                for sensor, value in response.__dict__.items():
                    if sensor == 'tachometer':
                        self.tachometer = value
                    if sensor == 'rpm':
                        self.rpm = value

        return self.tachometer, self.rpm
