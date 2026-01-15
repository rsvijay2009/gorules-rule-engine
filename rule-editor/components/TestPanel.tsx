"use client";

import { useState } from "react";
import { Play, Info, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

interface TestPanelProps {
    onTest: (facts: Record<string, unknown>) => Promise<Record<string, unknown>>;
}

interface SimulationResult {
    kyc_eligibility_status?: string;
    kyc_rejection_reason?: string;
    [key: string]: unknown;
}

export default function TestPanel({ onTest }: TestPanelProps) {
    const [facts, setFacts] = useState<string>(JSON.stringify({
        pan_verification_status: "VERIFIED",
        customer_age: 32,
        cibil_score: 750,
        dedupe_match_found: false
    }, null, 2));

    const [result, setResult] = useState<SimulationResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleRun = async () => {
        setLoading(true);
        setError(null);
        try {
            const parsedFacts = JSON.parse(facts);
            const data = await onTest(parsedFacts);
            setResult(data as SimulationResult);
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : "Failed to run test. Check your JSON format.";
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full gap-4 text-sans">
            <div className="flex items-center justify-between shrink-0">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Input Facts</span>
                <button
                    onClick={handleRun}
                    disabled={loading}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-wider transition-all shadow-lg shadow-blue-500/10 active:scale-95 border border-blue-400/20"
                >
                    {loading ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                    {loading ? "Simulating..." : "Run Simulation"}
                </button>
            </div>

            <div className="flex-[3] flex flex-col min-h-0">
                <textarea
                    value={facts}
                    onChange={(e) => setFacts(e.target.value)}
                    className="flex-1 w-full bg-slate-950/50 border border-slate-800 rounded-xl p-3 font-mono text-[11px] focus:ring-1 focus:ring-blue-500 outline-none transition-all resize-none text-slate-300"
                    placeholder="Enter context JSON..."
                />
            </div>

            <div className="flex-[2] flex flex-col min-h-0 gap-2">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Output Result</span>
                <div className="flex-1 w-full bg-slate-900/80 border border-slate-800 rounded-xl p-3 font-mono text-[11px] overflow-auto relative">
                    {loading ? (
                        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
                            <Loader2 size={24} className="animate-spin text-blue-500" />
                        </div>
                    ) : error ? (
                        <div className="flex items-start gap-2 text-red-400">
                            <AlertCircle size={14} className="shrink-0" />
                            <span>{error}</span>
                        </div>
                    ) : result ? (
                        <div className="space-y-3">
                            <div className={`flex items-center gap-2 p-2 rounded-lg border ${result.kyc_eligibility_status === "APPROVED"
                                ? "bg-green-500/5 border-green-500/20 text-green-400"
                                : "bg-red-500/5 border-red-500/20 text-red-400"
                                }`}>
                                {result.kyc_eligibility_status === "APPROVED" ? (
                                    <CheckCircle2 size={14} />
                                ) : (
                                    <AlertCircle size={14} />
                                )}
                                <span className="font-bold text-[12px]">{result.kyc_eligibility_status}</span>
                                {result.kyc_rejection_reason && (
                                    <span className="text-[10px] opacity-70 ml-auto">{result.kyc_rejection_reason}</span>
                                )}
                            </div>
                            <pre className="text-slate-500 leading-relaxed">{JSON.stringify(result, null, 2)}</pre>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-slate-600 gap-2">
                            <Info size={20} />
                            <p className="text-[10px] font-medium uppercase tracking-tighter">Ready for simulation</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
