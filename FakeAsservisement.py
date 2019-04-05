# encoding:utf-8

import logging

logger = logging.getLogger('mainLogger')
paramLogger = logging.getLogger('csvFile')


class Asservissement:
    # PID
    # Le coeff proportionnel reel depend de la vitesse
    COEFF_PROPORTIONNEL_POUR_VITESSE_NOMINALE = 0.3  # 0.3 lors des essais post TRR2017
    COEFF_PROPORTIONNEL_POUR_VITESSE_MIN = 2.0  # 2.0 lors des essais post TRR2017
    COEFF_PROPORTIONNEL_IMAGE_POUR_VITESSE_NOMINALE = 1.0  # 0.3 lors des essais post TRR2017
    COEFF_PROPORTIONNEL_IMAGE_POUR_VITESSE_MIN = 2.0  # 2.0 lors des essais post TRR2018
    VITESSE_NOMINALE = 75  # 45 lors des manches de la TRR2017 (surtout pas mettre 45, mettre la vitesse max utilisee, sinon le coeff prop peut devenir negatif ! Teste en 2017 apres la course, stable a vitesse 75)
    VITESSE_MIN = 20  # 25 lors des manches de la TRR2017
    # ***********************
    # TODO MODIFIE POUR TESTS, mise a zero des coeff integral et derivee
    # ***********************
    # COEFF_INTEGRAL = 0.0
    # COEFF_DERIVEE  = 0.0
    COEFF_INTEGRAL = 0.032  # 0.064 lors des essais de la veille TRR2017
    COEFF_AMORTISSEMENT_INTEGRAL = 1.0  # Attention, c'est l'amortissement. Inutilise.
    COEFF_DERIVEE = 3.9
    MAX_CUMUL_ERREUR_CAP = 200  # Cumul max des erreurs de cap pour le calcul integral (en degres)

    # PID suivi de bordure au telemetre
    COEFF_SUIVI_LIGNE_P = 0.13
    AMPLIFICATEUR_P_ANTI_PROCHE = 3  # Coeff multiplicateur pour P quand on est en mode anti proche
    COEFF_SUIVI_LIGNE_I = 0.1 * COEFF_SUIVI_LIGNE_P
    MAX_CUMUL_ERREUR_DISTANCE = 4 / COEFF_SUIVI_LIGNE_I  # Cumul max des erreurs de distance pour le calcul integral (en cm), avec N/COEFF_I, N est en degres (correction max I)
    MAX_CORRECTION_CAP_TELEMETRE = 10  # Correction de cap maxi lors du suivi de bordure au telemetre (en degres)

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

    # Autres constantes
    DELTA_T_SUIVI_COURBES = 0.1
    COEFF_DERIVEE_TELEMETRE_COURBES = 0.8
    COEFF_ERREUR_TELEMETRE_COURBES = 0.5

    arduino = None
    voiture = None
    imageAnalysis = None
    time = None
    capTarget = 0.0
    ligneDroite = False
    ligneDroiteTelemetre = False
    activationDistanceIntegrale = False
    suiviImage = False
    antiProche = False
    recalageAutoCap = False
    suiviCourbesTelemetre = False
    distance_ligne_droite_telemetre = 40
    distance_courbes_telemetre = 40
    vitesse = 0
    calculCapSuiviCourbesEnCours = False
    timeLastCalculSuiviCourbe = None
    mesureTelemetrePourSuiviCourbe = 0.0
    lastCapASuivrePourSuiviCourbe = 0.0
    capTargetSuiviCourbe = 0.0
    lastErreurCap = 0.0
    lastCapASuivreForImageAnalysis = 0.0
    currentOffset = 0.0  # Offset actuel, doit tendre progressivement vers l'offset voulu
    marche_arriere_en_cours = 0  # Indique si une marche arriere est en cours, et a quelle sequence on en est
    tacho_marche_arriere = 0  # Memorise le tacho pour la marche arriere
    obstacleEnabled = True

    cumulErreurCap = 0.0
    cumulErreurDistanceBordure = 0.0

    def __init__(self, arduino, voiture, imageAnalysis, time):
        self.arduino = arduino
        self.voiture = voiture
        self.imageAnalysis = imageAnalysis
        self.time = time
        self.timeLastCalculSuiviCourbe = time.time()

        # A appeler lorsqu'on demarre un asservissement de ligne droite

    def initLigneDroite(self):
        self.ligneDroite = True
        self.ligneDroiteTelemetre = False
        self.suiviCourbesTelemetre = False
        self.suiviImage = False
        self.suiviImageCap = False
        self.suiviImageLigneDroite = False
        self.suiviImageRoues = False
        self.recalageAutoCap = False
        self.cumulErreurCap = 0

        # A appeler lorsqu'on demarre un asservissement de ligne droite au telemetre
        # recalageCap indique si on doit recaler automatiquement le cap

    def initLigneDroiteTelemetre(self, distance, recalageCap, activationDistanceIntegrale, antiProche):
        self.ligneDroite = True
        self.ligneDroiteTelemetre = True
        self.suiviCourbesTelemetre = False
        self.suiviImage = False
        self.recalageAutoCap = recalageCap
        self.distance_ligne_droite_telemetre = distance
        self.cumulErreurCap = 0.0
        self.cumulErreurDistanceBordure = 0.0
        self.activationDistanceIntegrale = activationDistanceIntegrale
        self.antiProche = antiProche

        # A appeler lorsqu'on demarre un asservissement de suivi de ligne par reconnaissance d'image (strategie cap)

    def initSuiviImageCap(self):
        self.ligneDroite = False
        self.ligneDroiteTelemetre = False
        self.suiviCourbesTelemetre = False
        self.suiviImage = True
        self.suiviImageCap = True
        self.suiviImageRoues = False
        self.suiviImageLigneDroite = False
        self.recalageAutoCap = False
        self.cumulErreurCap = 0.0
        self.cumulErreurDistanceBordure = 0.0
        self.activationDistanceIntegrale = False
        self.antiProche = False

        # A appeler lorsqu'on demarre un asservissement de suivi de ligne par reconnaissance d'image (strategie position roues)

    def initSuiviImageRoues(self, offset=0.0):
        self.ligneDroite = False
        self.ligneDroiteTelemetre = False
        self.suiviCourbesTelemetre = False
        self.suiviImage = True
        self.suiviImageCap = False
        self.suiviImageRoues = True
        self.suiviImageLigneDroite = False
        self.recalageAutoCap = False
        self.offset = offset
        self.offset_hors_evitement = offset
        self.cumulErreurPositionLigne = 0.0
        self.cumulErreurCap = 0.0
        self.cumulErreurBraquage = 0.0
        self.cumulErreurDistanceBordure = 0.0
        self.activationDistanceIntegrale = False
        self.antiProche = False
        self.obstacleEnabled = True
        self.vitesseEvitement = None
        self.offset_progressif = False
        self.last_position_obstacle = 0
        self.marche_arriere_en_cours = 0
        self.tacho_marche_arriere = 0
        self.cote_marche_arriere = 0

        # A appeler lorsqu'on demarre un asservissement de suivi de ligne par reconnaissance d'image (strategie ligne droite)

    def initSuiviImageLigneDroite(self, activationDistanceIntegrale):
        self.ligneDroite = False
        self.ligneDroiteTelemetre = False
        self.suiviCourbesTelemetre = False
        self.suiviImage = True
        self.suiviImageCap = False
        self.suiviImageRoues = False
        self.suiviImageLigneDroite = True
        self.recalageAutoCap = False
        self.cumulErreurPositionLigne = 0.0
        self.cumulErreurCap = 0.0
        self.cumulErreurPositionLigne = 0.0
        self.cumulErreurDistanceBordure = 0.0
        self.activationDistanceIntegrale = activationDistanceIntegrale
        self.antiProche = False

        # A appeler lorsqu'on demarre un asservissement de courbe au telemetre

    def initCourbeTelemetre(self, distance):
        self.ligneDroite = False
        self.ligneDroiteTelemetre = False
        self.suiviCourbesTelemetre = True
        self.suiviImage = False
        self.distance_courbes_telemetre = distance
        self.calculCapSuiviCourbesEnCours = False
        self.cumulErreurCap = 0.0
        self.cumulErreurDistanceBordure = 0.0

        # A appeler lorsqu'on modifie la vitesse (permet au coefficient P d'etre plus eleve quand on roule moins vite)

    def setVitesse(self, vitesse):
        self.vitesse = vitesse

        # A appeler lorsqu'on veut fixer une vitesse d'evitement d'obstacle plus faible que la vitesse standard

    def setVitesseEvitement(self, vitesseEvitement):
        self.vitesseEvitement = vitesseEvitement

        # A appeler lorsqu'on demarre un asservissement autre que la ligne droite

    def annuleLigneDroite(self):
        self.ligneDroite = False
        self.ligneDroiteTelemetre = False
        self.recalageAutoCap = False

        # Definit le cap a suivre au cap courant

    def setCapTarget(self):
        target = self.arduino.getCap()
        print ('Cap Target : ', target)
        self.capTarget = target

        # Ajoute deltaCap au cap a suivre

    def ajouteCap(self, deltaCap):
        self.capTarget = (self.capTarget + deltaCap) % 360
        print ("Nouveau cap : ", self.capTarget)

        # Verifie si le cap est compris entre capTarget+capFinalMini et capTarget+capFinalMaxi

    def checkDeltaCapAtteint(self, capFinalMini, capFinalMaxi):
        absoluteCapMini = (self.capTarget + capFinalMini) % 360
        absoluteCapMaxi = (self.capTarget + capFinalMaxi) % 360

        ecartCapMini = (((self.arduino.getCap() - absoluteCapMini) + 180) % 360) - 180
        ecartCapMaxi = (((self.arduino.getCap() - absoluteCapMaxi) + 180) % 360) - 180

        if (ecartCapMini > 0 and ecartCapMaxi < 0):
            print ("--------------- Fin de virage ----------------")
            print ("CapTarget : ", self.capTarget, "Cap : ", self.arduino.getCap(), " Ecart cap mini : ", ecartCapMini,
                   " Ecart cap maxi : ", ecartCapMaxi)
            print ("----------------------------------------------")

        return (ecartCapMini > 0 and ecartCapMaxi < 0)

        # Execute l'asservissement

    def execute(self):

        arduino = self.arduino
        # On n'execute que s'il y a une nouvelle donnee gyro ou une nouvelle image en mode suiviImage
        if arduino.nouvelleDonneeGyro or (self.suiviImage and self.imageAnalysis.new_image_arrived):


            capASuivre = 0.0
            positionRoues = 0

            # Si on doit asservir selon la ligne droite ou faire un suivi par analyse d'image
            if self.ligneDroite or self.suiviCourbesTelemetre or self.suiviImage:

                ####################################
                # LIGNE DROITE : calcul cap a suivre
                ####################################
                if self.ligneDroite:
                    capASuivre = self.capTarget

                ##############################################
                # LIGNE DROITE TELEMETRE : calcul cap a suivre
                ##############################################
                if self.ligneDroiteTelemetre:
                    capASuivre, autoriseRecalage = self.calculeCapASuivreLigneDroiteTelemetre()

                    # Execute le calcul de la derive du cap si c'est demande
                    if self.recalageAutoCap and autoriseRecalage:
                        arduino.executeRecalageCap(self.capTarget)

                    # print ("bestTelemetre: ", arduino.bestTelemetre, "Telemetre1: ", arduino.telemetre1, " TelemetreIR: ", arduino.telemetreIR)
                    # print ("bestTelemetrePourDetectionVirage: ", arduino.bestTelemetrePourDetectionVirage())
                    # print ("Cap Target : ", self.capTarget, " Cap A suivre : ", capASuivre)

                # Si on doit suivre les courbes selon le telemetre (inutilise, TODO a supprimer)
                elif self.suiviCourbesTelemetre:
                    capASuivre = self.calculeCapSuiviCourbes()

                ########################################
                # SUIVI IMAGE LENT : calcul cap a suivre
                ########################################
                elif self.suiviImageCap:
                    capASuivre = self.calculeCapSuiviImageLent()

                elif self.suiviImageLigneDroite:
                    capASuivre = self.calculeCapSuiviImageLigneDroite()

                ###############################
                # Calcule la position des roues
                ###############################

                if self.suiviImageRoues:
                    print("suivi image roues")
                    # Si suivi image sans cap (asservissement direct des roues)
                    positionRoues, nouvellePositionRoues = self.calculePositionRouesFromImage()
                else:
                    nouvellePositionRoues = True
                    erreurCap = (((arduino.getCap() - capASuivre) + 180) % 360) - 180
                    print ("Erreur cap : ", erreurCap)

                    if self.suiviImageCap:
                        # Si suivi image lent
                        positionRoues = self.calculePositionRouesFromCapForSuiviImageLent(erreurCap)

                    else:
                        # Si pas suivi image lent, on calcule le PID roues avec les termes integral et derivee
                        positionRoues = self.calculePositionRouesFromCapStandard(erreurCap)

                # Envoi de la position des roues au servo
                if nouvellePositionRoues:
                    print ("Position roues : {:.0f}".format(positionRoues))
                    self.voiture.tourne(positionRoues)

                # Loggue cap, cap corrige, roulis, tangage, telemetre, instruction==ligne droite, instruction==ligne droite telemetre, cap Target, cap a suivre (apres correction telemetre), positionRoues
                # paramLogger.info(str(arduino.gyroX) + ',' + str(arduino.getCap()) + ',' + str(arduino.gyroY) + ',' + str(arduino.gyroZ) + ',' + str(arduino.telemetre1) + ',' + str(self.ligneDroite) + ',' + str(self.ligneDroiteTelemetre) + ',' + str(self.capTarget) + ',' + str(capASuivre) + ',' + str(positionRoues) + ',' + str(arduino.telemetreIR) + ',' + str(arduino.telemetreLidar) + ',' + str(arduino.bestTelemetrePourSuiviBordure()) + ',' + str(arduino.bestTelemetrePourDetectionVirage()))

                # Before logging, check if suivi_image vars exist, otherwise set them to None
                try:
                    braquage_courbure
                except NameError:
                    braquage_courbure = None
                    braquage_ecart_1 = None
                    braquage_ecart_2 = None
                    ecart_total = None
                    last_image_time = None
                paramLogger.info(str(arduino.getCap()) + ',' + str(self.ligneDroite) + ',' + str(
                    self.ligneDroiteTelemetre) + ',' + str(self.suiviImage) + ',' + str(self.capTarget) + ',' + str(
                    capASuivre) + ',' + str(positionRoues) + ',' + str(braquage_courbure) + ',' + str(
                    braquage_ecart_1) + ',' + str(braquage_ecart_2) + ',' + str(last_image_time) + ',' + str(
                    self.currentOffset))

        if arduino.nouvelleDonneeTelemetre1:
            # Loggue cap, cap corrige, roulis, tangage, telemetre, instruction==ligne droite, instruction==ligne droite telemetre, cap Target, cap a suivre (apres correction telemetre), positionRoues
            # paramLogger.info(str(arduino.gyroX) + ',' + str(arduino.getCap()) + ',' + str(arduino.gyroY) + ',' + str(arduino.gyroZ) + ',' + str(arduino.telemetre1) + ',' + str(self.ligneDroite) + ',' + str(self.ligneDroiteTelemetre) + ',' + str(self.capTarget) + ',' + '' + ',' + '' + ',' + str(arduino.telemetreIR) + ',' + str(arduino.telemetreLidar)  + ',' + str(arduino.bestTelemetrePourSuiviBordure()) + ',' + str(arduino.bestTelemetrePourDetectionVirage()))
            arduino.nouvelleDonneeTelemetre1 = False
            # print "Telemetre1 : ", "{:4.1f}".format(self.arduino.telemetre1), " TelemetreIR : ", "{:4.1f}".format(self.arduino.telemetreIR), " Lidar : ", self.arduino.telemetreLidar, " Best: ", self.arduino.bestTelemetre
            # print "functionBest : ", "{:4.1f}".format(self.arduino.bestTelemetrePourSuiviBordure()), " TelemetreIR : ", "{:4.1f}".format(self.arduino.telemetreIR), " Lidar : ", self.arduino.telemetreLidar, " Best: ", self.arduino.bestTelemetre
            # print "bestForVirage : ", "{:4.1f}".format(self.arduino.bestTelemetrePourDetectionVirage())

    def calculeCapSuiviImageLigneDroite(self):

        self.COEFF_CAP_IMAGE_LIGNE_DROITE_P = 20
        self.COEFF_CAP_IMAGE_LIGNE_DROITE_I = 0.5
        self.MAX_ERREUR_FOR_CUMUL_POSITION_LIGNE = 0.5
        self.MAX_CUMUL_ERREUR_POSITION_LIGNE = 8.0
        self.MAX_CORRECTION_CAP_IMAGE_LIGNE_DROITE = 10.0

        # N'execute le calcul que s'il y a une nouvelle image
        if self.imageAnalysis.isThereANewImage():

            # Initialise le cap a suivre en fonction de la cible fixee initialement
            capASuivre = self.capTarget

            # Recale le cap a suivre en fonction de l'erreur mesuree sur la ligne
            position_ligne1 = self.imageAnalysis.getPositionLigne1()
            # position_ligne2 = self.imageAnalysis.getPositionLigne2()

            print("Position ligne: ", position_ligne1)

            # Calcul de la correction proportionnelle
            if position_ligne1 is None:
                erreurDistance = 0
            else:
                erreurDistance = position_ligne1
            correctionProportionnelle = erreurDistance * self.COEFF_CAP_IMAGE_LIGNE_DROITE_P
            print("Correction Proportionnelle: ", correctionProportionnelle)

            # Calcul de la correction integrale
            maxVal = self.MAX_ERREUR_FOR_CUMUL_POSITION_LIGNE
            self.cumulErreurPositionLigne += max(min(erreurDistance, maxVal),
                                                 -maxVal)  # Inutile de cumuler trop vite quand on est vraiment trop loin
            # Maintient le cumul des erreurs à une valeur raisonnable
            maxVal = self.MAX_CUMUL_ERREUR_POSITION_LIGNE
            self.cumulErreurPositionLigne = max(min(self.cumulErreurPositionLigne, maxVal), -maxVal)

            print ("Cumul erreur distance: ", self.cumulErreurPositionLigne)
            if self.activationDistanceIntegrale:
                correctionIntegrale = self.cumulErreurPositionLigne * self.COEFF_CAP_IMAGE_LIGNE_DROITE_I
            else:
                correctionIntegrale = 0

            print("Correction integrale: ", correctionIntegrale)

            correctionCap = max(
                min(correctionProportionnelle + correctionIntegrale, self.MAX_CORRECTION_CAP_IMAGE_LIGNE_DROITE),
                -self.MAX_CORRECTION_CAP_IMAGE_LIGNE_DROITE)
            capASuivre = (capASuivre + correctionCap) % 360

            self.lastCapASuivreForImageAnalysis = capASuivre

        else:
            capASuivre = self.lastCapASuivreForImageAnalysis

        return capASuivre

    def calculePositionRouesFromImage(self):

        self.COEFF_SUIVI_IMAGE_PARALLELISME_P_SPEED = 50  # VITESSE RAPIDE : Coeff P pour le suivi du parallelisme
        self.COEFF_SUIVI_IMAGE_ROUES_P2_SPEED = 25  # VITESSE RAPIDE : Coeff P pour l'ecart par rapport a la position de ligne au point 2 (point proche)
        self.COEFF_SUIVI_IMAGE_ROUES_I2_SPEED = 1.5  # VITESSE RAPIDE : Coeff I pour l'ecart par rapport a la position de la ligne au point 2 (point proche)
        self.COEFF_SUIVI_IMAGE_PARALLELISME_P_EVITEMENT = 60  # EVITEMENT : Coeff P pour le suivi du parallelisme
        self.COEFF_SUIVI_IMAGE_ROUES_P2_EVITEMENT = 70  # EVITEMENT : Coeff P pour l'ecart par rapport a la position de ligne au point 2 (point proche)
        self.COEFF_SUIVI_IMAGE_ROUES_I2_EVITEMENT = 1.5  # EVITEMENT : Coeff I pour l'ecart par rapport a la position de la ligne au point 2 (point proche)
        self.COEFF_SUIVI_IMAGES_ROUES_MAX_ERREUR_I = 6.0  # Max cumul ecart ligne pour l'asservissement integral
        self.OFFSET_ECART_DROITE = 1.0  # Offset a appliquer pour s'ecarter a droite
        self.OFFSET_ECART_GAUCHE = -1.0  # Offset a appliquer pour s'ecarter a gauche
        self.TACHO_MARCHE_ARRIERE_1 = 50  # Nombre de tours de tacho pour 1ere sequence de marche arriere evitement
        self.TACHO_MARCHE_ARRIERE_2 = 70  # Nombre de tours de tacho pour 1ere sequence de marche arriere evitement

        # Si on a une sequence de marche arriere en cours
        if self.marche_arriere_en_cours > 0:
            # Initialise les variables de retour
            position_roues = None
            nouvellePositionRoues = False

            # Si on est en train de freiner
            if self.marche_arriere_en_cours == 1:
                self.voiture.freine()
                # Verifie si la voiture est immobile
                if self.voiture.estImmobile():
                    # Memorise le tacho
                    self.tacho_marche_arriere = self.voiture.speedController.get_tacho()
                    # Tourne les roues du bon cote
                    position_roues = -0 if self.cote_marche_arriere > 0 else 0
                    nouvellePositionRoues = True
                    # Passe a la sequence suivante
                    self.marche_arriere_en_cours = 2
                    print ("Arret termine, enclenchement marche arriere, tacho: ", self.tacho_marche_arriere)

            # Si on est en train de reculer, sequence 1
            if self.marche_arriere_en_cours == 2:
                print("En cours de marche arriere branche 1")
                print("RPM: ", self.voiture.speedController.rpm)
                # Marche arriere
                self.voiture.reverse()
                # Verifie si on a assez recule
                print(self.tacho_marche_arriere - self.voiture.speedController.get_tacho())
                if self.tacho_marche_arriere - self.voiture.speedController.get_tacho() > self.TACHO_MARCHE_ARRIERE_2:
                    # Memorise le tacho
                    self.tacho_marche_arriere = self.voiture.speedController.get_tacho()
                    # Tourne les roues du bon cote
                    position_roues = 0 if self.cote_marche_arriere > 0 else -0
                    nouvellePositionRoues = True
                    # Passe a la sequence suivante
                    self.marche_arriere_en_cours = 3

            # Si on est en train de reculer, sequence 2
            if self.marche_arriere_en_cours == 3:
                print("En cours de marche arriere branche 2")
                print("RPM: ", self.voiture.speedController.rpm)
                # Marche arriere
                self.voiture.reverse()
                # Verifie si on a assez recule
                print(self.tacho_marche_arriere - self.voiture.speedController.get_tacho())
                if self.tacho_marche_arriere - self.voiture.speedController.get_tacho() > self.TACHO_MARCHE_ARRIERE_2:
                    # Passe a la sequence suivante
                    self.marche_arriere_en_cours = 4

            # Fin de la sequence de recul, on freine
            if self.marche_arriere_en_cours == 4:
                self.voiture.freine()
                # Verifie si la voiture est immobile
                if self.voiture.estImmobile():
                    # Unlocke la position de l'obstacle
                    self.imageAnalysis.unlockObstacle()
                    # Passe a la sequence suivante
                    self.marche_arriere_en_cours = 0
                    print ("Fin de la sequence de marche arriere, reprise du programme")
                    self.voiture.avance(self.vitesse)

            # Laisse un peu de temps entre envoi servo et envoi VESC
            self.time.sleep(0.1)
            return position_roues, nouvellePositionRoues

            # N'execute le calcul que s'il y a une nouvelle image
        if self.imageAnalysis.isThereANewImage():
            last_image_time = self.imageAnalysis.last_execution_time

            # Verifie s'il faut engager une sequence de marche arriere
            if self.imageAnalysis.getObstacleInBrakeZone() and self.obstacleEnabled:
                self.marche_arriere_en_cours = 1
                self.voiture.freine()
                self.cote_marche_arriere = self.imageAnalysis.getPositionObstacle()
                position_roues = None
                nouvellePositionRoues = False
                return position_roues, nouvellePositionRoues

                # Calcule l'ecart de trajectoire par analyse d'image
            poly_coeff_square = self.imageAnalysis.getPolyCoeffSquare()
            position_ligne1 = self.imageAnalysis.getPositionLigne1()
            position_ligne2 = self.imageAnalysis.getPositionLigne2()
            parallelisme = self.imageAnalysis.getParallelism()

            if poly_coeff_square is None or position_ligne1 is None:
                # On n'a pas de ligne detectee, on maintient la position roues precedente (TODO trouver une autre strategie ?)
                position_roues = None
                nouvellePositionRoues = False

            else:
                # Set coeff d'asservissement par defaut
                coeff_parallelisme_P = self.COEFF_SUIVI_IMAGE_PARALLELISME_P_SPEED
                coeff_p2_p = self.COEFF_SUIVI_IMAGE_ROUES_P2_SPEED
                coeff_p2_i = self.COEFF_SUIVI_IMAGE_ROUES_I2_SPEED

                # Verifie s'il faut ralentir a cause d'un obstacle
                if self.vitesseEvitement is not None and self.obstacleEnabled:
                    if self.imageAnalysis.getObstacleExists():
                        # Set vitesse d'evitement
                        self.voiture.avance(self.vitesseEvitement)
                        # Set coeff d'asservissement evitement
                        coeff_parallelisme_P = self.COEFF_SUIVI_IMAGE_PARALLELISME_P_EVITEMENT
                        coeff_p2_p = self.COEFF_SUIVI_IMAGE_ROUES_P2_EVITEMENT
                        coeff_p2_i = self.COEFF_SUIVI_IMAGE_ROUES_I2_EVITEMENT
                    else:
                        # Set vitesse rapide
                        self.voiture.avance(self.vitesse)

                # Verifie s'il faut s'ecarter a cause d'un obstacle
                # Recupere la position de l'obstacle, qui a ete soit mesuree soit lockee en memoire
                position_obstacle = self.imageAnalysis.getPositionObstacle()
                if position_obstacle == 0:
                    self.offset = self.offset_hors_evitement
                    self.offset_progressif = True
                    if self.last_position_obstacle != 0:
                        # Reinitialise l'erreur integrale
                        self.cumulErreurPositionLigne = 0.
                elif position_obstacle > 0 and self.obstacleEnabled:
                    self.offset = self.OFFSET_ECART_GAUCHE
                    self.offset_progressif = False
                    if self.last_position_obstacle <= 0:
                        # Si on vient de commencer l'evitement, met l'erreur integrale au max pour aider a tourner
                        self.cumulErreurPositionLigne = self.COEFF_SUIVI_IMAGES_ROUES_MAX_ERREUR_I
                elif position_obstacle < 0 and self.obstacleEnabled:
                    self.offset = self.OFFSET_ECART_DROITE
                    self.offset_progressif = False
                    if self.last_position_obstacle >= 0:
                        # Si on vient de commencer l'evitement, met l'erreur integrale au max pour aider a tourner
                        self.cumulErreurPositionLigne = -self.COEFF_SUIVI_IMAGES_ROUES_MAX_ERREUR_I

                if self.offset_progressif:
                    # Fait tendre progressivement l'offset courant vers la cible
                    steps_progression_offset = 10
                    self.currentOffset += (self.offset - self.currentOffset) / steps_progression_offset
                else:
                    # Pas de progressivite de l'offset, on y va direct !
                    self.currentOffset = self.offset
                print("Offset: ", self.currentOffset)

                offset = self.currentOffset

                # Calcul roues parallelisme
                braquage_parallelisme = coeff_parallelisme_P * parallelisme
                # Calcul roues position ligne Proportionnel
                braquage_position_ligne_2_p = coeff_p2_p * (position_ligne2 + offset)
                # Calcul roues position ligne Integral
                self.cumulErreurPositionLigne += position_ligne2 + offset
                self.cumulErreurPositionLigne = max(-self.COEFF_SUIVI_IMAGES_ROUES_MAX_ERREUR_I,
                                                    min(self.COEFF_SUIVI_IMAGES_ROUES_MAX_ERREUR_I,
                                                        self.cumulErreurPositionLigne))
                braquage_position_ligne_2_i = coeff_p2_i * self.cumulErreurPositionLigne
                # TOTAL
                braquage_total = braquage_parallelisme + braquage_position_ligne_2_p + braquage_position_ligne_2_i
                position_roues = min(max(braquage_total, -100), 100)

                print(
                    "Braquage total P: {:.0f} Braquage parallelisme: {:.0f} Braquage ecart 2 P: {:.0f} Braquage ecart 2 I: {:.0f}".format(
                        braquage_total, braquage_parallelisme, braquage_position_ligne_2_p,
                        braquage_position_ligne_2_i))

                nouvellePositionRoues = True

                elapsedSinceLastImageMs = int((self.time.time() - last_image_time) * 1000)
                print ("Position lignes: {:.2f} {:.2f} Position roues: {:.0f} Last image since: {:d}ms".format(
                    position_ligne1, position_ligne2, position_roues, elapsedSinceLastImageMs))

        else:
            position_roues = None
            nouvellePositionRoues = False

        return position_roues, nouvellePositionRoues

    def calculeCapSuiviImageLent(self):
        # N'execute le calcul que s'il y a une nouvelle image
        if self.imageAnalysis.isThereANewImage():
            cap_actuel = self.arduino.getCap()
            last_image_time = self.imageAnalysis.last_execution_time

            # Calcule l'ecart de trajectoire par analyse d'image
            poly_coeff_square = self.imageAnalysis.getPolyCoeffSquare()
            if poly_coeff_square is None:
                # TODO voir ce qu'il faut faire. En attendant on met a zero
                poly_coeff_square = 0
            position_ligne1 = self.imageAnalysis.getPositionLigne1()
            position_ligne2 = self.imageAnalysis.getPositionLigne2()
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

            elapsedSinceLastImageMs = int(self.time.time() - last_image_time * 1000)
            print (
                "Position lignes: {:.2f} {:.2f} cap_actuel: {:.0f} cap_a_suivre: {:.0f} Last image since: {:d}ms".format(
                    position_ligne1, position_ligne2, cap_actuel, capASuivre, elapsedSinceLastImageMs))

        else:
            capASuivre = self.lastCapASuivreForImageAnalysis

        return capASuivre

    def calculeCapASuivreLigneDroiteTelemetre(self):
        # Initialise le cap a suivre en fonction de la cible fixee initialement
        capASuivre = self.capTarget

        # Recale le cap a suivre en fonction de la distance du telemetre (uniquement si la valeur du telemetre est bonne)
        mesureDistance = self.arduino.bestTelemetrePourSuiviBordure()  # Utilise exclusivement ultrason et lidar
        p = self.COEFF_SUIVI_LIGNE_P / 3  # On asservit mollement
        i = self.COEFF_SUIVI_LIGNE_I / 3
        autoriseRecalage = True
        if (
                mesureDistance > 200):  # TODO si besoin ne faire l'asservissement que si mesureDistance est à +-25cm de la consigne
            # Si on n'a pas de bonne mesure, alors on utilise le telemetre IR
            mesureDistance = self.arduino.telemetreIR
            p = self.COEFF_SUIVI_LIGNE_P / 3  # Asservissement beaucoup plus mou avec telemetre IR
            i = self.COEFF_SUIVI_LIGNE_I / 3
            autoriseRecalage = False
        erreurDistance = mesureDistance - self.distance_ligne_droite_telemetre

        # Si on est en mode antiProche, ne prendre en compte que les erreurs de distance négatives (trop proches)
        amplificateurPAntiProche = 1
        if self.antiProche:
            if erreurDistance > 0:
                erreurDistance = 0
                amplificateurPAntiProche = self.AMPLIFICATEUR_P_ANTI_PROCHE

        correctionProportionnelle = erreurDistance * self.COEFF_SUIVI_LIGNE_P * amplificateurPAntiProche

        self.cumulErreurDistanceBordure += max(min(erreurDistance, 10),
                                               -10)  # Inutile de cumuler trop vite quand on est vraiment trop loin
        # Maintient le cumul des erreurs à une valeur raisonnable
        self.cumulErreurDistanceBordure = max(min(self.cumulErreurDistanceBordure, self.MAX_CUMUL_ERREUR_DISTANCE),
                                              -self.MAX_CUMUL_ERREUR_DISTANCE)

        print ("Cumul erreur distance: ", self.cumulErreurDistanceBordure)
        if self.activationDistanceIntegrale:
            correctionIntegrale = self.cumulErreurDistanceBordure * self.COEFF_SUIVI_LIGNE_I
        else:
            correctionIntegrale = 0

        correctionCap = max(min(correctionProportionnelle + correctionIntegrale, self.MAX_CORRECTION_CAP_TELEMETRE),
                            -self.MAX_CORRECTION_CAP_TELEMETRE)
        capASuivre = (capASuivre + correctionCap) % 360
        return capASuivre, autoriseRecalage

        # Calcule le cap a suivre pour le suivi de courbes au telemetre

    def calculeCapSuiviCourbes(self):
        arduino = self.arduino
        print ("Enter calcul suivi courbes")
        if self.calculCapSuiviCourbesEnCours == False:
            print ("Premiere mesure")
            # Premiere mesure
            self.timeLastCalculSuiviCourbe = self.time.time()
            self.mesureTelemetrePourSuiviCourbe = arduino.telemetreIR
            self.calculCapSuiviCourbesEnCours = True
            print ("Arduino cap : ", arduino.getCap())
            capASuivre = arduino.getCap()
            self.capTargetSuiviCourbe = capASuivre

        elif self.time.time() > (self.timeLastCalculSuiviCourbe + self.DELTA_T_SUIVI_COURBES):
            # C'est le moment de recaler le cap de suivi de courbes
            print ("Recalage suivi courbes")
            print ("Arduino telemetreIR : ", arduino.telemetreIR)
            print ("Mesure telemetre ancienne : ", self.mesureTelemetrePourSuiviCourbe)
            deltaTelemetre = arduino.telemetreIR - self.mesureTelemetrePourSuiviCourbe
            print ("----- deltaTelemetre : ", deltaTelemetre)
            correctionCapDerivee = deltaTelemetre * self.COEFF_DERIVEE_TELEMETRE_COURBES
            correctionCapDistance = (
                                            arduino.telemetreIR - self.distance_courbes_telemetre) * self.COEFF_ERREUR_TELEMETRE_COURBES
            correctionCapDerivee = max(min(correctionCapDerivee, 5), -5)
            correctionCapDistance = max(min(correctionCapDistance, 5), -5)
            print ("correctionCapDerivee : ", correctionCapDerivee)
            print ("correctionCapDistance : ", correctionCapDistance)
            # if (arduino.telemetreIR - self.distance_courbes_telemetre) > 0:
            #  correctionCapDerivee = 0
            capASuivre = self.capTargetSuiviCourbe + correctionCapDerivee + correctionCapDistance

            self.mesureTelemetrePourSuiviCourbe = arduino.telemetreIR
            print ("Cap actuel : ", arduino.getCap(), " Cap a suivre : ", capASuivre)
            self.capTargetSuiviCourbe = capASuivre

            # if (arduino.telemetreIR - self.distance_courbes_telemetre) < -10:
            #  capASuivre = arduino.getCap() - 15
            # elif (arduino.telemetreIR - self.distance_courbes_telemetre) > 10:
            #  capASuivre = arduino.getCap() + 15

        else:
            capASuivre = self.capTargetSuiviCourbe

        return capASuivre

    def calculePositionRouesFromCapForSuiviImageLent(self, erreurCap):
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
            max(int(-(coeff_proportionnel * (sign(erreurCap) * abs(erreurCap) ** self.EXPONENTIELLE_P_IMAGE))) + offset,
                -100), 100)
        return positionRoues

    def calculePositionRouesFromCapStandard(self, erreurCap):
        # Si pas suivi image, on calcule les termes integral et derivee
        self.cumulErreurCap = (self.cumulErreurCap / self.COEFF_AMORTISSEMENT_INTEGRAL) + erreurCap
        # Maintient le cumul des erreurs à une valeur raisonnable
        self.cumulErreurCap = max(min(self.cumulErreurCap, self.MAX_CUMUL_ERREUR_CAP), -self.MAX_CUMUL_ERREUR_CAP)
        print ("Cumul erreur cap : ", self.cumulErreurCap, " time : ", self.time.time())
        # Calcul de D
        correctionDerivee = -self.COEFF_DERIVEE * (erreurCap - self.lastErreurCap)
        self.lastErreurCap = erreurCap
        # Calcul de P
        coeff_proportionnel = self.COEFF_PROPORTIONNEL_POUR_VITESSE_MIN + ((self.vitesse - self.VITESSE_MIN) * (
                self.COEFF_PROPORTIONNEL_POUR_VITESSE_NOMINALE - self.COEFF_PROPORTIONNEL_POUR_VITESSE_MIN) / (
                                                                                   self.VITESSE_NOMINALE - self.VITESSE_MIN))

        # Calcul de la position des roues
        positionRoues = min(max(
            int(-(coeff_proportionnel * erreurCap) - (self.COEFF_INTEGRAL * self.cumulErreurCap) + correctionDerivee),
            -100), 100)
        return positionRoues
