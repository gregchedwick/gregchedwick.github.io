/* ---------------------------------------------------------------------------
   Tools for the scrolling ticker above the skills section.

   The glyphs are hand-authored, single-path marks drawn in each product's brand
   colour — deliberately not reproductions of the official logos. A traced copy
   of a Microsoft trademark would be both a licensing question and, at 28px,
   a worse-looking mark than a purpose-drawn glyph. Each path uses `currentColor`
   so the grey-to-colour transition is a CSS colour change rather than a
   `grayscale()` filter, which keeps the colours exact.

   `years` drives the label; `note` replaces it when a year count would overstate
   things. Both mirror src/data/resume.ts — keep them in step.
   --------------------------------------------------------------------------- */

export interface Tech {
  name: string;
  /** Brand colour, used on hover and focus */
  color: string;
  /** Dark-mode step, where the brand colour is too dark on a near-black surface */
  colorDark?: string;
  years?: number;
  note?: string;
  detail: string;
  /** Inner SVG markup, drawn on a 24x24 viewBox */
  icon: string;
}

export const tech: Tech[] = [
  {
    name: 'SQL',
    color: '#0f7ba8',
    colorDark: '#39a8d6',
    years: 15,
    detail: 'Complex querying, data modeling, and large-scale analysis',
    icon: `<ellipse cx="12" cy="5.5" rx="7.5" ry="3" fill="none" stroke="currentColor" stroke-width="1.8"/>
           <path d="M4.5 5.5v13c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
           <path d="M4.5 12c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>`,
  },
  {
    name: 'KQL',
    color: '#3c4fa8',
    colorDark: '#8f9de8',
    years: 5,
    detail: 'Kusto queries over log and telemetry data',
    // Log lines under a magnifier — a query over records, distinct from SQL's cylinder.
    icon: `<path d="M3 5.5h13M3 10h13M3 14.5h7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
           <circle cx="15.5" cy="16.5" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/>
           <path d="m18.6 19.6 2.4 2.4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>`,
  },
  {
    name: 'Power BI',
    color: '#b8860b',
    colorDark: '#f2c811',
    years: 10,
    detail: 'Interactive dashboards, DAX, reporting, and visualization',
    icon: `<rect x="3" y="14" width="4.5" height="7" rx="1.4" fill="currentColor"/>
           <rect x="9.75" y="8" width="4.5" height="13" rx="1.4" fill="currentColor"/>
           <rect x="16.5" y="3" width="4.5" height="18" rx="1.4" fill="currentColor"/>`,
  },
  {
    name: 'Python',
    color: '#2b6ea3',
    colorDark: '#5b9bd5',
    years: 2,
    note: 'Growing',
    detail: 'Data manipulation, scripting, and automation',
    icon: `<path d="M12 2.5c-3.3 0-5 1.2-5 3.4V9h5.2v1H5.6C3.5 10 2 11.6 2 15s1.3 4.8 3.3 4.8h1.5v-2.9c0-2.2 1.8-3.9 4-3.9h4.4c1.8 0 3.3-1.5 3.3-3.3V5.9c0-2-1.6-3.4-3.6-3.4Zm-2.8 2a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2Z" fill="currentColor"/>
           <path d="M12 21.5c3.3 0 5-1.2 5-3.4V15h-5.2v-1h6.6c2.1 0 3.6-1.6 3.6-5s-1.3-4.8-3.3-4.8h-1.5v2.9c0 2.2-1.8 3.9-4 3.9H8.8c-1.8 0-3.3 1.5-3.3 3.3v4.7c0 2 1.6 3.4 3.6 3.4Zm2.8-2a1.1 1.1 0 1 1 0-2.2 1.1 1.1 0 0 1 0 2.2Z" fill="currentColor" opacity="0.62"/>`,
  },
  {
    name: 'VS Code',
    color: '#0068b8',
    colorDark: '#3ba0e8',
    years: 10,
    detail: 'Data modeling, analysis, and AI-assisted coding with Claude Code and Copilot CLI',
    icon: `<path d="M17.5 2.2 8.2 11.1 4.4 8.2 2.5 9.3l3.2 2.7-3.2 2.7 1.9 1.1 3.8-2.9 9.3 8.9L21.5 20V4l-4-1.8Zm.4 4.6v10.4l-6-5.2 6-5.2Z" fill="currentColor"/>`,
  },
  {
    name: 'Microsoft Fabric',
    color: '#0b7a7e',
    colorDark: '#2bb3b8',
    years: 10,
    detail: 'ETL pipelines, SQL databases, and lakehouses',
    icon: `<path d="M12 2 4 6.5v11L12 22l8-4.5v-11L12 2Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
           <path d="M12 2v20M4 6.5l8 4.5 8-4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>`,
  },
  {
    name: 'SSIS',
    color: '#a82420',
    colorDark: '#e05650',
    years: 10,
    detail: 'ETL packages and data pipeline orchestration',
    icon: `<rect x="2.5" y="3" width="7" height="6" rx="1.6" fill="none" stroke="currentColor" stroke-width="1.8"/>
           <rect x="14.5" y="15" width="7" height="6" rx="1.6" fill="none" stroke="currentColor" stroke-width="1.8"/>
           <path d="M6 9v5.5a2 2 0 0 0 2 2h6.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>`,
  },
  {
    name: 'SSMS',
    color: '#a82420',
    colorDark: '#e05650',
    years: 10,
    detail: 'Manage, query, and administer SQL databases',
    icon: `<ellipse cx="9.5" cy="5.5" rx="6.5" ry="2.6" fill="none" stroke="currentColor" stroke-width="1.8"/>
           <path d="M3 5.5v11c0 1.4 2.9 2.6 6.5 2.6 1 0 2-.1 2.8-.3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
           <path d="M3 11c0 1.4 2.9 2.6 6.5 2.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
           <circle cx="17" cy="17" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/>
           <path d="m20 20 1.5 1.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>`,
  },
  {
    name: 'Azure',
    color: '#0068b8',
    colorDark: '#3ba0e8',
    years: 5,
    detail: 'Function Apps, Logic Apps, Data Factory, and serverless automation',
    icon: `<path d="M9.2 3h5.3l-5.5 15.8 6.4-2.3L12 21.5l9.5-1.7L14.7 3H9.2Z" fill="currentColor" opacity="0.55"/>
           <path d="M8.6 4.6 2.5 19.8h5.2L14 3H9.2l-.6 1.6Z" fill="currentColor"/>`,
  },
  {
    name: 'Azure DevOps',
    color: '#0068b8',
    colorDark: '#3ba0e8',
    years: 10,
    detail: 'Plan, build, test, and deploy solutions',
    // The DevOps infinity loop — far more legible at 22px than the product mark.
    icon: `<path d="M7 7.5c-2.8 0-4.6 2-4.6 4.5S4.2 16.5 7 16.5c2.2 0 3.6-1.7 5-3.9 1.4-2.2 2.8-3.9 5-3.9 2.8 0 4.6 2 4.6 4.5s-1.8 4.5-4.6 4.5c-2.2 0-3.6-1.7-5-3.9-1.4-2.2-2.8-3.9-5-3.9Z" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>`,
  },
  {
    name: 'Power Automate',
    color: '#0b53ce',
    colorDark: '#5d8ff0',
    years: 7,
    detail: 'Workflow automation across licensing, ordering, and reporting',
    icon: `<path d="M13.5 2 4 13.4h6.3L9.8 22 20 10.3h-6.6L13.5 2Z" fill="currentColor"/>`,
  },
  {
    name: 'Power Apps',
    color: '#6f2a6f',
    colorDark: '#b072b0',
    years: 7,
    detail: 'Self-service tools that replaced manual ordering workflows',
    icon: `<path d="M12 2.2 3.4 7.1v9.8L12 21.8l8.6-4.9V7.1L12 2.2Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
           <path d="M12 7.2 7.8 9.6v4.8L12 16.8l4.2-2.4V9.6L12 7.2Z" fill="currentColor"/>`,
  },
  {
    name: 'Dataverse',
    color: '#0a6b5c',
    colorDark: '#3fb9a3',
    years: 3,
    detail: 'Modelled tables, relationships, and solution ALM behind production business apps',
    icon: `<ellipse cx="12" cy="5.6" rx="7.2" ry="2.9" fill="none" stroke="currentColor" stroke-width="1.8"/>
           <path d="M4.8 5.6v12.8c0 1.6 3.2 2.9 7.2 2.9s7.2-1.3 7.2-2.9V5.6" fill="none" stroke="currentColor" stroke-width="1.8"/>
           <path d="M4.8 12c0 1.6 3.2 2.9 7.2 2.9s7.2-1.3 7.2-2.9" fill="none" stroke="currentColor" stroke-width="1.8"/>`,
  },
  {
    name: 'Copilot Studio',
    color: '#0b6a86',
    colorDark: '#38b0cf',
    note: 'Recent',
    detail: 'AI agents and low-code intelligent automation for stakeholder self-service',
    icon: `<path d="M12 2.5 14 9l6.5 2-6.5 2-2 6.5-2-6.5L3.5 11 10 9l2-6.5Z" fill="currentColor"/>
           <path d="M19 15.5l.9 2.6 2.6.9-2.6.9-.9 2.6-.9-2.6-2.6-.9 2.6-.9.9-2.6Z" fill="currentColor" opacity="0.6"/>`,
  },
];
