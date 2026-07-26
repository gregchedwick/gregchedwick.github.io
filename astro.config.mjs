// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Drives canonical URLs and the sitemap. Paired with public/CNAME, which is
  // what actually tells GitHub Pages the custom domain — that file must live in
  // the published artifact, or each deploy would clear the domain set in the
  // repo settings.
  site: 'https://gregchedwick.dev',
  integrations: [sitemap()],
});
