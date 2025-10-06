export interface Paper {
  id: number;
  title: string;
  authors: string;
  abstract?: string;
  publication_date?: string;
  venue?: string;
  paper_type?: string;
  arxiv_id?: string;
  doi?: string;
  pdf_url?: string;
  website_url?: string;
}

export interface Lab {
  id: number;
  name: string;
  pi: string;
  institution: string;
  city?: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  focus_areas?: string[];
  website?: string;
  description?: string;
  established_year?: number;
  funding_sources?: string[];
  papers?: Paper[];
  paper_count?: number;
  lab_type?: string;
  parent_lab_id?: number;
  parent_lab?: string;
  sub_groups?: Lab[];
  sub_groups_count?: number;
}
