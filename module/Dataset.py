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

# display libary
import tqdm
from tqdm.notebook import tqdm

# Make numpy values easier to read.
np.set_printoptions(precision=3, suppress=True)

# developed library
import importlib

import module.FeatureExtraction

importlib.reload(module.FeatureExtraction)

from module.FeatureExtraction import FeatureExtraction

class Dataset:
    def __init__(self,):
        self.X = np.empty(shape=(0,80))
        self.Y = np.empty(shape=(0,2))
        self.DATASET = None
        self.PATH_ARRAY = []
        self.failed_file = []
        self.unexpected_label = []
        self.processed_counter = 0
        print("Object created!")

    def create_dataset(self,dataset_path,output_path):
        self.DATASET_PATH = dataset_path
        self.OUTPUT_PATH = output_path
        self.__process_dataset()
        self.__write_to_file()
        
    def get_feature_by_audio(self,y,sr):
          #exctract mfcc
        try:
            features = FeatureExtraction()
            features.load_y_sr(y,sr)
            features.melspectrogram()
            features.extractmfcc()
            features.extractrmse()
        except ValueError:
            self.failed_file.append(file_path)

        feature_vector = []

        for feature in features.mfcc:
            feature_vector.append(np.mean(feature))
            feature_vector.append(np.var(feature))

        for feature in features.delta_mfcc:
            feature_vector.append(np.mean(feature))
            feature_vector.append(np.var(feature))

        for feature in features.delta2_mfcc:
            feature_vector.append(np.mean(feature))
            feature_vector.append(np.var(feature))

        feature_vector.append(np.mean(features.rmse))
        feature_vector.append(np.var(features.rmse))

        return feature_vector
        
    def get_feature_by_file(self,audio):
        print("Extacting feature:", audio)
        try:
            features = FeatureExtraction()
            features.loadFile(audio)
            features.melspectrogram()
            features.extractmfcc()
            features.extractrmse()
        except ValueError:
            self.failed_file.apppend(file_path)

        feature_vector = []

        for feature in features.mfcc:
            feature_vector.append(np.mean(feature))
            feature_vector.append(np.var(feature))

        for feature in features.delta_mfcc:
            feature_vector.append(np.mean(feature))
            feature_vector.append(np.var(feature))

        for feature in features.delta2_mfcc:
            feature_vector.append(np.mean(feature))
            feature_vector.append(np.var(feature))

        feature_vector.append(np.mean(features.rmse))
        feature_vector.append(np.var(features.rmse))

        return feature_vector
        
    def __process_dataset(self):
        starttime = time.time()
        for i , (dirpath, dirnames, filenames) in enumerate(os.walk(self.DATASET_PATH)):
              if dirpath is not self.DATASET_PATH:
                label = dirpath.split("/")[-1]
                # print(label)
                print("Processing:", label)
                for file in filenames:
                  #load audio
                  file_path = os.path.join(dirpath,file)

                  # print(file_path)

                  #exctract mfcc
                try:
                    features = FeatureExtraction()
                    features.loadFile(file_path)
                    features.melspectrogram()
                    features.extractmfcc()
                    features.extractrmse()
                except ValueError:
                    self.failed_file.apppend(file_path)

                feature_vector = []

                for feature in features.mfcc:
                    feature_vector.append(np.mean(feature))
                    feature_vector.append(np.var(feature))

                for feature in features.delta_mfcc:
                    feature_vector.append(np.mean(feature))
                    feature_vector.append(np.var(feature))

                for feature in features.delta2_mfcc:
                    feature_vector.append(np.mean(feature))
                    feature_vector.append(np.var(feature))

                feature_vector.append(np.mean(features.rmse))
                feature_vector.append(np.var(features.rmse))

                self.X = np.vstack((self.X,[feature_vector]))
                if label == 'success':
                    self.Y = np.vstack((self.Y,[0,1]))
                    self.processed_counter += 1
                    print("Done ", self.processed_counter, file_path,' label=',label)
                elif label == 'stuttered':
                    self.Y = np.vstack((self.Y,[1,0]))
                    self.processed_counter += 1
                    print("Done ", self.processed_counter, file_path,' label=',label)
                else:
                    self.unexpected_label.append(file_path)
                    print("Fail ", self.processed_counter, file_path,' label=',label)

        for fail in self.unexpected_label:
            print("unexpected_label ", file_path, " !")

        for fail in self.failed_file:
            print("fail ", file_path, " !")

        # print("finished all!")
        print('Time taken = {} seconds'.format(time.time() - starttime))    
        self.DATASET = np.hstack((self.X,self.Y))

    def load_dataset(self,dataset_path):
        self.DATASET_PATH = dataset_path

        if os.path.exists(self.DATASET_PATH):
            print("Dataset exist!")
        else:
            print('Not found ',self.DATASET_PATH)
            return

        self.FILE_NAME, self.FILE_TYPE = os.path.splitext(self.DATASET_PATH)

        print("Loading ", self.DATASET_PATH)
        if self.FILE_TYPE == '.csv':
            print('Detect as .csv file')
            self.DATA = np.genfromtxt(self.DATASET_PATH, delimiter=',')
        elif self.FILE_TYPE == '.gz':
            print('Detect as .gz file')
            self.DATA = np.loadtxt(self.DATASET_PATH)
        else:
            print("Only support .gz and .csv file")
            return False

        self.X = self.DATA[:, 0:80]
        self.Y = self.DATA[:, 80:]

    def convert_to_csv(self,output_file):
        if os.path.exists(output_file):
            os.remove(output_file)
        np.savetxt(output_file,self.DATA, delimiter=',')
        print('Converted to',output_file)      

    def __write_to_file(self):
        if os.path.exists(self.OUTPUT_PATH):
            os.remove(self.OUTPUT_PATH)

        np.savetxt(self.OUTPUT_PATH, self.DATASET)
        print('Saved to',self.OUTPUT_PATH)  

    def get_x(self):
        return self.X

    def get_y(self):
        return self.Y