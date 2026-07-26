// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Repo is named `gregchedwick.github.io`, so GitHub serves it as a user page at
  // the domain root — no `base` path needed. When gregchedwick.dev is purchased,
  // change only this line (and add public/CNAME).
  site: 'https://gregchedwick.github.io',
  integrations: [sitemap()],
});
