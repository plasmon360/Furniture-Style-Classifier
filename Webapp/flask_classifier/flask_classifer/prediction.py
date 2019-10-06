import torch
from torch.nn import functional as F
from pytorch_utils.model_utils import transfer_learning_model
from torchvision import transforms, models
import io, os
import torchvision.transforms as transforms
from PIL import Image
from flask_classifer import app

def transform_image(img):
    ''' img can be image bytes or image filepath'''
    my_transforms = transforms.Compose([transforms.Resize(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(*imagenet_stats)])
    image = Image.open(img)
    return my_transforms(image).unsqueeze(0)


imagenet_stats = ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
class_mapping = {'Arts and Crafts': 0,
                 'Mid-century-model': 1, 'Rustic': 2, 'Traditional': 3}
classes = ['Arts and Crafts', 'Mid-Century Modern', 'Rustic', 'Traditional']
print('Load Transfer Learning Model')
net = transfer_learning_model(
    model_original=models.resnet34(pretrained=False), number_classes=4)
checkpoint = torch.load(os.path.join(app.instance_path,'Checkpoints/checkpoint.pth') 
,map_location=torch.device("cpu"))

net.load_state_dict(checkpoint['model'])
net.eval()



def get_prediction(image_bytes, critical_probability = 0.2):
    tensor = transform_image(image_bytes)
    logit = net.forward(tensor)
    out = F.softmax(logit, dim=1).squeeze()
    probs, idx = out.sort(descending=True)
    # predicted_class = str(torch.max(logit).item())
    predicted_class = classes[idx[0]] if probs[0]>critical_probability else 'Not able to predict'
    probabilities= {}
    for label, prob in zip([classes[i] for i in idx], probs):
        probabilities[label] = round(prob.item()*100,4)
    return predicted_class, probabilities
