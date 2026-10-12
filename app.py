def get_trading_sessions(tz_name):
    tz = ZoneInfo(tz_name)
    now_local = datetime.now(tz)
    
    # تحديد نطاقات الجلسات بالساعات (UTC)
    sessions_utc = {
        "جلسة آسيا (طوكيو)": {"open": 0, "close": 9},       # 00:00 UTC إلى 09:00 UTC
        "جلسة لندن (أوروبا)": {"open": 7, "close": 16},     # 07:00 UTC إلى 16:00 UTC
        "جلسة نيويورك (أمريكا)": {"open": 12, "close": 21},  # 12:00 UTC إلى 21:00 UTC
        "تداخل لندن / نيويورك": {"open": 12, "close": 16} # 12:00 UTC إلى 16:00 UTC
    }
    
    result = []
    now_utc = datetime.now(timezone.utc)
    
    for s_name, times in sessions_utc.items():
        # إنشاء تواريخ الجلسات بـ UTC
        start_utc = now_utc.replace(hour=times["open"], minute=0, second=0, microsecond=0)
        end_utc = now_utc.replace(hour=times["close"], minute=0, second=0, microsecond=0)
        
        # إذا كان الإغلاق أرقامه أقل من الافتتاح (عبور منتصف الليل في UTC)
        if times["close"] < times["open"]:
            if now_utc.hour < times["close"]:
                start_utc -= timedelta(days=1)
            else:
                end_utc += timedelta(days=1)
        
        # التحقق من النشاط بناءً على UTC الحقيقي
        is_active = start_utc <= now_utc < end_utc
        
        # تحويل العرض للتوقيت المحلي للمستخدم
        start_local = start_utc.astimezone(tz)
        end_local = end_utc.astimezone(tz)
        
        result.append({
            "الجلسة": s_name,
            "الافتتاح المحلي": start_local.strftime("%I:%M %p"),
            "الإغلاق المحلي": end_local.strftime("%I:%M %p"),
            "الحالة الحالية": "🟢 نشطة الآن" if is_active else "⚪ مغلقة",
            "مستوى السيولة": "عالي جداً" if "تداخل" in s_name or "نيويورك" in s_name else ("متوسط" if "لندن" in s_name else "منخفض / نطاق ضيق")
        })
    return result
