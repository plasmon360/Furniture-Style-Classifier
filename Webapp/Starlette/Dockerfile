FROM python:3.6-slim-stretch

RUN apt update
RUN apt install -y python3-dev gcc

# Install pytorch and fastai
RUN pip install torch_nightly -f https://download.pytorch.org/whl/nightly/cpu/torch_nightly.html
RUN pip install fastai

# Install starlette and uvicorn
RUN pip install starlette uvicorn python-multipart aiohttp aiofiles numpy

ADD furniture_style.py furniture_style.py
ADD tmp/models/stage-2.pth tmp/models/stage-2.pth
ADD static static
# Run it once to trigger resnet download
RUN python furniture_style.py

EXPOSE 8008

# Start the server
CMD ["python", "furniture_style.py", "serve"]
