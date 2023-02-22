from PIL import Image, ImageDraw, ImageFont
import base64
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI
from io import BytesIO
import math
from mangum import Mangum

# python -m uvicorn working:app --reload


class Rq(BaseModel):

    quality: float
    blackwhite: bool
    imageheight: Optional[float]
    imagewidth: Optional[float]
    base64: str


def base64_to_image(base64_string):
    # Remove the data:image/png;base64, header if present
    if ',' in base64_string:
        base64_string = base64_string.split(',', 1)[1]

    # Decode the base64-encoded image data
    image_data = base64.b64decode(base64_string)

    # Load the image data into a PIL Image object
    image = Image.open(BytesIO(image_data))

    return image


def getChar(inputInt):
    chars = 'Ñ@#W$9876543210?!abc;:+=-,._ '[::-1]
    charArray = list(chars)
    charLength = len(charArray)
    interval = charLength/256
    return charArray[math.floor(inputInt*interval)]


def prepare(base64_string, quality, blackwhite):

    print("quality", quality)
    print("blackwhite", blackwhite)

    image = base64_to_image(base64_string)

    return makeascii(image, quality, blackwhite)


def makeascii(im, scaleFactor=0.3, blackwhite=False):

    oneCharWidth = 10
    oneCharHeight = 18

    fnt = ImageFont.truetype('\\lucon.ttf', 15)

    width, height = im.size
    print("Scale factor is:", scaleFactor)
    print(width)
    print(height)
    im = im.resize((int(scaleFactor*width), int(scaleFactor *
                   height*(oneCharWidth/oneCharHeight))), Image.NEAREST)
    width, height = im.size
    pix = im.load()

    outputImage = Image.new(
        'RGB', (oneCharWidth * width, oneCharHeight * height), color=(0, 0, 0))

    d = ImageDraw.Draw(outputImage)

    # text_file = open("Output.txt", "w")

    for i in range(height):
        for j in range(width):
            try:
                r, g, b, a = pix[j, i]
            except:
                r, g, b = pix[j, i]
            h = int(r/3 + g/3 + b/3)

            try:
                pix[j, i] = (h, h, h, 255)
            except:
                pix[j, i] = (h, h, h)
            # text_file.write(getChar(h))
            d.text((j*oneCharWidth, i*oneCharHeight),
                   getChar(h), font=fnt, fill=((r, g, b) if blackwhite == False else (h, h, h)))

        # text_file.write('\n')

    # outputImage.save('output.png')

    im_file = BytesIO()

    outputImage.save(im_file, format='PNG')

    im_bytes = im_file.getvalue()

    im_b64 = base64.b64encode(im_bytes)

    base64result = str(im_b64)[2:-1]

    return base64result
# base64topixels("heyyyypoo")


app = FastAPI()
handler = Mangum(app)


@app.get("/")
def home():
    return {"Data": "Test"}


@app.post("/get-ascii")
def get_pixels(rq: Rq):
    return prepare(rq.base64, rq.quality, rq.blackwhite)
