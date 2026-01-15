"use client";

import { useEffect, useState } from "react";
import { Plus, Search, RefreshCcw } from "lucide-react";
import RuleCard from "@/components/RuleCard";

interface RuleFile {
  name: string;
  path: string;
  is_directory: boolean;
}

export default function Home() {
  const [rules, setRules] = useState<RuleFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const fetchRules = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/rules/");
      if (!response.ok) throw new Error("Failed to fetch rules");
      const data = await response.ok ? await response.json() : [];
      setRules(data);
    } catch (err) {
      setError("Is the backend running? Ensure the FastAPI server is started.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const filteredRules = rules.filter(r =>
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    r.path.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white">
                G
              </div>
              <span className="text-xl font-bold tracking-tight">BRE <span className="text-blue-500">Editor</span></span>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded border border-slate-700">
                v1.0.0
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 space-y-8 animate-in fade-in duration-500">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight">Business <span className="text-blue-500">Rules</span></h1>
            <p className="text-slate-400 mt-2">Manage and test your decision tables in real-time.</p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchRules}
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors"
              title="Refresh rules"
            >
              <RefreshCcw size={20} className={loading ? "animate-spin" : ""} />
            </button>
            <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold transition-all shadow-lg shadow-blue-500/20 active:scale-95">
              <Plus size={20} />
              New Rule
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
            <Search size={18} />
          </div>
          <input
            type="text"
            placeholder="Search rules..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="block w-full pl-10 pr-3 py-3 bg-slate-900 border border-slate-800 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
          />
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-48 rounded-xl bg-slate-900 border border-slate-800 animate-pulse" />
            ))}
          </div>
        ) : error ? (
          <div className="p-8 rounded-2xl border border-red-500/20 bg-red-500/5 text-center">
            <p className="text-red-400 font-medium">{error}</p>
            <button
              onClick={fetchRules}
              className="mt-4 text-sm text-red-400 underline"
            >
              Try again
            </button>
          </div>
        ) : filteredRules.length === 0 ? (
          <div className="text-center py-20 border-2 border-dashed border-slate-800 rounded-3xl">
            <p className="text-slate-500">No rules found. Start by creating a new one!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRules.map((rule) => (
              <RuleCard key={rule.path} name={rule.name} path={rule.path} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
