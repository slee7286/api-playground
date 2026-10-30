from fastapi import FastAPI, Request, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from starlette.responses import HTTPException as StarletteHTTPException
from pydantic import BaseModel
from enum import Enum

class Item(BaseModel): # Pydantic model for request body
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

app = FastAPI()

users = {"foo": "The Foo Wrestlers"}

# @app.exception_handler(StarletteHTTPException)
# async def custom_http_exception_handler(request, exc):
#     print(f"OMG! An HTTP error!: {repr(exc)}")
#     return await http_exception_handler(request, exc)


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     print(f"OMG! The client sent invalid data!: {exc}")
#     return await request_validation_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )

@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = "Validation errors:"
    for error in exc.errors():
        message += f"\nField: {error['loc']}: Error: {error['msg']}"
    return PlainTextResponse(message, status_code=400)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/health")
async def read_health():
    return {"message": "Service is healthy"}

@app.get("/items/")
async def read_item(item: Item):
    return item

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.get("/items/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result

@app.get("users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found", headers={"X-Error": "There goes my error"},)
    if user_id == "3":
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.",)
    return {"user_id": user_id, "name": users[user_id]}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

@app.get("/files/{file_path:path}") # URL might have double slash like /files//home/user/file.txt
async def read_file(file_path: str):
    return {"file_path": file_path}

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: str, item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item