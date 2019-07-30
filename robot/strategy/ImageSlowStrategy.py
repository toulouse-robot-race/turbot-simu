from robot.strategy.Strategy import Strategy


class ImageSlowStrategy(Strategy):

    # PID
    # Le coeff proportionnel reel depend de la vitesse
    COEFF_PROPORTIONNEL_POUR_VITESSE_NOMINALE = 0.3  # 0.3 lors des essais post TRR2017
    COEFF_PROPORTIONNEL_POUR_VITESSE_MIN = 2.0  # 2.0 lors des essais post TRR2017
    COEFF_PROPORTIONNEL_IMAGE_POUR_VITESSE_NOMINALE = 1.0  # 0.3 lors des essais post TRR2017
    COEFF_PROPORTIONNEL_IMAGE_POUR_VITESSE_MIN = 2.0  # 2.0 lors des essais post TRR2018
    VITESSE_NOMINALE = 100  # 45 lors des manches de la TRR2017 (surtout pas mettre 45, mettre la vitesse max utilisee, sinon le coeff prop peut devenir negatif ! Teste en 2017 apres la course, stable a vitesse 75.)
    VITESSE_MIN = 20  # 25 lors des manches de la TRR2017

    # PID suivi de ligne par analyse d'image
    COEFF_SUIVI_IMAGE_P1 = 150  # Coeff P pour l'ecart par rapport a la position de ligne au point 1 (point au loin)
    COEFF_SUIVI_IMAGE_P2 = 0  # Coeff P pour l'ecart par rapport a la position de ligne au point 2 (point proche)
    EXPONENTIELLE_P1_IMAGE = 1.0  # Coeff exponentiel pour accentuer le braquage lors des grands ecarts (point au loin)
    EXPONENTIELLE_P2_IMAGE = 1.0  # Coeff exponentiel pour accentuer le braquage lors des grands ecarts (point proche)
    EXPONENTIELLE_P_IMAGE = 1.0  # Coeff exponentiel a appliquer sur l'ecart de cap final pour accentuer le braquage lors des grands ecarts
    COEFF_SUIVI_IMAGE_COURBURE_P = 0  # 1000 # Coeff P pour le suivi de la courbure (coeff de degré 2 du polynome)
    MAX_SUIVI_COURBURE_P = 15  # Valeur max de braquage des roues a appliquer sur la base de la courbure
    COEFF_GLOBAL_ECART_IMAGE = 0.6  # Coeff a appliquer sur l'ecart total calcule a partir de l'image, afin d'obtenir une erreur de cap en degres
    OFFSET = 0  # TODO to remove (+60 pour rouler a doite, -20 pour rouler a gauche)

    def __init__(self, car, image_analyzer, vitesse):
        self.vitesse = vitesse
        self.car = car
        self.image_analyzer = image_analyzer

    def compute_steering(self):
        error_cap = self.compute_error_cap()
        return self.compute_steering(error_cap)

    def compute_error_cap(self):
        # N'execute le calcul que s'il y a une nouvelle image
        if self.image_analyzer.new_image_arrived:
            cap_actuel = self.car.get_cap()
            last_image_time = self.image_analyzer.last_execution_time

            # Calcule l'ecart de trajectoire par analyse d'image
            poly_coeff_square = self.image_analyzer.poly_coeff_square
            if poly_coeff_square is None:
                # TODO voir ce qu'il faut faire. En attendant on met a zero
                poly_coeff_square = 0
            position_ligne1 = self.image_analyzer.position_ligne_1
            position_ligne2 = self.image_analyzer.position_ligne_2
            # Calcule la position des roues
            braquage_courbure = min(self.MAX_SUIVI_COURBURE_P, max(-self.MAX_SUIVI_COURBURE_P,
                                                                   self.COEFF_SUIVI_IMAGE_COURBURE_P * poly_coeff_square))
            ecart_ligne1_fois_p = self.COEFF_SUIVI_IMAGE_P1 * position_ligne1
            ecart_ligne2_fois_p = self.COEFF_SUIVI_IMAGE_P2 * position_ligne2
            sign = lambda x: -1 if x < 0 else 1
            braquage_ecart_1 = sign(ecart_ligne1_fois_p) * abs(ecart_ligne1_fois_p) ** self.EXPONENTIELLE_P1_IMAGE
            braquage_ecart_2 = sign(ecart_ligne2_fois_p) * abs(ecart_ligne2_fois_p) ** self.EXPONENTIELLE_P2_IMAGE
            ecart_total = self.COEFF_GLOBAL_ECART_IMAGE * (braquage_courbure + braquage_ecart_1 + braquage_ecart_2)
            ecart_total = min(max(ecart_total, -90), 90)
            print(
                "Ecart total: {:.0f} Braquage courbure: {:.0f} Braquage ecart 1: {:.0f} Braquage ecart 2: {:.0f}".format(
                    ecart_total, braquage_courbure, braquage_ecart_1, braquage_ecart_2))

            capASuivre = cap_actuel + ecart_total
            self.lastCapASuivreForImageAnalysis = capASuivre

            elapsedSinceLastImageMs = int(self.car.get_time() - last_image_time * 1000)
            print(
                "Position lignes: {:.2f} {:.2f} cap_actuel: {:.0f} cap_a_suivre: {:.0f} Last image since: {:d}ms".format(
                    position_ligne1, position_ligne2, cap_actuel, capASuivre, elapsedSinceLastImageMs))

        else:
            capASuivre = self.lastCapASuivreForImageAnalysis

        return capASuivre

    def compute_steering(self, error_cap):
        # Si suivi image, on n'utilise pas les coeff integral et derivee
        self.cumulErreurCap = 0
        # On calcule le coeff P specifique pour le suivi d'image
        coeff_proportionnel = self.COEFF_PROPORTIONNEL_IMAGE_POUR_VITESSE_MIN + ((self.vitesse - self.VITESSE_MIN) * (
                self.COEFF_PROPORTIONNEL_IMAGE_POUR_VITESSE_NOMINALE - self.COEFF_PROPORTIONNEL_IMAGE_POUR_VITESSE_MIN) / (
                                                                                         self.VITESSE_NOMINALE - self.VITESSE_MIN))
        # Calcul de la position des roues
        sign = lambda x: -1 if x < 0 else 1
        ########## TODO remove Test offset
        offset = 0  # A mettre entre -15 et 20 environ
        positionRoues = min(
            max(int(-(coeff_proportionnel * (sign(error_cap) * abs(error_cap) ** self.EXPONENTIELLE_P_IMAGE))) + offset,
                -100), 100)
        return positionRoues
