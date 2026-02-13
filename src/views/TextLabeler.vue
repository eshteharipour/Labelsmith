<template>
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8">Text Dataset Labeler (JSONL)</h1>

        <!-- Controls -->
        <div class="flex justify-between mb-8">
            <div class="space-x-4">
                <button :class="btnSaveSettings.class" @click="syncSettings(btnSaveSettings)">
                    {{ btnSaveSettings.text }}
                </button>
                <button :class="btnSyncPage.class" @click="syncPage(btnSyncPage)">
                    {{ btnSyncPage.text }}
                </button>
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
        </div>

        <!-- Grid View -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div v-for="(item, index) in images" :key="index"
                class="border rounded-lg p-4 shadow-sm transition-all duration-300"
                :class="{ 'ring-2 ring-green-500': item._status === 'saved', 'ring-2 ring-red-500': item._status === 'error' }">

                <!-- Image Display -->
                <div class="mb-4 bg-gray-100 rounded flex items-center justify-center h-48 overflow-hidden">
                    <img :src="getImageSrc(item.image)" :alt="item.image" class="h-full w-full object-contain" />
                </div>

                <!-- Filename info -->
                <div class="text-xs text-gray-500 mb-2 truncate" :title="item.image">
                    {{ item.image }}
                </div>

                <!-- Text Input -->
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-bold text-gray-700">Label Text:</label>
                    <input type="text" v-model="item.text" @keydown.enter="saveTextItem(item)"
                        class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Type text and hit Enter..." />
                    <div class="h-4">
                        <span v-if="item._status === 'saved'" class="text-xs text-green-600 font-semibold">Saved!</span>
                        <span v-if="item._status === 'saving'" class="text-xs text-blue-600">Saving...</span>
                        <span v-if="item._status === 'error'" class="text-xs text-red-600">Error saving</span>
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
import CustomInput from '@/components/CustomInput.vue';

export default {
    name: 'TextLabeler',
    components: {
        CustomInput
    },

    data() {
        return {
            currentPage: 0,
            pageNum: 0,
            pageNumError: '',

            // Expected structure: [{image: "path.jpg", text: "label", _status: ""}]
            images: [],
            totalPages: 0,

            btnSaveSettings: {
                text: "Save settings",
                class: "bg-green-500 text-white px-4 py-2 rounded",
                origText: "Save settings",
                origClass: "bg-green-500 text-white px-4 py-2 rounded",
            },

            btnSyncPage: {
                text: "Save Page (Batch)",
                class: "bg-blue-500 text-white px-4 py-2 rounded",
                origText: "Save Page (Batch)",
                origClass: "bg-blue-500 text-white px-4 py-2 rounded",
            },
        }
    },

    methods: {
        async loadImages() {
            this.images = []
            try {
                // Assuming backend serves JSONL lines as a list of objects
                const response = await axios.get(`/api/images?page=${this.currentPage}`)

                // Add internal status tracker for UI feedback
                this.images = response.data.images.map(img => ({
                    ...img,
                    _status: ''
                }))
                this.totalPages = response.data.total_pages
            } catch (error) {
                console.error('Error loading images:', error)
            }
        },

        async loadSettings() {
            try {
                const response = await axios.get(`/api/load_settings`)
                if (response.data.settings.lastPage !== undefined) this.currentPage = response.data.settings.lastPage
            } catch (error) {
                console.error('Error loading settings', error)
            }
        },

        getImageSrc(path) {
            return `/api/images/file?image_path=${encodeURIComponent(path)}`;
        },

        // Save a single item when Enter is pressed
        async saveTextItem(item) {
            item._status = 'saving';
            try {
                const response = await axios.post('/api/images/update', {
                    path: item.image, // Identify by image path
                    text: item.text   // The new text label
                });

                if (response.data.success) {
                    item._status = 'saved';
                    // Clear success message after 2 seconds
                    setTimeout(() => {
                        if (item._status === 'saved') item._status = '';
                    }, 2000);
                } else {
                    item._status = 'error';
                }
            } catch (error) {
                console.error('Error saving text:', error);
                item._status = 'error';
            }
        },

        // Standard Pagination
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

        // Sync functions (Reused logic)
        async syncPage(btnState) {
            const apiUrl = '/api/sync_page' // Or specific endpoint for batch text save
            const data = { page: this.currentPage }
            await this.syncBtnHandler(apiUrl, data, btnState)
        },

        async syncSettings(btnState) {
            const apiUrl = '/api/save_settings'
            const data = { lastPage: this.currentPage }
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
                    throw new Error("API reported failure");
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
