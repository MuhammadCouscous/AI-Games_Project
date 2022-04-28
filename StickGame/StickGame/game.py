import pygame
import sys
from time import sleep
import random
import pickle

pygame.init()

pygame.mixer.init()

musics = 'OST/ganyu_theme.wav'  # Main Music du jeu
pygame.mixer.music.load(musics)
pygame.mixer.music.play(-1)

##############################################################################################################
#                                            InputBox Class                                                 #
##############################################################################################################

infos = pygame.display.Info()
scale_input = 0.6
cursor_auto = pygame.transform.scale(pygame.image.load('image/bowl.png'), (15, 15))


class InputBox:

    def __init__(self, text: str, positions: tuple, weight, height, font):
        self.base_color = (0, 125, 255)
        self.writing_color = (128, 255, 0)
        self.color = self.base_color
        self.font = font
        self.text = text
        self.x = positions[0]
        self.y = positions[1]
        self.minweight = weight * scale_input
        self.weight = weight * scale_input
        self.height = height * scale_input
        self.rect = pygame.Rect(self.x, self.y, self.weight, self.height)
        self.surface = self.font.render(self.text, True, self.color)
        self.writing = False

    def update(self, surf):
        if self.writing:
            self.color = self.writing_color
        else:
            self.color = self.base_color
        self.rect = pygame.Rect(self.x, self.y, self.weight, self.height)
        pygame.draw.rect(surf, self.color, self.rect)
        self.surface = self.font.render(self.text, True, (255, 255, 255))
        surf.blit(self.surface, (self.x + 10 * scale_input, self.y + 10 * scale_input))


##############################################################################################################
#                                               Button Class                                                 #
##############################################################################################################

class Button:

    def __init__(self, x, y, w, h, image, clicked_image, value):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, w, h)
        self.base_image = pygame.transform.scale(image, (w, h))
        self.clicked_image = pygame.transform.scale(clicked_image, (w, h))
        self.image = image
        self.value = value
        self.clicked = False
        self.hovered = False

    def display(self, surf):
        if self.hovered:
            self.image = self.clicked_image
            surf.blit(self.image, (self.x, self.y))
        if not self.hovered:
            self.image = self.base_image
            surf.blit(self.image, (self.x, self.y))
        pygame.display.flip()

    def hover(self, Ones, Twos, Turn):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and ((Ones == 'Barnabain' and Turn) or (Twos == 'Barnabine') and not Turn):
            self.hovered = True
            return True
        self.hovered = False
        return False

    def click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0] == 1:
                        return True
        return False


##############################################################################################################
#                                             CheckBox Class                                                 #
##############################################################################################################


class CheckBox:

    def __init__(self, x, y, weight, height, image, value: str, check_image, activation: bool = False):
        self.x = x
        self.y = y
        self.scale = 0.5
        self.base_image = pygame.transform.scale(image, (weight, height))
        self.checked_image = pygame.transform.scale(check_image, (weight * 1.25, height * 1.25))
        self.image = pygame.transform.scale(image, (weight, height))
        self.rect = pygame.Rect(x, y, weight, height)
        self.value = value
        self.checked = activation

    def display(self, surf):
        if self.checked:
            self.image = self.checked_image
            surf.blit(self.image, (self.x - 10 * self.scale, self.y - 10 * self.scale))
        else:
            self.image = self.base_image
            surf.blit(self.image, (self.x, self.y))

    def checks(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1:
                return True
        return False


##############################################################################################################
#                                                Human Class                                                 #
##############################################################################################################

scale = infos.current_w/1600

button1 = Button(400 * scale, 750 * scale, 140 * scale, 200 * scale, pygame.image.load("image/one_btn.png"),
                 pygame.image.load("image/one_btn_clicked.png"), 1)
button2 = Button(700 * scale, 750 * scale, 140 * scale, 200 * scale, pygame.image.load("image/two_btn.png"),
                 pygame.image.load("image/two_btn_clicked.png"), 2)
button3 = Button(1000 * scale, 750 * scale, 140 * scale, 200 * scale, pygame.image.load("image/three_btn.png"),
                 pygame.image.load("image/three_btn_clicked.png"), 3)


class Human:

    def play(self):
        if button1.click():
            return 1
        if button2.click():
            return 2
        if button3.click():
            return 3
        return 0


##############################################################################################################
#                                                  Bot Class                                                 #
##############################################################################################################

# représente l'IA
# Elle a un historique des coups (uniquement joués par elle pas de la partie)
# Une liste de Table pour chaque coup
# l'Etat de la partie est fourni extérieurement , elle n'est pas stocké
# Elle a aussi une variable e représentant la probabilité d'explorer un nouveau coup
class IAPlayer:
    def __init__(self, name, e=1, dtables={}):
        if dtables is None:
            dtables = {}
        self.name = name
        self.history = []
        self.dtables = dtables
        self.e = e

    # fonction permettant de choisir entre exploration et exploitation
    def epsilon_greedy(self):
        if random() < self.e:
            return True
        return False

    # Permet de choisir un coup en fonction de l'état de la partie
    def play(self, s):
        # On récupère la liste des coups possibles pour l'état et on cherche le maximum
        l_actions = self.dtables[s]

        """"""
        # On utilise l'algorithme epsilon greedy pour savoir si l'on exploite ou explore
        if random.random() < self.e:
            # On choisit un coup au hasard
            best_play = random.choice(l_actions)[0]
            self.history.append((s, best_play))
            return best_play

        """"""

        best_play = l_actions[0]
        for i in l_actions:
            if i[1] > best_play[1]:
                best_play = i

        """"""
        # Donne la liste de tous les index ayant la même valeur maximum que le meilleur coup
        l_max = [index for index, value in enumerate(l_actions) if value[1] == best_play[1]]

        best_play = l_actions[random.choice(l_max)][0]
        self.history.append((s, best_play))
        return best_play
        """"""

    """"""

    # Permet d'ajouter toutes les tables(ici pour les etats de 0 à 20)
    def add_tables(self):
        for i in range(1, 21):
            self.add_actions(i)

    # Permet de rajouter toutes les actions possible à un état précis
    def add_actions(self, s):
        # Si l'état n'est pas dans le dic, on l'initialise
        if s not in self.dtables: self.dtables[s] = []
        for i in range(1, 4):
            # On regarde si i est dans la liste des actions
            # Et si le coup est legal
            if any(i in d for d in self.dtables[s]) == False and s >= i:
                self.dtables[s].append([i, 0])

    """"""

    # Permet de récupérer l'arbre des valeurs selon le tour
    def get_previous(self):
        with open(self.name + ".txt", "rb") as f:
            L = pickle.load(f)
            self.dtables, self.e = L[0], L[1]

    # Permet de récupérer l'arbre des valeur selon le tour
    def save_previous(self):
        with open(self.name + ".txt", "wb") as f:
            pickle.dump([self.dtables, self.e], f)

    """"""

    # Permet d'actualiser toutes les valeurs des actions
    def update(self):

        r_history = list(reversed(self.history))
        # On donne la récompense pour le dernier coup, sinon elle est de 0.5
        if self.history[-1][0] == self.history[-1][1]:
            r = -1
        else:
            r = 1

        for index, value in enumerate(r_history):
            # q représente la valeur actuelle
            q = [i for i in self.dtables[value[0]] if i[0] == value[1]][0][1]

            # ind est l'index
            ind = [a for a, i in enumerate(self.dtables[value[0]]) if i[0] == value[1]]

            # maxa est la maximum au prochain coup, si l'on est au dernier coup, on considère qu'il vaut 0
            if index != 0:
                maxa = max([j[1] for j in [i for i in self.dtables[r_history[index - 1][0]]]])
            else:
                maxa = 0
            """"""
            # On actualise la valeur : += alpha* (r + gamma*maxa - q)
            self.dtables[value[0]][ind[0]][1] += 0.7 * (r + 0.9 * maxa - q)
            r = 0
            """"""
        # On actualise epsilon
        self.e = max(0.025, self.e * 0.99)
        self.history = []


# Représente un joueur qui joue au hasard
# Pour un état donné, le bot renvoie juste un coup au hasard, valide
class RandomPlayer:
    def play(self, n):
        p = random.randint(1, 3)
        while n < p:
            p = random.randint(1, 3)
        return p


# Représente un joueur
# Ressemble à RandomPlayer sauf qu'on a la possibilités de choisir son coup et
# d'écrire la suite de coup
class HumanPlayer:
    # Permet au joueur Humain de jouer
    # On demande le coup
    def play(self, n):
        coup = input("Votre Coup : ")
        while coup not in ["1", "2", "3"] or int(coup) > n:
            print("Coup Impossible " + "\n" + "\n")
            coup = input("Votre Coup : ")

        return int(coup)

    # Permet d'écrire l'état de la partie à partir du dernier coup
    def print_game(self, c, s):
        print("Coup joué :", c, "Il reste : " + "|" * s, "(" + str(s) + ")", "batons")


##############################################################################################################
#                                                Player Class                                                #
##############################################################################################################

class Player:

    def __init__(self, value: str):
        self.value = value

    def play(self, stick):
        if stick > 1:
            if self.value == 'human':
                player = Human()
                return player.play()
            if self.value == 'bot':
                player = IAPlayer('B01000', {}, 1)
                player.get_previous()
                player.e = 0
                return player.play(stick)
            if self.value == 'bot2':
                player = IAPlayer('B0150', {}, 1)
                player.get_previous()
                return player.play(stick)

            if self.value == 'botleft':
                player = IAPlayer('B11000', {}, 1)
                player.get_previous()
                player.e = 0
                return player.play(stick)
            if self.value == 'bot2left':
                player = IAPlayer('B1150', {}, 1)
                player.get_previous()
                return player.play(stick)

        return 0


##############################################################################################################
#                                   Initialisation de l'écran                                                #
##############################################################################################################

infos = pygame.display.Info()
scale = infos.current_w/1600 # Définir les proportions du jeu selon l'écran
run = True
pygame.display.set_caption('Stick Game 1.0')
window = pygame.display.set_mode((1600 * scale, 1000 * scale))
logo = pygame.image.load('image/logo.png')
pygame.display.set_icon(logo)
bg = pygame.image.load("image/wallpaper.jpg").convert()
bg = pygame.transform.scale(bg, (1600 * scale, 1000 * scale))
window.blit(bg, (0, 0))
coup = 0

##############################################################################################################
#                                   Initialisation des boutons                                               #
##############################################################################################################

button1.display(window)
button2.display(window)
button3.display(window)

checkbox_img = pygame.image.load("image/check_box.png").convert_alpha()
checkbox_img2 = pygame.image.load("image/check_box_able.png").convert_alpha()

checkbox_human_left = CheckBox(100 * scale, 100 * scale, 80 * scale, 80 * scale, checkbox_img, 'human', checkbox_img2,
                               True)
checkbox_bot_left = CheckBox(100 * scale, 240 * scale, 80 * scale, 80 * scale, checkbox_img, 'botleft', checkbox_img2)
checkbox_human_right = CheckBox(1400 * scale, 100 * scale, 80 * scale, 80 * scale, checkbox_img, 'human', checkbox_img2,
                                True)
checkbox_bot_right = CheckBox(1400 * scale, 240 * scale, 80 * scale, 80 * scale, checkbox_img, 'bot', checkbox_img2)
checkbox_bot_2_right = CheckBox(1400 * scale, 380 * scale, 80 * scale, 80 * scale, checkbox_img, 'bot2', checkbox_img2)
checkbox_bot_2_left = CheckBox(100 * scale, 380 * scale, 80 * scale, 80 * scale, checkbox_img, 'bot2left',
                               checkbox_img2)

bot_img = pygame.image.load('image/pictogramme_bot.png').convert_alpha()
bot_img = pygame.transform.scale(bot_img, (80 * scale, 85 * scale))
human_img = pygame.image.load('image/pictogramme_human.png').convert_alpha()
human_img = pygame.transform.scale(human_img, (80 * scale, 80 * scale))

title = pygame.image.load('image/title_stickgame.png').convert_alpha()

##############################################################################################################
#                                        Texte d'entée des noms                                              #
##############################################################################################################

base_font = pygame.font.Font(None, int(56 * scale))
mega_font = pygame.font.Font(None, int(90 * scale))
player_1_text = 'Barnabain'
player_2_text = 'Barnabine'
bot_text = 'Hard  Rob'
bot_text_2 = 'Hard Bob'
bot_2_text = 'Easy Rob'
bot_2_text_2 = 'Easy Bob'
input_rect_x = int(340 * scale)
input_rect_y = int(80 * scale)

inputbox_p1 = InputBox(player_1_text, (
    checkbox_human_right.x + checkbox_human_right.checked_image.get_width() - input_rect_x,
    checkbox_human_right.y + checkbox_human_right.y / 6),
                       input_rect_x, input_rect_y, base_font)
inputbox_p2 = InputBox(player_2_text,
                       (checkbox_human_left.x + (checkbox_human_left.checked_image.get_width()),
                        checkbox_human_left.y + checkbox_human_right.y / 6),
                       input_rect_x, input_rect_y, base_font)
inputbox_b1_right = InputBox(bot_text, (
    checkbox_bot_right.x + checkbox_bot_right.checked_image.get_width() - input_rect_x,
    checkbox_bot_right.y + checkbox_bot_right.y / 12),
                             input_rect_x, input_rect_y, base_font)
inputbox_b2_right = InputBox(bot_2_text, (
    checkbox_bot_2_right.x + checkbox_bot_2_right.checked_image.get_width() - input_rect_x,
    checkbox_bot_2_right.y + checkbox_bot_2_right.y / 24),
                             input_rect_x, input_rect_y, base_font)
inputbox_b1_left = InputBox(bot_text_2, (
    checkbox_bot_left.x + checkbox_bot_left.checked_image.get_width(), checkbox_bot_left.y + checkbox_bot_left.y / 12),
                            input_rect_x, input_rect_y, base_font)
inputbox_b2_left = InputBox(bot_2_text_2, (
    checkbox_bot_2_left.x + checkbox_bot_2_left.checked_image.get_width(),
    checkbox_bot_2_left.y + checkbox_bot_2_left.y / 24),
                            input_rect_x, input_rect_y, base_font)

FireOne = inputbox_p1
FireOne.writing = True
FireTwo = inputbox_p2
FireTwo.writing = False

##############################################################################################################
#                                   Fonction qui actualise le nombre de quilles                              #
##############################################################################################################


stick = 20


def update_pin():
    global stick
    window.blit(bg, (0, 0))
    for pins in range(stick):
        image = pygame.image.load("image/bowling_pin.png").convert_alpha()
        image = pygame.transform.scale(image, (75 * scale, 219 * scale))
        window.blit(image, (50 * scale + pins * 75 * scale, 500 * scale))


def update_all():
    inputbox_p1.update(window)
    inputbox_p2.update(window)
    inputbox_b1_right.update(window)
    inputbox_b2_right.update(window)
    inputbox_b1_left.update(window)
    inputbox_b2_left.update(window)
    window.blit(title, (575 * scale, 50 * scale))
    window.blit(bot_img, (10 * scale, 230 * scale))
    window.blit(human_img, (10 * scale, 100 * scale))
    window.blit(bot_img, (1510 * scale, 230 * scale))
    window.blit(human_img, (1510 * scale, 100 * scale))
    window.blit(bot_img, (10 * scale, 370 * scale))
    window.blit(bot_img, (1510 * scale, 370 * scale))
    checkbox_human_left.display(window)
    checkbox_bot_left.display(window)
    checkbox_human_right.display(window)
    checkbox_bot_right.display(window)
    checkbox_bot_2_right.display(window)
    checkbox_bot_2_left.display(window)
    button1.display(window)
    button2.display(window)
    button3.display(window)
    pygame.display.flip()


update_pin()
update_all()

##############################################################################################################
#                                        Players 1 et 2 par défaut                                           #
##############################################################################################################

player_1 = Player(checkbox_human_left.value)
player_2 = Player(checkbox_human_right.value)

playing = True

number = 0
number2 = 0
number3 = 0


def button_hovering():
    global number, number2, number3
    if button1.hover(FireOne.text, FireTwo.text, playing) and number == 0:
        button1.display(window)
        number = 1
    if not button1.hover(FireOne.text, FireTwo.text, playing) and number == 1:
        button1.display(window)
        number = 0

    if button2.hover(FireOne.text, FireTwo.text, playing) and number2 == 0:
        button2.display(window)
        number2 = 1
    if not button2.hover(FireOne.text, FireTwo.text, playing) and number2 == 1:
        button2.display(window)
        number2 = 0

    if button3.hover(FireOne.text, FireTwo.text, playing) and number3 == 0:
        button3.display(window)
        number3 = 1
    if not button3.hover(FireOne.text, FireTwo.text, playing) and number3 == 1:
        button3.display(window)
        number3 = 0


def plays():
    global playing, stick
    # Tour par tour
    if playing and stick >= 1:
        FireOne.writing = False
        FireTwo.writing = True
        begin = stick
        stick -= player_1.play(stick)
        if player_1.value == 'bot' or player_1.value == 'bot2' or player_1.value == 'botleft' or player_1.value == 'bot2left':
            sleep(1)
        if begin != stick:
            update_pin()
            update_all()
            playing = not playing

    if not playing and stick >= 1:
        FireTwo.writing = False
        FireOne.writing = True
        begin = stick
        stick -= player_2.play(stick)
        if player_2.value == 'bot' or player_2.value == 'bot2' or player_2.value == 'botleft' or player_2.value == 'bot2left':
            sleep(1)
        if begin != stick:
            update_pin()
            update_all()
            playing = not playing


while run:

    if stick < 0:
        stick = 0
        update_pin()
        update_all()

    plays()
    button_hovering()

    for event in pygame.event.get(pygame.QUIT):
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()

    for event in pygame.event.get(pygame.KEYDOWN, pygame.K_ESCAPE):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
                pygame.quit()
                sys.exit()

    # Player 1 soit BOT soit HUMAIN
    if checkbox_human_right.checks() and not checkbox_human_right.checked:
        checkbox_bot_right.checked = False
        checkbox_human_right.checked = True
        checkbox_bot_2_right.checked = False
        player_1 = Player(checkbox_human_right.value)
        FireOne = inputbox_p1
        FireOne.writing = True
        inputbox_b1_right.writing = False
        inputbox_b2_right.writing = False
    elif checkbox_bot_right.checks() and not checkbox_bot_right.checked:
        checkbox_human_right.checked = False
        checkbox_bot_right.checked = True
        checkbox_bot_2_right.checked = False
        player_1 = Player(checkbox_bot_right.value)
        FireOne = inputbox_b1_right
        FireOne.writing = True
        inputbox_p1.writing = False
        inputbox_b2_right.writing = False
    elif checkbox_bot_2_right.checks() and not checkbox_bot_2_right.checked:
        checkbox_human_right.checked = False
        checkbox_bot_2_right.checked = True
        checkbox_bot_right.checked = False
        player_1 = Player(checkbox_bot_2_right.value)
        FireOne = inputbox_b2_right
        FireOne.writing = True
        inputbox_p1.writing = False
        inputbox_b1_right.writing = False

    # Player 2 soit BOT soit HUMAIN
    if checkbox_human_left.checks() and not checkbox_human_left.checked:
        checkbox_bot_left.checked = False
        checkbox_human_left.checked = True
        checkbox_bot_2_left.checked = False
        player_2 = Player(checkbox_human_left.value)
        FireTwo = inputbox_p2
        FireOne.writing = True
        inputbox_b1_left.writing = False
        inputbox_b2_left.writing = False
    elif checkbox_bot_left.checks() and not checkbox_bot_left.checked:
        checkbox_human_left.checked = False
        checkbox_bot_left.checked = True
        checkbox_bot_2_left.checked = False
        player_2 = Player(checkbox_bot_left.value)
        FireTwo = inputbox_b1_left
        FireOne.writing = True
        inputbox_p2.writing = False
        inputbox_b2_left.writing = False
    elif checkbox_bot_2_left.checks() and not checkbox_bot_2_left.checked:
        checkbox_human_left.checked = False
        checkbox_bot_2_left.checked = True
        checkbox_bot_left.checked = False
        player_2 = Player(checkbox_bot_2_left.value)
        FireTwo = inputbox_b2_left
        FireOne.writing = True
        inputbox_p2.writing = False
        inputbox_b1_left.writing = False

    # Si l'une des checkbox est cliquée, on reset la partie
    if checkbox_bot_2_left.checks() or checkbox_bot_2_right.checks() or checkbox_human_right.checks() or checkbox_human_left.checks() or checkbox_bot_left.checks() or checkbox_bot_right.checks():
        stick = 20
        playing = True
        update_pin()
        update_all()

    if stick == 0 or stick == 1:

        if playing and stick == 1:
            pygame.draw.rect(window, (250, 250, 250),
                             pygame.Rect(450 * scale, 390 * scale, FireOne.weight + 43 * 11 * scale,
                                         FireOne.height + 40 * scale))
            window.blit(mega_font.render('VICTOIRE : ' + str(FireTwo.text), True, (128, 255, 0)),
                        (450 * scale, 400 * scale))
        if not playing and stick == 1:
            pygame.draw.rect(window, (250, 250, 250),
                             pygame.Rect(450 * scale, 390 * scale, FireTwo.weight + 43 * 11 * scale,
                                         FireTwo.height + 40 * scale))
            window.blit(mega_font.render('VICTOIRE : ' + str(FireOne.text), True, (128, 255, 0)),
                        (450 * scale, 400 * scale))
        if not playing and stick == 0:
            pygame.draw.rect(window, (250, 250, 250),
                             pygame.Rect(450 * scale, 390 * scale, FireOne.weight + 43 * 11 * scale,
                                         FireOne.height + 40 * scale))
            window.blit(mega_font.render('VICTOIRE : ' + str(FireTwo.text), True, (128, 255, 0)),
                        (450 * scale, 400 * scale))
        if playing and stick == 0:
            pygame.draw.rect(window, (250, 250, 250),
                             pygame.Rect(450 * scale, 390 * scale, FireTwo.weight + 43 * 11 * scale,
                                         FireTwo.height + 40 * scale))
            window.blit(mega_font.render('VICTOIRE : ' + str(FireOne.text), True, (128, 255, 0)),
                        (450 * scale, 400 * scale))
        pygame.display.flip()
        sleep(2.25)

        stick = 20
        playing = True

        FireOne = inputbox_p1
        FireOne.writing = True
        FireTwo = inputbox_p2
        FireTwo.writing = False
        inputbox_b1_left.writing = False
        inputbox_b2_left.writing = False
        inputbox_b1_right.writing = False
        inputbox_b2_right.writing = False

        checkbox_bot_right.checked = False
        checkbox_bot_2_right.checked = False
        checkbox_human_right.checked = True
        player_1 = Player(checkbox_human_right.value)
        checkbox_bot_left.checked = False
        checkbox_bot_2_left.checked = False
        checkbox_human_left.checked = True
        player_2 = Player(checkbox_human_left.value)

        update_pin()
        update_all()
