import importlib

import module.AutoEdit
importlib.reload(module.AutoEdit)
from module.AutoEdit import AutoEdit

import module.VoskProcess
importlib.reload(module.VoskProcess)
from module.VoskProcess import VoskProcess

# vosk = VoskProcess(vosk_path='module/vosk-model-small-en-us-0.15')
# End Auto Edit Library

import os
from flask import Flask, flash, request, redirect, url_for,render_template, send_file
from werkzeug.utils import secure_filename
import subprocess
from shutil import move, rmtree, copyfile
import requests
import json

# Get fps
import cv2

# class Timestamp:
#   def __init__(self,start = 0.0, end = 0.0, text='text'):
#     self.start = start
#     self.end = end
#     self.text = text

UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = {'mp4'}
ALLOWED_API_EXTENSIONS = {'wav'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'

from flask import send_from_directory

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    return render_template("index.html")

@app.route('/api/',methods=['GET', 'POST'])
def api_process():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_api_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(filename)
            # video_path = filename
            # video = cv2.VideoCapture(video_path)
            # fps = video.get(cv2.CAP_PROP_FPS)
            # print(fps)
            cut = AutoEdit(ac='1',
                    verbose=True,fm=4,st=0.2,
                    log=True,mono=True,
                    model='module/20201227-1123-MLP-RMSprop-Default-80-123.h5',
                    isRender=False
                    )
            # output = cut.export_good()
            cut.AUDIO_OUTPUT = filename
            # cut.extract_audio()
            cut.load_audio()
            # cut.vosk_process()
            # flash('Transcribing')
            cut.df = vosk.transcribe(cut.audioData)
            # flash('Feature processing')
            cut.feature_process()
            # flash('Generate command')
            cut.generate_complex_filter()
            # cut.execute()
            output = cut.post_process()
            command = cut.filter
            try:
                return command
            except Exception as e:
                return 404
                # self.log.exception(e)
                # self.Error(400)
            
        else:
            flash('Only wav are allowed')
            return render_template("api.html")
    return render_template("api.html")



@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(filename)
            video_path = filename
            video = cv2.VideoCapture(video_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            print(fps)
            cut = AutoEdit(file=video_path,ac='1',
                    verbose=True,fm=4,st=0.2,fps=fps,
                    log=True,mono=True,
                    model='module/20201227-1123-MLP-RMSprop-Default-80-123.h5'
                    )
            output = cut.export_good()
            # cut.extract_audio()
            # cut.load_audio()
            # # cut.vosk_process()
            # cut.df = vosk.transcribe(cut.audioData)
            # cut.feature_process()
            # cut.generate_complex_filter(cut.render_list)
            # cut.execute()
            # output = cut.post_process()
            path = output
            # try:
            return send_file(path, as_attachment=True)
            # except Exception as e:
                # self.log.exception(e)
                # self.Error(400)
            return 'file uploaded successfully'
        else:
            flash('Only mp4 are allowed')
            return render_template("upload.html")
    return render_template("upload.html")
    # '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Upload>
    # </form>
    # '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    video_path = filename
    # video = cv2.VideoCapture(video_path)
    # fps = video.get(cv2.CAP_PROP_FPS)
    # print(fps)
    # cut = AutoEdit(file=video_path,ac='1',
    #            verbose=True,fm=4,st=0.2,fps=fps,
    #            log=True,mono=True,
    #            model='20201227-1123-MLP-RMSprop-Default-80-123.h5'
    #           )
    # cut.extract_audio()
    # cut.load_audio()
    # cut.vosk_process()
    # cut.feature_process()
    # cut.generate_complex_filter(cut.render_list)
    # cut.execute()
    # cut.post_process()

    # filename = filename
    # filename_actual = filename.split(".")[0]
    # filetype = filename.split(".")[1]
    # filename_audio = f'{filename_actual}_AUDIO'
    # # os.system(f'python process.py {filename}')
    # os.system(f'ffmpeg -y -i {filename_actual}.{filetype} -acodec pcm_s16le -ac 1 -ar 16000 -af lowpass=3000,highpass=200 {filename_audio}.wav')
    # # subprocess.call(f'ffmpeg -y -i {filename_actual}.{filetype} -acodec pcm_s16le -ac 1 -ar 16000 -af lowpass=3000,highpass=200 {filename_audio}.wav', shell=True)

    # os.system(f'auto-editor {filename_audio}.wav')
    # # subprocess.call(f'auto-editor {filename_audio}.wav', shell=True)
    # headers = {
    #     'Content-Type': 'audio/wav',
    # }

    # params = (
    #     ('model', 'en-US_BroadbandModel'),
    #     ('timestamps', 'true'),
    #     ('max_alternatives', '1'),
    # )

    # data = open(f'{filename_audio}_ALTERED.wav', 'rb').read()
    # response = requests.post('https://api.jp-tok.speech-to-text.watson.cloud.ibm.com/instances/69250ebc-5a34-42a0-9096-ab9b382e2c25/v1/recognize', 
    #                         headers=headers, params=params, data=data, auth=('apikey', 'P75zKPwgFW2iwgbKS2GGApeuT84TymaJuFhFF88mYrPN'))

    # watson = response.json()
    # timestamps = watson['results'][0]['alternatives'][0]['timestamps']
    
    # ts_list = []
    # for timestamp in timestamps:
    #     if (timestamp[0]!="%HESITATION"):
    #         ts_list.append(Timestamp(timestamp[1],timestamp[2],timestamp[0]))

    # between = []
    # for ts in ts_list:
    #     between.append(f'between(t,{ts.start},{ts.end})')

    # betweens = '+'.join(between)
    # slt = '\"select=\'' + betweens + '\'' + ',setpts=N/FRAME_RATE/TB\"'
    # aslt = '\"aselect=\'' + betweens + '\'' + ',asetpts=N/SR/TB\"'
    # sltFilter = ['ffmpeg','-y','-i',f'{filename_audio}_ALTERED.wav', '-vf', f'{slt}','-af', f'{aslt}', f'{filename_actual}_FILTERED.wav']
    # total_string = ' '.join(sltFilter)
    # os.system(total_string)
    # print("Done!")
    # filepath=""
    # filename = f'{filename_actual}_FILTERED.wav'
    # # return send_file(os.path.join(filepath, filename), as_attachment=True)
    # return send_from_directory(app.config['UPLOAD_FOLDER'],
    #                             filename)
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
    # app.run(host='0.0.0.0',port=80)

