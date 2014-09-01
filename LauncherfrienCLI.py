#!/usr/bin/python

import sys
import socket, ssl
import re
import getpass
import os
import time
from multiprocessing import Process, Queue

def getTicket(username, password, desktop, q):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ssl_sock = ssl.wrap_socket(s)
		ssl_sock.connect(('lp.soe.com', 443))
		ssl_sock.write('POST /eqmac/live/login HTTP/1.1\r\nHost: lp.soe.com\r\nContent-Length: 57\r\n\r\nusername=' + username + '&password=' + password + '&rememberPassword=false\r\n')
		data = ssl_sock.read()
		print 'data recieved is: ' + data
		match = re.search(r'HTTP/1.1 504 Gateway Timeout', data)
		if match:
			oops('Gateway timeout detected! You will have to wait a while in order to log on with account "' + username + '".')
			return
		match = re.search(r'HTTP/1.1 401 Unauthorized', data)
		if match:
			oops('The password of "' + password + '" appears to be wrong.')
			return
		match = re.search(r'Set-Cookie: lp-token=.+\nSet-Cookie: lp-token=(.+); secure', data)
		cookie = match.group(1)
		del ssl_sock
		s.close()

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ssl_sock = ssl.wrap_socket(s)
		ssl_sock.connect(('lp.soe.com', 443))
		ssl_sock.write('POST /eqmac/live/get_play_session HTTP/1.1\r\nHost: lp.soe.com\r\nContent-Length: 16\r\nCookie: lp-token=' + cookie + '\r\n\r\nts=2000000000000\r\n')
		data = ssl_sock.read()
		print 'data recieved is: ' + data
		match = re.search(r'patchme /login:\d+ /ticket:................', data)
		arguments = match.group()
		del ssl_sock
		s.close()

		q.put((arguments, desktop))

	except:
		if s: s.close()
		oops('The request timed out or something else went wrong. Usually, this means a bad account name or password.')		

def useTicket(arguments):
	pid = os.popen('nohup /Users/' + getpass.getuser() + '/Applications/EverQuest\ Mac.app/Contents/MacOS/EverQuest ' + arguments + ' > /dev/null 2> /dev/null & echo $!').read().strip()

def oops(string):
	print "error: " + string

#q = Queue()
#getTicket('corpsefactory2', 'corpsefactory1', '13', q)
useTicket('patchme /login:167483128 /ticket:1K4UGC68TDrPu1YB')
# hifrien's account ID is 167483128