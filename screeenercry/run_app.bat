@echo off
echo Starting Crypto Technical Analysis App...
echo.
echo Installing required packages...
pip install streamlit pandas numpy ta ccxt plotly requests yfinance
echo.
echo Starting the application...
echo The app will open in your browser at http://localhost:8501
echo.
python -m streamlit run app.py
pause
