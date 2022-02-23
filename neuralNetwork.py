""" a simple neural network implementation """

from math import exp
from random import uniform

class NeuralNetwork:
    def __init__(self, nInput, nOutput):
        self.nInput = nInput
        self.nOutput = nOutput
        self.layerInput = []
        self.layerOutput = []
        self.hiddenLayers = []

    def add_hidden_layer(self, nNodes):
        
        # hiddenLayer = FCLayer(nNodes, self.nInput)
        # self.hiddenLayers.append(hiddenLayer)

        # if first layer, set input
        if len(self.hiddenLayers) == 0:
            self.hiddenLayers.append(FCLayer(nNodes, self.nInput))

        # if not first layer, set input size to previous output size
        else:
            self.hiddenLayers.append(FCLayer(nNodes, len(self.hiddenLayers[-1].nodes)))

    def setInput(self, input):
        self.layerInput = input

    def getOutput(self):
        return self.layerOutput

    def calculate(self):        
        # set input for first layer
        self.hiddenLayers[0].setInput(self.layerInput)
        
        for hiddenLayerIndex, hiddenLayer in enumerate(self.hiddenLayers):
            # calculate output for layer
            outputs = hiddenLayer.calculate()
            
            # set input for next layer if exists
            if hiddenLayerIndex < len(self.hiddenLayers) - 1:
                self.hiddenLayers[hiddenLayerIndex + 1].setInput(outputs)
                
            # if final layer, set output
            else:
                self.layerOutput = outputs
    def setParameters(self, parameters):
        print("setParameters: not implemented")
        pass

    def randomize(self):
        for layer in self.hiddenLayers:
            layer.randomize()

def sigmoid(x):
    return 1.0 / (1.0 + exp(-x))

def relu(x):
    return max(0, x)


class Perceptron:
    def __init__(self, size):
        self.size = size
        self.weights = []
        self.bias = 0
        self.input = []
        self.output = 0
    def setInput(self, input):
        self.input = input
    def randomize(self):
        self.weights = [uniform(-1, 1) for i in range(self.size)]
        self.bias = uniform(-1, 1)
    def calculate(self):
        self.output = sigmoid(sum([self.input[i] * self.weights[i] for i in range(len(self.input))]) + self.bias)
        return self.output

class FCLayer:
    def __init__(self, nNodes, nInput):
        self.nodes = [Perceptron(nInput) for i in range(nNodes)]
    def setInput(self, input):
        for node in self.nodes:
            node.setInput(input)
    def calculate(self):
        outputs = []
        for node in self.nodes:
            output = node.calculate()
            outputs.append(output)
        return outputs
    def randomize(self):
        for node in self.nodes:
            node.randomize()

    
