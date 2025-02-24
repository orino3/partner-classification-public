import os
from openai import AsyncOpenAI
import json
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = AsyncOpenAI(api_key=api_key)

def clean_json_string(s: str) -> str:
    """Clean and validate JSON string from GPT response."""
    # Find the first { and last } to extract just the JSON object
    start = s.find('{')
    end = s.rfind('}') + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in response")
    
    json_str = s[start:end]
    # Remove any markdown code block syntax
    json_str = re.sub(r'```json\s*|\s*```', '', json_str)
    # Replace any escaped newlines
    json_str = json_str.replace('\\n', ' ')
    return json_str

async def evaluate_partner(content: str) -> dict:
    """
    Evaluate if the website content indicates a potential partner.
    Returns a comprehensive analysis dictionary.
    """
    prompt = f"""Analyze this website to determine if it represents a potential partner/affiliate for accessiBe's web accessibility solutions. 
Provide a comprehensive analysis covering all aspects below.

Content to analyze:
{content[:4000]}

Analyze and provide detailed information for each category:

1. CORE EVALUATION
- Partnership potential (0-100%)
- Reach score (0-100%)
- Relevance score (0-100%)

2. BUSINESS PROFILE
- Industry/Vertical
- Company Size (estimate)
- Geographic Reach
- Years in Business (if found)
- Client Portfolio Size (estimate)

3. TECHNICAL ASSESSMENT
- Technology Stack
- Current Accessibility Solutions
- Integration Capabilities (rate 1-5)
- Development Services
- Hosting/Platform Services

4. MARKET POSITION
- Market Segments Served
- Competitor Relationships
- Industry Certifications
- Professional Memberships
- Awards/Recognition

5. CLIENT RELATIONSHIPS
- Client Types
- Average Client Size
- Client Retention Indicators
- Service Model
- Success Stories Count

6. BUSINESS MODEL
- Revenue Streams
- Pricing Model Type
- Sales Approach
- Service Delivery Method
- Contract Types

7. COMPLIANCE & GROWTH
- Regulatory Focus Areas
- Compliance Services
- Growth Indicators
- Digital Presence Score (1-5)
- Future Plans/Initiatives

8. PARTNERSHIP EVALUATION
- Key Strengths
- Potential Challenges
- Integration Opportunities
- Risk Factors
- Recommended Approach

Respond with a JSON object containing these fields and structure:
{{
    "probability": 85,
    "reachScore": 75,
    "relevanceScore": 90,
    "reasoning": "Comprehensive explanation of the evaluation",
    "category": "Primary partner category",
    "businessProfile": {{
        "industry": "Company's industry",
        "companySize": "Size description",
        "geographicReach": "Geographic coverage",
        "yearsInBusiness": "Years active",
        "clientPortfolioSize": "Portfolio size"
    }},
    "technicalAssessment": {{
        "techStack": ["Technology 1", "Technology 2"],
        "accessibilitySolutions": "Current solutions description",
        "integrationScore": 4,
        "developmentServices": ["Service 1", "Service 2"],
        "hostingServices": "Hosting capabilities"
    }},
    "marketPosition": {{
        "segments": ["Segment 1", "Segment 2"],
        "competitors": ["Competitor relationship 1", "Competitor relationship 2"],
        "certifications": ["Certification 1", "Certification 2"],
        "memberships": ["Membership 1", "Membership 2"],
        "awards": ["Award 1", "Award 2"]
    }},
    "clientRelationships": {{
        "clientTypes": ["Type 1", "Type 2"],
        "averageClientSize": "Average size description",
        "retentionRate": "Retention information",
        "serviceModel": "Service model description",
        "successStories": 5
    }},
    "businessModel": {{
        "revenueStreams": ["Stream 1", "Stream 2"],
        "pricingModel": "Pricing structure",
        "salesApproach": "Sales methodology",
        "serviceDelivery": "Delivery method",
        "contractTypes": ["Contract type 1", "Contract type 2"]
    }},
    "complianceGrowth": {{
        "regulatoryFocus": ["Focus 1", "Focus 2"],
        "complianceServices": ["Service 1", "Service 2"],
        "growthIndicators": ["Indicator 1", "Indicator 2"],
        "digitalPresenceScore": 4,
        "futurePlans": ["Plan 1", "Plan 2"]
    }},
    "partnershipEvaluation": {{
        "strengths": ["Strength 1", "Strength 2"],
        "challenges": ["Challenge 1", "Challenge 2"],
        "opportunities": ["Opportunity 1", "Opportunity 2"],
        "risks": ["Risk 1", "Risk 2"],
        "recommendedApproach": "Detailed partnership approach"
    }},
    "indicators": ["Key indicator 1", "Key indicator 2"],
    "salesPitch": "Customized sales pitch"
}}

Ensure all numeric scores are integers and arrays contain actual findings, not placeholder text.
"""
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are an expert at evaluating business partnership opportunities, specifically for SaaS and digital solutions. 
                Focus on finding partners who can reach many website owners or influence digital accessibility decisions.
                Consider both explicit statements and implicit indicators in the content.
                Be precise in categorizing and scoring potential partners.
                Ensure all numeric scores are integers.
                Format the response as a valid JSON object."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        # Get the response content and clean it
        response_text = response.choices[0].message.content
        cleaned_json = clean_json_string(response_text)
        
        try:
            # Parse the JSON response
            result = json.loads(cleaned_json)
            
            # Validate all required fields are present
            required_fields = [
                "probability", "reachScore", "relevanceScore", "reasoning", 
                "category", "businessProfile", "technicalAssessment", 
                "marketPosition", "clientRelationships", "businessModel",
                "complianceGrowth", "partnershipEvaluation", "indicators", 
                "salesPitch"
            ]
            
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                raise Exception(f"Missing required fields: {', '.join(missing_fields)}")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {str(e)}")
            print(f"Response text: {response_text}")
            print(f"Cleaned JSON: {cleaned_json}")
            raise Exception("Failed to parse GPT response as JSON")
        
    except Exception as e:
        raise Exception(f"Failed to evaluate content: {str(e)}") 