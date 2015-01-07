#!/usr/bin/python

import os
import re
import time

temp = os.popen('ps auwx | grep -v grep | grep VirtueDesktops.app').read().strip()
if temp == '':
	VDRunning = False
else:
	VDRunning = True

currentSpace = 0
popupPIDList = []

while True:
	# check for new popups
	temp = os.popen('./Tools/EQPopupDetect').read().strip().split()
	if len(temp) != 0:
		currentSpace = os.popen('./Tools/GetCurrentSpace').read().strip()
		for i in temp:
			notInList = True
			for j in popupPIDList:
				if i ==  j[0]:
					notInList = False
					break
			if notInList:
				start = time.time()
				popupPIDList.append((i, start))
				if VDRunning:
					temp = os.popen('./Tools/EQGetWID ' + i).read().strip()
					match = re.search(r'(\d+)$', temp)
					os.system('osascript -e \'tell application "VirtueDesktops" to show desktop "' + match.group(1) + '"\'')
				else:
					os.system('./Tools/Activate ' + i)
				time.sleep(0.1)
				os.system('osascript -e \'tell application "System Events" to keystroke return\'')
				time.sleep(0.1)

	# switch back
	if currentSpace != 0:
		if VDRunning:	
			os.system('osascript -e \'tell application "VirtueDesktops" to show desktop "' + currentSpace + '"\'')
		else:
			time.sleep(0.2) # need the popup to close for this next part to work
			temp = os.popen('./Tools/EQGetWIDAll').read().strip()
			match = re.search(r'(\d+) \d+ ' + currentSpace, temp)
			if match:
				os.system('./Tools/Activate ' + match.group(1))
		currentSpace = 0

	# check for timer expiration
	i = 0
	while i < len(popupPIDList):
		temp = time.time()
		temp -= popupPIDList[i][1]
		if temp > 2:
			popupPIDList.remove(popupPIDList[i])
			i -= 1
		i += 1;

	# check for Launcherfrien closing
	temp = os.popen('ps auwx | grep -v grep | grep Launcherfrien').read().strip()
	if temp == '':
		exit(0)

	# sleep
	time.sleep(0.1)