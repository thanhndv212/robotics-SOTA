"use client";

import type { Lab } from "../../types/lab";

interface LabCardProps {
  lab: Lab;
}

const formatDate = (value?: string) => {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString();
};

export default function LabCard({ lab }: LabCardProps) {
  const recentPapers = (lab.papers ?? [])
    .slice()
    .sort((a, b) => {
      const timeA = new Date(a.publication_date ?? 0).getTime();
      const timeB = new Date(b.publication_date ?? 0).getTime();
      return timeB - timeA;
    })
    .slice(0, 3);

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="border-b border-slate-200 bg-slate-100 px-5 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">{lab.name}</h3>
            <p className="text-sm text-slate-500">{lab.institution}</p>
          </div>
          {lab.paper_count ? (
            <span className="inline-flex items-center rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
              {lab.paper_count} papers
            </span>
          ) : null}
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-4 px-5 py-4">
        <div className="grid gap-2 text-sm text-slate-600">
          <p>
            <span className="font-semibold text-slate-700">Principal Investigator:</span> {lab.pi}
          </p>
          <p>
            <span className="font-semibold text-slate-700">Location:</span> {lab.city ?? "Unknown"}, {lab.country ?? "–"}
          </p>
          {lab.website ? (
            <p>
              <a
                href={lab.website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm font-medium text-brand hover:text-brand-dark"
              >
                Visit website ↗
              </a>
            </p>
          ) : null}
        </div>

        {lab.focus_areas && lab.focus_areas.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Focus areas
            </h4>
            <div className="flex flex-wrap gap-2">
              {lab.focus_areas.map((area) => (
                <span
                  key={area}
                  className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
                >
                  {area}
                </span>
              ))}
            </div>
          </div>
        )}

        {lab.description ? (
          <p className="text-sm leading-relaxed text-slate-600">{lab.description}</p>
        ) : null}

        {recentPapers.length > 0 ? (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Recent papers
            </h4>
            <ul className="space-y-2 text-sm text-slate-600">
              {recentPapers.map((paper) => (
                <li key={`${lab.id}-${paper.id}`} className="rounded-lg bg-slate-50 px-3 py-2">
                  <p className="font-medium text-slate-800">{paper.title}</p>
                  <p className="text-xs text-slate-500">
                    {formatDate(paper.publication_date)}
                    {paper.venue ? ` • ${paper.venue}` : ""}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs font-medium">
                    {paper.pdf_url ? (
                      <a
                        href={paper.pdf_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-brand hover:text-brand-dark"
                      >
                        PDF
                      </a>
                    ) : null}
                    {paper.arxiv_id ? (
                      <a
                        href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-brand hover:text-brand-dark"
                      >
                        arXiv
                      </a>
                    ) : null}
                    {paper.doi ? (
                      <a
                        href={`https://doi.org/${paper.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-brand hover:text-brand-dark"
                      >
                        DOI
                      </a>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </article>
  );
}
