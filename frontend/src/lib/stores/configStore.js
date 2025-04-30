import { writable } from 'svelte/store';

// Create a writable store to hold configuration data
export const configStore = writable(null);