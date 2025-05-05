# Natural Language to SQL using Gemini

This Streamlit-based app allows you to:

- Upload Excel files and convert them into a SQLite database.
- Ask questions in **natural language**, and automatically generate SQL queries using **Google Gemini**.
- View and modify your data interactively.
- Download the updated Excel file after data changes.

---

## 🚀 Features

-  Upload `.xlsx` files and convert them to SQLite
-  Use Gemini to generate SQL from plain English
-  Execute SQL queries and display results
-  Perform insert/update/delete operations via natural language
-  Download updated data as Excel

---

## 🛠️ Local Setup Instructions

```
# 1. Clone the repository
git clone https://github.com/karthikeya100804/Natural-Language-to-SQL-using-Gemini.git
cd Natural-Language-to-SQL-using-Gemini

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Create your .env file with your Gemini API key and copy paste the following
GEMINI_API_KEY=your_google_gemini_api_key_here

# 5. Create .env and paste your Gemini API key
# You can get it from https://aistudio.google.com/app/apikey

#6. Run code
streamlit run app.py
```
---
## 📁 Project Structure
```
Natural-Language-to-SQL-using-Gemini/
├── app.py                # Main Streamlit app
├── dataset.xlsx          # Sample Dataset
├── requirements.txt      # List of Python packages
├── README.md             
```
## 📦 Requirements
- Python 3.10 or higher
- A Google Gemini API Key


