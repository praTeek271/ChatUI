import sys
import os
import wave
import threading
import pyaudio
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPainterPath, QRegion
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt
from pydub import AudioSegment
import speech_recognition as sr

class VoiceRecorderApp(QWidget):
    '''
    A class representing a voice recorder application.

    Attributes:
        audio_format (int): The audio format for recording.
        channels (int): The number of audio channels.
        sample_rate (int): The sample rate for recording.
        chunk_size (int): The chunk size for recording.
        audio_frames (list): A list to store the recorded audio frames.
        recording (bool): A flag indicating whether recording is in progress.

    Methods:
        printME(): Prints a custom ASCII art.
        init_ui(): Initializes the user interface.
        close_dialog(): Closes the application.
        set_mask(): Sets the rounded corners for the application window.
        toggle_recording(): Toggles the recording state.
        start_recording(): Starts the audio recording.
        record_audio(): Records audio frames.
        stop_recording(): Stops the audio recording.
        recognize(): Runs speech recognition on the recorded audio.
        save_audio(): Saves the recorded audio to a WAV file.
        convert_audio_to_text(file_path): Converts audio to text using speech recognition.
    '''
    def __init__(self, channel=1):
        self.printME()
        super().__init__()
        self.init_ui()
        # Audio recording variables
        self.audio_format = pyaudio.paInt16
        self.channels = channel
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.audio_frames = []
        self.recording = False

        # Start recording automatically
        self.toggle_recording()

    def printME(self):
        
            print("""
    ██████╗ ██████╗  █████╗ ████████╗███████╗███████╗██╗  ██╗    ██████╗ ███████╗ ██╗
    ██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔════╝██║ ██╔╝    ╚════██╗╚════██║███║
    ██████╔╝██████╔╝███████║   ██║   █████╗  █████╗  █████╔╝      █████╔╝    ██╔╝╚██║
    ██╔═══╝ ██╔══██╗██╔══██║   ██║   ██╔══╝  ██╔══╝  ██╔═██╗     ██╔═══╝    ██╔╝  ██║
    ██║     ██║  ██║██║  ██║   ██║   ███████╗███████╗██║  ██╗    ███████╗   ██║   ██║
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝    ╚══════╝   ╚═╝   ╚═╝
    """)

    def init_ui(self):
        self.setWindowTitle('')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.setStyleSheet("background-color: #f1f1f1; border-radius: 10px;")
        self.setLayout(layout)
        # 
        # # Set rounded corners
        # self.set_mask()
        # rect = self.rect()
        # rect.adjust(-10, -10, 10, 10)

        # Label to display the GIF animation
        self.movie_screen = QLabel(self)
        self.movie = QMovie("ai_gf.gif")
        self.movie.setScaledSize(self.size())
        self.movie_screen.setMovie(self.movie)

        # Close button
        self.btn_close = QPushButton('✕', self)
        self.btn_close.clicked.connect(self.close_dialog)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setStyleSheet("QPushButton { background-color: #a3a0a0; color: black; border: none; border-radius: 5px;}")

        # Label to display status text
        self.label_status = QLabel('Ready to record...')
        self.label_status.setStyleSheet("QLabel { color: grey}")
        self.label_status.setAlignment(Qt.AlignCenter)

        # Button to toggle recording
        self.btn_record = QPushButton('🎙')
        self.btn_record.setStyleSheet("QPushButton { background-color: #77DD77; border: none; border-radius: 5px; padding: 5px;}")
        self.btn_record.setFixedSize(50, 50)
        self.btn_record.clicked.connect(self.toggle_recording)

        layout.addWidget(self.movie_screen)
        layout.addWidget(self.label_status)
        layout.addWidget(self.btn_record)

        self.setLayout(layout)


    def close_dialog(self):
        self.recording = False
        self.movie.stop()
        try:
            delk=os.remove("temp_mono_audio.wav")
            delk=os.remove("recorded_audio.wav")
            print("Deleted")
        except:
            pass
        finally:
            sys.exit()

    def set_mask(self):
        """
        Sets a rounded rectangular mask for the widget.

        This method creates a QPainterPath object and adds a rounded rectangle to it.
        The rounded rectangle is defined by the widget's rectangle and the specified corner radius.
        Then, a QRegion object is created from the filled polygon of the QPainterPath.
        Finally, the mask of the widget is set to the created QRegion.

        Note: This method assumes that the widget is a subclass of QWidget.

        Returns:
            None
        """
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10, mode=Qt.AbsoluteSize)

        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            # self.th1=threading.Thread(target=self.stop_recording)
            # self.th2=threading.Thread(target=self.recognize)
            # self.th1.start()
            # self.th2.start()
            # self.th1.join()
        
            self.stop_recording()

    def start_recording(self):
        self.audio_frames = []
        self.recording = True

        # Set the movie to start when recording begins
        self.movie.start()

        self.label_status.setText('Recording...')
        self.label_status.setStyleSheet("QLabel { color: red; }")

        self.audio_stream = pyaudio.PyAudio().open(
            format=self.audio_format, 
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=0,  # Adjust this index based on your system
            frames_per_buffer=self.chunk_size)
        self.record_thread = threading.Thread(target=self.record_audio)
        self.record_thread.start()

    def record_audio(self):
        while self.recording:
            data = self.audio_stream.read(self.chunk_size)
            self.audio_frames.append(data)

    def stop_recording(self):
        
        self.recording = False

        # Stop the movie when recording stops
        self.movie.stop()

        self.label_status.setText('Recording stopped.')
        self.label_status.setStyleSheet("QLabel { color: black; }")

        self.audio_stream.stop_stream()
        self.audio_stream.close()

        self.save_audio()
        self.recognize()
        
    #-------------------------- : this is for adding rounded corners to the window
        # self.label_status.setText('Running Speech Recognition...')
        # self.label_status.setStyleSheet("QLabel { color: black; }")
        # self.label_status.setText("-{0}-".format(self.convert_audio_to_text("recorded_audio.wav")))

    def recognize(self):
        self.label_status.setText('Running Speech Recognition...')
        self.label_status.setStyleSheet("QLabel { color: black; }")
        self.label_status.setText("{0}".format(self.convert_audio_to_text("recorded_audio.wav")))

    def save_audio(self):
        output_filename = 'recorded_audio.wav'
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.audio_format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()

    def convert_audio_to_text(self,file_path):
        # Load the audio file
        while True:
            try:
                audio = AudioSegment.from_file(file_path)
                break
            except:
                pass
        audio = AudioSegment.from_file(file_path)

        # Convert stereo to mono if needed
        if audio.channels > 1:
            audio = audio.set_channels(1)

        # Save the mono audio to a temporary WAV file
        temp_wav_file = "temp_mono_audio.wav"
        
        audio.export(temp_wav_file, format="wav")

        # Initialize the recognizer
        r = sr.Recognizer()

        with sr.AudioFile(temp_wav_file) as source:
            audio_data = r.record(source)
            
            try:
                text = r.recognize_google(audio_data)
                print("----------->",text)
                
                return text
            except sr.UnknownValueError:
                return("Speak again.")
            except sr.RequestError as e:
                return("Error occurred during speech recognition: {0}".format(e))
        
        delk=os.remove("temp_mono_audio.wav")


class EnvironmentChecker:
    """
    A class that checks the environment for the application.

    Attributes:
        p (pyaudio.PyAudio): An instance of the PyAudio class.

    Methods:
        check_microphone_channels(x): Checks the available microphone channels.
        check_installed_modules(): Checks the installed modules.
        print_running_message(): Prints a message indicating that the application is running.
        check_environment(channel): Checks the environment by calling the above methods.
        print_input_channel_info(id, name, channel_id, sample_rate, selected_channel): Prints information about the input channels.
    """

    def __init__(self):
        self.p = pyaudio.PyAudio()


    def check_microphone_channels(self, x):
        """
        Checks the available microphone channels.

        Args:
            x: Some argument description.

        Returns:
            None
        """
        print("Checking Microphone Channels:")
        
        # Get the number of audio input devices (microphones)
        num_devices = self.p.get_device_count()
        print(f"Number of Microphones: {num_devices}")

        for i in range(num_devices):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                self.print_input_channel_info(i, device_info['name'], device_info['maxInputChannels'], device_info['defaultSampleRate'], x)

    def check_installed_modules(self):
        print("\nChecking Installed Modules:")
        time.sleep(2)
        
        try:
            import PyQt5
            print("PyQt5 is installed.")
        except ImportError:
            print("PyQt5 is not installed. Please install it using 'pip install PyQt5'.")
            time.sleep(2)

        try:
            import pyaudio
            print("PyAudio is installed.")
        except ImportError:
            print("PyAudio is not installed. Please install it using 'pip install pyaudio'.")

    def print_running_message(self):
        """
        Prints a message indicating that the application is running.

        Returns:
            None
        """
        print("\nRunning the Application:")
        print("Press Ctrl+C to exit.")

    def check_environment(self, channel):
        """
        Checks the environment by calling the check_microphone_channels, check_installed_modules, and print_running_message methods.

        Args:
            channel: Some argument description.

        Returns:
            None
        """
        self.check_microphone_channels(channel)
        self.check_installed_modules()
        self.print_running_message()

    @staticmethod
    def print_input_channel_info(id, name, channel_id, sample_rate, selected_channel):
        """
        Prints information about the input channels.

        Args:
            id: Some argument description.
            name: Some argument description.
            channel_id: Some argument description.
            sample_rate: Some argument description.
            selected_channel: Some argument description.

        Returns:
            None
        """
        channel_selected = selected_channel
        if channel_id == channel_selected:
            print(f'\n---> Microphone_id: {channel_id}\t|\t Name: {name}\tSample Rate: {sample_rate}')
        else:
            print(f'\nMicrophone_id: {channel_id + 1}\t|\t Name: {name}')


if __name__ == "__main__":

    channel = 3 # Only valid for my system. Change it to 1 or 2 or 3 or 4 or 5 or 6 or 7 or 8 or 9 or 10 according to your system.
    # UnComment when needed

    environment_checker = EnvironmentChecker()
    environment_checker.check_environment(channel)
    app = QApplication([])
    main_app = VoiceRecorderApp(channel)
    main_app.show()
    sys.exit(app.exec_())
