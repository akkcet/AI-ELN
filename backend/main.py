from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading

from .database import Base, engine
from .routers import experiments, ai, audit, admin, admin_requests,chemistry
from .agents.admin_executor import execute_admin_requests

from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------
# ✅ Lifespan handler (modern FastAPI)
# ---------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------- STARTUP ----------
    executor_thread = threading.Thread(
        target=execute_admin_requests,
        daemon=True
    )
    executor_thread.start()
    print("✅ Admin request executor started")

    yield   # ---- app runs here ----

    # ---------- SHUTDOWN ----------
    print("🛑 Backend shutting down")


# ---------------------------------------------------
# ✅ FastAPI app
# ---------------------------------------------------
app = FastAPI(
    title="AI ELN Backend",
    lifespan=lifespan
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# ✅ Database init
# ---------------------------------------------------
Base.metadata.create_all(bind=engine)


# ---------------------------------------------------
# ✅ Routers
# ---------------------------------------------------
app.include_router(ai.router)
app.include_router(experiments.router)
app.include_router(audit.router)
app.include_router(admin.router)
app.include_router(admin_requests.router)
app.include_router(chemistry.router)

# ---------------------------------------------------
# ✅ Static files
# ---------------------------------------------------
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")


# ---------------------------------------------------
# ✅ Health / Debug
# ---------------------------------------------------
@app.get("/")
def root():
    return {"message": "Backend running"}


@app.get("/debug/routes")
def list_routes():
    return [route.path for route in app.routes]