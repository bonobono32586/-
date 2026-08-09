import React, { useState, useEffect, useMemo } from "react";
import {
  MapPin, Navigation, Route as RouteIcon, Layers, Plus, X, ChevronDown,
  AlertTriangle, Clock, Footprints, Star, Lightbulb, Armchair, Accessibility,
  Check, Home, GraduationCap, ShoppingBag, TreePine, Stethoscope, Train,
  Users, Bus, ArrowUpDown, MousePointerClick, Building2, BookOpen,
} from "lucide-react";

/* ============================================================
# 1. MOCK DATA - Node / Edge schema
   ============================================================ */

const NODES = [
  { id: "n1", name: "백련마을회관", category: "주거지", lat: 35.2058, lng: 127.4560, x: 40, y: 232 },
  { id: "n7", name: "구례군노인회관", category: "복지시설", lat: 35.2003, lng: 127.4658, x: 320, y: 471 },
  { id: "n2", name: "구례북초등학교", category: "학교", lat: 35.2038, lng: 127.4610, x: 51, y: 312 },
  { id: "n8", name: "구례공영버스터미널", category: "정류장", lat: 35.2005, lng: 127.4649, x: 272, y: 450 },
  { id: "n3", name: "구례5일시장", category: "시장", lat: 35.2035, lng: 127.4646, x: 325, y: 287 },
  { id: "n4", name: "서시천체육공원", category: "공원", lat: 35.2079, lng: 127.4655, x: 314, y: 180 },
  { id: "n6", name: "구례군국민체육센터", category: "체육시설", lat: 35.2087, lng: 127.4638, x: 226, y: 70 },
  { id: "n5", name: "구례병원", category: "병원", lat: 35.2065, lng: 127.4636, x: 149, y: 82 },
  { id: "n9", name: "구례중앙초등학교", category: "학교", lat: 35.1998, lng: 127.4630, x: 187, y: 560 },
  { id: "n10", name: "구례매천도서관", category: "도서관", lat: 35.1996, lng: 127.4633, x: 187, y: 542 },
  { id: "n11", name: "구례공공도서관", category: "도서관", lat: 35.1999, lng: 127.4627, x: 168, y: 551 },
  { id: "n12", name: "구례구역", category: "기차역", lat: 35.1762, lng: 127.4581, x: 90, y: 615 },
];
// Node positions are cross-referenced from the two uploaded Naver Map screenshots:
// the downtown POIs (n1–n11) keep their real relative bearing to one another (same
// scale for x and y, no rotation), read off the detailed 구례읍내 map. 구례구역(n12)
// is genuinely ~5.5km south-west of downtown (in Suncheon, across the river), which
// would push it far off this canvas at true scale — so it's pulled in near the bottom
// edge to preserve "far south, slightly west" direction rather than exact distance.

const INITIAL_EDGES = [
  { id: "e1", startNodeId: "n1", endNodeId: "n3", distance: 90, stairs: 18, incline: "심함", ramp: false, sidewalk: "없음", streetlight: false, restArea: false },
  { id: "e2", startNodeId: "n3", endNodeId: "n5", distance: 180, stairs: 14, incline: "심함", ramp: false, sidewalk: "없음", streetlight: true, restArea: false },
  { id: "e3", startNodeId: "n1", endNodeId: "n8", distance: 140, stairs: 0, incline: "낮음", ramp: true, sidewalk: "양호", streetlight: true, restArea: true },
  { id: "e4", startNodeId: "n8", endNodeId: "n4", distance: 160, stairs: 0, incline: "낮음", ramp: true, sidewalk: "양호", streetlight: true, restArea: true },
  { id: "e5", startNodeId: "n4", endNodeId: "n6", distance: 120, stairs: 0, incline: "보통", ramp: true, sidewalk: "양호", streetlight: false, restArea: true },
  { id: "e6", startNodeId: "n6", endNodeId: "n5", distance: 150, stairs: 0, incline: "낮음", ramp: true, sidewalk: "양호", streetlight: true, restArea: false },
  { id: "e7", startNodeId: "n1", endNodeId: "n7", distance: 70, stairs: 0, incline: "낮음", ramp: true, sidewalk: "양호", streetlight: true, restArea: true },
  { id: "e8", startNodeId: "n7", endNodeId: "n3", distance: 100, stairs: 4, incline: "보통", ramp: false, sidewalk: "좁음", streetlight: false, restArea: false },
  { id: "e9", startNodeId: "n4", endNodeId: "n2", distance: 140, stairs: 0, incline: "낮음", ramp: true, sidewalk: "양호", streetlight: true, restArea: false },
  { id: "e10", startNodeId: "n2", endNodeId: "n5", distance: 110, stairs: 6, incline: "보통", ramp: false, sidewalk: "없음", streetlight: false, restArea: false },
  { id: "e11", startNodeId: "n3", endNodeId: "n9", distance: 90, stairs: 0, incline: "낮음", ramp: true, sidewalk: "양호", streetlight: true, restArea: false },
  { id: "e12", startNodeId: "n9", endNodeId: "n10", distance: 40, stairs: 0, incline: "낮음", ramp: true, sidewalk: "양호", streetlight: true, restArea: true },
  { id: "e13", startNodeId: "n9", endNodeId: "n11", distance: 60, stairs: 2, incline: "낮음", ramp: false, sidewalk: "좁음", streetlight: true, restArea: false },
  { id: "e14", startNodeId: "n8", endNodeId: "n12", distance: 850, stairs: 0, incline: "보통", ramp: true, sidewalk: "양호", streetlight: true, restArea: false },
];

const CATEGORY_META = {
  주거지: { icon: Home },
  학교: { icon: GraduationCap },
  시장: { icon: ShoppingBag },
  공원: { icon: TreePine },
  병원: { icon: Stethoscope },
  체육시설: { icon: Building2 },
  복지시설: { icon: Users },
  정류장: { icon: Bus },
  도서관: { icon: BookOpen },
  기차역: { icon: Train },
};

/* ============================================================
   2. SCORING & COMFORT-COST LOGIC
   ============================================================ */

function calcScore(e) {
  let s = 100;
  s -= e.stairs * 2;
  s -= e.incline === "심함" ? 15 : e.incline === "보통" ? 5 : 0;
  s -= e.sidewalk === "없음" ? 20 : e.sidewalk === "좁음" ? 10 : 0;
  if (e.ramp) s += 5;
  if (e.streetlight) s += 5;
  if (e.restArea) s += 5;
  return Math.max(0, Math.min(100, s));
}

function scoreColor(score) {
  if (score >= 80) return "#3FA65B";
  if (score >= 50) return "#E8B93A";
  if (score >= 30) return "#E2792B";
  return "#D8483C";
}

function scoreLabel(score) {
  if (score >= 80) return "양호";
  if (score >= 50) return "보통";
  if (score >= 30) return "주의";
  return "위험 구간";
}

// Weighted cost used only for finding the "comfortable" route — not the display score.
function comfortCost(e) {
  let c = e.distance;
  c += e.stairs * 40;
  c += e.incline === "심함" ? 60 : e.incline === "보통" ? 20 : 0;
  c += e.sidewalk === "없음" ? 60 : e.sidewalk === "좁음" ? 25 : 0;
  if (e.ramp) c -= 10;
  if (e.streetlight) c -= 5;
  if (e.restArea) c -= 5;
  return Math.max(1, c);
}

/* ============================================================
   3. ROUTING — plain Dijkstra over the mock graph
   ============================================================ */

function dijkstra(nodes, edges, startId, endId, weightFn) {
  const adj = {};
  nodes.forEach((n) => (adj[n.id] = []));
  edges.forEach((e) => {
    adj[e.startNodeId].push({ to: e.endNodeId, edge: e });
    adj[e.endNodeId].push({ to: e.startNodeId, edge: e });
  });

  const dist = {};
  const prevEdge = {};
  const prevNode = {};
  const visited = new Set();
  nodes.forEach((n) => (dist[n.id] = Infinity));
  dist[startId] = 0;

  while (true) {
    let u = null;
    let best = Infinity;
    for (const n of nodes) {
      if (!visited.has(n.id) && dist[n.id] < best) {
        best = dist[n.id];
        u = n.id;
      }
    }
    if (u === null || u === endId) break;
    visited.add(u);
    for (const { to, edge } of adj[u]) {
      const w = weightFn(edge);
      if (dist[u] + w < dist[to]) {
        dist[to] = dist[u] + w;
        prevEdge[to] = edge;
        prevNode[to] = u;
      }
    }
  }

  if (dist[endId] === Infinity) return null;
  const edgeIds = [];
  let cur = endId;
  while (cur !== startId) {
    const e = prevEdge[cur];
    if (!e) return null;
    edgeIds.unshift(e.id);
    cur = prevNode[cur];
  }
  return { edgeIds };
}

const INCLINE_ORDER = { 낮음: 0, 보통: 1, 심함: 2 };

function summarizeRoute(edgeIds, edges) {
  const list = edgeIds.map((id) => edges.find((e) => e.id === id));
  const distance = list.reduce((a, e) => a + e.distance, 0);
  const stairs = list.reduce((a, e) => a + e.stairs, 0);
  const worstIncline = list.reduce(
    (w, e) => (INCLINE_ORDER[e.incline] > INCLINE_ORDER[w] ? e.incline : w),
    "낮음"
  );
  const score =
    distance > 0
      ? Math.round(list.reduce((a, e) => a + calcScore(e) * e.distance, 0) / distance)
      : 100;
  const time = Math.max(1, Math.round(distance / 50 + stairs * 0.3));
  return { edgeIds, edges: list, distance, stairs, worstIncline, score, time };
}

/* ============================================================
   4. SMALL UI PRIMITIVES
   ============================================================ */

function IconBadge({ Icon, size = 14, color = "var(--ink)" }) {
  return <Icon size={size} color={color} strokeWidth={2.2} />;
}

function SegButton({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className="flex-1 rounded-lg px-2 py-2 text-xs font-semibold transition-colors"
      style={{
        background: active ? "var(--brand)" : "var(--surface-2)",
        color: active ? "#FFFFFF" : "var(--ink-2)",
        fontFamily: "var(--font-body)",
      }}
    >
      {children}
    </button>
  );
}

function ToggleSwitch({ label, Icon, checked, onChange }) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className="flex items-center justify-between w-full rounded-lg px-3 py-2.5"
      style={{ background: "var(--surface-2)" }}
    >
      <span className="flex items-center gap-2 text-sm" style={{ color: "var(--ink)", fontFamily: "var(--font-body)" }}>
        <IconBadge Icon={Icon} size={16} color="var(--ink-2)" />
        {label}
      </span>
      <span
        className="relative inline-flex items-center rounded-full transition-colors"
        style={{ width: 38, height: 22, background: checked ? "var(--brand)" : "#C7D0CA" }}
      >
        <span
          className="absolute rounded-full bg-white transition-transform"
          style={{
            width: 16, height: 16, top: 3,
            transform: checked ? "translateX(19px)" : "translateX(3px)",
          }}
        />
      </span>
    </button>
  );
}

/* ============================================================
   5. MAIN APP
   ============================================================ */

export default function App() {
  const [edges, setEdges] = useState(INITIAL_EDGES);
  const [originId, setOriginId] = useState("n1");
  const [destId, setDestId] = useState("n5");
  const [routes, setRoutes] = useState(null);
  const [activeKey, setActiveKey] = useState("comfortable");
  const [heatmapOn, setHeatmapOn] = useState(true);

  const [modalOpen, setModalOpen] = useState(false);
  const [pickingEdge, setPickingEdge] = useState(false);
  const [modalEdgeId, setModalEdgeId] = useState(null);
  const [form, setForm] = useState({ stairs: 0, incline: "낮음", sidewalk: "양호", ramp: false, streetlight: false, restArea: false });
  const [savedFlash, setSavedFlash] = useState(false);

  useEffect(() => {
    if (originId === destId) { setRoutes(null); return; }
    const shortR = dijkstra(NODES, edges, originId, destId, (e) => e.distance);
    const comfR = dijkstra(NODES, edges, originId, destId, (e) => comfortCost(e));
    if (!shortR || !comfR) { setRoutes(null); return; }
    setRoutes({
      short: summarizeRoute(shortR.edgeIds, edges),
      comfortable: summarizeRoute(comfR.edgeIds, edges),
    });
  }, [originId, destId, edges]);

  const nodeById = useMemo(() => Object.fromEntries(NODES.map((n) => [n.id, n])), []);
  const activeRoute = routes ? routes[activeKey] : null;
  const activeEdgeIdSet = useMemo(
    () => new Set(activeRoute ? activeRoute.edgeIds : []),
    [activeRoute]
  );

  function swapOriginDest() {
    setOriginId(destId);
    setDestId(originId);
  }

  function openModalForEdge(edgeId) {
    const e = edges.find((x) => x.id === edgeId);
    if (!e) return;
    setModalEdgeId(edgeId);
    setForm({ stairs: e.stairs, incline: e.incline, sidewalk: e.sidewalk, ramp: e.ramp, streetlight: e.streetlight, restArea: e.restArea });
    setModalOpen(true);
    setPickingEdge(false);
  }

  function openModalFresh() {
    setModalEdgeId(edges[0]?.id ?? null);
    if (edges[0]) {
      const e = edges[0];
      setForm({ stairs: e.stairs, incline: e.incline, sidewalk: e.sidewalk, ramp: e.ramp, streetlight: e.streetlight, restArea: e.restArea });
    }
    setModalOpen(true);
    setPickingEdge(false);
  }

  function handleEdgeClickOnMap(edgeId) {
    if (modalOpen && pickingEdge) {
      openModalForEdge(edgeId);
      return;
    }
  }

  function handleSave() {
    if (!modalEdgeId) return;
    setEdges((prev) => prev.map((e) => (e.id === modalEdgeId ? { ...e, ...form } : e)));
    setModalOpen(false);
    setSavedFlash(true);
    setTimeout(() => setSavedFlash(false), 2200);
  }

  const routeCardMeta = [
    { key: "short", label: "최단 거리 경로", Icon: RouteIcon, tag: null },
    { key: "comfortable", label: "편한 길 (추천)", Icon: Star, tag: "추천" },
  ];

  return (
    <div
      className="w-full min-h-screen flex flex-col md:flex-row"
      style={{
        "--bg": "#EEF2ED",
        "--surface": "#FFFFFF",
        "--surface-2": "#F3F6F2",
        "--ink": "#142B22",
        "--ink-2": "#5C6B62",
        "--brand": "#2F6F4E",
        "--accent": "#E0862E",
        "--border": "#DCE3DD",
        "--font-display": "'Space Grotesk', sans-serif",
        "--font-body": "'Inter', sans-serif",
        "--font-mono": "'IBM Plex Mono', monospace",
        background: "var(--bg)",
        fontFamily: "var(--font-body)",
        color: "var(--ink)",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: #C7D0CA; border-radius: 999px; }
        .edge-line { cursor: pointer; transition: stroke-width 0.15s ease, opacity 0.15s ease; }
        .edge-line:hover { opacity: 0.85; }
        .mono { font-family: var(--font-mono); }
        .display { font-family: var(--font-display); }
        @keyframes dashmove { to { stroke-dashoffset: -24; } }
        .footpath { animation: dashmove 1.4s linear infinite; }
        @media (prefers-reduced-motion: reduce) { .footpath { animation: none; } }
      `}</style>

      {/* ============ MAP AREA ============ */}
      <div className="relative w-full md:w-[58%] md:order-2 md:h-screen md:sticky md:top-0">
        <div className="px-4 pt-4 pb-2 flex items-center justify-between md:hidden">
          <div>
            <h1 className="display text-lg font-semibold leading-tight">구례 생활 보행 지도</h1>
            <p className="text-xs" style={{ color: "var(--ink-2)" }}>Gurye Accessible Pedestrian Route &amp; Map</p>
          </div>
        </div>

        <div className="relative mx-3 mb-3 rounded-2xl overflow-hidden" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          {/* Heatmap toggle + legend */}
          <div className="absolute top-3 left-3 right-3 z-10 flex items-center justify-between gap-2">
            <button
              onClick={() => setHeatmapOn((v) => !v)}
              className="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold shadow-sm"
              style={{ background: heatmapOn ? "var(--brand)" : "var(--surface)", color: heatmapOn ? "#fff" : "var(--ink-2)", border: "1px solid var(--border)" }}
            >
              <IconBadge Icon={Layers} size={14} color={heatmapOn ? "#fff" : "var(--ink-2)"} />
              편의성 레이어
            </button>
            {pickingEdge && (
              <span className="flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-semibold shadow-sm" style={{ background: "var(--accent)", color: "#fff" }}>
                <IconBadge Icon={MousePointerClick} size={14} color="#fff" />
                구간을 탭하세요
              </span>
            )}
          </div>

          <svg viewBox="0 0 380 640" className="w-full h-[62vh] md:h-screen block">
            <rect x="0" y="0" width="380" height="640" fill="var(--surface)" />
            {/* Jirisan ridge silhouette — grounds the map in Gurye's setting */}
            <path
              d="M0,120 L40,95 L75,112 L110,70 L150,100 L195,55 L235,95 L270,78 L310,102 L345,80 L380,100 L380,0 L0,0 Z"
              fill="#EAF0E7"
            />
            <path
              d="M0,140 L50,118 L95,132 L140,100 L180,125 L225,90 L265,120 L305,105 L345,128 L380,112 L380,0 L0,0 Z"
              fill="#F3F6F0"
            />
            {/* faint grid to suggest streets */}
            {Array.from({ length: 9 }).map((_, i) => (
              <line key={"gh" + i} x1="0" x2="380" y1={i * 80} y2={i * 80} stroke="#EEF1EC" strokeWidth="1" />
            ))}
            {Array.from({ length: 7 }).map((_, i) => (
              <line key={"gv" + i} x1={i * 63} x2={i * 63} y1="0" y2="640" stroke="#EEF1EC" strokeWidth="1" />
            ))}

            {/* Edges */}
            {edges.map((e) => {
              const a = nodeById[e.startNodeId];
              const b = nodeById[e.endNodeId];
              const score = calcScore(e);
              const color = heatmapOn ? scoreColor(score) : "#C7D0CA";
              const mx = (a.x + b.x) / 2;
              const my = (a.y + b.y) / 2;
              return (
                <g key={e.id}>
                  <line
                    className="edge-line"
                    x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                    stroke={color} strokeWidth={7} strokeLinecap="round"
                    onClick={() => handleEdgeClickOnMap(e.id)}
                  />
                  {activeEdgeIdSet.has(e.id) && (
                    <line
                      className="footpath"
                      x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                      stroke="var(--ink)" strokeWidth={3.5} strokeLinecap="round"
                      strokeDasharray="1 11"
                    />
                  )}
                  {e.stairs > 0 && (
                    <g>
                      <circle cx={mx} cy={my} r="9" fill="#FFFFFF" stroke={color} strokeWidth="2" />
                      <text x={mx} y={my + 3} textAnchor="middle" fontSize="8" className="mono" fontWeight="600" fill="var(--ink)">
                        {e.stairs}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}

            {/* Nodes */}
            {NODES.map((n) => {
              const isOrigin = n.id === originId;
              const isDest = n.id === destId;
              const meta = CATEGORY_META[n.category] || { icon: MapPin };
              return (
                <g key={n.id} onClick={() => n.id !== originId && setDestId(n.id)} style={{ cursor: "pointer" }}>
                  {(isOrigin || isDest) && (
                    <circle cx={n.x} cy={n.y} r="17" fill="none" stroke={isOrigin ? "var(--brand)" : "var(--accent)"} strokeWidth="2.5" />
                  )}
                  <circle cx={n.x} cy={n.y} r="12" fill="var(--surface)" stroke={isOrigin || isDest ? (isOrigin ? "var(--brand)" : "var(--accent)") : "var(--ink-2)"} strokeWidth="1.6" />
                  <foreignObject x={n.x - 7} y={n.y - 7} width="14" height="14">
                    <meta.icon size={14} color={isOrigin ? "#2F6F4E" : isDest ? "#E0862E" : "#5C6B62"} strokeWidth={2.2} />
                  </foreignObject>
                  <text x={n.x} y={n.y + 26} textAnchor="middle" fontSize="9" fontWeight="600" fill="var(--ink)">
                    {n.name}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Legend */}
          <div className="flex items-center gap-3 px-3 py-2 flex-wrap" style={{ borderTop: "1px solid var(--border)", background: "var(--surface-2)" }}>
            {[
              { c: "#3FA65B", l: "양호 80+" },
              { c: "#E8B93A", l: "보통 50~79" },
              { c: "#E2792B", l: "주의 30~49" },
              { c: "#D8483C", l: "위험 <30" },
            ].map((it) => (
              <span key={it.l} className="flex items-center gap-1 text-[10px]" style={{ color: "var(--ink-2)" }}>
                <span style={{ width: 9, height: 9, borderRadius: 999, background: it.c, display: "inline-block" }} />
                {it.l}
              </span>
            ))}
            <span className="text-[10px] ml-auto" style={{ color: "var(--ink-2)" }}>지도를 탭해 도착지 변경</span>
          </div>
        </div>
      </div>

      {/* ============ SIDEBAR / PANEL ============ */}
      <div className="w-full md:w-[42%] md:order-1 md:h-screen md:overflow-y-auto px-4 pb-28 md:pb-6">
        <div className="hidden md:block pt-6 pb-2">
          <h1 className="display text-2xl font-semibold leading-tight">구례 생활 보행 지도</h1>
          <p className="text-sm mt-0.5" style={{ color: "var(--ink-2)" }}>Gurye Accessible Pedestrian Route &amp; Map</p>
        </div>

        {/* Route search */}
        <div className="rounded-2xl p-4 mt-3" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          <div className="flex items-center gap-2">
            <div className="flex-1 space-y-2">
              <div className="flex items-center gap-2 rounded-xl px-3 py-2.5" style={{ background: "var(--surface-2)" }}>
                <span style={{ width: 8, height: 8, borderRadius: 999, background: "var(--brand)" }} />
                <select
                  value={originId}
                  onChange={(ev) => setOriginId(ev.target.value)}
                  className="flex-1 bg-transparent text-sm font-medium outline-none"
                  style={{ color: "var(--ink)" }}
                >
                  {NODES.map((n) => (
                    <option key={n.id} value={n.id}>{n.name}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2 rounded-xl px-3 py-2.5" style={{ background: "var(--surface-2)" }}>
                <span style={{ width: 8, height: 8, borderRadius: 999, background: "var(--accent)" }} />
                <select
                  value={destId}
                  onChange={(ev) => setDestId(ev.target.value)}
                  className="flex-1 bg-transparent text-sm font-medium outline-none"
                  style={{ color: "var(--ink)" }}
                >
                  {NODES.map((n) => (
                    <option key={n.id} value={n.id}>{n.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <button
              onClick={swapOriginDest}
              className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
              style={{ background: "var(--surface-2)" }}
              aria-label="출발지와 도착지 바꾸기"
            >
              <ArrowUpDown size={16} color="var(--ink-2)" />
            </button>
          </div>

          {originId === destId && (
            <p className="text-xs mt-2" style={{ color: "var(--accent)" }}>출발지와 도착지를 다르게 선택해 주세요.</p>
          )}
        </div>

        {/* Route result cards */}
        {routes && (
          <div className="mt-4 space-y-3">
            {routeCardMeta.map(({ key, label, Icon, tag }) => {
              const r = routes[key];
              const active = activeKey === key;
              return (
                <button
                  key={key}
                  onClick={() => setActiveKey(key)}
                  className="w-full text-left rounded-2xl p-4 transition-shadow"
                  style={{
                    background: "var(--surface)",
                    border: active ? "2px solid var(--brand)" : "1px solid var(--border)",
                    boxShadow: active ? "0 4px 14px rgba(47,111,78,0.14)" : "none",
                  }}
                >
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-sm font-semibold display">
                      <IconBadge Icon={Icon} size={16} color={key === "comfortable" ? "var(--accent)" : "var(--ink)"} />
                      {label}
                      {tag && (
                        <span className="ml-1 text-[10px] font-bold rounded-full px-2 py-0.5" style={{ background: "var(--accent)", color: "#fff" }}>
                          {tag}
                        </span>
                      )}
                    </span>
                    <span className="mono text-xl font-semibold" style={{ color: scoreColor(r.score) }}>
                      {r.score}
                      <span className="text-xs" style={{ color: "var(--ink-2)" }}>점</span>
                    </span>
                  </div>

                  {/* Comfort ribbon — segmented mini heatmap of the route itself */}
                  <div className="flex w-full h-2 rounded-full overflow-hidden mt-3" style={{ background: "var(--surface-2)" }}>
                    {r.edges.map((e) => (
                      <span
                        key={e.id}
                        style={{ flexGrow: e.distance, flexBasis: 0, background: scoreColor(calcScore(e)) }}
                        title={`${e.distance}m · ${scoreLabel(calcScore(e))}`}
                      />
                    ))}
                  </div>

                  <div className="grid grid-cols-4 gap-2 mt-3">
                    <div>
                      <div className="text-[10px]" style={{ color: "var(--ink-2)" }}>거리</div>
                      <div className="mono text-sm font-semibold">{r.distance}m</div>
                    </div>
                    <div>
                      <div className="text-[10px]" style={{ color: "var(--ink-2)" }}>계단</div>
                      <div className="mono text-sm font-semibold">{r.stairs}개</div>
                    </div>
                    <div>
                      <div className="text-[10px]" style={{ color: "var(--ink-2)" }}>최고 경사</div>
                      <div className="text-sm font-semibold">{r.worstIncline}</div>
                    </div>
                    <div>
                      <div className="text-[10px]" style={{ color: "var(--ink-2)" }}>소요시간</div>
                      <div className="mono text-sm font-semibold">{r.time}분</div>
                    </div>
                  </div>

                  {r.stairs > 0 && (
                    <div className="flex items-center gap-1.5 mt-3 text-xs font-medium" style={{ color: "#B23A2E" }}>
                      <IconBadge Icon={AlertTriangle} size={13} color="#B23A2E" />
                      계단 {r.stairs}개 포함 · 휠체어/유모차는 우회가 필요할 수 있어요
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        )}

        {/* Crowdsource hint card */}
        <div className="mt-5 rounded-2xl p-4 flex items-center gap-3" style={{ background: "var(--surface-2)", border: "1px dashed var(--border)" }}>
          <Accessibility size={22} color="var(--brand)" />
          <div className="flex-1">
            <p className="text-sm font-semibold">현장 정보를 알고 계신가요?</p>
            <p className="text-xs" style={{ color: "var(--ink-2)" }}>계단, 경사, 보도 상태를 제보하면 다른 이웃에게 바로 반영돼요.</p>
          </div>
        </div>
      </div>

      {/* ============ FAB ============ */}
      <button
        onClick={openModalFresh}
        className="fixed z-20 bottom-5 right-5 w-14 h-14 rounded-full flex items-center justify-center shadow-lg"
        style={{ background: "var(--accent)" }}
        aria-label="보행 환경 제보하기"
      >
        <Plus size={26} color="#fff" strokeWidth={2.4} />
      </button>

      {savedFlash && (
        <div className="fixed z-30 bottom-24 left-1/2 -translate-x-1/2 rounded-full px-4 py-2 text-xs font-semibold shadow-lg flex items-center gap-1.5" style={{ background: "var(--ink)", color: "#fff" }}>
          <Check size={14} /> 저장되었습니다 · 지도에 반영됨
        </div>
      )}

      {/* ============ CROWDSOURCE MODAL ============ */}
      {modalOpen && (
        <div className="fixed inset-0 z-40 flex items-end md:items-center justify-center" style={{ background: "rgba(20,43,34,0.45)" }}>
          <div className="w-full md:w-[420px] md:rounded-2xl rounded-t-2xl max-h-[88vh] overflow-y-auto" style={{ background: "var(--surface)" }}>
            <div className="sticky top-0 flex items-center justify-between px-5 py-4" style={{ background: "var(--surface)", borderBottom: "1px solid var(--border)" }}>
              <h2 className="display text-base font-semibold">보행 환경 제보하기</h2>
              <button onClick={() => setModalOpen(false)} aria-label="닫기">
                <X size={20} color="var(--ink-2)" />
              </button>
            </div>

            <div className="p-5 space-y-5">
              <div>
                <label className="text-xs font-semibold" style={{ color: "var(--ink-2)" }}>제보할 구간</label>
                <div className="flex items-center gap-2 mt-1.5">
                  <select
                    value={modalEdgeId ?? ""}
                    onChange={(ev) => openModalForEdge(ev.target.value)}
                    className="flex-1 rounded-xl px-3 py-2.5 text-sm outline-none"
                    style={{ background: "var(--surface-2)" }}
                  >
                    {edges.map((e) => (
                      <option key={e.id} value={e.id}>
                        {nodeById[e.startNodeId].name} ↔ {nodeById[e.endNodeId].name}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => setPickingEdge((v) => !v)}
                    className="w-10 h-10 shrink-0 rounded-xl flex items-center justify-center"
                    style={{ background: pickingEdge ? "var(--brand)" : "var(--surface-2)" }}
                    aria-label="지도에서 구간 선택"
                  >
                    <MousePointerClick size={16} color={pickingEdge ? "#fff" : "var(--ink-2)"} />
                  </button>
                </div>
                {pickingEdge && (
                  <p className="text-[11px] mt-1.5" style={{ color: "var(--brand)" }}>지도(위쪽)에서 구간(선)을 탭해 선택하세요.</p>
                )}
              </div>

              <div>
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold" style={{ color: "var(--ink-2)" }}>계단 개수</label>
                  <span className="mono text-sm font-semibold">{form.stairs}개</span>
                </div>
                <input
                  type="range" min="0" max="30" step="1" value={form.stairs}
                  onChange={(ev) => setForm((f) => ({ ...f, stairs: Number(ev.target.value) }))}
                  className="w-full mt-2"
                  style={{ accentColor: "var(--brand)" }}
                />
              </div>

              <div>
                <label className="text-xs font-semibold" style={{ color: "var(--ink-2)" }}>경사도</label>
                <div className="flex gap-2 mt-1.5">
                  {["낮음", "보통", "심함"].map((v) => (
                    <SegButton key={v} active={form.incline === v} onClick={() => setForm((f) => ({ ...f, incline: v }))}>{v}</SegButton>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold" style={{ color: "var(--ink-2)" }}>보도 상태</label>
                <div className="flex gap-2 mt-1.5">
                  {["양호", "좁음", "없음"].map((v) => (
                    <SegButton key={v} active={form.sidewalk === v} onClick={() => setForm((f) => ({ ...f, sidewalk: v }))}>{v}</SegButton>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <ToggleSwitch label="경사로 있음" Icon={Accessibility} checked={form.ramp} onChange={(v) => setForm((f) => ({ ...f, ramp: v }))} />
                <ToggleSwitch label="가로등 있음" Icon={Lightbulb} checked={form.streetlight} onChange={(v) => setForm((f) => ({ ...f, streetlight: v }))} />
                <ToggleSwitch label="그늘/휴식공간 있음" Icon={Armchair} checked={form.restArea} onChange={(v) => setForm((f) => ({ ...f, restArea: v }))} />
              </div>

              <div className="rounded-xl px-3 py-2.5 flex items-center justify-between" style={{ background: "var(--surface-2)" }}>
                <span className="text-xs font-semibold" style={{ color: "var(--ink-2)" }}>예상 편의성 점수</span>
                <span className="mono text-lg font-bold" style={{ color: scoreColor(calcScore(form)) }}>
                  {calcScore(form)}점
                </span>
              </div>

              <button
                onClick={handleSave}
                className="w-full rounded-xl py-3 text-sm font-semibold text-white flex items-center justify-center gap-1.5"
                style={{ background: "var(--brand)" }}
              >
                <Check size={16} /> 저장하기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
