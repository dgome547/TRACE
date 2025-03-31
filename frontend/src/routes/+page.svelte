<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  onMount(() => {
    goto('/crawler/launch');
    // goto('/ml/launch');
  });
</script>

<p>Redirecting...</p>