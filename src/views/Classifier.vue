<!-- frontend/src/App.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Image Dataset Cleaner</h1>

    <!-- Controls -->
    <div class="flex justify-between mb-8">
      <div class="space-x-4">
        <button :class="btnSaveSettings.class" @click="syncSettings(btnSaveSettings)">
          {{ btnSaveSettings.text }}
        </button>
        <button :class="btnSyncClfs.class" @click="syncClassifications(btnSyncClfs)">
          {{ btnSyncClfs.text }}
        </button>
        <div class="button-separator">
          <button @click="pageMode = 'paginate'" :class="{ 'bg-purple-500': pageMode === 'paginate' }"
            class="px-4 py-2 rounded">
            Normal Mode
          </button>
          <button @click="pageMode = 'groups'" :class="{ 'bg-purple-500': pageMode === 'groups' }"
            class="px-4 py-2 rounded">
            Group Mode
          </button>
        </div>
        <div class="button-separator">
          <button @click="imageMode = true" :class="{ 'bg-red-500': imageMode === true }" class="px-4 py-2 rounded">
            Image Mode
          </button>
          <button @click="imageMode = false" :class="{ 'bg-red-500': imageMode === false }" class="px-4 py-2 rounded">
            Text Mode
          </button>
        </div>
        <div class="button-separator">
          <button @click="viewMode = 'grid'" :class="{ 'bg-blue-500': viewMode === 'grid' }" class="px-4 py-2 rounded">
            Grid View
          </button>
          <button @click="viewMode = 'row'" :class="{ 'bg-blue-500': viewMode === 'row' }" class="px-4 py-2 rounded">
            Row View
          </button>
        </div>
      </div>
      <button @click="showSelected = !showSelected" class="px-4 py-2 bg-green-500 rounded">
        {{ showSelected ? 'Back to Main View' : 'View Classifications' }}
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
      <CustomInput v-model="pageNum" label="Page number" placeholder="0" id="pagenum-input" :error="pageNumError"
        @enter="handlePageNumSubmit(pageNum)" />
      <!-- <button @click="handlePageNumSubmit(pageNum)" class="submit-button"> -->
    </div>

    <!-- Grid View -->
    <div v-if="viewMode === 'grid'" class="grid grid-cols-4 gap-4">
      <div v-for="(image, index) in images" :key="image.id" class="border rounded p-4">
        <div v-if="imageMode === true">
          <img :src="`/api/images/file?image_path=${encodeURIComponent(image.path)}`" :alt="image.name"
            class="w-full h-48 object-cover mb-2" />
        </div>
        <div class="truncate" :title="image.name">{{ image.name }}</div>
        <div v-if="imageMode === true">
          <div v-if="image.source" class="text-sm text-gray-600">Source: {{ image.source }}</div>
          <div v-if="image.site_id" class="text-sm text-gray-600">Site ID: {{ image.site_id }}</div>
          <div v-if="image.cluster_id" class="text-sm text-gray-600">Cluster ID: {{ image.cluster_id }}</div>
          <div v-if="image.split" class="text-sm text-gray-600">Split: {{ image.split }}</div>
          <div v-if="image.basename" class="text-sm truncate w-full text-gray-600">Bn: {{ image.basename }}</div>
          <div v-if="image.path" class="text-sm truncate w-full text-gray-600">Path: {{ image.path }}</div>
          <div v-if="image.dbscan" class="text-sm text-gray-600">dbscan: {{ image.dbscan }}</div>
          <div v-if="image.bn_freq" class="text-sm text-gray-600">bn freq: {{ image.bn_freq }}</div>
        </div>
        <div v-if="imageMode === true">
          <div class="dropdown">
            <select v-model="basename2status[image.basename]"
              @change="changeStatus(image, basename2status[image.basename])" class="dropdown-select" :class="{
                'dropdown-select': true,
                'default-select': basename2status[image.basename] === statuses[0],
                'selected-select-1': basename2status[image.basename] === statuses[1],
                'selected-select-2': basename2status[image.basename] === statuses[2],
                'selected-select-3': basename2status[image.basename] === statuses[3],
                'selected-select-4': basename2status[image.basename] === statuses[4],
                'selected-select-5': basename2status[image.basename] === statuses[5],
                'selected-select-6': basename2status[image.basename] === statuses[6],
                'selected-select-7': basename2status[image.basename] === statuses[7],
                'selected-select-8': basename2status[image.basename] === statuses[8],
                'selected-select-9': basename2status[image.basename] === statuses[9],
                'selected-select-10': basename2status[image.basename] === statuses[10]
              }">
              <option v-for="item in statuses" :key="item" :value="item">
                <!-- :class="{ 'base-option': item === statuses[0], 'selected-option': item !== statuses[0] }"> -->
                <!-- :selected="basename2status[image.basename] === item"> -->
                {{ item }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Row View -->
    <div v-else class="space-y-4">
      <div v-for="(image, index) in images" :key="image.id" class="flex items-center border rounded p-4">
        <div v-if="imageMode === true">
          <img :src="`/api/images/file?image_path=${encodeURIComponent(image.path)}`" :alt="image.name"
            class="w-48 h-48 object-cover" />
        </div>
        <div v-if="imageMode === true">
        </div>
        <div class="flex-1 px-4">
          <div class="font-bold">{{ image.name }}</div>
          <div v-if="imageMode === true">
            <div v-if="image.source" class="text-sm text-gray-600">Source: {{ image.source }}</div>
            <div v-if="image.site_id" class="text-sm text-gray-600">Site ID: {{ image.site_id }}</div>
            <div v-if="image.cluster_id" class="text-sm text-gray-600">Cluster ID: {{ image.cluster_id }}</div>
            <div v-if="image.split" class="text-sm text-gray-600">Split: {{ image.split }}</div>
            <div v-if="image.basename" class="text-sm truncate w-full text-gray-600">Bn: {{ image.basename }}</div>
            <div v-if="image.path" class="text-sm truncate w-full text-gray-600">Path: {{ image.path }}</div>
            <div v-if="image.dbscan" class="text-sm text-gray-600">dbscan: {{ image.dbscan }}</div>
            <div v-if="image.bn_freq" class="text-sm text-gray-600">bn freq: {{ image.bn_freq }}</div>
          </div>
          <div v-if="imageMode === true">
            <div class="dropdown">
              <select v-model="basename2status[image.basename]"
                @change="changeStatus(image, basename2status[image.basename])" class="dropdown-select" :class="{
                  'dropdown-select': true,
                  'default-select': basename2status[image.basename] === statuses[0],
                  'selected-select-1': basename2status[image.basename] === statuses[1],
                  'selected-select-2': basename2status[image.basename] === statuses[2],
                  'selected-select-3': basename2status[image.basename] === statuses[3],
                  'selected-select-4': basename2status[image.basename] === statuses[4],
                  'selected-select-5': basename2status[image.basename] === statuses[5],
                  'selected-select-6': basename2status[image.basename] === statuses[6],
                  'selected-select-7': basename2status[image.basename] === statuses[7],
                  'selected-select-8': basename2status[image.basename] === statuses[8],
                  'selected-select-9': basename2status[image.basename] === statuses[9],
                  'selected-select-10': basename2status[image.basename] === statuses[10]
                }">
                <option v-for="item in statuses" :key="item" :value="item">
                  {{ item }}
                </option>
              </select>
            </div>
          </div>
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
import CustomInput from '@/components/CustomInput.vue';
console.log(`Vue version: ${version}`);

export default {
  name: 'Image dataset cleaner',
  components: {
    CustomInput
  },

  data() {
    return {
      viewMode: 'grid',
      pageMode: 'paginate',
      imageMode: true,
      showSelected: false,
      currentPage: 0,

      pageNum: 0,
      pageNumError: '',

      images: [],
      statuses: [],
      selectedImages: {},
      basename2status: {},
      totalPages: 0,

      btnSaveSettings: {
        text: "Save",
        class: "bg-green-500 text-white px-4 py-2 rounded",
        origText: "Save",
        origClass: "bg-green-500 text-white px-4 py-2 rounded",
      },

      btnSyncClfs: {
        text: "Sync classifications",
        class: "bg-green-500 text-white px-4 py-2 rounded",
        origText: "Sync classifications",
        origClass: "bg-green-500 text-white px-4 py-2 rounded",
      },
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
        let response
        if (this.pageMode === 'paginate') {
          response = await axios.get(`/api/images?page=${this.currentPage}`)
        }
        else if (this.pageMode === 'groups') {
          response = await axios.get(`/api/groups?page=${this.currentPage}`)
        }

        this.selectedImages = response.data.selected_images
        this.basename2status = this.createBasename2Status(response.data.images, this.selectedImages)
        this.images = response.data.images
        this.totalPages = response.data.total_pages

        // Add disable option:
        const statuses = [""]
        statuses.push.apply(statuses, response.data.statuses)
        this.statuses = statuses
      } catch (error) {
        console.error('Error loading images:', error)
      }
    },

    async loadSettings() {
      const response = await axios.get(`/api/load_settings`)
      if (response.data.settings.lastPage) this.currentPage = response.data.settings.lastPage
      if (response.data.settings.pageMode) this.pageMode = response.data.settings.pageMode
      if (response.data.settings.imageMode) this.imageMode = response.data.settings.imageMode
      if (response.data.settings.viewMode) this.viewMode = response.data.settings.viewMode
    },

    async changeStatus(image, status) {
      try {
        await axios.post('/api/images/update', {
          path: image.path,
          status
        })
        if (status) {
          this.selectedImages[image.path] = status
        } else if (image.path in this.selectedImages) {
          delete this.selectedImages[image.path]
        }
        this.basename2status = this.createBasename2Status(this.images, this.selectedImages)
      } catch (error) {
        console.error('Error updating image:', error)
      }
    },

    createBasename2Status(images, selectedImages) {
      return images.reduce((acc, img) => {
        acc[img.basename] = selectedImages[img.path] ?? "";
        return acc;
      }, {})
    },

    async handlePageNumSubmit(pageNum) {
      this.currentPage = parseInt(pageNum)
      await this.loadImages()
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

    async syncSettings(btnState) {
      const apiUrl = '/api/save_settings'
      const data = {
        lastPage: this.currentPage,
        pageMode: this.pageMode,
        imageMode: this.imageMode,
        viewMode: this.viewMode,
      }
      await this.syncBtnHandler(apiUrl, data, btnState)
    },

    async syncClassifications(btnState) {
      const apiUrl = '/api/sync_classifications'
      const data = {}
      await this.syncBtnHandler(apiUrl, data, btnState)
    },

    async syncBtnHandler(apiUrl, data, btnState) {
      btnState.text = "Saving...";
      btnState.class = "bg-yellow-500 text-white px-4 py-2 rounded";

      try {
        const response = await axios.post(apiUrl, data);

        if (response.data.success) {
          btnState.text = "Saved!";
          btnState.class = "bg-green-500 text-white px-4 py-2 rounded";

          setTimeout(() => {
            btnState.text = btnState.origText;
            btnState.class = btnState.origClass;
          }, 2000);
        } else {
          btnState.text = "Failed!";
          btnState.class = "bg-red-500 text-white px-4 py-2 rounded";

          setTimeout(() => {
            btnState.text = btnState.origText;
            btnState.class = btnState.origClass;
          }, 2000);
        }
      } catch (error) {
        btnState.text = "Error!";
        btnState.class = "bg-red-500 text-white px-4 py-2 rounded";

        setTimeout(() => {
          btnState.text = btnState.origText;
          btnState.class = btnState.origClass;
        }, 2000);
      }
    },
  },

  async mounted() {
    await this.loadSettings()
    await this.loadImages()
  },

  watch: {
    showSelected: {
      async handler(val) {
        if (val) {
          const response = await axios.get('/api/images/selected')
          this.basename2status = this.createBasename2Status(response.data.images, this.selectedImages)
          this.images = response.data.images
        } else {
          await this.loadImages()
        }
      }
    },
    pageMode: {
      async handler(val) {
        if (val) {
          await this.loadImages()
        }
      }
    },
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

.selected-select-1 {
  background-color: #FF5733;
  /* Red-Orange */
  color: white;
}

.selected-select-2 {
  background-color: #33FF57;
  /* Bright Green */
  color: white;
}

.selected-select-3 {
  background-color: #FFD700;
  /* Gold */
  color: black;
}

.selected-select-4 {
  background-color: #33A1FF;
  /* Sky Blue */
  color: white;
}

.selected-select-5 {
  background-color: #8A2BE2;
  /* Blue-Violet */
  color: white;
}

.selected-select-6 {
  background-color: #FF1493;
  /* Deep Pink */
  color: white;
}

.selected-select-7 {
  background-color: #FF4500;
  /* Orange-Red */
  color: white;
}

.selected-select-8 {
  background-color: #1E90FF;
  /* Dodger Blue */
  color: white;
}

.selected-select-9 {
  background-color: #32CD32;
  /* Lime Green */
  color: white;
}

.selected-select-10 {
  background-color: #FF8C00;
  /* Dark Orange */
  color: white;
}

.submit-button {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  height: fit-content;
}

.submit-button:hover {
  background-color: #2563eb;
}

.button-separator {
  display: inline-block;
  border: 2px solid #FF1493;
  border-radius: 2px;
  margin: 0 1px;
  padding: 1px;
}
</style>
