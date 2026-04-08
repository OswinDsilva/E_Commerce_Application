from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .errors import ApiError
from .routers import auth, bank_accounts, orders, payments, products, users

app = FastAPI(title="The Atelier API")
UPLOADS_DIR = Path(__file__).resolve().parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(products.category_router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(bank_accounts.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

@app.exception_handler(ApiError)
async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "code": exc.code},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "Request failed", "code": "REQUEST_FAILED"},
        )

    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong. Please try again.", "code": "SERVER_ERROR"},
    )

@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}


