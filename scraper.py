"""
سحب بيانات حقيقية من Google Play Store
لتطبيقات النقل والتوصيل في السعودية
"""

import json
import time
from datetime import datetime
from google_play_scraper import app

APPS = [
    {
        "اسم":           "كريم",
        "package":       "com.careem.acma",
        "قطاع":          "نقل",
        "معامل_SA":      0.85,
        "سنة_الانشاء":   2016,
        "شهر_الانشاء":   1,
    },
    {
        "اسم":           "اوبر",
        "package":       "com.ubercab",
        "قطاع":          "نقل",
        "معامل_SA":      0.03,
        "سنة_الانشاء":   2012,
        "شهر_الانشاء":   6,
    },
    {
        "اسم":           "هنقرستيشن",
        "package":       "com.hungerstation.android.web",
        "قطاع":          "توصيل",
        "معامل_SA":      0.60,
        "سنة_الانشاء":   2015,
        "شهر_الانشاء":   1,
    },
    {
        "اسم":           "ديليفرو",
        "package":       "com.deliveroo.orderapp",
        "قطاع":          "توصيل",
        "معامل_SA":      0.25,
        "سنة_الانشاء":   2015,
        "شهر_الانشاء":   8,
    },
]


def months_since_launch(year, month):
    launch   = datetime(year, month, 1)
    now      = datetime.now()
    months   = (now.year - launch.year) * 12 + (now.month - launch.month)
    return max(months, 1)


def get_real_playstore_data():
    print("سحب البيانات من Google Play Store...")
    print("=" * 62)
    results = []

    for a in APPS:
        print(f"  جاري سحب بيانات {a['اسم']}...")
        try:
            data      = app(a["package"], lang="ar", country="sa")
            total_ratings  = data.get("ratings", 0)
            months         = months_since_launch(a["سنة_الانشاء"], a["شهر_الانشاء"])
            monthly_rate   = int(total_ratings / months)

            row = {
                "المنصة":               a["اسم"],
                "القطاع":               a["قطاع"],
                "معامل_SA":             a["معامل_SA"],
                "عدد_التقييمات_الكلي":  total_ratings,
                "التقييم_العام":        round(data.get("score", 0), 2),
                "عدد_التحميلات":        data.get("installs", "غير متاح"),
                "عمر_التطبيق_اشهر":    months,
                "تقييمات_شهرية":        monthly_rate,
            }
            print(f"  {a['اسم']:15} | كلي: {total_ratings:>10,} | عمر: {months} شهر | شهري: {monthly_rate:>6,}")
        except Exception as e:
            print(f"  {a['اسم']:15} | خطا: {e}")
            row = {
                "المنصة":               a["اسم"],
                "القطاع":               a["قطاع"],
                "معامل_SA":             a["معامل_SA"],
                "عدد_التقييمات_الكلي":  0,
                "التقييم_العام":        0,
                "عدد_التحميلات":        "غير متاح",
                "عمر_التطبيق_اشهر":    0,
                "تقييمات_شهرية":        0,
            }
        results.append(row)
        time.sleep(1)

    print("=" * 62)
    return results


def calculate_workers(results):
    """
    المنهجية:
      تقييمات شهرية / معدل التقييم (2%) = طلبات شهرية
      طلبات شهرية / 30 يوم              = طلبات يومية
      طلبات يومية * معامل SA            = طلبات يومية في السعودية
      طلبات SA / متوسط طلبات/عامل/يوم  = عدد العمال النشطين
    """
    REVIEW_RATE     = 0.02
    TRIPS_TRANSPORT = 8
    TRIPS_DELIVERY  = 11

    print()
    print("حساب تقدير العمال")
    print("=" * 62)
    print(f"  {'المنصة':15} | {'طلبات شهرية':>12} | {'طلبات SA/يوم':>13} | {'عمال':>8}")
    print("-" * 62)

    for row in results:
        monthly = row["تقييمات_شهرية"]
        if monthly == 0:
            row["عمال_مقدر"]      = 0
            row["طلبات_يومية_SA"] = 0
            print(f"  {row['المنصة']:15} | {'غير متاح':>12} | {'---':>13} | {'0':>8}")
            continue

        trips_per_worker  = TRIPS_TRANSPORT if row["القطاع"] == "نقل" else TRIPS_DELIVERY
        monthly_trips     = monthly / REVIEW_RATE
        daily_trips       = monthly_trips / 30
        daily_trips_sa    = daily_trips * row["معامل_SA"]
        workers           = int(daily_trips_sa / trips_per_worker)

        row["طلبات_يومية_SA"] = int(daily_trips_sa)
        row["عمال_مقدر"]      = workers

        print(f"  {row['المنصة']:15} | {int(monthly_trips):>12,} | {int(daily_trips_sa):>13,} | {workers:>8,}")

    print("=" * 62)
    return results


if __name__ == "__main__":
    data      = get_real_playstore_data()
    data      = calculate_workers(data)

    transport = sum(r["عمال_مقدر"] for r in data if r["القطاع"] == "نقل")
    delivery  = sum(r["عمال_مقدر"] for r in data if r["القطاع"] == "توصيل")
    total     = transport + delivery
    official  = 85000
    gap       = total - official
    gap_pct   = round(gap / official * 100, 1)

    print()
    print("النتيجة النهائية")
    print("=" * 62)
    print(f"  قطاع النقل          : {transport:>8,} عامل")
    print(f"  قطاع التوصيل        : {delivery:>8,} عامل")
    print("-" * 62)
    print(f"  اجمالي تقدير المرصد : {total:>8,} عامل")
    print(f"  الرسمي GASTAT       : {official:>8,} عامل")
    print(f"  الفجوة              : {gap:>8,} عامل ({gap_pct}%)")
    print("=" * 62)

    output = {
        "بيانات_التطبيقات":    data,
        "قطاع_النقل":          transport,
        "قطاع_التوصيل":        delivery,
        "اجمالي_العمال":       total,
        "الرقم_الرسمي_GASTAT": official,
        "الفجوة":              gap,
        "نسبة_الفجوة":         gap_pct,
    }
    with open("playstore_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print()
    print("تم حفظ البيانات في playstore_data.json")
