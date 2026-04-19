import fs from 'fs/promises';
import path from 'path';
import type { Action } from './interfaces';

export const load = async () => {
	const savesDir = path.resolve('../saves');

	// Read all files in the directory
	const files = await fs.readdir(savesDir);

	// Filter for .json files only
	const jsonFiles = files.filter((f) => f.endsWith('.json'));

	if (jsonFiles.length === 0) {
		return { items: [] as Action[] };
	}

	// Sort alphabetically and get the last one
	jsonFiles.sort((a, b) => a.localeCompare(b));
	const latestFile = jsonFiles[jsonFiles.length - 1];

	// Read and parse the file
	const filePath = path.join(savesDir, latestFile);
	const fileContent = await fs.readFile(filePath, 'utf-8');

	const items: Action[] = JSON.parse(fileContent);

	return {
		items
	};
};
