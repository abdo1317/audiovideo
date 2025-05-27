#!/usr/bin/env python3
"""
اختبار الطريقة الجديدة للشمعة الأخيرة
"""

from crypto_analyzer import CryptoAnalyzer

def test_new_method():
    """اختبار الطريقة الجديدة"""
    print("🔥 اختبار الطريقة الجديدة لإشارات الدايفرجنس في الشمعة الأخيرة")
    print("=" * 70)
    
    analyzer = CryptoAnalyzer()
    
    # تحليل عدة عملات
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    timeframes = ['4h']
    
    try:
        print("📊 تحليل العملات...")
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 100)
        
        if df_signals.empty:
            print("❌ لم يتم العثور على إشارات")
            return
        
        print(f"✅ تم تحليل {len(symbols)} عملة")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        
        # البحث عن إشارات الشمعة الأخيرة
        latest_signals = df_signals[df_signals['المؤشر'].str.contains('🔥', na=False)]
        
        print(f"\n🔥 إشارات الشمعة الأخيرة: {len(latest_signals)}")
        
        if not latest_signals.empty:
            print("\n🎯 إشارات الدايفرجنس في الشمعة الأخيرة:")
            print("-" * 60)
            
            for _, signal in latest_signals.iterrows():
                print(f"🔥 {signal['العملة']}")
                print(f"   📊 المؤشر: {signal['المؤشر']}")
                print(f"   📈 الإشارة: {signal['نوع الإشارة']}")
                print(f"   ⏰ الوقت: {signal['وقت الإشارة']}")
                print(f"   📝 الوصف: {signal['الوصف']}")
                print(f"   💰 السعر: ${signal['السعر الحالي']}")
                print()
        else:
            print("⚠️ لا توجد إشارات دايفرجنس في الشمعة الأخيرة حالياً")
        
        # إحصائيات عامة
        print(f"\n📈 إحصائيات الإشارات:")
        signal_types = df_signals['المؤشر'].value_counts()
        for indicator, count in signal_types.head(10).items():
            print(f"   - {indicator}: {count}")
        
        # البحث عن أي إشارات تحتوي على "الشمعة الأخيرة"
        latest_text_signals = df_signals[df_signals['الوصف'].str.contains('الشمعة الأخيرة', na=False)]
        print(f"\n🔍 إشارات تحتوي على 'الشمعة الأخيرة': {len(latest_text_signals)}")
        
        if not latest_text_signals.empty:
            for _, signal in latest_text_signals.iterrows():
                print(f"   ✅ {signal['العملة']}: {signal['الوصف']}")
        
        return len(latest_signals) > 0 or len(latest_text_signals) > 0
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_method()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 تم العثور على إشارات الشمعة الأخيرة!")
        print("🚀 شغل التطبيق لرؤية الإشارات:")
        print("python -m streamlit run app.py")
    else:
        print("⚠️ لم يتم العثور على إشارات في الشمعة الأخيرة حالياً")
        print("💡 هذا طبيعي - الدايفرجنس لا يحدث دائماً")
