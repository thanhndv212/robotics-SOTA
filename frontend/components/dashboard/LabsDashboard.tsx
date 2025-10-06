"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchLabs } from "../../lib/api";
import type { Lab } from "../../types/lab";
import LabFilters from "./LabFilters";
import LabList from "./LabList";
import MetricsSummary from "./MetricsSummary";

interface LabsDashboardState {
  labs: Lab[];
  loading: boolean;
  error: string | null;
  updatedAt: Date | null;
}

const initialState: LabsDashboardState = {
  labs: [],
  loading: true,
  error: null,
  updatedAt: null
};

export default function LabsDashboard() {
  const [{ labs, loading, error, updatedAt }, setState] = useState<LabsDashboardState>(initialState);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedCountry, setSelectedCountry] = useState<string>("");
  const [selectedFocus, setSelectedFocus] = useState<string>("");

  const loadLabs = useCallback(async (signal?: AbortSignal) => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const labsData = await fetchLabs(signal);
      setState({ labs: labsData, loading: false, error: null, updatedAt: new Date() });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setState((current) => ({ ...current, loading: false, error: message }));
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    loadLabs(controller.signal);
    return () => controller.abort();
  }, [loadLabs]);

  const countries = useMemo(() => {
    const list = labs
      .map((lab) => lab.country)
      .filter((country): country is string => Boolean(country));
    return Array.from(new Set(list)).sort((a, b) => a.localeCompare(b));
  }, [labs]);

  const focusAreas = useMemo(() => {
    const list = labs.flatMap((lab) => lab.focus_areas ?? []);
    return Array.from(new Set(list)).sort((a, b) => a.localeCompare(b));
  }, [labs]);

  const filteredLabs = useMemo(() => {
  const term = searchTerm.trim().toLowerCase();
  const focusTerm = selectedFocus.trim().toLowerCase();

    return labs.filter((lab) => {
      const searchTarget = [lab.name, lab.pi, lab.institution]
        .filter((value): value is string => Boolean(value))
        .join(" ")
        .toLowerCase();
      const matchesSearch = term ? searchTarget.includes(term) : true;

      const matchesCountry = selectedCountry ? lab.country === selectedCountry : true;
      const matchesFocus = focusTerm
        ? (lab.focus_areas ?? []).some((area) => area.toLowerCase().includes(focusTerm))
        : true;

      return matchesSearch && matchesCountry && matchesFocus;
    });
  }, [labs, searchTerm, selectedCountry, selectedFocus]);

  const stats = useMemo(() => {
    const totalLabs = labs.length;
    const totalCountries = countries.length;
    const labsWithPapers = labs.filter((lab) => (lab.paper_count ?? 0) > 0).length;
    const totalPapers = labs.reduce((sum, lab) => sum + (lab.paper_count ?? 0), 0);

    return { totalLabs, totalCountries, labsWithPapers, totalPapers };
  }, [labs, countries.length]);

  const handleResetFilters = useCallback(() => {
    setSearchTerm("");
    setSelectedCountry("");
    setSelectedFocus("");
  }, []);

  return (
    <main className="flex flex-1 flex-col gap-8">
      <section className="space-y-3">
        <div className="space-y-2">
          <span className="inline-flex items-center rounded-full bg-brand/10 px-4 py-1 text-xs font-semibold uppercase tracking-wide text-brand">
            Robotics SOTA
          </span>
          <h1 className="text-3xl font-bold text-slate-900">Robotics Research Labs Dashboard</h1>
          <p className="max-w-3xl text-sm leading-relaxed text-slate-600">
            Explore global robotics research labs, their focus areas, and their latest publications. This
            Next.js + Tailwind redesign keeps the original insights without the interactive map feature.
          </p>
        </div>
      </section>

      <MetricsSummary
        totalLabs={stats.totalLabs}
        totalCountries={stats.totalCountries}
        totalPapers={stats.totalPapers}
        labsWithPapers={stats.labsWithPapers}
        updatedAt={updatedAt}
      />

      <LabFilters
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        selectedCountry={selectedCountry}
        onCountryChange={setSelectedCountry}
        selectedFocus={selectedFocus}
        onFocusChange={setSelectedFocus}
        countries={countries}
        focusAreas={focusAreas}
        onReset={handleResetFilters}
      />

      <LabList labs={filteredLabs} loading={loading} error={error} />
    </main>
  );
}
