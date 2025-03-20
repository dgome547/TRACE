

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export const imports = ["_app/immutable/nodes/0.B3o2sADt.js","_app/immutable/chunks/CRNJLpyG.js","_app/immutable/chunks/MYgP6b1-.js"];
export const stylesheets = ["_app/immutable/assets/0.CNKcWJG5.css"];
export const fonts = [];
