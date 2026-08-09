import heapq
import streamlit as st
import plotly.graph_objects as go

# ============================================================
# 1. PAGE CONFIG & INITIAL DATA
# ============================================================
st.set_page_config(
    page_title="구례 생활 보행 지도",
    page_icon="🚶",
    layout="wide"
)

# 초기 노드 데이터
NODES = [
    {"id": "n1", "name": "백련마을회관", "category": "주거지", "x": 40, "y": 232},
    {"id": "n7", "name": "구례군노인회관", "category": "복지시설", "x": 320, "y": 471},
    {"id": "n2", "name": "구례북초등학교", "category": "학교", "x": 51, "y": 312},
    {"id": "n8", "name": "구례공영버스터미널", "category": "정류장", "x": 272, "y": 450},
    {"id": "n3", "name": "구례5일시장", "category": "시장", "x": 325, "y": 287},
    {"id": "n4", "name": "서시천체육공원", "category": "공원", "x": 314, "y": 180},
    {"id": "n6", "name": "구례군국민체육센터", "category": "체육시설", "x": 226, "y": 70},
    {"id": "n5", "name": "구례병원", "category": "병원", "x": 149, "y": 82},
    {"id": "n9", "name": "구례중앙초등학교", "category": "학교", "x": 187, "y": 560},
    {"id": "n10", "name": "구례매천도서관", "category": "도서관", "x": 187, "y": 542},
    {"id": "n11", "name": "구례공공도서관", "category": "도서관", "x": 168, "y": 551},
    {"id": "n12", "name": "구례구역", "category": "기차역", "x": 90, "y": 615},
]

INITIAL_EDGES = [
    {"id": "e1", "startNodeId": "n1", "endNodeId": "n3", "distance": 90, "stairs": 18, "incline": "심함", "ramp": False, "sidewalk": "없음", "streetlight": False, "restArea": False},
    {"id": "e2", "startNodeId": "n3", "endNodeId": "n5", "distance": 180, "stairs": 14, "incline": "심함", "ramp": False, "sidewalk": "없음", "streetlight": True, "restArea": False},
    {"id": "e3", "startNodeId": "n1", "endNodeId": "n8", "distance": 140, "stairs": 0, "incline": "낮음", "ramp": True, "sidewalk": "양호", "streetlight": True, "restArea": True},
    {"id": "e4", "startNodeId": "n8", "endNodeId": "n4", "distance": 160, "stairs": 0, "incline": "낮음", "ramp": True, "sidewalk": "양호", "streetlight": True, "restArea": True},
    {"id": "e5", "startNodeId": "n4", "endNodeId": "n6", "distance": 120, "stairs": 0, "incline": "보통", "ramp": True, "sidewalk": "양호", "streetlight": False, "restArea": True},
    {"id": "e6", "startNodeId": "n6", "endNodeId": "n5", "distance": 150, "stairs": 0, "incline": "낮음", "ramp": True, "sidewalk": "양호", "streetlight": True, "restArea": False},
    {"id": "e7", "startNodeId": "n1", "endNodeId": "n7", "distance": 70, "stairs": 0, "incline": "낮음", "ramp": True, "sidewalk": "양호", "streetlight": True, "restArea": True},
    {"id": "e8", "startNodeId": "n7", "endNodeId": "n3", "distance": 100, "stairs": 4, "incline": "보통", "ramp": False, "sidewalk": "좁음", "streetlight": False, "restArea": False},
    {"id": "e9", "startNodeId": "n4", "endNodeId": "n2", "distance": 140, "stairs": 0, "incline": "낮음", "ramp": True, "sidewalk": "양호", "streetlight": True, "restArea": False},
    {"id": "e10", "startNodeId": "n2", "endNodeId": "n5", "distance": 110, "stairs": 6, "incline": "보통", "ramp": False, "sidewalk": "없음", "streetlight": False, "restArea": False},
    {"id": "e11", "startNodeId": "n3", "endNodeId": "n9", "distance": 90, "stairs": 0, "incline": "낮음", "ramp": True, "sidewalk": "양호", "streetlight": True, "restArea": False},
    {"id": "e12", "startNodeId": "n9", "endNodeId": "n10", "distance": 40, "stairs": 0, "incline": "낮음", "ramp": True, "sidewalk": "양호", "streetlight": True, "restArea": True},
    {"id": "e13", "startNodeId": "n9", "endNodeId": "n11", "distance": 60, "stairs": 2, "incline": "낮음", "ramp": False, "sidewalk": "좁음", "streetlight": True, "restArea": False},
    {"id": "e14", "startNodeId": "n8", "endNodeId": "n12", "distance": 850, "stairs": 0, "incline": "보통", "ramp": True, "sidewalk": "양호", "streetlight": True, "restArea": False},
]

# 스트림릿 세션 상태(State)로 간선(Edges) 관리 (수정 반영 가능하도록)
if "edges" not in st.session_state:
    st.session_state["edges"] = INITIAL_EDGES

# 데이터 빠르게 조회용 dict 생성
node_by_id = {n["id"]: n for n in NODES}
node_name_to_id = {n["name"]: n["id"] for n in NODES}

# ============================================================
# 2. LOGIC FUNCTIONS
# ============================================================
INCLINE_ORDER = {"낮음": 0, "보통": 1, "심함": 2}

def calc_score(e):
    """보행 편의성 점수 계산 (0~100점)"""
    s = 100
    s -= e["stairs"] * 2
    s -= 15 if e["incline"] == "심함" else (5 if e["incline"] == "보통" else 0)
    s -= 20 if e["sidewalk"] == "없음" else (10 if e["sidewalk"] == "좁음" else 0)
    if e["ramp"]: s += 5
    if e["streetlight"]: s += 5
    if e["restArea"]: s += 5
    return max(0, min(100, s))

def score_color(score):
    if score >= 80: return "#3FA65B"
    if score >= 50: return "#E8B93A"
    if score >= 30: return "#E2792B"
    return "#D8483C"

def calc_comfort_cost(e):
    """가중 다익스트라용 Comfort Cost"""
    c = e["distance"]
    c += e["stairs"] * 40
    c += 60 if e["incline"] == "심함" else (20 if e["incline"] == "보통" else 0)
    c += 60 if e["sidewalk"] == "없음" else (25 if e["sidewalk"] == "좁음" else 0)
    if e["ramp"]: c -= 10
    if e["streetlight"]: c -= 5
    if e["restArea"]: c -= 5
    return max(1, c)

def dijkstra(nodes, edges, start_id, end_id, weight_fn):
    adj = {n["id"]: [] for n in nodes}
    for e in edges:
        adj[e["startNodeId"]].append((e["endNodeId"], e))
        adj[e["endNodeId"]].append((e["startNodeId"], e))

    distances = {n["id"]: float('inf') for n in nodes}
    distances[start_id] = 0
    pq = [(0, start_id, [])]
    visited = set()

    while pq:
        curr_dist, u, path = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        if u == end_id:
            return path

        for neighbor, edge in adj[u]:
            w = weight_fn(edge)
            if curr_dist + w < distances[neighbor]:
                distances[neighbor] = curr_dist + w
                heapq.heappush(pq, (curr_dist + w, neighbor, path + [edge["id"]]))
    return None

def summarize_route(edge_ids, edges):
    list_edges = [next(e for e in edges if e["id"] == eid) for eid in edge_ids]
    distance = sum(e["distance"] for e in list_edges)
    stairs = sum(e["stairs"] for e in list_edges)
    worst_incline = max(list_edges, key=lambda e: INCLINE_ORDER[e["incline"]])["incline"] if list_edges else "낮음"
    score = round(sum(calc_score(e) * e["distance"] for e in list_edges) / distance) if distance > 0 else 100
    time = max(1, round(distance / 50 + stairs * 0.3))
    return {
        "edge_ids": edge_ids,
        "edges": list_edges,
        "distance": distance,
        "stairs": stairs,
        "worstIncline": worst_incline,
        "score": score,
        "time": time
    }

# ============================================================
# 3. SIDEBAR CONTROLS & ROUTE SEARCH
# ============================================================
st.sidebar.title("🚶 구례 생활 보행 지도")
st.sidebar.caption("Gurye Accessible Pedestrian Route & Map")

node_names = [n["name"] for n in NODES]
origin_name = st.sidebar.selectbox("출발지 선택", node_names, index=0)
dest_name = st.sidebar.selectbox("도착지 선택", node_names, index=7)

origin_id = node_name_to_id[origin_name]
dest_id = node_name_to_id[dest_name]

routes = None
if origin_id != dest_id:
    short_ids = dijkstra(NODES, st.session_state["edges"], origin_id, dest_id, lambda e: e["distance"])
    comf_ids = dijkstra(NODES, st.session_state["edges"], origin_id, dest_id, calc_comfort_cost)
    if short_ids and comf_ids:
        routes = {
            "short": summarize_route(short_ids, st.session_state["edges"]),
            "comfortable": summarize_route(comf_ids, st.session_state["edges"])
        }
else:
    st.sidebar.warning("출발지와 도착지를 다르게 선택해 주세요.")

# ============================================================
# 4. MAIN LAYOUT: ROUTES & MAP
# ============================================================
col_info, col_map = st.columns([1, 1.2])

with col_info:
    st.subheader("📍 경로 비교")
    
    selected_route_key = "comfortable"
    if routes:
        tab1, tab2 = st.tabs(["⭐ 편한 길 (추천)", "🚀 최단 거리 경로"])
        
        def render_route_card(r, is_recommend=False):
            sc = r['score']
            color = scoreColor(sc)
            st.markdown(f"### 편의성 점수: <span style='color:{color}; font-size:28px;'>**{sc}점**</span>", unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("거리", f"{r['distance']}m")
            m2.metric("계단", f"{r['stairs']}개")
            m3.metric("최고 경사", r['worstIncline'])
            m4.metric("소요시간", f"{r['time']}분")

            if r['stairs'] > 0:
                st.warning(f"⚠️ 계단이 {r['stairs']}개 포함되어 있습니다. (휠체어/유모차 유의)")

        with tab1:
            render_route_card(routes["comfortable"], is_recommend=True)
            selected_route_key = "comfortable"

        with tab2:
            render_route_card(routes["short"])
            if st.button("최단 경로를 지도에 표시"):
                selected_route_key = "short"

    # 제보 기능
    st.markdown("---")
    st.subheader("📝 보행 환경 제보하기")
    with st.expander("현장 상태 업데이트하기"):
        edge_options = {
            f"{node_by_id[e['startNodeId']]['name']} ↔ {node_by_id[e['endNodeId']]['name']}": e['id']
            for e in st.session_state["edges"]
        }
        selected_edge_label = st.selectbox("제보할 구간 선택", list(edge_options.keys()))
        selected_edge_id = edge_options[selected_edge_label]
        
        target_edge = next(e for e in st.session_state["edges"] if e["id"] == selected_edge_id)
        
        with st.form("edit_edge_form"):
            new_stairs = st.slider("계단 개수", 0, 30, value=target_edge["stairs"])
            new_incline = st.radio("경사도", ["낮음", "보통", "심함"], index=["낮음", "보통", "심함"].index(target_edge["incline"]), horizontal=True)
            new_sidewalk = st.radio("보도 상태", ["양호", "좁음", "없음"], index=["양호", "좁음", "없음"].index(target_edge["sidewalk"]), horizontal=True)
            
            c1, c2, c3 = st.columns(3)
            new_ramp = c1.checkbox("경사로", value=target_edge["ramp"])
            new_streetlight = c2.checkbox("가로등", value=target_edge["streetlight"])
            new_rest_area = c3.checkbox("휴식공간", value=target_edge["restArea"])
            
            if st.form_submit_button("저장 및 지도 반영"):
                for e in st.session_state["edges"]:
                    if e["id"] == selected_edge_id:
                        e["stairs"] = new_stairs
                        e["incline"] = new_incline
                        e["sidewalk"] = new_sidewalk
                        e["ramp"] = new_ramp
                        e["streetlight"] = new_streetlight
                        e["restArea"] = new_rest_area
                st.success("정보가 반영되었습니다!")
                st.rerun()

# ============================================================
# 5. MAP VISUALIZATION (PLOTLY)
# ============================================================
with col_map:
    st.subheader("🗺️ 구례 보행 지도")
    
    fig = go.Figure()
    active_edge_ids = set(routes[selected_route_key]["edge_ids"]) if routes else set()

    # 간선(Edges) 그리기
    for e in st.session_state["edges"]:
        a = node_by_id[e["startNodeId"]]
        b = node_by_id[e["endNodeId"]]
        sc = calc_score(e)
        color = scoreColor(sc)
        
        is_active = e["id"] in active_edge_ids
        width = 8 if is_active else 4
        opacity = 1.0 if is_active else 0.4
        
        fig.add_trace(go.Scatter(
            x=[a["x"], b["x"]],
            y=[-a["y"], -b["y"]],  # Y축 반전 (웹 좌표계 맞춤)
            mode="lines",
            line=dict(color=color, width=width),
            opacity=opacity,
            hoverinfo="text",
            text=f"구간: {a['name']} - {b['name']}<br>점수: {sc}점 (계단:{e['stairs']}개, 경사:{e['incline']})",
            showlegend=False
        ))

    # 노드(Nodes) 그리기
    node_x = [n["x"] for n in NODES]
    node_y = [-n["y"] for n in NODES]
    node_text = [n["name"] for n in NODES]
    
    node_colors = []
    for n in NODES:
        if n["id"] == origin_id: node_colors.append("#2F6F4E")
        elif n["id"] == dest_id: node_colors.append("#E0862E")
        else: node_colors.append("#5C6B62")

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(size=14, color=node_colors, line=dict(color="white", width=2)),
        text=node_text,
        textposition="bottom center",
        hoverinfo="text",
        showlegend=False
    ))

    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=10, r=10, t=10, b=10),
        height=620,
        plot_bgcolor="#EEF2ED"
    )

    st.plotly_chart(fig, use_container_width=True)