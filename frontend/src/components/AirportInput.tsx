import React, { useState, useMemo, useEffect } from 'react';
import type { Airport } from '../types/airport';

interface Props {
  label: string;
  allAirports: Airport[];
  selectedCodes: string[];
  onAdd: (code: string) => void;
  onRemove: (code: string) => void;
  placeholder: string;
}

export const AirportInput: React.FC<Props> = ({ label, allAirports, selectedCodes, onAdd, onRemove, placeholder }) => {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);

  const suggestions = useMemo(() => {
    if (!query.trim()) return [];

    return allAirports.filter(a =>
      a.text.includes(query.toLowerCase()) &&
      !selectedCodes.includes(a.iata)
    ).slice(0, 8);
  }, [query, allAirports, selectedCodes]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [suggestions]);

  const handleSelect = (iata: string) => {
    if (selectedCodes.includes(iata)) {
      setQuery("");
      setIsOpen(false);
      return;
    }
    onAdd(iata);
    setQuery("");
    setIsOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || suggestions.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex(prev => (prev + 1) % suggestions.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex(prev => (prev - 1 + suggestions.length) % suggestions.length);
    } else if (e.key === "Enter") {
      e.preventDefault();
      handleSelect(suggestions[selectedIndex].iata);
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  return (
    <div className="flex-1 min-w-[220px] bg-white/55 border border-(--b) rounded-[14px] p-2.5 relative">
      <div className="flex justify-between gap-2.5 mb-1.5 text-(--m) font-bold text-xs">
        <span>{label}</span>
        <span>Enter to add</span>
      </div>

      <div className="flex flex-wrap gap-1.5 min-h-[24px] mb-2">
        {selectedCodes.map(code => (
          <span key={code} className="inline-flex gap-2 items-center px-2 py-1 rounded-full bg-[#73c6ff]/22 border border-[#4aa8df]/25 font-bold text-[13px]">
            {code}
            <button
              onClick={() => onRemove(code)}
              className="border-0 bg-transparent text-slate-900/60 cursor-pointer font-black hover:text-[#d84a4a]"
            >
              ×
            </button>
          </span>
        ))}
      </div>

      <input
        className="w-full rounded-xl border border-[#5aa0d2]/25 bg-white/85 px-2.5 py-2 outline-none focus:border-[#4aa8df]/55 focus:ring-4 focus:ring-[#4aa8df]/15 transition-all text-sm"
        value={query}
        onChange={(e) => { setQuery(e.target.value); setIsOpen(true); }}
        onFocus={() => setIsOpen(true)}
        onBlur={() => setTimeout(() => setIsOpen(false), 150)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoComplete="off"
      />

      {isOpen && suggestions.length > 0 && (
        <div className="absolute top-full left-0 w-full max-h-[300px] overflow-y-auto bg-white border border-black/10 rounded-lg shadow-xl mt-1.5 z-[9999]">
          {suggestions.map((a, index) => (
            <div
              key={a.iata}
              className={`px-3.5 py-2.5 cursor-pointer text-sm transition-colors ${
                index === selectedIndex ? 'bg-[#f0f7ff] text-[#0770e3]' : 'text-[#333]'
              }`}
              onMouseDown={() => handleSelect(a.iata)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              {a.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};