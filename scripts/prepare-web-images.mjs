import sharp from 'sharp';
import {readdir, stat} from 'node:fs/promises';
import {join, extname} from 'node:path';

let originals = 0;
let optimized = 0;
let count = 0;
async function prepare(folder) {
  for (const entry of await readdir(folder,{withFileTypes:true})) {
    const path = join(folder,entry.name);
    if (entry.isDirectory()) { await prepare(path); continue; }
    if (!/\.jpe?g$/i.test(entry.name)) continue;
    const output = path.slice(0,-extname(path).length)+'.webp';
    await sharp(path).rotate().resize({width:1600,withoutEnlargement:true}).webp({quality:76,effort:5}).toFile(output);
    originals += (await stat(path)).size;
    optimized += (await stat(output)).size;
    count++;
  }
}
await prepare('public/images');
console.log(`Prepared ${count} WebP photos: ${(originals/1024/1024).toFixed(1)} MB → ${(optimized/1024/1024).toFixed(1)} MB. Source JPEGs preserved.`);
