import { writable } from 'svelte/store';

// Create a writable store to hold fuzzer configuration data
export const fuzzerConfigStore = writable(null);