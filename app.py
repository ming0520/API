import importlib

import module.AutoEdit
importlib.reload(module.AutoEdit)
from module.AutoEdit import AutoEdit

import module.VoskProcess
importlib.reload(module.VoskProcess)
from module.VoskProcess import VoskProcess

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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'

vosk = VoskProcess(vosk_path='module/vosk-model-small-en-us-0.15')
from flask import send_from_directory

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/demo/')
def get_demo():
    # command = 'ffmpeg -y -i example.mp4 -filter_complex "[0:v]trim=start=0.15:end=0.69,setpts=PTS-STARTPTS[v0];[0:a]atrim=start=0.15:end=0.69,asetpts=PTS-STARTPTS[a0];[0:v]trim=start=1.29:end=3.21,setpts=PTS-STARTPTS[v1];[0:a]atrim=start=1.29:end=3.21,asetpts=PTS-STARTPTS[a1];[0:v]trim=start=3.24:end=4.23,setpts=PTS-STARTPTS[v2];[0:a]atrim=start=3.24:end=4.23,asetpts=PTS-STARTPTS[a2];[0:v]trim=start=4.26:end=4.83,setpts=PTS-STARTPTS[v3];[0:a]atrim=start=4.26:end=4.83,asetpts=PTS-STARTPTS[a3];[0:v]trim=start=5.04:end=6.09,setpts=PTS-STARTPTS[v4];[0:a]atrim=start=5.04:end=6.09,asetpts=PTS-STARTPTS[a4];[0:v]trim=start=6.12:end=8.34,setpts=PTS-STARTPTS[v5];[0:a]atrim=start=6.12:end=8.34,asetpts=PTS-STARTPTS[a5];[0:v]trim=start=8.4:end=10.41,setpts=PTS-STARTPTS[v6];[0:a]atrim=start=8.4:end=10.41,asetpts=PTS-STARTPTS[a6];[0:v]trim=start=10.71:end=11.7,setpts=PTS-STARTPTS[v7];[0:a]atrim=start=10.71:end=11.7,asetpts=PTS-STARTPTS[a7];[0:v]trim=start=11.76:end=13.05,setpts=PTS-STARTPTS[v8];[0:a]atrim=start=11.76:end=13.05,asetpts=PTS-STARTPTS[a8];[0:v]trim=start=13.83:end=15.99,setpts=PTS-STARTPTS[v9];[0:a]atrim=start=13.83:end=15.99,asetpts=PTS-STARTPTS[a9];[0:v]trim=start=16.05:end=17.28,setpts=PTS-STARTPTS[v10];[0:a]atrim=start=16.05:end=17.28,asetpts=PTS-STARTPTS[a10];[0:v]trim=start=39.96:end=40.62,setpts=PTS-STARTPTS[v11];[0:a]atrim=start=39.96:end=40.62,asetpts=PTS-STARTPTS[a11]; [v0] [a0] [v1] [a1] [v2] [a2] [v3] [a3] [v4] [a4] [v5] [a5] [v6] [a6] [v7] [a7] [v8] [a8] [v9] [a9] [v10] [a10] [v11] [a11]concat=n=12:v=1:a=1 [out]" -map "[out]" example_COMPLEX.mp4'
    command = '-filter_complex "[0:v]trim=s rt=0.15:end=0.69,setpts=PTS-STARTPTS[v0];[0:a]atrim=start=0.15:end=0.69,asetpts=PTS-STARTPTS[a0];[0:v]trim=start=1.29:end=3.21,setpts=PTS-STARTPTS[v1];[0:a]atrim=start=1.29:end=3.21,asetpts=PTS-STARTPTS[a1];[0:v]trim=start=3.24:end=4.23,setpts=PTS-STARTPTS[v2];[0:a]atrim=start=3.24:end=4.23,asetpts=PTS-STARTPTS[a2];[0:v]trim=start=4.26:end=4.83,setpts=PTS-STARTPTS[v3];[0:a]atrim=start=4.26:end=4.83,asetpts=PTS-STARTPTS[a3];[0:v]trim=start=5.04:end=6.09,setpts=PTS-STARTPTS[v4];[0:a]atrim=start=5.04:end=6.09,asetpts=PTS-STARTPTS[a4];[0:v]trim=start=6.12:end=8.34,setpts=PTS-STARTPTS[v5];[0:a]atrim=start=6.12:end=8.34,asetpts=PTS-STARTPTS[a5];[0:v]trim=start=8.4:end=10.41,setpts=PTS-STARTPTS[v6];[0:a]atrim=start=8.4:end=10.41,asetpts=PTS-STARTPTS[a6];[0:v]trim=start=10.71:end=11.7,setpts=PTS-STARTPTS[v7];[0:a]atrim=start=10.71:end=11.7,asetpts=PTS-STARTPTS[a7];[0:v]trim=start=11.76:end=13.05,setpts=PTS-STARTPTS[v8];[0:a]atrim=start=11.76:end=13.05,asetpts=PTS-STARTPTS[a8];[0:v]trim=start=13.83:end=15.99,setpts=PTS-STARTPTS[v9];[0:a]atrim=start=13.83:end=15.99,asetpts=PTS-STARTPTS[a9];[0:v]trim=start=16.05:end=17.28,setpts=PTS-STARTPTS[v10];[0:a]atrim=start=16.05:end=17.28,asetpts=PTS-STARTPTS[a10];[0:v]trim=start=39.96:end=40.62,setpts=PTS-STARTPTS[v11];[0:a]atrim=start=39.96:end=40.62,asetpts=PTS-STARTPTS[a11]; [v0] [a0] [v1] [a1] [v2] [a2] [v3] [a3] [v4] [a4] [v5] [a5] [v6] [a6] [v7] [a7] [v8] [a8] [v9] [a9] [v10] [a10] [v11] [a11]concat=n=12:v=1:a=1 [out]" -map "[out]"'
    return command

@app.route('/')
def main():
    return render_template("index.html")


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
            # output = cut.export_good()
            cut.extract_audio()
            cut.load_audio()
            # cut.vosk_process()
            cut.df = vosk.transcribe(cut.audioData)
            cut.feature_process()
            cut.generate_complex_filter(cut.render_list)
            cut.execute()
            output = cut.post_process()
            path = output
            try:
                return send_file(path, as_attachment=True)
            except Exception as e:
                return 404
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
    # app.run(debug=True, threaded=True)
    # vosk = VoskProcess(vosk_path='module/vosk-model-small-en-us-0.15')
    app.run(host='0.0.0.0',port=80)

