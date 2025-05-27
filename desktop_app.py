import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
import pandas as pd
import ccxt
import plotly.graph_objs as go
from plotly.offline import plot
import webbrowser
import ta

# --- إعداد منصة Binance ---
try:
    exchange = ccxt.binance({
        'options': {'defaultType': 'spot'},
        'enableRateLimit': True
    })
    exchange.load_markets()
except Exception as e:
    print(f"خطأ في الاتصال بمنصة Binance: {e}")
    sys.exit(1)

# --- دالة لجلب البيانات ---
def get_ohlcv_data(symbol, timeframe, limit=150):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        return None

timeframes = ['15m', '1h', '4h', '1d', '1w']

class MainWindow(QMainWindow):
    def __init__(self):
        print("[DEBUG] بدأ __init__ MainWindow")
        super().__init__()
        self.setWindowTitle("محلل العملات الرقمية - سطح المكتب")
        self.setGeometry(100, 100, 900, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # --- إشعار الدايفرجنس أعلى النافذة ---
        self.divergence_label = QLabel("")
        self.divergence_label.setAlignment(Qt.AlignCenter)
        self.divergence_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.divergence_label)

        # --- إشعار التقاطع التشخيصي ---
        self.cross_label = QLabel("")
        self.cross_label.setAlignment(Qt.AlignCenter)
        self.cross_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #005;")
        self.layout.addWidget(self.cross_label)

        # --- إشعار الدايفرجنس التشخيصي ---
        self.div_debug_label = QLabel("")
        self.div_debug_label.setAlignment(Qt.AlignCenter)
        self.div_debug_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #500;")
        self.layout.addWidget(self.div_debug_label)

        # --- عناصر الواجهة ---
        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.symbol_label = QLabel("اختر العملة:")
        self.top_layout.addWidget(self.symbol_label)
        self.symbol_combo = QComboBox()
        self.top_layout.addWidget(self.symbol_combo)

        self.tf_label = QLabel("الإطار الزمني:")
        self.top_layout.addWidget(self.tf_label)
        self.tf_combo = QComboBox()
        self.tf_combo.addItems(timeframes)
        self.top_layout.addWidget(self.tf_combo)

        self.refresh_btn = QPushButton("تحديث البيانات")
        self.refresh_btn.clicked.connect(self.load_data)
        self.top_layout.addWidget(self.refresh_btn)

        # --- جدول البيانات ---
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # --- زر عرض الرسم البياني ---
        self.plot_btn = QPushButton("عرض الرسم البياني")
        self.plot_btn.clicked.connect(self.show_plot)
        self.layout.addWidget(self.plot_btn)

        # --- تحميل قائمة العملات ---
        print("[DEBUG] قبل load_symbols")
        self.load_symbols()
        print("[DEBUG] بعد load_symbols")
        self.df = None

    def load_symbols(self):
        print("[DEBUG] بدأ load_symbols")
        try:
            markets = exchange.load_markets()
            print(f"[DEBUG] عدد الأسواق المحملة: {len(markets)}")
            symbols = [s for s in markets if s.endswith('/USDT')]
            print(f"[DEBUG] عدد الرموز المضافة: {len(symbols)}")
            self.symbol_combo.addItems(symbols)
        except Exception as e:
            print(f"[DEBUG] خطأ في جلب العملات: {e}")

    def load_data(self):
        print("[DEBUG] بدأ load_data")
        symbol = self.symbol_combo.currentText()
        tf = self.tf_combo.currentText()
        print(f"[DEBUG] العملة المختارة: {symbol}, الإطار الزمني: {tf}")
        df = get_ohlcv_data(symbol, tf)
        if df is None or df.empty:
            print("[DEBUG] تعذر جلب بيانات الأسعار أو البيانات فارغة")
            QMessageBox.warning(self, "خطأ", "تعذر جلب بيانات الأسعار. تأكد من الاتصال بالإنترنت أو جرب عملة أخرى.")
            return
        print(f"[DEBUG] تم جلب البيانات بعدد صفوف: {len(df)}")
        # حساب المؤشرات الفنية
        df['ma9'] = ta.trend.SMAIndicator(df['close'], window=9).sma_indicator()
        df['ma20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
        df['obv'] = ta.volume.OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
        df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx()
        print("[DEBUG] تم حساب المؤشرات الفنية")
        # إشعارات تقاطع MA9/MA20 إذا كان ADX قوي
        cross = self.detect_ma_cross(df)
        adx_val = df['adx'].iloc[-1]
        # إشعار الدايفرجنس في واجهة التطبيق (بدون نافذة منبثقة)
        rsi_div = self.detect_rsi_divergence(df)
        obv_div = self.detect_obv_divergence(df)
        # إشعار تشخيصي دائم لنتيجة الدايفرجنس
        div_text = ""
        if rsi_div:
            self.divergence_label.setText(f"إشارة دايفرجنس RSI: {rsi_div}")
            self.divergence_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
            div_text = f"نتيجة دالة الدايفرجنس RSI: {rsi_div}"
        elif obv_div:
            self.divergence_label.setText(f"إشارة دايفرجنس OBV: {obv_div}")
            self.divergence_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
            div_text = f"نتيجة دالة الدايفرجنس OBV: {obv_div}"
        else:
            self.divergence_label.setText("")
            div_text = "لا يوجد دايفرجنس RSI أو OBV في آخر الشموع"
        self.div_debug_label.setText(div_text)
        self.div_debug_label.setStyleSheet("color: #500; font-size: 14px; font-weight: bold;")
        # إشعار التشخيص لحالة التقاطع
        cross = self.detect_ma_cross(df)
        if cross:
            self.cross_label.setText(f"نتيجة دالة التقاطع: {cross}")
            self.cross_label.setStyleSheet("color: blue; font-size: 14px; font-weight: bold;")
        else:
            self.cross_label.setText("لا يوجد تقاطع بين MA9 وMA20 في آخر شمعتين")
            self.cross_label.setStyleSheet("color: gray; font-size: 14px; font-weight: bold;")
        adx_val = df['adx'].iloc[-1]
        # باقي الإشعارات كما هي (تقاطع MA9/MA20 مع ADX قوي)
        if cross and adx_val > 25:
            QMessageBox.information(
                self,
                "إشارة تقاطع MA9/MA20 (مع ADX قوي)",
                cross + f"\nقوة الترند (ADX): {adx_val:.2f}"
            )
        self.df = df
        self.show_table(df)

    def show_table(self, df):
        # عرض آخر 30 صف فقط لتسهيل القراءة
        show_df = df.tail(30)
        self.table.setRowCount(len(show_df))
        self.table.setColumnCount(len(show_df.columns))
        self.table.setHorizontalHeaderLabels(show_df.columns)
        for i in range(len(show_df)):
            for j, col in enumerate(show_df.columns):
                val = show_df.iloc[i, j]
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
        self.table.resizeColumnsToContents()

    def show_plot(self):
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "خطأ", "لا توجد بيانات لعرضها.")
            return
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=self.df['timestamp'],
            open=self.df['open'],
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            name='Candlesticks'))
        fig.update_layout(title=f"الرسم البياني لـ {self.symbol_combo.currentText()}", xaxis_title='الوقت', yaxis_title='السعر')
        html = plot(fig, output_type='div', include_plotlyjs='cdn')
        # حفظ الرسم في ملف مؤقت وفتحه في المتصفح الافتراضي
        with open('temp_chart.html', 'w', encoding='utf-8') as f:
            f.write(html)
        webbrowser.open_new_tab('temp_chart.html')

    def detect_ma_cross(self, df):
        # إشعار تقاطع MA9/MA20 (آخر تقاطع فقط)
        signal = None
        if len(df) < 21:
            return None
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        # تقاطع صاعد
        if prev['ma9'] < prev['ma20'] and curr['ma9'] >= curr['ma20']:
            signal = f"تقاطع صاعد: MA9 اخترق MA20 لأعلى عند {curr['close']:.2f}"
        # تقاطع هابط
        elif prev['ma9'] > prev['ma20'] and curr['ma9'] <= curr['ma20']:
            signal = f"تقاطع هابط: MA9 كسر MA20 لأسفل عند {curr['close']:.2f}"
        return signal

    def detect_rsi_divergence(self, df):
        # إشعار دايفرجنس RSI (بسيط: السعر يصعد وRSI يهبط أو العكس في آخر 7 شموع)
        if len(df) < 15:
            return None
        price_trend = df['close'].iloc[-7:].mean() - df['close'].iloc[-14:-7].mean()
        rsi_trend = df['rsi'].iloc[-7:].mean() - df['rsi'].iloc[-14:-7].mean()
        if price_trend > 0 and rsi_trend < 0:
            return "دايفرجنس سلبي: السعر يصعد وRSI يهبط (احذر من انعكاس محتمل)"
        elif price_trend < 0 and rsi_trend > 0:
            return "دايفرجنس إيجابي: السعر يهبط وRSI يصعد (قد يكون هناك صعود قادم)"
        return None

    def detect_obv_divergence(self, df):
        # إشعار دايفرجنس OBV (بسيط: السعر يصعد وOBV يهبط أو العكس في آخر 7 شموع)
        if len(df) < 15:
            return None
        price_trend = df['close'].iloc[-7:].mean() - df['close'].iloc[-14:-7].mean()
        obv_trend = df['obv'].iloc[-7:].mean() - df['obv'].iloc[-14:-7].mean()
        if price_trend > 0 and obv_trend < 0:
            return "دايفرجنس سلبي: السعر يصعد وOBV يهبط (احذر من انعكاس محتمل)"
        elif price_trend < 0 and obv_trend > 0:
            return "دايفرجنس إيجابي: السعر يهبط وOBV يصعد (قد يكون هناك صعود قادم)"
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
