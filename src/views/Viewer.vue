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
                <!-- Image Card -->
                <div class="flex items-center justify-between border rounded-lg p-6 bg-white shadow-sm">
                    <div class="flex flex-col items-center w-1/3">
                        <div class="text-lg font-semibold mb-2 farsi-text">{{ image.name }}</div>
                        <img :src="`/api/images/file?image_path=${encodeURIComponent(image.path)}`" :alt="image.path"
                            class="w-48 h-48 object-cover rounded-lg border" />
                        <div v-if="image.path" class="text-sm truncate w-full text-gray-600">{{
                            image.path.split('/').slice(-1).join() }}
                        </div>
                    </div>
                    <div class="flex flex-col items-center w-1/3">
                        <div class="text-lg font-semibold mb-2">{{ image.rn18_l2_d }}</div>
                        <img :src="`/api/images/file?image_path=${encodeURIComponent(image.rn18_l2)}`"
                            :alt="image.rn18_l2" class="w-48 h-48 object-cover rounded-lg border" />
                        <div v-if="image.rn18_l2" class="text-sm truncate w-full text-gray-600">{{
                            image.rn18_l2.split('/').slice(-1).join()
                            }}
                        </div>
                    </div>
                    <div class="flex flex-col items-center w-1/3">
                        <div class="text-lg font-semibold mb-2">{{ image.rn18_ip_d }}</div>
                        <img :src="`/api/images/file?image_path=${encodeURIComponent(image.rn18_ip)}`"
                            :alt="image.rn18_ip" class="w-48 h-48 object-cover rounded-lg border" />
                        <div v-if="image.rn18_ip" class="text-sm truncate w-full text-gray-600">{{
                            image.rn18_ip.split('/').slice(-1).join()
                            }}
                        </div>
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
                text: "Save settings",
                class: "bg-green-500 text-white px-4 py-2 rounded",
                origText: "Save settings",
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

/* Farsi RTL styling */
.farsi-text {
    direction: rtl;
    text-align: right;
    unicode-bidi: bidi-override;
    font-family: 'Tahoma', 'Arial', sans-serif;
    line-height: 1.6;
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
</style>
