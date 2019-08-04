# encoding:utf-8

import logging
import sys
import time
from collections import deque

import serial

# Constantes
DELTA_T_RECALAGE_CAP = 1.0  # Nombre de secondes entre chaque recalage de cap
VITESSE_EN_CM_PAR_SECONDE = 100  # TODO A calculer dynamiquement et a deplacer dans une autre classe TODO
COEFF_CORRECTION_ERREUR_CAP = 0.3  # Vitesse de correction de l'erreur du gyro, quand on la mesure avec les telemetres dans la ligne droite
MAX_ELIMINATION_MESURE_ULTRASON = 70  # Nombre de cm mesure par telemetre1 au-dela desquels on ne le prend plus en compte
MAX_ELIMINATION_MESURE_LIDAR = 100  # Nombre de cm mesure par lidar au-dela desquels on ne le prend plus en compte


class Arduino:
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
        elif time.time() > (self.timeLastMesureRecalage + DELTA_T_RECALAGE_CAP):
            # C'est le moment de recaler le cap
            print("----- Calcul de l'erreur de cap. Cap moyen mesure : ", self.capMoyen)
            # Calcul de l'erreur de suivi de la ligne droite mesuree par le gyro (cap moyen mesure moins cap de la ligne droite)
            deltaCapMesureTarget = (((self.capMoyen - capTarget) + 180) % 360) - 180
            print("deltaCap Mesure - Target : ", deltaCapMesureTarget)

            # Calcul de l'erreur reelle de suivi de la ligne droite
            deltaTelemetre = self.telemetre1 - self.mesureTelemetrePourRecalage
            deltaTelemetreEnDegres = -deltaTelemetre / (
                    DELTA_T_RECALAGE_CAP * VITESSE_EN_CM_PAR_SECONDE) * 180 / 3.14

            print("deltaTelemetreEnDegres : ", deltaTelemetreEnDegres)

            # Calcul de l'erreur du gyro
            erreurGyroCalculee = (((deltaCapMesureTarget - deltaTelemetreEnDegres) + 180) % 360) - 180

            # Ajoute une partie de l'erreur a l'erreur precedente
            self.erreurMesureCap = (((self.erreurMesureCap + (
                    erreurGyroCalculee * COEFF_CORRECTION_ERREUR_CAP)) + 180) % 360) - 180

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
    def get_cap(self):
        return (((self.gyroX - self.erreurMesureCap) + 180) % 360) - 180

    def checkGyroStable(self):
        if time.time() > (self.timeLastGyro + 4) and self.nouvelleDonneeLastGyro:
            self.nouvelleDonneeLastGyro = False
            self.timeLastGyro = time.time()
            ecart = (((self.gyroX - self.lastGyroX) + 180) % 360) - 180
            print("checkGyroStable - Ecart gyro : {}".format(ecart))
            # Verifie si le gyro est stabilise (variation faible depuis deux secondes)
            if abs(ecart) < 0.05:
                print("Gyro stable OK")
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
        except ValueError:
            print("Probleme de parsing des donnees recues de l'arduino")
            self.sequence = -1

    def send_pwm(self, pwm_steering):
        steering_pwm_mess = '#\n{:d}\n{:d}\n'.format(pwm_steering, 90)
        print("Sending to serial:")
        print(steering_pwm_mess)
        self.ser.write(bytes(steering_pwm_mess, 'utf-8'))

    def send_display(self, string):
        if len(string) > 8:
            print("cannot send string %s, too long" % string)
            return
        st = "%\n{:s}\n".format(string.ljust(8))
        self.ser.write(bytes(st, 'utf-8'))

    def set_led(self, state):
        if state == bool:
            raise Exception("Led state expect bool")
        st = "*\n{:d}\n".format(state)
        self.ser.write(bytes(st, 'utf-8'))

    def set_chenillard(self, state):
        if state == bool:
            raise Exception("Chenillard state expect bool")
        st = "/\n{:d}\n".format(state)
        self.ser.write(bytes(st, 'utf-8'))


if __name__ == '__main__':
    arduino = Arduino()
    while True:
        arduino.litDonnees()
        print("cap : %f" % arduino.get_cap())
        time.sleep(0.5)

