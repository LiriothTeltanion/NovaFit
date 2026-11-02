// Local profiles. Each profile owns a separate IndexedDB database, so records can never mix and deleting a
// profile removes exactly its data. Profile 1 keeps the original database name, so existing data stays put.
import Dexie from 'dexie';
import { NovaFitWebDb } from './db';

export interface Profile {
  id: number;
  name: string;
}

const KEY = 'novafit-web:profiles';
export const PRIMARY: Profile = { id: 1, name: 'Primary User' };

export function readProfiles(): Profile[] {
  try {
    const list = JSON.parse(localStorage.getItem(KEY) ?? '[]') as Profile[];
    const valid = list.filter((p) => Number.isInteger(p.id) && p.id > 1 && typeof p.name === 'string' && p.name.trim());
    const primary = list.find((p) => p.id === 1);
    return [{ ...PRIMARY, name: primary?.name?.trim() || PRIMARY.name }, ...valid];
  } catch {
    return [PRIMARY];
  }
}

export function saveProfiles(profiles: Profile[]): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(profiles));
  } catch {
    /* private mode: profile list is not remembered */
  }
}

export function validateName(name: string, profiles: Profile[], exceptId?: number): string {
  const clean = name.split(/\s+/).filter(Boolean).join(' ');
  if (!clean) throw new Error('Display name is required.');
  if (clean.length > 40) throw new Error('Display name cannot exceed 40 characters.');
  if (profiles.some((p) => p.id !== exceptId && p.name.toLocaleLowerCase() === clean.toLocaleLowerCase())) {
    throw new Error('A profile with that name already exists.');
  }
  return clean;
}

export const databaseName = (base: string, id: number) => (id === 1 ? base : `${base}-p${id}`);

const opened = new Map<string, NovaFitWebDb>();
export function storeFor(base: NovaFitWebDb, id: number): NovaFitWebDb {
  if (id === 1) return base;
  const name = databaseName(base.name, id);
  if (!opened.has(name)) opened.set(name, new NovaFitWebDb(name));
  return opened.get(name)!;
}

export async function deleteProfileData(base: NovaFitWebDb, id: number): Promise<void> {
  if (id === 1) throw new Error('The primary profile cannot be deleted; rename it instead.');
  const name = databaseName(base.name, id);
  opened.get(name)?.close();
  opened.delete(name);
  await Dexie.delete(name);
}
