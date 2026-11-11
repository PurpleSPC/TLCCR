import sharp from 'sharp';
import { mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
const archive = resolve('../Photos/From-current-site');
const images = {
  ponies: 'the_usual_suspects.jpg', creek: 'minis_in_creek2.jpg', pond: 'IMG_8410.jpg',
  goat: 'IMG_13091.jpg', people: 'IMG_14301.jpg',
  emu: 'Missionary-volunteers-08-RS.jpg', legacy: 'cropped-Box3-IMG1323-scaled-1.jpg',
  encounter: 'Low_little-boy-feeding-goat-in-the-garden.jpg',
  kiss: 'IMG_4125-goat-kisses.jpg', bridge: 'horse-on-bridge.jpg',
};
await mkdir('public/images/concepts', {recursive:true});
for (const [name, file] of Object.entries(images)) {
  await sharp(resolve(archive, file)).rotate().resize({width:1800, withoutEnlargement:true}).jpeg({quality:85, mozjpeg:true}).toFile(`public/images/concepts/${name}.jpg`);
}
console.log(`Prepared ${Object.keys(images).length} concept images from the existing photo archive.`);
