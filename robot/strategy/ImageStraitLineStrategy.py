from robot.strategy.Strategy import Strategy


class ImageStraitLineStrategy(Strategy):
    # Suivi image ligne droite
    COEFF_CAP_IMAGE_LIGNE_DROITE_P = 20
    COEFF_CAP_IMAGE_LIGNE_DROITE_I = 0.5
    MAX_ERREUR_FOR_CUMUL_POSITION_LIGNE = 0.5
    MAX_CUMUL_ERREUR_POSITION_LIGNE = 8.0
    MAX_CORRECTION_CAP_IMAGE_LIGNE_DROITE = 10.0

    def __init__(self, image_analyzer, cap_target, integral_enabled=False):
        self.integral_enabled = integral_enabled
        self.cap_target = cap_target
        self.image_analyzer = image_analyzer
        self.cumulErreurPositionLigne = 0.0
        self.lastCapASuivreForImageAnalysis = 0.0

    def compute_steering(self):
        # N'execute le calcul que s'il y a une nouvelle image
        if self.image_analyzer.new_image_arrived:

            # Initialise le cap a suivre en fonction de la cible fixee initialement
            capASuivre = self.cap_target

            # Recale le cap a suivre en fonction de l'erreur mesuree sur la ligne
            position_ligne1 = self.image_analyzer.position_ligne_1


            # Calcul de la correction proportionnelle
            if position_ligne1 is None:
                erreurDistance = 0
            else:
                erreurDistance = position_ligne1
            correctionProportionnelle = erreurDistance * self.COEFF_CAP_IMAGE_LIGNE_DROITE_P

            # Calcul de la correction integrale
            maxVal = self.MAX_ERREUR_FOR_CUMUL_POSITION_LIGNE
            self.cumulErreurPositionLigne += max(min(erreurDistance, maxVal),
                                                 -maxVal)  # Inutile de cumuler trop vite quand on est vraiment trop loin
            # Maintient le cumul des erreurs à une valeur raisonnable
            maxVal = self.MAX_CUMUL_ERREUR_POSITION_LIGNE
            self.cumulErreurPositionLigne = max(min(self.cumulErreurPositionLigne, maxVal), -maxVal)

            if self.integral_enabled:
                correctionIntegrale = self.cumulErreurPositionLigne * self.COEFF_CAP_IMAGE_LIGNE_DROITE_I
            else:
                correctionIntegrale = 0


            correctionCap = max(
                min(correctionProportionnelle + correctionIntegrale, self.MAX_CORRECTION_CAP_IMAGE_LIGNE_DROITE),
                -self.MAX_CORRECTION_CAP_IMAGE_LIGNE_DROITE)
            capASuivre = (capASuivre + correctionCap) % 360

            self.lastCapASuivreForImageAnalysis = capASuivre

        else:
            capASuivre = self.lastCapASuivreForImageAnalysis

        return capASuivre
