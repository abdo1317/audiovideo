#!/usr/bin/env python3
"""
اختبار إشارات الدايفرجنس في الشمعة الأخيرة
"""

from crypto_analyzer import CryptoAnalyzer
from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
import pandas as pd
from datetime import datetime

def test_latest_candle_divergence():
    """اختبار إشارات الدايفرجنس في الشمعة الأخيرة"""
    print("🔥 اختبار إشارات الدايفرجنس في الشمعة الأخيرة")
    print("=" * 60)

    # جلب البيانات
    fetcher = DataFetcher()

    # اختبار عدة عملات وأطر زمنية
    test_cases = [
        ('BTC/USDT', '4h', 100),
        ('ETH/USDT', '4h', 100),
        ('BNB/USDT', '1d', 50),
        ('ADA/USDT', '4h', 100),
    ]

    total_latest_signals = 0

    for symbol, timeframe, limit in test_cases:
        print(f"\n📊 تحليل {symbol} - {timeframe}")
        print("-" * 40)

        try:
            # جلب البيانات
            df = fetcher.get_crypto_data(symbol, timeframe, limit)
            if df.empty:
                print(f"❌ لا توجد بيانات لـ {symbol}")
                continue

            print(f"✅ تم جلب {len(df)} شمعة")

            # تحليل المؤشرات
            indicators = TechnicalIndicators(df)

            # حساب المؤشرات
            indicators.calculate_rsi()
            indicators.calculate_macd()
            indicators.calculate_obv()

            # معلومات الشمعة الأخيرة
            last_candle = df.iloc[-1]
            print(f"📈 الشمعة الأخيرة:")
            print(f"   - الوقت: {last_candle.name}")
            print(f"   - السعر: ${last_candle['close']:,.2f}")

            # التحقق من وجود المؤشرات
            if 'rsi' in df.columns:
                print(f"   - RSI: {last_candle['rsi']:.1f}")
            if 'macd_histogram' in df.columns:
                print(f"   - MACD Histogram: {last_candle['macd_histogram']:.4f}")
            if 'obv' in df.columns:
                print(f"   - OBV: {last_candle['obv']:,.0f}")

            # اختبار الدايفرجنس في الشمعة الأخيرة
            latest_signals = 0

            # RSI الدايفرجنس - الشمعة الأخيرة
            print(f"\n🔍 RSI الدايفرجنس (الشمعة الأخيرة):")
            try:
                rsi_latest = indicators.detect_latest_divergence(df['close'], df['rsi'])
                print(f"   - عدد الإشارات: {len(rsi_latest)}")

                for div in rsi_latest:
                    print(f"   ✅ {div['type']}: {div['signal']}")
                    print(f"      - {div['description']}")
                    print(f"      - القوة: {div['strength']:.3f}")
                    print(f"      - مقارنة مع {div['periods_back']} فترات سابقة")

                latest_signals += len(rsi_latest)

            except Exception as e:
                print(f"   ❌ خطأ: {e}")

            # MACD الدايفرجنس - الشمعة الأخيرة
            print(f"\n🔍 MACD الدايفرجنس (الشمعة الأخيرة):")
            try:
                macd_latest = indicators.detect_latest_divergence(df['close'], df['macd_histogram'])
                print(f"   - عدد الإشارات: {len(macd_latest)}")

                for div in macd_latest:
                    print(f"   ✅ {div['type']}: {div['signal']}")
                    print(f"      - {div['description']}")
                    print(f"      - القوة: {div['strength']:.3f}")
                    print(f"      - مقارنة مع {div['periods_back']} فترات سابقة")

                latest_signals += len(macd_latest)

            except Exception as e:
                print(f"   ❌ خطأ: {e}")

            # OBV الدايفرجنس - الشمعة الأخيرة
            print(f"\n🔍 OBV الدايفرجنس (الشمعة الأخيرة):")
            try:
                obv_latest = indicators.detect_latest_divergence(df['close'], df['obv'])
                print(f"   - عدد الإشارات: {len(obv_latest)}")

                for div in obv_latest:
                    print(f"   ✅ {div['type']}: {div['signal']}")
                    print(f"      - {div['description']}")
                    print(f"      - القوة: {div['strength']:.3f}")
                    print(f"      - مقارنة مع {div['periods_back']} فترات سابقة")

                latest_signals += len(obv_latest)

            except Exception as e:
                print(f"   ❌ خطأ: {e}")

            print(f"\n📊 إجمالي إشارات الشمعة الأخيرة لـ {symbol}: {latest_signals}")
            total_latest_signals += latest_signals

        except Exception as e:
            print(f"❌ خطأ في تحليل {symbol}: {e}")

    print("\n" + "=" * 60)
    print(f"🎯 إجمالي إشارات الدايفرجنس في الشمعة الأخيرة: {total_latest_signals}")

    return total_latest_signals

def test_full_app_latest_signals():
    """اختبار التطبيق الكامل للإشارات الحديثة"""
    print("\n🚀 اختبار التطبيق الكامل للإشارات الحديثة")
    print("=" * 60)

    analyzer = CryptoAnalyzer()

    # تحليل عدة عملات
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    timeframes = ['4h']  # التركيز على 4 ساعات للحصول على إشارات حديثة

    try:
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 100)

        if df_signals.empty:
            print("❌ لم يتم العثور على إشارات")
            return False

        print(f"✅ تم تحليل {len(symbols)} عملة على إطار {timeframes[0]}")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")

        # البحث عن إشارات الشمعة الأخيرة
        latest_signals = df_signals[df_signals['المؤشر'].str.contains('الشمعة الأخيرة', na=False)]

        print(f"\n🔥 إشارات الشمعة الأخيرة: {len(latest_signals)}")

        if not latest_signals.empty:
            print("\n🎯 إشارات الدايفرجنس في الشمعة الأخيرة:")
            print("-" * 50)

            for _, signal in latest_signals.iterrows():
                print(f"🔥 {signal['العملة']}")
                print(f"   📊 المؤشر: {signal['المؤشر']}")
                print(f"   📈 الإشارة: {signal['نوع الإشارة']}")
                print(f"   ⏰ الوقت: {signal['وقت الإشارة']}")
                print(f"   📝 الوصف: {signal['الوصف']}")
                print(f"   💰 السعر: ${signal['السعر الحالي']}")
                print()

        # إحصائيات الإشارات الحديثة
        if not latest_signals.empty:
            buy_latest = len(latest_signals[latest_signals['نوع الإشارة'] == 'شراء'])
            sell_latest = len(latest_signals[latest_signals['نوع الإشارة'] == 'بيع'])

            print(f"📈 إشارات الشراء (الشمعة الأخيرة): {buy_latest}")
            print(f"📉 إشارات البيع (الشمعة الأخيرة): {sell_latest}")

            # توزيع حسب المؤشر
            indicator_dist = latest_signals['المؤشر'].value_counts()
            print(f"\n📊 توزيع إشارات الشمعة الأخيرة:")
            for indicator, count in indicator_dist.items():
                print(f"   - {indicator}: {count}")

        return len(latest_signals) > 0

    except Exception as e:
        print(f"❌ خطأ في التحليل الكامل: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🎯 اختبار شامل لإشارات الدايفرجنس في الشمعة الأخيرة")
    print("=" * 70)

    # اختبار الدايفرجنس في الشمعة الأخيرة
    latest_count = test_latest_candle_divergence()

    # اختبار التطبيق الكامل
    app_success = test_full_app_latest_signals()

    print("\n" + "=" * 70)
    print("📋 ملخص النتائج:")
    print(f"  - إشارات الشمعة الأخيرة المكتشفة: {latest_count}")
    print(f"  - التطبيق يعرض الإشارات الحديثة: {'✅ نعم' if app_success else '❌ لا'}")

    if latest_count > 0 or app_success:
        print("\n🎉 نجح اكتشاف إشارات الدايفرجنس في الشمعة الأخيرة!")
        print("💡 ابحث عن الإشارات المميزة بـ 🔥 في التطبيق")
        print("🔍 هذه الإشارات تظهر الدايفرجنس الذي يتشكل الآن")
    else:
        print("\n⚠️ لم يتم العثور على إشارات في الشمعة الأخيرة حالياً")
        print("💡 جرب أطر زمنية مختلفة أو عملات أخرى")

    print("\n🚀 لتشغيل التطبيق ورؤية الإشارات الحديثة:")
    print("python -m streamlit run app.py")
    print("\n🔥 ابحث عن الإشارات التي تحتوي على '(الشمعة الأخيرة)' في الجدول")

if __name__ == "__main__":
    main()
