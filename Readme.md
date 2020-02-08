## This is a pytorch based furniture style image classifer. 

- A resnet CNN image classifation model is trained with images of Mid-century modern, Rustic, Arts and Crafts, Traditional styles of furniture. (see [Notebooks](https://github.com/plasmon360/Furniture-Style-Classifier/tree/master/Notebooks) for training)
- [pytorch_utils](https://github.com/plasmon360/Furniture-Style-Classifier/tree/master/pytorch_utils) is a seperate python module that is used during training and can be used with other pytorch projects. It consists of utils for callbacks, data processing and model building.
- [Webapp](https://github.com/plasmon360/Furniture-Style-Classifier/tree/master/Webapp/classifier) is a Flask based webapp. User can upload an image file or an URL. The webapp predicts the probabilities of each class based on a checkpoint model. It allows user to update the class label if the prediction is wrong. Every image upload, predictions and user input for correct label are recorded into a database.
- Data for training was obtained from Google Images.

### Webapp Screenshots: 

Home Page                 |  Prediction/Feedback Page
:-------------------------:|:-------------------------:
![alt text](https://github.com/plasmon360/Furniture-Style-Classifier/blob/master/Webapp/classifier/docs/home_snapshot.png "Home Page on Mobile") | ![alt text](https://github.com/plasmon360/Furniture-Style-Classifier/blob/master/Webapp/classifier/docs/prediction_snapshot.png "Precition/Feedback Page on Mobile")

