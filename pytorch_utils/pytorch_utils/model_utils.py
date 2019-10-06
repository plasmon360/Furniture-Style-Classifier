from pytorch_utils.imports import *
from pytorch_utils.hooks import Hook

from torchvision.models import resnet34 as resnet
from torch import nn
from torch.nn.modules import Module
from collections import OrderedDict


def model_summary(model, dummy_batch = torch.rand(2,3,10,10)):
    '''PRovide the summary of model showing the size of the parameters and size of activations'''
    
    print(f"Input: {dummy_batch.shape}")
    print(50*'-')
    
    forward_hooks = {child_name: Hook(child) for child_name, child in model.named_children()}
    model.eval() # Put the model in eval mode.
    output = model(dummy_batch)
    
    for child_name, child in model.named_children():
        print(child_name.upper())
        print(50*'-')
        print(f"INPUT SHAPE: {forward_hooks[child_name].input_shape}")
        if len(list(child.parameters())):
            print('Parameters')
            for name, param in child.named_parameters():
                print(f"{name}: {param.shape}")
        else:
            print('No Parameters')
        print(f"OUTPUT SHAPE: {forward_hooks[child_name].output_shape}")
        print(50*'-')


def transfer_learning_model(model_original, number_classes, resnet_dummy_img_batch=torch.rand(1, 3, 224, 224)):
    '''
    creates a transfer learning model by stripping some layers and adding
    new layers that incude pooling, fully connected and output layers
    '''

    class Pooling_Layers(Module):
        '''Create Pooling layers'''

        def __init__(self):
            super().__init__()
            self.AdpAvgPool = nn.AdaptiveAvgPool2d((1, 1))
            self.AdpMaxPool = nn.AdaptiveMaxPool2d((1, 1))

        def forward(self, x):
            return torch.cat((self.AdpAvgPool(x), self.AdpMaxPool(x)), dim=1)

    class Flatten_4D_2D(Module):
        '''Flatten'''

        def __init__(self):
            super().__init__()

        def forward(self, x):
            # May be there is a better way
            return x.squeeze(dim=3).squeeze(dim=2)

    def FC_layers(in_features, number_classes, inter_features=512, p=0.5):
        '''Fully connected layers: in_features->inter_features->number_classes'''
        layers = OrderedDict()
        layers['BatchNorm'] = nn.BatchNorm1d(num_features=in_features)
        layers['Dropout'] = nn.Dropout(p=p/2)

        layers['FC1'] = nn.Linear(in_features, inter_features)
        layers['FC1 RELU'] = nn.ReLU(inplace=True)
        layers['FC1 BatchNorm'] = nn.BatchNorm1d(inter_features)
        layers['FC1 Dropout'] = nn.Dropout(p)

        layers['FC2'] = nn.Linear(inter_features, number_classes)
        return nn.Sequential(layers)

    # Freeze all the layers in the original_model
    for param in model_original.parameters():
        param.requires_grad = False

    base = list(model_original.named_children())[:-2]  # remove last two layers
    base.append(('Pooling Layers', Pooling_Layers()))  # add pooling layers
    base.append(('Flatten', Flatten_4D_2D()))  # add flatten layers
    base_pooling_flatten = nn.Sequential(
        OrderedDict(base))  # create a temp model

    # calculate the output of temp model with dummy image batch
    with Hook(base_pooling_flatten) as hook:
        # Take the first two images from the batch
        _ = base_pooling_flatten(resnet_dummy_img_batch)

    output_features_size = hook.output_shape[1]

    # Add Fully Connected layers
    base.append(('Fully Connected', FC_layers(output_features_size, number_classes)))

    transfer_learn_model = nn.Sequential(OrderedDict(base))

    return transfer_learn_model
