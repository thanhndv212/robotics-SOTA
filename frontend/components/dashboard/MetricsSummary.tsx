interface MetricsSummaryProps {
  totalLabs: number;
  totalCountries: number;
  totalPapers: number;
  labsWithPapers: number;
  updatedAt?: Date | null;
}

const formatDate = (value?: Date | null) => {
  if (!value) return "–";
  return value.toLocaleString();
};

const cards: Array<{
  label: string;
  icon: string;
  color: string;
  key: keyof MetricsSummaryProps;
}> = [
  { label: "Total Labs", icon: "🤖", color: "bg-blue-500", key: "totalLabs" },
  { label: "Countries", icon: "🌍", color: "bg-emerald-500", key: "totalCountries" },
  { label: "Research Papers", icon: "📄", color: "bg-indigo-500", key: "totalPapers" },
  { label: "Labs w/ Papers", icon: "📚", color: "bg-purple-500", key: "labsWithPapers" }
];

export default function MetricsSummary({
  totalLabs,
  totalCountries,
  totalPapers,
  labsWithPapers,
  updatedAt = null
}: MetricsSummaryProps) {
  const values: MetricsSummaryProps = {
    totalLabs,
    totalCountries,
    totalPapers,
    labsWithPapers,
    updatedAt
  };

  return (
    <section className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map(({ label, icon, color, key }) => (
          <article
            key={label}
            className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
          >
            <div className="flex items-center gap-4 px-5 py-6">
              <span className={`flex h-12 w-12 items-center justify-center rounded-full text-xl text-white ${color}`}>
                {icon}
              </span>
              <div>
                <p className="text-sm font-medium text-slate-500">{label}</p>
                <p className="text-2xl font-semibold text-slate-900">
                  {values[key as keyof MetricsSummaryProps] as number}
                </p>
              </div>
            </div>
          </article>
        ))}
      </div>
      <p className="text-xs text-slate-500">
        Last refreshed: <span className="font-medium text-slate-700">{formatDate(updatedAt)}</span>
      </p>
    </section>
  );
}
