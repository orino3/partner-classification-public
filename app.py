from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
from utils.url_validation import validate_url
from utils.crawl4ai_integration import scrape_content
from utils.llm_integration import evaluate_partner
from pathlib import Path
import atexit
import signal
import traceback
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug print
logger.info(f"OpenAI API Key: {os.getenv('OPENAI_API_KEY')}")

# Create the FastAPI app
app = FastAPI(
    title="Partner Evaluator",
    description="Evaluates potential business partners based on their website content",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

# Configure static files with name and directory
static_files_app = StaticFiles(directory=str(BASE_DIR / "static"))
app.mount("/static", static_files_app, name="static")

# Initialize templates with absolute path
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def cleanup():
    """Cleanup function to run when server shuts down"""
    logger.info("Cleaning up server resources...")

# Register cleanup handlers
atexit.register(cleanup)
signal.signal(signal.SIGINT, lambda s, f: cleanup())

@app.on_event("startup")
async def startup_event():
    """Run when the server starts"""
    logger.info("Server starting up...")
    logger.info(f"Static files directory: {str(BASE_DIR / 'static')}")
    logger.info(f"Templates directory: {str(BASE_DIR / 'templates')}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run when the server shuts down"""
    logger.info("Server shutting down...")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the index page"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Template error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/predict")
async def predict(request: Request):
    """Evaluate a website for partnership potential"""
    try:
        # Get request data with timeout
        try:
            data = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse request JSON: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request format"}
            )

        url = data.get("url")
        logger.info(f"Received prediction request for URL: {url}")
        
        if not url:
            logger.warning("No URL provided in request")
            return JSONResponse(
                status_code=400,
                content={"error": "URL is required"}
            )
        
        if not validate_url(url):
            logger.warning(f"Invalid URL format: {url}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid URL format"}
            )
        
        try:
            # Scrape content using Crawl4AI with timeout
            logger.info(f"Starting content scraping for: {url}")
            content = await scrape_content(url)
            if not content:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to retrieve content from website"}
                )
            logger.info(f"Successfully scraped content, length: {len(content)}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout while scraping {url}")
            return JSONResponse(
                status_code=504,
                content={"error": "Timeout while scraping website"}
            )
        except Exception as e:
            logger.error(f"Scraping error for {url}: {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to scrape website: {str(e)}"}
            )
        
        try:
            # Evaluate using LLM with timeout
            logger.info("Starting LLM evaluation")
            result = await evaluate_partner(content)
            if not result:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to generate evaluation"}
                )
            logger.info("Successfully completed LLM evaluation")
            logger.debug(f"Evaluation result: {result}")
            return JSONResponse(content=result)
        except asyncio.TimeoutError:
            logger.error("Timeout during LLM evaluation")
            return JSONResponse(
                status_code=504,
                content={"error": "Timeout during content evaluation"}
            )
        except Exception as e:
            logger.error(f"LLM evaluation error: {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to evaluate content: {str(e)}"}
            )
    
    except Exception as e:
        logger.error(f"General error in predict endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    logger.info("Starting server on http://localhost:3000")
    uvicorn.run("app:app", host="127.0.0.1", port=3000, reload=True) 