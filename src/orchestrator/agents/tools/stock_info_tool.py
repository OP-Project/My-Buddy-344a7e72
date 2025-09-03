import yfinance as yf

def get_stock_analysis(ticker: str) -> dict:
    """
    Get current stock price and basic analysis for Indian stocks using yfinance.

    Parameters:
        ticker (str): Ticker symbol of the Indian stock (e.g., 'RELIANCE', 'TCS', 'INFY').

    Returns:
        dict: A dictionary with:
            - If success:
                {
                    "status": "success",
                    "report": "<human-readable stock summary>"
                }
            - If error:
                {
                    "status": "error",
                    "error_message": "<what went wrong>"
                }
    """
    try:
        # Handle NSE/BSE suffix
        if not ticker.endswith(('.NS', '.BO')):
            ticker_nse = f"{ticker}.NS"
            stock = yf.Ticker(ticker_nse)
            info = stock.info

            # If NSE doesn't work, try BSE
            if not info.get('currentPrice') and not info.get('regularMarketPrice'):
                ticker_bse = f"{ticker}.BO"
                stock = yf.Ticker(ticker_bse)
                info = stock.info
                ticker = ticker_bse
            else:
                ticker = ticker_nse
        else:
            stock = yf.Ticker(ticker)
            info = stock.info

        # Get current price and basic info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 'N/A')
        previous_close = info.get('previousClose', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        volume = info.get('volume', 'N/A')
        pe_ratio = info.get('trailingPE', 'N/A')

        # Get recent price history for trend analysis
        hist = stock.history(period="5d")
        if not hist.empty:
            latest_price = hist['Close'].iloc[-1]
            price_change = latest_price - hist['Close'].iloc[-2] if len(hist) > 1 else 0
            price_change_pct = (price_change / hist['Close'].iloc[-2]) * 100 if len(hist) > 1 else 0
            trend = "UPWARD" if price_change > 0 else "DOWNWARD" if price_change < 0 else "STABLE"
        else:
            latest_price = "N/A"
            price_change = "N/A"
            price_change_pct = "N/A"
            trend = "N/A"

        # Format market cap and volume with proper handling
        market_cap_str = f"₹{market_cap:,}" if market_cap != 'N/A' else 'N/A'
        volume_str = f"{volume:,}" if volume != 'N/A' else 'N/A'

        # Get exchange information
        exchange = "NSE" if ticker.endswith('.NS') else "BSE" if ticker.endswith('.BO') else "Unknown"

        report = (
            f"Stock Analysis for {ticker.upper()} ({exchange}):\n"
            f"Company: {info.get('longName', 'N/A')}\n"
            f"Sector: {info.get('sector', 'N/A')}\n"
            f"Industry: {info.get('industry', 'N/A')}\n\n"
            f"Current Price: ₹{current_price}\n"
            f"Previous Close: ₹{previous_close}\n"
            f"Latest Close: ₹{latest_price}\n"
            f"Price Change: ₹{price_change} ({price_change_pct:.2f}%)\n"
            f"Trend: {trend}\n\n"
            f"Market Cap: {market_cap_str}\n"
            f"Volume: {volume_str}\n"
            f"P/E Ratio: {pe_ratio}"
        )

        return {
            "status": "success",
            "report": report
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to fetch stock data for {ticker}: {str(e)}.\n"
                             f"Try NSE symbols like RELIANCE, INFY, TCS, HDFCBANK, WIPRO, etc."
        }
