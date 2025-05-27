#!/usr/bin/env python3
"""
اختبار سريع لإصلاح قوة الإشارة
"""

from crypto_analyzer import CryptoAnalyzer
import pandas as pd

def test_strength_fix_function():
    """اختبار دالة إصلاح قوة الإشارة"""
    print("🧪 اختبار دالة إصلاح قوة الإشارة")
    print("=" * 50)
    
    analyzer = CryptoAnalyzer()
    
    # حالات اختبار
    test_cases = [
        230.5,    # قيمة كبيرة
        2300,     # قيمة كبيرة جداً
        -50,      # قيمة سالبة
        5,        # قيمة صغيرة
        75,       # قيمة صحيحة
        150.7,    # قيمة متوسطة كبيرة
    ]
    
    print("📊 اختبار حالات مختلفة:")
    all_passed = True
    
    for i, test_value in enumerate(test_cases, 1):
        try:
            result = analyzer._fix_strength_value(test_value)
            
            print(f"   {i}. المدخل: {test_value} → النتيجة: {result:.1f}%")
            
            # التحقق من أن النتيجة بين 10-100
            if 10 <= result <= 100:
                print(f"      ✅ صحيح")
            else:
                print(f"      ❌ خاطئ")
                all_passed = False
            
        except Exception as e:
            print(f"      ❌ خطأ: {e}")
            all_passed = False
    
    return all_passed

def test_quick_analysis():
    """اختبار سريع للتحليل"""
    print("\n📊 اختبار سريع للتحليل")
    print("=" * 50)
    
    analyzer = CryptoAnalyzer()
    
    try:
        # تحليل عملة واحدة فقط
        symbols = ['BTC/USDT']
        timeframes = ['4h']
        
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 50)
        
        if df_signals.empty:
            print("❌ لا توجد إشارات")
            return False
        
        print(f"✅ تم تحليل {len(symbols)} عملة")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        
        # فحص قوة الإشارة
        if 'قوة الإشارة' not in df_signals.columns:
            print("❌ عمود قوة الإشارة غير موجود")
            return False
        
        strength_values = df_signals['قوة الإشارة'].dropna()
        
        if len(strength_values) == 0:
            print("❌ لا توجد قيم قوة إشارة")
            return False
        
        print(f"📈 عدد الإشارات مع قوة: {len(strength_values)}")
        print(f"🔻 أقل قوة: {strength_values.min():.1f}%")
        print(f"🔺 أعلى قوة: {strength_values.max():.1f}%")
        print(f"📈 متوسط القوة: {strength_values.mean():.1f}%")
        
        # البحث عن قيم خاطئة
        invalid_values = strength_values[(strength_values < 10) | (strength_values > 100)]
        
        if len(invalid_values) > 0:
            print(f"❌ قيم خاطئة: {len(invalid_values)}")
            print(f"   القيم: {invalid_values.tolist()}")
            return False
        else:
            print("✅ جميع القيم صحيحة (10-100%)")
        
        # عرض عينة من الإشارات
        print(f"\n📋 عينة من الإشارات:")
        sample_signals = df_signals.head(5)
        for _, signal in sample_signals.iterrows():
            strength = signal['قوة الإشارة']
            print(f"   - {signal['المؤشر']}: {strength:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 اختبار سريع لإصلاح قوة الإشارة")
    print("=" * 60)
    
    # اختبار دالة الإصلاح
    function_test = test_strength_fix_function()
    
    # اختبار التحليل السريع
    analysis_test = test_quick_analysis()
    
    # النتائج
    print("\n" + "=" * 60)
    print("📋 النتائج:")
    print(f"🧪 اختبار دالة الإصلاح: {'✅ نجح' if function_test else '❌ فشل'}")
    print(f"📊 اختبار التحليل: {'✅ نجح' if analysis_test else '❌ فشل'}")
    
    if function_test and analysis_test:
        print(f"\n🎉 تم إصلاح قوة الإشارة بنجاح!")
        print("✅ جميع القيم الآن بين 10-100%")
        print("✅ لا توجد قيم غير منطقية")
    else:
        print(f"\n⚠️ ما زالت هناك مشاكل")
    
    print(f"\n🚀 شغل التطبيق:")
    print("python -m streamlit run app.py")

if __name__ == "__main__":
    main()
