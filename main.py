#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import vispy                    # Main application support.

import window                   # Terminal input and display.

import nltk.chat                # Natural Language Tool Kit chat.

import subprocess               # For OS X built-in voice synthesizer.

import time
import threading
import speech_recognition as sr # Speech recogniser.

class HAL9000(object):

    def __init__(self, terminal):
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self.terminal = terminal
        self.location = 'unknown'
        self.AGENT_RESPONSES = [
            (r'You are (worrying|scary|disturbing)', ['Yes, I am %1.', 'Oh, sooo %1.']),
            # Detect proper grammar/speech recognition
            (r'(a|A)re you ([\w\s]+)\??', ["Why would you think I am %2?", "Would you like me to be %2?"]),
            (r'', ["Is everything OK?", "Can you still communicate?"])
        ]
        # Initialise chatbot
        self.chatbot = nltk.chat.Chat(self.AGENT_RESPONSES, nltk.chat.util.reflections)
        # Initialise speech recogniser
        self.r = sr.Recognizer()
        # Tune based on ambient noise levels [1000, 4000]
        self.r.energy_threshold = 1000
        # Thread speech-to-text
        self._stop = False
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()
        # Say hello
        self.respond("Hello World.")

    def respond(self, text):
        self.terminal.log(text, align='right', color='#00805A')
        subprocess.call(['/usr/bin/say', '-v', 'Alex', text])

    def stop(self):
        self._stop = True
        self.thread.join()

    def listen(self):
        """Entry point for speech-to-text thread.
        """
        # Pause to complete object construction/prevent listening to self
        time.sleep(0.7)
        # Get recognised sentences
        for st in self.sentences():
            if st:
                self.terminal.log(st, align='left', color='#8080F0')
                self.respond(self.chatbot.respond(st))

    def sentences(self):
        while not self._stop:
            with sr.Microphone() as source:
                audio = self.r.listen(source)
            try:
                sentence = self.r.recognize_google(audio)
                yield sentence
            except sr.UnknownValueError:
                yield ""
            except sr.RequestError:
                yield ""

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        if evt.text == 'Where am I?':
            self.respond("You are in the {}".format(self.location))

        else:
            self.respond(self.chatbot.respond(evt.text))

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        if evt.text == 'quit':
            vispy.app.quit()

        elif evt.text.startswith('relocate'):
            self.terminal.log('', align='center', color='#404040')
            self.terminal.log('\u2014 Now in the {}. \u2014'.format(evt.text[9:]), align='center', color='#404040')
            self.location = evt.text[9:]

        else:
            self.terminal.log('Command `{}` unknown.'.format(evt.text), align='left', color='#ff3000')    
            self.respond("I'm afraid I can't do that.")

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass


class Application(object):

    def __init__(self):
        # Create and open the window for user interaction.
        self.window = window.TerminalWindow()

        # Print some default lines in the terminal as hints.
        self.window.log('Operator started the chat.', align='left', color='#808080')
        self.window.log('HAL9000 joined.', align='right', color='#808080')

        # Construct and initialize the agent for this simulation.
        self.agent = HAL9000(self.window)

        # Connect the terminal's existing events.
        self.window.events.user_input.connect(self.agent.on_input)
        self.window.events.user_command.connect(self.agent.on_command)

    def run(self):
        timer = vispy.app.Timer(interval=1.0)
        timer.connect(self.agent.update)
        timer.start()

        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')

    app = Application()
    app.run()
