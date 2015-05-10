#	Copyright (c) 2014, Andrea Esposito <info@andreaesposito.org>
#	All rights reserved.
#
#	Redistribution and use in source and binary forms, with or without
#	modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Andrea Esposito nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
#	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#	ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#	DISCLAIMED. IN NO EVENT SHALL Andrea Esposito BE LIABLE FOR ANY
#	DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#	(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#	LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#	ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#	(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#	SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

if __name__ == '__main__':
	import configparser
	import threading
	import socket
	import requests
	import re
	import base64
	import Vigenere
	import LogManager
	import webbrowser
	import sys
	from PyQt5.QtWidgets import (QApplication, QWidget, QSystemTrayIcon, QMenu, QAction, QInputDialog, QLineEdit, QMessageBox, QTextEdit, QSizePolicy)
	from PyQt5.QtGui import QIcon
	from PyQt5.QtCore import Qt
	
	app = QApplication(sys.argv)
	wParent = QWidget()
	
	if not QSystemTrayIcon.isSystemTrayAvailable():
		QMessageBox.critical(None, "Systray", "I couldn't detect any system tray on this system.")
		sys.exit(1)		
	QApplication.setQuitOnLastWindowClosed(False)
	
	icon = 'icon/SerraAutoLogin.ico'
	hover_text = "SerraAutoLogin"
	
	LogManager.createLog()
	
	LogManager.log("Reading Config file...")
	config = configparser.ConfigParser()
	config.read('config.ini')
	username = config.get('SerraAutoLogin', 'Username')
	password = Vigenere.decryptMessage("NoobTest", config.get('SerraAutoLogin', 'cryptedpassword'))
	url = config.get('SerraAutoLogin', 'Url')
	loginAtStartup = config.get('SerraAutoLogin', 'loginAtStartup')
	time = int(config.get('SerraAutoLogin', 'Time'))
	firstRun = config.get('SerraAutoLogin', 'FirstRun') == '1'
	LogManager.log("Config file loaded successfully")
	
	leftTime = time
	
	def timerFunc():
		global leftTime
		global time
		if leftTime <= 0:
			login(True)
			leftTime = time
		startTimer()
	
	def startTimer():
		global timer
		global leftTime
		actualTime = leftTime if leftTime <= 30 else 30
		leftTime = leftTime - actualTime
		timer = threading.Timer(actualTime * 60.0, timerFunc)
		timer.daemon = True
		timer.start() 
		LogManager.log("Login Daemon Started")
		
	def stopTimer():
		global timer
		global leftTime
		global time
		LogManager.log("Old Login Daemon Cancelled")
		timer.cancel()
		leftTime = time
	
	def find_ip():
		LogManager.log("Searching IP Address...")
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("gmail.com",80))
		ip = s.getsockname()[0]
		s.close()
		LogManager.log("IP Address found: ("+ip+")")
		return ip
	
	def login(showIcon = True):
		global username
		global password
		global url
		global trayIcon
		if showIcon:
			trayIcon.setIcon(QIcon('icon/SerraAutoLogin_login.ico'))
		
		LogManager.log("Login function started")
		LogManager.log("NOTICE: This version of the app doesn't work in presence of the 'Remove Old Session' checkbox. Sorry.")
		
		ip = find_ip()
		
		host = re.findall(r"/[a-zA-Z0-9:/._?=&%]*[a-zA-Z0-9:/._?=&%]", url)[0][2:]
		
		headers = {
		"Host": host,
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:26.0) Gecko/20100101 Firefox/35.0",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "en,en-us;q=0.8,it-it;q=0.5,it;q=0.3",
		"Accept-Encoding": "gzip, deflate",
		"Connection": "keep-alive"
		}
		LogManager.log("Discovering redirect url...")
		r = requests.get(url, headers=headers, verify=False)
		realUrl = re.findall(r"URL=[a-zA-Z0-9:/._?=&%]*[a-zA-Z0-9:/._?=&%]", r.text)[0][4:]
		LogManager.log("Real URL = "+realUrl)
		r = requests.get(realUrl, headers=headers, verify=False)
		postAttr = {
		"reqFrom":"perfigo_login.jsp",
		"uri":url+"/",
		"session":"",
		"cm":"ws32vklm",
		"userip":ip,
		"pm":"",
		"index":"5",
		"pageid":"-1",
		"compact":"false",
		"registerGuest":"NO",
		"userNameLabel":"Username",
		"passwordLabel":"Password",
		"guestUserNameLabel":"Guest ID",
		"guestPasswordLabel":"Password",
		"username":username,
		"password":password,
		"provider":"AAA - UniPi",
		"submit": "Continua"
		}
		headers_post = {
		"Host": host,
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:26.0) Gecko/20100101 Firefox/35.0",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Origin": url,
		"Accept-Language": "it-IT,it;q=0.8,en-US;q=0.6,en;q=0.4",
		"Accept-Encoding": "gzip, deflate",
		"Referer": "https://"+host+"/auth/perfigo_cm_validate.jsp",
		"Connection": "keep-alive"
		}
		p = requests.post("https://"+host+"/auth/perfigo_cm_validate.jsp", postAttr, headers=headers_post, cookies={"JSESSIONID":r.cookies["JSESSIONID"]}, verify=False)
		status = "LOGGED IN" if len(re.findall(r"Logon Information", p.text)) > 0 else "FAILED LOGIN"
		LogManager.log("Login function ended. Status: "+status)
		
		if showIcon:
			trayIcon.setIcon(QIcon('icon/SerraAutoLogin.ico'))
			
	def updateConfig():
		global username
		global password
		global time
		global url
		global loginAtStartup
		LogManager.log("Updating config file...")
		file = open('config.ini', 'w')
		config = configparser.ConfigParser()
		config.add_section('SerraAutoLogin')
		config.set('SerraAutoLogin', 'Username', username)
		config.set('SerraAutoLogin', 'cryptedpassword', Vigenere.encryptMessage("NoobTest", password))
		config.set('SerraAutoLogin', 'Url', url)
		config.set('SerraAutoLogin', 'loginAtStartup', loginAtStartup)
		config.set('SerraAutoLogin', 'Time', str(time))
		config.set('SerraAutoLogin', 'FirstRun', '0')
		config.write(file)
		file.close()
		LogManager.log("Config file updated")
		stopTimer()
		startTimer()

	def changeUsername(): 
		global username
		global wParent
		reply, ok = QInputDialog.getText(wParent, "Username", "Insert your Serra Username", QLineEdit.Normal, username)
		if ok:
			username = reply
			updateConfig()
	def changePassword(): 
		global password
		global wParent
		reply, ok = QInputDialog.getText(wParent, "Password", "Insert your Serra Password", QLineEdit.Password, password)
		if ok:
			password = reply
			updateConfig()
	def changeUrl(): 
		global url
		global wParent
		reply, ok = QInputDialog.getText(wParent, "Serra Site Url", "Insert Serra site URL (without '/' at the end)", QLineEdit.Normal, url)
		if ok:
			url = reply
			updateConfig()
	def changeTime(sysTrayIcon): 
		global time
		global wParent
		reply, ok = QInputDialog.getInt(wParent, "Login interval", "Set login interval in minutes", time, 30, 200)
		if ok:
			time = reply
			updateConfig()
	def changeLoginAtStartup():
		global loginAtStartup
		global wParent
		msgBox = QMessageBox(wParent)
		msgBox.setWindowTitle("Login at Startup")
		msgBox.setText("")
		msgBox.setInformativeText("Do you want login at the app startup?")
		msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		msgBox.setDefaultButton(QMessageBox.Yes)
		ret = msgBox.exec()
		reply = ret == QMessageBox.Yes
		loginAtStartup = str(reply)
		updateConfig()
	def doLoginNow(sysTrayIcon):
		stopTimer()
		login(sysTrayIcon != None)
		startTimer()
	def showLog():
		#textEdit = QTextEdit(str(LogManager.readLog()))
		#textEdit.show()
		msgBox = QMessageBox(QMessageBox.Information, "SerraAutoLogin Log", "", QMessageBox.NoButton, wParent)
		msgBox.setInformativeText("SerraAutoLogin Log History")
		msgBox.setDetailedText(str(LogManager.readLog()))
		msgBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		msgBox.exec()
	
	def about():
		global wParent
		image = "about.gif"
		msg   = "\t               'SerraAutoLogin' v. 1.1.0\n\t                           created by\n        Andrea Esposito <info@andreaesposito.org>.\n\n*** If you like my work buy me a cup of coffee, thanks. ***"
		choices = ["Donate","Close"]
		msgBox = QMessageBox(wParent)
		msgBox.setWindowTitle("About")
		msgBox.setText("")
		msgBox.setInformativeText(msg)
		donateBtn = msgBox.addButton("Donate", QMessageBox.AcceptRole)
		closeBtn = msgBox.addButton(QMessageBox.Close)
		msgBox.exec()
		if msgBox.clickedButton() == donateBtn:
			webbrowser.open("https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=and1989%40gmail%2ecom&lc=IT&item_name=Andrea%20Esposito&item_number=SerraAutoLogin&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted", new=2)
	
	startTimer()
	
	if firstRun:
		LogManager.log("FirstRun procedure starting...")
		changeUsername()
		changePassword()
		doLoginNow(None)
		LogManager.log("FirstRun procedure Ended")
	else:
		if loginAtStartup == 'True':
			doLoginNow(None)
	
	trayIcon = QSystemTrayIcon(QIcon(icon), wParent)
	
	# Actions
	loginAction = QAction("Do Login Now", wParent, triggered=doLoginNow)
	
	setUserAction = QAction("Set Username", wParent, triggered=changeUsername)
	setPswAction = QAction("Set Password", wParent, triggered=changePassword)
	setUrlAction = QAction("Set Serra URL", wParent, triggered=changeUrl)
	setStartupLoginAction = QAction("Set Login at Startup", wParent, triggered=changeLoginAtStartup)
	setIntervalAction = QAction("Set Login Interval", wParent, triggered=changeTime)	
	
	showLogAction = QAction("Show Log", wParent, triggered=showLog)
	aboutAction = QAction("About", wParent, triggered=about)
	exitAction = QAction("Exit", wParent, triggered=app.quit)
	
	# Menus
	menu = QMenu(wParent)
	menu.addAction(loginAction)
	settingsMenu = menu.addMenu("Settings")
	settingsMenu.addAction(setUserAction)
	settingsMenu.addAction(setPswAction)
	settingsMenu.addAction(setUrlAction)
	settingsMenu.addAction(setStartupLoginAction)
	settingsMenu.addAction(setIntervalAction)
	menu.addAction(showLogAction)
	menu.addAction(aboutAction)
	menu.addAction(exitAction)
	
	trayIcon.setContextMenu(menu)
	trayIcon.show()	
	#trayIcon.showMessage("Titolo Prova", "Test Prova")
	
	sys.exit(app.exec_())
