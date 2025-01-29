# 📌 Compranet Scraper & AI-Powered Contract Analysis
Automate the extraction of government contract data and unlock powerful insights with AI

## 🏛️ What is Compranet?
Compranet is Mexico's official government procurement platform, where businesses can search, participate, and compete for public contracts.

This repository contains a Python-based web scraper to automate contract data extraction from Compranet using Selenium. Additionally, it provides a framework for AI-powered contract analysis using Large Language Models (LLMs).

-----

## 🚀 Features
✔️ Automates contract searches based on keywords (e.g., "cleaning", "security", "energy")
✔️ Extracts contract details into a structured CSV format
✔️ Downloads related documents and organizes them in folders
✔️ Uses AI (LLMs) to analyze contracts, summarize them, and highlight key insights

-----

## 📂 Installation & Setup
### 1️⃣ Clone this repository

```
git clone https://github.com/yourusername/compranet-scraper.git
cd compranet-scraper
```

### 2️⃣ Set up Selenium WebDriver
The script uses Google Chrome and requires Chromedriver. It will install automatically using:

```
from webdriver_manager.chrome import ChromeDriverManager

```
Ensure you have Chrome installed or modify the script to use a different browser.

----

## 🔍 Usage
Run the scraper by specifying a search term:

```
python3 compranet_scraper.py --search "limpieza"
```

You can modify the search_terms list inside compranet_scraper.py to include multiple keywords.

💡 Output:

- A structured CSV file with extracted contract details
- Downloaded contract documents organized by category

-----

## 📌 Future Enhancements
🔹 Expand AI capabilities for contract risk analysis
🔹 Improve automation for multi-keyword searches
🔹 Add NLP-based entity recognition for contract details

-----
## 🤝 Contributing
We welcome contributions! Feel free to open an issue or submit a pull request.

-----

## 📩 Need Help?
If you want to automate contract analysis or enhance procurement strategies with AI, reach out to Riemann Analytics. 🚀

https://www.riemannanalytics.com/

