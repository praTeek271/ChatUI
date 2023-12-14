# import speech_recognition as sr

# def convert_audio_to_text(file_path):
#     r = sr.Recognizer()
#     with sr.AudioFile(file_path) as source:
#         audio = r.record(source)
#         try:
#             text = r.recognize_google(audio)
#             return text
#         except sr.UnknownValueError:
#             print("Unable to recognize speech")
#         except sr.RequestError as e:
#             print("Error occurred during speech recognition: {0}".format(e))

# # Example usage
# file_path = "recorded_audio_pcm.wav"
# text = convert_audio_to_text(file_path)
# print(text)



# import speech_recognition as sr
from pydub import AudioSegment

def convert_audio_to_text(file_path):
    # Load the audio file
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
            return text
        except sr.UnknownValueError:
            print("Unable to recognize speech")
        except sr.RequestError as e:
            print("Error occurred during speech recognition: {0}".format(e))

# Example usage
file_path = "D:\\Lucifer-Drive\\Programs\\pitch_changer\\recorded_audio.wav"
try:
    text = convert_audio_to_text(file_path)
    print(text)
except RuntimeWarning as e:
    # print(f"Warning:--{e}")
    pass