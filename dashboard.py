import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.insert(0, ".")
from data_collector import estimate_all_sectors, get_regional_distribution, get_growth_timeline

st.set_page_config(page_title="رادار القوى العاملة الرقمية", layout="wide")

st.markdown("""
<style>
@import url("https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap");
* { font-family: Tajawal, sans-serif !important; direction: rtl; }
.sector-card { border-radius: 16px; padding: 20px; text-align: center; color: white; margin: 6px; }
.big-number { font-size: 2.2rem; font-weight: 900; }
.label { font-size: 0.9rem; opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    summary, all_df, by_sector, trends_df, playstore_df = estimate_all_sectors()
    regions = get_regional_distribution()
    growth  = get_growth_timeline()
    return summary, all_df, by_sector, trends_df, playstore_df, regions, growth

with st.spinner("جاري تحميل البيانات..."):
    summary, all_df, by_sector, trends_df, playstore_df, regions_df, growth_df = load_data()

st.markdown("## رادار القوى العاملة الرقمية")
st.markdown("##### مرصد ذكي لاقتصاد المنصات - المملكة العربية السعودية")
st.markdown("---")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("تقدير المرصد الكلي", f"{summary['اجمالي_تقدير_المرصد']:,}", "عامل نشط")
with c2:
    st.metric("الرقم الرسمي GASTAT", f"{summary['الرقم_الرسمي_GASTAT']:,}", "عامل مسجل")
with c3:
    st.metric("فجوة الرصد", f"{summary['فجوة_الرصد']:,}", f"+{summary['نسبة_الفجوة']}% غير مرصودة")

st.markdown("---")
st.markdown("### تفصيل العمالة حسب القطاع")

colors = {"نقل": "#2d6a9f", "توصيل": "#27ae60", "عمل حر": "#8e44ad"}
cols = st.columns(3)
for i, row in by_sector.iterrows():
    with cols[i % 3]:
        color = colors.get(row["القطاع"], "#555")
        st.markdown(f"""
        <div class="sector-card" style="background:{color}">
            <div class="big-number">{row["اجمالي_العمال"]:,}</div>
            <div class="label">{row["القطاع"]} - {row["النسبة"]}% من الاجمالي</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### نمو العمالة الرقمية مقابل الرقم الرسمي")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=growth_df["السنة"], y=growth_df["تقدير_المرصد"],
        name="تقدير المرصد", line=dict(color="#2d6a9f", width=3),
        fill="tozeroy", fillcolor="rgba(45,106,159,0.1)"))
    fig.add_trace(go.Scatter(x=growth_df["السنة"], y=growth_df["الرقم_الرسمي"],
        name="الرسمي GASTAT", line=dict(color="#e67e22", width=3, dash="dash")))
    fig.update_layout(height=320, paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", y=1.12), font=dict(family="Tajawal"))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### توزيع القطاعات")
    fig2 = px.pie(by_sector, values="اجمالي_العمال", names="القطاع",
        color="القطاع", color_discrete_map=colors, hole=0.5)
    fig2.update_layout(height=320, font=dict(family="Tajawal"),
        legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns([2, 3])
with col3:
    st.markdown("### تقدير العمال حسب المنصة")
    fig3 = px.bar(all_df.sort_values("عمال_مقدر_معدل"),
        x="عمال_مقدر_معدل", y="المنصة", color="القطاع",
        color_discrete_map=colors, orientation="h",
        labels={"عمال_مقدر_معدل": "عدد العمال", "المنصة": ""})
    fig3.update_layout(height=320, paper_bgcolor="white",
        font=dict(family="Tajawal"), legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("### مؤشر الاتجاه الرقمي - Google Trends")
    fig4 = go.Figure()
    colors_trend = ["#2d6a9f", "#27ae60", "#8e44ad", "#e67e22", "#c0392b"]
    for i, col in enumerate(trends_df.columns[:5]):
        fig4.add_trace(go.Scatter(x=trends_df.index, y=trends_df[col],
            name=col, line=dict(color=colors_trend[i], width=2)))
    fig4.update_layout(height=320, paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", y=1.12), font=dict(family="Tajawal"))
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("### منهجية التقدير")
tab1, tab2, tab3 = st.tabs(["النقل", "التوصيل", "العمل الحر"])
with tab1:
    st.info("تقييمات شهرية / 2% معدل التقييم = رحلات يومية / 8 رحلات لكل سائق = عدد السائقين النشطين")
with tab2:
    st.info("تقييمات شهرية / 2% معدل التقييم = طلبات يومية / 11 طلب لكل موصل = عدد الموصلين النشطين")
with tab3:
    st.info("مشاريع نشطة شهريا / 2.7 مشروع لكل مستقل = عدد المستقلين النشطين")

st.caption(f"اخر تحديث: {summary['تاريخ_التقدير']} | هاكاثون الابتكار في البيانات - الطريق الى الرياض 2026")
