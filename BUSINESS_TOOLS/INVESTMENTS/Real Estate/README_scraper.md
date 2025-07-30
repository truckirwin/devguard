# Real Estate Deal Finder Application
## Grant Cardone Investment Criteria

A comprehensive application that scrapes real estate websites, filters properties based on Grant Cardone's investment criteria, and presents qualifying deals through both command-line and web interfaces.

---

## 🚀 Features

### **Core Functionality**
- **Multi-Source Scraping**: LoopNet, Crexi, Zillow Commercial, Redfin Commercial
- **Grant Cardone Criteria Filtering**: Cap rate, cash-on-cash return, price per unit, value-add potential
- **Automated Deal Scoring**: 0-100 point system based on Cardone's methodology
- **Financial Analysis**: Mortgage calculations, cash flow projections, ROI analysis
- **Export Capabilities**: CSV export with detailed property data

### **Web Interface**
- **Modern UI**: Responsive Bootstrap design with real-time search
- **Interactive Filters**: Customizable search criteria
- **Real-time Results**: Live property analysis and scoring
- **Export Functionality**: One-click CSV download

### **Command Line Interface**
- **Batch Processing**: Process multiple properties efficiently
- **Detailed Reports**: Comprehensive analysis reports
- **Flexible Output**: Multiple export formats

---

## 📋 Prerequisites

### **System Requirements**
- macOS (with Homebrew)
- Python 3.8+
- Chrome/Chromium browser (for Selenium)
- 4GB+ RAM
- Stable internet connection

### **Python Dependencies**
Install all required packages:
```bash
pip3 install -r requirements_scraper.txt
```

### **Chrome WebDriver**
The application uses Selenium for web scraping. ChromeDriver is automatically managed, but you can install it manually:
```bash
# On macOS (recommended)
brew install chromedriver

# Alternative macOS installation
pip3 install webdriver-manager

# On Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# On Windows
# Download from https://chromedriver.chromium.org/
```

---

## 🛠️ Installation

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd real-estate-deal-finder

# Ensure you have Homebrew installed (if not already)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### **2. Install Dependencies**
```bash
pip3 install -r requirements_scraper.txt
```

### **3. Create Environment File**
```bash
cp .env.example .env
# Edit .env with your configuration
```

### **4. Test Installation**
```bash
python3 real_estate_scraper.py
```

---

## 🚀 Usage

### **Web Interface (Recommended)**

1. **Start the Web Server**
```bash
python3 web_interface.py
```

2. **Open Browser**
Navigate to `http://localhost:8080`

3. **Configure Search Criteria**
- Location: Target market (e.g., "Boise, ID")
- Min/Max Units: Property size range
- Min Cap Rate: Minimum capitalization rate
- Min Cash-on-Cash: Minimum cash-on-cash return
- Price Range: Property price limits

4. **Search and Analyze**
- Click "Search Deals" to find qualifying properties
- Review results with Cardone scores and recommendations
- Export to CSV for further analysis

### **Command Line Interface**

1. **Basic Search**
```bash
python3 real_estate_scraper.py
```

2. **Custom Location**
```python
from real_estate_scraper import DealAnalyzer
import asyncio

async def main():
    analyzer = DealAnalyzer()
    deals = await analyzer.find_qualifying_deals("Austin, TX")
    print(f"Found {len(deals)} qualifying deals")

asyncio.run(main())
```

3. **Custom Criteria**
```python
analyzer = DealAnalyzer()
analyzer.filter.criteria.update({
    'min_cap_rate': 0.07,  # 7% minimum
    'min_cash_on_cash': 0.10,  # 10% minimum
    'min_units': 8,
    'max_units': 30
})
```

---

## 📊 Grant Cardone Criteria

### **Scoring System (0-100 points)**

1. **Cap Rate (30 points)**
   - 8%+: 30 points
   - 7.5%+: 25 points
   - 7%+: 20 points
   - 6.5%+: 15 points

2. **Cash-on-Cash Return (25 points)**
   - 12%+: 25 points
   - 10%+: 20 points
   - 8%+: 15 points
   - 6%+: 10 points

3. **Price per Unit (20 points)**
   - $50K or less: 20 points
   - $75K or less: 15 points
   - $100K or less: 10 points
   - $150K or less: 5 points

4. **Value-Add Potential (15 points)**
   - 30+ years old: 15 points
   - 20+ years old: 12 points
   - 10+ years old: 10 points
   - 5+ years old: 8 points

5. **Market Growth (10 points)**
   - Boise: 10 points (2.3% annual growth)

### **Recommendations**
- **80+ points**: STRONG BUY
- **70-79 points**: BUY
- **60-69 points**: CONSIDER
- **<60 points**: PASS

---

## 🔧 Configuration

### **Environment Variables (.env)**
```env
# Web scraping settings
HEADLESS_MODE=true
REQUEST_DELAY=2
MAX_PAGES=5

# Financial settings
DEFAULT_DOWN_PAYMENT_PCT=0.25
DEFAULT_INTEREST_RATE=6.5
DEFAULT_LOAN_TERM=25

# Filter criteria
MIN_CAP_RATE=0.065
MIN_CASH_ON_CASH=0.08
MAX_PRICE_PER_UNIT=150000
MIN_UNITS=5
MAX_UNITS=50
MIN_CARDONE_SCORE=60

# Web interface
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
FLASK_DEBUG=false
```

### **Custom Filter Criteria**
```python
# Modify filter criteria
analyzer.filter.criteria.update({
    'min_cap_rate': 0.07,  # 7% minimum
    'min_cash_on_cash': 0.10,  # 10% minimum
    'max_price_per_unit': 100000,  # $100K max per unit
    'min_units': 8,
    'max_units': 30,
    'min_cardone_score': 70  # Only show BUY or STRONG BUY
})
```

---

## 📈 Output Formats

### **CSV Export**
The application exports detailed property data including:
- Property address and details
- Financial metrics (cap rate, cash-on-cash, etc.)
- Cardone score and recommendation
- Value-add potential analysis
- Contact information and URLs

### **Report Generation**
```python
# Generate detailed report
report = analyzer.generate_report(qualifying_deals)
with open("deal_analysis_report.txt", "w") as f:
    f.write(report)
```

### **JSON API Response**
```json
{
  "success": true,
  "deals": [
    {
      "address": "1234 N Main St, Boise, ID",
      "price": 720000,
      "units": 12,
      "cap_rate": 0.075,
      "cash_on_cash_return": 0.12,
      "cardone_score": 85,
      "recommendation": "STRONG BUY"
    }
  ],
  "total_count": 1
}
```

---

## ⚠️ Important Notes

### **Legal and Ethical Considerations**
1. **Respect Robots.txt**: Always check website terms of service
2. **Rate Limiting**: Implement delays between requests
3. **Authentication**: Some sites require login credentials
4. **Data Usage**: Use data responsibly and ethically

### **Technical Limitations**
1. **Anti-Bot Measures**: Some sites have sophisticated protection
2. **Dynamic Content**: JavaScript-heavy sites may require Selenium
3. **API Changes**: Website structures change frequently
4. **Data Accuracy**: Always verify scraped data independently

### **Best Practices**
1. **Verify Data**: Cross-reference with multiple sources
2. **Due Diligence**: Never rely solely on scraped data
3. **Professional Advice**: Consult with real estate professionals
4. **Market Research**: Understand local market conditions

---

## 🐛 Troubleshooting

### **Common Issues**

1. **ChromeDriver Errors**
```bash
# Install webdriver-manager
pip3 install webdriver-manager

# Update ChromeDriver
webdriver-manager update
```

2. **Selenium Timeout Errors**
```python
# Increase timeout
WebDriverWait(driver, 20).until(...)
```

3. **Memory Issues**
```python
# Reduce max_pages parameter
deals = await scraper.scrape_loopnet(max_pages=3)
```

4. **Network Errors**
```python
# Add retry logic
import time
for attempt in range(3):
    try:
        # scraping code
        break
    except Exception as e:
        time.sleep(2 ** attempt)
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 real_estate_scraper.py
```

---

## 🔄 Updates and Maintenance

### **Regular Updates**
1. **Dependencies**: Update packages monthly
2. **Selectors**: Monitor website changes
3. **Criteria**: Adjust based on market conditions
4. **Features**: Add new data sources as needed

### **Monitoring**
- Check for website structure changes
- Monitor scraping success rates
- Update user agents and headers
- Review and update filter criteria

---

## 📞 Support

### **Getting Help**
1. **Documentation**: Review this README thoroughly
2. **Issues**: Check existing GitHub issues
3. **Community**: Join real estate investment forums
4. **Professional**: Consult with real estate professionals

### **Contributing**
1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Submit a pull request**

---

## 📄 License

This project is for educational purposes. Please ensure compliance with:
- Website terms of service
- Local laws and regulations
- Ethical data usage guidelines

---

## 🎯 Success Metrics

### **Application Performance**
- **Scraping Success Rate**: >90%
- **Data Accuracy**: >95%
- **Processing Speed**: <30 seconds per search
- **Uptime**: >99%

### **Investment Criteria**
- **Cap Rate**: 6.5%+ minimum
- **Cash-on-Cash**: 8%+ minimum
- **Price per Unit**: $50K-$150K target
- **Cardone Score**: 60+ for consideration

**Remember**: This tool is for research and analysis. Always conduct thorough due diligence before making investment decisions. 