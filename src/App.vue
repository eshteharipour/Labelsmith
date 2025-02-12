<!-- frontend/src/App.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Image Dataset Cleaner</h1>

    <!-- Controls -->
    <div class="flex justify-between mb-8">
      <div class="space-x-4">
        <button :class="buttonClass" @click="saveData">
          {{ buttonText }}
        </button>
        <button @click="imageMode = true" :class="{ 'bg-red-500': imageMode === true }" class="px-4 py-2 rounded">
          Image Mode
        </button>
        <button @click="imageMode = false" :class="{ 'bg-red-500': imageMode === false }" class="px-4 py-2 rounded">
          Text Mode
        </button>
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
      <div v-for="image in images" :key="image.path" class="border rounded p-4">
        <div v-if="imageMode === true">
          <img :src="`/api/images/file/${image.id}`" :alt="image.name" class="w-full h-48 object-cover mb-2" />
        </div>
        <div class="truncate" :title="image.name">{{ image.name }}</div>
        <div v-if="imageMode === true">
          <div v-if="image.source" class="text-sm text-gray-600">Source: {{ image.source }}</div>
          <div v-if="image.site_id" class="text-sm text-gray-600">Site ID: {{ image.site_id }}</div>
          <div v-if="image.cluster_id" class="text-sm text-gray-600">Cluster ID: {{ image.cluster_id }}</div>
          <div v-if="image.basename" class="text-sm text-gray-600">Bn: {{ image.basename }}</div>
          <div v-if="image.dbscan" class="text-sm text-gray-600">dbscan: {{ image.dbscan }}</div>
        </div>
        <div class="dropdown">
          <select v-model="images2selected[image.basename]"
            @change="changeStatus(image, images2selected[image.basename])" class="dropdown-select" :class="{
              'dropdown-select': true,
              'default-select': images2selected[image.basename] === statuses[0],
              'selected-select': images2selected[image.basename] !== statuses[0]
            }">
            <option v-for="item in statuses" :key="item" :value="item">
              <!-- :class="{ 'base-option': item === statuses[0], 'selected-option': item !== statuses[0] }"> -->
              <!-- :selected="images2selected[image.basename] === item"> -->
              {{ item }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Row View -->
    <div v-else class="space-y-4">
      <div v-for="image in images" :key="image.path" class="flex items-center border rounded p-4">
        <div v-if="imageMode === true">
          <img :src="`/api/images/file/${image.id}`" :alt="image.name" class="w-48 h-32 object-cover" />
        </div>
        <div class="flex-1 px-4">
          <div class="font-bold">{{ image.name }}</div>
          <div v-if="imageMode === true">
            <div v-if="image.source" class="text-sm text-gray-600">Source: {{ image.source }}</div>
            <div v-if="image.site_id" class="text-sm text-gray-600">Site ID: {{ image.site_id }}</div>
            <div v-if="image.cluster_id" class="text-sm text-gray-600">Cluster ID: {{ image.cluster_id }}</div>
            <div v-if="image.basename" class="text-sm text-gray-600">Bn: {{ image.basename }}</div>
            <div v-if="image.dbscan" class="text-sm text-gray-600">dbscan: {{ image.dbscan }}</div>
          </div>
          <select v-model="images2selected[image.basename]"
            @change="changeStatus(image, images2selected[image.basename])" class="dropdown-select" :class="{
              'dropdown-select': true,
              'default-select': images2selected[image.basename] === statuses[0],
              'selected-select': images2selected[image.basename] !== statuses[0]
            }">
            <option v-for="item in statuses" :key="item" :value="item">
              {{ item }}
            </option>
          </select>
        </div>
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
import { version } from 'vue';
console.log(`Vue version: ${version}`);

export default {
  data() {
    return {
      imageMode: true,
      images: [],
      statuses: [],
      selectedImages: {},
      images2selected: {},
      currentPage: 0,
      totalPages: 0,
      viewMode: 'grid',
      showSelected: false,
      buttonText: "Save",
      buttonClass: "bg-green-500 text-white px-4 py-2 rounded",
      originalText: "Save",
      originalClass: "bg-green-500 text-white px-4 py-2 rounded",
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
      this.images = [] // Fixes duplicate products on changing page 
      // TODO: but spamming next/prev page makes vue not update anymore
      try {
        const response = await axios.get(`/api/images?page=${this.currentPage}`)
        this.selectedImages = response.data.selected_images
        this.images2selected = this.isSelected(response.data.images, this.selectedImages)

        this.images = response.data.images
        this.totalPages = response.data.total_pages
        const statuses = [""]
        statuses.push.apply(statuses, response.data.statuses)
        this.statuses = statuses
      } catch (error) {
        console.error('Error loading images:', error)
      }
    },

    async changeStatus(image, status) {
      try {
        await axios.post('/api/images/update', {
          basename: image.basename,
          status
        })
        if (status) {
          this.selectedImages[image.basename] = status
        } else if (image.basename in this.selectedImages) {
          delete this.selectedImages[image.basename]
        }
      } catch (error) {
        console.error('Error updating image:', error)
      }
    },

    isSelected(images, selectedImages) {
      return images.reduce((acc, img) => {
        acc[img.basename] = selectedImages[img.basename] ?? "";
        return acc;
      }, {})
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
    },

    async saveData() {
      this.buttonText = "Saving...";
      this.buttonClass = "bg-yellow-500 text-white px-4 py-2 rounded";

      try {
        const response = await axios.post('/api/save_page', {
          page: this.currentPage
        })

        if (response.data.success) {
          this.buttonText = "Saved!";
          this.buttonClass = "bg-green-500 text-white px-4 py-2 rounded";

          setTimeout(() => {
            this.buttonText = this.originalText;
            this.buttonClass = this.originalClass;
          }, 2000);
        } else {
          this.buttonText = "Failed!";
          this.buttonClass = "bg-red-500 text-white px-4 py-2 rounded";

          setTimeout(() => {
            this.buttonText = this.originalText;
            this.buttonClass = this.originalClass;
          }, 2000);
        }
      } catch (error) {
        this.buttonText = "Error!";
        this.buttonClass = "bg-red-500 text-white px-4 py-2 rounded";

        setTimeout(() => {
          this.buttonText = this.originalText;
          this.buttonClass = this.originalClass;
        }, 2000);
      }
    },
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
          this.images2selected = this.isSelected(response.data.images, this.selectedImages)
          this.images = response.data.images
        } else {
          await this.loadImages()
        }
      }
    },
    // images2selected: {
    //   deep: true,
    //   handler(newVal) {
    //     console.log('images2selected changed:', newVal);
    //   }
    // },
  }
}
</script>

<style>
button {
  transition: background-color 0.3s ease-in-out;
}
</style>

<style scoped>
.dropdown {
  margin: 1rem 0;
}

.dropdown-select {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 200px;
}

.default-select {
  background-color: white;
}

.selected-select {
  background-color: #4CAF50;
  color: white;
}
</style>
