## This is a pytorch based furniture style image classifer. 

- A resnet CNN model is built by training with images of Mid-century modern, Rustic, Arts and Crafts, Traditional styles of furniture. (see [Notebooks](https://github.com/plasmon360/Furniture-Style-Classifier/tree/master/Notebooks) section for training)
- [pytorch_utils](https://github.com/plasmon360/Furniture-Style-Classifier/tree/master/pytorch_utils) is part of this project and is a seperate module that is used during training and can be used with other pytorch training projects. It consists of utils for callbacks, data processing and model building.
- A [webapp](https://github.com/plasmon360/Furniture-Style-Classifier/tree/master/Webapp/flask_classifier) based on Flask is developed. User can upload an image file or an URL. The webapp predicts the probabilities of each class. It allows user to update the class label if the prediction is wrong. Every image upload, prediction and user input for correct label are recorded into a database.
- Data for training was obtained from Google Images.

### Webapp Screenshots: 

Home Page
![alt text]( "Home Page on Mobile")

Prediction/Feedback Page
![alt text]( "Precition/Feedback Page on Mobile")
 

