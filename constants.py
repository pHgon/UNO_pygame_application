__author__ = 'Paulo Henrik Gonçalves'

SCREEN_HEIGHT = 800
SCREEN_WIDTH  = 1200
SCREEN_SIZE   = (SCREEN_WIDTH, SCREEN_HEIGHT)
FPS           = 60

TITLE    = 'Divirta-se com UNO'
BGSCREEN = 'images/background.jpg'
BANNER   = 'images/banner.png'
CARDBACK = 'images/cards/back.png'

# Cores RGB
WHITE    = (255, 255, 255)
BLACK    = (0, 0, 0)
RED      = (255, 40, 40)
RED_B    = (255, 111, 111)
YELLOW   = (241, 232, 120)
YELLOW_B = (247, 241, 176)
GREEN    = (144, 238, 144)
BLUE     = (30, 144, 255)
BLUE_B   = (0, 191, 255)

# Propriedades Botoes
FONT_1       = 'fonts/SHOWG.TTF'
CONTOUR_MENU = 18

# Servidor
SERVER_PORT   = 55500
SERVER_NAME   = '192.168.11.88'
#SERVER_NAME   = '200.132.97.244'
SERVER_LISTEN = 40

""" Baralho contendo as 108 cartas
    [op_cor] : op(0-9=num, r=reverse, s=skip, d=draw) : cor(r=red, y=yellow, g=green, b=blue)"""
DECK = ['0_R', '1_R', '2_R', '3_R', '4_R', '5_R', '6_R', '7_R', '8_R', '9_R', 'R_R', 'S_R', 'D_R',
        '0_Y', '1_Y', '2_Y', '3_Y', '4_Y', '5_Y', '6_Y', '7_Y', '8_Y', '9_Y', 'R_Y', 'S_Y', 'D_Y',
        '0_G', '1_G', '2_G', '3_G', '4_G', '5_G', '6_G', '7_G', '8_G', '9_G', 'R_G', 'S_G', 'D_G',
        '0_B', '1_B', '2_B', '3_B', '4_B', '5_B', '6_B', '7_B', '8_B', '9_B', 'R_B', 'S_B', 'D_B',
        '1_R', '2_R', '3_R', '4_R', '5_R', '6_R', '7_R', '8_R', '9_R', 'R_R', 'S_R', 'D_R',
        '1_Y', '2_Y', '3_Y', '4_Y', '5_Y', '6_Y', '7_Y', '8_Y', '9_Y', 'R_Y', 'S_Y', 'D_Y',
        '1_G', '2_G', '3_G', '4_G', '5_G', '6_G', '7_G', '8_G', '9_G', 'R_G', 'S_G', 'D_G',
        '1_B', '2_B', '3_B', '4_B', '5_B', '6_B', '7_B', '8_B', '9_B', 'R_B', 'S_B', 'D_B',
        'WILD', 'WILD', 'WILD', 'WILD', 'WILDD', 'WILDD', 'WILDD', 'WILDD']

CARD_SPACING = 50
CARD_WIDTH   = 100
CARD_HEIGHT  = 150
CARD_MOVE    = 40
ROUND_TIME   = 30