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
                <button :class="btnSyncMatches.class" @click="markDfAsComplete(btnSyncMatches)">
                    {{ btnSyncMatches.text }}
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
            <!-- <button @click="handlePageNumSubmit(pageNum)" class="submit-button"> -->
        </div>

        <!-- Row View -->
        <div class="space-y-6">
            <!-- Separator -->
            <template v-for="(image, index) in images" :key="image.id">
                <!-- <div v-if="shouldShowSeparator(index)" class="bg-gray-100 p-3 rounded-lg font-semibold"> -->
                <div v-if="shouldShowSeparator(index)" class="separator">
                </div>
                <!-- Image Card -->
                <div class="flex items-center justify-between border rounded-lg p-6 bg-white shadow-sm">
                    <!-- Source Section -->
                    <div class="flex flex-col items-center w-1/3">
                        <div class="text-lg font-semibold mb-2">{{ image.source_name }}</div>
                        <img :src="`/api/images/file?image_path=${encodeURIComponent(image.source_image)}`"
                            :alt="image.source_image" class="w-48 h-48 object-cover rounded-lg border" />
                    </div>
                    <!-- Matching Controls -->
                    <div class="flex flex-col items-center justify-center w-1/4 space-y-4">
                        <div class="text-sm text-gray-600">Last evaluator</div>
                        <div class="text-sm text-gray-600">{{ image.evaluator }}</div>
                        <div class="text-sm text-gray-600">LLM response</div>
                        <div class="text-sm text-gray-600">{{ image.response }}</div>
                        <div class="text-sm text-gray-600">Match Status</div>
                        <div class="flex space-x-2">
                            <button @click="updateMatching(image, index, true)"
                                class="px-4 py-2 rounded-md font-medium transition-colors" :class="image.matching === true
                                    ? 'bg-green-600 text-white hover:bg-green-700'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'">
                                Match
                            </button>
                            <button @click="updateMatching(image, index, false)"
                                class="px-4 py-2 rounded-md font-medium transition-colors" :class="image.matching === false
                                    ? 'bg-red-600 text-white hover:bg-red-700'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'">
                                No Match
                            </button>
                        </div>
                    </div>
                    <!-- Target Section -->
                    <div class="flex flex-col items-center w-1/3">
                        <div class="text-lg font-semibold mb-2">{{ image.target_name }}</div>
                        <img :src="`/api/images/file?image_path=${encodeURIComponent(image.target_image)}`"
                            :alt="image.target_image" class="w-48 h-48 object-cover rounded-lg border" />
                    </div>
                </div>
            </template>
        </div>

        <!-- Navigation bottom -->
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
            currentPage: 0,
            pageNum: 0,
            pageNumError: '',

            images: [],
            totalPages: 0,

            btnSaveSettings: {
                text: "Save",
                class: "bg-green-500 text-white px-4 py-2 rounded",
                origText: "Save",
                origClass: "bg-green-500 text-white px-4 py-2 rounded",
            },

            btnSyncMatches: {
                text: "Save dataset to file",
                class: "bg-green-500 text-white px-4 py-2 rounded",
                origText: "Save dataset to file",
                origClass: "bg-green-500 text-white px-4 py-2 rounded",
            },
        }
    },

    methods: {
        async loadImages() {
            this.images = [] // Fixes duplicate products on changing page 
            // TODO: but spamming next/prev page makes vue not update anymore
            try {
                const response = await axios.get(`/api/images?page=${this.currentPage}`)

                this.images = response.data.images
                this.totalPages = response.data.total_pages
            } catch (error) {
                console.error('Error loading images:', error)
            }
        },

        async loadSettings() {
            const response = await axios.get(`/api/load_settings`)
            if (response.data.settings.lastPage) this.currentPage = response.data.settings.lastPage
        },

        async updateMatching(image, index, match) {
            try {
                const response = await axios.post('/api/images/update', {
                    id: image.id,
                    source_name: image.source_name,
                    source_image: image.source_image,
                    target_name: image.target_name,
                    target_image: image.target_image,
                    matching: match
                })
                if (response.data.success) {
                    // this.images[index].matching = match
                    image.matching = match
                }
            } catch (error) {
                console.error('Error updating image:', error)
            }
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

        shouldShowSeparator(index) {
            // Don't show separator for first item
            if (index === 0) return true;

            // Show separator if current name is different from previous name
            return this.images[index].source_name !== this.images[index - 1].source_name;
        },

        async markDfAsComplete(btnState) {
            const apiUrl = '/api/mark_complete'
            await this.syncBtnHandler(apiUrl, {}, btnState)
        },

        async syncSettings(btnState) {
            const apiUrl = '/api/save_settings'
            const data = {
                lastPage: this.currentPage,
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

.separator {
    margin: 12px 0 8px 0;
    padding: 4px 12px;
    background: linear-gradient(to right, #4f46e5, #7c3aed);
    color: white;
    font-weight: 500;
    font-size: 0.875rem;
    border-radius: 4px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
</style>
