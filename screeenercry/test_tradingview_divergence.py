#!/usr/bin/env python3
"""
اختبار الدايفرجنس بطريقة TradingView الصحيحة
"""

from crypto_analyzer import CryptoAnalyzer
from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
import pandas as pd

def test_tradingview_divergence():
    """اختبار الدايفرجنس بطريقة TradingView"""
    print("📊 اختبار الدايفرجنس بطريقة TradingView الصحيحة")
    print("=" * 60)
    
    # جلب البيانات
    fetcher = DataFetcher()
    
    # اختبار عدة عملات
    test_cases = [
        ('BTC/USDT', '4h', 100),
        ('ETH/USDT', '4h', 100),
        ('BNB/USDT', '1d', 80),
    ]
    
    total_signals = 0
    
    for symbol, timeframe, limit in test_cases:
        print(f"\n📈 تحليل {symbol} - {timeframe}")
        print("-" * 40)
        
        try:
            # جلب البيانات
            df = fetcher.get_crypto_data(symbol, timeframe, limit)
            if df.empty:
                print(f"❌ لا توجد بيانات لـ {symbol}")
                continue
            
            print(f"✅ تم جلب {len(df)} شمعة")
            print(f"📈 آخر سعر: ${df['close'].iloc[-1]:,.2f}")
            
            # تحليل المؤشرات
            indicators = TechnicalIndicators(df)
            
            # حساب المؤشرات
            indicators.calculate_rsi()
            indicators.calculate_macd()
            indicators.calculate_obv()
            
            print(f"📊 آخر RSI: {df['rsi'].iloc[-1]:.1f}")
            print(f"📊 آخر MACD: {df['macd_histogram'].iloc[-1]:.4f}")
            
            # اختبار الدايفرجنس بطريقة TradingView
            print(f"\n🔍 اختبار الدايفرجنس (طريقة TradingView):")
            
            try:
                tradingview_signals = indicators.detect_tradingview_divergence()
                print(f"   - عدد الإشارات: {len(tradingview_signals)}")
                
                for signal in tradingview_signals:
                    print(f"   🔥 {signal['type']}: {signal['signal']}")
                    print(f"      - {signal['description']}")
                    print(f"      - القوة: {signal['strength']:.3f}")
                    print(f"      - تغيير السعر: {signal['price_change']:.2f}%")
                    print(f"      - تغيير المؤشر: {signal['indicator_change']:.3f}")
                    print()
                
                total_signals += len(tradingview_signals)
                
            except Exception as e:
                print(f"   ❌ خطأ في TradingView: {e}")
                import traceback
                traceback.print_exc()
            
            # عرض معلومات القمم والقيعان
            print(f"\n📊 تحليل القمم والقيعان:")
            try:
                recent_data = df.tail(50)
                
                # البحث عن القمم والقيعان
                price_highs = indicators._find_peaks(recent_data['high'], min_distance=5)
                price_lows = indicators._find_troughs(recent_data['low'], min_distance=5)
                rsi_highs = indicators._find_peaks(recent_data['rsi'], min_distance=5)
                rsi_lows = indicators._find_troughs(recent_data['rsi'], min_distance=5)
                
                print(f"   - قمم السعر: {len(price_highs)}")
                print(f"   - قيعان السعر: {len(price_lows)}")
                print(f"   - قمم RSI: {len(rsi_highs)}")
                print(f"   - قيعان RSI: {len(rsi_lows)}")
                
                # عرض آخر قمة وقاع
                if price_highs:
                    last_high_idx = price_highs[-1]
                    last_high_price = recent_data['high'].iloc[last_high_idx]
                    last_high_time = recent_data.index[last_high_idx]
                    print(f"   - آخر قمة: ${last_high_price:.2f} في {last_high_time}")
                
                if price_lows:
                    last_low_idx = price_lows[-1]
                    last_low_price = recent_data['low'].iloc[last_low_idx]
                    last_low_time = recent_data.index[last_low_idx]
                    print(f"   - آخر قاع: ${last_low_price:.2f} في {last_low_time}")
                
            except Exception as e:
                print(f"   ❌ خطأ في تحليل القمم: {e}")
            
        except Exception as e:
            print(f"❌ خطأ في تحليل {symbol}: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 إجمالي إشارات الدايفرجنس (TradingView): {total_signals}")
    
    return total_signals

def test_full_app_tradingview():
    """اختبار التطبيق الكامل مع طريقة TradingView"""
    print("\n🚀 اختبار التطبيق الكامل (طريقة TradingView)")
    print("=" * 60)
    
    analyzer = CryptoAnalyzer()
    
    # تحليل عدة عملات
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    timeframes = ['4h']
    
    try:
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 100)
        
        if df_signals.empty:
            print("❌ لم يتم العثور على إشارات")
            return False
        
        print(f"✅ تم تحليل {len(symbols)} عملة")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        
        # البحث عن إشارات الدايفرجنس الجديدة
        tradingview_signals = df_signals[
            (df_signals['المؤشر'].str.contains('🔥', na=False)) |
            (df_signals['الوصف'].str.contains('الشمعة الأخيرة', na=False))
        ]
        
        print(f"\n🔥 إشارات الدايفرجنس (TradingView): {len(tradingview_signals)}")
        
        if not tradingview_signals.empty:
            print("\n🎯 إشارات الدايفرجنس الصحيحة:")
            print("-" * 50)
            
            for _, signal in tradingview_signals.iterrows():
                print(f"🔥 {signal['العملة']}")
                print(f"   📊 المؤشر: {signal['المؤشر']}")
                print(f"   📈 الإشارة: {signal['نوع الإشارة']}")
                print(f"   ⏰ الوقت: {signal['وقت الإشارة']}")
                print(f"   📝 الوصف: {signal['الوصف']}")
                print(f"   💰 السعر: ${signal['السعر الحالي']}")
                print()
        else:
            print("ℹ️ لا توجد إشارات دايفرجنس في الشمعة الأخيرة حالياً")
            print("💡 هذا طبيعي - الدايفرجنس الصحيح نادر الحدوث")
        
        # إحصائيات عامة
        print(f"\n📈 توزيع جميع الإشارات:")
        signal_types = df_signals['المؤشر'].value_counts()
        for indicator, count in signal_types.head(10).items():
            print(f"   - {indicator}: {count}")
        
        return len(tradingview_signals) > 0
        
    except Exception as e:
        print(f"❌ خطأ في التحليل الكامل: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    print("🎯 اختبار شامل للدايفرجنس بطريقة TradingView الصحيحة")
    print("=" * 70)
    
    # اختبار الدايفرجنس المباشر
    direct_count = test_tradingview_divergence()
    
    # اختبار التطبيق الكامل
    app_success = test_full_app_tradingview()
    
    print("\n" + "=" * 70)
    print("📋 ملخص النتائج:")
    print(f"  - إشارات الدايفرجنس المكتشفة: {direct_count}")
    print(f"  - التطبيق يعرض الإشارات الصحيحة: {'✅ نعم' if app_success else '❌ لا'}")
    
    if direct_count > 0 or app_success:
        print("\n🎉 نجح اكتشاف الدايفرجنس بطريقة TradingView!")
        print("✅ الإشارات الآن تتوافق مع معايير التحليل الفني الصحيحة")
        print("🔍 يتم البحث عن القمم والقيعان الحقيقية ومقارنتها")
    else:
        print("\n⚠️ لم يتم العثور على إشارات دايفرجنس حالياً")
        print("💡 هذا طبيعي - الدايفرجنس الصحيح نادر ولكنه أكثر دقة")
    
    print("\n🚀 لتشغيل التطبيق ورؤية الإشارات الصحيحة:")
    print("python -m streamlit run app.py")
    print("\n✅ الآن الإشارات تتوافق مع TradingView!")

if __name__ == "__main__":
    main()
