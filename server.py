__author__ = 'Paulo Henrik Gonçalves'

from socket import *
import random
import threading
import constants as c
import time

mutex = threading.Lock()
sockets = []         # Array de sockets aguardando jogo
IPs = []             # Array de IPs aguardando jogo
threads = []         # Threads jogando no momento
waitingGame = False  # Flag caso haja jogador esperando outro para iniciar


class MyThread(threading.Thread):
    def __init__(self, num_players):
        self.sockPlayers = []          # lista de sockets
        self.numPlayers = num_players  # numero de jogadores
        self.numDraws = [0, 0, 0, 0]   # numero de cartas compradas
        self.numCards = [7, 7, 7, 7]   # numero de cartas na mao
        self.cardTop = 0               # carta do top da pilha de descarte
        self.colorTop = 0              # cor do topo da pilha de descarte
        self.indexTurn = 0             # indice do socket do jogador atual
        threading.Thread.__init__(self)

    def run(self):
        global waitingGame
        waitingGame = True
        while len(self.sockPlayers) < self.numPlayers:  # Enquanto nao houver todos os jogadores conectados
            if len(sockets) > 0:                        # Se ha jogadores aguardando para entrar no jogo
                mutex.acquire()
                self.sockPlayers.append(sockets.pop(0)) # Retira da lista de sockets global pra local
                mutex.release()
            for sock in self.sockPlayers:
                data = "".join(map(chr, sock.recv(1014)))
                if data != '':
                    sock.send(b'WAIT')

        for sock in self.sockPlayers:
            print('Player {} Ready!!'.format(sock.getpeername()))
        print('Starting Game!!')
        waitingGame = False  # Apto a iniciar uma nova conexao

        for sock in self.sockPlayers:
            sock.send(b'READY')

        deck = c.DECK        # Deck de cartas
        discard = []         # Pilha de Descarte
        random.shuffle(deck) # Embaralha

        while True:  # Escolhe a carta inicial da pilha de descarte
            top = deck.pop(0)
            top2 = top.split("_")
            if top2[0].isnumeric():
                self.cardTop = top2[0]
                self.colorTop = top2[1]
                discard.append(top)
                break
            else:
                deck.append(top)

        start_clock = time.clock()

        while True:
            if len(self.sockPlayers) < self.numPlayers:  # Algum jogador se desconectou
                for sock in self.sockPlayers:
                    sock.send(b'|END')
                break

            if time.clock() - start_clock > c.ROUND_TIME:  # Tempo do ROUND foi estourado
                card = '|CARD'
                card += '*' + deck.pop(0)
                self.sockPlayers[self.indexTurn].send(card.encode())
                self.numCards[self.indexTurn] += 1
                if self.indexTurn == 0:
                    self.indexTurn = 1
                else:
                    self.indexTurn = 0
                start_clock = time.clock()

            enemy_index = self.indexTurn-1  # Indice do sock inimigo
            if enemy_index < 0:
                enemy_index = 1

            for sock in self.sockPlayers:
                index = self.sockPlayers.index(sock)
                data = "".join(map(chr, sock.recv(1014)))

                datas = data.split("|")

                for data in datas:
                    data = data.split("*")

                    # PROTOCOLO
                    if data[0] == 'DRAW':  # Jogador requisita compra inicial
                        if self.sockPlayers.index(sock) == self.indexTurn:
                            sock.send(b'|TURNON')
                        else:
                            sock.send(b'|TURNOFF')
                        if self.numDraws[index] == 0:  # Se for a primeira compra
                            cards = '|CARD'
                            for i in range(7):  # Numero de cartas iniciais
                                cards += '*' + deck.pop(0)
                            sock.send(cards.encode())

                        aux = len(discard) - 1
                        discard_list = []
                        discard_card = '|DISCARD'  # Prepara a lista de cartas no poto da pilha de descarte
                        for i in range(0, 3):
                            if aux >= 0:
                                discard_list.append(discard[aux])
                                aux -= 1
                        for i in range(0, len(discard_list)):
                            discard_card += ('*' + discard_list.pop())
                        sock.send(discard_card.encode())

                        message = '|PLAYER*' + str(self.numCards[enemy_index])
                        sock.send(message.encode())

                        self.numDraws[index] += 1

                    elif data[0] == 'DRAWCARD':  # Jogador requisita compra de carta
                        if self.sockPlayers.index(sock) == self.indexTurn:
                            sock.send(b'|TURNON')
                        else:
                            sock.send(b'|TURNOFF')
                        card = '|CARD'
                        card += '*' + deck.pop(0)
                        self.sockPlayers[self.indexTurn].send(card.encode())
                        self.numCards[self.sockPlayers.index(sock)] += 1
                        message = '|PLAYER*' + str(self.numCards[enemy_index])
                        sock.send(message.encode())
                        if self.indexTurn == 0:
                            self.indexTurn = 1
                        else:
                            self.indexTurn = 0
                        start_clock = time.clock()

                    elif data[0] == 'DRAW2':  # Jogador joga compra 2
                        if self.sockPlayers.index(sock) == self.indexTurn:
                            sock.send(b'|TURNON')
                        else:
                            sock.send(b'|TURNOFF')
                        cards = '|CARD'
                        for i in range(2):
                            cards += '*' + deck.pop(0)
                        sock.send(cards.encode())
                        self.numCards[self.sockPlayers.index(sock)] += 2
                        message = '|PLAYER*' + str(self.numCards[enemy_index])
                        sock.send(message.encode())

                    elif data[0] == 'DRAW4':
                        if self.sockPlayers.index(sock) == self.indexTurn:
                            sock.send(b'|TURNON')
                        else:
                            sock.send(b'|TURNOFF')
                        cards = '|CARD'
                        for i in range(4):
                            cards += '*' + deck.pop(0)
                        sock.send(cards.encode())
                        self.numCards[self.sockPlayers.index(sock)] += 4
                        message = '|PLAYER*' + str(self.numCards[enemy_index])
                        sock.send(message.encode())

                    elif data[0] == 'CARD':
                        card = data[1]
                        card = card.split("_")
                        if len(card) > 1:
                            if card[0] == self.cardTop or card[1] == self.colorTop:
                                if card[0] == 'S':
                                    if self.indexTurn == 0:
                                        self.indexTurn = 1
                                    else:
                                        self.indexTurn = 0
                                elif card[0] == 'R':
                                    pass
                                elif card[0] == 'D':
                                    cards = '|CARD'
                                    for i in range(2):
                                        cards += '*' + deck.pop(0)
                                    self.sockPlayers[enemy_index].send(cards.encode())
                                    self.numCards[enemy_index] += 2
                                else:
                                    pass
                                self.cardTop = card[0]
                                self.colorTop = card[1]
                                discard.append(data[1])
                                sock.send(b'|ACCEPT')
                                self.numCards[self.sockPlayers.index(sock)] -= 1
                                message = '|PLAYER*' + str(self.numCards[enemy_index])
                                sock.send(message.encode())
                                if self.indexTurn == 0:
                                    self.indexTurn = 1
                                else:
                                    self.indexTurn = 0
                                start_clock = time.clock()
                            else:
                                sock.send(b'|DENIED')
                        else:
                            card = card[0].split("+")
                            if card[0] == 'WILDD':
                                cards = '|CARD'
                                for i in range(4):
                                    cards += '*' + deck.pop(0)
                                self.sockPlayers[enemy_index].send(cards.encode())
                                self.numCards[enemy_index] += 4
                            cardstr = card[0] + '_' + card[1]
                            self.cardTop = card[0]
                            self.colorTop = card[1]
                            discard.append(cardstr)
                            sock.send(b'|ACCEPT')
                            self.numCards[self.sockPlayers.index(sock)] -= 1
                            message = '|PLAYER*' + str(self.numCards[enemy_index])
                            sock.send(message.encode())
                            if self.indexTurn == 0:
                                self.indexTurn = 1
                            else:
                                self.indexTurn = 0
                            start_clock = time.clock()

                    elif data[0] == 'WIN':
                        self.sockPlayers[enemy_index].send(b'|LOSE')

                    else:
                        sock.send(b'|WAIT')

        print('End Game .. Thread return')


def start_server():
    # Prepara socket para conexao
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((c.SERVER_NAME, c.SERVER_PORT))
    server_socket.listen(c.SERVER_LISTEN)
    print('The server is ready to receive')

    while True:
        player_socket, player_IP = server_socket.accept()  # Aguarda uma conexao
        data = "".join(map(chr, player_socket.recv(1014))) # Decodifica mensagem para string

        # Protocolo inicial
        if data == 'CONNECT':
            print('Player {} connected!!'.format(player_IP))
            mutex.acquire()
            sockets.append(player_socket)  # Insere na lista de sockets conectados
            mutex.release()
            IPs.append(player_IP)          # Insere na lista de IPs conectados
            player_socket.send(b'WAIT')

            if not waitingGame:            # Caso nao possua jogador esperando para iniciar
                thread = MyThread(2)       # Cria nova thread com 2 jogadores
                threads.append(thread)     # Insere na lista de Threads
                thread.start()             # Inicia thread

        else:
            player_socket.send(b'CLOSED')
            player_socket.close()


# Inicia servidor
start_server()
