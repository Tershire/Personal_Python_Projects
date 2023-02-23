import random
import time
import sys
import cs1graphics as cm
import math

FACES = list(range(2, 11)) + ['Jack', 'Queen', 'King', 'Ace']
SUITS = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
SIZECARD = (40, 80)
RADIUS = 3
depthBack = -2
depthText = -1

# ----------------------------------------------------------
# 클래스 정의

# Graphic Classes
class Card(object): # 도형 집합의 레이어
    """Graphical representation of a card."""

    def __init__(self, face, suit, back=True):
        assert (face in FACES and suit in SUITS)
        self.layer = cm.Layer()              # self.card 는 안 하나 보지???
        self.face = face
        self.suit = suit
        self.back = back

        # Card Background
        bg = cm.Rectangle(SIZECARD[0], SIZECARD[1])     # 굳이 self.bg? bg아니고
        bg.setDepth(0)
        bg.setFillColor('white')
        bg.setBorderColor('black')
        self.layer.add(bg)

        # depthBack = -2
        if back:
            self.bgBack = cm.Rectangle(SIZECARD[0], SIZECARD[1])
            self.bgBack.setDepth(depthBack)                    # 카드 뒷면은 장막이 가리고 있는 걸로 해석
            self.bgBack.setFillColor('rosy brown')
            self.bgBack.setBorderColor('black')
            self.layer.add(self.bgBack)
        
        # Symbol for Center
        symbol = cm.Layer()
        make_symbol(symbol, suit)
        symbol.setDepth(0)
        self.layer.add(symbol)                # 도형들의 모음인 symbol이란 레이어를 '카드그래픽스' 레이어에 추가

        # Text for Top-left, Bottom-right
        if suit in ['Diamonds', 'Hearts']:
            color = 'red'
        else:
            color = 'black'

        if type(face) == int:
            num = str(face)
        else:
            num = face[0]

        # depthText = -1                                      # 뒤집어진 카드인 경우, 카드배경과 심볼은 레이어 깊이 0, 문자는 -1, back 장막은 -2에 위치. show()시 장막은 +2로
        # text T-L
        numTL = cm.Text()
        numTL.setMessage(num)
        numTL.setFontColor(color)
        dim_numTL = numTL.getDimensions()
        numTL.moveTo(-SIZECARD[0]/2 + dim_numTL[0]/2,
                     -SIZECARD[1]/2 + dim_numTL[1]/2)
        numTL.setDepth(depthText)
        self.layer.add(numTL)

        # text B-R
        numBR = cm.Text()
        numBR.setMessage(num)
        numBR.setFontColor(color)
        dim_numBR = numTL.getDimensions()
        numBR.moveTo(+SIZECARD[0]/2 - dim_numBR[0]/2,
                     +SIZECARD[1]/2 - dim_numBR[1]/2)
        numBR.setDepth(depthText)
        self.layer.add(numBR)

class Deck(object): # 도형 집합의 레이어인 Card 레이어 집합의 레이어
    """Graphic representation of a list of cards"""
    def __init__(self, cards, coord=(0, 0), spread=False):                 # coord Ref. to Table Canvas. cards는 card_Grphics 모음 리스트.
        self.layer = cm.Layer()
        self.cards = cards
        # self.contents = self.layer.getcontents()                         # 이 상황에서 self.layer 는 빈 레이어이기 때문인가?
        self.coord = coord

        n = 0
        interval = SIZECARD[0] + 10
        numCards = len(cards)
        for card in cards:
            # angRandom = random.uniform(-3, +3)            # cs1graphics가 Text Rotation 지원 안함
            # card.layer.rotate(angRandom)
            card.layer.setDepth(-n)
            if spread:
                card.layer.move(n * interval, 0)
                card.layer.move(-((numCards - 1) * interval) / 2, 0)
            n += 1
            self.layer.add(card.layer)
        self.layer.moveTo(coord[0], coord[1])

    def __eq__(self, deck):
        detLen = (len(self) == len(deck))
        lisBool = []
        if detLen:
            for n in range(len(self)):
                lisBool.append(self.contents()[n] == deck.contents()[n])
        return detLen and (False not in lisBool)

    def __ne__(self, deck):
        return not self == deck

    def __len__(self):
        return len(self.contents())

    def contents(self):
        return self.layer.getContents()

    def draw(self, deck, m, show=False, retCard=False, noDelay=False):
        cardPlaced = move_card(deck, -1, self, m, show, retCard, noDelay)
        if retCard == True:
            return cardPlaced

    def dump(self, deck, n, show=False, noDelay=False):
        move_card(self, n, deck, -1, show, False, noDelay)

    def shuffle(self): # Shuffle a deck
        lis = self.contents()
        random.shuffle(lis)
        n = 0
        for card in lis:
            card.setDepth(-n)
            n +=1


    def compare(self, cardCompare): # Compare cards in deck with a card of your choice and return differences in value
        lisDiff = []
        valCardCompare = getCardValue(cardCompare)
        for card in self.contents():
            val = getCardValue(card)
            diff = abs(valCardCompare - val)
            lisDiff.append(diff)
        return lisDiff
        # lisDiff = []
        # for item in self.contents():
        #     diff = abs(card.value() - item.value())              # 리스트였던 카드 객체를 레이어로 바꾸고 나니 카드 객체의 어트리뷰트였던 value값을 더 이상 트래킹하지 못하게 됨
        #     lisDiff.append(diff)
        # return lisDiff

    def spread(self):
        n = 0
        interval = SIZECARD[0] + 10
        numCards = len(self)
        for card in self.contents():
            card.move(n * interval, 0)
            card.move(-((numCards - 1) * interval) / 2, 0)
            n += 1

    def show(self): # Show face, suit information of all cards in deck
        for card in self.contents():
            back = card.getContents()[-1]
            back.setDepth(-depthBack)                     # 뒷면 장막 걷기
            # card.show()                         # AttributeError: 'Layer' object has no attribute 'show' Deck() 클래스가 list of Card 가 아닌 순전히 레이어로만 작동하다보니 생긴 문제

    def hide(self):
        for card in self.contents():
            back = card.getContents()[0]
            back.setDepth(depthBack)


class Table(object):
    """Graphical representation of Table"""
    def __init__(self):
        self.canvas = cm.Canvas(980, 600, 'dark green', 'Speed Game')

# ----------------------------------------------------------
# 함수 정의
def distribute(deckSource, totalN, deck1, deck2, noDelay=False):
    N1 = totalN // 2
    N2 = totalN - N1
    for n in range(N1):
        move_card(deckSource, -1, deck1, -1, False, False, noDelay)
    for n in range(N2):
        move_card(deckSource, -1, deck2, -1, False, False, noDelay)

    # return deck1, deck2


def inHand(hand, cards):
    lis = [None, None]
    if len(hand.contents()) >= 1:
        for n in range(len(cards)):
            lisDiff = hand.compare(cards[n])
            if 12 in lisDiff:
                lisDiff[lisDiff.index(12)] = 1
            if 1 in lisDiff:
                lis[n] = lisDiff.index(1)               # 1인 첫번쨰 원소 반환 
    return lis


def dumpAndDraw(hand, deckDump, deckDraw, lis, which, ndx):
    cardDumped = lis[ndx]
    depthDumped = cardDumped.getDepth()
    coordDumped = cardDumped.getReferencePoint().get()

    hand.dump(deckDump[which], ndx, True)

    # cardDumped = hand.dump(deckDump[which], ndx, True, True)                      # move_card() 가 반환하는 cardDrawn은 도착 덱으로 이동을 다 마친 상태라 안됨
    # depthDumped = cardDumped.getDepth()
    # coordDumped = cardDumped.getReferencePoint().get()

    if len(deckDraw) != 0:  # 마지막 내려놓을 카드 5장부터는 deckDraw 에서 뽑아올 카드가 없다!!!
        blankCard = cm.Layer()
        blankCard.setDepth(depthDumped)
        blankCard.moveTo(coordDumped[0], coordDumped[1])  # 어제 blankCard 위치 선정을 안해줬다
        hand.layer.add(blankCard)

        cardDrawn = hand.draw(deckDraw, ndx, True, True)              # 이상하게도 반환시 None 이다. draw 함수 내에서는 아닌데, 아 draw 함수가 반환을 안했구나

        hand.layer.remove(blankCard)
        cardDrawn.setDepth(depthDumped)


def dumpAndDrawDet(hand, cardsOn, deckDump, deckDraw):
    ndx1, ndx2 = inHand(hand, cardsOn)
    lis = hand.contents()
    if ndx1 != None:
        dumpAndDraw(hand, deckDump, deckDraw, lis, 0, ndx1)

    elif ndx2 != None:
        dumpAndDraw(hand, deckDump, deckDraw, lis, 1, ndx2)


def make_symbol(symbol, suit):
    """Add suit on layer:symbol"""
    if suit == "Clubs":
        circles = [cm.Circle(RADIUS, cm.Point(0, -RADIUS)),
                   cm.Circle(RADIUS, cm.Point(-RADIUS, RADIUS)),
                   cm.Circle(RADIUS, cm.Point(+RADIUS, RADIUS))]            # 굳이 Point() 해줘야 해?
        for item in circles:
            item.setFillColor('black')
            symbol.add(item)

    if suit == "Diamonds":
        diamond = cm.Square(RADIUS * 3)
        diamond.setFillColor('red')
        diamond.rotate(45)
        symbol.add(diamond)

    if suit == "Hearts":
        circles = [cm.Circle(RADIUS, cm.Point(-RADIUS, -RADIUS)),
                   cm.Circle(RADIUS, cm.Point(+RADIUS, -RADIUS))]
        for item in circles:
            item.setFillColor('red')
            symbol.add(item)
        triangle = cm.Polygon(cm.Point(-RADIUS*2, -RADIUS),
                              cm.Point(+RADIUS*2, -RADIUS),
                              cm.Point(0, RADIUS*2))
        triangle.setFillColor('red')
        triangle.setBorderWidth(0)
        symbol.add(triangle)

    if suit == "Spades":
        triangle = cm.Polygon(cm.Point(-RADIUS * 2, +RADIUS),
                              cm.Point(+RADIUS * 2, +RADIUS),
                              cm.Point(0, -RADIUS * 2))
        triangle.setFillColor('black')
        triangle.setBorderWidth(0)
        symbol.add(triangle)

def show_card(card):
    layersOfCard = card.getContents()
    if layersOfCard[-1].getDepth() == depthBack:
        back = layersOfCard[-1]
        back.setDepth(+1)
        
def move_card(deckFrom, n, deckTo, m, show=False, retCard=False, noDelay=False):

    if len(deckTo) == 0:
        m = None

    cardDrawn = deckFrom.contents()[n]
    coordDrawn = cardDrawn.getReferencePoint().get()

    if show:
        show_card(cardDrawn)

    coordDeckFrom = deckFrom.layer.getReferencePoint().get()
    coordDeckTo = deckTo.layer.getReferencePoint().get()

    if m == None:
        coordTop = (0, 0)
        # coordTop = coordDeckTo
    else:
        cardTop = deckTo.contents()[m]
        coordTop = cardTop.getReferencePoint().get()                        # .get() 은 왜 붙은거지?

    # Animate!
    numSteps = 30
    if noDelay:
        numSteps = 3
    xDist = (coordDeckTo[0] + coordTop[0]) - (coordDeckFrom[0] + coordDrawn[0])
    yDist = (coordDeckTo[1] + coordTop[1]) - (coordDeckFrom[1] + coordDrawn[1])

    sleepTime = 0.0001
    if noDelay:
        sleepTime = 0
    for n in range(numSteps):
        time.sleep(sleepTime)
        cardDrawn.move(xDist / numSteps, yDist / numSteps)
    cardDrawn.moveTo(coordTop[0], coordTop[1])

    # 카드 빼고 더하기
    deckFrom.layer.remove(cardDrawn)
    deckTo.layer.add(cardDrawn)

    # depth 변경
    if m != None:
        depthTop = cardTop.getDepth()
        cardDrawn.setDepth(depthTop - 1)

    if retCard == True:
        cardPlaced = cardDrawn
        return cardPlaced


def getCardValue(card):
    layersOfCard = card.getContents()
    if layersOfCard[-1].getDepth() == depthBack:  # 즉 뒷면장막으로 가려진 hidden 상태일 경우 # 빈카드와 비교할 때는 물론 문제가 생기겠지만 내가 빈카드를 지웠을텐데
        textLayer = layersOfCard[-2]              # deckDraw에서 hand로 더 이상 뽑을 게 없을 때 오류가 난다 IndexError: list index out of range
    else:
        textLayer = layersOfCard[-1]
    num = textLayer.getMessage()
    if num == 'A':
        val = 1
    elif num == 'J':
        val = 11
    elif num == 'Q':
        val = 12
    elif num == 'K':
        val = 13
    else:
        val = int(num)
    return val

# ---------------------------------------------------
# Pre-setting
def setting():

    table = Table().canvas
    w = table.getWidth()
    h = table.getHeight()

    coordDeckDump1 = (w/2 - SIZECARD[0]/2 - 5, h/2)
    coordDeckDump2 = (w/2 + SIZECARD[0]/2 + 5, h/2)
    coordDeckFull = (w/2, h/2)
    coordDeckFlip1 = (coordDeckDump1[0] - SIZECARD[0] - 10, h/2)
    coordDeckFlip2 = (coordDeckDump2[0] + SIZECARD[0] + 10, h/2)
    coordHand1 = (w/2, h - SIZECARD[1]/2 - 10)
    coordHand2 = (w/2, 0 + SIZECARD[1]/2 + 10)
    coordDeckDraw1 = (w - 50, coordHand1[1])
    coordDeckDraw2 = (0 + 50, coordHand2[1])

    deckDump = (Deck([], coordDeckDump1), Deck([], coordDeckDump2))
    deckFlip1 = Deck([], coordDeckFlip1)
    deckFlip2 = Deck([], coordDeckFlip2)
    hand1 = Deck([], coordHand1)
    hand2 = Deck([], coordHand2)
    deckDraw1 = Deck([], coordDeckDraw1)
    deckDraw2 = Deck([], coordDeckDraw2)

    table.add(deckDump[0].layer)
    table.add(deckDump[1].layer)
    table.add(deckFlip1.layer)
    table.add(deckFlip2.layer)
    table.add(hand1.layer)
    table.add(hand2.layer)
    table.add(deckDraw1.layer)
    table.add(deckDraw2.layer)


    cardsFull = []
    for suit in SUITS:
        for face in FACES:
            cardsFull.append(Card(face, suit))

    # Shuffle
    deckFull = Deck(cardsFull, coordDeckFull)
    deckFull.shuffle()

    table.add(deckFull.layer)
    print(len(deckFull)) #
    print(len(deckFull.layer.getContents())) #

    # Give player 5 cards each
    distribute(deckFull, int(5 * 2), hand1, hand2)
    # hand1, hand2 = distribute(deckFull, 5, hand1, hand2)
    hand1.show()
    hand2.show()
    hand1.spread()
    hand2.spread()

    # Make two draw decks of 15 cards each
    distribute(deckFull, int(15 * 2), deckDraw1, deckDraw2)

    # Make two flip decks of 6 cards each
    distribute(deckFull, int(6 * 2), deckFlip1, deckFlip2)

    return deckFull, hand1, hand2, deckDraw1, deckDraw2, deckFlip1, deckFlip2, deckDump

# --------------------------------------------------
# Main Game
def speed_Game():

    iniDecks = setting()

    deckFull = iniDecks[0]
    hand1 = iniDecks[1]
    hand2 = iniDecks[2]
    deckDraw1 = iniDecks[3]
    deckDraw2 = iniDecks[4]
    deckFlip1 = iniDecks[5]
    deckFlip2 = iniDecks[6]
    deckDump = iniDecks[7]

    tStart = time.time()
    print(tStart)
    recorded1 = 0
    recorded2 = 0
    while deckDump == (Deck([]), Deck([])) or (not (len(hand1) == 0 and len(hand2) == 0)): # 아! 한 손만 비었을 때도 이 루프가 실행되는구나

        if len(deckFlip1) == 0 and len(deckFlip2) == 0:
            for n in range(len(deckDump[0]) - 1):
                deckDump[0].dump(deckFull, -1, False, True)
            for n in range(len(deckDump[1]) - 1):
                deckDump[1].dump(deckFull, -1, False, True)
            deckFull.shuffle()
            deckFull.hide()
            distribute(deckFull, len(deckFull), deckFlip1, deckFlip2, True)

        else:                                     
            deckFlip1.dump(deckDump[0], -1)
            deckFlip2.dump(deckDump[1], -1)
            show_card(deckDump[0].contents()[-1])
            show_card(deckDump[1].contents()[-1])
            time.sleep(0.7)                                                        # 뒤집고 뜸 들이는 시간
            cardsOn = (deckDump[0].contents()[-1], deckDump[1].contents()[-1])
            # deckHist = (deckDump[0], deckDump[1])

        # recorded1 = 0
        # recorded2 = 0
        while inHand(hand1, cardsOn) != [None, None] or inHand(hand2, cardsOn) != [None, None]:
            tReact1 = random.random()
            tReact2 = random.random()
            # time.sleep(0.01) # 이걸 안 하니 시간차 인식을 잘 못함

            if tReact1 < tReact2:
                dumpAndDrawDet(hand1, cardsOn, deckDump, deckDraw1)
                if len(hand1) == 0 and recorded1 == 0:
                    tP1End = time.time()                              # 심각한 문제. 측정된 시간이 계속 바뀌어버린다
                    recorded1 +=1
                    print(tP1End) #

            elif tReact1 > tReact2:
                dumpAndDrawDet(hand2, cardsOn, deckDump, deckDraw2)
                if len(hand2) == 0 and recorded2 == 0:
                    tP2End = time.time()
                    recorded2 +=1
                    print(tP2End) #

            else:
                break

            cardsOn = (deckDump[0].contents()[-1], deckDump[1].contents()[-1])


    tP1dur = tP1End - tStart                    # 설마 여기서 문제가 생기는 건 아니겠지
    tP2dur = tP2End - tStart
    return [tP1dur, tP2dur, hand1, hand2, deckDraw1, deckDraw2, deckFlip1, deckFlip2, deckDump[0], deckDump[1]]


# --------------------------------------------------
# 결과 출력

endDecks = speed_Game()

for item in endDecks[2:]:
    print(len(item))

tP1dur = endDecks[0]
tP2dur = endDecks[1]
if tP1dur < tP2dur:
    print("Player1 Won!: %.3f sec taken" % tP1dur)
    print("Player2 Lost: %.3f sec taken" % tP2dur)
elif tP1dur > tP2dur:
    print("Player2 Won!: %.3f sec taken" % tP2dur)
    print("Player1 Lost: %.3f sec taken" % tP1dur)
else:
    print("What a tie!")
