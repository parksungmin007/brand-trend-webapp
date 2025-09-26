
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
  const [q, setQ] = useState("브랜드");
  const [results, setResults] = useState([]);
  const [ts, setTs] = useState(null);

  useEffect(()=>{
    fetch("http://localhost:8000/health").then(r=>r.json()).then(setHealth);
    fetch("http://localhost:8000/analytics/summary").then(r=>r.json()).then(setSummary);
  },[]);

  const doSearch = async () => {
    const r = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(q)}`);
    setResults(await r.json());
  };

  const loadTs = async () => {
    const r = await fetch("http://localhost:8000/analytics/timeseries?metric=mentions&period=day");
    setTs(await r.json());
  };

  return (
    <div style={{fontFamily:"system-ui", padding:20, maxWidth:1000, margin:"0 auto"}}>
      <h1>브랜드/제품 트렌드 대시보드(초기)</h1>
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
