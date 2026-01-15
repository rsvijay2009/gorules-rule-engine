"use client";

import { useState } from "react";
import { Play, ClipboardList, Info, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

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
        <div className="flex flex-col h-full space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                    <ClipboardList size={16} /> Test Context
                </h3>
                <button
                    onClick={handleRun}
                    disabled={loading}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-500 disabled:bg-slate-800 text-white px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
                >
                    {loading ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
                    Run Test
                </button>
            </div>

            <div className="flex-1 space-y-4 min-h-0 flex flex-col">
                <div className="flex-1 flex flex-col space-y-2">
                    <label className="text-[10px] font-bold text-slate-500 uppercase">Input Facts (JSON)</label>
                    <textarea
                        value={facts}
                        onChange={(e) => setFacts(e.target.value)}
                        className="flex-1 w-full bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs focus:ring-1 focus:ring-blue-500 outline-none transition-all resize-none"
                    />
                </div>

                <div className="flex-1 flex flex-col space-y-2 min-h-0">
                    <label className="text-[10px] font-bold text-slate-500 uppercase">Decision Result</label>
                    <div className="flex-1 w-full bg-slate-900 border border-slate-800 rounded-xl p-4 font-mono text-xs overflow-auto relative">
                        {loading ? (
                            <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
                                <Loader2 size={24} className="animate-spin text-blue-500" />
                            </div>
                        ) : error ? (
                            <div className="flex items-start gap-2 text-red-400">
                                <AlertCircle size={14} className="shrink-0 mt-0.5" />
                                <span>{error}</span>
                            </div>
                        ) : result ? (
                            <div className="space-y-4">
                                <div className="flex items-center gap-2 p-2 rounded bg-slate-800/50 border border-slate-700">
                                    {result.kyc_eligibility_status === "APPROVED" ? (
                                        <CheckCircle2 size={16} className="text-green-500" />
                                    ) : (
                                        <AlertCircle size={16} className="text-red-500" />
                                    )}
                                    <span className="font-bold text-slate-200">{result.kyc_eligibility_status}</span>
                                    {result.kyc_rejection_reason && (
                                        <span className="text-slate-500 ml-auto text-[10px]">{result.kyc_rejection_reason}</span>
                                    )}
                                </div>
                                <pre className="text-slate-400">{JSON.stringify(result, null, 2)}</pre>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-slate-600 gap-2">
                                <Info size={24} />
                                <p>Run a test to see results</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
