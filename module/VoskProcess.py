
import vosk
import json
import pandas as pd
import numpy as np
import math

class VoskProcess:
    def __init__(self,vosk_path='vosk-model-small-en-us-0.15'):
        print('Loading vosk...')
        vosk.SetLogLevel(-1)
        self.VOSK_PATH = vosk_path
        self.vosk_model = vosk.Model(self.VOSK_PATH)
        print('Loaded vosk!')

    def extract_words(self,res):
        jres = json.loads(res)
        if not 'result' in jres:
            return []
        words = jres['result']
        return words

    def transcribe_words(self,recognizer, bytes):
        results = []

        chunk_size = 4000
        for chunk_no in range(math.ceil(len(bytes)/chunk_size)):
            start = chunk_no*chunk_size
            end = min(len(bytes), (chunk_no+1)*chunk_size)
            data = bytes[start:end]

            if recognizer.AcceptWaveform(data):
                words = self.extract_words(recognizer.Result())
                results += words
        results += self.extract_words(recognizer.FinalResult())

        return results                

    def transcribe(self,audioData):
        print('Creating recognizer ...')
        self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
        print('Created recognizer')
        self.audioData = audioData
        int16 = np.int16(self.audioData * 32768).tobytes()
        # vosk_path = self.VOSK_PATH
        # vosk_model = vosk.Model(vosk_path) 
        print('Transcribing...')
        res = self.transcribe_words(self.recognizer, int16)
        df = pd.DataFrame.from_records(res)
        df = df.sort_values('start')
        print('Completed transcribe')
        self.df = df
        return self.df