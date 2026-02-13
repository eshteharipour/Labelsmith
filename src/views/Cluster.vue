<!-- frontend/src/App.vue -->
<template>
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8">Image Dataset Matcher</h1>

        <!-- Controls -->
        <div class="flex justify-between mb-8">
            <div class="space-x-4">
                <button :class="btnSaveSettings.class" @click="syncSettings(btnSaveSettings)">
                    {{ btnSaveSettings.text }}
                </button>
                <!-- Image Source Toggle -->
                <div class="flex items-center space-x-2">
                    <span class="text-sm font-medium">Local</span>
                    <button @click="toggleImageSource"
                        class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
                        :class="isServerMode ? 'bg-blue-600' : 'bg-gray-200'">
                        <span class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                            :class="isServerMode ? 'translate-x-6' : 'translate-x-1'"></span>
                    </button>
                    <span class="text-sm font-medium">Server</span>
                </div>
            </div>
        </div>

        <!-- Navigation -->
        <div class="flex justify-center items-center space-x-4 mb-8">
            <button @click="prevPage" :disabled="currentPage === 0"
                class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">
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

        <!-- Clustered Card View -->
        <div class="space-y-8">
            <div v-for="(cluster, cluster_id) in groupedImages" :key="cluster_id" class="cluster-group">
                <h2 v-if="cluster_id !== 'undefined'" class="text-xl font-semibold mb-4">
                    Cluster {{ cluster_id }}
                </h2>
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    <div v-for="image in cluster" :key="image.id"
                        class="bg-white border rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
                        <div class="text-center">
                            <img :src="getImageSrc(image)" :alt="image.name"
                                class="w-32 h-32 object-cover rounded-md mx-auto mb-2" />
                            <div class="text-sm font-semibold truncate">{{ image.name }}</div>
                            <div class="text-xs text-gray-600 truncate">{{ image.path.split('/').slice(-1)[0] }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Navigation bottom -->
        <div class="flex justify-center items-center space-x-4 mt-8">
            <button @click="prevPage" :disabled="currentPage === 0"
                class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">
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
    name: 'Image Cluster Viewer',
    components: {
        CustomInput
    },

    data() {
        return {
            currentPage: 0,
            pageNum: 0,
            pageNumError: '',
            isServerMode: false,

            images: [],
            totalPages: 0,

            btnSaveSettings: {
                text: "Save settings",
                class: "bg-green-500 text-white px-4 py-2 rounded",
                origText: "Save settings",
                origClass: "bg-green-500 text-white px-4 py-2 rounded",
            },
        }
    },

    computed: {
        groupedImages() {
            // Group images by cluster_id, with 'undefined' as a fallback for unclustered items
            return this.images.reduce((acc, image) => {
                const cluster_id = image.cluster_id != undefined ? image.cluster_id : 'undefined'
                if (!acc[cluster_id]) acc[cluster_id] = []
                acc[cluster_id].push(image)
                return acc
            }, {})
        }
    },

    methods: {
        async loadImages() {
            this.images = [] // Fixes duplicate products on changing page 
            // TODO: but spamming next/prev page makes vue not update anymore
            try {
                const response = await axios.get(`/api/cluster/images?page=${this.currentPage}`)

                this.images = response.data.images
                this.totalPages = response.data.total_pages
            } catch (error) {
                console.error('Error loading images:', error)
            }
        },

        // getImageSrc(image) {
        //     if (this.isServerMode && image.path_id) {
        //         // Use the path_id which is a web address for server mode
        //         return image.path_id
        //     } else {
        //         // Use the local file path for local mode
        //         return `/api/cluster/images/file?image_path=${encodeURIComponent(image.path)}`
        //     }
        // },

        getImageSrc(image) {
            if (this.isServerMode && image.path_id) {
                // Use the proxy endpoint for external images
                return `/api/cluster/proxy-image?url=${encodeURIComponent(image.path_id)}`;
            } else {
                // Local images remain the same
                return `/api/cluster/images/file?image_path=${encodeURIComponent(image.path)}`;
            }
        },

        toggleImageSource() {
            this.isServerMode = !this.isServerMode
            this.loadImages() // Reload images with the new source mode
        },

        async loadSettings() {
            const response = await axios.get(`/api/load_settings`)
            if (response.data.settings.lastPage !== undefined) this.currentPage = response.data.settings.lastPage
            if (response.data.settings.isServerMode !== undefined) this.isServerMode = response.data.settings.isServerMode
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
            const apiUrl = '/api/cluster/save_settings'
            const data = {
                lastPage: this.currentPage,
                isServerMode: this.isServerMode
            }
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
}
</script>

<style>
button {
    transition: background-color 0.3s ease-in-out;
}
</style>

<style scoped>
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

.cluster-group {
    background-color: #f9fafb;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
