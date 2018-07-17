__author__ = 'Paulo Henrik Gonçalves'

import pygame, os, sys
from pygame.locals import *
from socket import *
import time
import constants as c

os.environ['SDL_VIDEO_CENTERED'] = '1'


class Game_Uno:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode(c.SCREEN_SIZE)
        pygame.display.set_caption(c.TITLE)
        self.background = pygame.image.load(c.BGSCREEN)
        self.playing = False
        self.waiting = False
        self.loadingPoints = 0
        self.discardOrder = 0
        self.clickIndex = 0
        self.myTurn = False
        self.drawCard = False
        self.drawPressed = False
        self.lenHand = 0
        self.lenDraw = 0
        self.uno_status = -1  # 0=travado  1=habilitado  2=pressionado
        self.extraDraw = False
        self.win_status = False
        self.enableColorChoice = False
        self.endGame = False
        self.wildColor = ''
        self.loadingClock = time.clock()
        self.sock = socket(AF_INET, SOCK_STREAM)

    def start_connection(self):
        try:
            self.sock.connect((c.SERVER_NAME, c.SERVER_PORT))
        except:
            self.sock.send(b'READY')
            while True:
                data = "".join(map(chr, self.sock.recv(1024)))
                if data == 'WAIT':
                    break
                if data == 'READY':
                    self.playing = True
                    break
            return

        self.waiting = True
        self.sock.send(b'CONNECT')
        while True:
            data = "".join(map(chr, self.sock.recv(1024)))
            if data == 'WAIT':
                break

    def draw_bg(self):
        self.display.blit(self.background, (0, 0))

    def text_objects(self, text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def button(self, msg, fs, bd, x, y, w, h, ic, ac, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        line = bd
        pygame.draw.rect(self.display, c.BLACK, (x-(line/2), y-(line/2), w+line, h+line))
        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(self.display, ac, (x, y, w, h))
            if click[0] == 1 and action is not None:
                action()
        else:
            pygame.draw.rect(self.display, ic, (x, y, w, h))

        smallText = pygame.font.Font(c.FONT_1, fs)
        textSurf, textRect = self.text_objects(msg, smallText, c.BLACK)
        textRect.center = ((x+(w/2)), (y+(h/2)))
        self.display.blit(textSurf, textRect)

    def quit(self):
        pygame.quit()
        sys.exit()

    def play_status(self):
        if self.playing:
            return 2
        elif self.waiting:
            return 1
        else:
            return 0

    def restart(self):
        self.sock.close()
        game.quit()
        self.playing = False
        self.waiting = False
        self.loadingPoints = 0
        self.loadingClock = time.clock()

        '''self.sock.send(b'END')
        data = ''
        while data != 'CLOSED':
            data = "".join(map(chr, self.sock.recv(1024)))
            print(data)'''
        init_game()

    def draw(self):
        if self.myTurn:
            if not self.drawPressed:
                self.drawCard = True
                self.drawPressed = True
                self.lenDraw = self.lenHand

    def uno(self):
        self.uno_status = 2

    def wildRed(self):
        self.wildColor = '+R'
        self.enableColorChoice = False

    def wildGreen(self):
        self.wildColor = '+G'
        self.enableColorChoice = False

    def wildBlue(self):
        self.wildColor = '+B'
        self.enableColorChoice = False

    def wildYellow(self):
        self.wildColor = '+Y'
        self.enableColorChoice = False

    def end_connection(self):
        self.sock.close()

    def menu(self):
        self.display.blit(pygame.image.load(c.BANNER), (0, 0))
        self.button('Iniciar Jogo', 26, c.CONTOUR_MENU, c.SCREEN_WIDTH - 370, 450, 200, 70, c.YELLOW, c.YELLOW_B, self.load_game)
        self.button('Sair', 26, c.CONTOUR_MENU, c.SCREEN_WIDTH - 370, 550, 200, 70, c.RED, c.RED_B, self.quit)

    def load_game(self):
        self.start_connection()

        smallText = pygame.font.Font(c.FONT_1, 40)
        fontColor = c.YELLOW
        if self.loadingPoints == 0:
            textSurf, textRect = self.text_objects('AGUARDANDO SERVIDOR    ', smallText, fontColor)
            textRect.center= ((c.SCREEN_WIDTH / 2)-2, (c.SCREEN_HEIGHT / 2))
        elif self.loadingPoints == 1:
            textSurf, textRect = self.text_objects('AGUARDANDO SERVIDOR .  ', smallText, fontColor)
            textRect.center = ((c.SCREEN_WIDTH / 2), (c.SCREEN_HEIGHT / 2))
        elif self.loadingPoints == 2:
            textSurf, textRect = self.text_objects('AGUARDANDO SERVIDOR .. ', smallText, fontColor)
            textRect.center = ((c.SCREEN_WIDTH / 2)+2, (c.SCREEN_HEIGHT / 2))
        else:
            textSurf, textRect = self.text_objects('AGUARDANDO SERVIDOR ...', smallText, fontColor)
            textRect.center = ((c.SCREEN_WIDTH / 2)+4, (c.SCREEN_HEIGHT / 2))

        if (time.clock() - self.loadingClock) > 1:
            self.loadingPoints += 1
            if self.loadingPoints == 4:
                self.loadingPoints = 0
            self.loadingClock = time.clock()

        self.display.blit(textSurf, textRect)

    def start_game(self):
        hand = []
        discard = []
        enemyCards = 0
        move = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        while True:
            '''if self.endGame:
                time.sleep(2)
                game.quit()'''
            mouseDown = False
            self.lenHand = len(hand)
            if len(hand) > 2:
                self.uno_status = 0
            game.draw_bg()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.sock.close()
                    game.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.sock.close()
                        game.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouseDown = True

            # BOTOES
            self.button('DESISTIR', 22, c.CONTOUR_MENU, c.SCREEN_WIDTH - 140, (c.SCREEN_HEIGHT/2)-60, 120, 45, c.RED, c.RED_B, self.restart)
            self.button('COMPRAR CARTA', 18, c.CONTOUR_MENU, 20, (c.SCREEN_HEIGHT / 2) + 15, 150, 150, c.BLUE, c.BLUE_B, self.draw)
            if self.myTurn:
                self.button('SEU TURNO', 30, c.CONTOUR_MENU, c.SCREEN_WIDTH - 310, (c.SCREEN_HEIGHT / 2) + 15, 290, 45, c.GREEN, c.GREEN)
            else:
                self.button('TURNO DO INIMIGO', 30, c.CONTOUR_MENU, c.SCREEN_WIDTH - 310, (c.SCREEN_HEIGHT / 2) + 15, 290, 45, c.RED_B, c.RED_B)
            if len(hand) == 2:
                self.button('UNO', 30, c.CONTOUR_MENU, 20, (c.SCREEN_HEIGHT / 2) - 165, 150, 150, c.YELLOW, c.YELLOW_B, self.uno)
            else:
                self.button('UNO', 30, c.CONTOUR_MENU, 20, (c.SCREEN_HEIGHT / 2) - 165, 150, 150, c.YELLOW, c.YELLOW)
            if self.uno_status == 2:
                self.button('UNO', 30, c.CONTOUR_MENU, 20, (c.SCREEN_HEIGHT / 2) - 165, 150, 150, c.RED_B, c.RED_B)

            # PROTOCOLOS
            data = ''
            if self.drawCard:
                self.sock.send(b'|DRAWCARD')
                self.drawCard = False
            else:
                self.sock.send(b'|DRAW')

            if self.lenHand != self.lenDraw:
                self.drawPressed = False

            while data == '':
                data = "".join(map(chr, self.sock.recv(1024)))

            datas = data.split("|")
            for data in datas:
                if len(data) < 1:
                    continue
                data = data.split("*")
                command = data.pop(0)
                if command == 'CARD':
                    for d in data:
                        hand.append(d)
                elif command == 'DISCARD':
                    discard.clear()
                    discard = data
                elif command == 'PLAYER':
                    enemyCards = int(data[0])
                elif command == 'END':
                    self.restart()
                elif command == 'ACCEPT':
                    if len(hand) == 2 and self.uno_status != 2:
                        self.extraDraw = True
                    self.uno_status = 0
                    hand.pop(self.clickIndex)
                    images.pop(self.clickIndex)
                    rects.pop(self.clickIndex)
                    if len(discard) > 2:
                        if self.discardOrder == 2:
                            self.discardOrder = 0
                        else:
                            self.discardOrder += 1
                elif command == 'DENIED':
                    pass
                elif command == 'TURNON':
                    self.myTurn = True
                elif command == 'TURNOFF':
                    self.myTurn = False
                elif command == 'LOSE':
                    self.win_status = True
                else:
                    pass

                images = []
                rects = []
                auxPos = (len(hand)+1) * c.CARD_SPACING
                auxPos = (c.SCREEN_WIDTH/2) - (auxPos/2) + c.CARD_SPACING

                # prepara cartas do jogador
                for card in hand:
                    image = pygame.image.load('images/cards/' + card.lower() + '.png')
                    rect = image.get_rect()
                    rect.centerx = auxPos
                    rect.centery = c.SCREEN_HEIGHT - c.CARD_HEIGHT + 50
                    images.append(image)
                    rects.append(rect)
                    auxPos += c.CARD_SPACING

                # movimenta as cartas com mouse
                (mouseL, mouseT) = pygame.mouse.get_pos()
                for index, rect in enumerate(rects):
                    inside = False
                    rectL = rect.left
                    rectT = rect.top
                    s = 0
                    if index == len(rects)-1:
                        s = c.CARD_WIDTH/2
                    if mouseL >= rectL:
                        if mouseL < rectL + c.CARD_SPACING+s:
                            if mouseT >= rectT:
                                if mouseT < rectT + c.CARD_HEIGHT:
                                    if move[index] < c.CARD_MOVE:
                                        rect.top -= move[index]
                                        move[index] += 4
                                        inside = True
                    if not inside:
                        if move[index] > 0:
                            move[index] -= 4
                            rect.top -= (c.CARD_MOVE - (c.CARD_MOVE - move[index]))

                # verifica clique em carta
                if mouseDown:
                    for index, rect in enumerate(rects):
                        rectL = rect.left
                        rectT = rect.top
                        s = 0
                        if index == len(rects) - 1:
                            s = c.CARD_WIDTH / 2
                        if mouseL >= rectL:
                            if mouseL < rectL + c.CARD_SPACING + s:
                                if mouseT >= rectT:
                                    if mouseT < rectT + c.CARD_HEIGHT:
                                        card = '|CARD*'
                                        if hand[index] == 'WILD' or hand[index] == 'WILDD':
                                            if self.myTurn:
                                                if self.wildColor != '':
                                                    card += hand[index] + self.wildColor
                                                    self.sock.send(card.encode())
                                                    self.wildColor = ''
                                                else:
                                                    self.enableColorChoice = True
                                                mouseDown = False
                                                self.clickIndex = index
                                                break

                                        else:
                                            card += hand[index]
                                            if self.myTurn:
                                                self.sock.send(card.encode())

                                            mouseDown = False
                                            self.clickIndex = index
                                            break

                # Escolhe Cor
                if self.enableColorChoice:
                    self.button(' ', 30, 0, (c.SCREEN_WIDTH/2) - 100, 540, 50, 50, c.RED, c.RED, self.wildRed)
                    self.button(' ', 30, 0, (c.SCREEN_WIDTH / 2) - 50, 540, 50, 50, c.GREEN, c.GREEN, self.wildGreen)
                    self.button(' ', 30, 0, (c.SCREEN_WIDTH / 2), 540, 50, 50, c.BLUE, c.BLUE, self.wildBlue)
                    self.button(' ', 30, 0, (c.SCREEN_WIDTH / 2) + 50, 540, 50, 50, c.YELLOW_B, c.YELLOW_B, self.wildYellow)

                if self.extraDraw:
                    self.sock.send(b'|DRAW2')
                    self.extraDraw = False

                # prepara cartas da pilha de descarte
                auxPos = 0
                for card in discard:
                    image = pygame.image.load('images/cards/' + card.lower() + '.png')
                    rect = image.get_rect()
                    if self.discardOrder == 0:
                        if auxPos == 0:
                            rect.centerx = c.SCREEN_WIDTH/2 - 30
                            rect.centery = c.SCREEN_HEIGHT/2 - 30
                        elif auxPos == 1:
                            rect.centerx = c.SCREEN_WIDTH/2 + 30
                            rect.centery = c.SCREEN_HEIGHT/2 - 15
                        else:
                            rect.centerx = c.SCREEN_WIDTH/2 - 5
                            rect.centery = c.SCREEN_HEIGHT/2 + 25
                    elif self.discardOrder == 1:
                        if auxPos == 0:
                            rect.centerx = c.SCREEN_WIDTH / 2 + 30
                            rect.centery = c.SCREEN_HEIGHT / 2 - 15
                        elif auxPos == 1:
                            rect.centerx = c.SCREEN_WIDTH / 2 - 5
                            rect.centery = c.SCREEN_HEIGHT / 2 + 25
                        else:
                            rect.centerx = c.SCREEN_WIDTH / 2 - 30
                            rect.centery = c.SCREEN_HEIGHT / 2 - 30
                    else:
                        if auxPos == 0:
                            rect.centerx = c.SCREEN_WIDTH / 2 - 5
                            rect.centery = c.SCREEN_HEIGHT / 2 + 25
                        elif auxPos == 1:
                            rect.centerx = c.SCREEN_WIDTH / 2 - 30
                            rect.centery = c.SCREEN_HEIGHT / 2 - 30
                        else:
                            rect.centerx = c.SCREEN_WIDTH / 2 + 30
                            rect.centery = c.SCREEN_HEIGHT / 2 - 15
                    auxPos += 1
                    images.append(image)
                    rects.append(rect)

                # prepara cartas dos outros jogadores
                auxPos = (enemyCards + 1) * c.CARD_SPACING
                auxPos = (c.SCREEN_WIDTH / 2) - (auxPos / 2) + c.CARD_SPACING
                for i in range(0, enemyCards):
                    image = pygame.image.load(c.CARDBACK)
                    rect = image.get_rect()
                    rect.centerx = auxPos
                    rect.centery = 100
                    images.append(image)
                    rects.append(rect)
                    auxPos += c.CARD_SPACING

            for i in range(len(images)):
                self.display.blit(images[i], rects[i])

            # Verifica se Jogador Ganhou
            if len(hand) == 0 and self.uno_status >= 0:
                self.button('VOCÊ GANHOU !!!', 72, c.CONTOUR_MENU, 20, 20, c.SCREEN_WIDTH - 40, c.SCREEN_HEIGHT - 40, c.BLUE, c.BLUE, self.end_connection)
                self.sock.send(b'|WIN')
                self.endGame = False
                self.win_status = False

            if self.win_status:
                self.button('VOCÊ PERDEU ...', 72, c.CONTOUR_MENU, 20, 20, c.SCREEN_WIDTH - 40, c.SCREEN_HEIGHT - 40, c.BLUE, c.BLUE, self.end_connection)
                self.endGame = False

            clock.tick(c.FPS)
            pygame.display.update()


def init_game():
    while True:
        game.draw_bg()

        for event in pygame.event.get():
            if event.type == QUIT:
                game.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.quit()

        if game.play_status() == 1:
            game.load_game()
        elif game.play_status() == 2:
            game.start_game()
        else:
            game.menu()

        clock.tick(c.FPS)
        pygame.display.update()


game = Game_Uno()
clock = pygame.time.Clock()
init_game()

