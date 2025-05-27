#!/usr/bin/env python3
"""
اختبار إصلاح قوة الإشارة لجميع الأطر الزمنية والإشارات
"""

from crypto_analyzer import CryptoAnalyzer
from data_fetcher import DataFetcher
import pandas as pd

def test_strength_fix_all_timeframes():
    """اختبار إصلاح قوة الإشارة لجميع الأطر الزمنية"""
    print("🔧 اختبار إصلاح قوة الإشارة لجميع الأطر الزمنية")
    print("=" * 70)
    
    analyzer = CryptoAnalyzer()
    
    # اختبار جميع الأطر الزمنية
    timeframes = ['1h', '4h', '1d']
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    all_results = {}
    
    for timeframe in timeframes:
        print(f"\n📊 اختبار الإطار الزمني: {timeframe}")
        print("-" * 50)
        
        try:
            df_signals = analyzer.analyze_multiple_cryptos(symbols, [timeframe], 100)
            
            if df_signals.empty:
                print(f"❌ لا توجد إشارات في {timeframe}")
                continue
            
            print(f"✅ تم تحليل {len(symbols)} عملة")
            print(f"📊 إجمالي الإشارات: {len(df_signals)}")
            
            # التحقق من وجود عمود قوة الإشارة
            if 'قوة الإشارة' not in df_signals.columns:
                print(f"❌ عمود قوة الإشارة غير موجود في {timeframe}")
                continue
            
            # فحص القيم
            strength_values = df_signals['قوة الإشارة'].dropna()
            
            if len(strength_values) == 0:
                print(f"❌ لا توجد قيم قوة إشارة في {timeframe}")
                continue
            
            # إحصائيات القوة
            min_strength = strength_values.min()
            max_strength = strength_values.max()
            avg_strength = strength_values.mean()
            
            print(f"   🔻 أقل قوة: {min_strength:.1f}%")
            print(f"   🔺 أعلى قوة: {max_strength:.1f}%")
            print(f"   📈 متوسط القوة: {avg_strength:.1f}%")
            
            # التحقق من القيم الخاطئة
            invalid_values = strength_values[(strength_values < 0) | (strength_values > 100)]
            
            if len(invalid_values) > 0:
                print(f"   ❌ قيم خاطئة: {len(invalid_values)} قيمة")
                print(f"   القيم الخاطئة: {invalid_values.tolist()[:5]}...")  # أول 5 قيم
                all_results[timeframe] = False
            else:
                print(f"   ✅ جميع القيم صحيحة (10-100%)")
                all_results[timeframe] = True
            
            # عرض توزيع القوة
            strong_signals = len(strength_values[strength_values >= 70])
            medium_signals = len(strength_values[(strength_values >= 40) & (strength_values < 70)])
            weak_signals = len(strength_values[strength_values < 40])
            
            print(f"   📈 توزيع القوة:")
            print(f"      🟢 قوية (70%+): {strong_signals}")
            print(f"      🟡 متوسطة (40-70%): {medium_signals}")
            print(f"      🔴 ضعيفة (<40%): {weak_signals}")
            
            # عرض أقوى 3 إشارات
            strongest_signals = df_signals.nlargest(3, 'قوة الإشارة')
            print(f"   🏆 أقوى 3 إشارات:")
            for i, (_, signal) in enumerate(strongest_signals.iterrows(), 1):
                strength = signal['قوة الإشارة']
                print(f"      {i}. {signal['العملة']} - {signal['المؤشر']} - {strength:.1f}%")
            
        except Exception as e:
            print(f"❌ خطأ في تحليل {timeframe}: {e}")
            all_results[timeframe] = False
    
    return all_results

def test_strength_fix_function():
    """اختبار دالة إصلاح قوة الإشارة مباشرة"""
    print("\n🧪 اختبار دالة إصلاح قوة الإشارة")
    print("=" * 70)
    
    analyzer = CryptoAnalyzer()
    
    # حالات اختبار مختلفة
    test_cases = [
        {'input': 230.5, 'expected_range': (10, 100), 'description': 'قيمة كبيرة (230.5)'},
        {'input': 2300, 'expected_range': (10, 100), 'description': 'قيمة كبيرة جداً (2300)'},
        {'input': -50, 'expected_range': (10, 100), 'description': 'قيمة سالبة (-50)'},
        {'input': 5, 'expected_range': (10, 100), 'description': 'قيمة صغيرة (5)'},
        {'input': 75, 'expected_range': (75, 75), 'description': 'قيمة صحيحة (75)'},
        {'input': None, 'expected_range': (10, 100), 'description': 'قيمة فارغة (None)'},
        {'input': 'invalid', 'expected_range': (10, 100), 'description': 'قيمة نصية (invalid)'},
        {'input': 150.7, 'expected_range': (10, 100), 'description': 'قيمة متوسطة كبيرة (150.7)'},
    ]
    
    print("📊 اختبار حالات مختلفة:")
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        try:
            result = analyzer._fix_strength_value(test['input'])
            
            print(f"   {i}. {test['description']}")
            print(f"      المدخل: {test['input']}")
            print(f"      النتيجة: {result:.1f}%")
            
            # التحقق من النطاق
            if test['expected_range'][0] <= result <= test['expected_range'][1]:
                print(f"      ✅ ضمن النطاق المتوقع")
            else:
                print(f"      ❌ خارج النطاق المتوقع ({test['expected_range'][0]}-{test['expected_range'][1]})")
                all_passed = False
            
            # التحقق من أن النتيجة بين 10-100
            if 10 <= result <= 100:
                print(f"      ✅ ضمن النطاق العام (10-100%)")
            else:
                print(f"      ❌ خارج النطاق العام (10-100%)")
                all_passed = False
            
            print()
            
        except Exception as e:
            print(f"      ❌ خطأ في الاختبار: {e}")
            all_passed = False
    
    return all_passed

def test_real_data_fix():
    """اختبار الإصلاح على بيانات حقيقية"""
    print("\n📊 اختبار الإصلاح على بيانات حقيقية")
    print("=" * 70)
    
    analyzer = CryptoAnalyzer()
    
    try:
        # تحليل بيانات حقيقية
        symbols = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'ADA/USDT']
        timeframes = ['1h', '4h', '1d']
        
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 100)
        
        if df_signals.empty:
            print("❌ لا توجد إشارات للاختبار")
            return False
        
        print(f"✅ تم تحليل {len(symbols)} عملة في {len(timeframes)} أطر زمنية")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        
        # فحص جميع قيم قوة الإشارة
        strength_values = df_signals['قوة الإشارة'].dropna()
        
        print(f"\n📈 إحصائيات شاملة:")
        print(f"   📊 عدد الإشارات مع قوة: {len(strength_values)}")
        print(f"   🔻 أقل قوة: {strength_values.min():.1f}%")
        print(f"   🔺 أعلى قوة: {strength_values.max():.1f}%")
        print(f"   📈 متوسط القوة: {strength_values.mean():.1f}%")
        
        # البحث عن قيم خاطئة
        invalid_values = strength_values[(strength_values < 10) | (strength_values > 100)]
        
        if len(invalid_values) > 0:
            print(f"\n❌ توجد قيم خاطئة: {len(invalid_values)} قيمة")
            print(f"   القيم الخاطئة: {invalid_values.tolist()}")
            return False
        else:
            print(f"\n✅ جميع القيم صحيحة (بين 10-100%)")
        
        # توزيع القوة
        strong_signals = len(strength_values[strength_values >= 70])
        medium_signals = len(strength_values[(strength_values >= 40) & (strength_values < 70)])
        weak_signals = len(strength_values[strength_values < 40])
        
        print(f"\n📈 توزيع القوة الإجمالي:")
        print(f"   🟢 قوية (70%+): {strong_signals} ({strong_signals/len(strength_values)*100:.1f}%)")
        print(f"   🟡 متوسطة (40-70%): {medium_signals} ({medium_signals/len(strength_values)*100:.1f}%)")
        print(f"   🔴 ضعيفة (<40%): {weak_signals} ({weak_signals/len(strength_values)*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار البيانات الحقيقية: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 اختبار شامل لإصلاح قوة الإشارة")
    print("=" * 80)
    
    # اختبار جميع الأطر الزمنية
    timeframe_results = test_strength_fix_all_timeframes()
    
    # اختبار دالة الإصلاح
    function_test = test_strength_fix_function()
    
    # اختبار البيانات الحقيقية
    real_data_test = test_real_data_fix()
    
    # النتائج النهائية
    print("\n" + "=" * 80)
    print("📋 ملخص نتائج الاختبار:")
    
    print(f"\n🕐 نتائج الأطر الزمنية:")
    for timeframe, result in timeframe_results.items():
        status = "✅ نجح" if result else "❌ فشل"
        print(f"   - {timeframe}: {status}")
    
    print(f"\n🧪 اختبار دالة الإصلاح: {'✅ نجح' if function_test else '❌ فشل'}")
    print(f"📊 اختبار البيانات الحقيقية: {'✅ نجح' if real_data_test else '❌ فشل'}")
    
    # التقييم الإجمالي
    all_timeframes_passed = all(timeframe_results.values())
    overall_success = all_timeframes_passed and function_test and real_data_test
    
    if overall_success:
        print(f"\n🎉 تم إصلاح قوة الإشارة بنجاح لجميع الأطر الزمنية!")
        print("✅ جميع القيم الآن بين 10-100%")
        print("✅ لا توجد قيم غير منطقية مثل 2300%")
        print("✅ الإصلاح يعمل لجميع أنواع الإشارات")
    else:
        print(f"\n⚠️ ما زالت هناك مشاكل في بعض الأطر الزمنية")
        print("🔧 راجع النتائج أعلاه لمعرفة المشاكل")
    
    print(f"\n🚀 لتشغيل التطبيق المصحح:")
    print("python -m streamlit run app.py")

if __name__ == "__main__":
    main()
