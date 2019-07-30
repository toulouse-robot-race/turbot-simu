# encoding:utf-8

# Librairies tierces

from robot.Component import Component


class Sequencer(Component):
    # Durees d'appui sur le bouton poussoir
    DUREE_APPUI_COURT_REDEMARRAGE = 2  # Nombre de secondes d'appui sur le poussoir pour reinitialiser le programme
    DUREE_APPUI_LONG_SHUTDOWN = 10  # Nombre de secondes d'appui sur le poussoir pour eteindre le raspberry

    tacho = 0
    cap_target = 0.0
    sequence = 0
    start_sequence = True
    time_start = 0
    current_program = {}

    timer_led = 0
    vitesse_clignote_led = 10
    led_clignote = True
    last_led = 0

    timer_bouton = 0
    last_bouton = 1  # 1 = bouton relache, 0 = bouton appuye
    flag_appui_court = False  # Passe a True quand un appui court (3 secondes) a ete detecte

    strategy = None

    def __init__(self, car, program, strategy_factory):
        self.strategy_factory = strategy_factory
        self.car = car
        self.program = program

    def execute(self):
        # Fait clignoter la led
        self.handle_led()

        if self.start_sequence:
            self.handle_start_sequence()

        if self.strategy is not None:
            steering = self.strategy.compute_steering()
            if steering is not None:
                self.car.turn(steering)

        if self.check_end_sequence():
            self.handle_end_sequence()

    def handle_led(self):
        if self.led_clignote:
            if self.car.get_time() > self.timer_led + self.vitesse_clignote_led:
                self.timer_led = self.car.get_time()
                self.last_led = 0 if self.last_led else 1
                self.car.set_led(self.last_led)
        else:
            self.car.set_led(1)

    def handle_start_sequence(self):

        # Premiere execution de l'instruction courante
        self.current_program = self.program[self.sequence]
        instruction = self.current_program['instruction']
        print("********** Nouvelle instruction *********** ", instruction)
        self.time_start = self.car.get_time()
        self.start_sequence = False

        # Fait du cap courant le cap a suivre
        if instruction == 'setCap':
            target = self.car.get_cap()
            self.cap_target = target

        if instruction == 'setTacho':
            self.tacho = self.car.get_tacho()

        # Positionne les roues pour l'instruction 'tourne'
        if instruction == 'tourne':
            steering = self.current_program['positionRoues']
            self.car.turn(steering)

        # Ajoute une valeur a capTarget pour l'instruction 'ajouteCap'
        if instruction == 'ajouteCap':
            self.cap_target = (self.cap_target + self.current_program['cap']) % 360

        # Programme la vitesse de la car
        if 'vitesse' in self.current_program:
            vitesse = self.current_program['vitesse']
            self.car.forward(vitesse)

        # Set steering algo
        if instruction == 'ligneDroite':
            pass
            # self.strategy = LigneDroite()
        elif instruction == 'suiviImageCap':
            pass
            # self.strategy = SuiviImageCap()
        elif instruction == 'suiviImageRoues':
            pass
            # self.strategy = SuiviImageRoues()
        elif instruction == 'lineAngleOffset':
            additional_offset = self.current_program['offset'] if 'offset' in self.current_program else 0
            self.strategy = self.strategy_factory.create_lao()
        elif instruction == 'suiviImageLigneDroite':
            activation_distance_integrale = False
            if 'activationDistanceIntegrale' in self.current_program:
                activation_distance_integrale = self.current_program['activationDistanceIntegrale']
                # self.strategy = SuiviImageLigneDroite()
        else:
            self.strategy = None

    def check_end_sequence(self):
        # Verifie s'il faut passer a l'instruction suivante
        end_sequence = False  # Initialise finSequence
        # Recupere la condition de fin
        end_condition = self.current_program['conditionFin']
        # Verifie si la condition de fin est atteinte
        if end_condition == 'cap':
            final_cap_mini = self.current_program['capFinalMini']
            cap_final_maxi = self.current_program['capFinalMaxi']
            if self.check_delta_cap_reached(final_cap_mini, cap_final_maxi):
                end_sequence = True
        elif end_condition == 'duree':
            if (self.car.get_time() - self.time_start) > self.current_program['duree']:
                end_sequence = True
        elif end_condition == 'tacho':
            if self.car.get_tacho() > (self.tacho + self.current_program['tacho']):
                end_sequence = True
        elif end_condition == 'immediat':
            end_sequence = True
        elif end_condition == 'attendBouton':
            self.vitesse_clignote_led = 0.3
            self.led_clignote = True
            if self.car.getBoutonPoussoir() == 0:
                self.led_clignote = False
                end_sequence = True
        return end_sequence

    def handle_end_sequence(self):
        # Si le champ nextLabel est defini, alors il faut chercher le prochain element par son label
        if 'nextLabel' in self.current_program:
            next_label = self.current_program['nextLabel']
            for i in range(len(self.program)):
                if 'label' in self.program[i]:
                    if self.program[i]['label'] == next_label:
                        # On a trouve la prochaine sequence
                        self.sequence = i
        else:
            # Si le champ nextLabel n'est pas defini, on passe simplement a l'element suivant
            self.sequence += 1
        self.start_sequence = True

    def check_delta_cap_reached(self, final_cap_min, final_cap_max):

        absolute_cap_mini = (self.cap_target + final_cap_min) % 360
        absolute_cap_maxi = (self.cap_target + final_cap_max) % 360

        gap_cap_mini = (((self.car.get_cap() - absolute_cap_mini) + 180) % 360) - 180
        gap_cap_maxi = (((self.car.get_cap() - absolute_cap_maxi) + 180) % 360) - 180

        turn_over = (gap_cap_mini > 0 and gap_cap_maxi < 0)

        if turn_over:
            print("--------------- Fin de virage ----------------")
            print("CapTarget : ", self.cap_target, "Cap : ", self.car.get_cap(), " Ecart cap mini : ", gap_cap_mini,
                  " Ecart cap maxi : ", gap_cap_maxi)
            print("----------------------------------------------")

        return turn_over
