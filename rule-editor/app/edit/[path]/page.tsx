"use client";

import { useEffect, useState, Suspense, useMemo } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import {
    Save,
    Play,
    ChevronRight,
    CheckCircle2,
    AlertCircle,
    Loader2,
    LayoutDashboard
} from "lucide-react";
import TestPanel from "@/components/TestPanel";

// Import JDM Editor styles
import "@gorules/jdm-editor/dist/style.css";

import { DecisionGraphType, JdmConfigProvider, Simulation } from "@gorules/jdm-editor";

// Dynamically import DecisionGraph as it's a client-side library
const DecisionGraph = dynamic(
    () => import("@gorules/jdm-editor").then((mod) => mod.DecisionGraph),
    {
        ssr: false, loading: () => (
            <div className="flex flex-col items-center justify-center h-full glass gap-4">
                <Loader2 className="animate-spin text-blue-500" size={32} />
                <p className="text-slate-400 font-medium font-sans">Initializing Studio...</p>
            </div>
        )
    }
);

export default function EditRulePage({ params }: { params: { path: string } }) {
    const { path: encodedPath } = params;
    const path = decodeURIComponent(encodedPath);

    const [data, setData] = useState<DecisionGraphType | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
    const [simulation, setSimulation] = useState<Simulation | undefined>();

    useEffect(() => {
        const fetchRule = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/v1/rules/${encodedPath}`);
                if (!response.ok) throw new Error("Failed to fetch rule");
                const json = await response.json();
                setData({
                    nodes: json.nodes || [],
                    edges: json.edges || []
                });
            } catch (err) {
                console.error("Fetch rule error:", err);
                setMsg({ type: "error", text: "Failed to load rule. Is the backend running?" });
            } finally {
                setLoading(false);
            }
        };
        fetchRule();
    }, [encodedPath]);

    const handleSave = async () => {
        if (!data) return;
        setSaving(true);
        setMsg(null);
        try {
            const response = await fetch(`http://localhost:8000/api/v1/rules/${encodedPath}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: data }),
            });
            if (!response.ok) throw new Error("Failed to save");
            setMsg({ type: "success", text: "Rule saved successfully!" });
            setTimeout(() => setMsg(null), 3000);
        } catch (err) {
            console.error("Save rule error:", err);
            setMsg({ type: "error", text: "Failed to save rule." });
        } finally {
            setSaving(false);
        }
    };

    const simulatorPanel = useMemo(() => ({
        id: 'simulator',
        title: 'Simulator',
        icon: <Play size={14} />,
        renderPanel: () => (
            <div className="h-full bg-slate-900/50 backdrop-blur-md p-4 overflow-hidden">
                <TestPanel
                    onTest={async (facts) => {
                        const response = await fetch("http://localhost:8000/api/v1/rules/test", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ path, facts })
                        });
                        if (!response.ok) {
                            const err = await response.json();
                            throw new Error(err.detail || "Simulation failed");
                        }
                        const result = await response.json();
                        if (result.trace) {
                            setSimulation({
                                result: {
                                    performance: result.performance || '0ms',
                                    result: result.result,
                                    trace: result.trace,
                                    snapshot: data!
                                }
                            });
                        }
                        return result;
                    }}
                />
            </div>
        )
    }), [path, data]);

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-screen bg-slate-950 gap-6">
            <div className="relative">
                <Loader2 className="animate-spin text-blue-500" size={48} />
                <div className="absolute inset-0 blur-xl bg-blue-500/20 animate-pulse" />
            </div>
            <div className="text-center space-y-2">
                <p className="text-slate-200 font-bold text-lg tracking-tight">Loading Rule Model</p>
                <p className="text-slate-500 text-sm font-medium">{path}</p>
            </div>
        </div>
    );

    return (
        <JdmConfigProvider theme={{ mode: 'dark' }}>
            <div className="h-screen bg-slate-950 flex flex-col overflow-hidden">
                {/* Minimal Header */}
                <header className="h-14 border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl flex items-center justify-between px-6 shrink-0 z-10">
                    <div className="flex items-center gap-6">
                        <Link
                            href="/"
                            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors group"
                        >
                            <LayoutDashboard size={18} className="group-hover:scale-110 transition-transform" />
                            <span className="text-sm font-bold tracking-tight">Platform</span>
                        </Link>

                        <div className="h-4 w-px bg-slate-800" />

                        <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">{path.split("/")[0]}</span>
                            <ChevronRight size={12} className="text-slate-600" />
                            <h1 className="text-sm font-bold text-slate-200">
                                {path.split("/").pop()?.replace(".json", "")}
                            </h1>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        {msg && (
                            <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider animate-in fade-in zoom-in duration-300 ${msg.type === "success"
                                ? "bg-green-500/10 text-green-400 border border-green-500/20"
                                : "bg-red-500/10 text-red-400 border border-red-500/20"
                                }`}>
                                {msg.type === "success" ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                                {msg.text}
                            </div>
                        )}

                        <button
                            disabled={saving}
                            onClick={handleSave}
                            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 text-white px-4 py-1.5 rounded-full text-xs font-bold transition-all shadow-lg shadow-blue-500/10 active:scale-95 border border-blue-400/20"
                        >
                            {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                            {saving ? "Saving..." : "Save Rule"}
                        </button>
                    </div>
                </header>

                {/* Full Screen Editor Area */}
                <main className="flex-1 relative overflow-hidden flex flex-col bg-[#0b0e14]">
                    <Suspense fallback={
                        <div className="flex-1 flex items-center justify-center">
                            <Loader2 className="animate-spin text-slate-700" size={32} />
                        </div>
                    }>
                        {data && (
                            <div className="absolute inset-0">
                                <DecisionGraph
                                    value={data}
                                    onChange={(val) => setData(val)}
                                    simulate={simulation}
                                    panels={[simulatorPanel]}
                                    defaultActivePanel="simulator"
                                />
                            </div>
                        )}
                    </Suspense>
                </main>
            </div>
        </JdmConfigProvider>
    );
}
