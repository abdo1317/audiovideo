import ccxt
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

class DataFetcher:
    def __init__(self):
        """تهيئة جالب البيانات مع إعداد منصة Binance"""
        self.exchange = ccxt.binance({
            'apiKey': '',  # يمكن تركها فارغة للبيانات العامة
            'secret': '',
            'timeout': 30000,
            'enableRateLimit': True,
        })

    def get_crypto_data(self, symbol, timeframe='1d', limit=200):
        """
        جلب بيانات العملة الرقمية من Binance

        Args:
            symbol (str): رمز العملة مثل 'BTC/USDT'
            timeframe (str): الإطار الزمني ('1h', '4h', '1d', '1w')
            limit (int): عدد الشموع المطلوبة

        Returns:
            pd.DataFrame: بيانات OHLCV
        """
        try:
            # جلب البيانات من Binance
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

            # تحويل إلى DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            print(f"خطأ في جلب البيانات من Binance: {e}")
            return self._get_fallback_data(symbol, timeframe, limit)

    def _get_fallback_data(self, symbol, timeframe, limit):
        """
        جلب البيانات من yfinance كبديل
        """
        try:
            # تحويل رمز العملة لصيغة yfinance
            if '/' in symbol:
                base, quote = symbol.split('/')
                if quote == 'USDT':
                    yf_symbol = f"{base}-USD"
                else:
                    yf_symbol = f"{base}-{quote}"
            else:
                yf_symbol = symbol

            # تحديد فترة البيانات
            period_map = {
                '1h': '5d',
                '4h': '60d',
                '1d': '1y',
                '1w': '5y'
            }
            period = period_map.get(timeframe, '1y')

            # جلب البيانات
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=self._convert_timeframe(timeframe))

            # إعادة تسمية الأعمدة
            df.columns = [col.lower() for col in df.columns]
            df = df[['open', 'high', 'low', 'close', 'volume']].tail(limit)

            return df

        except Exception as e:
            print(f"خطأ في جلب البيانات من yfinance: {e}")
            return pd.DataFrame()

    def _convert_timeframe(self, timeframe):
        """تحويل الإطار الزمني لصيغة yfinance"""
        timeframe_map = {
            '1h': '1h',
            '4h': '1h',  # yfinance لا يدعم 4h مباشرة
            '1d': '1d',
            '1w': '1wk'
        }
        return timeframe_map.get(timeframe, '1d')

    def get_available_symbols(self):
        """الحصول على قائمة العملات القيادية (40 عملة)"""
        try:
            markets = self.exchange.load_markets()
            # فلترة العملات المقترنة بـ USDT
            usdt_pairs = [symbol for symbol in markets.keys() if symbol.endswith('/USDT')]

            # أفضل 40 عملة قيادية مرتبة حسب الأهمية
            top_40_coins = [
                # العملات الأساسية (Top 10)
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT',
                'SOL/USDT', 'DOGE/USDT', 'DOT/USDT', 'MATIC/USDT', 'LTC/USDT',

                # العملات القوية (11-20)
                'AVAX/USDT', 'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'XLM/USDT',
                'BCH/USDT', 'ALGO/USDT', 'VET/USDT', 'ICP/USDT', 'FIL/USDT',

                # العملات الناشئة (21-30)
                'NEAR/USDT', 'SAND/USDT', 'MANA/USDT', 'CRO/USDT', 'FTM/USDT',
                'HBAR/USDT', 'EOS/USDT', 'AAVE/USDT', 'GRT/USDT', 'ENJ/USDT',

                # العملات الإضافية (31-40)
                'THETA/USDT', 'XTZ/USDT', 'EGLD/USDT', 'KSM/USDT', 'FLOW/USDT',
                'CHZ/USDT', 'CAKE/USDT', 'AR/USDT', 'ZIL/USDT', 'ONE/USDT'
            ]

            # التحقق من توفر العملات في البورصة
            available_coins = [coin for coin in top_40_coins if coin in usdt_pairs]

            # إضافة عملات إضافية إذا لم تكن 40 عملة متاحة
            if len(available_coins) < 40:
                additional_coins = [
                    'SUSHI/USDT', 'COMP/USDT', 'YFI/USDT', 'SNX/USDT', 'MKR/USDT',
                    'DASH/USDT', 'ZEC/USDT', 'WAVES/USDT', 'ICX/USDT', 'ONT/USDT'
                ]
                for coin in additional_coins:
                    if coin in usdt_pairs and coin not in available_coins:
                        available_coins.append(coin)
                        if len(available_coins) >= 40:
                            break

            return available_coins[:40]

        except Exception as e:
            print(f"خطأ في جلب قائمة العملات: {e}")
            # قائمة افتراضية موسعة
            return [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT',
                'SOL/USDT', 'DOGE/USDT', 'DOT/USDT', 'MATIC/USDT', 'LTC/USDT',
                'AVAX/USDT', 'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'XLM/USDT',
                'BCH/USDT', 'ALGO/USDT', 'VET/USDT', 'ICP/USDT', 'FIL/USDT'
            ]

    def get_multiple_symbols_data(self, symbols, timeframe='1d', limit=200):
        """
        جلب بيانات عدة عملات

        Args:
            symbols (list): قائمة رموز العملات
            timeframe (str): الإطار الزمني
            limit (int): عدد الشموع

        Returns:
            dict: قاموس يحتوي على بيانات كل عملة
        """
        data = {}
        for symbol in symbols:
            try:
                df = self.get_crypto_data(symbol, timeframe, limit)
                if not df.empty:
                    data[symbol] = df
                time.sleep(0.1)  # تجنب تجاوز حدود API
            except Exception as e:
                print(f"خطأ في جلب بيانات {symbol}: {e}")
                continue

        return data
