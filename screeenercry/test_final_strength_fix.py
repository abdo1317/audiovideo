#!/usr/bin/env python3
"""
اختبار نهائي لإصلاح قوة الإشارة - التأكد من عدم وجود قيم شاذة
"""

from crypto_analyzer import CryptoAnalyzer
import pandas as pd

def test_all_signals_have_strength():
    """اختبار أن جميع الإشارات لديها قوة"""
    print("🔍 اختبار أن جميع الإشارات لديها قوة")
    print("=" * 60)
    
    analyzer = CryptoAnalyzer()
    
    try:
        # تحليل عدة عملات وأطر زمنية
        symbols = ['BTC/USDT', 'ETH/USDT']
        timeframes = ['4h', '1d']
        
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 50)
        
        if df_signals.empty:
            print("❌ لا توجد إشارات للاختبار")
            return False
        
        print(f"✅ تم تحليل {len(symbols)} عملة في {len(timeframes)} أطر زمنية")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        
        # التحقق من وجود عمود قوة الإشارة
        if 'قوة الإشارة' not in df_signals.columns:
            print("❌ عمود قوة الإشارة غير موجود")
            return False
        
        print("✅ عمود قوة الإشارة موجود")
        
        # فحص جميع القيم
        strength_values = df_signals['قوة الإشارة']
        
        # البحث عن قيم فارغة
        null_values = strength_values.isnull().sum()
        if null_values > 0:
            print(f"❌ توجد {null_values} قيمة فارغة")
            return False
        else:
            print("✅ لا توجد قيم فارغة")
        
        # فحص النطاق
        min_strength = strength_values.min()
        max_strength = strength_values.max()
        
        print(f"📊 نطاق القوة: {min_strength:.1f}% - {max_strength:.1f}%")
        
        # البحث عن قيم شاذة
        extreme_values = strength_values[
            (strength_values < 10) | 
            (strength_values > 100) |
            (strength_values > 1000)  # قيم كبيرة جداً
        ]
        
        if len(extreme_values) > 0:
            print(f"❌ توجد {len(extreme_values)} قيمة شاذة:")
            for val in extreme_values.unique():
                count = (strength_values == val).sum()
                print(f"   - {val:.1f}%: {count} إشارة")
            return False
        else:
            print("✅ لا توجد قيم شاذة - جميع القيم بين 10-100%")
        
        # توزيع القوة
        strong_signals = len(strength_values[strength_values >= 70])
        medium_signals = len(strength_values[(strength_values >= 40) & (strength_values < 70)])
        weak_signals = len(strength_values[strength_values < 40])
        
        print(f"\n📈 توزيع القوة:")
        print(f"   🟢 قوية (70%+): {strong_signals} ({strong_signals/len(strength_values)*100:.1f}%)")
        print(f"   🟡 متوسطة (40-70%): {medium_signals} ({medium_signals/len(strength_values)*100:.1f}%)")
        print(f"   🔴 ضعيفة (10-40%): {weak_signals} ({weak_signals/len(strength_values)*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_extreme_values():
    """اختبار القيم الشاذة المحددة"""
    print("\n🎯 اختبار القيم الشاذة المحددة")
    print("=" * 60)
    
    analyzer = CryptoAnalyzer()
    
    # القيم التي كانت تظهر في المشكلة
    test_values = [2060, 4000, 230, 150, 999, 10000, -500]
    
    print("📊 اختبار إصلاح القيم الشاذة:")
    
    all_fixed = True
    
    for i, value in enumerate(test_values, 1):
        try:
            fixed_value = analyzer._fix_strength_value(value)
            final_value = analyzer._final_strength_check(fixed_value)
            
            print(f"   {i}. {value:,} → {final_value:.1f}%", end="")
            
            if 10 <= final_value <= 100:
                print(" ✅")
            else:
                print(" ❌")
                all_fixed = False
                
        except Exception as e:
            print(f"   {i}. {value:,} → خطأ: {e} ❌")
            all_fixed = False
    
    return all_fixed

def test_real_app_usage():
    """اختبار الاستخدام الحقيقي للتطبيق"""
    print("\n🚀 اختبار الاستخدام الحقيقي للتطبيق")
    print("=" * 60)
    
    analyzer = CryptoAnalyzer()
    
    try:
        # محاكاة استخدام التطبيق الحقيقي
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        timeframes = ['1h', '4h']
        
        print(f"📊 تحليل {len(symbols)} عملة في {len(timeframes)} أطر زمنية...")
        
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 100)
        
        if df_signals.empty:
            print("❌ لا توجد إشارات")
            return False
        
        print(f"✅ تم العثور على {len(df_signals)} إشارة")
        
        # فحص شامل لقوة الإشارة
        strength_values = df_signals['قوة الإشارة']
        
        # إحصائيات
        print(f"\n📈 إحصائيات شاملة:")
        print(f"   📊 عدد الإشارات: {len(strength_values)}")
        print(f"   🔻 أقل قوة: {strength_values.min():.1f}%")
        print(f"   🔺 أعلى قوة: {strength_values.max():.1f}%")
        print(f"   📈 متوسط القوة: {strength_values.mean():.1f}%")
        print(f"   📊 الانحراف المعياري: {strength_values.std():.1f}%")
        
        # فحص القيم الشاذة
        outliers = strength_values[
            (strength_values < 5) | 
            (strength_values > 105) |
            (strength_values > 500)  # قيم كبيرة جداً
        ]
        
        if len(outliers) > 0:
            print(f"\n❌ توجد {len(outliers)} قيمة شاذة:")
            for val in outliers.unique():
                print(f"   - {val:.1f}%")
            return False
        else:
            print(f"\n✅ لا توجد قيم شاذة")
        
        # عرض عينة من الإشارات
        print(f"\n📋 عينة من الإشارات:")
        sample = df_signals.head(5)
        for _, signal in sample.iterrows():
            strength = signal['قوة الإشارة']
            print(f"   - {signal['العملة']} {signal['الإطار الزمني']}: {signal['المؤشر']} - {strength:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار الحقيقي: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 اختبار نهائي شامل لإصلاح قوة الإشارة")
    print("=" * 70)
    
    # اختبار أن جميع الإشارات لديها قوة
    all_have_strength = test_all_signals_have_strength()
    
    # اختبار القيم الشاذة المحددة
    extreme_values_fixed = test_specific_extreme_values()
    
    # اختبار الاستخدام الحقيقي
    real_usage_test = test_real_app_usage()
    
    # النتائج النهائية
    print("\n" + "=" * 70)
    print("📋 ملخص النتائج النهائية:")
    print(f"✅ جميع الإشارات لديها قوة: {'✅ نجح' if all_have_strength else '❌ فشل'}")
    print(f"🎯 إصلاح القيم الشاذة: {'✅ نجح' if extreme_values_fixed else '❌ فشل'}")
    print(f"🚀 الاستخدام الحقيقي: {'✅ نجح' if real_usage_test else '❌ فشل'}")
    
    overall_success = all([all_have_strength, extreme_values_fixed, real_usage_test])
    
    if overall_success:
        print(f"\n🎉 تم إصلاح مشكلة قوة الإشارة نهائياً!")
        print("✅ لا مزيد من القيم الشاذة مثل 2,060% أو 4,000%")
        print("✅ جميع القيم الآن بين 10-100%")
        print("✅ التطبيق جاهز للاستخدام الاحترافي")
        print("\n🚀 شغل التطبيق الآن:")
        print("python -m streamlit run app.py")
        print("\n🎯 ستجد جميع قيم قوة الإشارة منطقية ومفهومة!")
    else:
        print(f"\n⚠️ ما زالت هناك مشاكل تحتاج إصلاح")
        print("🔧 راجع النتائج أعلاه لمعرفة المشاكل المتبقية")

if __name__ == "__main__":
    main()
