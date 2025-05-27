import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

from crypto_analyzer import CryptoAnalyzer
from data_fetcher import DataFetcher

# إعداد الصفحة
st.set_page_config(
    page_title="محلل العملات الرقمية",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص للتصميم المحسن
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .buy-signal {
        background: linear-gradient(135deg, #4CAF50, #45a049) !important;
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
        border: none;
    }
    .sell-signal {
        background: linear-gradient(135deg, #f44336, #d32f2f) !important;
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 2px 4px rgba(244, 67, 54, 0.3);
        border: none;
    }
    .strength-bar {
        height: 20px;
        border-radius: 10px;
        background: linear-gradient(90deg, #ff4444 0%, #ffaa00 50%, #00aa00 100%);
        position: relative;
        overflow: hidden;
    }
    .strength-indicator {
        height: 100%;
        background: rgba(255,255,255,0.8);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    .auto-refresh {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
        cursor: pointer;
        font-weight: bold;
    }
    .last-update {
        color: #666;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # تخزين مؤقت لمدة 5 دقائق
def load_crypto_data(symbols, timeframes):
    """تحميل بيانات العملات مع التخزين المؤقت"""
    analyzer = CryptoAnalyzer()
    return analyzer.analyze_multiple_cryptos(symbols, timeframes)

@st.cache_data(ttl=600)  # تخزين مؤقت لمدة 10 دقائق
def get_available_symbols():
    """الحصول على قائمة العملات المتاحة"""
    fetcher = DataFetcher()
    return fetcher.get_available_symbols()

def create_strength_bar(strength_percentage):
    """إنشاء شريط قوة الإشارة"""
    color = "#ff4444" if strength_percentage < 30 else "#ffaa00" if strength_percentage < 70 else "#00aa00"
    return f"""
    <div style="width: 100%; background-color: #f0f0f0; border-radius: 10px; height: 20px;">
        <div style="width: {strength_percentage}%; background-color: {color}; height: 100%; border-radius: 10px;
                    display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold;">
            {strength_percentage:.0f}%
        </div>
    </div>
    """

def main():
    # العنوان الرئيسي
    st.markdown('<h1 class="main-header">📈 محلل العملات الرقمية المتقدم</h1>', unsafe_allow_html=True)
    st.markdown("### تحليل فني احترافي مع 40 عملة قيادية وإشارات الدايفرجنس الدقيقة")

    # إعدادات التحديث التلقائي
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        auto_refresh = st.checkbox("🔄 التحديث التلقائي كل ساعة", value=False)
    with col2:
        if st.button("🔄 تحديث الآن", type="primary"):
            st.cache_data.clear()
            st.rerun()
    with col3:
        st.markdown(f'<div class="last-update">آخر تحديث: {datetime.now().strftime("%H:%M:%S")}</div>',
                   unsafe_allow_html=True)

    # التحديث التلقائي
    if auto_refresh:
        time.sleep(3600)  # ساعة واحدة
        st.rerun()

    # الشريط الجانبي للإعدادات
    with st.sidebar:
        st.header("⚙️ إعدادات التحليل")

        # اختيار العملات
        st.subheader("اختيار العملات")
        try:
            available_symbols = get_available_symbols()
        except:
            available_symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'XRP/USDT']

        # خيار تحديد الكل
        select_all = st.checkbox("تحديد جميع العملات")

        if select_all:
            selected_symbols = available_symbols
        else:
            selected_symbols = st.multiselect(
                "اختر العملات للتحليل:",
                available_symbols,
                default=available_symbols[:5] if len(available_symbols) >= 5 else available_symbols
            )

        # اختيار الأطر الزمنية
        st.subheader("الأطر الزمنية")
        timeframe_options = {
            '1 ساعة': '1h',
            '2 ساعة': '2h',
            '3 ساعات': '3h',
            '4 ساعات': '4h',
            'يوم واحد': '1d',
            'أسبوع واحد': '1w'
        }

        selected_timeframes_display = st.multiselect(
            "اختر الأطر الزمنية:",
            list(timeframe_options.keys()),
            default=['4 ساعات', 'يوم واحد']
        )

        selected_timeframes = [timeframe_options[tf] for tf in selected_timeframes_display]

        # إعدادات الفلترة
        st.subheader("فلترة النتائج")

        signal_type_filter = st.selectbox(
            "نوع الإشارة:",
            ['الكل', 'شراء', 'بيع']
        )

        indicator_filter = st.selectbox(
            "المؤشر:",
            ['الكل', 'RSI', 'MACD', 'OBV', 'MA']
        )

        hours_back = st.slider(
            "عرض الإشارات من آخر (ساعة):",
            min_value=1,
            max_value=168,  # أسبوع
            value=24,
            step=1
        )

        # زر التحديث
        refresh_button = st.button("🔄 تحديث البيانات", type="primary")

    # التحقق من صحة الإدخال
    if not selected_symbols:
        st.warning("⚠️ يرجى اختيار عملة واحدة على الأقل")
        return

    if not selected_timeframes:
        st.warning("⚠️ يرجى اختيار إطار زمني واحد على الأقل")
        return

    # عرض حالة التحميل
    with st.spinner('🔍 جاري تحليل العملات...'):
        try:
            # تحميل البيانات
            signals_df = load_crypto_data(selected_symbols, selected_timeframes)

            if signals_df.empty:
                st.warning("❌ لم يتم العثور على إشارات للعملات المختارة")
                return

            # تطبيق الفلاتر
            analyzer = CryptoAnalyzer()
            filtered_signals = analyzer.filter_signals(
                signals_df,
                signal_type_filter=signal_type_filter if signal_type_filter != 'الكل' else None,
                indicator_filter=indicator_filter if indicator_filter != 'الكل' else None,
                hours_back=hours_back
            )

            # عرض الإحصائيات
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("إجمالي الإشارات", len(filtered_signals))

            with col2:
                buy_signals = len(filtered_signals[filtered_signals['نوع الإشارة'] == 'شراء'])
                st.metric("إشارات الشراء", buy_signals, delta=None)

            with col3:
                sell_signals = len(filtered_signals[filtered_signals['نوع الإشارة'] == 'بيع'])
                st.metric("إشارات البيع", sell_signals, delta=None)

            with col4:
                unique_coins = filtered_signals['العملة'].nunique()
                st.metric("العملات النشطة", unique_coins)

            # عرض الجدول الرئيسي المحسن
            st.subheader("📊 جدول الإشارات المتقدم")

            if not filtered_signals.empty:
                # إضافة عمود قوة الإشارة إذا لم يكن موجوداً
                if 'قوة الإشارة' not in filtered_signals.columns:
                    # إضافة قوة افتراضية للإشارات القديمة
                    filtered_signals['قوة الإشارة'] = 50.0

                # تنسيق الجدول مع الألوان المحسنة
                def highlight_signals(val):
                    if val == 'شراء':
                        return 'background: linear-gradient(135deg, #4CAF50, #45a049); color: white; font-weight: bold; text-align: center; padding: 8px; border-radius: 5px;'
                    elif val == 'بيع':
                        return 'background: linear-gradient(135deg, #f44336, #d32f2f); color: white; font-weight: bold; text-align: center; padding: 8px; border-radius: 5px;'
                    return ''

                def highlight_strength(val):
                    try:
                        strength = float(val)
                        if strength >= 70:
                            return 'background-color: #4CAF50; color: white; font-weight: bold; text-align: center; padding: 5px; border-radius: 3px;'
                        elif strength >= 40:
                            return 'background-color: #FF9800; color: white; font-weight: bold; text-align: center; padding: 5px; border-radius: 3px;'
                        else:
                            return 'background-color: #f44336; color: white; font-weight: bold; text-align: center; padding: 5px; border-radius: 3px;'
                    except:
                        return ''

                # تطبيق التنسيق
                styled_df = filtered_signals.style.map(
                    highlight_signals, subset=['نوع الإشارة']
                )

                if 'قوة الإشارة' in filtered_signals.columns:
                    styled_df = styled_df.map(
                        highlight_strength, subset=['قوة الإشارة']
                    )

                # عرض الجدول
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=500,
                    column_config={
                        "قوة الإشارة": st.column_config.ProgressColumn(
                            "قوة الإشارة %",
                            help="قوة الإشارة من 0 إلى 100%",
                            min_value=0,
                            max_value=100,
                        ),
                        "نوع الإشارة": st.column_config.TextColumn(
                            "نوع الإشارة",
                            help="نوع الإشارة: شراء أو بيع",
                            width="medium"
                        )
                    }
                )

                # عرض إحصائيات قوة الإشارات
                if 'قوة الإشارة' in filtered_signals.columns:
                    st.subheader("📈 إحصائيات قوة الإشارات")
                    col1, col2, col3, col4 = st.columns(4)

                    avg_strength = filtered_signals['قوة الإشارة'].mean()
                    strong_signals = len(filtered_signals[filtered_signals['قوة الإشارة'] >= 70])
                    medium_signals = len(filtered_signals[(filtered_signals['قوة الإشارة'] >= 40) & (filtered_signals['قوة الإشارة'] < 70)])
                    weak_signals = len(filtered_signals[filtered_signals['قوة الإشارة'] < 40])

                    with col1:
                        st.metric("متوسط القوة", f"{avg_strength:.1f}%")
                    with col2:
                        st.metric("إشارات قوية", strong_signals, delta=f"{strong_signals/len(filtered_signals)*100:.1f}%")
                    with col3:
                        st.metric("إشارات متوسطة", medium_signals, delta=f"{medium_signals/len(filtered_signals)*100:.1f}%")
                    with col4:
                        st.metric("إشارات ضعيفة", weak_signals, delta=f"{weak_signals/len(filtered_signals)*100:.1f}%")

                # إحصائيات إضافية
                st.subheader("📈 تحليل الإشارات")

                col1, col2 = st.columns(2)

                with col1:
                    # توزيع الإشارات حسب العملة
                    coin_distribution = filtered_signals['العملة'].value_counts()
                    if not coin_distribution.empty:
                        fig_coins = px.bar(
                            x=coin_distribution.index,
                            y=coin_distribution.values,
                            title="توزيع الإشارات حسب العملة",
                            labels={'x': 'العملة', 'y': 'عدد الإشارات'}
                        )
                        fig_coins.update_layout(height=400)
                        st.plotly_chart(fig_coins, use_container_width=True)

                with col2:
                    # توزيع الإشارات حسب المؤشر
                    indicator_distribution = filtered_signals['المؤشر'].value_counts()
                    if not indicator_distribution.empty:
                        fig_indicators = px.pie(
                            values=indicator_distribution.values,
                            names=indicator_distribution.index,
                            title="توزيع الإشارات حسب المؤشر"
                        )
                        fig_indicators.update_layout(height=400)
                        st.plotly_chart(fig_indicators, use_container_width=True)

                # تصدير البيانات
                st.subheader("💾 تصدير البيانات")

                col1, col2 = st.columns(2)

                with col1:
                    csv = filtered_signals.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 تحميل كملف CSV",
                        data=csv,
                        file_name=f"crypto_signals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )

                with col2:
                    json_data = filtered_signals.to_json(orient='records', force_ascii=False)
                    st.download_button(
                        label="📥 تحميل كملف JSON",
                        data=json_data,
                        file_name=f"crypto_signals_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )

            else:
                st.info("ℹ️ لا توجد إشارات تطابق المعايير المحددة")

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء تحليل البيانات: {str(e)}")
            st.info("💡 تأكد من اتصالك بالإنترنت وحاول مرة أخرى")

    # معلومات إضافية
    with st.expander("ℹ️ معلومات حول المؤشرات"):
        st.markdown("""
        **المؤشرات المستخدمة في التحليل:**

        - **RSI (مؤشر القوة النسبية)**: يقيس قوة حركة السعر
          - تشبع شرائي: أعلى من 70
          - تشبع بيعي: أقل من 30

        - **MACD**: يقيس العلاقة بين متوسطين متحركين

        - **OBV (حجم التداول المتوازن)**: يربط بين السعر وحجم التداول

        - **المتوسطات المتحركة**: تقاطع MA9 مع MA20

        - **الدايفرجنس**: اختلاف اتجاه السعر عن المؤشر
        """)

    # تحديث تلقائي
    st.markdown("---")
    st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
