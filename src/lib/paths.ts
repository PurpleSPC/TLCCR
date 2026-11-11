import {createSitePaths} from './site-paths.mjs';
export const {withBase, withoutBase} = createSitePaths(import.meta.env.BASE_URL);
// The staff editor shows original uploads immediately; production serves build-generated WebP copies.
export const imageSrc = (value: string | null | undefined) => withBase(
  import.meta.env.PROD && value?.startsWith('/images/') ? value.replace(/\.jpe?g$/i, '.webp') : value
);
