from collections import deque
from pyllist import dllist
import keyboard
import time
import json
import random

PlayersHealthStart = 50
PlayersCardAmmount=45

class node:
    def __init__(self,data):
        self.data=data
        self.prev=None
        self.next=None
        
class cdll(dllist):
    def __init__(self):
        self.start=None
        
    def insert_last(self,data):
        n = node(data)
        if self.start is None:
            n.prev = n
            n.next = n
            self.start = n
        else:
            n.next = self.start
            n.prev = self.start.prev
            self.start.prev.next = n
            self.start.prev = n
    
    def delete_at_position(self, pos):
        if self.start is None:
            return None

        current = self.start
        count = 0

        while count < pos:
            current = current.next
            count += 1
            if current == self.start:
                return None

        current.prev.next = current.next
        current.next.prev = current.prev

        if current == self.start:
            self.start = current.next

        del current
    
    def display(self):
        if self.start is None:
            print("Hand is empty")
            return
        current = self.start
        while True:
            print(f"{current.data.cardInfo} - {current.data.cardEffectName}: {current.data.cardEffect}", end=" | ")
            current = current.next
            if current is self.start:
                break
        print()

class Cards:
    def __init__(self, cardInfo, cardEffectName, cardEffect, Amount):
        self.cardInfo = cardInfo
        self.cardEffectName = cardEffectName
        self.cardEffect = cardEffect
        self.Amount = Amount

    @classmethod
    def from_json(cls, card_data):
        return cls(
            cardInfo=card_data["Name"],
            cardEffectName=card_data["EffectName"],
            cardEffect=card_data["Effect"],
            Amount=card_data["Amount"]
        )

    def ReadCards(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            cards_array = [Cards.from_json(card) for card in data["cards"]]
        return cards_array

class BasePlayer:
    def __init__(self, Turn):
        self.cardCount = PlayersCardAmmount
        self.hand = cdll()
        self.health = PlayersHealthStart
        self.status = ["None", "None", "None", "None"]
        self.statusTime = [0, 0, 0, 0]
        self.turn = Turn
        self.deck = deque()
        self.cardsInHand = 0
 
    def InitializeDeck(self, cards):
        self.deck.clear()
        total_cards = 0
        remaining_cards = self.cardCount
        selected_cards = []

        for card in cards:

            if remaining_cards == 0:
                break
            selected_amount = card.Amount

            if selected_amount > remaining_cards:
                selected_amount = remaining_cards

            self.deck.extend([card] * selected_amount)
            total_cards += selected_amount
            remaining_cards -= selected_amount
            selected_cards.append((card.cardInfo, selected_amount))

            if remaining_cards == 0:
                break

        random.shuffle(self.deck)
        self.cardCount=PlayersCardAmmount

    def DrawCard(self,cards):
        if self.deck:
            card = self.deck.popleft()
            self.hand.insert_last(card)
            self.cardsInHand += 1
            self.cardCount-=1
        else: 
            self.InitializeDeck(cards)
    
    def GetCardsPerTurn(self,cards):
        for _ in range(3):
            self.DrawCard(cards)
    
    def EndOfTurn(self):
        while(self.cardsInHand>4):
            rCard = random.randrange(1, self.cardsInHand) 
            self.hand.delete_at_position(rCard)
            self.cardsInHand -= 1
           
class Cat(BasePlayer):
    def ChooseCard(self):
        pos = 0
        hand_size = self.cardsInHand
        self.hand.display()
        print(f"Card: {pos + 1}")
        while not keyboard.is_pressed('space'):
            if keyboard.is_pressed('left') or keyboard.is_pressed('right'):
                print("\033[A\033[A", end="")
                if keyboard.is_pressed('left'):
                    pos = (pos - 1) % hand_size 
                    time.sleep(0.2)
                elif keyboard.is_pressed('right'):
                    pos = (pos + 1) % hand_size
                    time.sleep(0.2)
                self.hand.display()
                print(f"Card: {pos + 1}")
            time.sleep(0.2)

        current = self.hand.start
        for _ in range(pos):
            current = current.next
        self.hand.delete_at_position(pos)
        self.cardsInHand -= 1
        print(f"Selected card: {current.data.cardInfo} - {current.data.cardEffect}")
        return current.data  # Return the selected card
    
class Dog(BasePlayer):
    def Decide(self):
        pos = random.randrange(1,self.cardsInHand)
        current = self.hand.start
        for _ in range(pos):
             current = current.next
        self.hand.delete_at_position(pos)
        self.cardsInHand -= 1
        print(f"BOB choose card: {current.data.cardInfo} - {current.data.cardEffect}")
        return current.data

def StartGame():
    time.sleep(1)
    cards = Cards.ReadCards('cards.json') 
    Kitten = Cat(Turn=1)
    Puppy = Dog(Turn=0) 
    Kitten.InitializeDeck(cards)
    Puppy.InitializeDeck(cards)
    while Kitten.health>0 and Puppy.health > 0: 
        time.sleep(0.5)
        print("\033c", end="")
        if Puppy.turn==1:
            Puppy.GetCardsPerTurn(cards)
            GamePlayUI(Kitten, Puppy)
            Kitten.turn=1
            Puppy.turn=0
            time.sleep(3)
            continue
        else:
            Kitten.GetCardsPerTurn(cards)
            GamePlayUI(Kitten, Puppy)
            Kitten.turn=0
            Puppy.turn=1
            time.sleep(2)
            continue
    if(Puppy.health<0):
        print("\033c", end="")
        print("YOU WON")
        time.sleep(10)
        exit
    else:
        print("\033c", end="")
        print("YOU LOST")
        time.sleep(10)
        exit
        
    

def GamePlayUI(Kitten, Puppy):
    print("\033c", end="")
    print("===============================================================================================")
    for i in range(4):
        if(Puppy.status[i]=="Heal Overtime" and  Puppy.statusTime[i]>0):
            Puppy.health+=1
            Puppy.statusTime[i]-=1
            print(f"BOB WAS HEALED {Puppy.health}")
        if(Kitten.status[i]=="Heal Overtime" and Kitten.statusTime[i]>0):
            Kitten.health+=1 
            Kitten.statusTime[i]-=1
            print(f"YOUR WERE HEALED {Kitten.health}")
    print("===============================================================================================")
    if Puppy.turn==1:
        print("\t\t\t\t\tBOB'S TURN")
    else:
        print("\t\t\t\t\tYOUR TURN")
    print("===============================================================================================")
    print(f"BOB'S HEALTH: {Puppy.health} \nBOB'S DECK SIZE: {Puppy.cardCount}")
    for _ in range(Puppy.cardsInHand):
        print("**************", end=" ")
    if Puppy.turn==1:
        print()
        cardUsed = Puppy.Decide()
        if cardUsed.cardEffectName=="Damage":
            Kitten.health-=cardUsed.cardEffect
        elif cardUsed.cardEffectName=="Burn" or cardUsed.cardEffectName=="Stun":
            for i in range(4):
                if(Kitten.statusTime[i]==0):
                    Kitten.status[i]=cardUsed.cardEffectName
                    Kitten.statusTime[i]=cardUsed.cardEffect
                    break
        elif cardUsed.cardEffectName=="Heal Overtime":
            for i in range(4):
                if(Puppy.statusTime[i]==0):
                    Puppy.status[i]=cardUsed.cardEffectName
                    Puppy.statusTime[i]=cardUsed.cardEffect
                    break
        elif cardUsed.cardEffectName=="Heal":
            Puppy.health+=cardUsed.cardEffect
            print(f"BOB WAS HEALED {Puppy.health}")
        Puppy.EndOfTurn()
    else:
        print("")
    print()
    print("===============================================================================================")
    print(f"YOUR HEALTH: {Kitten.health} \nYOUR DECK SIZE: {Kitten.cardCount}")
    if Kitten.turn==1:
        cardUsed = Kitten.ChooseCard()
        if cardUsed.cardEffectName=="Damage":
            Puppy.health-=cardUsed.cardEffect
        elif cardUsed.cardEffectName=="Burn" or cardUsed.cardEffectName=="Stun":
            for i in range(4):
                if(Puppy.statusTime[i]==0):
                    Puppy.status[i]=cardUsed.cardEffectName
                    Puppy.statusTime[i]=cardUsed.cardEffect
                    break
        elif cardUsed.cardEffectName=="Heal Overtime":
            for i in range(4):
                if(Kitten.statusTime[i]==0):
                    Kitten.status[i]=cardUsed.cardEffectName
                    Kitten.statusTime[i]=cardUsed.cardEffect
                    break
        elif cardUsed.cardEffectName=="Heal":
            Kitten.health+=cardUsed.cardEffect
            print(f"YOUR WERE HEALED {Kitten.health}")
        Kitten.EndOfTurn()
    else:
        Kitten.hand.display()
    print("===============================================================================================")
    for i in range(4):
        if(Puppy.status[i]=="Burn" and  Puppy.statusTime[i]>0):
            Puppy.health-=2
            Puppy.statusTime[i]-=1
            print(f"BOB WAS BURNED {Puppy.health}")
        if(Kitten.status[i]=="Burn" and Kitten.statusTime[i]>0):
            Kitten.health-=2
            Kitten.statusTime[i]-=1
            print(f"YOUR WERE BURNED {Kitten.health}")
    print("===============================================================================================")

def Meniu():
    print("\033c", end="")
    print("=================================================================")
    print("||                                                             ||")
    print("||  ||||||      ||||||    ||                  ||  ||||||||||   ||")
    print("||  ||    ||  ||      ||  ||                  ||  ||           ||")
    print("||  ||    ||  ||      ||  ||                  ||  ||           ||")
    print("||  ||    ||  ||      ||  ||        ||        ||  ||           ||")
    print("||  ||||||    ||      ||   ||      ||||      ||   ||||||||||   ||")
    print("||  ||        ||||||||||    ||     ||||     ||            ||   ||")
    print("||  ||        ||      ||    ||    ||  ||    ||            ||   ||")
    print("||  ||        ||      ||       ||        ||       ||||||||||   ||")
    print("||                                                             ||")
    print("=================================================================")
    print('\n')
    print("                         Start")
    print("                 (Press space to start)")
    print('\n')
    while not keyboard.is_pressed('space'):
        pass
    print("\033c", end="")
    StartGame()

Meniu()