<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  onMount(() => {
    goto('/ml/launch');
  });
</script>

<p>Redirecting...</p>