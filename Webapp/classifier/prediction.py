# TODO Some images are not being predicted properly. Figure out what is causing it.
import os

import torch
from PIL import Image
from torch.nn import functional as F
from torchvision import models, transforms

from classifier import app
from pytorch_utils.model_utils import transfer_learning_model

from flask import url_for
def transform_image(img):
    ''' img can be image bytes or image filepath'''
    IMAGENET_STATS = ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    my_transforms = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize(*IMAGENET_STATS)
    ])
    image = Image.open(img)
    return my_transforms(image).unsqueeze(0)


CLASSES = ['Arts and Crafts', 'Mid-Century Modern', 'Rustic', 'Traditional']

print('Loading Transfer Learning Model')

# Make a  empty CNN model
net = transfer_learning_model(model_original=models.resnet34(pretrained=False),
                              number_classes=4)

# Load a precomputed checkpoint weights
checkpoint = torch.load('./classifier/checkpoints/checkpoint.pth',
                        map_location=torch.device("cpu"))

net.load_state_dict(checkpoint['model'])

# Put the model in eval mode, so that it doent calculate gradients
net.eval()


def get_prediction(img):
    try:
        tensor = transform_image(img)
        logit = net.forward(tensor)
        out = F.softmax(logit, dim=1).squeeze()
        probs, idx = out.sort(descending=True)
        predicted_class = CLASSES[idx[0]]
        probabilities = {}
        for label, prob in zip([CLASSES[i] for i in idx], probs):
            probabilities[label] = round(prob.item() * 100, 4)
    except Exception as e:
        print(str(e))
        predicted_class = 'Unable to predict'
        probabilities = {}
    return predicted_class, probabilities
