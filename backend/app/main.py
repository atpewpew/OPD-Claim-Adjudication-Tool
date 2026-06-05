import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claimiq")

# Try to import DB functions, since they will be created later
try:
    from app.database.connection import init_db, AsyncSessionLocal
except ImportError:
    init_db = None
    AsyncSessionLocal = None
    logger.warning("Could not import init_db from app.database.connection. This is expected if the file does not exist yet.")

try:
    from app.database.seed import seed_members
except ImportError:
    seed_members = None
    logger.warning("Could not import seed_members from app.database.seed. This is expected if the file does not exist yet.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up...")
    
    if init_db is not None:
        try:
            if asyncio.iscoroutinefunction(init_db):
                await init_db()
            else:
                init_db()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error during init_db: {e}", exc_info=True)
    else:
        logger.warning("Skipping database initialization as init_db is not available.")
        
    if seed_members is not None and AsyncSessionLocal is not None:
        try:
            async with AsyncSessionLocal() as session:
                await seed_members(session)
            logger.info("Members seeded successfully.")
        except Exception as e:
            logger.error(f"Error during seed_members: {e}", exc_info=True)
    else:
        logger.warning("Skipping member seeding as seed_members is not available.")
        
    yield
    
    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title="ClaimIQ API",
    version="1.0.0",
    description="Intelligent OPD Insurance Claim Adjudication",
    lifespan=lifespan
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with try/except ImportError so application works even if routes files don't exist yet
try:
    from app.routes.claims import router as claims_router
    app.include_router(claims_router, prefix="/api/claims", tags=["claims"])
    logger.info("Claims router included successfully.")
except ImportError:
    logger.warning("Could not import claims router from app.routes.claims. Skipping registration.")

try:
    from app.routes.misc import router as misc_router
    app.include_router(misc_router, prefix="/api", tags=["misc"])
    logger.info("Misc router included successfully.")
except ImportError:
    logger.warning("Could not import misc router from app.routes.misc. Skipping registration.")
