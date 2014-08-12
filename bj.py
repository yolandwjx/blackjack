#!/usr/bin/env python

"""bj.py: A Python based Blackjack game allow user to type in the terminal to play
with simple strategy computer. Featured color output, user defined deck amount, and
more advanced actions include double down, splitting and surrender"""

__author__ = "Jiaxing Wang"
__version__ = "1.0.5"
__email__ = "yolandwjx@gmail.com"
__status__ = "Submission"

import random
import time
import sys

'''This class enable colorful output in terminal'''
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKRED = '\033[91m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'#Back to regular color

'''This class handle UI, mostly static method
For better user experience, both upper and lower string input are acceptable
 in this Class, and will keep asking until get a valid input'''
class UInterface():
	@staticmethod
	def printcolor(msg,color):
		print color+msg+bcolors.ENDC
		time.sleep(1)#for better user experience

	'''Accept the numerical input in a range'''
	@staticmethod
	def asknumber(msg,rangemin,rangemax,color):
		rv=rangemin-1
		#keep trying useless we get a valid number
		while rv<rangemin or rv>rangemax:
			command=raw_input(msg+'(from '+str(rangemin)+' to '+str(rangemax)+'):')
			try:
				rv=int(command)
			except:
				print "Unexpected input:", sys.exc_info()[0]#the user input is not a number
				rv=rangemin-1
		return rv

	'''Ask user to type True or False'''
	@staticmethod
	def askiftrue(msg):
		while True:
			command=raw_input(msg+' [Y]es or [N]o:')
			if command[0]=='Y' or command[0]=='y':
				return True
			elif command[0]=='N' or command[0]=='n':
				return False
			else:
				print 'Invalid Input'
	
	'''The user can select a basic action here'''
	@staticmethod
	def decide(player,deck,other):
		while True:
			UInterface.printcolor(player.name,player.color)
			command=raw_input('[H]it, [S]tay? , [D]ouble Down or [Q]uit:')
			if command[0]=='H' or command[0]=='h':
				player.draw(deck.deal(),deck)#draw one card
			elif command[0]=='S' or command[0]=='s':
				break#end the turn
			elif command[0]=='D' or command[0]=='d':
				if player.is_double_available(player,other)==True:
					UInterface.printcolor(player.name+' double down!',player.color)
					player.draw(deck.deal(),deck)#draw only one more card and end the turn 
					break
			elif command[0]=='Q' or command[0]=='q':
				sys.exit()
			else:
				print 'Invalid Input'

'''This class will create user, dealer, deck object, and also define the work flow which allow 
these three object interact with each other'''
class Game():
	def __init__(self,color):
		self.color=color
		#init the deck
		deck_amount=UInterface.asknumber('How many deck do you want yo use',1,4,self.color)
		self.deck=Deck(deck_amount,bcolors.HEADER)
		self.deck.shuffle()#init shuffle

		#Create Player, Dealer, Split for this game, split object will be used only if the user
		#decide to split, it is a instance of Player class
		self.player=Player(bcolors.OKGREEN,'Player')
		self.split=Player(bcolors.YELLOW,'Split')
		self.dealer=Dealer(bcolors.OKRED)

	#the work flow for the game
	def start(self):
		while True:
			#all reset
			self.player.reset()
			self.dealer.reset()
			self.split.reset()
			UInterface.printcolor('\nNew Round Start!',self.color)
			#Player set bet
			self.player.set_init_bet()
			#Get the initial two cards
			self.dealer.preparehand('Dealer',self.deck)
			self.player.preparehand('Player:',self.deck)
			#if Surrender
			if UInterface.askiftrue('Do you want to Surrender')==True:
				self.player.bet=max(1,self.player.bet/2)#at least one chip lose, prevent bet round to 0
				self.winlose(0,21,self.player,self.player)#feed the function with 0/21 point so the funtion know player lose
				continue
			#if Split
			self.ifsplit=False
			if UInterface.askiftrue('Do you want to split')==True:
				self.ifsplit=self.player.is_double_available(self.player,self.split)#check if user has enough chips to split

			#user has enough chips and choose to split
			if self.ifsplit==True:
				self.split.cards.append(self.player.getsplitcard())#draw one card from the plsyer append to the split
				self.split.draw(self.deck.deal(),self.deck)#split draw another card
				self.split.bet=self.player.bet#the bet is equal

				#player draw another card so both have two cards, and print out current point
				#the two object will have different color so the user can discriminate
				self.split.reveal_get_point(self.deck)
				self.player.draw(self.deck.deal(),self.deck)
				self.player.reveal_get_point(self.deck)

			#user's(and split's if available) turn to choose action
			UInterface.decide(self.player,self.deck,self.split)
			if self.ifsplit==True:
				UInterface.decide(self.split,self.deck,self.player)

			#dealer's turn
			self.dealer.turn(self.deck)
			self.get_result()

	def get_result(self):
		#get the total point and judge 
		my_point=self.player.reveal_get_point(self.deck)
		dealer_point=self.dealer.reveal_get_point(self.deck)
		self.winlose(my_point,dealer_point,self.player,self.player)
		time.sleep(1)
		if self.ifsplit==True:
			my_point=self.split.reveal_get_point(self.deck)
			self.winlose(my_point,dealer_point,self.player,self.split)
			time.sleep(1)
	
	#adjust_balance will add/remove chips, note that we use payer.adjust_balance, so if the "split" object win 
	#or lose chips still the player's balance will be changed
	def winlose(self,my_point,dealer_point,payer,player):
		#both exceed 21 and equal point
		if (my_point>21 and dealer_point>21) or my_point==dealer_point:
			UInterface.printcolor('Draw!',self.color)
		elif my_point>21 or (my_point<dealer_point and dealer_point<=21):
			UInterface.printcolor('You lose '+str(player.bet)+' chips!',self.color)
			payer.adjust_balance(False,player.bet)
		elif dealer_point>21 or (my_point>dealer_point and my_point<=21):
			UInterface.printcolor('You win '+str(player.bet)+' chips!',self.color)
			payer.adjust_balance(True,player.bet)

"""This class define common behavior for both player/split and dealer"""
class Human():
	def __init__(self,color):
		self.color=color

	def reset(self):
		self.bet=0
		self.cards=[]

	def reveal_get_point(self,deck):
		points=deck.evaluate(self.cards)
		UInterface.printcolor(self.name+' Hand:',self.color)
		for card in self.cards:
			print '-['+card+']'
		UInterface.printcolor(self.name+' Total Point:'+str(points),self.color)
		return points

	def preparehand(self,msg,deck):
		self.draw(deck.deal(),deck)
		self.draw(deck.deal(),deck)

"""This class define the Player, which is subclass of Human"""
class Player(Human):
	def __init__(self,color,name):
		Human.__init__(self,color)
		self.chips=100
		self.color=color
		self.name=name

	def set_init_bet(self):
		#each time before the play set the bet, check if player lose all the bet
		if self.chips<=0:
			print 'You lose all your chips!'
			sys.exit()
		self.bet=UInterface.asknumber('How many chips do you want to use',1,self.chips,self.color)
		return self.bet

	#is function is both for split and double down
	def is_double_available(self,current,other):
		if current.chips-current.bet*2-other.bet>0:
			return True
		else:
			UInterface.printcolor('You don not have enough chips!',self.color)
			return False

	def adjust_balance(self,if_win,bet):
		if if_win==True:
			self.chips+=bet
		else:
			self.chips-=bet

	#return a card and remove it from current player, use for split
	def getsplitcard(self):
		card=self.cards[1]
		del self.cards[1]
		return card

	def draw(self,card,deck):
		UInterface.printcolor(self.name+' -Draw ['+card+']',self.color)
		self.cards.append(card)
		UInterface.printcolor(self.name+' Current point is:'+str(deck.evaluate(self.cards)),self.color)


"""This class define the Dealer, which is subclass of Human"""
class Dealer(Human):
	def __init__(self,color):
		Human.__init__(self,color)
		self.name='Dealer'

	def draw(self,card,deck):
		if len(self.cards)<=0:
			#the first card dealer draw is not revealed to the player
			UInterface.printcolor(self.name+' -Draw [?]',self.color)
		else:
			UInterface.printcolor(self.name+' -Draw ['+card+']',self.color)
		self.cards.append(card)

	#dealer will keep drawing card until hit 17
	#we assume dealer will stop hitting even Ace are regard as 11
	def turn(self,deck):
		while deck.evaluate(self.cards)<17:
			self.draw(deck.deal(),deck)
		
"""This class define the deck. The cards in the Deck are store with a array of names, 
e.g. "Hearts 9", and a dictionary of names-value pair, the value of Ace is store as 1 
when the game request a card, the card's name will return"""		
class Deck(object):


	def __init__(self, deck_amount,color):
		self.cards_dict={}#use to index card value
		self.cards_name=[]#cards array used to shuffle
		
		self.deck_amount=deck_amount#how mnay set of cards in one deck
		self.color=color#color to print msg
		self.init_deck()
		self.i = 0#this variable indicate how many cards will have used
		

	def init_deck(self):
		single_cards_name=[]#names for one set of cards
		rank_name=['A','2','3','4','5','6','7','8','9','10','J','Q','K']
		#generate one set
		for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:
			for rank_idx in range(13):
				card_name=suit+' '+rank_name[rank_idx]#e.g. "Hearts 9"
				single_cards_name.append(card_name)
				self.cards_dict[card_name]=min(rank_idx+1,10)#give its value from 1 to 10
		#when we have multiple decks
		for j in range(self.deck_amount):
			self.cards_name=self.cards_name+single_cards_name
		UInterface.printcolor(str(len(self.cards_name))+' cards will be used',self.color)
		
	def shuffle(self):
		UInterface.printcolor('Shuffling...',self.color)
		random.shuffle(self.cards_name)# we only need to shuffle all the cards' name
		self.i = 0

	def deal(self):#return the name of the card
		card_name=self.cards_name[self.i]
		self.i+=1#we will not use used card
		return card_name
		
	#return as large point(but not bust) as possible
	def evaluate(self,cards):
		result=0
		ace_count=0
		for card in cards:
			value=self.cards_dict[card]
			result+=value#first count Ace as 1
			if value==1:
				ace_count+=1#and keep track of the amount of Ace
		while result+10<=21 and ace_count>0:#if this condition hold, then we can treat Ace as 11
			result+=10
			ace_count-=1

		#evaluate mean end of one round, decide here whether it is time to re-shuffle
		#here when we use more than half of all the card then, re-shuffle
		if self.i>self.deck_amount*26:
			self.shuffle()
		return result

'''Entry point of the whole program'''
def main():
    game=Game(bcolors.OKBLUE)
    game.start()
   
if __name__ == '__main__':
    main()


