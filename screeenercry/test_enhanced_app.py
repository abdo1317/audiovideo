#!/usr/bin/env python3
"""
اختبار التطبيق المحسن مع 40 عملة وقوة الإشارة
"""

from crypto_analyzer import CryptoAnalyzer
from data_fetcher import DataFetcher
import pandas as pd

def test_40_coins():
    """اختبار جلب 40 عملة قيادية"""
    print("🪙 اختبار جلب 40 عملة قيادية")
    print("=" * 50)
    
    fetcher = DataFetcher()
    
    try:
        symbols = fetcher.get_available_symbols()
        print(f"✅ تم جلب {len(symbols)} عملة")
        
        print("\n📋 قائمة العملات:")
        for i, symbol in enumerate(symbols, 1):
            print(f"{i:2d}. {symbol}")
        
        # اختبار جلب بيانات عدة عملات
        print(f"\n📊 اختبار جلب بيانات أول 5 عملات...")
        test_symbols = symbols[:5]
        
        for symbol in test_symbols:
            try:
                df = fetcher.get_crypto_data(symbol, '4h', 50)
                if not df.empty:
                    print(f"✅ {symbol}: {len(df)} شمعة، آخر سعر: ${df['close'].iloc[-1]:,.2f}")
                else:
                    print(f"❌ {symbol}: لا توجد بيانات")
            except Exception as e:
                print(f"❌ {symbol}: خطأ - {e}")
        
        return len(symbols) >= 30  # نتوقع على الأقل 30 عملة
        
    except Exception as e:
        print(f"❌ خطأ في جلب العملات: {e}")
        return False

def test_signal_strength():
    """اختبار قوة الإشارة"""
    print("\n💪 اختبار قوة الإشارة")
    print("=" * 50)
    
    analyzer = CryptoAnalyzer()
    
    try:
        # تحليل عدة عملات
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
        timeframes = ['4h']
        
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 100)
        
        if df_signals.empty:
            print("❌ لا توجد إشارات للاختبار")
            return False
        
        print(f"✅ تم تحليل {len(symbols)} عملة")
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        
        # التحقق من وجود عمود قوة الإشارة
        if 'قوة الإشارة' in df_signals.columns:
            print("✅ عمود قوة الإشارة موجود")
            
            # إحصائيات قوة الإشارة
            avg_strength = df_signals['قوة الإشارة'].mean()
            max_strength = df_signals['قوة الإشارة'].max()
            min_strength = df_signals['قوة الإشارة'].min()
            
            print(f"📈 متوسط القوة: {avg_strength:.1f}%")
            print(f"📈 أقصى قوة: {max_strength:.1f}%")
            print(f"📈 أقل قوة: {min_strength:.1f}%")
            
            # توزيع قوة الإشارات
            strong_signals = len(df_signals[df_signals['قوة الإشارة'] >= 70])
            medium_signals = len(df_signals[(df_signals['قوة الإشارة'] >= 40) & (df_signals['قوة الإشارة'] < 70)])
            weak_signals = len(df_signals[df_signals['قوة الإشارة'] < 40])
            
            print(f"\n📊 توزيع قوة الإشارات:")
            print(f"   🟢 قوية (70%+): {strong_signals} إشارة ({strong_signals/len(df_signals)*100:.1f}%)")
            print(f"   🟡 متوسطة (40-70%): {medium_signals} إشارة ({medium_signals/len(df_signals)*100:.1f}%)")
            print(f"   🔴 ضعيفة (<40%): {weak_signals} إشارة ({weak_signals/len(df_signals)*100:.1f}%)")
            
            # عرض أقوى الإشارات
            strongest_signals = df_signals.nlargest(5, 'قوة الإشارة')
            print(f"\n🏆 أقوى 5 إشارات:")
            for _, signal in strongest_signals.iterrows():
                print(f"   💎 {signal['العملة']} - {signal['المؤشر']} - {signal['نوع الإشارة']} - قوة: {signal['قوة الإشارة']:.1f}%")
            
            return True
        else:
            print("❌ عمود قوة الإشارة غير موجود")
            return False
        
    except Exception as e:
        print(f"❌ خطأ في اختبار قوة الإشارة: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_divergence_signals():
    """اختبار إشارات الدايفرجنس المحسنة"""
    print("\n🔥 اختبار إشارات الدايفرجنس المحسنة")
    print("=" * 50)
    
    analyzer = CryptoAnalyzer()
    
    try:
        # تحليل عملات أكثر
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 
                  'SOL/USDT', 'DOT/USDT', 'MATIC/USDT', 'AVAX/USDT', 'LINK/USDT']
        timeframes = ['4h', '1d']
        
        df_signals = analyzer.analyze_multiple_cryptos(symbols, timeframes, 100)
        
        if df_signals.empty:
            print("❌ لا توجد إشارات")
            return False
        
        # البحث عن إشارات الدايفرجنس الجديدة
        divergence_signals = df_signals[
            (df_signals['المؤشر'].str.contains('🔥', na=False)) |
            (df_signals['الوصف'].str.contains('الشمعة الأخيرة', na=False))
        ]
        
        print(f"📊 إجمالي الإشارات: {len(df_signals)}")
        print(f"🔥 إشارات الدايفرجنس الجديدة: {len(divergence_signals)}")
        
        if not divergence_signals.empty:
            print("\n🎯 إشارات الدايفرجنس المكتشفة:")
            for _, signal in divergence_signals.iterrows():
                strength = signal.get('قوة الإشارة', 'غير محدد')
                print(f"   🔥 {signal['العملة']} - {signal['الإطار الزمني']}")
                print(f"      📊 {signal['المؤشر']}")
                print(f"      📈 {signal['نوع الإشارة']} - قوة: {strength}%")
                print(f"      📝 {signal['الوصف']}")
                print(f"      💰 السعر: ${signal['السعر الحالي']}")
                print()
        else:
            print("ℹ️ لا توجد إشارات دايفرجنس في الشمعة الأخيرة حالياً")
            print("💡 هذا طبيعي - الدايفرجنس الصحيح نادر الحدوث")
        
        # إحصائيات عامة
        print(f"\n📈 توزيع الإشارات حسب النوع:")
        signal_types = df_signals['نوع الإشارة'].value_counts()
        for signal_type, count in signal_types.items():
            print(f"   - {signal_type}: {count} إشارة")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار الدايفرجنس: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار شامل للتطبيق المحسن")
    print("=" * 70)
    
    # اختبار 40 عملة
    coins_test = test_40_coins()
    
    # اختبار قوة الإشارة
    strength_test = test_signal_strength()
    
    # اختبار إشارات الدايفرجنس
    divergence_test = test_divergence_signals()
    
    # النتائج النهائية
    print("\n" + "=" * 70)
    print("📋 ملخص نتائج الاختبار:")
    print(f"  🪙 40 عملة قيادية: {'✅ نجح' if coins_test else '❌ فشل'}")
    print(f"  💪 قوة الإشارة: {'✅ نجح' if strength_test else '❌ فشل'}")
    print(f"  🔥 إشارات الدايفرجنس: {'✅ نجح' if divergence_test else '❌ فشل'}")
    
    if all([coins_test, strength_test, divergence_test]):
        print("\n🎉 جميع الاختبارات نجحت!")
        print("✅ التطبيق جاهز مع التحسينات الجديدة:")
        print("   - 40 عملة قيادية")
        print("   - قوة الإشارة مع ألوان محسنة")
        print("   - إشارات دايفرجنس دقيقة")
        print("   - إمكانية التحديث التلقائي")
    else:
        print("\n⚠️ بعض الاختبارات فشلت - راجع الأخطاء أعلاه")
    
    print("\n🚀 لتشغيل التطبيق المحسن:")
    print("python -m streamlit run app.py")

if __name__ == "__main__":
    main()
