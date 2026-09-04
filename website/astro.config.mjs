// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://coolsam726.github.io/avalon',
	// Astro's audit toolbar currently throws (M_ID) on these pages; docs don't need it.
	devToolbar: { enabled: false },
	integrations: [
		starlight({
			title: 'Avalon',
			description:
				'The elegant Python web framework for artisans who love Laravel-shaped apps.',
			logo: {
				src: './src/assets/avalon-banner.svg',
				alt: 'Avalon',
				replacesTitle: true,
			},
			favicon: '/favicon.svg',
			social: [
				{
					icon: 'github',
					label: 'GitHub',
					href: 'https://github.com/coolsam726/avalon',
				},
			],
			editLink: {
				baseUrl: 'https://github.com/coolsam726/avalon/edit/main/website/',
			},
			customCss: ['./src/styles/custom.css'],
			expressiveCode: {
				themes: ['one-dark-pro'],
				useStarlightDarkModeSwitch: false,
				useStarlightUiThemeColors: false,
				// Avoid hashed /_astro/ec.*.css 404s across pages in Vite/dev
				// (different pages were emitting different hashes; only one existed).
				emitExternalStylesheet: false,
				styleOverrides: {
					borderRadius: '0.85rem',
					borderWidth: '1px',
					codeFontFamily: "'JetBrains Mono', ui-monospace, monospace",
					codeFontSize: '0.9rem',
					codeBackground: '#282c34',
					codeForeground: '#abb2bf',
					frames: {
						shadowColor: 'rgba(0, 0, 0, 0.4)',
						editorBackground: '#282c34',
						terminalBackground: '#282c34',
					},
				},
			},
			head: [
				{
					tag: 'link',
					attrs: {
						rel: 'preconnect',
						href: 'https://fonts.googleapis.com',
					},
				},
				{
					tag: 'link',
					attrs: {
						rel: 'preconnect',
						href: 'https://fonts.gstatic.com',
						crossorigin: true,
					},
				},
			],
			sidebar: [
				{
					label: 'Getting Started',
					items: [
						{ label: 'Installation', slug: 'installation' },
						{ label: 'Directory Structure', slug: 'structure' },
					],
				},
				{
					label: 'The Basics',
					items: [{ label: 'Middleware', slug: 'middleware' }],
				},
				{
					label: 'Database',
					items: [
						{ label: 'Getting Started', slug: 'database' },
						{ label: 'Query Builder', slug: 'database/queries' },
						{ label: 'Pagination', slug: 'database/pagination' },
						{ label: 'Migrations', slug: 'database/migrations' },
						{ label: 'Seeding', slug: 'database/seeding' },
					],
				},
				{
					label: 'Caliburn',
					items: [
						{ label: 'Getting Started', slug: 'caliburn' },
						{ label: 'Rendering Views', slug: 'caliburn/rendering' },
						{ label: 'Layouts & Inheritance', slug: 'caliburn/layouts' },
						{ label: 'Components & Slots', slug: 'caliburn/components' },
						{ label: 'Control Structures', slug: 'caliburn/control' },
						{ label: 'Including Subviews', slug: 'caliburn/includes' },
						{ label: 'Stacks & Directives', slug: 'caliburn/stacks' },
					],
				},
				{
					label: 'Articulate',
					items: [
						{ label: 'Getting Started', slug: 'articulate' },
						{ label: 'Relationships', slug: 'articulate/relationships' },
						{ label: 'Collections', slug: 'articulate/collections' },
						{ label: 'Soft Deletes & Events', slug: 'articulate/events' },
					],
				},
			],
		}),
	],
});
