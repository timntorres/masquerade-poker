import type { PageServerLoad } from './$types';
import { promises as fs } from 'fs';
import path from 'path';

type Action = {
	// define your actual structure here
	type: string;
	payload: unknown;
};

export const load: PageServerLoad = async () => {
	// --- SAVES ---
	const savesDir: string = path.resolve('../saves');

	const files: string[] = await fs.readdir(savesDir);
	const jsonFiles: string[] = files.filter((f) => f.endsWith('.json'));

	let items: Action[] = [];

	if (jsonFiles.length > 0) {
		jsonFiles.sort((a, b) => a.localeCompare(b));
		const latestFile: string = jsonFiles[jsonFiles.length - 1];

		const filePath: string = path.join(savesDir, latestFile);
		const fileContent: string = await fs.readFile(filePath, 'utf-8');

		items = JSON.parse(fileContent) as Action[];
	}

	// --- AUDIO ---
	const speechDir: string = path.resolve('../speech');
	const speechFiles: string[] = await fs.readdir(speechDir);

	const audioFiles: string[] = speechFiles.filter((f) => f.endsWith('.wav'));

	const audioUrls: string[] = audioFiles.map((f) => `/speech/${encodeURIComponent(f)}`);

	return {
		items,
		audioUrls
	};
};
