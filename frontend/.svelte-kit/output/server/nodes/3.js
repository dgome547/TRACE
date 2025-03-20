

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/admin/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/3.SOagDvs7.js","_app/immutable/chunks/DQOls_oE.js","_app/immutable/chunks/D_cHL4BB.js","_app/immutable/chunks/LFAF7uX4.js"];
export const stylesheets = ["_app/immutable/assets/3.r_MUY0qq.css"];
export const fonts = [];
