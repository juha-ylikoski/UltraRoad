import base64
import json
from typing import Annotated
from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    Response,
    UploadFile,
    Header,
)
from PIL import Image
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import io
from sqlalchemy.orm import Session
import sqlalchemy
from openai import AsyncOpenAI

from .annotate import slipsum
from . import db, models
from .db import get_db
from . import schemas
from .chatgpt import get_openai


app = FastAPI(lifespan=db.lifespan)


@app.get("/")
async def index():
    return "foo"


@app.get("/kinds")
async def kinds(db: Session = Depends(get_db)) -> list[schemas.Kind]:
    return models.get_kinds(db)


@app.post("/kind")
async def new_kind(kind: schemas.Kind, db: Session = Depends(get_db)) -> int:
    return models.create_kind(db, kind)


@app.delete("/kind/{name}")
async def delete_kind(name: str, db: Session = Depends(get_db)) -> int:
    return models.delete_kind(db, name)


@app.post("/post")
async def upload_image(
    x_latitude: Annotated[float, Header()],
    x_longitude: Annotated[float, Header()],
    x_text: Annotated[str, Header()],
    x_kind: Annotated[str, Header()],
    x_title: Annotated[str, Header()],
    x_address: Annotated[str, Header()],
    file: UploadFile = File(content_type="image/jpeg"),
    db: Session = Depends(get_db),
    openai_client: AsyncOpenAI = Depends(get_openai),
) -> int:
    image = await file.read()
    if x_kind not in [x.name for x in models.get_kinds(db)]:
        raise HTTPException(status_code=400, detail="Kind not allowed!")
    resp = await openai_client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"Does a class {x_kind} describe the following image?",
                    },
                    {
                        "type": "text",
                        "text": 'Answer with only "yes" or "no".',
                    },
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64.b64encode(image).decode()}"
                        },
                    }
                ],
            },
        ],
    )
    if resp != "yes":
        raise HTTPException(status_code=400, detail="Image does not represent kind.")

    return models.create_post(
        db, x_latitude, x_longitude, x_text, image, x_kind, x_title, x_address
    )


@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)) -> list[schemas.BasePost]:

    return models.get_posts(db)


@app.get(
    "/posts/{id}/img",
    responses={200: {"content": {"image/jpeg": {}}}},
    # Prevent FastAPI from adding "application/json" as an additional
    # response media type in the autogenerated OpenAPI specification.
    # https://github.com/tiangolo/fastapi/issues/3258
    response_class=Response,
)
async def get_img(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    img = models.get_post_img(db, id)
    return Response(content=img, media_type="image/jpeg")


@app.post("/posts/{id}/upvote")
async def upvote(
    id: str,
    db: Session = Depends(get_db),
):
    models.upvote(db, id)


class AnnotatedModel(BaseModel):
    text: str
    kind: str
    title: str


@app.post("/annotate")
async def annotate_image(
    file: UploadFile = File(content_type="image/jpeg"),
    db: Session = Depends(get_db),
    openai_client: AsyncOpenAI = Depends(get_openai),
) -> AnnotatedModel:
    contents = await file.read()
    # make sure it is image
    Image.open(io.BytesIO(contents))
    kinds = [x.name for x in models.get_kinds(db)]

    json_format = """{
    "text": <Annotate the following image and find anything which is broken or malfunctioning in it>,
    "title": <Title for the text field. The length of this field should be maximum of 7 words but prefer shorter>,
    "kind": <Can the following image be classified in the following classes {kinds}? Only answer with one of the kinds and nothing else>
    }""".replace(
        "{kinds}", str(kinds)
    )
    pred_json_raw = await openai_client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"Respond with a json with following format: {json_format}",
                    },
                    {
                        "type": "text",
                        "text": "Respond in finnish",
                    },
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64.b64encode(contents).decode()}"
                        },
                    }
                ],
            },
        ],
    )
    try:
        pred_json = (
            pred_json_raw.choices[0]
            .message.content.replace("```json\n", "")
            .replace("```", "")
        )

        return AnnotatedModel.model_validate_json(pred_json)
    except Exception:
        return AnnotatedModel(text="", kind=models.get_kinds(db)[0], title="")


@app.exception_handler(sqlalchemy.exc.IntegrityError)
def unique_violation(request: Request, exc: sqlalchemy.exc.IntegrityError):
    return JSONResponse(status_code=400, content={"message": "Already exists!"})


@app.exception_handler(sqlalchemy.exc.NoResultFound)
def not_found(request: Request, exc: sqlalchemy.exc.NoResultFound):
    return JSONResponse(status_code=404, content={"message": "Not found!"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
