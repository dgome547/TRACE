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
		client: {start:"_app/immutable/entry/start.CXa8XuJ9.js",app:"_app/immutable/entry/app.Sk11TNPK.js",imports:["_app/immutable/entry/start.CXa8XuJ9.js","_app/immutable/chunks/Cuu9QU7k.js","_app/immutable/chunks/D_cHL4BB.js","_app/immutable/chunks/D_7aRlFW.js","_app/immutable/entry/app.Sk11TNPK.js","_app/immutable/chunks/D_cHL4BB.js","_app/immutable/chunks/DYTQeLS7.js","_app/immutable/chunks/DQOls_oE.js","_app/immutable/chunks/D_7aRlFW.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
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
				id: "/admin",
				pattern: /^\/admin\/?$/,
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
