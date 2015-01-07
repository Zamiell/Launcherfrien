#! /usr/bin/python

# Imports
import sys # For sys.exit()
import socket, ssl
import re
import getpass
import os
import time
from multiprocessing import Process, Queue
from Tkinter import *
import ConfigParser

# Global variables
version = '1.05'

# The graphical user interface
class GUI:
	def __init__(self, parent):
		parent.geometry('925x350-50-70')
		parent.wm_title('Launcherfrien')

		fairy = PhotoImage(file="./Pictures/fairy.gif")
		w = Label(parent, image=fairy)
		w.fairy = fairy
		w.place(x=10, y=40)

		w = Label(parent, text="Launcherfrien", font=("Helvetica", 18))
		w.place(x=70, y=15)
		w = Label(parent, text="version " + version, font=("Helvetica", 14))
		w.place(x=85, y=40)
		w = Label(parent, text="by Zamiel", font=("Helvetica", 14))
		w.place(x=94, y=72)

		if TotalSpacesRunning:
			w = Label(parent, text="TotalSpaces detected.", font=("Helvetica", 12))
			w.place(x=70, y=272)
		elif osxVersion > 6:
			w = Label(parent, text="Mission Control detected.", font=("Helvetica", 12))
			w.place(x=64, y=272)
		elif VDRunning and spacesRunning:
			w = Label(parent, text="VirtueDesktops and Spaces detected.", font=("Helvetica", 12))
			w.place(x=32, y=272)
		elif VDRunning:
			w = Label(parent, text="VirtueDesktops detected.", font=("Helvetica", 12))
			w.place(x=65, y=272)
		elif spacesRunning:
			w = Label(parent, text="Spaces detected.", font=("Helvetica", 12))
			w.place(x=80, y=272)

		w = Button(parent, text="Quit", command=parent.destroy)
		w.place(x=100, y=300)

		w = Canvas(parent, width=3, height=346)
		w.place(x=258, y=0)
		w.create_rectangle(0, 0, 3, 346, fill="black")

		w = Label(parent, text="Launch by Alias", font=("Helvetica", 16))
		w.place(x=350, y=15)
		w = Button(parent, text="Instructions", command=self.instructions)
		w.place(x=290, y=50)
		w = Button(parent, text="Edit Alias List", command=self.editAliasList)
		w.place(x=410, y=50)
		w = Button(parent, text="Repeat Last Launch", command=self.repeatLastLaunch)
		w.place(x=330, y=85)
		self.aliasHistoryIndex = 0
		self.alias = Entry(parent, width=25)
		self.alias.bind('<Return>', self.launchByAliasPrep)
		self.alias.bind('<Up>', self.upArrow)
		self.alias.bind('<Down>', self.downArrow)
		self.alias.bind('<Command-a>', self.aliasSelectAll)
		self.alias.place(x=300, y=125)
		self.alias.focus_set()

		w = Canvas(parent, width=280, height=1)
		w.place(x=262, y=173)
		w.create_rectangle(0, 0, 280, 3, fill="black")

		w = Label(parent, text="Launch by Account / Password", font=("Helvetica", 16))
		w.place(x=300, y=200)
		w = Label(parent, text="Account:", font=("Helvetica", 14))
		w.place(x=300, y=250)
		self.account = Entry(parent, width=16)
		self.account.bind('<Return>', self.launchByAccountPassword)
		self.account.bind('<Command-a>', self.accountSelectAll)
		self.account.place(x=375, y=248)
		w = Label(parent, text="Password:", font=("Helvetica", 14))
		w.place(x=300, y=280)
		self.password = Entry(parent, width=16, show="*")
		self.password.bind('<Return>', self.launchByAccountPassword)
		self.password.bind('<Command-a>', self.passwordSelectAll)
		self.password.place(x=375, y=278)

		w = Canvas(parent, width=3, height=346)
		w.place(x=542, y=0)
		w.create_rectangle(0, 0, 3, 346, fill="black")

		w = Label(parent, text="Launch by Button", font=("Helvetica", 16))
		w.place(x=575, y=15)
		w = Button(parent, text="Customize Buttons", command=self.customizeButtons)
		w.place(x=562, y=45)
		w = Button(parent, text="Redraw Buttons", command=self.drawButtons)
		w.place(x=572, y=75)
		self.drawButtons()

		w = Canvas(parent, width=3, height=346)
		w.place(x=730, y=0)
		w.create_rectangle(0, 0, 3, 346, fill="black")

		w = Label(parent, text="Miscellaneous", font=("Helvetica", 16))
		w.place(x=780, y=15)

		self.c2var = IntVar()
		self.c2 = Checkbutton(parent, text="Automatically close\nEQ dialog boxes", variable=self.c2var, command=self.closeDialogBoxes, justify=LEFT)
		self.c2.place(x=745, y=90)

		config = ConfigParser.RawConfigParser()
		config.optionxform = str
		config.read('./Config/config.ini')
		if config.get('Main', 'CloseDialogBoxes') == 'Yes':
			self.c2.select()
			temp = os.popen('ps auwx | grep -v grep | grep EQPopupDaemon.py | awk \'{print $2}\'').read().strip()
			if temp == '':
				os.system('./Tools/EQPopupDaemon.py &')

		self.c3var = IntVar()
		self.c3 = Checkbutton(parent, text="Disable Launcherfrien's\nsound effects", variable=self.c3var, command=self.disableSoundCheck, justify=LEFT)
		self.c3.place(x=745, y=130)
		config = ConfigParser.RawConfigParser()
		config.optionxform = str
		config.read('./Config/config.ini')
		if config.get('Main', 'DisableSoundEffects') == 'Yes':
			self.c3.select()
			self.disableSoundEffects = 1
		else:
			self.disableSoundEffects = 0

		w = Button(parent, text="Change Launch Speed for Multiple Accounts", command=self.launchSpeed, wraplength=150)
		w.place(x=747, y=180)

		config = ConfigParser.RawConfigParser()
		config.optionxform = str
		config.read('./Config/config.ini')
		if config.get('Main', 'MultipleAccountLaunchSpeed') == 'Slower':
			self.launchMode = 1
		elif config.get('Main', 'MultipleAccountLaunchSpeed') == 'Slowest':
			self.launchMode = 2
		else:
			self.launchMode = 0

		w = Button(parent, text="Realign Windows", command=self.realignWindows)
		w.place(x=762, y=240)
		if VDRunning:
			w = Button(parent, text="Fix Cursor Pop-out", command=self.activateWindows)
			w.place(x=755, y=280)

	def oops(self, text):
		boxOops = Toplevel()
		boxOops.title("Oops")
		Label(boxOops, text=text).pack(padx=10, pady=10)
		Button(boxOops, text="OK", command=boxOops.destroy).pack(pady=10)

	def aliasSelectAll(self, text):
		self.alias.selection_range(0, END)

	def accountSelectAll(self, text):
		self.account.selection_range(0, END)

	def passwordSelectAll(self, text):
		self.password.selection_range(0, END)

	def upArrow(self, text):
		self.aliasHistoryIndex += 1
		aliasHistory = os.popen('cat ./Config/aliasHistory').read().strip().split('\n')
		if len(aliasHistory) < self.aliasHistoryIndex:
			self.aliasHistoryIndex -= 1
		else:
			value = aliasHistory[-self.aliasHistoryIndex]
			self.alias.delete(0, END)
			self.alias.insert(0, value)
		return 'break'

	def downArrow(self, text):
		self.aliasHistoryIndex -= 1
		if self.aliasHistoryIndex <= 0:
			self.aliasHistoryIndex = 0
			self.alias.delete(0, END)
		else:
			aliasHistory = os.popen('cat ./Config/aliasHistory').read().strip().split('\n')
			value = aliasHistory[-self.aliasHistoryIndex]
			self.alias.delete(0, END)
			self.alias.insert(0, value)
		return 'break'

	def instructions(self):
		boxInstructions = Toplevel()
		boxInstructions.title("Instructions")
		w = Label(boxInstructions, text="\n-  Type the account alias and press enter.", font=("Helvetica", 14))
		w.pack(anchor="w", padx=10)
		if VDRunning == False and spacesRunning == False:
			w = Label(boxInstructions, text="-  You can only log on one account at a time since you don't have VirtueDesktops / Spaces.", font=("Helvetica", 14))
			w.pack(anchor="w", padx=10)
		else:
			w = Label(boxInstructions, text="-  Launch more than one account at a time by separating aliases with spaces.", font=("Helvetica", 14))
			w.pack(anchor="w", padx=10)
			w = Label(boxInstructions, text="   When you hear the second sound effect, Launcherfrien is done launching.", font=("Helvetica", 14))
			w = Label(boxInstructions, text="   See the Launcherfrien post on the TAKP forums for more details.", font=("Helvetica", 14))
			w.pack(anchor="w", padx=10)
			if osxVersion <= 6:
				w = Label(boxInstructions, text="-  Note that you can manually drag EQ instances around using the spaces zoom-out feature if needed.", font=("Helvetica", 14))
				w.pack(anchor="w", padx=10)
				w = Label(boxInstructions, text="   When doing this, if you manage to screw up the window alignment, use the \"Realign Windows\" buttton.", font=("Helvetica", 14))
				w.pack(anchor="w", padx=10)
		w = Label(boxInstructions, text="-  A thunder sound effect means that a crash has occured;", font=("Helvetica", 14))
		w.pack(anchor="w", padx=10)
		w = Label(boxInstructions, text="   Launcherfrien will automatically try to launch the respective account(s) again.", font=("Helvetica", 14))
		w.pack(anchor="w", padx=10)
		w = Label(boxInstructions, text="-  Hint: Use the up and down arrow keys to recall your alias history for quick repeat logons.", font=("Helvetica", 14))
		w.pack(anchor="w", padx=10)
		w = Button(boxInstructions, text="OK", command=boxInstructions.destroy)
		w.pack(pady=10)

	def editAliasList(self):
		try:
			with open('./Config/AliasList.txt'):	pass
			os.system('open -a TextEdit ./Config/AliasList.txt')
		except IOError:
			self.oops('AliasList.txt doesn\'t exist or cannot be opened.')

	def repeatLastLaunch(self):
		aliasHistory = os.popen('cat ./Config/aliasHistory').read().strip().split('\n')
		if len(aliasHistory) < 1:
			self.oops('I can\'t repeat the last launch because you haven\'t launched anything yet, silly!')
		else:
			value = aliasHistory[-1]
			self.launchedByButton = True
			self.launchByAlias(value)

	def customizeButtons(self):
		try:
			with open('./Config/ButtonConfig.txt'):	pass
			os.system('open -a TextEdit ./Config/ButtonConfig.txt')
		except IOError:
			self.oops('ButtonConfig.txt doesn\'t exist or cannot be opened.')

	def drawButtons(self):
		try:
			self.b1.destroy()
		except:
			pass
		try:
			self.b2.destroy()
		except:
			pass
		try:
			self.b3.destroy()
		except:
			pass
		try:
			self.b4.destroy()
		except:
			pass
		try:
			self.b5.destroy()
		except:
			pass
		try:
			self.b6.destroy()
		except:
			pass
		try:
			self.b7.destroy()
		except:
			pass

		temp = os.popen('cat ./Config/ButtonConfig.txt').read().strip()

		match = re.search('Button1\n(.+)\n(.+)', temp)
		if match:
			button1text = match.group(1)
			self.button1alias = match.group(2)
			if button1text != 'Button 1 Title':
				self.b1 = Button(root, text=button1text, command=self.button1)
				self.b1.place(x=562, y=120)

		match = re.search('Button2\n(.+)\n(.+)', temp)
		if match:
			button2text = match.group(1)
			self.button2alias = match.group(2)
			if button2text != 'Button 2 Title':
				self.b2 = Button(root, text=button2text, command=self.button2)
				self.b2.place(x=562, y=150)

		match = re.search('Button3\n(.+)\n(.+)', temp)
		if match:
			button3text = match.group(1)
			self.button3alias = match.group(2)
			if button3text != 'Button 3 Title':
				self.b3 = Button(root, text=button3text, command=self.button3)
				self.b3.place(x=562, y=180)

		match = re.search('Button4\n(.+)\n(.+)', temp)
		if match:
			button4text = match.group(1)
			self.button4alias = match.group(2)
			if button4text != 'Button 4 Title':
				self.b4 = Button(root, text=button4text, command=self.button4)
				self.b4.place(x=562, y=210)

		match = re.search('Button5\n(.+)\n(.+)', temp)
		if match:
			button5text = match.group(1)
			self.button5alias = match.group(2)
			if button5text != 'Button 5 Title':
				self.b5 = Button(root, text=button5text, command=self.button5)
				self.b5.place(x=562, y=240)

		match = re.search('Button6\n(.+)\n(.+)', temp)
		if match:
			button6text = match.group(1)
			self.button6alias = match.group(2)
			if button6text != 'Button 6 Title':
				self.b6 = Button(root, text=button6text, command=self.button6)
				self.b6.place(x=562, y=270)

		match = re.search('Button7\n(.+)\n(.+)', temp)
		if match:
			button7text = match.group(1)
			self.button7alias = match.group(2)
			if button7text != 'Button 7 Title':
				self.b7 = Button(root, text=button7text, command=self.button7)
				self.b7.place(x=562, y=300)

	def button1(self):
		self.launchedByButton = True
		self.launchByAlias(self.button1alias)

	def button2(self):
		self.launchedByButton = True
		self.launchByAlias(self.button2alias)

	def button3(self):
		self.launchedByButton = True
		self.launchByAlias(self.button3alias)

	def button4(self):
		self.launchedByButton = True
		self.launchByAlias(self.button4alias)

	def button5(self):
		self.launchedByButton = True
		self.launchByAlias(self.button5alias)

	def button6(self):
		self.launchedByButton = True
		self.launchByAlias(self.button6alias)

	def button7(self):
		self.launchedByButton = True
		self.launchByAlias(self.button7alias)

	def closeDialogBoxes(self):
		config = ConfigParser.RawConfigParser()
		config.optionxform = str
		config.read('./Config/config.ini')
		temp = os.popen('ps auwx | grep -v grep | grep EQPopupDaemon.py | awk \'{print $2}\'').read().strip()

		if self.c2var.get() == 0:
			if temp != '':
				os.system('kill ' + temp)
			config.set('Main', 'CloseDialogBoxes', 'No')
		else:
			if temp == '':
				os.system('./Tools/EQPopupDaemon.py &')
			config.set('Main', 'CloseDialogBoxes', 'Yes')
		with open('./Config/config.ini', 'wb') as configfile:
			config.write(configfile)

	def disableSoundCheck(self):
		self.disableSoundEffects = self.c3var.get()
		config = ConfigParser.RawConfigParser()
		config.optionxform = str
		config.read('./Config/config.ini')
		if self.disableSoundEffects == 0:
			config.set('Main', 'DisableSoundEffects', 'No')
		else:
			config.set('Main', 'DisableSoundEffects', 'Yes')
		with open('./Config/config.ini', 'wb') as configfile:
			config.write(configfile)

	def launchSpeed(self):
		boxLaunchSpeed = Toplevel()
		boxLaunchSpeed.wm_title("Change Launch Speed")
		w = Label(boxLaunchSpeed, text="", font=("Helvetica", 14))
		w.pack()
		self.c4var = IntVar()
		self.c4 = Checkbutton(boxLaunchSpeed, text="Normal - Log on multiple accounts concurrently. Automatic sorting will only work on OSX 10.6.", variable=self.c4var, command=self.c4command, justify=LEFT)
		self.c4.pack(anchor="w", padx=10)
		self.c5var = IntVar()
		self.c5 = Checkbutton(boxLaunchSpeed, text="Slower - Log on multiple accounts one at a time. This allows automatic sorting on OSX 10.7+.", variable=self.c5var, command=self.c5command, justify=LEFT)
		self.c5.pack(anchor="w", padx=10)
		self.c6var = IntVar()
		self.c6 = Checkbutton(boxLaunchSpeed, text="Slowest - Log on multiple accounts one at a time with cursor activation.", variable=self.c6var, command=self.c6command, justify=LEFT)
		self.c6.pack(anchor="w", padx=10)
		w = Button(boxLaunchSpeed, text="OK", command=boxLaunchSpeed.destroy)
		w.pack(pady=10)

		config = ConfigParser.RawConfigParser()
		config.optionxform = str
		config.read('./Config/config.ini')
		if config.get('Main', 'MultipleAccountLaunchSpeed') == 'Slower':
			self.c5.select()
		elif config.get('Main', 'MultipleAccountLaunchSpeed') == 'Slowest':
			self.c6.select()
		else:
			self.c4.select()

	def c4command(self):
		if self.c4var.get() == 0:
			self.c4.select()
		else:
			self.launchMode = 0
			self.c5.deselect()
			self.c6.deselect()
			config = ConfigParser.RawConfigParser()
			config.optionxform = str
			config.read('./Config/config.ini')
			config.set('Main', 'MultipleAccountLaunchSpeed', 'Normal')
			with open('./Config/config.ini', 'wb') as configfile:
				config.write(configfile)

	def c5command(self):
		if self.c5var.get() == 0:
			self.c5.select()
		else:
			self.launchMode = 1
			self.c4.deselect()
			self.c6.deselect()
			config = ConfigParser.RawConfigParser()
			config.optionxform = str
			config.read('./Config/config.ini')
			config.set('Main', 'MultipleAccountLaunchSpeed', 'Slower')
			with open('./Config/config.ini', 'wb') as configfile:
				config.write(configfile)
			self.oops('I have no idea what your space/desktop hotkeys\nare set to, but this feature will only work\nproperly if you have your hotkeys mapped to\nCommand+1, Command+2, and so forth.\n\nIf you use different hotkeys, see the forum\nthread for instructions on how to manually\ncustomize me.')

	def c6command(self):
		if self.c6var.get() == 0:
			self.c6.select()
		else:
			self.launchMode = 2
			self.c4.deselect()
			self.c5.deselect()
			config = ConfigParser.RawConfigParser()
			config.optionxform = str
			config.read('./Config/config.ini')
			config.set('Main', 'MultipleAccountLaunchSpeed', 'Slowest')
			with open('./Config/config.ini', 'wb') as configfile:
				config.write(configfile)
			self.oops('I have no idea what your space/desktop hotkeys\nare set to, but this feature will only work\nproperly if you have your hotkeys mapped to\nCommand+1, Command+2, and so forth.\n\nIf you use different hotkeys, see the forum\nthread for instructions on how to manually\ncustomize me.')

	def realignWindows(self):
		pids = os.popen('ps auwx | grep -v grep | grep "' + EQPath + '" | awk \'{print $2}\'').read().strip().split()
		success = True
		for pid in pids:
			os.system('./Tools/Activate ' + pid)
			if (os.system('./Tools/EQWindowRealign ' + pid)):
				success = False
		if success:
			if self.disableSoundEffects == 0:
				os.system('afplay ./Sounds/navi.wav &')
		else:
			os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
			os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
			time.sleep(0.1)
			self.oops('I failed realigning all the windows. Do an "/mc i" in all EQ instances and try again.')

	def activateWindows(self):
		pids = os.popen('ps auwx | grep -v grep | grep "' + EQPath + '" | awk \'{print $2}\'').read().strip().split()
		for pid in pids:
			os.system('./Tools/Activate ' + pid)
		if self.disableSoundEffects == 0:
			os.system('afplay ./Sounds/navi.wav &')

	def launchByAccountPassword(self, text):
		# Validate that we have a username and password
		if self.account.get() == '' and self.password.get() == '':
			return
		if self.account.get() == '':
			self.oops('You have to enter an account name.')
			return
		if self.password.get() == '':
			self.oops('You have to enter a password.')
			return

		# Change the graphic and play a sound
		root.geometry('542x350')
		w1 = Canvas(root, width=280, height=350)
		w1.place(x=265, y=0)
		rainbow = PhotoImage(file="./Pictures/rainbow.gif")
		w2 = Label(root, image=rainbow)
		w2.rainbow = rainbow
		w2.place(x=295, y=40)
		w3 = Label(root, text="Launching!", font=("Helvetica", 30))
		w3.place(x=330, y=210)
		if VDRunning:
			w4 = Label(root, text="Switch to the desktop you\nwant the EQ instance to go!", font=("Helvetica", 16))
		elif spacesRunning:
			w4 = Label(root, text="Switch to the space you want\nthe EQ instance to go!", font=("Helvetica", 16))
		else:
			w4 = Label(root, text="", font=("Helvetica", 16))
		w4.place(x=310, y=260)
		root.update_idletasks()
		if self.disableSoundEffects == 0:
			os.system('afplay ./Sounds/magic.mp3 &')

		# Prepare the arguments
		arguments = ('patchme /ticket:' + self.account.get() + '/' + self.password.get(), 99)

		# Launch EQ
		os.system('defaults write com.apple.CrashReporter DialogType none') # Disable the annoying crash popup in case EQ crashes on boot
		q = Queue()
		self.useTicket(arguments[0], arguments[1], q)
		time.sleep(0.1)
		temp = q.get()
		pid = temp[0]
		time.sleep(2)
		os.system('./Tools/Activate ' + pid) # /mc i
		time.sleep(4) # Wait for the EQ instance to fill the screen

		# Check to see if EQ crashed on boot
		temp = os.popen('ps auwx | grep -v grep | grep "' + EQPath + '" | awk \'{print $2}\' | grep ' + pid).read().strip()
		if temp == '': # It crashed
			if self.disableSoundEffects == 0:
				os.system('afplay ./Sounds/thunder.mp3 &')
			q = Queue()
			self.useTicket(arguments[0], arguments[1], q)
			time.sleep(0.1)
			temp = q.get()
			pid = temp[0]
			time.sleep(2)
			os.system('./Tools/Activate ' + pid) # /mc i
			time.sleep(4) # Wait for the EQ instance to fill the screen

			# Check to see if EQ crashed two times in a row
			temp = os.popen('ps auwx | grep -v grep | grep "' + EQPath + '" | awk \'{print $2}\' | grep ' + pid).read().strip()
			if temp == '': # It crashed again
				self.oops('I\'m giving up on launching account ' + self.account.get() + '\nsince it crashed while launching twice in a row.\nThis shouldn\'t normally happen.')
				root.geometry('925x350')
				w1.destroy()
				w2.destroy()
				w3.destroy()
				w4.destroy()
				os.system('defaults write com.apple.CrashReporter DialogType prompt') # Disable the annoying crash popup in case EQ crashes on boot
				return

		# Fix the OSX cursor popout bug with VD
		if VDRunning:
			os.system('./Tools/Activate ' + pid)
			time.sleep(0.1)
			os.system('osascript -e \'tell application "Finder" to activate\'')
			time.sleep(0.1)
			os.system('./Tools/Activate ' + pid)
			time.sleep(0.1)

		self.account.delete(0, END)
		self.password.delete(0, END)
		self.account.focus_set()
		root.geometry('925x350')
		w1.destroy()
		w2.destroy()
		w3.destroy()
		w4.destroy()
		os.system('defaults write com.apple.CrashReporter DialogType prompt') # Disable the annoying crash popup in case EQ crashes on boot

	def launchByAliasPrep(self, text):
		self.launchedByButton = False
		value = text.widget.get()
		self.launchByAlias(value)

	def launchByAlias(self, text):
		# Validate that the user entered something other than spaces
		text = text.strip()
		if text == '':
			return

		# Validate that AliasList.txt still exists
		try:
			with open('./Config/AliasList.txt'): pass
		except IOError:
			self.oops('AliasList.txt doesn\'t exist or cannot be opened.')
			return

		# Go through all of the aliases that the user entered
		nameList = text.split()
		usernameList = []
		passwordList = []
		desktopList = []
		for name in nameList:
			try:
				with open('./Config/AliasList.txt') as f:
					username = ''
					for line in f:
						match = re.search('^' + name + ' ', line, re.IGNORECASE)
						if match:
							array = line.split()
							username = array[1]
							usernameList.append(array[1])
							passwordList.append(array[2])
							try:
								desktopList.append(array[3])
							except IndexError:
								desktopList.append(99)
							try:
								int(array[3])
							except:
								self.oops('One of your default spaces is not a number.')
								return
							if int(array[3]) < 1:
								self.oops('One of your default spaces is 0 or less. Fix it, loser.')
								return
							try:
								eqclientini = array[4]
							except IndexError:
								eqclientini = 'eqclient.ini'
							break
			except IndexError:
				self.oops('There is a formatting error in your AliasList.txt.')
				return
			if username == '':
				self.oops('Could not find "' + name + '" in AliasList.txt.')
				return

		# Return if the usernameList is blank for some reason
		if usernameList == []:
			return

		# If we are launching more than one instance, validate that we can launch more than one instance
		if len(usernameList) > 1:
			if VDRunning == False and spacesRunning == False:
		 		self.oops('You need either VirtueDesktops or Spaces to launch more than one account at a time.')
		 		return
			if VDRunning and spacesRunning == False:
				self.oops('You must have Spaces enabled to launch more than one account at a time.\n(VirtueDesktops and Spaces can function concurrently.)')
				return
		 	if VDRunning and VDMisconfigured:
			 	self.oops('In order to launch more than one account at a time, you will need your VirtueDesktops properly configured.\nRight now, some of your desktops are inproperly named.\nSet up your desktops with names from "1" to "16" and make sure they align properly with the respective Spaces.')
			 	return

		# Validate that the custom eqclient.ini files are present
		if len(usernameList) == 1 and eqclientini != 'eqclient.ini':
			try:
				with open('/Users/' + getpass.getuser() + '/Library/Application Support/EverQuest/' + eqclientini): pass
			except IOError:
				self.oops('I can\'t find the custom eqclient.ini file that is supposed to be at:\n/Users/' + getpass.getuser() + '/Library/Application Support/EverQuest/' + eqclientini)
				return
			os.system('cp /Users/' + getpass.getuser() + '/Library/Application\ Support/EverQuest/' + eqclientini + ' /Users/' + getpass.getuser() + '/Library/Application\ Support/EverQuest/eqclient.ini')

		# Update the alias history
		if self.launchedByButton == False:
			self.alias.delete(0, END)
			self.aliasHistoryIndex = 0
			os.system('sed -i "" -e "/^' + text + '$/d" ./Config/aliasHistory') # Delete all past occurances of this alias
			aliasHistory = os.popen('cat ./Config/aliasHistory').read().strip().split('\n')
			if len(aliasHistory) > 100:
				os.system('sed -i "" -e "1d" ./Config/aliasHistory') # Remove the first line
			os.system('echo ' + text + ' >> ./Config/aliasHistory')

		# Change the graphic and play a sound
		root.geometry('542x350')
		w1 = Canvas(root, width=270, height=350)
		w1.place(x=265, y=0)
		rainbow = PhotoImage(file="./Pictures/rainbow.gif")
		w2 = Label(root, image=rainbow)
		w2.rainbow = rainbow
		w2.place(x=295, y=40)
		w3 = Label(root, text="Launching!", font=("Helvetica", 30))
		w3.place(x=330, y=210)
		if len(usernameList) > 1:
			if osxVersion > 6:
				if self.launchMode > 0:
					w4 = Label(root, text="Don't switch spaces;\nI'll take care of everything!", font=("Helvetica", 16))
					w4.place(x=315, y=260)
				else:
					w4 = Label(root, text="Switch to the space you want\nall of the EQ instances to go!", font=("Helvetica", 16))
					w4.place(x=302, y=260)
			elif VDRunning:
				w4 = Label(root, text="Don't switch desktops;\nI'll take care of everything!", font=("Helvetica", 16))
				w4.place(x=315, y=260)
			else:
				w4 = Label(root, text="Don't switch spaces;\nI'll take care of everything!", font=("Helvetica", 16))
				w4.place(x=315, y=260)
		else:
			if VDRunning:
				w4 = Label(root, text="Switch to the desktop you\nwant the EQ instance to go!", font=("Helvetica", 16))
			else:
				w4 = Label(root, text="Switch to the space you want\nthe EQ instance to go!", font=("Helvetica", 16))
			w4.place(x=310, y=260)
		root.update_idletasks()
		if self.disableSoundEffects == 0:
			os.system('afplay ./Sounds/magic.mp3 &')
		errorHappened = False

		# Make an arguments list
		argumentsList = []
		for i in range(len(usernameList)):
			argumentsList.append(('patchme /ticket:' + usernameList[i] + '/' + passwordList[i], desktopList[i]))

		# We are doing concurrent launching
		if len(usernameList) == 1 or self.launchMode == 0:
			os.system('defaults write com.apple.CrashReporter DialogType none') # Disable the annoying crash popup in case EQ crashes on boot
			p = []
			q = Queue()
			for i in range(len(argumentsList)):
				p.append(Process(target=self.useTicket, args=(argumentsList[i][0], argumentsList[i][1], q,)))
				p[i].start()
			for i in range(len(p)):
				p[i].join()
			time.sleep(0.1)
			pidList = []
			while q.empty() == False:
				pidList.append(q.get())
			time.sleep(2)
			os.system('./Tools/Activate ' + pidList[0][0]) # /mc i, can only do one of them though
			time.sleep(4) # Wait for the EQ instance to fill the screen

			# Check to see if any of the instances crashed on boot
			crashedArgsList = []
			i = 0
			while i < len(pidList):
				temp = os.popen('ps auwx | grep -v grep | grep "' + EQPath + '" | awk \'{print $2}\' | grep ' + pidList[i][0]).read().strip()
				if temp == '': # It crashed
					if self.disableSoundEffects == 0:
						os.system('afplay ./Sounds/thunder.mp3 &')
					crashedDesktop = pidList[i][1]
					pidList.remove(pidList[i])
					i -= 1
					j = 0
					while j < len(argumentsList): # Find the corresponding arguments
						temp = os.popen('ps auwx | grep -v grep | grep "' + EQPath + '" | grep "' + argumentsList[j][0] + '"').read().strip()
						if temp == '':
							if argumentsList[j][1] == crashedDesktop:
								crashedArgsList.append((argumentsList[j][0], crashedDesktop))
								break
						j += 1
				i += 1

			# One or more instances crashed
			if len(crashedArgsList) > 0:
				p = []
				q = Queue()
				for i in range(len(crashedArgsList)):
					p.append(Process(target=self.useTicket, args=(crashedArgsList[i][0], crashedArgsList[i][1], q,)))
					p[i].start()
				for i in range(len(p)):
					p[i].join()
				time.sleep(0.1)
				crashedPIDList = []
				while q.empty() == False:
					temp = q.get()
					pidList.append(temp)
					crashedPIDList.append(temp)
				time.sleep(2)
				os.system('./Tools/Activate ' + crashedPIDList[0][0]) # /mc i, can only do one of them though
				time.sleep(4) # Wait for the EQ instance to fill the screen

				# Check to see if the same instance crashed twice in a row
				for pid in crashedPIDList:
					temp = os.popen('ps auwx | grep -v grep | grep "' + EQPath + '" | awk \'{print $2}\' | grep ' + pid[0]).read().strip()
					if temp == '': # It crashed again
						if len(usernameList) > 1:
							self.oops('I\'m giving up on launching one or more accounts\nsince it crashed while launching twice in a row.\nThis shouldn\'t normally happen.\nI\'ll still log in the other accounts, though.')
						else:
							self.oops('I\'m giving up on launching account ' + usernameList[0] + '\nsince it crashed while launching twice in a row.\nThis shouldn\'t normally happen.')

			# Move the EQ window to the intended space; this will only work on OSX 10.6
			if osxVersion <= 6 and len(usernameList) > 1:
				for pid in pidList:
					temp = os.popen('./Tools/EQGetWID ' + pid[0]).read().strip()
					match = re.search(r'(\d+) \d+', temp)
					os.system('./Tools/MoveWindow ' + match.group(1) + ' ' + pid[1])

		# We are logging on multiple characters one at a time
		else:
			# Start EQ #1 after 2 seconds, EQ #2 after 4 seconds, EQ #3 after 6 seconds, and so forth
			p = []
			q = Queue()
			for i in range(len(argumentsList)):
				p.append(Process(target=self.useTicketDelayed, args=(argumentsList[i][0], argumentsList[i][1], q, i,)))
				p[i].start()
			time.sleep(0.1)

			# Switch to the space for this EQ instance
			pidList = []
			for i in range(len(argumentsList)):
				if argumentsList[i][1] == '1':
					os.system('osascript -e \'tell application "System Events" to key code {18} using command down\'') # 1
				elif argumentsList[i][1] == '2':
					os.system('osascript -e \'tell application "System Events" to key code {19} using command down\'') # 2
				elif argumentsList[i][1] == '3':
					os.system('osascript -e \'tell application "System Events" to key code {20} using command down\'') # 3
				elif argumentsList[i][1] == '4':
					os.system('osascript -e \'tell application "System Events" to key code {21} using command down\'') # 4
				elif argumentsList[i][1] == '5':
					os.system('osascript -e \'tell application "System Events" to key code {23} using command down\'') # 5
				elif argumentsList[i][1] == '6':
					os.system('osascript -e \'tell application "System Events" to key code {22} using command down\'') # 6
				elif argumentsList[i][1] == '7':
					os.system('osascript -e \'tell application "System Events" to key code {26} using command down\'') # 7
				elif argumentsList[i][1] == '8':
					os.system('osascript -e \'tell application "System Events" to key code {28} using command down\'') # 8
				elif argumentsList[i][1] == '9':
					os.system('osascript -e \'tell application "System Events" to key code {25} using command down\'') # 9
				elif argumentsList[i][1] == '10':
					os.system('osascript -e \'tell application "System Events" to key code {29} using command down\'') # 0
				elif argumentsList[i][1] == '11':
					os.system('osascript -e \'tell application "System Events" to key code {18} using {command down, shift down}\'') # 1
				elif argumentsList[i][1] == '12':
					os.system('osascript -e \'tell application "System Events" to key code {19} using {command down, shift down}\'') # 2
				elif argumentsList[i][1] == '13':
					os.system('osascript -e \'tell application "System Events" to key code {20} using {command down, shift down}\'') # 3
				elif argumentsList[i][1] == '14':
					os.system('osascript -e \'tell application "System Events" to key code {21} using {command down, shift down}\'') # 4
				elif argumentsList[i][1] == '15':
					os.system('osascript -e \'tell application "System Events" to key code {23} using {command down, shift down}\'') # 5
				elif argumentsList[i][1] == '16':
					os.system('osascript -e \'tell application "System Events" to key code {22} using {command down, shift down}\'') # 6

				pidList.append(q.get())

				# Try to automatically /mc i
				if self.launchMode == 2:
					endTime = time.time() + 0.5 # 0.75 is too high
					while time.time() <= endTime:
						os.system('./Tools/Activate ' + pidList[i][0]) # Try to activate constantly because it can't hurt anything

				# Wait for EQ to open
				while True:
					if os.system('./Tools/EQIsWindowOpen ' + pidList[i][0]) == 0:
						break

		# Fix the OSX cursor popout bug with VD
		if VDRunning:
			for pid in pidList:
				os.system('./Tools/Activate ' + pid[0])
				time.sleep(0.1)
				os.system('osascript -e \'tell application "Finder" to activate\'')
				time.sleep(0.1)
				os.system('./Tools/Activate ' + pid[0])
				time.sleep(0.1)

		# Done
		if self.disableSoundEffects == 0:
			os.system('afplay ./Sounds/success.mp3 &')
		root.geometry('925x350')
		w1.destroy()
		w2.destroy()
		w3.destroy()
		w4.destroy()
		os.system('defaults write com.apple.CrashReporter DialogType prompt') # Disable the annoying crash popup in case EQ crashes on boot
		if errorHappened:
			os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
			os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
			time.sleep(0.1)

	def useTicket(self, arguments, desktop, q):
		pid = os.popen('nohup "' + EQPath + '" ' + arguments + ' > /dev/null 2> /dev/null & echo $!').read().strip()
		q.put((pid, desktop))

	def useTicketDelayed(self, arguments, desktop, q, i):
		if self.launchMode == 2:
			time.sleep(i * 2)
		else:
			time.sleep(i)
		self.useTicket(arguments, desktop, q)

# --------------------
#  The main function
# --------------------

# Validate that the tools are executable
if not os.access("./Tools/Activate", os.X_OK):
	os.system('chmod +x ./Tools/Activate')
if not os.access("./Tools/AssistiveDevicesCheck", os.X_OK):
	os.system('chmod +x ./Tools/AssistiveDevicesCheck')
if not os.access("./Tools/EQGetWID", os.X_OK):
	os.system('chmod +x ./Tools/EQGetWID')
if not os.access("./Tools/EQGetWIDAll", os.X_OK):
	os.system('chmod +x ./Tools/EQGetWIDAll')
if not os.access("./Tools/EQIsWindowOpen", os.X_OK):
	os.system('chmod +x ./Tools/EQIsWindowOpen')
if not os.access("./Tools/EQPopupDaemon.py", os.X_OK):
	os.system('chmod +x ./Tools/EQPopupDaemon.py')
if not os.access("./Tools/EQPopupDetect", os.X_OK):
	os.system('chmod +x ./Tools/EQPopupDetect')
if not os.access("./Tools/EQWindowRealign", os.X_OK):
	os.system('chmod +x ./Tools/EQWindowRealign')
if not os.access("./Tools/GetCurrentSpace", os.X_OK):
	os.system('chmod +x ./Tools/GetCurrentSpace')
if not os.access("./Tools/MoveWindow", os.X_OK):
	os.system('chmod +x ./Tools/MoveWindow')
if not os.access("./Tools/spaces-util", os.X_OK):
	os.system('chmod +x ./Tools/spaces-util')
if not os.access("./Tools/GetWindowList", os.X_OK):
	os.system('chmod +x ./Tools/GetWindowList')

# Try to find out where the EverQuest is installed
if os.path.exists('/Applications/EverQuest.app/Contents/MacOS/EverQuest'):
	EQPath = '/Applications/EverQuest.app/Contents/MacOS/EverQuest'
elif os.path.exists('/Applications/EverQuest Mac.app/Contents/MacOS/EverQuest'):
	EQPath = '/Applications/EverQuest Mac.app/Contents/MacOS/EverQuest'
elif os.path.exists('/Users/' + getpass.getuser() + '/Applications/EverQuest.app/Contents/MacOS/EverQuest'):
	EQPath = '/Users/' + getpass.getuser() + '/Applications/EverQuest.app/Contents/MacOS/EverQuest'
elif os.path.exists('/Users/' + getpass.getuser() + '/Applications/EverQuest Mac.app/Contents/MacOS/EverQuest'):
	EQPath = '/Users/' + getpass.getuser() + '/Applications/EverQuest Mac.app/Contents/MacOS/EverQuest'
elif os.path.exists('/Applications/EverQuest Mac Test.app/Contents/MacOS/EverQuest'):
	EQPath = '/Applications/EverQuest Mac Test.app/Contents/MacOS/EverQuest'
elif os.path.exists('/Users/' + getpass.getuser() + '/Applications/EverQuest Mac Test.app/Contents/MacOS/EverQuest'):
	EQPath = '/Applications/EverQuest Mac Test.app/Contents/MacOS/EverQuest'
else:
	EQPathBox = Tk()
	EQPathBox.wm_title("Launcherfrien")
	w = Label(EQPathBox, text="I can't find out where your EverQuest application\nis located. Try putting EverQuest in the\n\"/Applications\" directory.")
	w.pack(padx=10, pady=10)
	w = Button(EQPathBox, text="OK", command=EQPathBox.destroy)
	w.pack(pady=10)
	os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
	os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
	EQPathBox.mainloop()
	sys.exit(1)

# Validate that the eqhost.txt is correct
EQDirectory = EQPath[:-16] # Strip off the /MacOS/EverQuest
temp = os.popen('md5 "' + EQDirectory + '/Resources/eqhost.txt"').read().strip()
match = re.search(r'MD5 \(.+\) = (.+)', temp)
if match:
	if not match.group(1) == '0ebc749efae3cc9c2c5e5483be8871c1':
		# Create a new "eqhost.txt" from scratch
		os.system('echo "[Registration Servers]" > "' + EQDirectory + '/Resources/eqhost.txt"')
		os.system('echo "{" >> "' + EQDirectory + '/Resources/eqhost.txt"')
		os.system('echo \'"loginserver.takproject.net:6000"\' >> "' + EQDirectory + '/Resources/eqhost.txt"')
		os.system('echo "}" >> "' + EQDirectory + '/Resources/eqhost.txt"')
		os.system('echo "[Login Servers]" >> "' + EQDirectory + '/Resources/eqhost.txt"')
		os.system('echo "{" >> "' + EQDirectory + '/Resources/eqhost.txt"')
		os.system('echo \'"loginserver.takproject.net:6000"\' >> "' + EQDirectory + '/Resources/eqhost.txt"')
		os.system('echo "}" >> "' + EQDirectory + '/Resources/eqhost.txt"')

		# Let the user know what we did
		EQHostBox = Tk()
		EQHostBox.wm_title("Launcherfrien")
		w = Label(EQHostBox, text="Your \"eqhost.txt\" file was wrong. Don't worry, I've took the liberty to fix it for you.")
		w.pack(padx=10, pady=10)
		w = Button(EQHostBox, text="OK", command=EQHostBox.destroy)
		w.pack(pady=10)
		os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
		os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
		EQHostBox.mainloop()

# Validate that AliasList.txt exists
try:
	with open('./Config/AliasList.txt'): pass
except IOError:
	os.system('touch ./Config/AliasList.txt')

# Validate that aliasHistory exists
try:
	with open('./Config/aliasHistory'): pass
except IOError:
	os.system('touch ./Config/aliasHistory')

# Validate that ButtonConfig.txt exists
try:
	with open('./Config/ButtonConfig.txt'): pass
except IOError:
	os.system('touch ./Config/ButtonConfig.txt')

# Validate that config.ini exists
try:
	with open('./Config/config.ini'): pass
except IOError:
	config = ConfigParser.RawConfigParser()
	config.optionxform = str
	config.add_section('Main')
	config.set('Main', 'CloseDialogBoxes', 'No')
	config.set('Main', 'VirtueDesktopsConfiguredCorrectly', 'No')
	config.set('Main', 'DisableSoundEffects', 'No')
	config.set('Main', 'MultipleAccountLaunchSpeed', 'Normal')
	with open('./Config/config.ini', 'wb') as configfile:
		config.write(configfile)

# Get the current version of OSX
temp = os.popen('osascript -e \'system version of (system info)\'').read().strip()
match = re.search(r'\d+\.(\d+)\.\d+', temp)
if match:
	osxVersion = int(match.group(1))
else:
	match = re.search(r'\d+\.(\d+)', temp)
	osxVersion = int(match.group(1))

# Check to see if Launcherfrien has access to assistive devices in the OSX system preferences
temp = os.popen('./Tools/AssistiveDevicesCheck').read().strip()
if temp == '0':
	assistiveDevicesBox = Tk()
	assistiveDevicesBox.wm_title("Launcherfrien")
	if osxVersion == 8:
		w = Label(assistiveDevicesBox, text="In order to use Launcherfrien you have to turn on\n\"Enable access for assistive devices\" in\nSystem Preferences --> Accessibility.")
	elif osxVersion > 8:
		w = Label(assistiveDevicesBox, text="In order to use Launcherfrien you have to enable it\nin the \"Accessibility\" section in\nSystem Preferences --> Security & Privacy.")
	else:
		w = Label(assistiveDevicesBox, text="In order to use Launcherfrien you have to turn on\n\"Enable access for assistive devices\" in\nSystem Preferences --> Universal Access.")
	w.pack(padx=10, pady=10)
	w = Button(assistiveDevicesBox, text="OK", command=assistiveDevicesBox.destroy)
	w.pack(pady=10)
	os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
	os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
	assistiveDevicesBox.mainloop()
	sys.exit(1)

# Check to see if TotalSpaces is running
temp = os.popen('ps auwx | grep -v grep | grep TotalSpaces').read().strip()
if temp == '':
	TotalSpacesRunning = False
else:
	TotalSpacesRunning = True

# Check to see if Spaces is running
temp = os.popen('./Tools/spaces-util -n').read().strip()
if temp == 'Spaces is not enabled':
	spacesRunning = False
else:
	spacesRunning = True

# Check to see if VirtueDesktops is running
temp = os.popen('ps auwx | grep -v grep | grep VirtueDesktops.app').read().strip()
if temp == '':
	VDRunning = False
else:
	VDRunning = True

# Used in the popup box for VD/Spaces validation
def checkVDBoxConfirm():
	global timeForSwitching
	timeForSwitching = True
	checkVDBox.destroy()

# Confirm that VirtueDesktops will play nicely with Spaces
if spacesRunning and VDRunning:
	VDMisconfigured = False
	config = ConfigParser.RawConfigParser()
	config.optionxform = str
	config.read('./Config/config.ini')
	if config.get('Main', 'VirtueDesktopsConfiguredCorrectly') == 'No':
		timeForSwitching = False
		checkVDBox = Tk()
		checkVDBox.wm_title("Launcherfrien")
		w = Label(checkVDBox, text="I have to check to see if your\nVirtueDesktops is set up properly.\nOnce I confirm that it is, I'll\nremember and won't ask you again.")
		w.pack(padx=10, pady=10)
		w = Button(checkVDBox, text="Okay", command=checkVDBoxConfirm)
		w.pack(side="left", padx=10, pady=10)
		w = Button(checkVDBox, text="Not Now", command=checkVDBox.destroy)
		w.pack(side="right", padx=20, pady=10)
		os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
		os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
		checkVDBox.mainloop()

		# The user consented to doing the check
		if timeForSwitching:
			currentDesktop = os.popen('osascript -e \'tell application "VirtueDesktops" to get title of active desktop\'').read().strip()
			for i in range(1, 17):
				temp = os.popen('osascript -e \'tell application "VirtueDesktops" to show desktop "' + str(i) + '"\' 2>&1').read().strip()
				match = re.search(r'execution error: VirtueDesktops got an error', temp)
				if match:
					VDErrorBox = Tk()
					VDErrorBox.wm_title("Oops")
					w = Label(VDErrorBox, text="You don't have a desktop named " + str(i) + ".\nLauncherfrien will still work, but it won't be able to launch more than one account at a time.")
					w.pack(padx=10, pady=10)
					w = Button(VDErrorBox, text="OK", command=VDErrorBox.destroy)
					w.pack(pady=10)
					os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
					os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
					VDErrorBox.mainloop()
					VDMisconfigured == True
					break

				time.sleep(0.1)
				temp = os.popen('./Tools/GetCurrentSpace').read().strip()
				if temp != str(i):
					VDErrorBox = Tk()
					VDErrorBox.wm_title("Oops")
					w = Label(VDErrorBox, text="Desktop " + str(i) + " is aligned with space " + temp + ". That's bad.\nLauncherfrien will still work, but it won't be able to launch more than one account at a time.")
					w.pack(padx=10, pady=10)
					w = Button(VDErrorBox, text="OK", command=VDErrorBox.destroy)
					w.pack(pady=10)
					os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
					os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
					VDErrorBox.mainloop()
					VDMisconfigured == True

			os.system('osascript -e \'tell application "VirtueDesktops" to show desktop "' + currentDesktop + '"\'')
			if VDMisconfigured == False:
				VDSuccessBox = Tk()
				VDSuccessBox.wm_title("Success")
				w = Label(VDSuccessBox, text="Everything looks good!")
				w.pack(padx=10, pady=10)
				w = Button(VDSuccessBox, text="OK", command=VDSuccessBox.destroy)
				w.pack(pady=10)
				os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
				os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
				VDSuccessBox.mainloop()
				config = ConfigParser.RawConfigParser()
				config.optionxform = str
				config.read('./Config/config.ini')
				config.set('Main', 'VirtueDesktopsConfiguredCorrectly', 'Yes')
				with open('./Config/config.ini', 'wb') as configfile:
					config.write(configfile)

# Start the GUI
root = Tk()
gui = GUI(root)
os.system('osascript -e \'tell application "System Events" to tell process "Python" to activate\'')
os.system('osascript -e \'tell application "System Events" to set frontmost of process "Python" to true\'')
root.mainloop()
