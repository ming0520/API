# Start Auto Edit Library

# os system processing library
import shutil
import json
from glob import glob
from shutil import move, rmtree, copyfile

# mathematic operation
import time
import math
import numpy as np
import pandas as pd

# audio related
import librosa
import librosa.display

# display libary
import tqdm
from tqdm.notebook import tqdm

# Make numpy values easier to read.
np.set_printoptions(precision=3, suppress=True)


class FeatureExtraction:
    def __init__(self, n_mels=128):
        self.n_mels = n_mels
        self.y = None
        self.sr = 11025
        self.S = None
        self.log_S = None
        self.mfcc = None
        self.delta_mfcc = None
        self.delta2_mfcc = None
        self.M = None
        self.rmse = None
        self.foldername = None
        self.filename=None
    
    def loadFile(self, foldernname):
        self.foldernname=foldernname
        self.y, self.sr = librosa.load(foldernname)
    
    def load_y_sr(self, y, sr):
        self.y = y
        self.sr = sr
    
    def melspectrogram(self):
        self.S = librosa.feature.melspectrogram(self.y, sr=self.sr, n_mels=self.n_mels)
        self.log_S = librosa.amplitude_to_db(self.S)
    
    def plotmelspectrogram(self, save=True):
        fig = plt.figure(figsize=(12, 4))
        librosa.display.specshow(self.log_S, sr=self.sr, x_axis='time', y_axis='mel')
        plt.title(f'mel Power Spectrogram ({self.filename})')
        plt.colorbar(format='%+02.0f dB')
        plt.tight_layout()
        if not os.path.exists('mel'):
            os.mkdir('mel')
        if save:
            fig.savefig(f'./mel/{self.filename}-mel.png', dpi=fig.dpi)
            print(f'Saved to ./mel/{self.filename}-mel.png')
            plt.close('all')

    def extractmfcc(self, n_mfcc=13):
        self.mfcc = librosa.feature.mfcc(S=self.log_S, n_mfcc=n_mfcc)
        self.delta_mfcc = librosa.feature.delta(self.mfcc,mode='nearest')
        self.delta2_mfcc = librosa.feature.delta(self.mfcc, order=2,mode='nearest')
        self.M = np.vstack([self.mfcc, self.delta_mfcc, self.delta2_mfcc])
    
    def plotmfcc(self,save=False):
        fig = plt.figure(figsize=(12, 6))
        plt.subplot(3, 1, 1)
        librosa.display.specshow(self.mfcc)
        plt.title(f'mel Power Spectrogram ({self.filename})')
        plt.ylabel('MFCC')
        plt.colorbar()
        
        plt.subplot(3, 1, 2)
        librosa.display.specshow(self.delta_mfcc)
        plt.title(f'mel Power Spectrogram ({self.filename})')
        plt.ylabel('MFCC-$\Delta$')
        plt.colorbar()
        
        plt.subplot(3, 1, 3)
        librosa.display.specshow(self.delta2_mfcc, sr=self.sr, x_axis='time')
        plt.title(f'mel Power Spectrogram ({self.filename})')
        plt.ylabel('MFCC-$\Delta^2$')
        plt.colorbar()
        
        plt.tight_layout()
        if not os.path.exists('mfcc'):
            os.mkdir('mfcc')
        if save:
            fig.savefig(f'./mfcc/{self.filename}-mfcc.png', dpi=fig.dpi)
            print(f'Saved to ./mfcc/{self.filename}-mfcc.png')
            plt.close('all')

    def extractrmse(self):
        self.rmse = librosa.feature.rms(y=self.y)