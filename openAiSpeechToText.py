# Note: you need to be using OpenAI Python v0.27.0 for the code below to work


# File uploads are currently limited to 25 MB and the following input file types are supported: 
# mp3, mp4, mpeg, mpga, m4a, wav, and webm.

import queue
import sys
import openai
import sounddevice as sd
import soundfile as sf
import datetime
import os
assert os

import numpy
assert numpy  # avoid "imported but unused" message (W0611)

openai.api_key = open('openai_api_key.txt','r').readline()

def record(filename=None, device=None, samplerate=None, channels=1, subtype=None):
    """Record audio until Enter key is pressed.

    :param filename: str, name of file to write recording to (default: None)
    :param device: int or str, input device ID or substring (default: None)
    :param samplerate: int, sampling rate in Hz (default: None)
    :param channels: int, number of input channels (default: 1)
    :param subtype: str, sound file subtype (e.g. "PCM_24") (default: None)
    :return: str, name of file recording was written to
    """
    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())

    try:
        if samplerate is None:
            device_info = sd.query_devices(device, 'input')
            samplerate = int(device_info['default_samplerate'])
        if filename is None:
            filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.wav")

        # Make sure the file is opened before recording anything:
        with sf.SoundFile(filename, mode='x', samplerate=samplerate,
                          channels=channels, subtype=subtype) as file:
            with sd.InputStream(samplerate=samplerate, device=device,
                                channels=channels, callback=callback):
                print('Press Enter to stop the recording')
                print('recording... \nwaiting for Enter key...')
                input()
                while not q.empty():
                    file.write(q.get())
                print('Recording finished: ' + filename)
                return filename
    except KeyboardInterrupt:
        print('\nRecording interrupted')
        raise
    except Exception as e:
        print(type(e).__name__ + ': ' + str(e))
        raise

audio_file= record(channels=2)

transcript = openai.Audio.transcribe("whisper-1", open(audio_file, "rb"))

print(f'transcription: {transcript.text}')


"""delete audio file """
if os.path.exists(audio_file):
    os.remove(audio_file)
    #print(f"{audio_file} has been deleted.")
else:
    print(f"{audio_file} does not exist.")
