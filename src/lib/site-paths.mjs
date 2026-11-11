/** Build URLs for both a domain root and a GitHub Pages project subdirectory. */
export function createSitePaths(base = '/') {
  const prefix = `/${base.split('/').filter(Boolean).join('/')}`;
  const root = prefix === '/' ? '' : prefix;
  const withBase = value => {
    if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//')) return value;
    if (root && (value === root || value.startsWith(`${root}/`) || value.startsWith(`${root}?`) || value.startsWith(`${root}#`))) return value;
    return `${root}${value}`;
  };
  const withoutBase = pathname => {
    if (root && pathname === root) return '/';
    return root && pathname.startsWith(`${root}/`) ? pathname.slice(root.length) : pathname;
  };
  return {withBase, withoutBase};
}
