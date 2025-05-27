#!/usr/bin/env python3
"""
اختبار بسيط لمحلل العملات الرقمية
"""

from crypto_analyzer import CryptoAnalyzer
from data_fetcher import DataFetcher
import pandas as pd

def test_data_fetcher():
    """اختبار جالب البيانات"""
    print("🔍 اختبار جالب البيانات...")
    
    fetcher = DataFetcher()
    
    # اختبار جلب قائمة العملات
    try:
        symbols = fetcher.get_available_symbols()
        print(f"✅ تم جلب {len(symbols)} عملة بنجاح")
        print(f"العملات المتاحة: {symbols[:5]}...")
    except Exception as e:
        print(f"❌ خطأ في جلب قائمة العملات: {e}")
        return False
    
    # اختبار جلب بيانات عملة واحدة
    try:
        df = fetcher.get_crypto_data('BTC/USDT', '1d', 50)
        if not df.empty:
            print(f"✅ تم جلب بيانات BTC/USDT بنجاح ({len(df)} شمعة)")
            print(f"آخر سعر: ${df['close'].iloc[-1]:,.2f}")
        else:
            print("❌ لم يتم جلب أي بيانات")
            return False
    except Exception as e:
        print(f"❌ خطأ في جلب بيانات BTC/USDT: {e}")
        return False
    
    return True

def test_analyzer():
    """اختبار المحلل"""
    print("\n📊 اختبار المحلل...")
    
    analyzer = CryptoAnalyzer()
    
    try:
        # تحليل عملة واحدة
        signals = analyzer.analyze_single_crypto('BTC/USDT', '1d', 100)
        print(f"✅ تم تحليل BTC/USDT بنجاح ({len(signals)} إشارة)")
        
        if signals:
            print("أحدث الإشارات:")
            for signal in signals[:3]:
                print(f"  - {signal['type']}: {signal['signal']} في {signal['timestamp']}")
        
        # تحليل عدة عملات
        symbols = ['BTC/USDT', 'ETH/USDT']
        df_signals = analyzer.analyze_multiple_cryptos(symbols, ['1d'], 50)
        
        if not df_signals.empty:
            print(f"✅ تم تحليل {len(symbols)} عملة بنجاح")
            print(f"إجمالي الإشارات: {len(df_signals)}")
        else:
            print("❌ لم يتم العثور على إشارات")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في التحليل: {e}")
        return False
    
    return True

def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء اختبار تطبيق تحليل العملات الرقمية")
    print("=" * 50)
    
    # اختبار جالب البيانات
    if not test_data_fetcher():
        print("\n❌ فشل اختبار جالب البيانات")
        return
    
    # اختبار المحلل
    if not test_analyzer():
        print("\n❌ فشل اختبار المحلل")
        return
    
    print("\n" + "=" * 50)
    print("✅ جميع الاختبارات نجحت!")
    print("🎉 التطبيق جاهز للاستخدام")
    print("\nلتشغيل التطبيق:")
    print("python -m streamlit run app.py")
    print("أو تشغيل ملف: run_app.bat")

if __name__ == "__main__":
    main()
