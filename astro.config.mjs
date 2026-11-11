import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import keystatic from '@keystatic/astro';

const githubPages = process.env.GITHUB_ACTIONS === 'true' && process.env.GITHUB_REPOSITORY;
const repository = process.env.GITHUB_REPOSITORY?.split('/')[1];
const owner = process.env.GITHUB_REPOSITORY_OWNER || process.env.GITHUB_REPOSITORY?.split('/')[0];
const base = process.env.BASE_PATH || (githubPages ? `/${repository}/` : '/');
const site = process.env.SITE_URL || (githubPages ? `https://${owner}.github.io` : 'https://www.crittercreekranch.org');

// Local filesystem editing is available only in development. The published
// build is static and never exposes an unauthenticated content-write API.
export default defineConfig({
  site,
  base,
  output: 'static',
  // Keystatic calls extensionless API routes without a trailing slash.
  trailingSlash: process.env.NODE_ENV === 'development' ? 'ignore' : 'always',
  integrations: process.env.NODE_ENV === 'development' ? [react(), keystatic()] : [],
  devToolbar: { enabled: false },
});
