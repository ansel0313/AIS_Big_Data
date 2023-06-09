import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'
import sys
sys.path.append(os.getcwd() + '/..')
from absl import logging
logging._warn_preinit_stderr = 0
logging.warning('...')
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import itertools
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import tensorflow as tf
from load_data_30_turn import load_all_data, load_test_data, load_saved_data
from models import get_model
import ENN_loss
from ENN_loss import build_evidential_cross_entropy, build_evidential_mse
import time


vb_dir   = os.path.dirname(__file__)
data_dir = os.path.join(vb_dir, "resources/")
results_dir = os.path.join(vb_dir, "results/")

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    #print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


t11, f12, f13, f21, t22, f23, f31, f32, t33 = 0, 0, 0, 0, 0, 0, 0, 0, 0
acc = 0

# tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
# features = ['x', 'y', 'cog', 'sog']
features = ['cog']
dim = len(features)
timesteps = 60 # number of sequences per batch
CLASSES = 2
# load_data
X_data, Y_data = load_all_data(timesteps, dim, features, CLASSES)
# X_data, Y_data = load_saved_data()

algo = "evidential_turn_30"
nr_iter = 1
# train_time, test_time = 0, 0

for val in range(nr_iter):
    np.random.seed(val)
    x_train, x_test, y_train, y_test = train_test_split(X_data, Y_data, test_size=0.10)
    start_time = time.time()
    ############ model #######################
    lambda_callback = ENN_loss.ENN_lambda_update()
    loss_function = build_evidential_mse(lambda_callback) # build_evidential_cross_entropy(lambda_callback)
    model = get_model(algo, timesteps, dim, CLASSES)
    # Compile and fit the model!
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss=loss_function)
    epochs = 150
    history = model.fit(x_train, y_train, validation_data=(x_test, y_test), batch_size=16, epochs=epochs, verbose=1, callbacks=[lambda_callback])  # callbacks=tf.keras.callbacks.Callback
    # train_time += (time.time() - start_time) * 1000 / x_train.shape[0]

    plt.figure(figsize=(5, 3), dpi=200)
    plt.plot(history.history["loss"], "r-", label="training")
    plt.plot(history.history["val_loss"], "b--", label="validation")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.pause(0.001)
    plt.savefig(results_dir + "train_loss_val_loss_epochs_" + str(epochs) + ".png")

    # model.summary()

    # Predict and plot using the trained model
    # start_time = time.time()
    evidence = model(x_test)
    evidence = tf.nn.relu(evidence)
    # evidence = np.array(tf.clip_by_value(evidence,clip_value_min=-10000, clip_value_max=300))
    if evidence.min() < 0:
        evidence = np.exp(evidence)
        S = np.sum(evidence, axis=1) + CLASSES
        y_pred = np.divide(evidence+1,S.reshape((len(evidence), 1))) # evidence/S.T #
        uncertainty = np.divide(CLASSES*np.ones_like(S.reshape((len(evidence), 1))), S.reshape((len(evidence), 1)))
    else:
        S = np.sum(evidence, axis=1) + CLASSES
        y_pred = np.divide(evidence+1,S.reshape((len(evidence), 1))) # evidence/S.T
        uncertainty = np.divide(CLASSES * np.ones_like(S.reshape((len(evidence), 1))), S.reshape((len(evidence), 1)))

    plt.figure(figsize=(5, 3), dpi=200)
    plt.plot(uncertainty, "k.")
    plt.xlabel("Validation Samples")
    plt.ylabel("Uncertainty")
    plt.savefig(results_dir + "uncertainty_val_epochs_" + str(epochs) + ".png")
    # plot_predictions(x_train, y_train, x_test, y_test, y_pred, dim, scaling)
    # test_time += (time.time() - start_time) * 1000 / x_test.shape[0]

    acc += accuracy_score(y_test.argmax(axis=1), y_pred.argmax(axis=1))

    # cm = confusion_matrix(target_test.argmax(axis=1), pred.argmax(axis=1))
    # cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    # print('confusion matrix : \n',cm)
    # cnf_matrix = confusion_matrix(target_test.argmax(axis=1), pred.argmax(axis=1))
    # print('classification_report : \n', classification_report(y_test,pred))

    r11, r12, r21, r22 = confusion_matrix(y_test.argmax(axis=1), y_pred.argmax(axis=1)).ravel()
    t11 += r11
    f12 += r12
    f21 += r21
    t22 += r22

    print("Completed run ", val)


print(">>>>>>>>>>>>>>>>>>>>>>>>> \n accuracy : ", acc / nr_iter)
cm = np.reshape(np.array([t11, f12, f21, t22]), (2, 2))
# print(cm)

# cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
print(cm)
# plot_confusion_matrix(cm, ['normal', 'anomaly'], normalize=False, title='Confusion matrix')
# plt.show()

# save the model to disk
filename = 'ENN_30_turn_rostock.h5'
model.save(data_dir + filename)


# print('train time per 1000 samples= ', train_time / nr_iter)
# print('test time per 1000 samples= ', test_time / nr_iter)