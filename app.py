import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="서울시 따릉이 데이터 분석", layout="wide")

# 2. 데이터베이스 연결 확인 함수
def check_db():
    if not os.path.exists('bicycle.db'):
        st.error("🚨 'bicycle.db' 파일을 찾을 수 없습니다! 데이터베이스 파일이 app.py와 같은 폴더에 있는지 확인해주세요.")
        st.stop()

def run_query(query):
    conn = sqlite3.connect('bicycle.db')
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# DB 체크 실행
check_db()

st.title("🚲 서울시 따릉이 이용현황 대시보드")
st.markdown("공공데이터를 활용하여 대여소별 이용 패턴과 고장 의심 자전거를 분석합니다.")

# --- 차트 1: 인기 대여소 TOP 3 vs 비인기 대여소 TOP 3 ---
st.header("1. 대여소 인기도 분석 (TOP 3 & BOTTOM 3)")

# SQL 작성
sql_top3 = """
SELECT s.보관소명, SUM(u.이용건수) as 총이용건수
FROM 이용정보 u
JOIN 대여소 s ON u.대여소번호 = s.대여소번호
GROUP BY s.보관소명
ORDER BY 총이용건수 DESC
LIMIT 3
"""

sql_bottom3 = """
SELECT s.보관소명, SUM(u.이용건수) as 총이용건수
FROM 이용정보 u
JOIN 대여소 s ON u.대여소번호 = s.대여소번호
GROUP BY s.보관소명
ORDER BY 총이용건수 ASC
LIMIT 3
"""

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 인기 대여소 TOP 3")
    df_top3 = run_query(sql_top3)
    fig_top3 = px.bar(df_top3, x='보관소명', y='총이용건수', color='총이용건수', color_continuous_scale='Reds')
    st.plotly_chart(fig_top3, use_container_width=True)
    st.code(sql_top3, language='sql')

with col2:
    st.subheader("❄️ 비인기 대여소 TOP 3")
    df_bottom3 = run_query(sql_bottom3)
    fig_bottom3 = px.bar(df_bottom3, x='보관소명', y='총이용건수', color='총이용건수', color_continuous_scale='Blues')
    st.plotly_chart(fig_bottom3, use_container_width=True)
    st.code(sql_bottom3, language='sql')

st.info("**💡 인사이트:**\n- 인기 대여소는 주로 지하철역 인근이나 유동인구가 많은 거점에 위치해 있습니다.\n- 비인기 대여소는 접근성이 떨어지거나 신설된 지 얼마 되지 않았을 가능성이 높으므로 재배치 검토가 필요할 수 있습니다.")


# --- 차트 2: 고장 의심 자전거 분석 ---
st.divider()
st.header("2. 고장 의심 자전거 발생 대여소 TOP 3")

# SQL 작성
sql_broken = """
SELECT s.보관소명, COUNT(*) as 고장의심건수
FROM 이용정보 u
JOIN 대여소 s ON u.대여소번호 = s.대여소번호
WHERE u.이용건수 = 0
GROUP BY s.보관소명
ORDER BY 고장의심건수 DESC
LIMIT 3
"""

df_broken = run_query(sql_broken)

st.subheader("🛠️ 고장 의심 자전거 수 (이용건수 0인 데이터 집계)")
fig_broken = px.bar(df_broken, x='고장의심건수', y='보관소명', orientation='h', 
                    color='고장의심건수', color_continuous_scale='Viridis')
st.plotly_chart(fig_broken, use_container_width=True)

st.code(sql_broken, language='sql')

st.info("**💡 인사이트:**\n- 이용건수가 0인 데이터가 많다는 것은 자전거가 대여소에 거치되어 있으나 고장으로 인해 대여되지 못했음을 암시합니다.\n- 해당 대여소 3곳(보관소명 기준)에 정비팀을 우선적으로 파견하여 점검을 실시하면 효율적인 운영이 가능합니다.")