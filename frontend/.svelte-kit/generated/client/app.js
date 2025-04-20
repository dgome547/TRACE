export { matchers } from './matchers.js';

export const nodes = [
	() => import('./nodes/0'),
	() => import('./nodes/1'),
	() => import('./nodes/2'),
	() => import('./nodes/3'),
	() => import('./nodes/4'),
	() => import('./nodes/5'),
	() => import('./nodes/6'),
	() => import('./nodes/7'),
	() => import('./nodes/8'),
	() => import('./nodes/9'),
	() => import('./nodes/10'),
	() => import('./nodes/11'),
	() => import('./nodes/12'),
	() => import('./nodes/13'),
	() => import('./nodes/14')
];

export const server_loads = [];

export const dictionary = {
		"/": [~2],
		"/bruteForce": [3],
		"/bruteForce/results": [4],
		"/bruteForce/scan": [5],
		"/crawler": [6],
		"/crawler/execution": [7],
		"/crawler/launch": [8],
		"/crawler/results": [9],
		"/fuzzer": [10],
		"/fuzzer/results": [11],
		"/fuzzer/running": [12],
		"/ml/launch": [13],
		"/ml/results": [14]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
	
	reroute: (() => {}),
	transport: {}
};

export const decoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.decode]));

export const decode = (type, value) => decoders[type](value);

export { default as root } from '../root.js';