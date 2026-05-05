"use client";
import { useEffect, useState, useCallback } from "react";
import { generateOpportunities, generateBotStatus, generatePnlHistory } from "@/lib/mockData";
export default function Dashboard() {
    const [opps, setOpps] = useState([]);
    const [status, setStatus] = useState(null);
    useEffect(() => {
          setOpps(generateOpportunities());
          setStatus(generateBotStatus());
    }, []);
    if (!status) return <div>Loading...</div>div>;
    return (
          <div>
                <h1>Sentinel-Poly Dashboard</h1>h1>
                <div>Status: {status.status}</div>div>
                <div>Capital: ${status.capital}</div>div>
                <table>
                        <thead><tr><th>Market</th>th><th>Signal</th>th></tr>tr></thead>thead>
                        <tbody>{opps.map(o => <tr key={o.id}><td>{o.question}</td>td><td>{o.signal}</td>td></tr>tr>)}</tbody>tbody>
                </table>table>
          </div>div>
        );
}</div>
