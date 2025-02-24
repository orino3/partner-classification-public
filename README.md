# Partner Classification for accessiBe

This application evaluates potential business partners for accessiBe by analyzing their websites and determining their partnership potential based on multiple factors.

## Features

- **Website Analysis**: Scrapes and analyzes website content using Crawl4AI
- **AI-Powered Evaluation**: Uses GPT-4 to evaluate partnership potential
- **Comprehensive Business Analysis**:
  - Core Scoring Metrics
  - Business Profile Assessment
  - Technical Capabilities Evaluation
  - Market Position Analysis
  - Client Relationship Assessment
  - Business Model Evaluation
  - Compliance & Growth Indicators

## Evaluation Parameters

### Core Scores
- **Partnership Potential**: Overall compatibility score (0-100%)
- **Reach Score**: Measures potential client reach (0-100%)
- **Relevance Score**: Evaluates business model alignment (0-100%)

### Business Profile
- Industry/Vertical
- Company Size
- Geographic Reach
- Years in Business
- Client Portfolio Size

### Technical Assessment
- Technology Stack
- Current Accessibility Solutions
- Integration Capabilities
- Development Services
- Hosting/Platform Services

### Market Position
- Market Segments Served
- Competitor Relationships
- Industry Certifications
- Professional Memberships
- Awards/Recognition

### Client Relationships
- Client Types
- Average Client Size
- Client Retention
- Service Model
- Success Stories

### Business Model
- Revenue Streams
- Pricing Model
- Sales Approach
- Service Delivery Method
- Contract Types

### Compliance & Growth
- Regulatory Focus
- Compliance Services
- Growth Indicators
- Digital Presence
- Future Plans

## Setup

1. Clone the repository:
```bash
git clone https://github.com/orino3/partners-classification.git
cd partners-classification
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_key_here
```

4. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:8000`

## How It Works

1. **Input**: Enter a website URL to analyze
2. **Analysis**: The system will:
   - Scrape the website content
   - Analyze the content using GPT-4
   - Generate comprehensive partnership evaluation
3. **Output**: Receive detailed scoring and analysis including:
   - Partnership potential score
   - Reach and relevance metrics
   - Suggested sales approach
   - Key partnership indicators

## Scoring System

- **Partnership Potential (0-100%)**: Overall score combining reach, relevance, and other factors
- **Reach Score (0-100%)**: Measures potential impact through client network
- **Relevance Score (0-100%)**: Evaluates alignment with accessibility needs

High scores (80-100%) indicate ideal partnership candidates who:
- Have significant reach to website owners
- Understand accessibility importance
- Don't compete directly with accessiBe
- Could benefit from offering accessiBe to their clients

## Technologies Used

- FastAPI
- OpenAI GPT-4
- Crawl4AI
- TailwindCSS
- Python 3.11+

## License

MIT License 