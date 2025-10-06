"use client";

import type { Lab } from "../../types/lab";
import LabCard from "./LabCard";

interface LabListProps {
  labs: Lab[];
  loading: boolean;
  error: string | null;
}

export default function LabList({ labs, loading, error }: LabListProps) {
  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center rounded-xl border border-slate-200 bg-white p-12 shadow-sm">
        <p className="text-sm font-medium text-slate-600">Loading robotics labs…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-1 items-center justify-center rounded-xl border border-red-200 bg-red-50 p-12 text-center shadow-sm">
        <div className="space-y-3">
          <p className="text-lg font-semibold text-red-700">We couldn’t load the labs.</p>
          <p className="text-sm text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (labs.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center rounded-xl border border-slate-200 bg-white p-12 text-center shadow-sm">
        <div className="space-y-3">
          <p className="text-lg font-semibold text-slate-800">No labs match your filters.</p>
          <p className="text-sm text-slate-500">Try clearing the filters or adjusting your search.</p>
        </div>
      </div>
    );
  }

  return (
    <section className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3">
      {labs.map((lab) => (
        <LabCard key={lab.id} lab={lab} />
      ))}
    </section>
  );
}
