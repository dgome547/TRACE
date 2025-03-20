export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.png"]),
	mimeTypes: {".png":"image/png"},
	_: {
		client: {start:"_app/immutable/entry/start.DTBPbQKA.js",app:"_app/immutable/entry/app.BiKMnwdn.js",imports:["_app/immutable/entry/start.DTBPbQKA.js","_app/immutable/chunks/BNWC5ssn.js","_app/immutable/chunks/Bh_pQRl2.js","_app/immutable/chunks/CTOIgGWE.js","_app/immutable/entry/app.BiKMnwdn.js","_app/immutable/chunks/Bh_pQRl2.js","_app/immutable/chunks/DYPMIxbg.js","_app/immutable/chunks/C5CMfB9T.js","_app/immutable/chunks/CzQvxr8r.js","_app/immutable/chunks/CTOIgGWE.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js'))
		],
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			},
			{
				id: "/homeScreen",
				pattern: /^\/homeScreen\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
