"""
# Python 3 

# Portfolio.py
# A program that allow recording current portfolio value, adding new investmnet, removing investment
# The program will have four big function, buy, sell, modified (for inaccurate information), main
# The program will have sub function for handling calculation of book cost after selling
# The program will check if there's already a csv file for portfolio if not, it will create one from scratch

""" 


# import function
import os
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# portfolio class
class Port:
	#initialize the portfolio
	def __init__(self):
		self.port = pd.DataFrame()
		self.name = ''

	# A function to create an empty dataframe to store the portfolio, can import portfolio through csv 
	def open_port(self,name):
		self.name = name
		try:
			self.port = pd.read_csv(name,index_col=0)
			Port.update_all(self)
			Port.show_port(self)
		except:
			self.port = pd.DataFrame(columns = ['Market Price','Currency','Type','Book Cost','Average Cost','Quantity','Market Value','Unrealized gain or loss'])
			cash_us = input('How many USD you have?\n')
			cash_ca = input('How many CAD you have?\n')
			if float(cash_us) != 0:
				Port.contri(self,'CASH-US','USD',cash_us)
			if float(cash_ca) != 0:
				Port.contri(self,'CASH-CA','CAD',cash_ca)
			Port.show_port(self)
	
	# Using the symbol as a key, check if the investment exist, if it do, update quantity, cost and average price. If the investment doesn't exist add a new entry to the dataframe
	def buy(self, symbol, currency, type ,cost, quantity):
		# Getting the market price of the product
		marketp = Port.market_price(self,symbol)
		# Use the key error as an indication if a certain investment exist
		try:
			self.port.loc[symbol]
			Current_records = self.port.loc[[symbol]]
			Now_book = float(Current_records['Book Cost']) + float(cost)
			Now_quant = int(Current_records['Quantity']) + int(quantity)
			marketv = Port.market_value(self,marketp,Now_quant)
			average = cal_avg(Now_book,Now_quant)
			self.port.loc[symbol]=[marketp,currency,type,Now_book,average,Now_quant,marketv,marketv-Now_book]
			print('\nInvestment successfully added\n')
			print(self.port.loc[symbol])
		except KeyError:
			average = cal_avg(cost,quantity)
			marketv = Port.market_value(self,marketp,int(quantity))
			self.port.loc[symbol]=[marketp,currency,type,cost,average,quantity,marketv,marketv-float(cost)]
			print('\nInvestment successfully added\n')
			print(self.port.loc[symbol])
		# Deduct the amount of cash from the purchase
		if currency.upper() == 'USD':
				Port.contri(self,'CASH-US','USD',-float(cost))
		elif currency.upper() == 'CAD':
				Port.contri(self,'CASH-CA','CAD',-float(cost))

	
	# A function to sell investment in your portfolio, the function the new quantity, new book cost, new average cost, and quantity equal to 0 after selling it removed the entry
	def sell(self, symbol, quantity, amount):
		try:
			Current_records = self.port.loc[[symbol]]
			currency = Current_records["Currency"][0]
			currency = currency.upper()
			if currency == 'USD':
				Port.contri(self,'CASH-US','USD',float(amount))
			elif currency == 'CAD':
				Port.contri(self,'CASH-CA','CAD',float(amount))
			New_quantity = Current_records['Quantity']-int(quantity)
			if New_quantity[0] != 0:
				New_book = Current_records['Average Cost']*New_quantity
				New_marketv = Port.market_value(self,Current_records['Market Price'][0],New_quantity[0])
				self.port.loc[symbol,'Quantity']=New_quantity[0]
				self.port.loc[symbol,'Book Cost']=New_book[0]
				self.port.loc[symbol,'Market Value']= New_marketv
				self.port.loc[symbol,'Unrealized gain or loss']=New_marketv - New_book[0]
				print('\nInvestment successfully removed\n')
				print(self.port.loc[symbol])
			else:
				self.port = self.port.drop([symbol])
				print('\nInvestment successfully removed\n')
		except KeyError:
			print('\nNo investment with the name {} is found in your portfolio\n'.format(symbol))
	
	# A specific function for cash contribution, can also be used later if a trading is found profitable
	def contri(self,symbol,currency,amount):
		try:
			self.port.loc[symbol]
			amount = float(amount)
			Current_records = self.port.loc[[symbol]]
			Now_book = float(Current_records['Book Cost']) + float(amount)
			self.port.loc[symbol]=[Now_book,currency,'CASH',Now_book,Now_book,1,Now_book,0]
			if float(amount)>0:
				print('\n${} added, your new balance\n'.format(amount))
				print(self.port.loc[symbol])
			else:
				print('\n${} removed, your new balance\n'.format(-amount))
				print(self.port.loc[symbol])
		except KeyError:
			amount = float(amount)
			self.port.loc[symbol]=[amount,currency,'CASH',amount,amount,1,amount,0]
			print('\n${} added\n'.format(amount))
			print(self.port.loc[symbol])
	
	# A function to transfer investment to the current portfolio
	def transfer(self, symbol, currency, type ,cost, quantity):
		# Getting the market price of the product
		marketp = Port.market_price(self,symbol)
		# Use the key error as an indication if a certain investment exist
		try:
			self.port.loc[symbol]
			Current_records = self.port.loc[[symbol]]
			Now_book = float(Current_records['Book Cost']) + float(cost)
			Now_quant = int(Current_records['Quantity']) + int(quantity)
			average = cal_avg(Now_book,Now_quant)
			marketv = Port.market_value(self,marketp,Now_quant)
			self.port.loc[symbol]=[marketp,currency,type,Now_book[0],average,Now_quant[0],marketv,marketv-Now_book[0]]
			print('\nInvestment successfully added\n')
			print(self.port.loc[symbol])
		except KeyError:
			average = cal_avg(cost,quantity)
			marketv = Port.market_value(self,marketp,quantity)
			self.port.loc[symbol]=[marketp,currency,type,cost,average,quantity,marketv,marketv-float(cost)]
			print('\nInvestment successfully added\n')
			print(self.port.loc[symbol])
	
	# Getting newest prices
	def market_price(self,symbol):
		information = yf.Ticker(symbol)
		current_price = information.history(period='1d')
		current_price = round((current_price['Close'])[0],2)
		return current_price

	# Calculating Market Value of your investmnet
	def market_value(self,price,quantity):
		return round(price*quantity,2)

	# A function that update all market price and market value 
	def update_all(self):
		for item in self.port.index:
			if not (item == 'CASH-US' or item == 'CASH-CA'):
				marketp = Port.market_price(self,item)
				quantity = self.port.loc[item]['Quantity']
				marketv = Port.market_value(self,marketp,quantity)
				self.port.loc[item,'Market Price']=marketp
				self.port.loc[item, 'Market Value']=marketv
				self.port.loc[item, 'Unrealized gain or loss']= marketv-self.port.loc[item]['Book Cost']
		self.port = self.port.sort_values(by='Market Value')
				
				
	
	# A function to show current portfolio market value
	def total_marketv(self):
		print('*'*60)
		print("$"+str(self.port['Market Value'].sum()))
		print('*'*60)
	
	# Show total unrealized gain or loss
	def total_unreal(self):
		print('*'*60)
		print("$"+str(self.port['Unrealized gain or loss'].sum()))
		print('*'*60)	
	
	# A function to auto change your portfolio by reading your trading recorder
	def auto_trade(self,name):
		trade_record = pd.read_csv(name,index_col=0)
		for item in trade_record.index:
			print(trade_record.loc[item]['Action'])
			if trade_record.loc[item]['Action'] == 'BUY':
				Port.buy(self, trade_record.loc[item]['Company'], trade_record.loc[item]['Currency'], trade_record.loc[item]['Type'],trade_record.loc[item]['Amount'], trade_record.loc[item]['Quantity'])
			elif trade_record.loc[item,'Action'] == 'SOLD' or trade_record.loc[item,'Action'] == 'SELL':
				Port.sell(self,trade_record.loc[item]['Company'], trade_record.loc[item]['Quantity'], trade_record.loc[item]['Amount'])
			elif trade_record.loc[item,'Action']=='CONTRI':
				Port.contri(self,trade_record.loc[item]['Company'], trade_record.loc[item]['Currency'], trade_record.loc[item]['Amount'])
			else:
				print('Cannot identify action, make sure you use BUY, SOLD, SELL, CONTRI')
		
	# A function to show the current portfolio
	def show_port(self):
		print()
		print('*'*120)
		print(self.port)
		print('*'*120)
		print()
	
	# Show a bar chart of market value
	def show_barm(self):
		print()
		ax = self.port.plot.barh(y='Market Value', title=self.name)
		plt.show()
		print()

	# A function to save the current portfolio
	def sav_port(self,name):
		self.port.to_csv(name)
		print("*"*30+'File saved'+"*"*30)


# sub function
# A function to calculate the average cost of an investment
def cal_avg(cost,quantity):
	try:
		cost = float(cost)
		quantity = float(quantity)
		return cost/quantity
	except:
		print("Please make sure quantity and cost are not string")


# Main function, a text base UI allow user to access their portfolio and perform action.
def main():
	portfolio = Port()
	path = "./portfolios"
	files = os.listdir(path)
	print("Which portfolio would you like to open today? Please input the full name of the portfolio\n")
	print('*'*100)
	for file in files: 
		print(file)
	print('*'*100)
	option = ''
	choice = input()
	choice = path+'/' +choice 
	print(choice)
	portfolio.open_port(choice)
	while option != ':q':
		option = input("Type b to buy an investment.\nType s to sell an investment.\nType c to contribute cash to your account,\nType t to transfer investment to your account.\nType m! to show the current market value of your portfolio. (Recommend updating your portfolio first.) \nType u! to show the total unrealized gain or loss of your portfolio\nType :u to update your portfolio to the latest prices.\nType :a to update your portfolio using trading record\nType :s to show your portfolio.\nType :g to show a horizontal bar chart representation of your portfolio market value\nType :q to quit and save your portfolio\n")
		option = option.lower()
		if option == 'b':
			symbol = input("Symbol: ")
			currency = input("Currency: ")
			type = input("Type: ")
			cost = input("Cost: ")
			quantity = input("Quantity: ")
			portfolio.buy(symbol.upper(),currency.upper(),type.upper(),float(cost),int(quantity))
		if option == 's':
			symbol = input("Symbol: ")
			quantity = input("Quantity: ")
			amount = input("Amount: ")
			portfolio.sell(symbol.upper(),int(quantity),float(amount))
		if option == 'c':
			symbol = input("Symbol: ")
			currency = input("Currency: ")
			amount = input("Amount: ")
			portfolio.contri(symbol.upper(),currency.upper(),float(amount))
		if option == 't':
			symbol = input("Symbol: ")
			currency = input("Currency: ")
			type = input("Type: ")
			cost = input("Cost: ")
			quantity = input("Quantity: ")
			portfolio.transfer(symbol.upper(),currency.upper(),type.upper(),float(cost),int(quantity))
		if option == 'm!':
			portfolio.total_marketv()
		if option == 'u!':
			portfolio.total_unreal()
		if option == ':u':
			portfolio.update_all()
		if option == ':a':
			recordname = input("\nPlease input the name of the record.\n")
			portfolio.auto_trade(recordname)
		if option == ':s':
			portfolio.show_port()
		if option == ':g':
			portfolio.show_barm()
	portfolio.sav_port(choice)
		




###############################TEST-FUNCTION####################################

if __name__ == "__main__":
	main()
