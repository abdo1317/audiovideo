import pandas as pd
import numpy as np
import ta
try:
    from scipy.signal import argrelextrema
except ImportError:
    # بديل بسيط إذا لم تكن scipy متاحة
    def argrelextrema(data, comparator, order=1):
        peaks = []
        for i in range(order, len(data) - order):
            if comparator == np.greater:
                if all(data[i] > data[i-j] for j in range(1, order+1)) and \
                   all(data[i] > data[i+j] for j in range(1, order+1)):
                    peaks.append(i)
            elif comparator == np.less:
                if all(data[i] < data[i-j] for j in range(1, order+1)) and \
                   all(data[i] < data[i+j] for j in range(1, order+1)):
                    peaks.append(i)
        return (np.array(peaks),)

class TechnicalIndicators:
    def __init__(self, df):
        """
        تهيئة حاسبة المؤشرات الفنية

        Args:
            df (pd.DataFrame): بيانات OHLCV
        """
        self.df = df.copy()
        self.signals = []

    def calculate_rsi(self, period=14):
        """حساب مؤشر RSI"""
        rsi_indicator = ta.momentum.RSIIndicator(self.df['close'], window=period)
        self.df['rsi'] = rsi_indicator.rsi()
        return self.df['rsi']

    def calculate_macd(self, fast=12, slow=26, signal=9):
        """حساب مؤشر MACD"""
        macd_indicator = ta.trend.MACD(self.df['close'], window_fast=fast, window_slow=slow, window_sign=signal)
        self.df['macd'] = macd_indicator.macd()
        self.df['macd_signal'] = macd_indicator.macd_signal()
        self.df['macd_histogram'] = macd_indicator.macd_diff()
        return self.df[['macd', 'macd_signal', 'macd_histogram']]

    def calculate_obv(self):
        """حساب مؤشر OBV"""
        obv_indicator = ta.volume.OnBalanceVolumeIndicator(self.df['close'], self.df['volume'])
        self.df['obv'] = obv_indicator.on_balance_volume()
        return self.df['obv']

    def calculate_moving_averages(self, short_period=9, long_period=20):
        """حساب المتوسطات المتحركة"""
        self.df['ma_short'] = ta.trend.SMAIndicator(self.df['close'], window=short_period).sma_indicator()
        self.df['ma_long'] = ta.trend.SMAIndicator(self.df['close'], window=long_period).sma_indicator()
        return self.df[['ma_short', 'ma_long']]

    def detect_divergence(self, price_series, indicator_series, lookback=3):
        """
        اكتشاف الدايفرجنس بين السعر والمؤشر - نسخة محسنة

        Args:
            price_series: سلسلة الأسعار
            indicator_series: سلسلة المؤشر
            lookback: عدد النقاط للبحث عن القمم والقيعان

        Returns:
            list: قائمة بإشارات الدايفرجنس
        """
        divergences = []

        # تنظيف البيانات من القيم المفقودة
        clean_data = pd.DataFrame({
            'price': price_series,
            'indicator': indicator_series
        }).dropna()

        if len(clean_data) < 20:  # نحتاج بيانات كافية
            return divergences

        price_clean = clean_data['price']
        indicator_clean = clean_data['indicator']

        # البحث عن القمم والقيعان بطريقة أكثر مرونة
        price_highs = argrelextrema(price_clean.values, np.greater, order=lookback)[0]
        price_lows = argrelextrema(price_clean.values, np.less, order=lookback)[0]

        indicator_highs = argrelextrema(indicator_clean.values, np.greater, order=lookback)[0]
        indicator_lows = argrelextrema(indicator_clean.values, np.less, order=lookback)[0]

        # البحث عن الدايفرجنس الصعودي (Bullish Divergence)
        if len(price_lows) >= 2:
            for i in range(1, len(price_lows)):
                price_idx1, price_idx2 = price_lows[i-1], price_lows[i]

                # البحث عن أقرب قاع في المؤشر
                closest_ind_low = None
                min_distance = float('inf')

                for ind_idx in indicator_lows:
                    distance = abs(ind_idx - price_idx2)
                    if distance < min_distance and distance <= 10:  # مرونة أكبر في المسافة
                        min_distance = distance
                        closest_ind_low = ind_idx

                if closest_ind_low is not None:
                    # البحث عن القاع السابق في المؤشر
                    prev_ind_low = None
                    for ind_idx in indicator_lows:
                        if ind_idx < closest_ind_low and abs(ind_idx - price_idx1) <= 10:
                            prev_ind_low = ind_idx
                            break

                    if prev_ind_low is not None:
                        price_val1 = price_clean.iloc[price_idx1]
                        price_val2 = price_clean.iloc[price_idx2]
                        ind_val1 = indicator_clean.iloc[prev_ind_low]
                        ind_val2 = indicator_clean.iloc[closest_ind_low]

                        # دايفرجنس صعودي: السعر ينخفض والمؤشر يرتفع
                        price_change = (price_val2 - price_val1) / price_val1
                        ind_change = (ind_val2 - ind_val1) / abs(ind_val1) if ind_val1 != 0 else 0

                        if price_change < -0.02 and ind_change > 0.05:  # تحسين الشروط
                            divergences.append({
                                'type': 'bullish_divergence',
                                'timestamp': price_clean.index[price_idx2],
                                'strength': abs(price_change) + abs(ind_change),
                                'price_change': price_change,
                                'indicator_change': ind_change
                            })

        # البحث عن الدايفرجنس الهبوطي (Bearish Divergence)
        if len(price_highs) >= 2:
            for i in range(1, len(price_highs)):
                price_idx1, price_idx2 = price_highs[i-1], price_highs[i]

                # البحث عن أقرب قمة في المؤشر
                closest_ind_high = None
                min_distance = float('inf')

                for ind_idx in indicator_highs:
                    distance = abs(ind_idx - price_idx2)
                    if distance < min_distance and distance <= 10:
                        min_distance = distance
                        closest_ind_high = ind_idx

                if closest_ind_high is not None:
                    # البحث عن القمة السابقة في المؤشر
                    prev_ind_high = None
                    for ind_idx in indicator_highs:
                        if ind_idx < closest_ind_high and abs(ind_idx - price_idx1) <= 10:
                            prev_ind_high = ind_idx
                            break

                    if prev_ind_high is not None:
                        price_val1 = price_clean.iloc[price_idx1]
                        price_val2 = price_clean.iloc[price_idx2]
                        ind_val1 = indicator_clean.iloc[prev_ind_high]
                        ind_val2 = indicator_clean.iloc[closest_ind_high]

                        # دايفرجنس هبوطي: السعر يرتفع والمؤشر ينخفض
                        price_change = (price_val2 - price_val1) / price_val1
                        ind_change = (ind_val2 - ind_val1) / abs(ind_val1) if ind_val1 != 0 else 0

                        if price_change > 0.02 and ind_change < -0.05:
                            divergences.append({
                                'type': 'bearish_divergence',
                                'timestamp': price_clean.index[price_idx2],
                                'strength': abs(price_change) + abs(ind_change),
                                'price_change': price_change,
                                'indicator_change': ind_change
                            })

        return divergences

    def detect_simple_divergence(self, price_series, indicator_series, window=20):
        """
        طريقة بديلة أبسط لاكتشاف الدايفرجنس
        """
        divergences = []

        if len(price_series) < window * 2:
            return divergences

        # تحليل النوافذ المتحركة
        for i in range(window, len(price_series) - window):
            # النافذة الأولى (الماضي)
            price_window1 = price_series.iloc[i-window:i]
            ind_window1 = indicator_series.iloc[i-window:i]

            # النافذة الثانية (الحاضر)
            price_window2 = price_series.iloc[i:i+window]
            ind_window2 = indicator_series.iloc[i:i+window]

            # حساب الاتجاهات
            price_trend1 = price_window1.iloc[-1] - price_window1.iloc[0]
            price_trend2 = price_window2.iloc[-1] - price_window2.iloc[0]

            ind_trend1 = ind_window1.iloc[-1] - ind_window1.iloc[0]
            ind_trend2 = ind_window2.iloc[-1] - ind_window2.iloc[0]

            # البحث عن الدايفرجنس
            if price_trend2 < 0 and ind_trend2 > 0 and abs(price_trend2) > abs(price_trend1) * 0.5:
                # دايفرجنس صعودي
                divergences.append({
                    'type': 'bullish_divergence',
                    'timestamp': price_series.index[i + window - 1],
                    'strength': abs(price_trend2) + abs(ind_trend2)
                })
            elif price_trend2 > 0 and ind_trend2 < 0 and abs(price_trend2) > abs(price_trend1) * 0.5:
                # دايفرجنس هبوطي
                divergences.append({
                    'type': 'bearish_divergence',
                    'timestamp': price_series.index[i + window - 1],
                    'strength': abs(price_trend2) + abs(ind_trend2)
                })

        return divergences

    def detect_latest_divergence(self, price_series, indicator_series, lookback_periods=10):
        """
        اكتشاف الدايفرجنس في الشمعة الأخيرة فقط

        Args:
            price_series: سلسلة الأسعار
            indicator_series: سلسلة المؤشر
            lookback_periods: عدد الفترات للمقارنة مع الشمعة الأخيرة

        Returns:
            list: إشارات الدايفرجنس في الشمعة الأخيرة
        """
        divergences = []

        # التأكد من أن المؤشرات محسوبة
        if 'rsi' not in self.df.columns:
            self.calculate_rsi()
        if 'macd_histogram' not in self.df.columns:
            self.calculate_macd()
        if 'obv' not in self.df.columns:
            self.calculate_obv()

        # استخدام البيانات من DataFrame مباشرة
        try:
            if 'rsi' in str(indicator_series.name) or len(indicator_series) == len(self.df):
                if 'rsi' in self.df.columns:
                    indicator_series = self.df['rsi']
                elif 'macd_histogram' in self.df.columns:
                    indicator_series = self.df['macd_histogram']
                elif 'obv' in self.df.columns:
                    indicator_series = self.df['obv']
        except:
            pass

        if len(price_series) < lookback_periods + 5:
            return divergences

        # الشمعة الأخيرة (الحالية)
        current_price = price_series.iloc[-1]
        current_indicator = indicator_series.iloc[-1]
        current_timestamp = price_series.index[-1]

        # البحث في الفترات السابقة للمقارنة
        for i in range(2, min(lookback_periods + 1, len(price_series) - 1)):
            past_price = price_series.iloc[-i]
            past_indicator = indicator_series.iloc[-i]

            # حساب التغيير في السعر والمؤشر
            price_change = (current_price - past_price) / past_price
            indicator_change = (current_indicator - past_indicator) / abs(past_indicator) if past_indicator != 0 else 0

            # شروط الدايفرجنس الصعودي (إشارة شراء)
            # السعر ينخفض لكن المؤشر يرتفع
            if price_change < -0.01 and indicator_change > 0.02:  # تغيير السعر -1% والمؤشر +2%
                strength = abs(price_change) + abs(indicator_change)
                if strength > 0.05:  # قوة إجمالية 5%
                    divergences.append({
                        'type': 'bullish_divergence',
                        'timestamp': current_timestamp,
                        'strength': strength,
                        'price_change_pct': price_change * 100,
                        'indicator_change_pct': indicator_change * 100,
                        'periods_back': i,
                        'signal': 'شراء',
                        'description': f'دايفرجنس صعودي: السعر انخفض {abs(price_change)*100:.1f}% والمؤشر ارتفع {indicator_change*100:.1f}%'
                    })
                    break  # أول إشارة قوية كافية

            # شروط الدايفرجنس الهبوطي (إشارة بيع)
            # السعر يرتفع لكن المؤشر ينخفض
            elif price_change > 0.01 and indicator_change < -0.02:  # تغيير السعر +1% والمؤشر -2%
                strength = abs(price_change) + abs(indicator_change)
                if strength > 0.05:  # قوة إجمالية 5%
                    divergences.append({
                        'type': 'bearish_divergence',
                        'timestamp': current_timestamp,
                        'strength': strength,
                        'price_change_pct': price_change * 100,
                        'indicator_change_pct': indicator_change * 100,
                        'periods_back': i,
                        'signal': 'بيع',
                        'description': f'دايفرجنس هبوطي: السعر ارتفع {price_change*100:.1f}% والمؤشر انخفض {abs(indicator_change)*100:.1f}%'
                    })
                    break  # أول إشارة قوية كافية

        return divergences

    def detect_tradingview_divergence(self):
        """
        اكتشاف الدايفرجنس الصحيح بطريقة TradingView
        منطق بسيط وصحيح: مقارنة آخر قمتين أو آخر قاعين فقط
        """
        signals = []

        if len(self.df) < 30:
            return signals

        # التأكد من حساب المؤشرات
        try:
            if 'rsi' not in self.df.columns:
                self.calculate_rsi()
            if 'macd_histogram' not in self.df.columns:
                self.calculate_macd()
            if 'obv' not in self.df.columns:
                self.calculate_obv()
        except Exception as e:
            print(f"خطأ في حساب المؤشرات: {e}")
            return signals

        # تحليل آخر 30 شمعة فقط
        recent_data = self.df.tail(30).copy()
        current_timestamp = recent_data.index[-1]

        # البحث عن الدايفرجنس لكل مؤشر
        signals.extend(self._detect_rsi_divergence_simple(recent_data, current_timestamp))
        signals.extend(self._detect_macd_divergence_simple(recent_data, current_timestamp))
        signals.extend(self._detect_obv_divergence_simple(recent_data, current_timestamp))

        return signals

    def _detect_rsi_divergence_simple(self, data, timestamp):
        """اكتشاف دايفرجنس RSI بطريقة بسيطة وصحيحة"""
        signals = []

        # البحث عن آخر قمتين في السعر
        price_highs = []
        for i in range(2, len(data) - 2):
            if (data['high'].iloc[i] > data['high'].iloc[i-1] and
                data['high'].iloc[i] > data['high'].iloc[i-2] and
                data['high'].iloc[i] > data['high'].iloc[i+1] and
                data['high'].iloc[i] > data['high'].iloc[i+2]):
                price_highs.append((i, data['high'].iloc[i]))

        # البحث عن آخر قاعين في السعر
        price_lows = []
        for i in range(2, len(data) - 2):
            if (data['low'].iloc[i] < data['low'].iloc[i-1] and
                data['low'].iloc[i] < data['low'].iloc[i-2] and
                data['low'].iloc[i] < data['low'].iloc[i+1] and
                data['low'].iloc[i] < data['low'].iloc[i+2]):
                price_lows.append((i, data['low'].iloc[i]))

        # التحقق من الدايفرجنس الهبوطي (آخر قمتين)
        if len(price_highs) >= 2:
            # آخر قمتين
            peak1_idx, peak1_price = price_highs[-2]
            peak2_idx, peak2_price = price_highs[-1]

            # التأكد من أن القمة الثانية قريبة من النهاية (آخر 5 شموع)
            if peak2_idx >= len(data) - 5:
                peak1_rsi = data['rsi'].iloc[peak1_idx]
                peak2_rsi = data['rsi'].iloc[peak2_idx]

                # دايفرجنس هبوطي: سعر أعلى + RSI أقل
                if (peak2_price > peak1_price and peak2_rsi < peak1_rsi and
                    (peak2_price - peak1_price) / peak1_price > 0.005 and  # 0.5% على الأقل
                    abs(peak2_rsi - peak1_rsi) > 2):  # فرق RSI 2 نقاط على الأقل

                    # حساب قوة الإشارة بطريقة محسنة
                    price_change_pct = (peak2_price - peak1_price) / peak1_price * 100
                    rsi_change = abs(peak2_rsi - peak1_rsi)

                    # تطبيع القوة لتكون بين 0-100
                    price_strength = min(50, abs(price_change_pct) * 10)  # حد أقصى 50 من السعر
                    rsi_strength = min(50, rsi_change * 2)  # حد أقصى 50 من RSI
                    total_strength = price_strength + rsi_strength

                    signals.append({
                        'type': 'rsi_latest_bearish_divergence',
                        'timestamp': timestamp,
                        'signal': 'بيع',
                        'description': f'🔥 RSI دايفرجنس هبوطي: قمة سعر جديدة ${peak2_price:.2f} > ${peak1_price:.2f} لكن RSI انخفض {peak2_rsi:.1f} < {peak1_rsi:.1f} (الشمعة الأخيرة)',
                        'strength': total_strength,
                        'strength_percentage': min(100, max(10, total_strength))  # بين 10-100%
                    })

        # التحقق من الدايفرجنس الصعودي (آخر قاعين)
        if len(price_lows) >= 2:
            # آخر قاعين
            low1_idx, low1_price = price_lows[-2]
            low2_idx, low2_price = price_lows[-1]

            # التأكد من أن القاع الثاني قريب من النهاية (آخر 5 شموع)
            if low2_idx >= len(data) - 5:
                low1_rsi = data['rsi'].iloc[low1_idx]
                low2_rsi = data['rsi'].iloc[low2_idx]

                # دايفرجنس صعودي: سعر أقل + RSI أعلى
                if (low2_price < low1_price and low2_rsi > low1_rsi and
                    (low1_price - low2_price) / low1_price > 0.005 and  # 0.5% على الأقل
                    abs(low2_rsi - low1_rsi) > 2):  # فرق RSI 2 نقاط على الأقل

                    # حساب قوة الإشارة بطريقة محسنة
                    price_change_pct = (low1_price - low2_price) / low1_price * 100
                    rsi_change = abs(low2_rsi - low1_rsi)

                    # تطبيع القوة لتكون بين 0-100
                    price_strength = min(50, abs(price_change_pct) * 10)  # حد أقصى 50 من السعر
                    rsi_strength = min(50, rsi_change * 2)  # حد أقصى 50 من RSI
                    total_strength = price_strength + rsi_strength

                    signals.append({
                        'type': 'rsi_latest_bullish_divergence',
                        'timestamp': timestamp,
                        'signal': 'شراء',
                        'description': f'🔥 RSI دايفرجنس صعودي: قاع سعر جديد ${low2_price:.2f} < ${low1_price:.2f} لكن RSI ارتفع {low2_rsi:.1f} > {low1_rsi:.1f} (الشمعة الأخيرة)',
                        'strength': total_strength,
                        'strength_percentage': min(100, max(10, total_strength))  # بين 10-100%
                    })

        return signals

    def _detect_macd_divergence_simple(self, data, timestamp):
        """اكتشاف دايفرجنس MACD بطريقة بسيطة وصحيحة"""
        signals = []

        # البحث عن آخر قمتين في السعر
        price_highs = []
        for i in range(2, len(data) - 2):
            if (data['high'].iloc[i] > data['high'].iloc[i-1] and
                data['high'].iloc[i] > data['high'].iloc[i-2] and
                data['high'].iloc[i] > data['high'].iloc[i+1] and
                data['high'].iloc[i] > data['high'].iloc[i+2]):
                price_highs.append((i, data['high'].iloc[i]))

        # البحث عن آخر قاعين في السعر
        price_lows = []
        for i in range(2, len(data) - 2):
            if (data['low'].iloc[i] < data['low'].iloc[i-1] and
                data['low'].iloc[i] < data['low'].iloc[i-2] and
                data['low'].iloc[i] < data['low'].iloc[i+1] and
                data['low'].iloc[i] < data['low'].iloc[i+2]):
                price_lows.append((i, data['low'].iloc[i]))

        # التحقق من الدايفرجنس الهبوطي
        if len(price_highs) >= 2:
            peak1_idx, peak1_price = price_highs[-2]
            peak2_idx, peak2_price = price_highs[-1]

            if peak2_idx >= len(data) - 5:
                peak1_macd = data['macd_histogram'].iloc[peak1_idx]
                peak2_macd = data['macd_histogram'].iloc[peak2_idx]

                if (peak2_price > peak1_price and peak2_macd < peak1_macd and
                    (peak2_price - peak1_price) / peak1_price > 0.005 and
                    abs(peak2_macd - peak1_macd) > 0.1):

                    # حساب قوة الإشارة بطريقة محسنة
                    price_change_pct = (peak2_price - peak1_price) / peak1_price * 100
                    macd_change = abs(peak2_macd - peak1_macd)

                    # تطبيع القوة لتكون بين 0-100
                    price_strength = min(50, abs(price_change_pct) * 10)  # حد أقصى 50 من السعر
                    macd_strength = min(50, macd_change * 200)  # حد أقصى 50 من MACD
                    total_strength = price_strength + macd_strength

                    signals.append({
                        'type': 'macd_latest_bearish_divergence',
                        'timestamp': timestamp,
                        'signal': 'بيع',
                        'description': f'🔥 MACD دايفرجنس هبوطي: قمة سعر جديدة لكن MACD انخفض (الشمعة الأخيرة)',
                        'strength': total_strength,
                        'strength_percentage': min(100, max(10, total_strength))  # بين 10-100%
                    })

        # التحقق من الدايفرجنس الصعودي
        if len(price_lows) >= 2:
            low1_idx, low1_price = price_lows[-2]
            low2_idx, low2_price = price_lows[-1]

            if low2_idx >= len(data) - 5:
                low1_macd = data['macd_histogram'].iloc[low1_idx]
                low2_macd = data['macd_histogram'].iloc[low2_idx]

                if (low2_price < low1_price and low2_macd > low1_macd and
                    (low1_price - low2_price) / low1_price > 0.005 and
                    abs(low2_macd - low1_macd) > 0.1):

                    # حساب قوة الإشارة بطريقة محسنة
                    price_change_pct = (low1_price - low2_price) / low1_price * 100
                    macd_change = abs(low2_macd - low1_macd)

                    # تطبيع القوة لتكون بين 0-100
                    price_strength = min(50, abs(price_change_pct) * 10)  # حد أقصى 50 من السعر
                    macd_strength = min(50, macd_change * 200)  # حد أقصى 50 من MACD
                    total_strength = price_strength + macd_strength

                    signals.append({
                        'type': 'macd_latest_bullish_divergence',
                        'timestamp': timestamp,
                        'signal': 'شراء',
                        'description': f'🔥 MACD دايفرجنس صعودي: قاع سعر جديد لكن MACD ارتفع (الشمعة الأخيرة)',
                        'strength': total_strength,
                        'strength_percentage': min(100, max(10, total_strength))  # بين 10-100%
                    })

        return signals

    def _detect_obv_divergence_simple(self, data, timestamp):
        """اكتشاف دايفرجنس OBV بطريقة بسيطة وصحيحة"""
        signals = []

        # البحث عن آخر قمتين في السعر
        price_highs = []
        for i in range(2, len(data) - 2):
            if (data['high'].iloc[i] > data['high'].iloc[i-1] and
                data['high'].iloc[i] > data['high'].iloc[i-2] and
                data['high'].iloc[i] > data['high'].iloc[i+1] and
                data['high'].iloc[i] > data['high'].iloc[i+2]):
                price_highs.append((i, data['high'].iloc[i]))

        # البحث عن آخر قاعين في السعر
        price_lows = []
        for i in range(2, len(data) - 2):
            if (data['low'].iloc[i] < data['low'].iloc[i-1] and
                data['low'].iloc[i] < data['low'].iloc[i-2] and
                data['low'].iloc[i] < data['low'].iloc[i+1] and
                data['low'].iloc[i] < data['low'].iloc[i+2]):
                price_lows.append((i, data['low'].iloc[i]))

        # التحقق من الدايفرجنس الهبوطي
        if len(price_highs) >= 2:
            peak1_idx, peak1_price = price_highs[-2]
            peak2_idx, peak2_price = price_highs[-1]

            if peak2_idx >= len(data) - 5:
                peak1_obv = data['obv'].iloc[peak1_idx]
                peak2_obv = data['obv'].iloc[peak2_idx]

                if (peak2_price > peak1_price and peak2_obv < peak1_obv and
                    (peak2_price - peak1_price) / peak1_price > 0.005):

                    # حساب قوة الإشارة بطريقة محسنة
                    price_change_pct = (peak2_price - peak1_price) / peak1_price * 100
                    obv_change_pct = abs(peak2_obv - peak1_obv) / abs(peak1_obv) * 100 if peak1_obv != 0 else 5

                    # تطبيع القوة لتكون بين 0-100
                    price_strength = min(50, abs(price_change_pct) * 10)  # حد أقصى 50 من السعر
                    obv_strength = min(50, obv_change_pct)  # حد أقصى 50 من OBV
                    total_strength = price_strength + obv_strength

                    signals.append({
                        'type': 'obv_latest_bearish_divergence',
                        'timestamp': timestamp,
                        'signal': 'بيع',
                        'description': f'🔥 OBV دايفرجنس هبوطي: قمة سعر جديدة لكن OBV انخفض (الشمعة الأخيرة)',
                        'strength': total_strength,
                        'strength_percentage': min(100, max(10, total_strength))  # بين 10-100%
                    })

        # التحقق من الدايفرجنس الصعودي
        if len(price_lows) >= 2:
            low1_idx, low1_price = price_lows[-2]
            low2_idx, low2_price = price_lows[-1]

            if low2_idx >= len(data) - 5:
                low1_obv = data['obv'].iloc[low1_idx]
                low2_obv = data['obv'].iloc[low2_idx]

                if (low2_price < low1_price and low2_obv > low1_obv and
                    (low1_price - low2_price) / low1_price > 0.005):

                    # حساب قوة الإشارة بطريقة محسنة
                    price_change_pct = (low1_price - low2_price) / low1_price * 100
                    obv_change_pct = abs(low2_obv - low1_obv) / abs(low1_obv) * 100 if low1_obv != 0 else 5

                    # تطبيع القوة لتكون بين 0-100
                    price_strength = min(50, abs(price_change_pct) * 10)  # حد أقصى 50 من السعر
                    obv_strength = min(50, obv_change_pct)  # حد أقصى 50 من OBV
                    total_strength = price_strength + obv_strength

                    signals.append({
                        'type': 'obv_latest_bullish_divergence',
                        'timestamp': timestamp,
                        'signal': 'شراء',
                        'description': f'🔥 OBV دايفرجنس صعودي: قاع سعر جديد لكن OBV ارتفع (الشمعة الأخيرة)',
                        'strength': total_strength,
                        'strength_percentage': min(100, max(10, total_strength))  # بين 10-100%
                    })

        return signals

    def _find_peaks(self, series, min_distance=5):
        """البحث عن القمم الحقيقية"""
        peaks = []
        for i in range(min_distance, len(series) - min_distance):
            is_peak = True
            current_val = series.iloc[i]

            # التحقق من أن القيمة أعلى من الجيران
            for j in range(1, min_distance + 1):
                if (current_val <= series.iloc[i-j] or
                    current_val <= series.iloc[i+j]):
                    is_peak = False
                    break

            if is_peak:
                peaks.append(i)

        return peaks

    def _find_troughs(self, series, min_distance=5):
        """البحث عن القيعان الحقيقية"""
        troughs = []
        for i in range(min_distance, len(series) - min_distance):
            is_trough = True
            current_val = series.iloc[i]

            # التحقق من أن القيمة أقل من الجيران
            for j in range(1, min_distance + 1):
                if (current_val >= series.iloc[i-j] or
                    current_val >= series.iloc[i+j]):
                    is_trough = False
                    break

            if is_trough:
                troughs.append(i)

        return troughs

    def _check_latest_divergence(self, data, current_idx, price_highs, price_lows,
                                indicator_highs, indicator_lows, price_col, indicator_col, indicator_name):
        """
        التحقق من الدايفرجنس في الشمعة الأخيرة
        """
        # التحقق من أن الشمعة الأخيرة قريبة من قمة أو قاع
        tolerance = 3  # السماح بـ 3 شموع من القمة/القاع

        # البحث عن دايفرجنس هبوطي (عند القمم)
        recent_price_highs = [h for h in price_highs if abs(h - current_idx) <= tolerance]
        recent_indicator_highs = [h for h in indicator_highs if abs(h - current_idx) <= tolerance]

        if recent_price_highs and len(price_highs) >= 2:
            # العثور على قمة سابقة للمقارنة
            for prev_price_high in reversed(price_highs[:-1]):
                if prev_price_high < current_idx - 10:  # على الأقل 10 شموع سابقة
                    # البحث عن قمة مؤشر مقابلة
                    closest_indicator_high = min(indicator_highs,
                                               key=lambda x: abs(x - prev_price_high))

                    if abs(closest_indicator_high - prev_price_high) <= 5:
                        # مقارنة القيم
                        current_price = data[price_col].iloc[current_idx]
                        prev_price = data[price_col].iloc[prev_price_high]

                        current_indicator = data[indicator_col].iloc[current_idx]
                        prev_indicator = data[indicator_col].iloc[closest_indicator_high]

                        # دايفرجنس هبوطي: سعر أعلى، مؤشر أقل
                        if (current_price > prev_price and
                            current_indicator < prev_indicator and
                            (current_price - prev_price) / prev_price > 0.01):  # 1% على الأقل

                            return {
                                'type': f'{indicator_col}_latest_bearish_divergence',
                                'signal': 'بيع',
                                'description': f'🔥 {indicator_name} دايفرجنس هبوطي: سعر جديد أعلى لكن {indicator_name} أقل (الشمعة الأخيرة)',
                                'strength': abs((current_price - prev_price) / prev_price),
                                'price_change': (current_price - prev_price) / prev_price * 100,
                                'indicator_change': current_indicator - prev_indicator
                            }
                    break

        # البحث عن دايفرجنس صعودي (عند القيعان)
        recent_price_lows = [l for l in price_lows if abs(l - current_idx) <= tolerance]
        recent_indicator_lows = [l for l in indicator_lows if abs(l - current_idx) <= tolerance]

        if recent_price_lows and len(price_lows) >= 2:
            # العثور على قاع سابق للمقارنة
            for prev_price_low in reversed(price_lows[:-1]):
                if prev_price_low < current_idx - 10:  # على الأقل 10 شموع سابقة
                    # البحث عن قاع مؤشر مقابل
                    closest_indicator_low = min(indicator_lows,
                                              key=lambda x: abs(x - prev_price_low))

                    if abs(closest_indicator_low - prev_price_low) <= 5:
                        # مقارنة القيم
                        current_price = data['low'].iloc[current_idx]  # استخدام Low للقيعان
                        prev_price = data['low'].iloc[prev_price_low]

                        current_indicator = data[indicator_col].iloc[current_idx]
                        prev_indicator = data[indicator_col].iloc[closest_indicator_low]

                        # دايفرجنس صعودي: سعر أقل، مؤشر أعلى
                        if (current_price < prev_price and
                            current_indicator > prev_indicator and
                            (prev_price - current_price) / prev_price > 0.01):  # 1% على الأقل

                            return {
                                'type': f'{indicator_col}_latest_bullish_divergence',
                                'signal': 'شراء',
                                'description': f'🔥 {indicator_name} دايفرجنس صعودي: قاع جديد أقل لكن {indicator_name} أعلى (الشمعة الأخيرة)',
                                'strength': abs((prev_price - current_price) / prev_price),
                                'price_change': (current_price - prev_price) / prev_price * 100,
                                'indicator_change': current_indicator - prev_indicator
                            }
                    break

        return None

    def analyze_ma_crossover(self):
        """تحليل تقاطع المتوسطات المتحركة"""
        signals = []

        if 'ma_short' not in self.df.columns or 'ma_long' not in self.df.columns:
            self.calculate_moving_averages()

        # البحث عن التقاطعات
        for i in range(1, len(self.df)):
            prev_short = self.df['ma_short'].iloc[i-1]
            prev_long = self.df['ma_long'].iloc[i-1]
            curr_short = self.df['ma_short'].iloc[i]
            curr_long = self.df['ma_long'].iloc[i]

            # تقاطع صعودي
            if prev_short <= prev_long and curr_short > curr_long:
                signals.append({
                    'type': 'ma_bullish_crossover',
                    'timestamp': self.df.index[i],
                    'signal': 'شراء',
                    'description': 'MA9 تقطع MA20 صعودياً',
                    'strength_percentage': 35.0  # قوة افتراضية
                })

            # تقاطع هبوطي
            elif prev_short >= prev_long and curr_short < curr_long:
                signals.append({
                    'type': 'ma_bearish_crossover',
                    'timestamp': self.df.index[i],
                    'signal': 'بيع',
                    'description': 'MA9 تقطع MA20 هبوطياً',
                    'strength_percentage': 35.0  # قوة افتراضية
                })

        return signals

    def analyze_rsi_signals(self):
        """تحليل إشارات RSI"""
        signals = []

        if 'rsi' not in self.df.columns:
            self.calculate_rsi()

        # إشارات RSI التقليدية
        for i in range(len(self.df)):
            rsi_val = self.df['rsi'].iloc[i]
            timestamp = self.df.index[i]

            if rsi_val <= 30:
                # حساب قوة الإشارة بناءً على مدى انخفاض RSI
                strength = max(10, min(70, (30 - rsi_val) * 2 + 40))
                signals.append({
                    'type': 'rsi_oversold',
                    'timestamp': timestamp,
                    'signal': 'شراء',
                    'description': f'RSI في منطقة التشبع البيعي ({rsi_val:.1f})',
                    'strength_percentage': strength
                })
            elif rsi_val >= 70:
                # حساب قوة الإشارة بناءً على مدى ارتفاع RSI
                strength = max(10, min(70, (rsi_val - 70) * 2 + 40))
                signals.append({
                    'type': 'rsi_overbought',
                    'timestamp': timestamp,
                    'signal': 'بيع',
                    'description': f'RSI في منطقة التشبع الشرائي ({rsi_val:.1f})',
                    'strength_percentage': strength
                })

        # ملاحظة: إشارات الشمعة الأخيرة تُضاف في get_all_signals()

        # البحث عن دايفرجنس RSI - الطريقة البسيطة (للتاريخ)
        try:
            rsi_simple_div = self.detect_simple_divergence(self.df['close'], self.df['rsi'])
            for div in rsi_simple_div:
                signal_type = 'شراء' if div['type'] == 'bullish_divergence' else 'بيع'
                signals.append({
                    'type': f"rsi_simple_{div['type']}",
                    'timestamp': div['timestamp'],
                    'signal': signal_type,
                    'description': f"RSI دايفرجنس {signal_type}",
                    'strength_percentage': 65.0  # قوة افتراضية للدايفرجنس البسيط
                })
        except Exception as e:
            print(f"خطأ في تحليل RSI البسيط: {e}")

        return signals

    def get_all_signals(self):
        """الحصول على جميع الإشارات"""
        all_signals = []

        # حساب جميع المؤشرات
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_obv()
        self.calculate_moving_averages()

        # جمع الإشارات التقليدية
        all_signals.extend(self.analyze_rsi_signals())
        all_signals.extend(self.analyze_ma_crossover())

        # إشارات الدايفرجنس الصحيحة (طريقة TradingView)
        try:
            tradingview_divergences = self.detect_tradingview_divergence()
            all_signals.extend(tradingview_divergences)
        except Exception as e:
            print(f"خطأ في تحليل الدايفرجنس: {e}")

        # إشارات MACD الدايفرجنس - الطريقة البسيطة (للتاريخ)
        try:
            macd_simple_div = self.detect_simple_divergence(self.df['close'], self.df['macd_histogram'])
            for div in macd_simple_div:
                signal_type = 'شراء' if div['type'] == 'bullish_divergence' else 'بيع'
                all_signals.append({
                    'type': f"macd_simple_{div['type']}",
                    'timestamp': div['timestamp'],
                    'signal': signal_type,
                    'description': f"MACD دايفرجنس {signal_type}",
                    'strength_percentage': 60.0  # قوة افتراضية للدايفرجنس البسيط
                })
        except Exception as e:
            print(f"خطأ في تحليل MACD البسيط: {e}")

        # إشارات OBV الدايفرجنس - الطريقة البسيطة (للتاريخ)
        try:
            obv_simple_div = self.detect_simple_divergence(self.df['close'], self.df['obv'])
            for div in obv_simple_div:
                signal_type = 'شراء' if div['type'] == 'bullish_divergence' else 'بيع'
                all_signals.append({
                    'type': f"obv_simple_{div['type']}",
                    'timestamp': div['timestamp'],
                    'signal': signal_type,
                    'description': f"OBV دايفرجنس {signal_type}",
                    'strength_percentage': 55.0  # قوة افتراضية للدايفرجنس البسيط
                })
        except Exception as e:
            print(f"خطأ في تحليل OBV البسيط: {e}")

        return sorted(all_signals, key=lambda x: x['timestamp'], reverse=True)
