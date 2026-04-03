from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from products.routes import router as products_router

app = FastAPI(title="E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)

@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}