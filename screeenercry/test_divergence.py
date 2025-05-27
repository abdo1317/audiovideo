#!/usr/bin/env python3
"""
اختبار مخصص لإشارات الدايفرجنس
"""

from crypto_analyzer import CryptoAnalyzer
from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
import pandas as pd

def test_divergence_detection():
    """اختبار اكتشاف الدايفرجنس بالتفصيل"""
    print("🔍 اختبار اكتشاف الدايفرجنس...")
    print("=" * 50)
    
    # جلب البيانات
    fetcher = DataFetcher()
    
    # اختبار عدة عملات وأطر زمنية
    test_cases = [
        ('BTC/USDT', '4h', 200),
        ('ETH/USDT', '1d', 100),
        ('BNB/USDT', '4h', 150),
    ]
    
    total_divergences = 0
    
    for symbol, timeframe, limit in test_cases:
        print(f"\n📊 تحليل {symbol} - {timeframe}")
        print("-" * 30)
        
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
            
            print(f"📈 آخر سعر: ${df['close'].iloc[-1]:,.2f}")
            print(f"📊 آخر RSI: {df['rsi'].iloc[-1]:.1f}")
            
            # اختبار الدايفرجنس لكل مؤشر
            divergence_count = 0
            
            # RSI الدايفرجنس
            print("\n🔍 RSI الدايفرجنس:")
            try:
                rsi_div = indicators.detect_divergence(df['close'], df['rsi'])
                rsi_simple = indicators.detect_simple_divergence(df['close'], df['rsi'])
                
                print(f"  - الطريقة المتقدمة: {len(rsi_div)} إشارة")
                print(f"  - الطريقة البسيطة: {len(rsi_simple)} إشارة")
                
                for div in rsi_div[-3:]:  # آخر 3 إشارات
                    print(f"    * {div['type']} في {div['timestamp']} (قوة: {div.get('strength', 0):.2f})")
                
                divergence_count += len(rsi_div) + len(rsi_simple)
                
            except Exception as e:
                print(f"    ❌ خطأ: {e}")
            
            # MACD الدايفرجنس
            print("\n🔍 MACD الدايفرجنس:")
            try:
                macd_div = indicators.detect_divergence(df['close'], df['macd_histogram'])
                macd_simple = indicators.detect_simple_divergence(df['close'], df['macd_histogram'])
                
                print(f"  - الطريقة المتقدمة: {len(macd_div)} إشارة")
                print(f"  - الطريقة البسيطة: {len(macd_simple)} إشارة")
                
                for div in macd_div[-3:]:
                    print(f"    * {div['type']} في {div['timestamp']} (قوة: {div.get('strength', 0):.2f})")
                
                divergence_count += len(macd_div) + len(macd_simple)
                
            except Exception as e:
                print(f"    ❌ خطأ: {e}")
            
            # OBV الدايفرجنس
            print("\n🔍 OBV الدايفرجنس:")
            try:
                obv_div = indicators.detect_divergence(df['close'], df['obv'])
                obv_simple = indicators.detect_simple_divergence(df['close'], df['obv'])
                
                print(f"  - الطريقة المتقدمة: {len(obv_div)} إشارة")
                print(f"  - الطريقة البسيطة: {len(obv_simple)} إشارة")
                
                for div in obv_div[-3:]:
                    print(f"    * {div['type']} في {div['timestamp']} (قوة: {div.get('strength', 0):.2f})")
                
                divergence_count += len(obv_div) + len(obv_simple)
                
            except Exception as e:
                print(f"    ❌ خطأ: {e}")
            
            print(f"\n📊 إجمالي إشارات الدايفرجنس لـ {symbol}: {divergence_count}")
            total_divergences += divergence_count
            
        except Exception as e:
            print(f"❌ خطأ في تحليل {symbol}: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 إجمالي إشارات الدايفرجنس المكتشفة: {total_divergences}")
    
    if total_divergences > 0:
        print("✅ تم اكتشاف إشارات الدايفرجنس بنجاح!")
    else:
        print("⚠️ لم يتم اكتشاف إشارات دايفرجنس - قد تحتاج لتعديل المعايير")
    
    return total_divergences > 0

def test_full_analysis():
    """اختبار التحليل الكامل مع الدايفرجنس"""
    print("\n🚀 اختبار التحليل الكامل...")
    print("=" * 50)
    
    analyzer = CryptoAnalyzer()
    
    # تحليل عدة عملات
    symbols = ['BTC/USDT', 'ETH/USDT']
    timeframes = ['4h', '1d']
    
    try:
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 150)
        
        if df_signals.empty:
            print("❌ لم يتم العثور على إشارات")
            return False
        
        print(f"✅ تم تحليل {len(symbols)} عملة على {len(timeframes)} إطار زمني")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        
        # تصنيف الإشارات
        signal_types = df_signals['المؤشر'].value_counts()
        print("\n📈 توزيع الإشارات:")
        for indicator, count in signal_types.items():
            print(f"  - {indicator}: {count} إشارة")
        
        # البحث عن إشارات الدايفرجنس
        divergence_signals = df_signals[df_signals['المؤشر'].str.contains('دايفرجنس', na=False)]
        
        print(f"\n🎯 إشارات الدايفرجنس المكتشفة: {len(divergence_signals)}")
        
        if not divergence_signals.empty:
            print("\n🔍 أحدث إشارات الدايفرجنس:")
            for _, signal in divergence_signals.head(5).iterrows():
                print(f"  - {signal['العملة']}: {signal['المؤشر']} - {signal['نوع الإشارة']} في {signal['وقت الإشارة']}")
        
        return len(divergence_signals) > 0
        
    except Exception as e:
        print(f"❌ خطأ في التحليل الكامل: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🎯 اختبار شامل لإشارات الدايفرجنس")
    print("=" * 60)
    
    # اختبار اكتشاف الدايفرجنس
    divergence_success = test_divergence_detection()
    
    # اختبار التحليل الكامل
    analysis_success = test_full_analysis()
    
    print("\n" + "=" * 60)
    print("📋 ملخص النتائج:")
    print(f"  - اكتشاف الدايفرجنس: {'✅ نجح' if divergence_success else '❌ فشل'}")
    print(f"  - التحليل الكامل: {'✅ نجح' if analysis_success else '❌ فشل'}")
    
    if divergence_success and analysis_success:
        print("\n🎉 جميع اختبارات الدايفرجنس نجحت!")
        print("💡 يمكنك الآن رؤية إشارات الدايفرجنس في التطبيق")
    else:
        print("\n⚠️ بعض الاختبارات فشلت - قد تحتاج لتعديل المعايير")
    
    print("\n🚀 لتشغيل التطبيق:")
    print("python -m streamlit run app.py")

if __name__ == "__main__":
    main()
