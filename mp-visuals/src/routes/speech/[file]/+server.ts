import type { RequestHandler } from '@sveltejs/kit';
import { createReadStream, promises as fs } from 'fs';
import path from 'path';

const speechDir: string = path.resolve('../speech');

export const GET: RequestHandler = async ({ params }) => {
	const fileParam = params.file;

	if (!fileParam) {
		return new Response('Missing file parameter', { status: 400 });
	}

	const fileName: string = path.basename(fileParam);
	const filePath: string = path.join(speechDir, fileName);

	try {
		await fs.access(filePath); // ensure file exists

		const stream = createReadStream(filePath);

		return new Response(stream as unknown as ReadableStream, {
			headers: {
				'Content-Type': 'audio/mpeg',
				'Cache-Control': 'no-cache'
			}
		});
	} catch {
		return new Response('Not found', { status: 404 });
	}
};
