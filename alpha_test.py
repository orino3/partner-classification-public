import requests
import logging
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
BASE_URL = "https://www.alphavantage.co/query"

def test_income_statement(symbol: str = "AAPL"):
    """Test getting income statement data from Alpha Vantage"""
    try:
        # Make API request
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": symbol,
            "apikey": API_KEY
        }
        
        logger.info(f"Fetching income statement for {symbol}")
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        
        if "Error Message" in data:
            logger.error(f"API Error: {data['Error Message']}")
            return False, data["Error Message"]
            
        if "annualReports" not in data:
            logger.error("No annual reports found in response")
            return False, "No annual reports found"
            
        # Get latest annual report
        latest_report = data["annualReports"][0]
        
        result = {
            "symbol": symbol,
            "fiscal_year": latest_report["fiscalDateEnding"],
            "total_revenue": latest_report["totalRevenue"],
            "gross_profit": latest_report["grossProfit"],
            "net_income": latest_report["netIncome"]
        }
        
        logger.info(f"Successfully retrieved data: {result}")
        return True, result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return False, str(e)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False, str(e)

if __name__ == "__main__":
    # Test with Apple
    success, result = test_income_statement("AAPL")
    print(f"\nTest result for AAPL:")
    print(f"Success: {success}")
    print(f"Data: {result}")
    
    # Test with Microsoft
    success, result = test_income_statement("MSFT")
    print(f"\nTest result for MSFT:")
    print(f"Success: {success}")
    print(f"Data: {result}") 