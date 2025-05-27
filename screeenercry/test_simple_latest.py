#!/usr/bin/env python3
"""
اختبار بسيط لإشارات الدايفرجنس في الشمعة الأخيرة
"""

from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
import pandas as pd

def test_simple_latest():
    """اختبار بسيط للشمعة الأخيرة"""
    print("🔥 اختبار بسيط لإشارات الدايفرجنس في الشمعة الأخيرة")
    print("=" * 60)
    
    # جلب البيانات
    fetcher = DataFetcher()
    
    try:
        # جلب بيانات BTC
        print("📊 جلب بيانات BTC/USDT...")
        df = fetcher.get_crypto_data('BTC/USDT', '4h', 100)
        
        if df.empty:
            print("❌ لا توجد بيانات")
            return
        
        print(f"✅ تم جلب {len(df)} شمعة")
        print(f"📈 آخر سعر: ${df['close'].iloc[-1]:,.2f}")
        
        # حساب المؤشرات
        print("\n🔧 حساب المؤشرات...")
        indicators = TechnicalIndicators(df)
        
        # حساب RSI
        rsi_values = indicators.calculate_rsi()
        print(f"✅ RSI محسوب - آخر قيمة: {rsi_values.iloc[-1]:.2f}")
        
        # حساب MACD
        macd_values = indicators.calculate_macd()
        print(f"✅ MACD محسوب - آخر هيستوغرام: {macd_values['macd_histogram'].iloc[-1]:.4f}")
        
        # حساب OBV
        obv_values = indicators.calculate_obv()
        print(f"✅ OBV محسوب - آخر قيمة: {obv_values.iloc[-1]:,.0f}")
        
        # اختبار الدايفرجنس في الشمعة الأخيرة
        print("\n🔍 اختبار الدايفرجنس في الشمعة الأخيرة...")
        
        # RSI الدايفرجنس
        print("\n📊 RSI الدايفرجنس:")
        try:
            rsi_latest = indicators.detect_latest_divergence(df['close'], df['rsi'], lookback_periods=15)
            print(f"   - عدد الإشارات: {len(rsi_latest)}")
            
            for div in rsi_latest:
                print(f"   🔥 {div['type']}: {div['signal']}")
                print(f"      - {div['description']}")
                print(f"      - القوة: {div['strength']:.3f}")
                
        except Exception as e:
            print(f"   ❌ خطأ في RSI: {e}")
        
        # MACD الدايفرجنس
        print("\n📊 MACD الدايفرجنس:")
        try:
            macd_latest = indicators.detect_latest_divergence(df['close'], df['macd_histogram'], lookback_periods=15)
            print(f"   - عدد الإشارات: {len(macd_latest)}")
            
            for div in macd_latest:
                print(f"   🔥 {div['type']}: {div['signal']}")
                print(f"      - {div['description']}")
                print(f"      - القوة: {div['strength']:.3f}")
                
        except Exception as e:
            print(f"   ❌ خطأ في MACD: {e}")
        
        # OBV الدايفرجنس
        print("\n📊 OBV الدايفرجنس:")
        try:
            obv_latest = indicators.detect_latest_divergence(df['close'], df['obv'], lookback_periods=15)
            print(f"   - عدد الإشارات: {len(obv_latest)}")
            
            for div in obv_latest:
                print(f"   🔥 {div['type']}: {div['signal']}")
                print(f"      - {div['description']}")
                print(f"      - القوة: {div['strength']:.3f}")
                
        except Exception as e:
            print(f"   ❌ خطأ في OBV: {e}")
        
        # اختبار مع معايير أقل صرامة
        print("\n🔧 اختبار مع معايير مخففة...")
        
        # تجربة معايير أقل صرامة
        try:
            # تقليل الحد الأدنى للتغيير
            current_price = df['close'].iloc[-1]
            current_rsi = df['rsi'].iloc[-1]
            
            print(f"📈 السعر الحالي: ${current_price:,.2f}")
            print(f"📊 RSI الحالي: {current_rsi:.2f}")
            
            # مقارنة مع الفترات السابقة
            for i in range(2, 11):
                past_price = df['close'].iloc[-i]
                past_rsi = df['rsi'].iloc[-i]
                
                price_change = (current_price - past_price) / past_price * 100
                rsi_change = current_rsi - past_rsi
                
                print(f"   فترة {i}: السعر {price_change:+.2f}%, RSI {rsi_change:+.2f}")
                
                # البحث عن دايفرجنس بسيط
                if abs(price_change) > 0.5 and abs(rsi_change) > 1:
                    if (price_change < 0 and rsi_change > 0) or (price_change > 0 and rsi_change < 0):
                        signal_type = "صعودي" if price_change < 0 and rsi_change > 0 else "هبوطي"
                        print(f"   🔥 دايفرجنس {signal_type} محتمل!")
        
        except Exception as e:
            print(f"❌ خطأ في الاختبار المخفف: {e}")
        
        print("\n✅ انتهى الاختبار")
        
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

if __name__ == "__main__":
    test_simple_latest()
