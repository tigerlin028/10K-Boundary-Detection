from sec_edgar_downloader import Downloader
import os

# === Set absolute save path ===
SAVE_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K"
os.makedirs(SAVE_DIR, exist_ok=True)
os.chdir(SAVE_DIR)

# === Initialize downloader (email is required by SEC) ===
dl = Downloader(
    company_name="WRDS_Project",
    email_address="tigerlin@seas.upenn.edu"
)

# === Dow Jones 30 company tickers ===
DOW30_TICKERS = [
    "AAPL", "MSFT", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS",
    "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD",
    "MMM", "MRK", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT"
]

# === Download date range ===
START_DATE = "2019-01-01"
END_DATE = "2021-12-31"

# === Batch download loop ===
for ticker in DOW30_TICKERS:
    try:
        print(f"⬇️  Downloading 10-K for {ticker} ...")
        dl.get("10-K", ticker, after=START_DATE, before=END_DATE)
    except Exception as e:
        print(f"⚠️  Failed for {ticker}: {e}")

print("✅ All downloads complete!")
print(f"📂 Files saved to: {os.path.abspath(SAVE_DIR)}")
