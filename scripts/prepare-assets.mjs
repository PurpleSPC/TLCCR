import sharp from 'sharp';
import { mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
const sources = {
  'goat-portrait': 'IMG_7558.JPEG',
  'goats-together': 'IMG_7567.JPEG',
  'parrot': 'IMG_7552.JPEG',
  'miniature-horse': 'IMG_7610.JPEG',
  'swans': 'IMG_7570.JPEG',
  'emu': 'IMG_7673.JPEG',
};
await mkdir('public/images/uploads', { recursive: true });
for (const [name, source] of Object.entries(sources)) {
  await sharp(resolve('..', 'Photos', source)).rotate().resize({ width: 1400, withoutEnlargement: true }).jpeg({ quality: 85, mozjpeg: true }).toFile(`public/images/uploads/${name}.jpg`);
  console.log(`Prepared ${name}.jpg`);
}
