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
		client: {start:"_app/immutable/entry/start.BhDyj8iG.js",app:"_app/immutable/entry/app.VwRDPsJX.js",imports:["_app/immutable/entry/start.BhDyj8iG.js","_app/immutable/chunks/DRr5nLvw.js","_app/immutable/chunks/MYgP6b1-.js","_app/immutable/chunks/SLTg8hsI.js","_app/immutable/entry/app.VwRDPsJX.js","_app/immutable/chunks/MYgP6b1-.js","_app/immutable/chunks/DBP_O3ab.js","_app/immutable/chunks/CRNJLpyG.js","_app/immutable/chunks/BHOcLJ1l.js","_app/immutable/chunks/BRy_4ppC.js","_app/immutable/chunks/SLTg8hsI.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js')),
			__memo(() => import('./nodes/5.js'))
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
				id: "/MLalgorithm",
				pattern: /^\/MLalgorithm\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 4 },
				endpoint: null
			},
			{
				id: "/admin",
				pattern: /^\/admin\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/webcrawler",
				pattern: /^\/webcrawler\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 5 },
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
