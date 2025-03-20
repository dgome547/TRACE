

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/homeScreen/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/3.BGHMYTMk.js","_app/immutable/chunks/C5CMfB9T.js","_app/immutable/chunks/Bh_pQRl2.js","_app/immutable/chunks/DgCaneqZ.js"];
export const stylesheets = [];
export const fonts = [];
