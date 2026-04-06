from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse

from .errors import ApiError
from .routers import auth, bank_accounts, payments, users


app = FastAPI(title="The Atelier API")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(bank_accounts.router)
app.include_router(payments.router)


@app.exception_handler(ApiError)
async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "code": exc.code},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, FastAPIHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "Request failed", "code": "REQUEST_FAILED"},
        )

    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong. Please try again.", "code": "SERVER_ERROR"},
    )
