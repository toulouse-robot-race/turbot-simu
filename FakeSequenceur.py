# encoding:utf-8

# Librairies tierces
import os


class Sequenceur:
    # General
    # CONST_NOMBRE_MESURES_DEPASSEMENT_DISTANCE = 1000 # Nombre de mesures consecutives du telemetre avant de considerer qu'un depassement de distance est effectif
    DUREE_DEPASSEMENT_TELEMETRE = 0.1  # Temps en secondes pendant lequel le telemetre doit mesurer un depassement avant de considerer qu'un depassement est effectif
    DISTANCE_DEPASSEMENT_TELEMETRE_IR = 1  # TODO: remettre ? Distance min mesuree par le telemetre IR pour confirmer depassement

    # Premiere ligne droite
    VITESSE_PREMIERE_LIGNE_DROITE = 65  # 45 pendant 4.8 fonctionne
    DUREE_PREMIERE_LIGNE_DROITE = 3.0  # 3.7 avant incident - 4.5 lors des essais à 33s
    DISTANCE_BORDURE_PREMIERE_LIGNE_DROITE = 30

    # Ligne droite avant 180°
    VITESSE_LIGNE_DROITE_AVANT_180 = 25
    DISTANCE_DECLENCHEMENT_180 = 60

    # Premier virage 180°
    POSITION_ROUES_180_DEBUT = 75
    POSITION_ROUES_180_FIN = 30  # Initialement 30 ou 35, mais ca passe trop pres
    VITESSE_180_DEBUT = 30
    VITESSE_180_FIN = 38
    DUREE_LIGNE_DROITE_PENDANT_180 = 0.2

    # Ligne droite apres premier virage 180°
    VITESSE_LIGNE_DROITE_APRES_PREMiER_VIRAGE = 52  # Auparavant 47
    DISTANCE_BORDURE_APRES_PREMIER_VIRAGE = 30
    DUREE_LIGNE_DROITE_SANS_SUIVI_BORDURE_APRES_PREMIER_VIRAGE = 1
    DUREE_LIGNE_DROITE_APRES_PREMIER_VIRAGE = 2.1  # Auparavant 2.5 puis 2.7

    # Chicane
    VITESSE_ENTREE_CHICANE = 25
    DISTANCE_DECLENCHEMENT_CHICANE = 60
    VITESSE_PREMIER_VIRAGE = 42

    VITESSE_CHICANE = 40
    DUREE_LIGNE_DIAGONALE_CHICANE_1 = 0.40  # 0.7 essais de la veille TRR2017
    DUREE_LIGNE_DIAGONALE_CHICANE_2 = 0.6  # 0.7 essais de la veille TRR2017
    DUREE_LIGNE_DIAGONALE_CHICANE_3 = 0.90  # 0.95 essais de la veille TRR2017
    DUREE_LIGNE_DIAGONALE_CHICANE_4 = 0.6  # 0.5 essais de la veille TRR2017

    DELTA_CAP_LIGNE_DIAGONALE = 27
    DUREE_LIGNE_DROITE_CHICANE_1 = 0.60  # 0.40 essais de la veille TRR2017
    DUREE_LIGNE_DROITE_CHICANE_2 = 0.35  # 0.35
    DUREE_LIGNE_DROITE_CHICANE_3 = 0.55  # 0.55
    DUREE_LIGNE_DROITE_CHICANE_4 = 0.25

    # Ligne droite après chicane sans telemetre pour stabilisation
    VITESSE_LIGNE_DROITE_SORTIE_CHICANE = 45
    DUREE_LIGNE_DROITE_SORTIE_CHICANE = 1.0
    # Ligne droite au telemetre apres chicane
    VITESSE_LIGNE_DROITE_APRES_CHICANE = 57
    DISTANCE_BORDURE_LIGNE_DROITE_APRES_CHICANE = 30
    DUREE_LIGNE_DROITE_APRES_CHICANE = 2.5  # Auparavant 2.3

    # Deuxieme virage 180°
    POSITION_ROUES_180_DEBUT_2E = 75
    POSITION_ROUES_180_FIN_2E = 30  # Initialement 30 ou 35, mais ca passe trop pres
    VITESSE_180_DEBUT_2E = 30
    VITESSE_180_FIN_2E = 38
    DUREE_LIGNE_DROITE_PENDANT_180_2E = 0.2

    # Sortie dernier virage
    DUREE_LIGNE_DROITE_SANS_SUIVI_BORDURE_APRES_DERNIER_VIRAGE = 1  # On commence par une ligne droite au cap
    VITESSE_LIGNE_DROITE_SANS_SUIVI_BORDURE_APRES_DERNIER_VIRAGE = 45

    # Derniere ligne droite suivi bordure
    VITESSE_DERNIERE_LIGNE_DROITE = 75  # Nominal : 61 pendant 5.4s. On peut tenter 63 pendant 5.3s
    DISTANCE_BORDURE_DERNIERE_LIGNE_DROITE = 35
    DUREE_DERNIERE_LIGNE_DROITE = 4.6  # On poursuit par un suivi bordure (67 avec 5.0)

    # Acceleration finale
    VITESSE_DERNIERE_LIGNE_DROITE_CAP = 60
    DUREE_DERNIERE_LIGNE_DROITE_CAP = 0.1

    # Ralentissement ligne droite finale suivi bordure
    VITESSE_RALENTISSEMENT_FINAL = 30
    DISTANCE_BORDURE_RALENTISSEMENT_FINAL = 30
    DUREE_RALENTISSEMENT_FINAL = 1.5

    # Suivi courbes au telemetre IR
    VITESSE_SUIVI_COURBE_TELEMETRE_IR = 25
    DISTANCE_SUIVI_COURBE_TELEMETRE_IR = 60
    DUREE_SUIVI_COURBE_TELEMETRE_IR = 180

    # Durees d'appui sur le bouton poussoir
    DUREE_APPUI_COURT_REDEMARRAGE = 2  # Nombre de secondes d'appui sur le poussoir pour reinitialiser le programme
    DUREE_APPUI_LONG_SHUTDOWN = 10  # Nombre de secondes d'appui sur le poussoir pour eteindre le raspberry

    programme = [
        {
            'instruction': 'setCap',  # Cap asuivre = cap actuel
            'chenillard': True,
            'conditionFin': 'immediat'
        },
        {
            'label': 'startTest',
            'instruction': 'setTacho',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        {
            'instruction': 'suiviImageRoues',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': False,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 50
        },
        {
            'instruction': 'setTacho',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        {
            'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 1
        },
        # Premier virage
        {
            'instruction': 'suiviImageRoues',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'cap',
            'capFinalMini': 160,
            # En relatif par rapport au cap initial, pour la gauche : 180 300, pour la droite 60 180
            'capFinalMaxi': 270,  # En relatif par rapport au cap initial
        },
        {
            'instruction': 'setTacho',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        {
            'instruction': 'ajouteCap',
            'cap': 180,
            'conditionFin': 'immediat',
        },
        # deuxième ligne droite sortie de premier virage
        {
            'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 9,
        },
        {
            'instruction': 'setTacho',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        # Fin deuxième ligne droite
        {
            'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 2
        },
        {
            'instruction': 'setTacho',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        # Chicane
        {
            'instruction': 'suiviImageRoues',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho1',
            'tacho': 5,
        },
        {
            'instruction': 'setTacho1',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        # Troisième ligne droite sortie de chicane
        {
            'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 10,
        },
        {
            'instruction': 'setTacho',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        # Fin troisième ligne droite
        {
            'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 500
        },
        # Deuxième virage
        {
            'instruction': 'suiviImageRoues',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'cap',
            'capFinalMini': 160,
            'capFinalMaxi': 270,
        },
        {
            'instruction': 'setTacho',
            'conditionFin': 'immediat'
        },
        {
            'instruction': 'ajouteCap',
            'cap': 180,
            'conditionFin': 'immediat',
        },
        # début dernière ligne droite, sortie de deuxième virage
        {
            'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 5,
        },
        {
            'instruction': 'setTacho',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        # Dernière ligne droite
        {
            'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 20,
        },
        {
            'instruction': 'setTacho',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        # Ralentissement arrivée
        {
            'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 2,

        },
        {
            'instruction': 'setTacho',  # Memorise le tacho actuel
            'conditionFin': 'immediat'
        },
        {
            'instruction': 'suiviImageRoues',  # suiviImageLigneDroite ou suiviImageRoues
            'activationDistanceIntegrale': True,
            'obstacle': False,
            'vitesse': 1,
            'conditionFin': 'tacho',
            'tacho': 2,
            'nextLabel': 'arret_apres_freinage'
        },
        ############ TEST HIPPODROME
        # {
        #     'label': 'hippodrome',
        #     'instruction': 'SetCap',
        #     'conditionFin': 'immediat',
        # },
        # {
        #     'instruction': 'setTacho',  # Memorise le tacho actuel
        #     'conditionFin': 'immediat'
        # },
        # {
        #     'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        #     'activationDistanceIntegrale': False,
        #     'vitesse': 4,
        #     'conditionFin': 'tacho',
        #     'tacho': 10,
        # },
        # {
        #     'instruction': 'ligneDroite',  # Puis finit le virage 180°
        #     'vitesse': 2,
        #     'conditionFin': 'tacho',
        #     'tacho': 5,
        # },
        # # {
        # #     'instruction': 'tourne',  # Puis finit le virage 180°
        # #     'positionRoues': 0,
        # #     'vitesse': 0.5,
        # #     'conditionFin': 'tacho',
        # #     'tacho': 3,
        # # },
        # {
        #     'instruction': 'tourne',  # Puis finit le virage 180°
        #     'positionRoues': 80,
        #     'vitesse': 1,
        #     'conditionFin': 'cap',
        #     'capFinalMini': 165,  # En relatif par rapport au cap initial
        #     'capFinalMaxi': 195  # En relatif par rapport au cap initial
        # },
        # {
        #     'instruction': 'ajouteCap',
        #     'cap': 180,
        #     'conditionFin': 'immediat',
        # },
        # {
        #     'instruction': 'setTacho',  # Memorise le tacho actuel
        #     'conditionFin': 'immediat'
        # },
        # # {
        # #     'instruction': 'tourne',  # Puis finit le virage 180°
        # #     'positionRoues': 0,
        # #     'vitesse': 0.5,
        # #     'conditionFin': 'tacho',
        # #     'tacho': 5,
        # # },
        # {
        #     'instruction': 'ligneDroite',  # Puis finit le virage 180°
        #     'vitesse': 2,
        #     'conditionFin': 'tacho',
        #     'tacho': 5,
        # },
        # {
        #     'instruction': 'tourne',  # Puis finit le virage 180°
        #     'positionRoues': 80,
        #     'vitesse': 1,
        #     'conditionFin': 'cap',
        #     'capFinalMini': 165,  # En relatif par rapport au cap initial
        #     'capFinalMaxi': 195  # En relatif par rapport au cap initial
        # },
        # {
        #     'instruction': 'ajouteCap',
        #     'cap': 180,
        #     'conditionFin': 'immediat',
        #     'nextLabel': 'hippodrome'
        # },
    ]

    tacho = 0
    sequence = 0
    debut = True
    timeDebut = 0
    time = None
    programmeCourant = {}
    voiture = None
    asservissement = None
    last_mesure_depassement = False
    time_debut_depassement = 0
    last_mesure_telemetre1 = 0

    timer_led = 0
    vitesse_clignote_led = 10
    led_clignote = True
    last_led = 0

    timer_bouton = 0
    last_bouton = 1  # 1 = bouton relache, 0 = bouton appuye
    flag_appui_court = False  # Passe a True quand un appui court (3 secondes) a ete detecte

    def __init__(self, voiture, time, arduino, asservissement):
        self.voiture = voiture
        self.time = time
        self.arduino = arduino
        self.asservissement = asservissement

    def execute(self):

        # Fait clignoter la led
        if self.led_clignote:
            if self.time.time() > self.timer_led + self.vitesse_clignote_led:
                self.timer_led = self.time.time()
                self.last_led = 0 if self.last_led else 1
                self.voiture.setLed(self.last_led)
        else:
            self.voiture.setLed(1)

        # Verifie appui court (3 sec) ou long (10 sec) sur bouton
        if self.voiture.getBoutonPoussoir() == 0:
            if self.last_bouton == 1:
                self.timer_bouton = self.time.time()
            else:
                if self.time.time() > self.timer_bouton + self.DUREE_APPUI_COURT_REDEMARRAGE:
                    # Arrete la voiture
                    self.voiture.avance(0)
                    self.voiture.tourne(0)
                    self.vitesse_clignote_led = 0.3
                    self.led_clignote = True
                    self.flag_appui_court = True
                if self.time.time() > self.timer_bouton + self.DUREE_APPUI_LONG_SHUTDOWN:
                    # Appui long: shutdown Raspberry Pi
                    os.system('sudo shutdown -h now')
                    pass
            self.last_bouton = 0
        else:
            self.last_bouton = 1
            if self.flag_appui_court:
                # Si on a detecte un appui court avant la relache du bouton
                self.flag_appui_court = False
                # Retourne a la sequence du debut
                for i in range(len(self.programme)):
                    if 'label' in self.programme[i]:
                        if self.programme[i]['label'] == 'attendBouton':
                            # On a trouve la prochaine sequence
                            self.sequence = i
                            self.debut = True

        if self.debut:
            # Premiere execution de l'instruction courante
            self.programmeCourant = self.programme[self.sequence]
            instruction = self.programmeCourant['instruction']
            print ("********** Nouvelle instruction *********** ", instruction)
            self.timeDebut = self.time.time()
            self.debut = False
            self.arduino.annuleRecalageCap()
            self.asservissement.cumulErreurCap = 0
            self.last_mesure_depassement = False

            # Fait du cap courant le cap a suivre
            if instruction == 'setCap':
                self.asservissement.setCapTarget()

            if instruction == 'setTacho':
                self.tacho = self.voiture.speedController.get_tacho()

            # Programme la vitesse de la voiture
            if instruction == 'ligneDroite' or instruction == 'ligneDroiteTelemetre' or instruction == 'tourne' or \
                    instruction == 'suiviCourbeTelemetre' or instruction == 'suiviLigne' or \
                    instruction == 'suiviImageLigneDroite' or instruction == 'suiviImageRoues' or \
                    instruction == 'suiviImageCap':
                vitesse = self.programmeCourant['vitesse']
                print ("Vitesse : ", vitesse)
                self.voiture.avance(vitesse)
                self.asservissement.setVitesse(vitesse)

            # Positionne les roues pour l'instruction 'tourne'
            if instruction == 'tourne':
                positionRoues = self.programmeCourant['positionRoues']
                print ("Position roues : ", positionRoues)
                self.voiture.tourne(positionRoues)

            # Ajoute une valeur a capTarget pour l'instruction 'ajouteCap'
            if instruction == 'ajouteCap':
                self.asservissement.ajouteCap(self.programmeCourant['cap'])

            # Indique a la classe d'asservissement si elle doit asservir, et selon quel algo
            if instruction == 'ligneDroite':
                self.asservissement.initLigneDroite()
            elif instruction == 'suiviImageCap':
                self.asservissement.initSuiviImageCap()
            elif instruction == 'suiviImageRoues':
                self.asservissement.initSuiviImageRoues()
            elif instruction == 'suiviImageLigneDroite':
                activationDistanceIntegrale = False
                if 'activationDistanceIntegrale' in self.programmeCourant:
                    activationDistanceIntegrale = self.programmeCourant['activationDistanceIntegrale']
                self.asservissement.initSuiviImageLigneDroite(activationDistanceIntegrale)
            elif instruction == 'ligneDroiteTelemetre':

                recalageCap = False
                if 'recalageCap' in self.programmeCourant:
                    recalageCap = self.programmeCourant['recalageCap']

                activationDistanceIntegrale = False
                if 'activationDistanceIntegrale' in self.programmeCourant:
                    activationDistanceIntegrale = self.programmeCourant['activationDistanceIntegrale']

                antiProche = False
                if 'antiProche' in self.programmeCourant:
                    antiProche = self.programmeCourant['antiProche']
                    # Surtout pas de correction integrale avec la protection antiProche
                    activationDistanceIntegrale = False

                self.asservissement.initLigneDroiteTelemetre(self.programmeCourant['distance'], recalageCap,
                                                             activationDistanceIntegrale, antiProche)
            elif instruction == 'suiviCourbeTelemetre':
                self.asservissement.initCourbeTelemetre(self.programmeCourant['distance'])
            else:
                self.asservissement.annuleLigneDroite()

        else:
            # Partie qui s'execute en boucle tant que la condition de fin n'est pas remplie
            pass

        # Verifie s'il faut passer a l'instruction suivante
        finSequence = False  # Initialise finSequence
        # Recupere la condition de fin
        conditionFin = self.programmeCourant['conditionFin']
        # Verifie si la condition de fin est atteinte
        if conditionFin == 'attendreGyroStable':
            if self.arduino.gyroX != 0.0:
                # Si l'arduino a bien reussi a acquerir le gyro, le dit a travers la vitesse de clignotement de la led
                self.vitesse_clignote_led = 1.5
            finSequence = self.arduino.checkGyroStable()
        elif conditionFin == 'cap':
            capFinalMini = self.programmeCourant['capFinalMini']
            capFinalMaxi = self.programmeCourant['capFinalMaxi']
            if self.asservissement.checkDeltaCapAtteint(capFinalMini, capFinalMaxi):
                finSequence = True
        elif conditionFin == 'duree':
            if (self.time.time() - self.timeDebut) > self.programmeCourant['duree']:
                finSequence = True
        elif conditionFin == 'tacho':
            if self.voiture.speedController.get_tacho() > (self.tacho + self.programmeCourant['tacho']):
                finSequence = True
        elif conditionFin == 'immediat':
            finSequence = True
        elif conditionFin == 'telemetre':
            if self.arduino.bestTelemetrePourDetectionVirage() > self.programmeCourant['distSupA']:
                # if self.last_mesure_depassement:
                #  if self.last_mesure_telemetre1 != self.arduino.telemetre1:
                #    print "Telemetre1 : ", self.arduino.telemetre1, " Distance a depasser : ", self.programmeCourant['distSupA']
                #    self.last_mesure_telemetre1 = self.arduino.telemetre1
                #  # Verifie si depassement du telemetre1 pendant longtemps + confirmation par telemetre IR
                #  if (time.time() > self.time_debut_depassement + self.DUREE_DEPASSEMENT_TELEMETRE) and (self.arduino.telemetreIR > self.DISTANCE_DEPASSEMENT_TELEMETRE_IR):
                finSequence = True
            # else:
            #  self.time_debut_depassement = time.time()
            # self.last_mesure_depassement = True
            # else:
            #  self.last_mesure_depassement = False
        elif conditionFin == 'attendBouton':
            self.vitesse_clignote_led = 0.3
            self.led_clignote = True
            if self.voiture.getBoutonPoussoir() == 0:
                self.led_clignote = False
                finSequence = True

        if finSequence:
            # Si le champ nextLabel est defini, alors il faut chercher le prochain element par son label
            if 'nextLabel' in self.programmeCourant:
                nextLabel = self.programmeCourant['nextLabel']
                for i in range(len(self.programme)):
                    if 'label' in self.programme[i]:
                        if self.programme[i]['label'] == nextLabel:
                            # On a trouve la prochaine sequence
                            self.sequence = i
            else:
                # Si le champ nextLabel n'est pas defini, on passe simplement a l'element suivant
                self.sequence += 1
            self.debut = True
