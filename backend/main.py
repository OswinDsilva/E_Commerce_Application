from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from products.routes import router as products_router
from products.routes import cat_router

app = FastAPI(title="E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(cat_router)

@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}