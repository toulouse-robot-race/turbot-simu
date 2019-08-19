from robot.Component import Component


class SteeringController(Component):
    TRIM_DIRECTION = 0

    duty_cycle_direction_neutre = 88.0  # PWM a envoyer au servo pour qu'il soit au neutre 88.0 lors des reglages preliminaires, baisser pour aller vers la gauche
    duty_cycle_debattement_direction = 35.0  # Debattement de direction (doit etre inferieur a duty_cycle_direction_neutre)
    echelle_debattement_direction = 100.0  # Direction max

    def __init__(self, arduino):
        self.arduino = arduino

    steering = 0

    previous_steering = 0

    def set_steering(self, steering):
        if not -100 < steering < 100:
            raise Exception("steering must be between -100 and 100, was ", steering)
        self.steering = steering

    def execute(self):
        if abs(self.previous_steering - self.steering) < 1:
            return

        # Applique une exponentielle
        sign = 1 if self.steering > 0 else -1
        direction = sign * (abs(self.steering) ** 0.7) * 4
        trim_pwm = (-self.TRIM_DIRECTION / self.echelle_debattement_direction) * self.duty_cycle_debattement_direction
        pwm_steering = int(((
                                    direction / self.echelle_debattement_direction) *
                            self.duty_cycle_debattement_direction) + trim_pwm + self.duty_cycle_direction_neutre)
        self.arduino.send_pwm(pwm_steering)

        self.previous_steering = pwm_steering
