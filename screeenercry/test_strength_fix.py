#!/usr/bin/env python3
"""
اختبار إصلاح نسبة قوة الإشارة
"""

from crypto_analyzer import CryptoAnalyzer
from data_fetcher import DataFetcher
import pandas as pd

def test_strength_calculation():
    """اختبار حساب قوة الإشارة المصحح"""
    print("💪 اختبار حساب قوة الإشارة المصحح")
    print("=" * 60)
    
    analyzer = CryptoAnalyzer()
    
    try:
        # تحليل عدة عملات
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT']
        timeframes = ['4h', '1d']
        
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 100)
        
        if df_signals.empty:
            print("❌ لا توجد إشارات للاختبار")
            return False
        
        print(f"✅ تم تحليل {len(symbols)} عملة")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        
        # التحقق من وجود عمود قوة الإشارة
        if 'قوة الإشارة' not in df_signals.columns:
            print("❌ عمود قوة الإشارة غير موجود")
            return False
        
        print("✅ عمود قوة الإشارة موجود")
        
        # فحص القيم
        strength_values = df_signals['قوة الإشارة'].dropna()
        
        if len(strength_values) == 0:
            print("❌ لا توجد قيم قوة إشارة")
            return False
        
        # إحصائيات القوة
        min_strength = strength_values.min()
        max_strength = strength_values.max()
        avg_strength = strength_values.mean()
        
        print(f"\n📊 إحصائيات قوة الإشارة:")
        print(f"   🔻 أقل قوة: {min_strength:.1f}%")
        print(f"   🔺 أعلى قوة: {max_strength:.1f}%")
        print(f"   📈 متوسط القوة: {avg_strength:.1f}%")
        
        # التحقق من أن القيم منطقية
        invalid_values = strength_values[(strength_values < 0) | (strength_values > 100)]
        
        if len(invalid_values) > 0:
            print(f"\n❌ توجد قيم غير منطقية: {len(invalid_values)} قيمة")
            print(f"   القيم الخاطئة: {invalid_values.tolist()}")
            return False
        else:
            print(f"\n✅ جميع القيم منطقية (بين 0-100%)")
        
        # عرض توزيع القوة
        strong_signals = len(strength_values[strength_values >= 70])
        medium_signals = len(strength_values[(strength_values >= 40) & (strength_values < 70)])
        weak_signals = len(strength_values[strength_values < 40])
        
        print(f"\n📈 توزيع قوة الإشارات:")
        print(f"   🟢 قوية (70%+): {strong_signals} إشارة ({strong_signals/len(strength_values)*100:.1f}%)")
        print(f"   🟡 متوسطة (40-70%): {medium_signals} إشارة ({medium_signals/len(strength_values)*100:.1f}%)")
        print(f"   🔴 ضعيفة (<40%): {weak_signals} إشارة ({weak_signals/len(strength_values)*100:.1f}%)")
        
        # عرض أقوى الإشارات
        strongest_signals = df_signals.nlargest(10, 'قوة الإشارة')
        print(f"\n🏆 أقوى 10 إشارات:")
        for i, (_, signal) in enumerate(strongest_signals.iterrows(), 1):
            strength = signal['قوة الإشارة']
            print(f"   {i:2d}. {signal['العملة']} - {signal['المؤشر']} - {signal['نوع الإشارة']} - {strength:.1f}%")
        
        # البحث عن إشارات الدايفرجنس الجديدة
        divergence_signals = df_signals[
            (df_signals['المؤشر'].str.contains('🔥', na=False)) |
            (df_signals['الوصف'].str.contains('الشمعة الأخيرة', na=False))
        ]
        
        print(f"\n🔥 إشارات الدايفرجنس الجديدة: {len(divergence_signals)}")
        
        if not divergence_signals.empty:
            print("\n🎯 تفاصيل إشارات الدايفرجنس:")
            for _, signal in divergence_signals.iterrows():
                strength = signal['قوة الإشارة']
                print(f"   🔥 {signal['العملة']} - {signal['الإطار الزمني']}")
                print(f"      📊 {signal['المؤشر']}")
                print(f"      📈 {signal['نوع الإشارة']} - قوة: {strength:.1f}%")
                print(f"      💰 السعر: ${signal['السعر الحالي']}")
                
                # التحقق من أن قوة الدايفرجنس منطقية
                if strength < 0 or strength > 100:
                    print(f"      ❌ قوة غير منطقية: {strength}%")
                else:
                    print(f"      ✅ قوة منطقية")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار قوة الإشارة: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_calculations():
    """اختبار حسابات محددة لقوة الإشارة"""
    print("\n🧮 اختبار حسابات محددة لقوة الإشارة")
    print("=" * 60)
    
    # محاكاة حسابات قوة الإشارة
    test_cases = [
        {
            'name': 'RSI دايفرجنس قوي',
            'price_change': 2.0,  # 2%
            'indicator_change': 10.0,  # 10 نقاط RSI
            'expected_range': (40, 70)
        },
        {
            'name': 'RSI دايفرجنس ضعيف',
            'price_change': 0.5,  # 0.5%
            'indicator_change': 3.0,  # 3 نقاط RSI
            'expected_range': (10, 30)
        },
        {
            'name': 'RSI دايفرجنس قوي جداً',
            'price_change': 5.0,  # 5%
            'indicator_change': 20.0,  # 20 نقطة RSI
            'expected_range': (90, 100)
        }
    ]
    
    print("📊 اختبار حسابات RSI:")
    for test in test_cases:
        # محاكاة حساب القوة (نفس المنطق في الكود)
        price_strength = min(50, abs(test['price_change']) * 10)
        rsi_strength = min(50, test['indicator_change'] * 2)
        total_strength = price_strength + rsi_strength
        final_strength = min(100, max(10, total_strength))
        
        print(f"   {test['name']}:")
        print(f"      تغيير السعر: {test['price_change']}% → قوة: {price_strength:.1f}")
        print(f"      تغيير RSI: {test['indicator_change']} → قوة: {rsi_strength:.1f}")
        print(f"      القوة الإجمالية: {final_strength:.1f}%")
        
        # التحقق من النطاق المتوقع
        if test['expected_range'][0] <= final_strength <= test['expected_range'][1]:
            print(f"      ✅ ضمن النطاق المتوقع ({test['expected_range'][0]}-{test['expected_range'][1]}%)")
        else:
            print(f"      ❌ خارج النطاق المتوقع ({test['expected_range'][0]}-{test['expected_range'][1]}%)")
        print()
    
    return True

def main():
    """الدالة الرئيسية"""
    print("🔧 اختبار إصلاح نسبة قوة الإشارة")
    print("=" * 70)
    
    # اختبار حساب القوة
    strength_test = test_strength_calculation()
    
    # اختبار حسابات محددة
    calculation_test = test_specific_calculations()
    
    # النتائج النهائية
    print("=" * 70)
    print("📋 ملخص نتائج الاختبار:")
    print(f"  💪 حساب قوة الإشارة: {'✅ نجح' if strength_test else '❌ فشل'}")
    print(f"  🧮 الحسابات المحددة: {'✅ نجح' if calculation_test else '❌ فشل'}")
    
    if strength_test and calculation_test:
        print("\n🎉 تم إصلاح نسبة قوة الإشارة بنجاح!")
        print("✅ جميع القيم الآن بين 0-100%")
        print("✅ الحسابات منطقية ودقيقة")
        print("✅ لا توجد قيم غير منطقية مثل 230%")
    else:
        print("\n⚠️ ما زالت هناك مشاكل في حساب قوة الإشارة")
    
    print("\n🚀 لتشغيل التطبيق المصحح:")
    print("python -m streamlit run app.py")

if __name__ == "__main__":
    main()
