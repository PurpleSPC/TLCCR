import { createReader } from '@keystatic/core/reader';
import process from 'node:process';
import config from '../../keystatic.config';
import { visibleEvents } from './events.mjs';

export const reader = createReader(process.cwd(), config);
export const getSettings = () => reader.singletons.settings.readOrThrow();
export const getHome = () => reader.singletons.homepage.readOrThrow();
export async function getAnimals() {
  return (await reader.collections.animals.all()).filter(a => a.entry.status === 'published').sort((a, b) => (a.entry.order ?? 10) - (b.entry.order ?? 10));
}
export async function getEvents() {
  return visibleEvents(await reader.collections.events.all());
}
export function paragraphs(text: string | null | undefined) { return (text || '').split(/\r?\n\s*\r?\n/).filter(Boolean); }
export function emailLink(email: string, subject: string) { return `mailto:${email}?subject=${encodeURIComponent(subject)}`; }
