<template>
  <div class="shell">
    <aside class="sidebar">
      <div>
        <p class="eyebrow">FinFlow</p>
        <h1>Investor signal cockpit</h1>
      </div>
      <nav class="nav">
        <RouterLink to="/">Feed</RouterLink>
        <RouterLink to="/creators">Creators</RouterLink>
        <RouterLink to="/settings">Settings</RouterLink>
        <RouterLink to="/crawl-logs">Crawl Logs</RouterLink>
      </nav>
    </aside>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>
