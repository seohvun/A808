import json
import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium

# 1. Streamlit 페이지 기본 설정
st.set_page_config(
    page_title="17기는 어디에 살고 있을까?🧐",
    page_icon="🗺️",
    layout="wide"
)

# 메인 화면 제목 및 설명
st.title("17기는 어디에 살고 있을까?🧐")
st.write("서울시 행정동별 인구수 시각화")
st.write("By. 2026 1학기 A808 강재이, 박서현, 백서연, 심나현")

# 2. 데이터 불러오기 및 가공
@st.cache_data
def load_data():  # ◀ 오타 'ㄴ' 제거 완료!
    # CSV 데이터 불러오기 및 전체동이름 생성
    state_data = pd.read_csv('A808 프로젝트(응답) - 결과_동.csv')
    state_data['전체동이름'] = state_data['시'] + ' ' + state_data['구'] + ' ' + state_data['동']
    
    # GeoJSON 데이터 불러오기
    with open('행정동_edited.geojson', 'r', encoding='utf-8') as f:
        geo_json_data = json.load(f)
        
    # GeoJSON 속성에 CSV의 인구수 데이터 매핑하기
    pop_dict = dict(zip(state_data['전체동이름'], state_data['인구수']))
    
    # GeoJSON의 각 행정동(feature) 속성에 인구수 정보를 추가
    for feature in geo_json_data['features']:
        adm_nm = feature['properties'].get('adm_nm')
        pop_value = pop_dict.get(adm_nm, 0)
        
        # 툴팁에 보기 좋게 출력되도록 천 단위 쉼표(,)와 '명'을 붙인 문자열 저장
        if pd.notna(pop_value) and pop_value != 0:
            feature['properties']['인구수_표시'] = f"{int(pop_value):,} 명"
        else:
            feature['properties']['인구수_표시'] = "데이터 없음"
            
    return state_data, geo_json_data

# 데이터 로딩 실행
state_data, geo_json_data = load_data()

# 3. Folium 지도 객체 생성
m = folium.Map(location=[37.5502, 126.982], zoom_start=11)

# Choropleth 타일 추가
fmap = folium.Choropleth(
    geo_data=geo_json_data, 
    data=state_data, 
    columns=['전체동이름', '인구수'], 
    key_on='feature.properties.adm_nm',
    nan_fill_color='#FFFFFF',
    fill_color='Blues',
    fill_opacity=0.8, 
    line_opacity=0.3, 
    legend_name='인구수 (명)',
    threshold_scale=[x for x in range(0, 11)],
).add_to(m)

# 툴팁(Tooltip) 추가: 행정동 이름과 인구수 표시
fmap.geojson.add_child(
    folium.features.GeoJsonTooltip(
        fields=['adm_nm', '인구수_표시'],
        aliases=['행정동:', '인구수:'],
        labels=True,
        style="""
            background-color: white;
            color: #333333;
            font-family: arial;
            font-size: 13px;
            padding: 8px;
            border-radius: 4px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        """
    )
)

# 4. Streamlit 화면에 지도 렌더링
st_folium(m, width=1000, height=600)

# 페이지 하단 제작자 이름 (Footer) 추가
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666666; font-size: 14px; padding: 10px;'>
        <p><b>By:</b> Seohyun | <b>프로젝트:</b> A808 서울시 행정동별 인구 시각화</p>
        <p>© 2026 All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)