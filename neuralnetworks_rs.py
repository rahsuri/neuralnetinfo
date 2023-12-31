# -*- coding: utf-8 -*-
"""NeuralNetworks_RS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iC1FuJPu6ZvFjnY0zJE32YNeIMtXbEFB

Here I have annotated a basic digit recognition neural network that anyone
even with limited coding experience can grasp. I'd recommend watching a video
on the basic algorithm of a neural network prior to going through the code to
get the most out of this. Please feel free to let me know if you have any questions.  - *Rahul Suri*
"""

#libraries used for our neural network

#used for extra math components
import numpy as np

#works with some numpy functions - not necessary in this context
import pandas as pd

#basic data manipulation
import pickle

#importing our dataset of handwritten numbers
from keras.datasets import mnist

#used to visualize the handwritten image
import matplotlib.pyplot as plt

#basic ReLU - return the maximum value. If the max value is negative, return 0.
def ReLU(x):
    return np.maximum(x, 0)

#returns the derivative of the ReLU function. Simply returns 1 if the value is
# over 0, and 0 if the function is less than or equal to 0. In this case it
# returns a boolean, which is a true of false value. Since in python true is
# equal to 1 false is equal to 0, we can use it instead of if then branches.
def dx_ReLU(x):
    return x > 0

#soft max function used to calculate the probability of a node being true
#this function is used so that significant values are noticed more than insignificant
def soft_max(x):

    #incase our values are too high for the exponentiation, we want to minus all
    # the values by the maximum so they are easier to deal with
    # (for the computer).
    x = x - np.max(x)

    #getting our eulers numbers.
    exp_x = np.exp(x)

    #taking every value in the exp_x array and finding its probability from 0-1
    #this makes it so the final array has values that add up to 1
    return exp_x / exp_x.sum(axis=0)

#this creates the starting weight(W) and bias(b) values for our neural network.
#since it doesn't matter about the starting values due to the learning process,
#these values can be randomized.
def initial_params(size):
    W1 = np.random.rand(10,size) - 0.5
    b1 = np.random.rand(10,1) - 0.5
    W2 = np.random.rand(10,10) - 0.5
    b2 = np.random.rand(10,1) - 0.5
    return W1,b1,W2,b2

#our forward propagation algorithm. This takes in our input array and applies
#our activation function (ReLu) and then calculates the output probabilities
#using our softmax function.
def for_prop(X,W1,b1,W2,b2):

    #X - testing data set
    #W1 - weights connected from the input layer to the first layer
    #b1 - bias' for the first layer
    #W2 - weights connected from the first layer to the second layer (output)
    #b2 - bias' for the second layer

    #using dot product on the weights of the going to the first nodes and
    # applying the bias value to obtain the weighted sum values, which results
    # in the array Z1 (all the weighted sums).
    Z1 = W1.dot(X) + b1 #array dimensions: (10,m)

    #now we can apply our activation function on the weighted sum values, which
    # in this case we are using the ReLU activation function, to finally get the
    # value of the nodes in the first layer.
    A1 = ReLU(Z1) #array dimensions: (10,m)

    #we are now repeating the process as we did before, but now finding the
    # weighted sums that we will be using for the second layer.
    Z2 = W2.dot(A1) + b2 #array dimensions: (10,m)

    #after obtaining the weighted sums for the second layer, we are now applying
    # our ReLU activation function once again to obtain our second layer values
    # which also happens to be our prediction layer (output layer). This means
    # we must apply our softmax function, so that each of the 10 nodes connected
    # to this layer have probabilites that all add up to 1.0 (100%). Each node
    # corresponds to a possible value the image could hold, and each value of
    # the node represents the possbility it is in fact that value.
    A2 = soft_max(Z2) #array dimensions: (10,m)

    #Z1 - weighted sums of the first layer
    #A1 - node values of the first layer
    #Z2 - weighted sums of the second layer
    #A2 - node values of the second layer (prediction layer)
    return Z1, A1, Z2, A2

#helper func used for backpropagation training. Creates an array of all 0s and
#marks 1 corresponding to the category that the item falls under (for example,
# if there are 5 categories and the item falls under the 3rd one, the 3rd column
# is marked with 1 as so: [0,0,1,0,0]).
def one_hot(Y):

    #Y = data set of our annotated digits

    #creates a one hot array using the training set.
    # + np.zeros creates an array with 0s to start
    # + Y.max() + 1 finds how many categories there are. Since we are doing
    # digit recognition, there are 10 (0, 1,..9).
    # + Y.size gives us how many examples there are in the training set.
    #this all together creates an array of 0s with 10 categories (rows) and
    # in this case 6000 examples (columns).
    one_hot_Y = np.zeros((Y.max()+1,Y.size))

    #changes the appropriate value in the array from 0 to 1. This method is
    # using numpy's advanced array indexing.
    # + Y is the training array with size 6000 containing numbers from 0 to 9.
    # + np.arange(Y.size) creates an array with the numbers 0 to 6000 (exc).
    #this marks a 0 in each of the 6000 columns with a 1 depending on what the
    # value from the Y array is. For example, if the 12th column (representing
    # the 12th example) has the value of 4 from the Y array, the 0 in the 4th
    # row is changed to a 1.
    one_hot_Y[Y,np.arange(Y.size)] = 1

    #one_hot_Y - one hot array
    return one_hot_Y

    #our essential backpropagation function. The aim of this function is to
    # calculate gradients in the form of derivatives of the cost function
    # so that we can update our paramaters accordingly. The goal is to minimize
    # the value of the cost function, as the higher the cost function is, the
    # more innaccurate our predictions are.
def back_prop(X, Y, A1, A2, W2, Z1, m):

    #X - images of the digits, in pixel arrays
    #Y - annotated digits
    #A1 - values of our first layer
    #A2 - values of our second (prediction) layer
    #W2 - weights going into our second layer from first layer
    #Z1 - weighted sum of our first layer
    #m - size of our training set

    #turning the annotated dataset into a one hot array to compare our computed
    # values against
    one_hot_Y = one_hot(Y)

    #creating an array that has the differences in values between the computed
    # prediction layer and the correct prediction layer. This is essentially
    # our cost function.
    dZ2 = 2*(A2 - one_hot_Y) #array dimensions: (10,m)

    #calculating the weights that are going from the second layer into the the
    # first layer, using a dot product array between our difference array above
    # and a transposed array of the first hidden layer values.
    # + A1.T creates the transposed array. This swaps the dimensions of the
    # array. For example, an array with 3 columns and 2 rows will become an array
    # with 2 columns and 3 rows. The reason we do this is so that the dZ2 and A1
    # array are in proper dimensions to be multiplied with eachother via
    # dotproduct. Not transposing first would cause dimensional error.
    # + .dot() multiplies the matrices together, allowing us to see which values
    # in the A1 array (the values of the first layer) contribute to the most
    # error in our ouput.
    #1/m is a scaling factor we are using to average the gradient value across
    # m training data points.
    dW2 = 1/m * (dZ2.dot(A1.T)) #array dimensions: (10,10)

    #take the sum of the errors values (the difference between the computed
    # value and the correct value) across all of the training values and then
    # applies our 1/m scaling factor. This creates an array that contains bias
    # values to mitigate the error in our computations while finding our
    # weighted sums (see above for info on weighted sum), thus making our
    # prediction more accurate.
    # + the .sum(x, axis) function here is used so that we can sum the values
    # along axis=1, which is the columns, since each column represents a
    # prediction value.
    db2 = 1/m * np.sum(dZ2,1) #array dimensions: (10,1)

    #first we are multipying the W2 array (the weights from the first to second
    # layer) with the dZ2 array, the array that shows where the errors are in
    # our predictions, to obtain a new weight array. Then, we are applying
    # our ReLU derivative function on our Z1 array, which weighted sums from
    # first layer, and multiplying that with our previous array, giving us a
    # gradient array that propagates error values through the array.
    dZ1 = W2.T.dot(dZ2)*dx_ReLU(Z1) #array dimensions: (10,m)

    #calculating the weights going from the first layer into the input layer.
    # for this we use the dZ1 array from before that represents the weighted
    # sums for the first layer, and then use a transposed array of the X array.
    # in this context, the X array is the array that contains the pixel values
    # of the 28 x 28 image, so in total 784 pixels per image, and m images for
    # the size of the training set. The X array is the input layer, so we are
    # calculating what the weights should be for a given input, which is key in
    # making the correct prediction.
    dW1 = 1/m * (dZ1.dot(X.T)) #10, 784

    #lastly, we are calculating the bias values for the connection between the
    # input layer and the first hidden layer. We are simply going to sum the of
    # the values in the dZ1 array across the columns (axis=1) to obtain the
    # values that we need to correct the connection between the first layer and
    # the input layer.
    db1 = 1/m * np.sum(dZ1,1) # 10, 1

    #dW1 - gradient of our first layer of weights
    #db1 - gradient of our first layer of bias' values
    #dW2 - gradient of our second layer of weights
    #db2 - gradient of our second layer of bias' values
    return dW1, db1, dW2, db2

#this function is crucial for the learning stage of our neural network. It
# takes the gradient values that we obtained via the backpropagation
# function, and then uses those values to update our parameters accordingly.
# + the alpha value is the learning rate of our updates. In this case, we
# will be using the value 0.15. We want to make sure our learning rate is
# high enough to the point where we can see improvements in our networks
# learning, and we also want it to be low enough where we dont overshoot.
def update_wb(alpha, W1, b1, W2, b2, dW1, db1, dW2, db2):

    #alpha - learning rate
    #W1 - weights for first layer
    #b1 - bias' for first layer
    #W2 - weights for second layer
    #b2 - bias' for second layer
    #dW1 - gradient for first layer of weights
    #dW2 gradient for second layer of weights
    #db2 gradient for first layer of bias'

    #here we are using the alpha value and multiplying it with the gradient
    # array that we calculated in our backprop function. The dW1 array indicates
    # how far off our values are from the correct values, so we want to multiply
    # our alpha value (0.15) to slowly update our first layer weights
    # contained by the W1 array.
    W1 -= alpha * dW1

    #same principle is being done here. We are using the reshape method (see
    # notes) to rearrange the array so that it is in the same dimensions as our
    # original b1 array. This will update our bias' marginially in the correct
    # direction.
    b1 -= alpha * np.reshape(db1, (10,1))

    #contuining to update our values. This will be for the second layer of weights
    #, which happens to be the weights going into our prediction layer.
    W2 -= alpha * dW2

    #finally, we are updating the bias values for the second layer connection.
    b2 -= alpha * np.reshape(db2, (10,1))

    #W1 - updated weights for first layer
    #b1 - updated bias' for first layer
    #W2 - updated weights for second layer
    #b2 - updated bias' for second layer
    return W1, b1, W2, b2

#gives us the prediction that our model has made. takes A2, the prediction
# layer array, as input.
def predictions(A2):

    #A2 - values from our prediction layer

    #using the argmax function, we return the index of the maximum value of our
    # prediction array. since the array contains the probabilities of the data
    # belonging to a certain catagory, it returns the catagory with the highest
    # percentage which will be a number from 0-9, our desired output. Since the
    # axis for our argmax is 0, we return the max of each column, where each
    # column represents a piece of training data.
    return np.argmax(A2, 0)

#function to determine the accuracy of of the the model at the current
# state.
def accuracy(prediction, Y):

    #prediction - an array of our predicted values using the model
    #Y - the array of correct values for each handwritten digit

    # The expression prediction == Y will return an array of truth
    # values, and then we will sum all those values using .sum(). We will then
    # divide that number by the size of the Y array, giving us a percentage of
    # how many predictions were correct (returned true) for the entire Y array.
    return np.sum(prediction == Y)/Y.size

#the main function in our neural network. utilizes the previous functions we
# created to train a model and returns the final values.
def train_model(X, Y, alpha, iterations):

    #X - dataset of training values
    #Y - dataset of correct annotations for each training value from X
    #alpha - our learning rate (used in updating bias' & weights)
    #iterations - number of iterations of training cycles

    #size - number of input values per data point (784 for a 28 x 278 image)
    #m - number of data points, 6000 since that is the size of our training set
    size , m = X.shape

    #creating out initial paramaters, these are randomized to start (see initial
    # param function)
    W1, b1, W2, b2 = initial_params(size)

    #this is the most important part of our neural network. Here, we run our
    # algorithm of forward prop, back prop, and then we update the paramaters
    # based on returned values. The iterations is how many times we are going
    # to run our training functions. Since it takes about 200 iterations for
    # this specific model to get to a relatively high accuracy rate (we get
    # about 80-95%), we will just do 200 iterations. You can increase this if
    # desired.
    # + we are setting up a for loop that will run "iterations" times.

    for i in range(iterations):

        #running our forward propagation
        Z1, A1, Z2, A2 = for_prop(X, W1, b1, W2, b2)

        #running our backward propagation
        dW1, db1, dW2, db2 = back_prop(X, Y, A1, A2, W2, Z1, m)

        #updating our values based off of the results.
        W1, b1, W2, b2 = update_wb(alpha, W1, b1, W2, b2, dW1, db1, dW2, db2)

        #simple if statement that gives us updates every 5% of the way we are
        # to completing the training. So, for 200 iterations it will give us an
        # update every 10 iterations completed.
        if (i+1) % int(iterations/10) == 0:

            #printing the iteration we are on
            print(f"Current Iteration: {i+1} / {iterations}")

            #printing the accuracy of the model in this current iteration
            prediction = predictions(A2)
            print(f"Current Model Accuracy: {accuracy(prediction, Y):.3%}")

    print("Model training successfully completed.")
    #W1 - our final, accurate first layer of weights
    #b1 - final values for the first layer of bias'
    #W2 - final values for second layer of weights
    #b2 - final values for the second layer of bias values
    return W1, b1, W2, b2

#using the trained data we get from our previous functions, we can use this
# function to make a final prediction; a digit from 0-9.
def make_predictions(X, W1 ,b1, W2, b2):

    #X - our data set
    #W1 - first layer weights
    #b1 - first layer bias'
    #W2 - second layer weights
    #b2 - second layer bias'

    #here we are running our forward propagation function to get a prediction
    # using the given data set, weights, and bias' we have enetered. In this
    # function, since we are making a final prediction, the values we are using
    # will be the final, trained values. Since we only want the prediction layer
    # values to make a prediction, we are only extracting the A2 array (the
    # prediction layer) and discarding the other information.
    _, _, _, A2 = for_prop(X, W1, b1, W2, b2)

    #now, we are using our predictions function to gather a digit wise
    # prediction from inputting the prediction values.
    prediction = predictions(A2)

    #simply returning the prediction, which will be a value from 0-9.
    return prediction

#this function is used for printing our models predicted value, the correct
# value, and an image of the handwritten digit.
def show_prediction(index,X, Y, W1, b1, W2, b2):

    #index - an index for the specific handwritten digit we are referencing
    #X - the data set we are indexing
    #Y - the array of labels for the data (used to print the correct value)
    #W1 - first layer weights
    #b1 - first layer bias'
    #W2 - second layer weights
    #b2 - second layer bias'

    #the vector of the image's pixel values
    vect_X = X[:, index,None]

    #the prediction our model makes using our make_predictions function
    prediction = make_predictions(vect_X, W1, b1, W2, b2)

    #the label of the image using our index on the label array (Y)
    label = Y[index]

    #printing the prediction
    print("Prediction: ", prediction)

    #printing the label of the image
    print("Label: ", label)

    #reshaping the image and applying our scale factor to normalize values
    current_image = vect_X.reshape((WIDTH, HEIGHT)) * SCALE_FACTOR

    #using matplotlib functions to print out our visualized handwritten digit.
    plt.gray()
    plt.imshow(current_image, interpolation='nearest')
    plt.show()

#===MAIN===

#loading in the data we will be using
(X_train, Y_train), (X_test, Y_test) = mnist.load_data()

#our scale factor we use so that the data is digestible by our model and our
# printing functions
SCALE_FACTOR = 255

#gathering some data characteristics to create our training and testing array
WIDTH = X_train.shape[1]
HEIGHT = X_train.shape[2]

#creating our training and testing arrays. The width and height are the
# characteristics of the image, and in this case it is a 28x28 pixel image.
# the .shape[0] value is the number of datapoints there are, in this case it is
# 6000. finally, our scale factor is applied.
#this will result in a scaled, reshaped array that contains 6000 data points
# with 784 values in each (1 value for each 28x28 pixels).
X_train = X_train.reshape(X_train.shape[0],WIDTH*HEIGHT).T / SCALE_FACTOR
X_test = X_test.reshape(X_test.shape[0],WIDTH*HEIGHT).T  / SCALE_FACTOR

#training our model
W1, b1, W2, b2 = train_model(X_train, Y_train, 0.15, 200)

#these functions are necessary to run the function, but they are useful for
# future reference.

#this function creates a file called "trained_params.pk1" and dumps our data in
# the file as bytes.
with open("trained_params.pkl","wb") as dump_file:
    pickle.dump((W1, b1, W2, b2),dump_file)

#this function reads our file and retrieves the data to be used in our
# show prediction functions.
with open("trained_params.pkl","rb") as dump_file:
    W1, b1, W2, b2=pickle.load(dump_file)

#making predictions using our trained model.
show_prediction(0,X_test, Y_test, W1, b1, W2, b2)
show_prediction(1,X_test, Y_test, W1, b1, W2, b2)
show_prediction(2,X_test, Y_test, W1, b1, W2, b2)
show_prediction(100,X_test, Y_test, W1, b1, W2, b2)
show_prediction(200,X_test, Y_test, W1, b1, W2, b2)
show_prediction(150,X_test, Y_test, W1, b1, W2, b2)

#===NOTES===
#np.exp(x) returns e^x
#x.sum() returns the sum of all values contained in x
# + if you use sum(axis=0), it returns an array with the sums of each row
# + if you use sum(axis=1), it returns an array with the sums of each column
#np.random.rand(x, y)
#np.zeros(z, y, x) / np.array([v1, v2,...vx]) creates an array. the first one
# creates an array filled with 0s with z planes (z axis), y rows (y axis) and
# x columns (x axis). You can also do (y, x), for y rows and x columns, or
# simply just (x) for x columns.
# + .size returns the size of the array along the x axis (columns)
# + .shape returns the shape of the array in the format of (z, y, x), (y, x) or
# just (x).
# + .reshape reshapes the array to desired dimensions. Total elements must be
# the same as the original array.
#np.arange(start, stop, step)
#np.ndarray.T - transposes the array, swapping the dimensions of it. x becomes y
# and y becomes x.
#np.ndarray.dot - dot product of the array, in this case just performs standard
# matrix multiplication.
#np.argmax(x, axis) - provides the index of the maximum value in the given array.
# + if axis is 0, gives the index of the max value of each column.
# + if axis is 1, gives the index of the max value in each row.

#===TESTING===
#feel free to print out the training and testing data that we have obtained
# from the mnist dataset. Below I have initialized the train and test data.
# remove commenting and run the block to see what the data arrays look like.

# (X_train, Y_train), (X_test, Y_test) = mnist.load_data()

#X represents the image of the digit, expressed in an array of pixel values.

# print(X_train)

#Y represents the annotated digit images.

# print(Y_train)

#Also try out testing individual functions themselves to get a better
# understanding.