''' 
p_datautils.py:  Just some routines that we use for moving data around
'''
from __future__ import print_function
import numpy as np
import librosa
import os
from os.path import isfile


def get_class_names(path="Preproc/Train/"):  # class names are subdirectory names in Preproc/ directory
    class_names = sorted( os.listdir(path) ) # sorted for consistency; but not always same as 'ls'
    return class_names

def get_total_files(path="Preproc/Train/"): 
    sum_total = 0
    subdirs = os.listdir(path)
    for subdir in subdirs:
        files = os.listdir(path+subdir)
        n_files = len(files)
        sum_total += n_files
    return sum_total

def get_sample_dimensions(path='Preproc/Train/'):
    classname = os.listdir(path)[0]
    files = os.listdir(path+classname)
    infilename = files[0]
    audio_path = path + classname + '/' + infilename
    melgram = np.load(audio_path)
    print("   get_sample_dimensions: melgram.shape = ",melgram.shape)
    return melgram.shape
 

def encode_class(class_name, class_names):  # makes a "one-hot" vector for each class name called
    try:
        idx = class_names.index(class_name)
        vec = np.zeros(len(class_names))
        vec[idx] = 1
        return vec
    except ValueError:
        return None


def decode_class(vec, class_names):  # generates a number from the one-hot vector
    return int(np.argmax(vec))


# can be used for test dataset as well
def build_dataset(path="Preproc/Train/",shuffle=True, load_frac=1.0):

    class_names = get_class_names(path=path)
    print("class_names = ",class_names)

    total_files = get_total_files(path=path)
    print("total files = ",total_files)

    nb_classes = len(class_names)

    total_load = int(total_files * load_frac)

    # pre-allocate memory for speed (old method used np.concatenate, slow)
    mel_dims = get_sample_dimensions(path=path)  # Find out the 'shape' of each data file
    print(" melgram dimensions: ",mel_dims)
    X = np.zeros((total_load, mel_dims[1], mel_dims[2], mel_dims[3]))   
    Y = np.zeros((total_load, nb_classes))  
    paths = []

    count = 0
    for idx, classname in enumerate(class_names):
        this_Y = np.array(encode_class(classname,class_names) )
        this_Y = this_Y[np.newaxis,:]
        class_files = os.listdir(path+classname)
        n_files = len(class_files)
        n_load =  int(n_files * load_frac)
        printevery = 100

        file_list = class_files[0:n_load]
        if (shuffle):                       # preproc already shuffled btw
            np.random.shuffle(file_list)  
        for idx2, infilename in enumerate(file_list):          
            audio_path = path + classname + '/' + infilename
            if (0 == idx2 % printevery):
                print(" Loading class ",idx+1,"/",nb_classes,": \'",classname,
                    "\', File ",idx2+1,"/", n_load,": ",audio_path,"                  ", 
                    sep="")

            
            melgram = np.load(audio_path)
            
            X[count,:,:] = melgram
            Y[count,:] = this_Y
            paths.append(audio_path)     
            count += 1
 
    sr = 44100    # uh...probably shouldn't be hard-coding this. ??

    return X, Y, paths, class_names, sr