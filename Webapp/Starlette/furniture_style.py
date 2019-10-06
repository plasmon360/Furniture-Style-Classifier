from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.routing import Router, Mount
from starlette.staticfiles import StaticFiles


from fastai.vision import (
    ImageDataBunch,
    create_cnn,
    open_image,
    get_transforms,
    models,
)
import torch
from pathlib import Path
from io import BytesIO
import sys
import uvicorn
import aiohttp
import asyncio
import numpy as np

async def get_bytes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()





app = Starlette()

app.debug = True
app.mount('/static', StaticFiles(directory="static"))


path = Path(__file__).parents[0]/ "tmp"
classes = ['arts_and_crafts', 'mid-century-modern', 'rustic', 'traditional', 'transitional']
imagenet_stats = ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
data2 = ImageDataBunch.single_from_classes(path, classes, tfms=get_transforms(), size=224).normalize(imagenet_stats)
learner = create_cnn(data2, models.resnet34)
learner.load('stage-2')

#cat_learner = create_cnn(cat_data, models.resnet34)
#cat_learner.model.load_state_dict(
#    torch.load("usa-inaturalist-cats.pth", map_location="cpu")
#)

@app.route("/random-image-predict", methods=["GET"])
async def random_image_predict(request):
    print('hello from random image predict')
    bytes = await (data["file"].read())
    return predict_image_from_bytes(bytes)


@app.route("/upload", methods=["POST"])
async def upload(request):
    data = await request.form()
    bytes = await (data["file"].read())
    return predict_image_from_bytes(bytes)


@app.route("/classify-url", methods=["GET"])
async def classify_url(request):
    bytes = await get_bytes(request.query_params["url"])
    return predict_image_from_bytes(bytes)

def stablesoftmax(x): 
    """Compute the softmax of vector x in a numerically stable way.""" 
    """https://eli.thegreenplace.net/2016/the-softmax-function-and-its-derivative/"""
    shiftx = x - np.max(x) 
    exps = np.exp(shiftx) 
    return exps / np.sum(exps) 

def predict_image_from_bytes(bytes):
    img = open_image(BytesIO(bytes))
    pred_class,pred_idx,outputs= learner.predict(img)    
    probabilities = stablesoftmax(outputs.numpy())
    return JSONResponse({"prediction":pred_class, 
			"outputs": dict(sorted(zip(classes,probabilities.tolist()), reverse = True, key = lambda x: x[1]))
			})
	

@app.route("/")
def form(request):
    return HTMLResponse('''
			<head>
			   <title>Furniture Style Classfier</title>
			 <link rel="stylesheet" href="/static/styles.css">
			   <script>
			      function myFunction(input) {
				  document.getElementById("image").height = "200";
				  document.getElementById("image").width = "200";
				  document.getElementById('image').src = window.URL.createObjectURL(input.files[0]);
			      }

			   </script>
			</head>
			<body>
			   <div class = 'page'>
			      <h1>Classify style of furniture</h1>
			      <div class = 'upload'>
				 <form action="/upload" method="post" enctype="multipart/form-data">
				    Select an image to upload:
				    <input type="file" name="file"  accept="image/*"  onchange="myFunction(this)">
				    <div class = 'myimage'> <img id="image" width="00" height="00" /> </div>
				    <input type="submit" value="Predict">
				 </form>
			      </div>
			      <div class = 'url_submit'>
				 <form action="/classify-url" method="get">
				    or submit a URL:
				    <input type="url" name="url" onchange="myFunction2(this)">
				    <input type="submit" value="Fetch and analyze">
				 </form>
			      </div>
			   </div>
			</body>
			</html>

			''')



@app.route("/form")
def redirect_to_homepage(request):
    return RedirectResponse("/")


if __name__ == "__main__":
    if "serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8008)
