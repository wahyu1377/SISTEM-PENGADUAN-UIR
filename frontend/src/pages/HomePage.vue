<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-primary-600">Sistem Pengaduan UIR</h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/login" class="btn btn-secondary">Masuk</router-link>
            <router-link to="/register" class="btn btn-primary">Daftar</router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
      <div class="text-center">
        <h2 class="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
          Sampaikan Pengaduan<br>
          <span class="text-primary-600">Dengan Mudah</span>
        </h2>
        <p class="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
          Sistem Pengaduan Mahasiswa Universitas Islam Riau Berbasis Artificial Intelligence.
          Pengaduan Anda akan dianalisis secara otomatis dan diteruskan ke unit yang tepat.
        </p>
        <div class="mt-10 flex justify-center gap-4">
          <router-link to="/register" class="btn btn-primary text-lg px-8 py-3">
            Mulai Pengaduan
          </router-link>
          <router-link to="/login" class="btn btn-secondary text-lg px-8 py-3">
            Masuk
          </router-link>
        </div>
      </div>
    </div>

    <!-- Features -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="card p-6 text-center">
          <div class="w-16 h-16 mx-auto bg-primary-100 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-semibold text-gray-900">Analisis Otomatis</h3>
          <p class="mt-2 text-gray-600">AI akan menganalisis pengaduan Anda dan menentukan kategori serta prioritas.</p>
        </div>

        <div class="card p-6 text-center">
          <div class="w-16 h-16 mx-auto bg-secondary-100 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-secondary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-semibold text-gray-900">Proses Cepat</h3>
          <p class="mt-2 text-gray-600">Pengaduan langsung diteruskan ke unit terkait tanpa proses yang berbelit.</p>
        </div>

        <div class="card p-6 text-center">
          <div class="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-semibold text-gray-900">Transparan</h3>
          <p class="mt-2 text-gray-600">Pantau status pengaduan Anda kapan saja dengan mudah.</p>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <p class="text-gray-400">&copy; 2026 Universitas Islam Riau. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// Home page component
</script>
