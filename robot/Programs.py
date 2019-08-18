# coding=utf-8
TRR_2019 = [{
    'instruction': 'setCap',  # Cap asuivre = cap actuel
    'chenillard': True,
    'conditionFin': 'immediat'
},
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'ligneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 70,
        'conditionFin': 'tacho',
        'tacho': 2000
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'ligneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 60,
        'conditionFin': 'tacho',
        'tacho': 1000
    },
    # Premier virage
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 50,
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
        'instruction': 'ligneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 70,
        'conditionFin': 'tacho',
        'tacho': 1800,
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    # Fin deuxième ligne droite
    {
        'instruction': 'ligneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 60,
        'conditionFin': 'tacho',
        'tacho': 600
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    # Chicane
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 60,
        'conditionFin': 'tacho',
        'tacho': 4050,
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    # Troisième ligne droite sortie de chicane
    {
        'instruction': 'ligneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 60,
        'conditionFin': 'tacho',
        'tacho': 2000,
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    # Fin troisième ligne droite
    {
        'instruction': 'ligneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 50,
        'conditionFin': 'tacho',
        'tacho': 500
    },
    # Deuxième virage
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 45,
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
        'instruction': 'ligneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 50,
        'conditionFin': 'tacho',
        'tacho': 1000,
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    # Dernière ligne droite
    {
        'instruction': 'ligneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 90,  # Was 90 in TRR2018
        'conditionFin': 'tacho',
        'tacho': 7000,
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    # Ralentissement arrivée
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 60,
        'conditionFin': 'tacho',
        'tacho': 500,

    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 45,
        'conditionFin': 'tacho',
        'tacho': 500,
        'nextLabel': 'arret_apres_freinage'
    },

    {
        'label': 'arret_apres_freinage',
        'instruction': 'tourne',  # Arrêt avec roues a 0
        'speed': 0,
        'positionRoues': 0,
        'conditionFin': 'duree',
        'duree': 1.5,
        'nextLabel': 'attendBouton'  # Retour au début
    }
]

TRR_2018 = [
    {
        'instruction': 'setCap',  # Cap asuivre = cap actuel
        'chenillard': True,
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': False,
        'obstacle': False,
        'speed': 70,
        'conditionFin': 'tacho',
        'tacho': 2000
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 45,
        'conditionFin': 'tacho',
        'tacho': 500
    },
    # Premier virage
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 31,
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
        'speed': 70,
        'conditionFin': 'tacho',
        'tacho': 1800,
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
        'speed': 45,
        'conditionFin': 'tacho',
        'tacho': 450
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    # Chicane
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 31,
        'conditionFin': 'tacho',
        'tacho': 4250,
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    # Troisième ligne droite sortie de chicane
    {
        'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 70,
        'conditionFin': 'tacho',
        'tacho': 2000,
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
        'speed': 45,
        'conditionFin': 'tacho',
        'tacho': 500
    },
    # Deuxième virage
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 28,
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
        'speed': 50,
        'conditionFin': 'tacho',
        'tacho': 1000,
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
        'speed': 90,  # Was 90 in TRR2018
        'conditionFin': 'tacho',
        'tacho': 6500,
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
        'speed': 40,
        'conditionFin': 'tacho',
        'tacho': 500,

    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'speed': 30,
        'conditionFin': 'tacho',
        'tacho': 500,
        'nextLabel': 'arret_apres_freinage'
    },

    {
        'label': 'arret_apres_freinage',
        'instruction': 'tourne',  # Arrêt avec roues a 0
        'speed': 0,
        'positionRoues': 0,
        'conditionFin': 'duree',
        'duree': 1.5,
        'nextLabel': 'attendBouton'  # Retour au début
    }
]

DLVV = [
    {
        'instruction': 'setCap',  # Cap asuivre = cap actuel
        'conditionFin': 'immediat'
    },

    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'suiviImageRoues',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'display': 'GO',
        'speed': 30,
        'vitesseEvitement': 16,
        'conditionFin': 'tacho',
        'tacho': 25000,
    },
    {
        'instruction': 'tourne',  # Arrêt avec roues a 0
        'speed': 0,
        'positionRoues': 0,
        'conditionFin': 'duree',
        'duree': 1.5,
    }

]

LINE_ANGLE_OFFSET = [
    {
        'instruction': 'setCap',  # Cap asuivre = cap actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'lineAngleOffset',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 45,
        'conditionFin': 'tacho',
        'tacho': 25000,
    },
    {
        'instruction': 'tourne',  # Arrêt avec roues a 0
        'speed': 0,
        'positionRoues': 0,
        'conditionFin': 'duree',
        'duree': 10,
    }
]

CALIBRATE = [
    {
        'instruction': 'setCap',  # Cap asuivre = cap actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'tourne',  # suiviImageLigneDroite ou suiviImageRoues
        'speed': 20,
        'positionRoues': 40,
        'conditionFin': 'tacho',
        'tacho': 50000,
    },
    {
        'instruction': 'tourne',  # Arrêt avec roues a 0
        'speed': 0,
        'positionRoues': 0,
        'conditionFin': 'duree',
        'duree': 10,
    }
]

HIPPODROME = [
    ############ TEST HIPPODROME
    {
        'label': 'hippodrome',
        'instruction': 'SetCap',
        'conditionFin': 'immediat',
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': False,
        'speed': 4,
        'conditionFin': 'tacho',
        'tacho': 10,
    },
    {
        'instruction': 'ligneDroite',  # Puis finit le virage 180°
        'speed': 2,
        'conditionFin': 'tacho',
        'tacho': 5,
    },
    # {
    #     'instruction': 'tourne',  # Puis finit le virage 180°
    #     'positionRoues': 0,
    #     'speed': 0.5,
    #     'conditionFin': 'tacho',
    #     'tacho': 3,
    # },
    {
        'instruction': 'tourne',  # Puis finit le virage 180°
        'positionRoues': 80,
        'speed': 1,
        'conditionFin': 'cap',
        'capFinalMini': 165,  # En relatif par rapport au cap initial
        'capFinalMaxi': 195  # En relatif par rapport au cap initial
    },
    {
        'instruction': 'ajouteCap',
        'cap': 180,
        'conditionFin': 'immediat',
    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    # {
    #     'instruction': 'tourne',  # Puis finit le virage 180°
    #     'positionRoues': 0,
    #     'speed': 0.5,
    #     'conditionFin': 'tacho',
    #     'tacho': 5,
    # },
    {
        'instruction': 'ligneDroite',  # Puis finit le virage 180°
        'speed': 2,
        'conditionFin': 'tacho',
        'tacho': 5,
    },
    {
        'instruction': 'tourne',  # Puis finit le virage 180°
        'positionRoues': 80,
        'speed': 1,
        'conditionFin': 'cap',
        'capFinalMini': 165,  # En relatif par rapport au cap initial
        'capFinalMaxi': 195  # En relatif par rapport au cap initial
    },
    {
        'instruction': 'ajouteCap',
        'cap': 180,
        'conditionFin': 'immediat',
        'nextLabel': 'hippodrome'
    }
]

TEST = [
    {
        'label': 'attendBouton',
        'instruction': 'tourne',  # Attend l'appui sur le bouton
        'display': 'WAITB',
        'positionRoues': 0,
        'vitesse': 0,
        'conditionFin': 'attendBouton'
    },
    {
        'instruction': 'tourne',  # Puis finit le virage 180°
        'positionRoues': 10,
        'conditionFin': 'duree',
        'duree': 10,
    },
    {
        'instruction': 'tourne',  # Puis finit le virage 180°
        'positionRoues': -10,
        'conditionFin': 'duree',
        'duree': 10,
    },
    {
        'instruction': 'tourne',  # Puis finit le virage 180°
        'positionRoues': 20,
        'conditionFin': 'duree',
        'duree': 10,
    },
    {
        'instruction': 'tourne',  # Puis finit le virage 180°
        'positionRoues': -20,
        'conditionFin': 'duree',
        'duree': 10,
    }
]
