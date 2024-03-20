from fastapi import FastAPI, File, UploadFile
from PIL import Image
from numpy import asarray
import io

#Only used for "/" Feel free to delete if no longer used
#/static and /templates can also be deleted
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Homepage displaying the image submission form.
    """
    return templates.TemplateResponse("index.html", {"request": request})
#END OF "/"

@app.post("/poggers/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    numpydata = asarray(image)
    print(numpydata.shape)
    with open(file.filename, "wb") as f:
        f.write(contents)
    return {"filename": file.filename}