# encoding:utf-8

import logging
import sys
import time
# Permet de faire des listes en fifo
from collections import deque

# Imports pour lire le port serie (communication avec Arduino)
import serial

logger = logging.getLogger('mainLogger')


class Arduino:
    # Constantes
    DELTA_T_RECALAGE_CAP = 1.0  # Nombre de secondes entre chaque recalage de cap
    VITESSE_EN_CM_PAR_SECONDE = 100  # TODO A calculer dynamiquement et a deplacer dans une autre classe TODO
    COEFF_CORRECTION_ERREUR_CAP = 0.3  # Vitesse de correction de l'erreur du gyro, quand on la mesure avec les telemetres dans la ligne droite
    MAX_ELIMINATION_MESURE_ULTRASON = 70  # Nombre de cm mesure par telemetre1 au-dela desquels on ne le prend plus en compte
    MAX_ELIMINATION_MESURE_LIDAR = 100  # Nombre de cm mesure par lidar au-dela desquels on ne le prend plus en compte

    capteurGauche = -1
    capteurDroit = -1
    gyroX = 0.0
    gyroY = 0.0
    gyroZ = 0.0
    nouvelleDonneeGyro = False
    telemetre1LastMesures = deque([0.0, 0.0, 0.0])
    telemetreIRLastMesures = deque([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    telemetreLidarLastMesures = deque([0.0, 0.0, 0.0, 0.0])
    timeLastMesureTelemetre1 = 0
    telemetre1 = 0.0
    telemetreIR = 0.0
    telemetreLidar = 0.0
    bestTelemetre = 0.0
    noir = 1
    blanc = 0
    sequence = -1
    typeCapteur = 0
    ser = serial.Serial('/dev/ttyUSB0', 115200, dsrdtr=True)
    time.sleep(1)

    # Variables pour savoir si le gyro est stable
    lastGyroX = -999.9
    timeLastGyro = 0
    nouvelleDonneeLastGyro = False

    # Variables pour recaler le cap quand on est en ligne droite en suivant le telemetre
    erreurMesureCap = 0.0
    recalageCapEnCours = False
    mesureTelemetrePourRecalage = 0
    timeLastMesureRecalage = 0
    capMoyen = 0.0
    nombreMesuresCap = 0

    # Variable pour savoir si le telemetre a envoye une nouvelle donnee, reinitialisee dans l'asservissement apres log
    nouvelleDonneeTelemetre1 = False

    button = 1  # 1 relaché , 0 appuyé

    # Calcule la meilleure mesure du telemetre ultrason, pour suivi de bordure
    def bestTelemetre1MesureBordure(self):
        # Si pas de mesure depuis 100ms, on abandonne
        if time.time() > self.timeLastMesureTelemetre1 + 0.1:
            # Retourne une valeur tres elevee (5m)
            return 500
        else:
            # Prend la derniere mesure de la liste inferieure a 70cm
            for valeur in self.telemetre1LastMesures:
                if valeur < 70:
                    return valeur
        # Si on n'a pas trouve de valeur, c'est que toutes les mesures sont invalides, retourne une valeur invalide (5m)
        return 500

    # Calcule la meilleure mesure du telemetre laser, pour suivi de bordure
    def bestTelemetreLidarMesureBordure(self):
        sortedMesures = sorted(self.telemetreLidarLastMesures)
        # Supprime toutes les valeurs superieures a 120
        for valeur in sortedMesures:
            if valeur > 120:
                sortedMesures.pop()
        if len(sortedMesures) < 3:
            # Si on a trop peu de mesures valides
            return 500
        else:
            return sum(sortedMesures) / len(sortedMesures)

    # Renvoie la meilleure mesure de telemetre pour suivi de bordure
    def bestTelemetrePourSuiviBordure(self):
        '''
        return 500  # SUPPRESSION DES DEUX TELEMETRES ULTRASON ET LIDAR
        ultrason = self.bestTelemetre1MesureBordure()
        if ultrason < 70:
          return ultrason
        else:
          lidar = self.bestTelemetreLidarMesureBordure()
          if lidar < 120:
            return lidar
        # Si le lidar et l'ultrason sont tous deux invalides, retourne valeur tres elevee (5m)
        return 500
        '''
        lidar = self.bestTelemetreLidarMesureBordure()
        # Ne se sert du lidar que quand on est tres pres, la ou le telemetre IR n'est pas bon
        if lidar < 20:
            return lidar
        # Si le lidar a une valeur trop elevee, retourne valeur tres elevee
        return 500

    # Renvoie la valeur mediane de la liste
    def median(self, lst):
        lst = sorted(lst)
        if len(lst) < 1:
            return None
        if len(lst) % 2 == 1:
            return lst[((len(lst) + 1) / 2) - 1]
        else:
            return float(sum(lst[(len(lst) / 2) - 1:(len(lst) / 2) + 1])) / 2.0

    # Renvoie la meilleure mesure de telemetre pour la detection de debut de virage
    def bestTelemetrePourDetectionVirage(self):
        ultrason = self.bestTelemetre1MesureBordure()
        lidar = self.median(self.telemetreLidarLastMesures)
        ir = self.telemetreIR
        return min(ultrason, min(lidar, ir))

    # A appeler au debut de chaque nouvelle instruction pour annuler le recalage de cap precedent
    def annuleRecalageCap(self):
        self.recalageCapEnCours = False

    # Execute le calcul de recalage de cap quand on est en ligne droite en suivant le telemetre
    def executeRecalageCap(self, capTarget):
        if self.recalageCapEnCours == False:
            # Premiere mesure
            self.timeLastMesureRecalage = time.time()
            self.mesureTelemetrePourRecalage = self.telemetre1
            self.recalageCapEnCours = True
            self.capMoyen = self.getCap()
            self.nombreMesuresCap = 1
        elif time.time() > (self.timeLastMesureRecalage + self.DELTA_T_RECALAGE_CAP):
            # C'est le moment de recaler le cap
            print("----- Calcul de l'erreur de cap. Cap moyen mesure : ", self.capMoyen)
            # Calcul de l'erreur de suivi de la ligne droite mesuree par le gyro (cap moyen mesure moins cap de la ligne droite)
            deltaCapMesureTarget = (((self.capMoyen - capTarget) + 180) % 360) - 180
            print("deltaCap Mesure - Target : ", deltaCapMesureTarget)

            # Calcul de l'erreur reelle de suivi de la ligne droite
            deltaTelemetre = self.telemetre1 - self.mesureTelemetrePourRecalage
            deltaTelemetreEnDegres = -deltaTelemetre / (
                    self.DELTA_T_RECALAGE_CAP * self.VITESSE_EN_CM_PAR_SECONDE) * 180 / 3.14

            print("deltaTelemetreEnDegres : ", deltaTelemetreEnDegres)

            # Calcul de l'erreur du gyro
            erreurGyroCalculee = (((deltaCapMesureTarget - deltaTelemetreEnDegres) + 180) % 360) - 180

            # Ajoute une partie de l'erreur a l'erreur precedente
            self.erreurMesureCap = (((self.erreurMesureCap + (
                    erreurGyroCalculee * self.COEFF_CORRECTION_ERREUR_CAP)) + 180) % 360) - 180

            print("erreurMesureCap : ", self.erreurMesureCap)

            # Reinitialise les mesures
            self.timeLastMesureRecalage = time.time()
            self.mesureTelemetrePourRecalage = self.telemetre1
            self.capMoyen = self.getCap()
            self.nombreMesuresCap = 1
        else:
            # Actualise le cap moyen suivi pendant le recalage courant
            self.nombreMesuresCap += 1
            ecart = (((self.getCap() - self.capMoyen) + 180) % 360) - 180
            self.capMoyen = (self.capMoyen + (ecart / self.nombreMesuresCap)) % 360
            # (( (self.getCap() % 360) +  (self.nombreMesuresCap * self.capMoyen)) / (self.nombreMesuresCap + 1)) % 360

    # Renvoie le cap corrige de l'erreur
    def getCap(self):
        return (((self.gyroX - self.erreurMesureCap) + 180) % 360) - 180

    def checkGyroStable(self):
        if time.time() > (self.timeLastGyro + 4) and self.nouvelleDonneeLastGyro:
            self.nouvelleDonneeLastGyro = False
            self.timeLastGyro = time.time()
            ecart = (((self.gyroX - self.lastGyroX) + 180) % 360) - 180
            logger.info("checkGyroStable - Ecart gyro : {}".format(ecart))
            # Verifie si le gyro est stabilise (variation faible depuis deux secondes)
            if abs(ecart) < 0.05:
                logger.info("Gyro stable OK")
                return True
            else:
                self.lastGyroX = self.gyroX
                return False
        return False

    testTime = 0

    # Lit les donnees transmises par l'Arduino
    def litDonnees(self):
        try:
            # Read data incoming on the serial line
            while self.ser.inWaiting() > 0:
                data = self.ser.readline().decode('utf-8').split('\r')[0].strip(' \t\r\n\0')
                # logger.info('[arduino.py]Serial read : ' + repr(data))
                # logger.info('Telemetre ir: ' + str(self.telemetreIR))
                # logger.info('Telemetre us: ' + str(self.telemetre1))
                # print("Last time: ", time.time() - self.testTime)
                self.testTime = time.time()
                if data == '@':
                    # Debut de sequence de transmission pour le gyroscope
                    self.sequence = 0
                    self.typeCapteur = 2
                elif data == '/':
                    # Debut de sequence de transmission pour les capteurs de ligne (pas encore implemente dans l'Arduino)
                    self.sequence = 0
                    self.typeCapteur = 1
                elif data == '#':
                    # Debut de sequence de transmission pour les telemetres ultrason
                    self.sequence = 0
                    self.typeCapteur = 3
                elif data == '~':
                    # Debut de sequence de transmission pour le telemetre infrarouge
                    self.sequence = 0
                    self.typeCapteur = 4
                elif data == '{':
                    # Debut de sequence de transmission pour le telemetre infrarouge
                    self.sequence = 0
                    self.typeCapteur = 5
                elif data == '+':
                    # Boutton appuyé
                    self.button = 0
                elif data == '-':
                    # Boutton relaché
                    self.button = 1
                elif data == '!':
                    # Boutton d'arret d'urgence
                    raise KeyboardInterrupt("Boutton d'arret d'urgence appuyé")

                    # Lecture des capteurs de ligne
                elif self.typeCapteur == 1:
                    if self.sequence == 0:
                        # Recupere le premier element de la transmission
                        self.capteurDroit = int(data[0])
                        # Passe a l'element suivant
                        self.sequence += 1
                    elif self.sequence == 1:
                        # Recupere le deuxieme element de la transmission
                        self.capteurGauche = int(data[0])
                        self.sequence += 1

                # Lecture des gyros
                elif self.typeCapteur == 2:
                    if self.sequence == 0:
                        # Recupere le premier element de la transmission
                        self.gyroX = float(data)
                        # Passe a l'element suivant
                        self.sequence += 1
                    elif self.sequence == 1:
                        # Recupere le deuxieme element de la transmission
                        self.gyroY = float(data)
                        self.sequence += 1
                    elif self.sequence == 2:
                        # Recupere le troisième element de la transmission
                        self.gyroZ = float(data)
                        self.nouvelleDonneeGyro = True
                        self.nouvelleDonneeLastGyro = True
                        self.sequence += 1

                # Lecture des telemetres ultrasons (avec moyenne des mesures)
                elif self.typeCapteur == 3:
                    if self.sequence == 0:
                        # Recupere le premier element de la transmission
                        mesure = float(data)
                        # L'ajoute dans le tableau de mesures
                        self.telemetre1LastMesures.appendleft(mesure)
                        # Retire l'élément périmé du tableau des mesures (FIFO)
                        self.telemetre1LastMesures.pop()
                        # Conserve l'heure de la derniere mesure
                        self.timeLastMesureTelemetre1 = time.time()
                        # Prend la moyenne
                        self.telemetre1 = sum(self.telemetre1LastMesures) / len(self.telemetre1LastMesures)
                        # self.telemetre1 = min(self.telemetre1LastMesures)
                        # Indique qu'on a une nouvelle donnee
                        self.nouvelleDonneeTelemetre1 = True
                        # Passe a l'element suivant
                        self.sequence += 1

                # Lecture du telemetre infrarouge (avec moyenne des mesures)
                elif self.typeCapteur == 4:
                    if self.sequence == 0:
                        # Recupere le premier element de la transmission
                        mesure = float(data)
                        # L'ajoute dans le tableau de mesures
                        self.telemetreIRLastMesures.appendleft(mesure)
                        # Retire l'élément périmé du tableau des mesures (FIFO)
                        self.telemetreIRLastMesures.pop()
                        # Prend la moyenne
                        moyenneIR = sum(self.telemetreIRLastMesures) / len(self.telemetreIRLastMesures)
                        # maxIR = max(self.telemetreIRLastMesures) # Prend le max plutot que le min car la fonction de correspondance est decroissante
                        # Applique la formule de correspondance valeur => cm
                        self.telemetreIR = self.mesureIRtoCm(moyenneIR)
                        # Passe a l'element suivant
                        self.sequence += 1

                # Lecture du telemetre lidar (avec moyenne des mesures)
                elif self.typeCapteur == 5:
                    if self.sequence == 0:
                        # Recupere le premier element de la transmission
                        mesure = float(data)
                        # Convertit en cm
                        mesure = mesure / 10
                        # L'ajoute dans le tableau de mesures
                        self.telemetreLidarLastMesures.appendleft(mesure)
                        # Retire l'élément périmé du tableau des mesures (FIFO)
                        self.telemetreLidarLastMesures.pop()
                        # Prend le min
                        # moyenneLidar = sum(self.telemetreLidarLastMesures) / len(self.telemetreLidarLastMesures)
                        minLidar = min(self.telemetreLidarLastMesures)
                        # Affecte la valeur
                        self.telemetreLidar = minLidar
                        # Passe a l'element suivant
                        self.sequence += 1

            # Verifie quel telemetre il faut prendre en compte (filtrage des mesures aberrantes)
            if self.telemetre1 < self.MAX_ELIMINATION_MESURE_ULTRASON:
                # Choisit le telemetre ultrason
                self.bestTelemetre = self.telemetre1
            elif self.telemetreLidar < self.MAX_ELIMINATION_MESURE_LIDAR:
                # Choisit le telemetre laser
                self.bestTelemetre = self.telemetreLidar
            else:
                # Prend le min des trois
                self.bestTelemetre = min(self.telemetre1, min(self.telemetreIR, self.telemetreLidar))

        except KeyboardInterrupt:
            print("W: interrupt received, stopping")
            raise
        except ValueError:
            logger.error("Probleme de parsing des donnees recues de l'arduino")
            self.sequence = -1
        except:
            print("Erreur lors de la lecture sur le port serie:", sys.exc_info())
            raise

    # Transforme une valeur mesuree par le telemetre IR en cm
    def mesureIRtoCm(self, mesure):
        e = [0, 100, 134, 139, 157, 173, 200, 255, 301, 352, 408, 446, 530, 604, 1000]  # Valeurs en entree
        s = [130, 130, 110, 106, 93, 83, 68, 56, 43, 37, 32, 28, 21, 13, 0]  # Valeurs en sortie
        for i in range(1, len(e)):
            if mesure < e[i]:
                return s[i - 1] + ((mesure - e[i - 1]) * (s[i] - s[i - 1]) / (e[i] - e[i - 1]))
        return 0

    def send_pwm(self, pwm_steering):
        steering_pwm_mess = '#\n{:d}\n{:d}\n'.format(pwm_steering, 90)
        print("Sending to serial:")
        print(steering_pwm_mess)
        self.ser.write(bytes(steering_pwm_mess, 'utf-8'))


if __name__ == '__main__':
    arduino = Arduino()
    time.sleep(5)
    st = "/\n{:d}\n".format(1)
    arduino.ser.write(bytes(st, 'utf-8'))
    time.sleep(5)
    st = "/\n{:d}\n".format(0)
    arduino.ser.write(bytes(st, 'utf-8'))
    time.sleep(5)
    st = "/\n{:d}\n".format(1)
    arduino.ser.write(bytes(st, 'utf-8'))
    time.sleep(5)
    st = "/\n{:d}\n".format(0)
    arduino.ser.write(bytes(st, 'utf-8'))
