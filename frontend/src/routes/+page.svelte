<script>
  import { goto } from '$app/navigation'; // Correct import for navigation
  
  let userTypes = [
    { label: 'Admin', value: 'admin' },
    { label: 'User', value: 'user' },
    { label: 'Guest', value: 'guest' }
  ];

  async function selectUserType(type) {
  try {
    if (type === 'admin') {
      await goto('/admin');
    } else if (type === 'user') {
      await goto('/user');
    } else if (type === 'guest') {
      await goto('/guest');
    }
    console.log(`Selected user type: ${type}`);
  } catch (error) {
    console.error('Navigation failed:', error);
  }
}

</script>

  
  <section class="flex flex-col items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded-2xl shadow-lg w-80">
      <h2 class="text-2xl font-semibold mb-4 text-center">Select User Type</h2>
      <div class="flex flex-col space-y-4">
        {#each userTypes as user}
          <button 
            on:click={() => selectUserType(user.value)}
            class="bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors">
            {user.label}
          </button>
        {/each}
      </div>
    </div>
  </section>
  
  <style>
    section {
      background-color: #f8fafc;
    }
  </style>
  
  