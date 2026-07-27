/* ---------------------------------------------------------------------------
   Single source of truth for every piece of resume content on the site.
   Nothing here is duplicated into markup — components read from this file, so
   updating a job title or a metric is a one-line edit.

   Deliberately absent: street address and phone number. This repo is public;
   keeping them out of the source is the point, not hiding them with CSS.
   --------------------------------------------------------------------------- */

export interface Metric {
  /** The number itself, already scaled — e.g. 4300 for "4,300+" */
  value: number;
  /** Rendered before the number */
  prefix?: string;
  /** Rendered after the number */
  suffix?: string;
  /** Decimal places to animate/display */
  decimals?: number;
  label: string;
  /** The story behind the number — shown under the label */
  detail: string;
}

export interface Role {
  title: string;
  /** Team or org, where the resume names one */
  team?: string;
  /** Date range, where the resume gives one per role rather than per employer */
  dates?: string;
  achievements: string[];
}

export interface Tenure {
  company: string;
  location: string;
  start: string;
  end: string;
  /** Year span used to position the tenure bar on the timeline */
  startYear: number;
  endYear: number;
  /** true = current employer, rendered as "Present" */
  current?: boolean;
  /** Roles held, most recent first. */
  roles: Role[];
}

export interface Skill {
  name: string;
  /** Years of hands-on experience; drives bar length */
  years: number;
  /** Shown when years would be misleading (e.g. recent but growing) */
  note?: string;
  detail: string;
}

export interface SkillGroup {
  name: string;
  skills: Skill[];
}

export const profile = {
  name: 'Greg Chedwick',
  shortName: 'Greg',
  title: 'Senior Data Analyst',
  company: 'Microsoft',
  location: 'Reno, NV',
  email: 'gregchedwick@outlook.com',
  linkedin: 'https://www.linkedin.com/in/gregchedwick/',
  github: 'https://github.com/gregchedwick',
  tagline:
    'Domain agnostic: I build the pipelines, then the dashboards and automation ' +
    'people actually use.',
  summary:
    'Senior engineering and analytics professional with 20+ years in data analytics, 6+ of them ' +
    'leading initiatives, across software licensing, mortgage and consumer lending, advertising, ' +
    'supply chain, and freight. I engineer scalable solutions — data modeling, transformation, ' +
    'warehousing, and ETL pipelines in SQL and Python — then build the dashboards and AI-driven ' +
    'automation that sit on top of them, treating data quality and privacy as requirements rather ' +
    'than afterthoughts. I do my best work in ambiguous 0-to-1 territory with minimal oversight.',
} as const;

/** Headline numbers for the stat tiles. Every one is traceable to a role below. */
export const metrics: Metric[] = [
  {
    value: 4300,
    suffix: '+',
    label: 'Hours automated per year',
    detail: 'Anniversary and mid-term ordering workflows, enabling 3x business scaling in two years',
  },
  {
    value: 106,
    prefix: '$',
    suffix: 'M',
    label: 'On-time renewal lift',
    detail: 'Driven by compliance analytics and automated deep-dive reporting',
  },
  {
    value: 3.2,
    prefix: '$',
    suffix: 'B',
    decimals: 1,
    label: 'Agreement portfolio in view',
    detail: 'Power BI dashboards giving stakeholders live visibility into portfolio health',
  },
  {
    value: 31,
    prefix: '$',
    suffix: 'M',
    label: 'Cost reduction',
    detail: 'Data-driven business cases built with DMAIC and Agile methodologies',
  },
  {
    value: 5.7,
    prefix: '$',
    suffix: 'B',
    decimals: 1,
    label: 'Revenue enabled',
    detail: 'Process and system improvements substantiated through analytics',
  },
  {
    value: 60,
    prefix: '$',
    suffix: 'B+',
    label: 'Portfolio remediated',
    detail: 'Loan modification campaigns supporting $25B+ in government programs',
  },
];

export const tenures: Tenure[] = [
  {
    company: 'Microsoft',
    location: 'Reno, NV',
    start: 'Jun 2015',
    end: 'Present',
    startYear: 2015,
    endYear: new Date().getFullYear(),
    current: true,
    roles: [
      {
        title: 'Senior Data Analyst',
        team: 'Fusion Development, Operations Service Center',
        dates: 'Aug 2022 – Present',
        achievements: [
          'Engineered scalable licensing data models, automated workflows, and developed Power Apps that automated anniversary and mid-term ordering — saving 4,300+ hours annually and enabling 3x business scaling over two years.',
          'Developed compliance analytics metrics and Power BI dashboards giving visibility into a $3.2B+ agreement portfolio, driving a $106M increase in on-time renewals.',
          'Designed agreement complexity models to identify bottlenecks, enabling targeted root-cause investigations and scalable automation for ad-hoc requests.',
          'Built custom AI automation with Copilot Studio to enable stakeholder self-service, integrate disparate data sources, and accelerate insight delivery.',
        ],
      },
      {
        title: 'Business Analytics Specialist',
        team: 'Business Process & Analytics, Commercial Ops',
        dates: 'Aug 2018 – Jul 2022',
        achievements: [
          'Led global analytics backlog prioritization using Cost of Delay / Weighted Shortest Job First within a SAFe framework, ensuring timely deployment of high-impact BI across software licensing, advertising, and supply chain.',
          'Partnered with cross-functional stakeholders to define requirements and ship scalable dashboards that informed decisions and supported new program launches.',
          'Developed automated reporting pipelines and self-service tools across digital attach, hardware compliance, search, and advertising.',
        ],
      },
      {
        title: 'Business Operations Analyst',
        team: 'Process Management, Commercial Ops',
        dates: 'Jun 2015 – Jul 2018',
        achievements: [
          'Crafted data-driven business cases using DMAIC and Agile methodologies, substantiating improvements that cut costs by $31M, reduced AR exposure by $400M, and enabled $5.7B in revenue.',
          'Engineered BI solutions and monitoring dashboards to track outcomes of process and system improvements.',
        ],
      },
    ],
  },
  {
    company: 'Bank of America',
    location: 'Reno, NV',
    start: 'Aug 2010',
    end: 'May 2015',
    startYear: 2010,
    endYear: 2015,
    roles: [
      {
        title: 'Vice President, Consumer Products Strategic Manager',
        team: 'Loan Loss Mitigation and Portfolio Analytics',
        dates: 'Aug 2010 – May 2015',
        achievements: [
          'Led the analytics team behind loan modification campaigns, remediating a $60B+ portfolio and supporting $25B+ in government programs through advanced BI and reporting.',
          'Managed BI strategy, reporting, and operational process for Enterprise Complaint Resolution, covering mortgage, credit card, and deposit escalations from state attorneys general, elected officials, the CFPB, the OCC, and other regulators.',
          'Presented program performance, risk trends, and operational insight to executive leadership, advising on initiatives that improved complaint resolution efficiency and regulatory compliance.',
          'Directed production of the National Mortgage Settlement Servicing Standard Scorecard for executive review and submission to the Office of Mortgage Settlement Oversight.',
          'Oversaw reporting and process development for the U.S. DOJ National Mortgage Settlement Program, enabling modification of $25B+ in loan balances.',
          'Managed a team of 4 senior analysts and coordinated 8 operational managers across loan modification and complaint resolution programs.',
          'Built and automated an enterprise-grade BI and data warehouse supporting marketing, production, modeling, forecasting, and operational decision-making across proprietary and government programs.',
          'Analyzed portfolio trends across risk, losses, delinquency roll rates, payment shock, rate resets, and FICO vintage, alongside campaign effectiveness, and delivered the findings to executive leadership.',
          'Led cross-functional work with finance, technology, marketing, legal, compliance, and executive management to optimize program performance and regulatory adherence.',
          'Directed UAT, training, and deployment of loan modification and refinance tools across multiple business lines.',
        ],
      },
    ],
  },
  {
    company: 'Charles Schwab Bank',
    location: 'Reno, NV',
    start: 'Aug 2003',
    end: 'Aug 2010',
    startYear: 2003,
    endYear: 2010,
    roles: [
      {
        title: 'Finance Manager, Bank Finance',
        team: 'Bank Finance',
        dates: 'Aug 2003 – Aug 2010',
        achievements: [
          'Built and administered enterprise loan, sales, and marketing databases supporting Finance, Credit, Compliance, and senior leadership.',
          'Led analytics infrastructure modernization, serving as subject matter expert for the MS Access to SQL Server migration.',
          'Enhanced and managed loan pricing models, and executed pricing exception decisions using ROE, spreads, cost of funds, LTV, FICO, and credit history.',
          'Produced executive-level reporting for the Board of Directors, ALCO, and the Credit Risk Management Committee.',
          'Designed delinquency roll-rate, industry comparison, and portfolio vintage analytics to assess performance and risk trends.',
          'Developed industry rate databases and analyses guiding Pricing Committee lending decisions.',
          'Built marketing effectiveness analytics enabling strategic campaign decisions for the Chief Marketing Officer.',
          'Created streamlined pricing exception processes, improving the speed and consistency of lending decisions.',
          'Managed junior analysts to ensure accurate, timely reporting across Finance, Credit, Accounting, Marketing, Legal, and Compliance.',
          'Coordinated regulatory reporting for the Office of Thrift Supervision and supported OCC annual review analytics.',
        ],
      },
    ],
  },
];

export const skillGroups: SkillGroup[] = [
  {
    name: 'Data & BI',
    skills: [
      { name: 'SQL', years: 15, detail: 'Complex querying, data modeling, large-scale analysis' },
      // The resume combines these as "SQL/KQL (15+/ 5+ years)". Split here because
      // bar length is years — one row would have to claim 15 for both.
      { name: 'KQL', years: 5, detail: 'Kusto queries over log and telemetry data' },
      { name: 'Power BI & DAX', years: 10, detail: 'Interactive dashboards, reporting, visualization' },
      {
        name: 'SSMS & VS Code',
        years: 10,
        detail: 'Data modeling, analysis, AI-assisted coding with Claude Code and Copilot CLI',
      },
    ],
  },
  {
    name: 'Data Engineering',
    skills: [
      { name: 'Microsoft Fabric & SSIS', years: 10, detail: 'ETL pipelines, SQL databases, lakehouses' },
      { name: 'Azure DevOps', years: 10, detail: 'Plan, build, test, and deploy solutions' },
      {
        name: 'Azure Platform Services',
        years: 5,
        detail: 'Function Apps, Logic Apps, Data Factory, serverless automation',
      },
      { name: 'Python', years: 2, note: 'Growing', detail: 'Data manipulation, scripting, automation' },
    ],
  },
  {
    name: 'Automation & AI',
    skills: [
      { name: 'Power Automate & Power Apps', years: 7, detail: 'Workflow automation and self-service tools' },
      { name: 'Microsoft Copilot Studio', years: 2, note: 'Recent', detail: 'AI agents, low-code intelligent automation' },
    ],
  },
];

export const education = [
  {
    school: 'University of Nevada, Reno',
    degree: 'Master of Business Administration',
    detail: 'GPA 4.0 · Data Resource Management, Information & Communication Technology, Strategic Management',
    year: '2013',
  },
  {
    school: 'California State University, East Bay',
    degree: 'B.S. Business Administration',
    detail: 'Minor in Computer Science',
    year: '1998',
  },
];
