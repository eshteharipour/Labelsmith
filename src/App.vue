<!-- frontend/src/App.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Image Dataset Cleaner</h1>

    <!-- Controls -->
    <div class="flex justify-between mb-8">
      <div class="space-x-4">
        <button :class="saveButtonClass" @click="saveData">
          {{ saveButtonText }}
        </button>
        <CustomInput v-model="clusterCol" label="Cluster Column" placeholder="cluster_id" id="clustercol-input"
          :error="clusterColError" @enter="handleClusterColSubmit(clusterCol)" />
        <!-- <button @click="handleClusterColSubmit(clusterCol)" class="submit-button"> -->
        <button @click="taskMode = 'classify'" :class="{ 'bg-orange-500': taskMode === 'classify' }"
          class="px-4 py-2 rounded">
          Classify Mode
        </button>
        <button @click="taskMode = 'cluster'" :class="{ 'bg-orange-500': taskMode === 'cluster' }"
          class="px-4 py-2 rounded">
          Cluster Mode
        </button>
        <button @click="groupMode = false" :class="{ 'bg-purple-500': groupMode === false }" class="px-4 py-2 rounded">
          Normal Mode
        </button>
        <button @click="groupMode = true" :class="{ 'bg-purple-500': groupMode === true }" class="px-4 py-2 rounded">
          Group Mode
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
        <button :class="syncButtonClass" @click="syncFlush">
          {{ syncButtonText }}
        </button>
      </div>
      <div v-if="taskMode === 'classify'">
        <button @click="showSelected = !showSelected" class="px-4 py-2 bg-green-500 rounded">
          {{ showSelected ? 'Back to Main View' : 'View Selected Images' }}
        </button>
      </div>
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
    </div>

    <!-- Grid View -->
    <div v-if="viewMode === 'grid'" class="grid grid-cols-4 gap-4">
      <div v-for="(image, index) in images" :key="image.id" class="border rounded p-4">
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
        <div v-if="imageMode === true && taskMode === 'classify'">
          <div class="dropdown">
            <select v-model="images2selected[image.basename]"
              @change="changeStatus(image, images2selected[image.basename])" class="dropdown-select" :class="{
                'dropdown-select': true,
                'default-select': images2selected[image.basename] === statuses[0],
                'selected-select-1': images2selected[image.basename] === statuses[1],
                'selected-select-2': images2selected[image.basename] === statuses[2],
                'selected-select-3': images2selected[image.basename] === statuses[3],
                'selected-select-4': images2selected[image.basename] === statuses[4]
              }">
              <option v-for="item in statuses" :key="item" :value="item">
                <!-- :class="{ 'base-option': item === statuses[0], 'selected-option': item !== statuses[0] }"> -->
                <!-- :selected="images2selected[image.basename] === item"> -->
                {{ item }}
              </option>
            </select>
          </div>
        </div>
        <div v-if="taskMode === 'cluster'">
          <CustomInput v-model="name2Cluster[image.name]" label="Cluster Column" placeholder="cluster_id"
            :id="`clustercol-input-${index}`" :error="clusterColError" />
          <button @click="handleFixCluster(image, name2Cluster[image.name])" class="submit-button">
            Submit
          </button>
        </div>
      </div>
    </div>

    <!-- Row View -->
    <div v-else class="space-y-4">
      <div v-for="(image, index) in images" :key="image.id" class="flex items-center border rounded p-4">
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
          <div v-if="imageMode === true && taskMode === 'classify'">
            <div class="dropdown">
              <select v-model="images2selected[image.basename]"
                @change="changeStatus(image, images2selected[image.basename])" class="dropdown-select" :class="{
                  'dropdown-select': true,
                  'default-select': images2selected[image.basename] === statuses[0],
                  'selected-select-1': images2selected[image.basename] === statuses[1],
                  'selected-select-2': images2selected[image.basename] === statuses[2],
                  'selected-select-3': images2selected[image.basename] === statuses[3],
                  'selected-select-4': images2selected[image.basename] === statuses[4]
                }">
                <option v-for="item in statuses" :key="item" :value="item">
                  {{ item }}
                </option>
              </select>
            </div>
          </div>
          <div v-if="taskMode === 'cluster'">
            <CustomInput v-model="name2Cluster[image.name]" label="Cluster Column" placeholder="cluster_id"
              :id="`clustercol-input-${index}`" :error="clusterColError" />
            <button @click="handleFixCluster(image, name2Cluster[image.name])" class="submit-button">
              Submit
            </button>
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
import CustomInput from './components/CustomInput.vue';
console.log(`Vue version: ${version}`);

export default {
  name: 'Image dataset cleaner',
  components: {
    CustomInput
  },

  data() {
    return {
      viewMode: 'grid',
      taskMode: "classify",
      groupMode: false,
      imageMode: true,
      showSelected: false,
      currentPage: 0,

      clusterCol: "cluster_id",
      clusterColError: '',
      pageNum: 0,
      pageNumError: '',

      images: [],
      statuses: [],
      selectedImages: {},
      images2selected: {},
      name2Cluster: {},
      totalPages: 0,

      saveButtonText: "Save",
      saveButtonClass: "bg-green-100 text-white px-4 py-2 rounded",
      saveOriginalText: "Save",
      saveOriginalClass: "bg-green-500 text-white px-4 py-2 rounded",

      syncButtonText: "Sync classifications",
      syncButtonClass: "bg-green-100 text-white px-4 py-2 rounded",
      syncOriginalText: "Sync classifications",
      syncOriginalClass: "bg-green-500 text-white px-4 py-2 rounded",
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

        if (response.data.settings.taskMode) this.taskMode = response.data.settings.taskMode
        if (response.data.settings.groupMode) this.groupMode = response.data.settings.groupMode
        if (response.data.settings.clusterCol) this.clusterCol = response.data.settings.clusterCol
        if (response.data.settings.imageMode) this.imageMode = response.data.settings.imageMode
        if (response.data.settings.viewMode) this.viewMode = response.data.settings.viewMode
      } catch (error) {
        console.error('Error loading images:', error)
      }
    },

    async loadGroups() {
      this.images = []
      try {
        const response = await axios.get(`/api/groups?cluster_col=${this.clusterCol}&page=${this.currentPage}`)
        this.name2Cluster = this.isFixed(response.data.images, response.data.fixed_groups)
        this.images = response.data.images
        this.totalPages = response.data.total_pages

        if (response.data.settings.taskMode) this.taskMode = response.data.settings.taskMode
        if (response.data.settings.groupMode) this.groupMode = response.data.settings.groupMode
        if (response.data.settings.clusterCol) this.clusterCol = response.data.settings.clusterCol
        if (response.data.settings.imageMode) this.imageMode = response.data.settings.imageMode
        if (response.data.settings.viewMode) this.viewMode = response.data.settings.viewMode
      } catch (error) {
        console.error('Error loading images:', error)
      }
    },

    async handleClusterColSubmit(clusterCol) {
      if (this.groupMode == true)
        await this.loadGroups()
    },

    async handlePageNumSubmit(pageNum) {
      this.currentPage = pageNum
      if (this.groupMode == false)
        await this.loadImages()
      else
        await this.loadGroups()
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

    async handleFixCluster(image, cluster_id) {
      try {
        await axios.post('/api/images/update_cluster', {
          name: image.name,
          cluster_id
        })
        if (!isNaN(Number(cluster_id))) {
          this.name2Cluster[image.name] = cluster_id
        } else if (image.name in this.name2Cluster) {
          delete this.name2Cluster[image.name]
        }
      } catch (error) {
        console.error('Error updating cluster:', error)
      }
    },

    isSelected(images, selectedImages) {
      return images.reduce((acc, img) => {
        acc[img.basename] = selectedImages[img.basename] ?? "";
        return acc;
      }, {})
    },

    isFixed(images, selectedCluster) {
      return images.reduce((acc, img) => {
        acc[img.name] = selectedCluster[img.name] ?? "";
        return acc;
      }, {})
    },


    async prevPage() {
      if (this.currentPage > 0) {
        this.currentPage--
        if (this.groupMode == false)
          await this.loadImages()
        else
          await this.loadGroups()
      }
    },

    async nextPage() {
      if (this.currentPage < this.totalPages - 1) {
        this.currentPage++
        if (this.groupMode == false)
          await this.loadImages()
        else
          await this.loadGroups()
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
      this.saveButtonText = "Saving...";
      this.saveButtonClass = "bg-yellow-500 text-white px-4 py-2 rounded";

      try {
        const response = await axios.post('/api/save_page', {
          page: this.currentPage,
          taskMode: this.taskMode,
          groupMode: this.groupMode,
          clusterCol: this.clusterCol,
          imageMode: this.imageMode,
          viewMode: this.viewMode,
        })

        if (response.data.success) {
          this.saveButtonText = "Saved!";
          this.saveButtonClass = "bg-green-500 text-white px-4 py-2 rounded";

          setTimeout(() => {
            this.saveButtonText = this.saveOriginalText;
            this.saveButtonClass = this.saveOriginalClass;
          }, 2000);
        } else {
          this.saveButtonText = "Failed!";
          this.saveButtonClass = "bg-red-500 text-white px-4 py-2 rounded";

          setTimeout(() => {
            this.saveButtonText = this.saveOriginalText;
            this.saveButtonClass = this.saveOriginalClass;
          }, 2000);
        }
      } catch (error) {
        this.saveButtonText = "Error!";
        this.saveButtonClass = "bg-red-500 text-white px-4 py-2 rounded";

        setTimeout(() => {
          this.saveButtonText = this.saveOriginalText;
          this.saveButtonClass = this.saveOriginalClass;
        }, 2000);
      }
    },
    async syncFlush() {
      this.syncButtonText = "Syncing...";
      this.syncButtonClass = "bg-yellow-500 text-white px-4 py-2 rounded";

      try {
        const response = await axios.post('/api/sync')

        if (response.data.success) {
          this.syncButtonText = "Synced!";
          this.syncButtonClass = "bg-green-500 text-white px-4 py-2 rounded";

          setTimeout(() => {
            this.syncButtonText = this.syncOriginalText;
            this.syncButtonClass = this.syncOriginalClass;
          }, 2000);
        } else {
          this.syncButtonText = "Failed!";
          this.syncButtonClass = "bg-red-500 text-white px-4 py-2 rounded";

          setTimeout(() => {
            this.syncButtonText = this.syncOriginalText;
            this.syncButtonClass = this.syncOriginalClass;
          }, 2000);
        }
      } catch (error) {
        this.syncButtonText = "Error!";
        this.syncButtonClass = "bg-red-500 text-white px-4 py-2 rounded";

        setTimeout(() => {
          this.syncButtonText = this.syncOriginalText;
          this.syncButtonClass = this.syncOriginalClass;
        }, 2000);
      }
    }
  },

  async mounted() {
    await this.lastPage()
    if (this.groupMode == false)
      await this.loadImages()
    else
      await this.loadGroups()
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
    groupMode: {
      async handler(val) {
        if (val) {
          await this.loadGroups()
        } else {
          await this.loadImages()
        }
      }
    },
    // name2Cluster: {
    //   deep: true,
    //   handler(newVal) {
    //     console.log('name2Cluster changed:', newVal);
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

.selected-select-1 {
  background-color: #FF5733;
  /* Red-Orange */
  color: white;
}

.selected-select-2 {
  background-color: #33A1FF;
  /* Sky Blue */
  color: white;
}

.selected-select-3 {
  background-color: #33FF57;
  /* Bright Green */
  color: white;
}

.selected-select-4 {
  background-color: #FFD700;
  /* Gold */
  color: black;
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
</style>
