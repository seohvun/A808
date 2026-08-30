import os
import json
import pandas as pd
import folium
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

# 1. Streamlit 페이지 기본 설정
st.set_page_config(
    page_title="17기 인구 시각화 프로젝트",
    page_icon="🗺️",
    layout="wide"
)

# 메인 제목 및 설명
st.title("17기는 어디에 살고 있을까?🧐")
st.subheader("서울시 법정동 및 자치구별 인구수 시각화")
st.write("By. 2026 1학기 A808 강재이, 박서현, 백서연, 심나현")

# 2. 탭(Tabs) 생성: 행정동, 지역구
tab1, tab2 = st.tabs(["🗺️ 법정동별 지도", "📊 지역구별 3D 지형"])

# ==============================================================================
# TAB 1: 행정동별 인구 지도 (Folium)
# ==============================================================================
with tab1:
    st.markdown("### 서울시 법정동별 인구수 지도")
    
    @st.cache_data
    def load_dong_data():
        base_dir = os.path.dirname(__file__)
        csv_path = os.path.join(base_dir, 'A808 프로젝트(응답) - 결과_동.csv')
        geojson_path = os.path.join(base_dir, '행정동_edited.geojson')
        
        state_data = pd.read_csv(csv_path)
        state_data['전체동이름'] = state_data['시'] + ' ' + state_data['구'] + ' ' + state_data['동']
        
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geo_json_data = json.load(f)
            
        pop_dict = dict(zip(state_data['전체동이름'], state_data['인구수']))
        
        for feature in geo_json_data['features']:
            adm_nm = feature['properties'].get('adm_nm')
            pop_value = pop_dict.get(adm_nm, 0)
            
            if pd.notna(pop_value) and pop_value != 0:
                feature['properties']['인구수_표시'] = f"{int(pop_value):,} 명"
            else:
                feature['properties']['인구수_표시'] = "데이터 없음"
                
        return state_data, geo_json_data

    state_data, geo_json_data = load_dong_data()

    # Folium 지도 작성
    m = folium.Map(location=[37.5502, 126.982], zoom_start=11)

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

    fmap.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=['adm_nm', '인구수_표시'],
            aliases=['법정동:', '인구수:'],
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

    st_folium(m, width=1000, height=600)

# ==============================================================================
# TAB 2: 지역구별 3D 인구 지형 (Plotly)
# ==============================================================================
with tab2:
    st.markdown("### 서울시 자치구별 3D 인구수 지형 그래프")
    
    @st.cache_data
    def load_gu_data():
        base_dir = os.path.dirname(__file__)
        csv_path = os.path.join(base_dir, 'A808 프로젝트(응답) - 결과_구.csv')
        
        df = pd.read_csv(csv_path)
        if 'Unnamed: 0' in df.columns:
            df = df.rename(columns={'Unnamed: 0': '자치구'})
        
        seoul_coords = {
            '강남구': (37.5172, 127.0473), '강동구': (37.5301, 127.1238),
            '강북구': (37.6396, 127.0257), '강서구': (37.5509, 126.8495),
            '관악구': (37.4784, 126.9516), '광진구': (37.5385, 127.0823),
            '구로구': (37.4954, 126.8874), '금천구': (37.4568, 126.8955),
            '노원구': (37.6542, 127.0568), '도봉구': (37.6688, 127.0471),
            '동대문구': (37.5744, 127.0400), '동작구': (37.5124, 126.9393),
            '마포구': (37.5663, 126.9016), '서대문구': (37.5791, 126.9368),
            '서초구': (37.4837, 127.0324), '성동구': (37.5635, 127.0369),
            '성북구': (37.5894, 127.0167), '송파구': (37.5145, 127.1061),
            '양천구': (37.5169, 126.8665), '영등포구': (37.5264, 126.8962),
            '용산구': (37.5326, 126.9900), '은평구': (37.6027, 126.9291),
            '종로구': (37.5730, 126.9794), '중구': (37.5641, 126.9979),
            '중랑구': (37.6066, 127.0927)
        }
        
        df['lat'] = df['자치구'].map(lambda x: seoul_coords.get(str(x).strip(), (None, None))[0])
        df['lon'] = df['자치구'].map(lambda x: seoul_coords.get(str(x).strip(), (None, None))[1])
        df = df.dropna(subset=['lat', 'lon'])
        return df

    df_gu = load_gu_data()

    # Plotly 3D 그래프 작성
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=df_gu['lon'],
        y=df_gu['lat'],
        z=df_gu['구인구수'],
        mode='markers+text',
        text=df_gu['자치구'],
        textposition="top center",
        marker=dict(
            size=df_gu['구인구수'] * 1.8 + 5,
            color=df_gu['구인구수'],
            colorscale='Viridis',
            opacity=0.85,
            showscale=True,
            colorbar=dict(title="인구수(명)")
        ),
        hovertemplate="<b>%{text}</b><br>위도: %{y}<br>경도: %{x}<br><b>인구수: %{z} 명</b><extra></extra>"
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="경도(Longitude)"),
            yaxis=dict(title="위도(Latitude)"),
            zaxis=dict(title="인구수(명)"),
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2))
        ),
        width=900,
        height=600,
        margin=dict(l=0, r=0, b=0, t=20)
    )

    st.plotly_chart(fig, use_container_width=True)

# 3. 하단 푸터 (공통 적용)
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666666; font-size: 14px; padding: 10px;'>
        <p><b>By:</b> Seohyun | <b>프로젝트:</b> A808 서울시 행정동 및 자치구 인구 시각화</p>
        <p>© 2026 All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)
