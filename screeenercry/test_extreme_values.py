#!/usr/bin/env python3
"""
اختبار إصلاح القيم الشاذة مثل 2,060% و 4,000%
"""

from crypto_analyzer import CryptoAnalyzer
import pandas as pd

def test_extreme_values():
    """اختبار القيم الشاذة التي ظهرت في الصورة"""
    print("🔥 اختبار إصلاح القيم الشاذة")
    print("=" * 60)
    
    analyzer = CryptoAnalyzer()
    
    # القيم التي ظهرت في الصورة
    extreme_values = [
        2060.0,   # 2,060%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
        4000.0,   # 4,000%
    ]
    
    print("📊 اختبار القيم الشاذة من الصورة:")
    print("-" * 50)
    
    all_fixed = True
    
    for i, value in enumerate(extreme_values, 1):
        try:
            # اختبار دالة الإصلاح الأساسية
            fixed_value = analyzer._fix_strength_value(value)
            
            # اختبار الفحص النهائي
            final_value = analyzer._final_strength_check(fixed_value)
            
            print(f"   {i:2d}. المدخل: {value:,.0f}% → مُصحح: {fixed_value:.1f}% → نهائي: {final_value:.1f}%")
            
            # التحقق من أن القيمة النهائية صحيحة
            if 10.0 <= final_value <= 100.0:
                print(f"       ✅ صحيح")
            else:
                print(f"       ❌ خاطئ - خارج النطاق")
                all_fixed = False
            
        except Exception as e:
            print(f"       ❌ خطأ: {e}")
            all_fixed = False
    
    return all_fixed

def test_various_extreme_cases():
    """اختبار حالات شاذة متنوعة"""
    print("\n🧪 اختبار حالات شاذة متنوعة")
    print("=" * 60)
    
    analyzer = CryptoAnalyzer()
    
    # حالات اختبار متنوعة
    test_cases = [
        {'value': 10000, 'description': 'قيمة كبيرة جداً (10,000%)'},
        {'value': 50000, 'description': 'قيمة ضخمة (50,000%)'},
        {'value': 999, 'description': 'قيمة كبيرة (999%)'},
        {'value': 2060, 'description': 'القيمة من الصورة (2,060%)'},
        {'value': 4000, 'description': 'القيمة من الصورة (4,000%)'},
        {'value': -2000, 'description': 'قيمة سالبة كبيرة (-2,000%)'},
        {'value': 0.5, 'description': 'قيمة صغيرة جداً (0.5%)'},
        {'value': 150, 'description': 'قيمة متوسطة كبيرة (150%)'},
    ]
    
    print("📊 اختبار حالات متنوعة:")
    print("-" * 50)
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        try:
            value = test['value']
            
            # تطبيق الإصلاح
            fixed_value = analyzer._fix_strength_value(value)
            final_value = analyzer._final_strength_check(fixed_value)
            
            print(f"   {i}. {test['description']}")
            print(f"      المدخل: {value:,.1f}%")
            print(f"      مُصحح: {fixed_value:.1f}%")
            print(f"      نهائي: {final_value:.1f}%")
            
            # التحقق من النتيجة
            if 10.0 <= final_value <= 100.0:
                print(f"      ✅ صحيح")
            else:
                print(f"      ❌ خاطئ")
                all_passed = False
            
            print()
            
        except Exception as e:
            print(f"      ❌ خطأ: {e}")
            all_passed = False
    
    return all_passed

def test_real_analysis():
    """اختبار التحليل الحقيقي للتأكد من عدم ظهور قيم شاذة"""
    print("\n📊 اختبار التحليل الحقيقي")
    print("=" * 60)
    
    analyzer = CryptoAnalyzer()
    
    try:
        # تحليل عدة عملات
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        timeframes = ['4h']
        
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 50)
        
        if df_signals.empty:
            print("❌ لا توجد إشارات للاختبار")
            return False
        
        print(f"✅ تم تحليل {len(symbols)} عملة")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        
        # فحص قوة الإشارة
        if 'قوة الإشارة' not in df_signals.columns:
            print("❌ عمود قوة الإشارة غير موجود")
            return False
        
        strength_values = df_signals['قوة الإشارة'].dropna()
        
        print(f"📈 عدد الإشارات مع قوة: {len(strength_values)}")
        print(f"🔻 أقل قوة: {strength_values.min():.1f}%")
        print(f"🔺 أعلى قوة: {strength_values.max():.1f}%")
        print(f"📈 متوسط القوة: {strength_values.mean():.1f}%")
        
        # البحث عن قيم شاذة
        extreme_values = strength_values[
            (strength_values < 10) | 
            (strength_values > 100) | 
            (strength_values > 1000)  # قيم كبيرة جداً
        ]
        
        if len(extreme_values) > 0:
            print(f"\n❌ توجد قيم شاذة: {len(extreme_values)}")
            print(f"   القيم الشاذة: {extreme_values.tolist()}")
            return False
        else:
            print(f"\n✅ لا توجد قيم شاذة - جميع القيم بين 10-100%")
        
        # عرض توزيع القوة
        strong_signals = len(strength_values[strength_values >= 70])
        medium_signals = len(strength_values[(strength_values >= 40) & (strength_values < 70)])
        weak_signals = len(strength_values[strength_values < 40])
        
        print(f"\n📈 توزيع القوة:")
        print(f"   🟢 قوية (70%+): {strong_signals}")
        print(f"   🟡 متوسطة (40-70%): {medium_signals}")
        print(f"   🔴 ضعيفة (10-40%): {weak_signals}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التحليل: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 اختبار شامل لإصلاح القيم الشاذة")
    print("=" * 70)
    
    # اختبار القيم من الصورة
    extreme_test = test_extreme_values()
    
    # اختبار حالات متنوعة
    various_test = test_various_extreme_cases()
    
    # اختبار التحليل الحقيقي
    real_test = test_real_analysis()
    
    # النتائج النهائية
    print("\n" + "=" * 70)
    print("📋 ملخص النتائج:")
    print(f"🔥 إصلاح القيم من الصورة: {'✅ نجح' if extreme_test else '❌ فشل'}")
    print(f"🧪 اختبار حالات متنوعة: {'✅ نجح' if various_test else '❌ فشل'}")
    print(f"📊 اختبار التحليل الحقيقي: {'✅ نجح' if real_test else '❌ فشل'}")
    
    if all([extreme_test, various_test, real_test]):
        print(f"\n🎉 تم إصلاح جميع القيم الشاذة بنجاح!")
        print("✅ لا مزيد من 2,060% أو 4,000%")
        print("✅ جميع القيم الآن بين 10-100%")
        print("✅ الإصلاح يعمل لجميع الحالات")
    else:
        print(f"\n⚠️ ما زالت هناك مشاكل في بعض الحالات")
    
    print(f"\n🚀 شغل التطبيق لرؤية النتائج:")
    print("python -m streamlit run app.py")

if __name__ == "__main__":
    main()
