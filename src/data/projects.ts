export interface Project {
  slug: string;
  title: string;
  blurb: string;
  /** What the project actually demonstrates, in hiring-manager terms */
  role: string;
  stack: string[];
  repo?: string;
  highlights: string[];
  status: 'live' | 'in-progress';
}

export const projects: Project[] = [
  {
    slug: 'carrier-survival',
    title: 'Carrier Survival Model',
    blurb:
      'A predictive model that estimates whether a trucking carrier will still be operating twelve ' +
      'months from now, built from public FMCSA data. Brokers and insurers can check whether ' +
      'authority is active today; nothing tells them the odds it lasts the length of a contract.',
    role: 'Problem framing, data forensics, feature engineering, modelling, validation',
    stack: ['Python', 'scikit-learn', 'Pandas', 'Parquet', 'pytest', 'Survival analysis'],
    repo: 'https://github.com/gregchedwick/carrier-survival',
    status: 'live',
    highlights: [
      'Discriminates at 0.889 AUC across 1.9M carriers — reviewing the riskiest 10% surfaces 58% of all failures',
      'Well calibrated (ECE 0.0008), so predicted risk is usable for pricing and not only for triage',
      'Thirteen silent data defects found and each fitted with an automated guardrail and regression test',
    ],
  },
  {
    slug: 'netflix-ads-analytics',
    title: 'Netflix Ads Analytics',
    blurb:
      'An end-to-end analytics project simulating what an ad platform team needs to decide where ad ' +
      'inventory is worth buying — built as if for Netflix’s ad-supported tier.',
    role: 'Data ingestion through to a scored, ranked, decision-ready output',
    stack: ['Python', 'Pandas', 'Matplotlib', 'Jupyter', 'Power BI', 'Git'],
    repo: 'https://github.com/gregchedwick/Netflix-Ads-Analytics',
    status: 'live',
    highlights: [
      'Cleaned and merged 32,000+ Netflix titles with 2025–26 global top-500 viewership data',
      'Designed a custom Ad Opportunity Score weighting hours viewed, sustained relevance, ratings, and recency',
      'Shipped an interactive Power BI dashboard alongside the notebook',
    ],
  },
  {
    slug: 'this-site',
    title: 'This Site',
    blurb:
      'The portfolio you’re reading. Built as a static site so the resume itself renders as live data ' +
      'visualization rather than a PDF nobody opens.',
    role: 'Design, build, and deployment',
    stack: ['Astro', 'TypeScript', 'SVG', 'GitHub Actions'],
    repo: 'https://github.com/gregchedwick/gregchedwick.github.io',
    status: 'live',
    highlights: [
      'Career history and impact metrics render from a single typed data file',
      'Charts validated for colorblind separation and contrast in both light and dark mode',
      'Deploys automatically to GitHub Pages on every push to main',
    ],
  },
];
