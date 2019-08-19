# encoding:utf-8
import json

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

    def set_cap(self):
        target = self.car.get_cap()
        self.cap_target = target

    def add_cap(self):
        self.cap_target = (self.cap_target + self.current_program['cap']) % 360

    def set_tacho(self):
        self.tacho = self.car.get_tacho()

    def turn(self):
        steering = self.current_program['positionRoues']
        self.car.turn(steering)

    def forward(self):
        vitesse = self.current_program['speed']
        self.car.forward(vitesse)

    def passs(self):
        pass

    def init_lao(self):
        additional_offset = self.current_program['offset'] if 'offset' in self.current_program else 0
        self.strategy = self.strategy_factory.create_lao(additional_offset)

    def init_cap_standard(self):
        self.strategy = self.strategy_factory.create_cap_standard(self.cap_target, self.current_program['speed'])

    def handle_start_sequence(self):

        # Premiere execution de l'instruction courante
        self.current_program = self.program[self.sequence]
        instruction = self.current_program['instruction']
        print("********** Nouvelle instruction *********** ")
        print(print(json.dumps(self.current_program, indent = 4)))
        self.time_start = self.car.get_time()
        self.strategy = None

        # Applique l'instruction
        instractions_actions = {
            'setCap': self.set_cap,
            'setTacho': self.set_tacho,
            'ajouteCap': self.add_cap,
            'tourne': self.turn,
            'lineAngleOffset': self.init_lao,
            'ligneDroite': self.init_cap_standard,
        }
        if instruction not in instractions_actions.keys():
            raise Exception("Instruction " + instruction + " does not exist")
        instractions_actions[instruction]()

        # Programme la speed de la voiture
        if 'speed' in self.current_program:
            vitesse = self.current_program['speed']
            self.car.forward(vitesse)
        if 'display' in self.current_program:
            self.car.send_display(self.current_program['display'])
        if 'chenillard' in self.current_program:
            self.car.set_chenillard(self.current_program['chenillard'])

        self.start_sequence = False

    def check_cap(self):
        final_cap_mini = self.current_program['capFinalMini']
        cap_final_maxi = self.current_program['capFinalMaxi']
        return self.check_delta_cap_reached(final_cap_mini, cap_final_maxi)

    def check_delay(self):
        return (self.car.get_time() - self.time_start) > self.current_program['duree']

    def check_tacho(self):
        return self.car.get_tacho() > (self.tacho + self.current_program['tacho'])

    def end_now(self):
        return True

    def check_button(self):
        self.vitesse_clignote_led = 0.3
        self.led_clignote = True
        button_value = self.car.get_push_button() == 0
        if button_value:
            self.led_clignote = False
        return button_value

    def check_gyro_stable(self):
        return self.car.check_gyro_stable()

    def check_end_sequence(self):
        # Recupere la condition de fin
        end_condition = self.current_program['conditionFin']

        # Verifie si la condition de fin est atteinte
        end_conditions_check = {
            'cap': self.check_cap,
            'duree': self.check_delay,
            'tacho': self.check_tacho,
            'immediat': self.end_now,
            'attendBouton': self.check_button,
            'attendreGyroStable': self.check_gyro_stable
        }

        if end_condition not in end_conditions_check.keys():
            raise Exception("End condition " + end_condition + "does not exist")
        return end_conditions_check[end_condition]()

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
