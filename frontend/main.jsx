
import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend
} from "recharts";




function toRechartsTS(ts) {
  if(!ts || !ts.series) return [];
  return ts.series.map(d => ({ date: d.date, value: d.value }));
}
function toBarDataFromKeywords(summary) {
  if(!summary || !summary.keywords) return [];
  return summary.keywords.slice(0,10).map(k => ({ name: k.term, count: k.count }));
}
function toPieDataFromPlatform(summary) {
  if(!summary || !summary.platform_share) return [];
  return summary.platform_share.map(p => ({ name: p.platform, value: p.count }));
}

function App(){
  const [health, setHealth] = useState(null);
  const [summary, setSummary] = useState(null);
  const [brandFilter, setBrandFilter] = useState("");
  const [platformFilter, setPlatformFilter] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [q, setQ] = useState("브랜드");
  const [results, setResults] = useState([]);
  const [ts, setTs] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [evidenceTitle, setEvidenceTitle] = useState("");

  useEffect(()=>{
    fetch("http://localhost:8000/health").then(r=>r.json()).then(setHealth);
    loadSummary();
  },[]);

  const loadSummary = async () => {
    const params = new URLSearchParams();
    if(brandFilter) params.set("brand", brandFilter);
    if(platformFilter) params.set("platform", platformFilter);
    if(startDate) params.set("start_date", startDate);
    if(endDate) params.set("end_date", endDate);
    const r = await fetch(`http://localhost:8000/analytics/summary?${params.toString()}`);
    setSummary(await r.json());
  };

  const onKeywordClick = async (term) => {
    const r = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(term)}`);
    setEvidence(await r.json());
    setEvidenceTitle(term);
  };

  const doSearch = async () => {
    const r = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(q)}`);
    setResults(await r.json());
  };

  const loadTs = async () => {
    const params = new URLSearchParams({ metric: "mentions", period: "day" });
    if(brandFilter) params.set("brand", brandFilter);
    if(platformFilter) params.set("platform", platformFilter);
    if(startDate) params.set("start_date", startDate);
    if(endDate) params.set("end_date", endDate);
    const r = await fetch(`http://localhost:8000/analytics/timeseries?${params.toString()}`);
    setTs(await r.json());
  };

  return (
    <div style={{fontFamily:"system-ui", padding:20, maxWidth:1000, margin:"0 auto"}}>
      <h1>브랜드/제품 트렌드 대시보드</h1>

<section style={{marginBottom:24}}>
  <h2>필터</h2>
  <div style={{display:"grid", gridTemplateColumns:"repeat(4, 1fr)", gap:8, maxWidth:800}}>
    <input value={brandFilter} onChange={e=>setBrandFilter(e.target.value)} placeholder="브랜드 (예: A)" />
    <input value={platformFilter} onChange={e=>setPlatformFilter(e.target.value)} placeholder="플랫폼 (예: news, blog)" />
    <input type="date" value={startDate} onChange={e=>setStartDate(e.target.value)} placeholder="시작일" />
    <input type="date" value={endDate} onChange={e=>setEndDate(e.target.value)} placeholder="종료일" />
  </div>
  <div style={{marginTop:8}}>
    <button onClick={()=>{ loadSummary(); loadTs(); }}>적용</button>
    <button style={{marginLeft:8}} onClick={()=>{ setBrandFilter(''); setPlatformFilter(''); setStartDate(''); setEndDate(''); }}>초기화</button>
  </div>
</section>

      <section style={{marginBottom:24}}>
        <h2>상태</h2>
        <pre>{JSON.stringify(health, null, 2)}</pre>
      </section>
      <section style={{marginBottom:24}}>
        <h2>요약</h2>
        <pre>{JSON.stringify(summary, null, 2)}</pre>
      </section>
      <section>
        <h2>검색</h2>
        <input value={q} onChange={e=>setQ(e.target.value)} placeholder="키워드" />
        <button onClick={doSearch}>검색</button>
        <pre>{JSON.stringify(results, null, 2)}</pre>
      </section>
      <section style={{marginTop:24}}>
        <h2>시계열(언급량)</h2>
        <button onClick={loadTs}>불러오기</button>
        <pre>{JSON.stringify(ts, null, 2)}</pre>
      </section>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App/>);
