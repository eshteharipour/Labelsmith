<!-- frontend/src/App.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Image Dataset Cleaner</h1>

    <!-- Controls -->
    <div class="flex justify-between mb-8">
      <div class="space-x-4">
        <button @click="viewMode = 'grid'" :class="{ 'bg-blue-500': viewMode === 'grid' }" class="px-4 py-2 rounded">
          Grid View
        </button>
        <button @click="viewMode = 'row'" :class="{ 'bg-blue-500': viewMode === 'row' }" class="px-4 py-2 rounded">
          Row View
        </button>
      </div>
      <button @click="showSelected = !showSelected" class="px-4 py-2 bg-green-500 rounded">
        {{ showSelected ? 'Back to Main View' : 'View Selected Images' }}
      </button>
    </div>

    <!-- Navigation -->
    <div v-if="!showSelected" class="flex justify-center items-center space-x-4 mb-8">
      <button @click="prevPage" :disabled="currentPage === 0" class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">
        Previous
      </button>
      <span>Page {{ currentPage + 1 }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage >= totalPages - 1"
        class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">
        Next
      </button>
    </div>

    <!-- Grid View -->
    <div v-if="viewMode === 'grid'" class="grid grid-cols-4 gap-4">
      <div v-for="image in displayImages" :key="image.path" class="border rounded p-4">
        <img :src="`/api/images/file/${image.id}`" :alt="image.name" class="w-full h-48 object-cover mb-2" />
        <div class="truncate" :title="image.name">{{ image.name }}</div>
        <div v-if="image.source" class="text-sm text-gray-600">Source: {{ image.source }}</div>
        <div v-if="image.site_id" class="text-sm text-gray-600">Site ID: {{ image.site_id }}</div>
        <button @click="toggleSelect(image)" :class="{ 'bg-green-500': isSelected(image.basename) }"
          class="mt-2 w-full px-4 py-2 rounded">
          {{ isSelected(image.basename) ? 'Deselect' : 'Select' }}
        </button>
      </div>
    </div>

    <!-- Row View -->
    <div v-else class="space-y-4">
      <div v-for="image in displayImages" :key="image.path" class="flex items-center border rounded p-4">
        <img :src="`/api/images/file/${image.id}`" :alt="image.name" class="w-48 h-32 object-cover" />
        <div class="flex-1 px-4">
          <div class="font-bold">{{ image.name }}</div>
          <div v-if="image.source" class="text-sm text-gray-600">Source: {{ image.source }}</div>
          <div v-if="image.site_id" class="text-sm text-gray-600">Site ID: {{ image.site_id }}</div>
        </div>
        <button @click="toggleSelect(image)" :class="{ 'bg-green-500': isSelected(image.basename) }"
          class="px-4 py-2 rounded">
          {{ isSelected(image.basename) ? 'Deselect' : 'Select' }}
        </button>
      </div>
    </div>

    <!-- Navigation bottom -->
    <div v-if="!showSelected" class="flex justify-center items-center space-x-4 mb-8">
      <button @click="prevPage" :disabled="currentPage === 0" class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">
        Previous
      </button>
      <span>Page {{ currentPage + 1 }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage >= totalPages - 1"
        class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">
        Next
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      images: [],
      selectedImages: [],
      currentPage: 0,
      totalPages: 0,
      viewMode: 'grid',
      showSelected: false
    }
  },

  computed: {
    displayImages() {
      return this.showSelected ?
      // this.images.filter(img => this.selectedImages.includes(img.basename)) :
        this.images :
        this.images
    }
  },

  methods: {
    async loadImages() {
      try {
        const response = await axios.get(`/api/images?page=${this.currentPage}`)
        this.images = response.data.images
        this.totalPages = response.data.total_pages
        this.selectedImages = response.data.selected_images
      } catch (error) {
        console.error('Error loading images:', error)
      }
    },

    async toggleSelect(image) {
      try {
        const selected = !this.isSelected(image.basename)
        await axios.post('/api/images/update', {
          basename: image.basename,
          selected
        })
        if (selected) {
          this.selectedImages.push(image.basename)
        } else {
          this.selectedImages = this.selectedImages.filter(bn => bn !== image.basename)
        }
      } catch (error) {
        console.error('Error updating image:', error)
      }
    },

    isSelected(str) {
      return this.selectedImages.includes(str)
    },

    async prevPage() {
      if (this.currentPage > 0) {
        this.currentPage--
        await this.loadImages()
      }
    },

    async nextPage() {
      if (this.currentPage < this.totalPages - 1) {
        this.currentPage++
        await this.loadImages()
      }
    },

    async lastPage() {
      try {
        const response = await axios.get(`/api/last`)
        this.currentPage = response.data.last_page
      } catch (error) {
        console.error('Error loading last page:', error)
      }
    }
  },

  async mounted() {
    await this.lastPage()
    await this.loadImages()
  },

  watch: {
    showSelected: {
      async handler(val) {
        if (val) {
          const response = await axios.get('/api/images/selected')
          this.images = response.data.images
        } else {
          await this.loadImages()
        }
      }
    }
  }
}
</script>