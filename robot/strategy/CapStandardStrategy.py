from robot.strategy.Strategy import Strategy



class CapStandardStrategy(Strategy):
    # Le coeff proportionnel reel depend de la speed
    COEFF_PROPORTIONNEL_POUR_VITESSE_NOMINALE = 1.0  # 0.3 lors des essais post TRR2017
    COEFF_PROPORTIONNEL_POUR_VITESSE_MIN = 2.0  # 2.0 lors des essais post TRR2017
    COEFF_PROPORTIONNEL_IMAGE_POUR_VITESSE_NOMINALE = 1.0  # 0.3 lors des essais post TRR2017
    COEFF_PROPORTIONNEL_IMAGE_POUR_VITESSE_MIN = 2.0  # 2.0 lors des essais post TRR2018
    VITESSE_NOMINALE = 75  # 45 lors des manches de la TRR2017 (surtout pas mettre 45, mettre la speed max utilisee, sinon le coeff prop peut devenir negatif ! Teste en 2017 apres la course, stable a speed 75)
    VITESSE_MIN = 20  # 25 lors des manches de la TRR2017

    COEFF_INTEGRAL = 0.032  # 0.064 lors des essais de la veille TRR2017
    COEFF_AMORTISSEMENT_INTEGRAL = 1.0  # Attention, c'est l'amortissement. Inutilise.
    COEFF_DERIVEE = 3.9
    MAX_CUMUL_ERREUR_CAP = 200  # Cumul max des erreurs de cap pour le calcul integral (en degres)

    # PID suivi de bordure

    def __init__(self, car, cap_target, speed):
        self.speed = speed
        self.car = car
        self.cap_target = cap_target
        self.cumul_error_cap = 0.0
        self.last_error_cap = 0.0

    def compute_steering(self):
        error_cap = (((self.car.get_cap() - self.cap_target) + 180) % 360) - 180
        # Si pas suivi image, on calcule les termes integral et derivee
        self.cumul_error_cap = (self.cumul_error_cap / self.COEFF_AMORTISSEMENT_INTEGRAL) + error_cap
        # Maintient le cumul des erreurs à une valeur raisonnable
        self.cumul_error_cap = max(min(self.cumul_error_cap, self.MAX_CUMUL_ERREUR_CAP), -self.MAX_CUMUL_ERREUR_CAP)
        # Calcul de D
        correction_derivee = -self.COEFF_DERIVEE * (error_cap - self.last_error_cap)
        self.last_error_cap = error_cap
        # Calcul de P
        coeff_proportionnel = self.COEFF_PROPORTIONNEL_POUR_VITESSE_MIN + ((self.speed - self.VITESSE_MIN) * (
                self.COEFF_PROPORTIONNEL_POUR_VITESSE_NOMINALE - self.COEFF_PROPORTIONNEL_POUR_VITESSE_MIN) / (
                                                                                   self.VITESSE_NOMINALE - self.VITESSE_MIN))

        # Calcul de la position des roues
        steering = min(max(
            int(-(coeff_proportionnel * error_cap) - (self.COEFF_INTEGRAL * self.cumul_error_cap) + correction_derivee),
            -100), 100)
        return steering
