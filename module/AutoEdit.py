# Start Auto Edit Library

# os system processing library
import subprocess
import shutil
import json
from glob import glob
from shutil import move, rmtree, copyfile
import os

# mathematic operation
import time
import math
import numpy as np
import pandas as pd

# audio related
import librosa
import soundfile as sf
import vosk

# display libary
from tqdm import tqdm
from tqdm.notebook import tqdm

# machine learning libary
import tensorflow as tf

# Make numpy values easier to read.
np.set_printoptions(precision=3, suppress=True)

# developed library
import importlib

import module.Timecode
import module.FeatureExtraction
import module.Dataset
import module.Timestamp

importlib.reload(module.Timecode)
importlib.reload(module.FeatureExtraction)
importlib.reload(module.Dataset)
importlib.reload(module.Timestamp)

from module.Timecode import Timecode
from module.FeatureExtraction import FeatureExtraction
from module.Dataset import Dataset
from module.Timestamp import Timestamp


class AutoEdit:
    def __init__(self, file=None, ba='160000', ac='1', ar='16000',output_format='.wav', fps = 30.0, 
                 st = 0.04, fm = 4, lt = 2.00, verbose = False, isRender = True,
                 log=False, mono = True, 
                 model='Model/mymodel_78_18.h5'):
        #parameter for ffmpeg to convert the file
        self.MODEL_PATH = model
        self.INPUT_FILE = file
        if(file != None):
            self.FILENAME = file.split('.')[0]
        else:
            self.FILENAME = None
        self.AUDIO_OUTPUT_FORMAT = output_format
        if(file != None):
            self.AUDIO_OUTPUT = f'{self.FILENAME}{self.AUDIO_OUTPUT_FORMAT}'
        else:
            self.AUDIO_OUTPUT = None
        
        self.BITRATE_AUDIO = ba
        self.AUDIO_CHANEL = ac
        self.AUDIO_RATE = ar
        self.FRAME_RATE = fps
        
        self.FRAME_MARGIN = fm
        self.SILENT_THRESHOLD = st
        self.LOUDNESS_THRESHOLD = lt
        
        self.VERBOSE = verbose
        
        self.audioData = None
        self.sampleRate = None
        
        self.audioSampleCount = None
        self.maxAudioVolume = None
        self.samplesPerFrame = None
        self.audioFrameCount = None
        self.hasLoudAudio = None
        
        self.chunks = None
        self.shouldIncludeFrame = None
        self.timecodeList = None
        self.chunks_path = 'chunks.txt'
        self.log = log
        self.isMono = mono
        self.VOSK_PATH = 'vosk-model-small-en-us-0.15'
        self.isRender = isRender
        # self.VOSK_PATH = 'vosk-model-en-us-aspire-0.2'
            
    def extract_audio(self):
        if self.INPUT_FILE == None:
            print("No input file!")
            
        cmd = ['ffmpeg', '-y' ,'-i',self.INPUT_FILE,'-acodec','pcm_s16le' ,'-b:a', self.BITRATE_AUDIO, '-ac', self.AUDIO_CHANEL, 
               '-ar', self.AUDIO_RATE, '-vn', f'{self.AUDIO_OUTPUT}']
        #ffmpeg -i "%%a" -acodec pcm_s16le -ac 1 -ar 16000 -af lowpass=3000,highpass=200 "converted\%%~na.wav
        # ffmpeg -y -i SBLQ.mp4 -acodec pcm_s16le -b:a 16k -ac 1 -ar 16000 -vn output.wav

        # ffmpeg -y -i SBLQ.mp4 -acodec libmp3lame -b:a 16k -ac 1 -ar 16000 -vn output.mp3
        if(not self.VERBOSE):
            cmd.extend(['-nostats', '-loglevel', '0'])
        subprocess.call(cmd)
        
    def get_max_volume(self,s):
        maxv = float(np.max(s))
        minv = float(np.min(s))
        return max(maxv, -minv)

    def load_audio(self):
        # self.sampleRate,self.audioData = wavfile.read(f'{self.AUDIO_OUTPUT}')
        self.audioData,self.sampleRate = librosa.load(f'{self.AUDIO_OUTPUT}',
        mono = self.isMono,sr=self.sampleRate)

        self.audioSampleCount = self.audioData.shape[0]
        self.maxAudioVolume = self.get_max_volume(self.audioData)
        self.samplesPerFrame = self.sampleRate / self.FRAME_RATE
        self.audioFrameCount = int(math.ceil(self.audioSampleCount / self.samplesPerFrame))
    
    def get_shape(self):
        return self.audioData.shape
    
    def calc_has_loud_audio(self):
        self.hasLoudAudio = np.zeros((self.audioFrameCount))
        
        for i in range(self.audioFrameCount):
            start = int(i * self.samplesPerFrame)
            end = min( int( (i+1) * self.samplesPerFrame ), self.audioSampleCount)
            audiochunks = self.audioData[start:end]
            maxchunksVolume = self.get_max_volume(audiochunks) / self.maxAudioVolume
            
            if(maxchunksVolume >= self.LOUDNESS_THRESHOLD):
                self.hasLoudAudio[i] = 2
            elif(maxchunksVolume >= self.SILENT_THRESHOLD):
                self.hasLoudAudio[i] = 1
    
    def calc_should_include_frame(self):
        self.shouldIncludeFrame = np.zeros((self.audioFrameCount))
        self.chunks = [[0,0,0]]
        
        for i in range(self.audioFrameCount):
            start = int(max(0, i-self.FRAME_MARGIN))
            end = int(min(self.audioFrameCount, i+1+self.FRAME_MARGIN))
            self.shouldIncludeFrame[i] = min(1,np.max(self.hasLoudAudio[start:end]))

            if(i >= 1 and self.shouldIncludeFrame[i] != self.shouldIncludeFrame[i-1]):
                self.chunks.append([self.chunks[-1][1], i, self.shouldIncludeFrame[i-1]])
        self.chunks.append([self.chunks[-1][1], self.audioFrameCount, self.shouldIncludeFrame[i-1]])
        self.chunks = self.chunks[1:]
        
    def calc_timecode(self):
        self.timecodeList = []
        
        for chunk in self.chunks:
            startTime = Timecode(fps=self.FRAME_RATE)
            endTime = Timecode(fps=self.FRAME_RATE)
            
            startTime.set_by_frames(chunk[0])
            endTime.set_by_frames(chunk[1])
            isInclude = chunk[2]
            self.timecodeList.append([startTime,endTime,isInclude])
            
    def execute(self):
        print('Executing command...')
        command = 'bash ./run.sh'
        if os.path.exists('run.sh'):
            # if self.log:
            #      command += ' > log.txt'    
            output = subprocess.call(command,shell=True)
        if self.VERBOSE:
            print("Complex filter command success") if output == 0 else print("Complex filter command failed!")
      
            
            
    def write_to_bat(self,command):
        if(self.isRender == False):
            return
        if os.path.exists('run.sh'):
            os.remove(f'run.sh')
        file1 = open("run.sh","w")
        file1.write(command)
        file1.close()
        filename = 'run.sh'
        # if self.log:
        #     filename += ' > log.txt'
        return filename
    
    def produce_concat_file(self):
        if os.path.exists(self.chunks_path):
            os.remove(self.chunks_path)
            
        with open(self.chunks_path, 'w') as f:
            for index in range(len(self.timecodeList)):
                isInclude = float(self.timecodeList[index][2])
                if isInclude < 1:
                    continue;
                # startTime = self.timecodeList[index][0].get_timecode_ffmpeg()
                # endTime = self.timecodeList[index][1].get_timecode_ffmpeg()
                startTime = self.timecodeList[index][0].get_seconds()
                endTime = self.timecodeList[index][1].get_seconds()
                f.write(f'file {self.INPUT_FILE}\ninpoint {startTime}\noutpoint {endTime}\n')
    
    def concat_way(self):
        concat = ['ffmpeg','-y','-f','concat','-safe','0','-i', f'{self.chunks_path}',
                 '-async','1','-framerate', f'{self.FRAME_RATE}','-b:a', f'{self.BITRATE_AUDIO}',
                 '-c:v', 'copy', '-ar', f'{self.AUDIO_RATE}', '-ac', f'{self.AUDIO_CHANEL}',
                 '-c:a','aac','-movflags','+faststart',f'{self.FILENAME}_CONCATED.mp4']
        subprocess.call(concat)
        
    def select_filter(self):
        
        between = []
        counter = 0
        for i in self.timecodeList:
            if i[2] > 0:
#                 print(f'{self.INPUT_FILE},{i[0].get_seconds()},{i[1].get_seconds()}')
                between.append(f'between(t,{i[0].get_seconds()},{i[1].get_seconds()})') 
        
        betweens = '+'.join(between)
        slt = '\"select=\'' + betweens + '\'' + ',setpts=N/FRAME_RATE/TB\"'
        aslt = '\"aselect=\'' + betweens + '\'' + ',asetpts=N/SR/TB\"'
        
        sltFilter = ['ffmpeg','-y','-i',f'{self.INPUT_FILE}', '-vf', 
                     f'{slt}','-af', f'{aslt}',
                     f'{self.FILENAME}_FILTERED.mp4']
        
        total_string = ' '.join(sltFilter)
#         if self.log:
#             total_string += " > log.txt 2>&1";
        bat_path = self.write_to_bat(total_string)
        # output = subprocess.call(bat_path,shell=True)
        self.execute()
        if self.VERBOSE:
            print("Select filter command success") if output == 0 else print("Select filter command failed!")
            
    def remove_silence(self):
        trim = []
        duration_list = []
        number_of_segment = 0
        prev = 0
        current = 0

        # with out xfade
        for i in self.timecodeList:
            if i[2] > 0:
                duration_list.append(i[0].get_seconds()-i[1].get_seconds())
                trim.append(
                    f'[0:v]trim=start={i[0].get_seconds()}:end={i[1].get_seconds()},setpts=PTS-STARTPTS[v{number_of_segment}]')
                trim.append(
                    f'[0:a]atrim=start={i[0].get_seconds()}:end={i[1].get_seconds()},asetpts=PTS-STARTPTS[a{number_of_segment}]')
                number_of_segment += 1

                
        filter = ';'.join(trim)
        filter = filter + ";"

        # Normal cut feature
        for i in range(number_of_segment):
            filter += f' [v{i}] [a{i}]'

        # Start to generate ending of command
        filter += f'concat=n={number_of_segment}:v=1:a=1 [out]'
        filter = '"' + filter + '"'
        filter = f'ffmpeg -y -i {self.INPUT_FILE} -filter_complex ' + filter
        filter = filter + f' -map "[out]" {self.FILENAME}_SILENCE.mp4'
            
        bat_path = self.write_to_bat(filter)     
    

    def fliter_complex(self):
        trim = []
        duration_list = []
        number_of_segment = 0
        prev = 0
        current = 0

        # with out xfade
        for i in self.timecodeList:
            if i[2] > 0:
                duration_list.append(i[0].get_seconds()-i[1].get_seconds())
                trim.append(
                    f'[0:v]trim=start={i[0].get_seconds()}:end={i[1].get_seconds()},setpts=PTS-STARTPTS[v{number_of_segment}]')
                trim.append(
                    f'[0:a]atrim=start={i[0].get_seconds()}:end={i[1].get_seconds()},asetpts=PTS-STARTPTS[a{number_of_segment}]')
                number_of_segment += 1
                
        filter = ';'.join(trim)
        filter = filter + ";"

        # Normal cut feature
        for i in range(number_of_segment):
            filter += f' [v{i}] [a{i}]'

        # Start to generate ending of command
        filter += f'concat=n={number_of_segment}:v=1:a=1 [out]'
        filter = '"' + filter + '"'
        filter = f'ffmpeg -y -i {self.INPUT_FILE} -filter_complex ' + filter
        filter = filter + f' -map "[out]" {self.FILENAME}_COMPLEX.mp4'

        bat_path = self.write_to_bat(filter)
        self.execute()
        output = 1
        if self.VERBOSE:
            print("Complex filter command success") if output == 0 else print("Complex filter command failed!")
    
    
    def post_process(self):
        if os.path.exists(f'{self.chunks_path}'):
            os.remove(f'{self.chunks_path}')
            if self.VERBOSE:
                print(f"Removed {self.chunks_path}")
                
        if os.path.exists(f'{self.AUDIO_OUTPUT}'):
            os.remove(f'{self.AUDIO_OUTPUT}')
            if self.VERBOSE:
                print(f"Removed {self.AUDIO_OUTPUT}")
        return f'{self.FILENAME}_COMPLEX.mp4'
       
        
    def export_complex(self):
        self.pbar = tqdm(total=7)
        print("Start processing...")
        self.extract_audio()
        self.update_mypbar()
        self.load_audio()
        self.update_mypbar()
        self.calc_has_loud_audio()
        self.update_mypbar()
        self.calc_should_include_frame()
        self.update_mypbar()
        self.calc_timecode()
        self.update_mypbar()
        
        print(f'Exporting {self.FILENAME}_COMPLEX.mp4 ...')
        self.fliter_complex()
        self.update_mypbar()
        print(f'Exported {self.FILENAME}_COMPLEX.mp4 successfully!')
        
        self.post_process()
        self.update_mypbar()
        self.pbar.close()
        
    def export_fast(self):
        try:
            self.extract_audio()
            self.load_audio()
            self.calc_has_loud_audio()
            self.calc_should_include_frame()
            self.calc_timecode()
            self.produce_concat_file()
            self.concat_way()
            self.post_process()
            if(self.VERBOSE):
                print(f'Exported {self.FILENAME}_CONCATED.mp4 successfully!')
        except:
            print('Failed to export fast!')

        return f'{self.FILENAME}_CONCATED.mp4'
            
    def update_mypbar(self):
        self.pbar.update(1)
        time.sleep(0.01)
        self.pbar.refresh()
            
    def export_good(self):
        self.pbar = tqdm(total=7)
        try:
            print("Start processing...")
            self.extract_audio()
            self.update_mypbar()

            self.load_audio()
            self.update_mypbar()

            self.calc_has_loud_audio()
            self.update_mypbar()
            self.calc_should_include_frame()
            self.update_mypbar()
            self.calc_timecode()
            self.update_mypbar()
            
            print(f'Exporting {self.FILENAME}_FILTERED.mp4 ...')
            self.select_filter()
            self.update_mypbar()
            print(f'Exported {self.FILENAME}_FILTERED.mp4 successfully!')
  
            self.post_process()
            self.update_mypbar()
            self.pbar.close()
        except:
            print(f'Failed to export {self.FILENAME}_FILTERED.mp4 !')
        return f'{self.FILENAME}_FILTERED.mp4'
            
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

    def vosk_process(self):
        print('Loading vosk...')
        vosk.SetLogLevel(-1)
        int16 = np.int16(self.audioData * 32768).tobytes()
        vosk_path = self.VOSK_PATH
        vosk_model = vosk.Model(vosk_path)
        recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
        print('Transcribing...')
        res = self.transcribe_words(recognizer, int16)
        df = pd.DataFrame.from_records(res)
        df = df.sort_values('start')
        print('Completed transcribe')
        self.df = df
        
        
    def feature_process(self):
        # Process by using vosk
        self.audioData
        df = self.df
        model = tf.keras.models.load_model(self.MODEL_PATH)
        feature_file = f'{self.FILENAME}_feature.csv'
        
        sampleRate = self.sampleRate
        fail_list = []
        time_margin = int( (  (1/self.FRAME_RATE) *self.FRAME_MARGIN ) )
        index_margin = int( (  (1/self.FRAME_RATE) *self.FRAME_MARGIN ) *self.sampleRate )

        if(os.path.exists(feature_file)):
            os.remove(feature_file)

        if(not os.path.exists(feature_file)):
            print("Extracting feature...")
            features = np.empty(shape=(0,80))
            ds = Dataset()
            for i in tqdm(df.index[:]): 
                start_index = max(0, int(  df['start'][i] * self.sampleRate))
                end_index = min( int( (df['end'][i]) * self.sampleRate), self.audioSampleCount)
                fea = ds.get_feature_by_audio(self.audioData[start_index:end_index],11025)
                features = np.vstack((features,[fea]))
            print(f'Saved features to {feature_file}')
            np.savetxt(feature_file, features, delimiter=',')


        print(f'Load feature from {feature_file}')
        features = np.loadtxt(feature_file,delimiter=',')

        print('Predicting...')
        predictions = model.predict(x=features, batch_size=84,verbose=0)
        print("Finish predict!")

        self.predictions = predictions
        include_list = []
        for i in tqdm(df.index[:]):
            isInclude = True
            predict = np.round(predictions[i])
            word = df['word'][i]
            if(word == "i'm" or word == 'um' or word =='m' or word=='ah'or word=='huh'or word=='hm'):
                if(predict == 1):
                    isInclude = False
            if(isInclude):
                start = df['start'][i]
                end = df['end'][i]
                ts = Timestamp(start,end,word=word,label=predict)
                include_list.append(ts)
                
        self.include_list = include_list        
        render_list = []
        counter = 0
        start = include_list[0].start
        end = include_list[0].end
        word = ""
        for i,ts in tqdm(enumerate(include_list)):
            current_start = ts.start
            current_end = ts.end
            prev_start = include_list[i-1].start
            prev_end = include_list[i-1].end
            if(i >= 1 and current_start != prev_end):
                segment = Timestamp(start,prev_end, word=word)
                word = ''
                start = current_start
                render_list.append(segment)
                counter = counter + 1
            word = word + ts.word + " "    

        render_list.append(Timestamp(include_list[-1].start,include_list[-1].end,include_list[-1].word))
        self.render_list = render_list           


    def generate_complex_filter(self):
        render_list = self.render_list
        print('Generating complex filter...')
        trim = []
        duration_list = []
        number_of_segment = 0
        prev = 0
        current = 0
        # with out xfade
        for ts in render_list:
            duration_list.append(ts.end-ts.start)
            trim.append(
                f'[0:v]trim=start={ts.start}:end={ts.end},setpts=PTS-STARTPTS[v{number_of_segment}]')
            trim.append(
                f'[0:a]atrim=start={ts.start}:end={ts.end},asetpts=PTS-STARTPTS[a{number_of_segment}]')
            number_of_segment += 1

        filter = ';'.join(trim)
        filter = filter + ";"

        # Normal cut feature
        for i in range(number_of_segment):
            filter += f' [v{i}] [a{i}]'


        # Start to generate ending of command
        filter += f'concat=n={number_of_segment}:v=1:a=1 [out]'
        filter = '"' + filter + '"'
        
        if(self.isRender):
            filter = f'ffmpeg -y -i {self.INPUT_FILE} -filter_complex ' + filter
        else:
            filter = f'-filter_complex ' + filter

        filter = filter + f' -map "[out]"'

        if(self.isRender):
            filter = filter + f' {self.FILENAME}_COMPLEX.mp4'
            bat_path = self.write_to_bat(filter)
            print('Complete complex filter...')
            self.filter = filter
        else:
            self.filter = filter
        
        
