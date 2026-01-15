"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import {
    ArrowLeft,
    Save,
    Play,
    ChevronRight,
    LayoutGrid,
    Network,
    Code,
    CheckCircle2,
    AlertCircle,
    Loader2,
    Info,
    X
} from "lucide-react";
import DecisionTableEditor, { DecisionTableContent } from "@/components/DecisionTableEditor";
import TestPanel from "@/components/TestPanel";

interface Node {
    id: string;
    name: string;
    type: string;
    content: unknown; // content structure depends on node type
}

interface RuleData {
    nodes: Node[];
    edges: unknown[];
}

export default function EditRulePage({ params }: { params: Promise<{ path: string }> }) {
    const { path: encodedPath } = use(params);
    const path = decodeURIComponent(encodedPath);

    const [data, setData] = useState<RuleData | null>(null);
    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [showTest, setShowTest] = useState(false);
    const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

    useEffect(() => {
        const fetchRule = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/v1/rules/${encodedPath}`);
                if (!response.ok) throw new Error("Failed to fetch rule");
                const json = await response.json();
                setData(json);

                // Select first decision table by default
                const firstTable = json.nodes.find((n: Node) => n.type === "decisionTableNode");
                if (firstTable) setSelectedNodeId(firstTable.id);
                else if (json.nodes.length > 0) setSelectedNodeId(json.nodes[0].id);

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

    const updateNodeContent = (nodeId: string, newContent: Record<string, unknown>) => {
        if (!data) return;
        const newNodes = data.nodes.map(n =>
            n.id === nodeId ? { ...n, content: newContent } : n
        );
        setData({ ...data, nodes: newNodes });
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
            <Loader2 className="animate-spin text-blue-500" size={40} />
            <p className="text-slate-400 font-medium">Loading rule definition...</p>
        </div>
    );

    const selectedNode = data?.nodes.find(n => n.id === selectedNodeId);

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <Link
                        href="/"
                        className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
                    >
                        <ArrowLeft size={20} />
                    </Link>
                    <div>
                        <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                            <span>Rules</span>
                            <ChevronRight size={12} />
                            <span>{path.split("/")[0]}</span>
                        </div>
                        <h1 className="text-2xl font-bold uppercase tracking-tight">
                            {path.split("/").pop()?.replace(".json", "").replace(/_/g, " ")}
                        </h1>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {msg && (
                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium animate-in zoom-in duration-300 ${msg.type === "success" ? "bg-green-500/10 text-green-400 border border-green-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"
                            }`}>
                            {msg.type === "success" ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                            {msg.text}
                        </div>
                    )}
                    <button
                        disabled={saving}
                        onClick={handleSave}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white px-4 py-2 rounded-lg font-semibold transition-all shadow-lg shadow-blue-500/20"
                    >
                        {saving ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                        {saving ? "Saving..." : "Save Changes"}
                    </button>
                    <button
                        onClick={() => setShowTest(true)}
                        className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2 rounded-lg font-semibold border border-slate-700 transition-all"
                    >
                        <Play size={18} />
                        Test
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Sidebar Navigation */}
                <div className="lg:col-span-1 space-y-4">
                    <div className="glass p-4 rounded-2xl">
                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Network size={14} /> Decision Nodes
                        </h3>
                        <div className="space-y-1">
                            {data?.nodes.map(node => (
                                <button
                                    key={node.id}
                                    onClick={() => setSelectedNodeId(node.id)}
                                    className={`w-full text-left px-3 py-2.5 rounded-xl text-sm transition-all flex items-center gap-3 ${selectedNodeId === node.id
                                        ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20"
                                        : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                                        }`}
                                >
                                    <div className={`p-1.5 rounded-md ${selectedNodeId === node.id ? "bg-white/20" : "bg-slate-800"
                                        }`}>
                                        {node.type === "decisionTableNode" ? <LayoutGrid size={14} /> : <Code size={14} />}
                                    </div>
                                    <span className="truncate font-medium">{node.name}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="glass p-5 rounded-2xl text-center space-y-3">
                        <div className="w-12 h-12 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto text-blue-500">
                            <Info size={24} />
                        </div>
                        <h4 className="text-sm font-bold">Need Help?</h4>
                        <p className="text-xs text-slate-500 leading-relaxed">
                            Select a node to edit its contents. Decision tables allow you to define business logic in a spreadsheet-like view.
                        </p>
                    </div>
                </div>

                {/* Content Area */}
                <div className="lg:col-span-3 space-y-6">
                    {selectedNode ? (
                        <div className="animate-in fade-in slide-in-from-right-4 duration-500">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2.5 bg-blue-500/10 rounded-xl text-blue-500">
                                    {selectedNode.type === "decisionTableNode" ? <LayoutGrid size={24} /> : <Code size={24} />}
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold">{selectedNode.name}</h2>
                                    <p className="text-xs text-slate-500 uppercase tracking-wider font-mono">{selectedNode.type}</p>
                                </div>
                            </div>

                            {selectedNode.type === "decisionTableNode" ? (
                                <DecisionTableEditor
                                    content={selectedNode.content as DecisionTableContent}
                                    onChange={(newContent: DecisionTableContent) => updateNodeContent(selectedNode.id, newContent as unknown as Record<string, unknown>)}
                                />
                            ) : (
                                <div className="glass p-6 rounded-2xl border-dashed">
                                    <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
                                        <div className="p-4 bg-slate-800 rounded-2xl text-slate-500">
                                            <Code size={32} />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-slate-300">Advanced Node Configuration</h3>
                                            <p className="text-sm text-slate-500 max-w-sm mx-auto mt-2">
                                                This node type ({selectedNode.type}) is managed via internal schema. Visual editing for this type will be available in the next version.
                                            </p>
                                        </div>
                                        <pre className="mt-6 p-4 bg-slate-950 rounded-xl text-xs text-slate-400 text-left w-full overflow-auto max-h-40 border border-slate-800 font-mono">
                                            {JSON.stringify(selectedNode.content, null, 2)}
                                        </pre>
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-32 glass rounded-3xl border-dashed">
                            <p className="text-slate-500">Select a node from the sidebar to begin editing.</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Test Drawer */}
            {showTest && (
                <div className="fixed inset-y-0 right-0 w-full md:w-[500px] bg-slate-900 border-l border-slate-800 shadow-2xl z-[100] animate-in slide-in-from-right duration-300 flex flex-col">
                    <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50 backdrop-blur-md">
                        <div className="flex items-center gap-2">
                            <div className="p-2 bg-green-500/10 rounded-lg text-green-500">
                                <Play size={18} />
                            </div>
                            <span className="font-bold">Live Simulation</span>
                        </div>
                        <button
                            onClick={() => setShowTest(false)}
                            className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 transition-colors"
                        >
                            <X size={20} />
                        </button>
                    </div>
                    <div className="flex-1 p-6 overflow-hidden">
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
                                return response.json();
                            }}
                        />
                    </div>
                </div>
            )}

            {/* Overlay for Test Drawer */}
            {showTest && (
                <div
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[90] animate-in fade-in duration-300"
                    onClick={() => setShowTest(false)}
                />
            )}
        </div>
    );
}
