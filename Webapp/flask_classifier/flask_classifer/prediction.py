import os
import torch
from PIL import Image
from torch.nn import functional as F
from torchvision import models, transforms
from flask_classifer import app
from pytorch_utils.model_utils import transfer_learning_model


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


class_mapping = {
    'Arts and Crafts': 0,
    'Mid-century-model': 1,
    'Rustic': 2,
    'Traditional': 3
}

classes = ['Arts and Crafts', 'Mid-Century Modern', 'Rustic', 'Traditional']

print('Loading Transfer Learning Model')

net = transfer_learning_model(model_original=models.resnet34(pretrained=False),
                              number_classes=4)

checkpoint = torch.load(os.path.join(app.instance_path,
                                     'Checkpoints/checkpoint.pth'),
                        map_location=torch.device("cpu"))

net.load_state_dict(checkpoint['model'])
net.eval()


def get_prediction(img):
    try:
        tensor = transform_image(img)
        logit = net.forward(tensor)
        out = F.softmax(logit, dim=1).squeeze()
        probs, idx = out.sort(descending=True)
        predicted_class = classes[idx[0]]
        probabilities = {}
        for label, prob in zip([classes[i] for i in idx], probs):
            probabilities[label] = round(prob.item() * 100, 4)
    except Exception as e:
        print(str(e))
        predicted_class = 'Unable to predict'
        probabilities = {}
    return predicted_class, probabilities
