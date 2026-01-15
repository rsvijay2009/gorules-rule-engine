"use client";

import { Plus, Trash2, Settings2, Info } from "lucide-react";

interface Input {
    id: string;
    name: string;
    field: string;
}

interface Output {
    id: string;
    name: string;
    field: string;
}

export interface DecisionTableContent {
    hitPolicy: string;
    inputs: Input[];
    outputs: Output[];
    rules: Record<string, string>[];
}

interface DecisionTableEditorProps {
    content: DecisionTableContent;
    onChange: (newContent: DecisionTableContent) => void;
}

export default function DecisionTableEditor({ content, onChange }: DecisionTableEditorProps) {
    const { inputs, outputs, rules } = content;

    const updateRule = (rowIndex: number, colId: string, value: string) => {
        const newRules = [...rules];
        newRules[rowIndex] = { ...newRules[rowIndex], [colId]: value };
        onChange({ ...content, rules: newRules });
    };

    const addRow = () => {
        const newRule: Record<string, string> = {};
        inputs.forEach(i => newRule[i.id] = "");
        outputs.forEach(o => newRule[o.id] = "");
        onChange({ ...content, rules: [...rules, newRule] });
    };

    const removeRow = (index: number) => {
        const newRules = rules.filter((_, i) => i !== index);
        onChange({ ...content, rules: newRules });
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <Settings2 size={18} className="text-slate-400" />
                    <span className="text-sm font-semibold text-slate-300">Hit Policy: <span className="text-blue-400 uppercase">{content.hitPolicy}</span></span>
                </div>
                <button
                    onClick={addRow}
                    className="flex items-center gap-2 text-xs bg-blue-600 hover:bg-blue-500 px-3 py-1.5 rounded font-medium transition-colors"
                >
                    <Plus size={14} /> Add Row
                </button>
            </div>

            <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/50 shadow-2xl">
                <table className="w-full text-left border-collapse min-w-[800px]">
                    <thead>
                        {/* Type Headers */}
                        <tr>
                            <th className="p-1 border border-slate-800 bg-slate-800/30 w-10"></th>
                            <th colSpan={inputs.length} className="px-4 py-2 text-[10px] font-bold uppercase tracking-wider text-blue-400 border border-slate-800 text-center bg-blue-500/5">
                                Inputs
                            </th>
                            <th colSpan={outputs.length} className="px-4 py-2 text-[10px] font-bold uppercase tracking-wider text-green-400 border border-slate-800 text-center bg-green-500/5">
                                Outputs
                            </th>
                            <th className="p-1 border border-slate-800 bg-slate-800/30 w-12 text-center"></th>
                        </tr>
                        {/* Column Name Headers */}
                        <tr>
                            <th className="p-3 border border-slate-800 bg-slate-800/50 text-xs text-slate-500 text-center">#</th>
                            {inputs.map(input => (
                                <th key={input.id} className="p-3 border border-slate-800 bg-slate-800/50">
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold text-slate-200">{input.name}</span>
                                        <span className="text-[10px] font-mono text-slate-500">{input.field}</span>
                                    </div>
                                </th>
                            ))}
                            {outputs.map(output => (
                                <th key={output.id} className="p-3 border border-slate-800 bg-slate-800/50">
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold text-slate-200">{output.name}</span>
                                        <span className="text-[10px] font-mono text-slate-500">{output.field}</span>
                                    </div>
                                </th>
                            ))}
                            <th className="p-3 border border-slate-800 bg-slate-800/50"></th>
                        </tr>
                    </thead>
                    <tbody>
                        {rules.map((rule, rowIndex) => (
                            <tr key={rowIndex} className="group hover:bg-slate-800/30 transition-colors">
                                <td className="p-3 border border-slate-800 text-xs text-slate-500 text-center font-mono">
                                    {rowIndex + 1}
                                </td>

                                {/* Inputs Cells */}
                                {inputs.map(input => (
                                    <td key={input.id} className="p-1 border border-slate-800">
                                        <input
                                            type="text"
                                            value={rule[input.id] || ""}
                                            onChange={(e) => updateRule(rowIndex, input.id, e.target.value)}
                                            className="w-full bg-transparent p-2 text-sm text-slate-300 focus:bg-slate-800 outline-none rounded transition-all font-mono"
                                            placeholder="-"
                                        />
                                    </td>
                                ))}

                                {/* Outputs Cells */}
                                {outputs.map(output => (
                                    <td key={output.id} className="p-1 border border-slate-800">
                                        <input
                                            type="text"
                                            value={rule[output.id] || ""}
                                            onChange={(e) => updateRule(rowIndex, output.id, e.target.value)}
                                            className="w-full bg-transparent p-2 text-sm text-green-400 focus:bg-slate-800 outline-none rounded transition-all font-mono"
                                            placeholder="-"
                                        />
                                    </td>
                                ))}

                                <td className="p-3 border border-slate-800 text-center">
                                    <button
                                        onClick={() => removeRow(rowIndex)}
                                        className="text-slate-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                                        title="Delete row"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="flex items-start gap-2 bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                <Info size={16} className="text-blue-500 shrink-0 mt-0.5" />
                <p className="text-xs text-slate-400 leading-relaxed">
                    Use quotes for strings (e.g., <code className="text-blue-400">&quot;VERIFIED&quot;</code>). Expressions like <code className="text-blue-400">&gt; 21</code> or <code className="text-blue-400">[21..60]</code> are supported.
                    Use <code className="text-blue-400">null</code> for empty values.
                </p>
            </div>
        </div>
    );
}
