from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
import os
import uuid
from typing import Dict, Any
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from dotenv import load_dotenv

# Load environment variables from a .env file locally.
# On Vercel, this will safely do nothing if the file isn't present, 
# and use the Environment Variables injected by Vercel automatically.
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Real estate external API config (optional)
REAL_ESTATE_API_KEY = os.getenv("REAL_ESTATE_API_KEY", "")
REAL_ESTATE_API_URL = os.getenv("REAL_ESTATE_API_URL", "https://api.realestateapi.com/v1/market")


def get_real_estate_data(zip_code: str) -> Dict[str, Any] | None:
    """Try to fetch market data from RealEstateAPI.com (or configured URL).
    Returns a dict with the expected fields or None on failure.
    The function is defensive: any error returns None so the caller can fallback to mock data.
    """
    if not REAL_ESTATE_API_KEY:
        return None

    try:
        # Example: GET https://api.realestateapi.com/v1/market/90210?apikey=KEY
        url = f"{REAL_ESTATE_API_URL}/{zip_code}"
        headers = {"Accept": "application/json"}
        params = {"apikey": REAL_ESTATE_API_KEY}
        resp = requests.get(url, headers=headers, params=params, timeout=6)
        if resp.status_code != 200:
            print(f"RealEstateAPI returned {resp.status_code}: {resp.text}")
            return None
        payload = resp.json()

        # Map provider response to our expected shape. Adjust keys depending on real API.
        # We'll defensively pick fields with sensible fallbacks.
        return {
            "Median Price": payload.get("median_price") or payload.get("medianPrice") or payload.get("median") or "$0",
            "Days on Market": payload.get("days_on_market") or payload.get("daysOnMarket") or payload.get("dom") or 0,
            "Inventory Months": payload.get("inventory_months") or payload.get("inventoryMonths") or payload.get("inventory") or 0,
            "New Listings": payload.get("new_listings") or payload.get("newListings") or payload.get("new") or 0,
            "List-to-Sale Ratio": payload.get("list_to_sale_ratio") or payload.get("listToSaleRatio") or payload.get("lts_ratio") or "0%",
        }
    except Exception as e:
        print(f"Error calling RealEstateAPI for {zip_code}: {e}")
        return None


def get_market_data(zip_code: str) -> Dict[str, Any]:
    """Return market data: prefer RealEstateAPI when available, otherwise fall back to mock data."""
    # Try external provider first
    external = get_real_estate_data(zip_code)
    if external:
        return external
    # Fallback to existing mock mapping
    return get_mock_market_data(zip_code)

class ReportRequest(BaseModel):
    zip_code: str

# Mock Market Data Layer
def get_mock_market_data(zip_code: str) -> Dict[str, Any]:
    # In a real app, this would call a real estate API or DB
    if zip_code == "90210":
        return {
            "Median Price": "$3,500,000",
            "Days on Market": 45,
            "Inventory Months": 4.5,
            "New Listings": 18,
            "List-to-Sale Ratio": "98%"
        }
    return {
        "Median Price": "$450,000",
        "Days on Market": 21,
        "Inventory Months": 2.1,
        "New Listings": 8,
        "List-to-Sale Ratio": "101%"
    }

@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    if not request.zip_code:
        raise HTTPException(status_code=400, detail="ZIP code is required")
        
    data = get_market_data(request.zip_code)
    
    # Generate AI insights
    ai_text = "Market Summary:\nBuyer Insights:\nSeller Insights:\nRecommendations:\n(Configure GEMINI_API_KEY to see real AI insights)"
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"""
            Act as a friendly, expert neighborhood real estate agent having a personal, one-on-one conversation with a client over coffee.
            Here is the current market data for ZIP code {request.zip_code}:
            {data}
            
            Make the analysis highly engaging, conversational, and easy to read. Speak directly to the client ("you", "we"), using an enthusiastic, supportive, and accessible tone. 
            Translate the 'Days on Market', 'Inventory', and 'List-to-Sale Ratio' numbers into plain English—what does it ACTUALLY mean for them right now? Keep it punchy, warm, and avoid long walls of corporate text!

            Strictly use these exact 4 headings (no markdown formatting, use plain text with a clear blank line between sections):
            Market Summary: [Your conversational overview of how the neighborhood is doing right now. Keep it engaging!]
            Buyer Insights: [Friendly, direct advice for someone looking to buy—how fast do they need to act? Do they have negotiating room?]
            Seller Insights: [Encouraging but realistic advice for someone thinking of selling—what should they expect regarding pricing and timeline?]
            Recommendations: [Your personal, bottom-line advice on the best next steps to take in this specific ZIP code.]
            """
            response = model.generate_content(prompt)
            if response.text:
                ai_text = response.text
        except Exception as e:
            ai_text += f"\nError generating insights: {e}"
            
    return {
        "zip_code": request.zip_code,
        "market_data": data,
        "ai_insights": ai_text
    }

class DownloadRequest(BaseModel):
    zip_code: str
    market_data: dict
    ai_insights: str

@app.post("/download-report")
async def download_report(request: DownloadRequest):
    pdf_filename = f"report_{uuid.uuid4().hex}.pdf"
    
    # Generate PDF
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter
    
    # Branding
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "SnapReport by Snaphomz")
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 100, f"Market Report for ZIP: {request.zip_code}")
    
    # Data
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 130, "Market Data:")
    c.setFont("Helvetica", 12)
    y = height - 150
    for key, value in request.market_data.items():
        c.drawString(70, y, f"{key}: {value}")
        y -= 20
        
    # AI Insights
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "AI Insights:")
    y -= 20
    
    c.setFont("Helvetica", 10)
    lines = request.ai_insights.split('\n')
    for line in lines:
        if not line.strip():
            y -= 10
            continue
            
        wrapped_lines = simpleSplit(line, 'Helvetica', 10, width - 100)
        for wl in wrapped_lines:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
            c.drawString(50, y, wl)
            y -= 15

    c.save()
    
    return FileResponse(pdf_filename, media_type="application/pdf", filename=f"SnapReport_{request.zip_code}.pdf")
