import pandas as pd
from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
from datetime import datetime

class CryptoAnalyzer:
    def __init__(self):
        """تهيئة محلل العملات الرقمية"""
        self.data_fetcher = DataFetcher()
        self.timeframes = {
            '1H': '1h',
            '2H': '2h',
            '3H': '3h',
            '4H': '4h',
            '1D': '1d',
            '1W': '1w'
        }

    def analyze_single_crypto(self, symbol, timeframe='1d', limit=200):
        """
        تحليل عملة واحدة

        Args:
            symbol (str): رمز العملة
            timeframe (str): الإطار الزمني
            limit (int): عدد الشموع

        Returns:
            list: قائمة الإشارات
        """
        try:
            # جلب البيانات
            df = self.data_fetcher.get_crypto_data(symbol, timeframe, limit)

            if df.empty:
                return []

            # تحليل المؤشرات الفنية
            indicators = TechnicalIndicators(df)
            signals = indicators.get_all_signals()

            # إضافة معلومات العملة والإطار الزمني
            for signal in signals:
                signal['symbol'] = symbol
                signal['timeframe'] = timeframe
                signal['current_price'] = df['close'].iloc[-1]

            return signals

        except Exception as e:
            print(f"خطأ في تحليل {symbol}: {e}")
            return []

    def analyze_multiple_cryptos(self, symbols, timeframes=['1d'], limit=200):
        """
        تحليل عدة عملات على عدة أطر زمنية

        Args:
            symbols (list): قائمة رموز العملات
            timeframes (list): قائمة الأطر الزمنية
            limit (int): عدد الشموع

        Returns:
            pd.DataFrame: جدول الإشارات
        """
        all_signals = []

        for symbol in symbols:
            for timeframe in timeframes:
                signals = self.analyze_single_crypto(symbol, timeframe, limit)
                all_signals.extend(signals)

        if not all_signals:
            return pd.DataFrame()

        # تحويل إلى DataFrame
        df_signals = pd.DataFrame(all_signals)

        # ترتيب حسب الوقت (الأحدث أولاً)
        df_signals = df_signals.sort_values('timestamp', ascending=False)

        # إعادة تنسيق الأعمدة
        if not df_signals.empty:
            df_signals['timestamp'] = pd.to_datetime(df_signals['timestamp'])
            df_signals['وقت الإشارة'] = df_signals['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            df_signals['العملة'] = df_signals['symbol']
            df_signals['الإطار الزمني'] = df_signals['timeframe']
            df_signals['نوع الإشارة'] = df_signals['signal']
            df_signals['المؤشر'] = df_signals['type'].apply(self._format_indicator_name)
            df_signals['الوصف'] = df_signals['description']
            df_signals['السعر الحالي'] = df_signals['current_price'].round(4)

            # إضافة قوة الإشارة مع إصلاح القيم الخاطئة
            if 'strength_percentage' in df_signals.columns:
                # إصلاح القيم الخاطئة
                df_signals['strength_percentage_fixed'] = df_signals['strength_percentage'].apply(self._fix_strength_value)
                df_signals['قوة الإشارة'] = df_signals['strength_percentage_fixed'].round(1)
            else:
                # قوة افتراضية للإشارات القديمة
                df_signals['قوة الإشارة'] = df_signals.apply(self._calculate_default_strength, axis=1)

            # فحص نهائي إضافي لضمان عدم وجود قيم خاطئة
            df_signals['قوة الإشارة'] = df_signals['قوة الإشارة'].apply(self._final_strength_check)

            # اختيار الأعمدة المطلوبة
            columns_order = ['العملة', 'الإطار الزمني', 'نوع الإشارة', 'المؤشر',
                           'قوة الإشارة', 'وقت الإشارة', 'الوصف', 'السعر الحالي']
            df_signals = df_signals[columns_order]

        return df_signals

    def _format_indicator_name(self, indicator_type):
        """تنسيق أسماء المؤشرات باللغة العربية"""
        indicator_map = {
            # RSI إشارات
            'rsi_oversold': 'RSI - تشبع بيعي',
            'rsi_overbought': 'RSI - تشبع شرائي',
            'rsi_latest_bullish_divergence': '🔥 RSI - دايفرجنس صعودي (الشمعة الأخيرة)',
            'rsi_latest_bearish_divergence': '🔥 RSI - دايفرجنس هبوطي (الشمعة الأخيرة)',
            'rsi_simple_bullish_divergence': 'RSI - دايفرجنس صعودي',
            'rsi_simple_bearish_divergence': 'RSI - دايفرجنس هبوطي',

            # MA إشارات
            'ma_bullish_crossover': 'MA - تقاطع صعودي',
            'ma_bearish_crossover': 'MA - تقاطع هبوطي',

            # MACD إشارات
            'macd_latest_bullish_divergence': '🔥 MACD - دايفرجنس صعودي (الشمعة الأخيرة)',
            'macd_latest_bearish_divergence': '🔥 MACD - دايفرجنس هبوطي (الشمعة الأخيرة)',
            'macd_simple_bullish_divergence': 'MACD - دايفرجنس صعودي',
            'macd_simple_bearish_divergence': 'MACD - دايفرجنس هبوطي',

            # OBV إشارات
            'obv_latest_bullish_divergence': '🔥 OBV - دايفرجنس صعودي (الشمعة الأخيرة)',
            'obv_latest_bearish_divergence': '🔥 OBV - دايفرجنس هبوطي (الشمعة الأخيرة)',
            'obv_simple_bullish_divergence': 'OBV - دايفرجنس صعودي',
            'obv_simple_bearish_divergence': 'OBV - دايفرجنس هبوطي'
        }
        return indicator_map.get(indicator_type, indicator_type)

    def _calculate_default_strength(self, row):
        """حساب قوة محسنة للإشارات القديمة - بين 10-100%"""
        indicator_type = row['type']

        # قوة محسنة حسب نوع المؤشر (بين 10-100%)
        strength_map = {
            # إشارات الدايفرجنس الجديدة (قوية جداً)
            'rsi_latest_bullish_divergence': 85,
            'rsi_latest_bearish_divergence': 85,
            'macd_latest_bullish_divergence': 80,
            'macd_latest_bearish_divergence': 80,
            'obv_latest_bullish_divergence': 75,
            'obv_latest_bearish_divergence': 75,

            # إشارات الدايفرجنس البسيطة (متوسطة إلى قوية)
            'rsi_simple_bullish_divergence': 65,
            'rsi_simple_bearish_divergence': 65,
            'macd_simple_bullish_divergence': 60,
            'macd_simple_bearish_divergence': 60,
            'obv_simple_bullish_divergence': 55,
            'obv_simple_bearish_divergence': 55,

            # إشارات RSI التقليدية (متوسطة)
            'rsi_oversold': 45,
            'rsi_overbought': 45,

            # إشارات المتوسطات المتحركة (ضعيفة إلى متوسطة)
            'ma_bullish_crossover': 35,
            'ma_bearish_crossover': 35,
        }

        # التأكد من أن القيمة بين 10-100
        base_strength = strength_map.get(indicator_type, 40)
        return min(100, max(10, base_strength))

    def _fix_strength_value(self, value):
        """إصلاح قيم قوة الإشارة الخاطئة - نسخة محسنة"""
        try:
            # التحقق من أن القيمة رقم
            if pd.isna(value) or value is None:
                return 40.0  # قيمة افتراضية

            # تحويل إلى رقم
            numeric_value = float(value)

            # إصلاح القيم الخاطئة بطريقة أكثر دقة
            if numeric_value >= 10000:
                # قيم كبيرة جداً مثل 40000
                fixed_value = min(100.0, numeric_value / 1000)
            elif numeric_value >= 1000:
                # قيم كبيرة مثل 2060, 4000
                fixed_value = min(100.0, numeric_value / 100)
            elif numeric_value > 100:
                # قيم متوسطة كبيرة مثل 150, 200
                fixed_value = min(100.0, numeric_value / 10)
            elif numeric_value < 0:
                # قيم سالبة
                abs_value = abs(numeric_value)
                if abs_value > 100:
                    fixed_value = min(100.0, abs_value / 10)
                else:
                    fixed_value = min(100.0, abs_value)
            elif numeric_value < 10:
                # قيم صغيرة جداً
                fixed_value = max(10.0, numeric_value)
            else:
                # القيمة في النطاق الصحيح (10-100)
                fixed_value = numeric_value

            # التأكد النهائي من النطاق
            final_value = min(100.0, max(10.0, fixed_value))

            # تقريب لرقم عشري واحد
            return round(final_value, 1)

        except (ValueError, TypeError, OverflowError):
            # في حالة أي خطأ، إرجاع قيمة افتراضية
            return 40.0

    def _final_strength_check(self, value):
        """فحص نهائي لضمان أن قوة الإشارة في النطاق الصحيح"""
        try:
            # تحويل إلى رقم
            numeric_value = float(value)

            # التأكد من النطاق النهائي
            if numeric_value > 100:
                return 100.0
            elif numeric_value < 10:
                return 10.0
            else:
                return round(numeric_value, 1)

        except (ValueError, TypeError):
            # في حالة خطأ، إرجاع قيمة افتراضية
            return 40.0

    def get_market_overview(self, symbols, timeframe='1d'):
        """
        نظرة عامة على السوق

        Args:
            symbols (list): قائمة العملات
            timeframe (str): الإطار الزمني

        Returns:
            dict: ملخص السوق
        """
        overview = {
            'total_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'most_active_coins': [],
            'signal_distribution': {}
        }

        try:
            # تحليل جميع العملات
            signals_df = self.analyze_multiple_cryptos(symbols, [timeframe])

            if signals_df.empty:
                return overview

            # إحصائيات عامة
            overview['total_signals'] = len(signals_df)
            overview['buy_signals'] = len(signals_df[signals_df['نوع الإشارة'] == 'شراء'])
            overview['sell_signals'] = len(signals_df[signals_df['نوع الإشارة'] == 'بيع'])

            # العملات الأكثر نشاطاً
            coin_counts = signals_df['العملة'].value_counts().head(5)
            overview['most_active_coins'] = coin_counts.to_dict()

            # توزيع الإشارات حسب المؤشر
            indicator_counts = signals_df['المؤشر'].value_counts()
            overview['signal_distribution'] = indicator_counts.to_dict()

        except Exception as e:
            print(f"خطأ في حساب نظرة عامة على السوق: {e}")

        return overview

    def filter_signals(self, signals_df, symbol_filter=None, signal_type_filter=None,
                      indicator_filter=None, hours_back=24):
        """
        فلترة الإشارات

        Args:
            signals_df (pd.DataFrame): جدول الإشارات
            symbol_filter (str): فلتر العملة
            signal_type_filter (str): فلتر نوع الإشارة
            indicator_filter (str): فلتر المؤشر
            hours_back (int): عدد الساعات الماضية

        Returns:
            pd.DataFrame: الإشارات المفلترة
        """
        if signals_df.empty:
            return signals_df

        filtered_df = signals_df.copy()

        # فلتر الوقت
        if hours_back > 0:
            cutoff_time = datetime.now() - pd.Timedelta(hours=hours_back)
            filtered_df = filtered_df[pd.to_datetime(filtered_df['وقت الإشارة']) >= cutoff_time]

        # فلتر العملة
        if symbol_filter and symbol_filter != 'الكل':
            filtered_df = filtered_df[filtered_df['العملة'] == symbol_filter]

        # فلتر نوع الإشارة
        if signal_type_filter and signal_type_filter != 'الكل':
            filtered_df = filtered_df[filtered_df['نوع الإشارة'] == signal_type_filter]

        # فلتر المؤشر
        if indicator_filter and indicator_filter != 'الكل':
            filtered_df = filtered_df[filtered_df['المؤشر'].str.contains(indicator_filter, na=False)]

        return filtered_df
