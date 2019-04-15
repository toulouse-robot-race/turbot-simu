# coding=utf-8

TRR = [
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
        'instruction': 'suiviImageLigneDroite',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': False,
        'obstacle': False,
        'vitesse': 70,
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
        'vitesse': 45,
        'conditionFin': 'tacho',
        'tacho': 500
    },
    # Premier virage
    {
        'instruction': 'suiviImageRoues',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'vitesse': 31,
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
        'vitesse': 70,
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
        'vitesse': 45,
        'conditionFin': 'tacho',
        'tacho': 450
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
        'vitesse': 31,
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
        'vitesse': 70,
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
        'vitesse': 45,
        'conditionFin': 'tacho',
        'tacho': 500
    },
    # Deuxième virage
    {
        'instruction': 'suiviImageRoues',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'vitesse': 28,
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
        'vitesse': 50,
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
        'vitesse': 90,  # Was 90 in TRR2018
        'conditionFin': 'tacho',
        'tacho': 5900,
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
        'vitesse': 40,
        'conditionFin': 'tacho',
        'tacho': 500,

    },
    {
        'instruction': 'setTacho',  # Memorise le tacho actuel
        'conditionFin': 'immediat'
    },
    {
        'instruction': 'suiviImageRoues',  # suiviImageLigneDroite ou suiviImageRoues
        'activationDistanceIntegrale': True,
        'obstacle': False,
        'vitesse': 30,
        'conditionFin': 'tacho',
        'tacho': 500,
        'nextLabel': 'arret_apres_freinage'
    },

    {
        'label': 'arret_apres_freinage',
        'instruction': 'tourne',  # Arrêt avec roues a 0
        'vitesse': 0,
        'positionRoues': 0,
        'conditionFin': 'duree',
        'duree': 1.5,
        'nextLabel': 'attendBouton'  # Retour au début
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
        'vitesse': 4,
        'conditionFin': 'tacho',
        'tacho': 10,
    },
    {
        'instruction': 'ligneDroite',  # Puis finit le virage 180°
        'vitesse': 2,
        'conditionFin': 'tacho',
        'tacho': 5,
    },
    # {
    #     'instruction': 'tourne',  # Puis finit le virage 180°
    #     'positionRoues': 0,
    #     'vitesse': 0.5,
    #     'conditionFin': 'tacho',
    #     'tacho': 3,
    # },
    {
        'instruction': 'tourne',  # Puis finit le virage 180°
        'positionRoues': 80,
        'vitesse': 1,
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
    #     'vitesse': 0.5,
    #     'conditionFin': 'tacho',
    #     'tacho': 5,
    # },
    {
        'instruction': 'ligneDroite',  # Puis finit le virage 180°
        'vitesse': 2,
        'conditionFin': 'tacho',
        'tacho': 5,
    },
    {
        'instruction': 'tourne',  # Puis finit le virage 180°
        'positionRoues': 80,
        'vitesse': 1,
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
