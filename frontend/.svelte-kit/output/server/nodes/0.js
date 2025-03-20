

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export const imports = ["_app/immutable/nodes/0.CbAIT_uC.js","_app/immutable/chunks/DQOls_oE.js","_app/immutable/chunks/D_cHL4BB.js"];
export const stylesheets = ["_app/immutable/assets/0.CNKcWJG5.css"];
export const fonts = [];
