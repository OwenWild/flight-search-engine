import { useState, useEffect } from 'react';
import type {Airport} from '../types/airport';

export function useAirports() {
  const [allAirports, setAllAirports] = useState<Airport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/airports.json")
      .then(r => r.json())
      .then(d => {
        const list = Array.isArray(d) ? d : (d.airports || d.data || []);
        const formatted = list.map(toA).filter((item: Airport | null): item is Airport => item !== null);
        setAllAirports(formatted);
        setLoading(false);
      });
  }, []);

  const toA = (o: any): Airport | null => {
    const pick = (obj: any, ks: string[]) => {
      for (const k of ks) if (obj && obj[k]) return obj[k];
      return "";
    };
    const iata = (pick(o, ["iata", "code"]) || "").toString().toUpperCase().trim();
    if (iata.length !== 3) return null;
    return {
      iata,
      label: `${pick(o, ["name", "city"]) || iata} (${iata})`,
      text: (iata + " " + pick(o, ["name", "city", "country"])).toLowerCase()
    };
  };

  return { allAirports, loading };
}