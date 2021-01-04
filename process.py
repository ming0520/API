#python auto-editor.py lib.mp4 --frame_margin 8 --silent_threshold 0.03

# internal python libraries
import os
import subprocess
from shutil import move, rmtree, copyfile
import requests
import json
import argparse

parser = argparse.ArgumentParser("Description remove stuttered from audio.")
parser.add_argument('fname', type=str, help="Audio File Name")
args = parser.parse_args()

class Timestamp:
  def __init__(self,start = 0.0, end = 0.0, text='text'):
    self.start = start
    self.end = end
    self.text = text

def process(fname):
    filename = fname
    filename_actual = filename.split(".")[0]
    filetype = filename.split(".")[1]
    filename_audio = f'{filename_actual}_AUDIO'
    print('converting to audio')
    os.system(f'ffmpeg -i {filename_actual}.{filetype} -acodec pcm_s16le -ac 1 -ar 16000 -af lowpass=3000,highpass=200 {filename_audio}.wav')
    print('removing silent part')
    os.system(f'auto-editor {filename_audio}.wav')
    headers = {
    'Content-Type': 'audio/wav',
    }

    params = (
        ('model', 'en-US_BroadbandModel'),
        ('timestamps', 'true'),
        ('max_alternatives', '1'),
    )
    print('requesting for api')
    data = open(f'{filename_audio}_ALTERED.wav', 'rb').read()
    response = requests.post('https://api.jp-tok.speech-to-text.watson.cloud.ibm.com/instances/69250ebc-5a34-42a0-9096-ab9b382e2c25/v1/recognize',headers=headers, params=params, data=data, auth=('apikey', 'P75zKPwgFW2iwgbKS2GGApeuT84TymaJuFhFF88mYrPN'))
    watson = response.json()
    timestamps = watson['results'][0]['alternatives'][0]['timestamps']

    print('processing hesitation')
    ts_list = []
    for timestamp in timestamps:
        if (timestamp[0]!="%HESITATION"):
            ts_list.append(Timestamp(timestamp[1],timestamp[2],timestamp[0]))

    between = []
    for ts in ts_list:
        between.append(f'between(t,{ts.start},{ts.end})') 

    betweens = '+'.join(between)
    slt = '\"select=\'' + betweens + '\'' + ',setpts=N/FRAME_RATE/TB\"'
    aslt = '\"aselect=\'' + betweens + '\'' + ',asetpts=N/SR/TB\"'
    sltFilter = ['ffmpeg','-y','-i',f'{filename_audio}_ALTERED.wav', '-vf', f'{slt}','-af', f'{aslt}', f'{filename_actual}_FILTERED.wav']
    total_string = ' '.join(sltFilter)

    print('Rendering output.')
    os.system(total_string)

if __name__ == '__main__':
        process(args.fname)
