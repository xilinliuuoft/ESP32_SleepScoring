# import tensorflow as tf
# from tensorflow import keras
import numpy as np
# from sklearn.model_selection import KFold
import argparse
import random
import os
import tensorflow as tf
from tensorflow import keras
from model import simpleCNN, doubleCNN, fashionCNN,doubleCNNBiLSTM

from data_preprocess import preprocess_data
from sklearn.model_selection import KFold

        
  
def run(batch_size, pretrain_epochs):
    allfiles = os.listdir(parameters.data_dir)
    best_acc = 0
    all_scores = []
    kfold = KFold(n_splits=parameters.k_folds, shuffle=True, random_state = 1)
    
    fold_no = 1
    for i, (trainfile_idx, testfile_idx) in enumerate(kfold.split(allfiles)):
        print("trainfile_idx", trainfile_idx)
        print("testfile_idx", testfile_idx)
        x_train, y_train, x_val, y_val = preprocess_data(parameters.data_dir, trainfile_idx, testfile_idx)

        # y_train = keras.utils.to_categorical(y_train, 5)
        # y_val = keras.utils.to_categorical(y_val, 5)
        
        if parameters.model_mode == 'simpleCNN':
            model = simpleCNN()
            
        if parameters.model_mode == 'doubleCNN':
            model = doubleCNN()
            
        if parameters.model_mode == 'fashionCNN':
            model = fashionCNN()
        
        if parameters.model_mode == '2CNNsBiLSTM':
            model = fashionCNN()
        # Compile the model
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        # Create a checkpoint for the current fold
        if not os.path.exists("./checkpoint"):
            os.mkdir("./checkpoint")
        
        if not os.path.exists("./checkpoint/"+parameters.model_mode):
            os.mkdir("./checkpoint/"+ parameters.model_mode) 
            
        if not os.path.exists("./checkpoint/"+parameters.model_mode+"/fold_"+str(fold_no)):
            os.mkdir("./checkpoint/"+ parameters.model_mode+"/fold_"+str(fold_no)) 
        
        filepath = "./checkpoint/"+parameters.model_mode+"/fold_"+str(fold_no)+ "/cp.ckpt"
        checkpoint = keras.callbacks.ModelCheckpoint(filepath=filepath, verbose=1, save_best_only=True)
    
        print('------------------------------------------------------------------------')
        print(f'Training for fold {fold_no} ...')

        y_train = keras.utils.to_categorical(y_train, 5)
        y_val = keras.utils.to_categorical(y_val, 5)

        print('y_train',y_train.shape)
        print('y_val',y_val.shape)
        
        x_train = x_train.swapaxes(1, 2)
        print("aaa x_train", x_train.shape)
        get_x = x_train[:100, :]
        print("aaa get_x", get_x.shape)
        # x_train = x_train.reshape(9585, 1, 7680, 1)
        # Train the model
        model.fit(x=x_train, y=y_train, epochs=pretrain_epochs, batch_size=batch_size, callbacks=[checkpoint])
        
        # evaluate the model on the validation data
        x_val = x_val.swapaxes(1, 2)
        val_loss, val_acc = model.evaluate(x_val, y_val)

        all_scores.append(val_acc)
        
        # keep track of the best accuracy
        if val_acc > best_acc:
            best_acc = val_acc
            best_model = model
        
        # break
        # Increase fold number
        fold_no = fold_no + 1
        
    print("Validation accuracy:", np.mean(all_scores))
    # save the best model
    if not os.path.exists("./output"):
        os.mkdir("./output")
        
    if not os.path.exists("./output/bestModel"):
        os.mkdir("./output/bestModel")
        
    best_model.save("result/output/bestModel/lfinalbest_"+parameters.model_mode+"model")
    
    

if __name__ == '__main__':
    random.seed(1337)
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--data_dir', type=str, default='data/eeg_fz_ler')
    # parser.add_argument('--checkpoint_dir', type=str, default='checkpoint')
    # parser.add_argument('--output_dir', type=str, default='result/output')
    parser.add_argument('--k_folds', type=int, default=21)
    parser.add_argument('--pretrain_epochs', type=int, default=50)
    parser.add_argument('--resume', type=bool, default=False)
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--model_mode', type=str, default='doubleCNN',choices=['simpleCNN', 'doubleCNN', '2CNNsBiLSTM', 'fashionCNN'])
    
    args = parser.parse_args()
    parameters = args
    print(args)
    print(parameters.batch_size)
    
    run(parameters.batch_size, parameters.pretrain_epochs)
    
    # run(32, 3)