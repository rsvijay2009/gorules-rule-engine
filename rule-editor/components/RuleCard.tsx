"use client";

import Link from "next/link";
import { FileBadge2, ArrowRight, Calendar } from "lucide-react";

interface RuleCardProps {
    name: string;
    path: string;
}

export default function RuleCard({ name, path }: RuleCardProps) {
    return (
        <div className="glass glass-hover p-6 rounded-xl transition-all duration-300 group">
            <div className="flex items-start justify-between mb-4">
                <div className="p-3 bg-blue-500/10 rounded-lg text-blue-500">
                    <FileBadge2 size={24} />
                </div>
                <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold bg-slate-800/50 px-2 py-1 rounded">
                    JSON Rule
                </div>
            </div>

            <h3 className="text-xl font-bold mb-1 group-hover:text-blue-400 transition-colors uppercase">
                {name.replace(".json", "").replace(/_/g, " ")}
            </h3>
            <p className="text-sm text-slate-400 mb-6 font-mono">
                {path}
            </p>

            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-slate-500">
                    <Calendar size={14} />
                    <span>v1.0.0</span>
                </div>

                <Link
                    href={`/edit/${encodeURIComponent(path)}`}
                    className="flex items-center gap-2 text-sm font-semibold text-blue-500 group-hover:translate-x-1 transition-transform"
                >
                    Edit Rule
                    <ArrowRight size={16} />
                </Link>
            </div>
        </div>
    );
}
