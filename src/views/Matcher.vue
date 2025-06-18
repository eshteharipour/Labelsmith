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
                <button :class="btnSyncMatches.class" @click="syncChanges(btnSyncMatches)">
                    {{ btnSyncMatches.text }}
                </button>
                <button class="px-4 py-2 rounded transition-colors"
                    :class="showHighlights ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'"
                    @click="toggleHighlights">
                    {{ showHighlights ? 'Highlighting On' : 'Highlighting Off' }}
                </button>
                <button class="px-4 py-2 rounded transition-colors"
                    :class="centeredLayout ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'"
                    @click="changeLayout">
                    {{ centeredLayout ? 'Centered layout' : 'Side layout' }}
                </button>
            </div>
            <button :class="btnSyncPage.class" @click="syncPage(btnSyncPage)">
                {{ btnSyncPage.text }}
            </button>
            <button :class="btnSyncAll.class" @click="syncAll(btnSyncAll)">
                {{ btnSyncAll.text }}
            </button>
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


        <!-- Text Dir Test -->
        <!-- <div class="text-lg font-semibold mb-2" :class="getTextDirectionClass('eng1 lish1 فا رسی eng2 lishhhhhhhhh2')">
            'eng1 lish1 فا رسی eng2 lishhhhhhhhh2'
        </div>
        <div class="text-lg font-semibold mb-2" :class="getTextDirectionClass('فا1 eng lishhhhhhhhhhhh رسی2')">
            'فا1 eng lishhhhhhhhhhhh رسی2'
        </div>
        <div class="text-lg font-semibold mb-2" :class="getTextDirectionClass('ترانزیستور قدرت 2n3055 60v 15a')">
            'ترانزیستور قدرت 2n3055 60v 15a'
        </div>
        <div class="text-lg font-semibold mb-2" :class="getTextDirectionClass('2n3055 معمولی')">
            '2n3055 معمولی'
        </div> -->

        <!-- Row View -->
        <div class="space-y-6">
            <!-- Separator -->
            <template v-for="(image, index) in images" :key="image.id">
                <!-- <div v-if="shouldShowSeparator(index)" class="bg-gray-100 p-3 rounded-lg font-semibold"> -->
                <div v-if="shouldShowSeparator(index)" class="separator">
                </div>
                <!-- Dynamic Section Ordering -->
                <div class="flex items-center justify-between border rounded-lg p-6 bg-white shadow-sm">
                    <template v-for="section in orderedSections" :key="section">
                        <!-- Source Section -->
                        <div v-if="section === 'source'" class="flex flex-col items-center w-1/3">
                            <div class="text-lg font-semibold mb-2" :class="getTextDirectionClass(image.source_name)">
                                {{ image.source_name }}
                            </div>
                            <div v-if="image.source_category" class="text-lg font-semibold mb-2"
                                :class="getTextDirectionClass(image.source_category)">
                                {{ image.source_category }}
                            </div>
                            <img :src="`/api/images/file?image_path=${encodeURIComponent(image.source_image)}`"
                                :alt="image.source_image" class="w-48 h-48 object-cover rounded-lg border" />
                        </div>
                        <!-- Matching Controls -->
                        <div v-else-if="section === 'controls'"
                            class="flex flex-col items-center justify-center w-1/4 space-y-4">
                            <div v-if="image.evaluator" class="text-sm text-gray-600">Last evaluator</div>
                            <div v-if="image.evaluator" class="text-sm text-gray-600">{{ image.evaluator }}</div>
                            <div v-if="image.response" class="text-sm text-gray-600">Model response</div>
                            <div v-if="image.response" class="text-sm text-gray-600">{{ image.response }}</div>
                            <div v-if="image.response2" class="text-sm text-gray-600">Model 2 response</div>
                            <div v-if="image.response2" class="text-sm text-gray-600">{{ image.response2 }}</div>
                            <!-- <div class="text-sm text-gray-600">Match Status</div> -->
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
                        <div v-else-if="section === 'target'" class="flex flex-col items-center w-1/3">
                            <div class="text-lg font-semibold mb-2" :class="getTextDirectionClass(image.target_name)"
                                v-html="showHighlights ? matchHighlighter(image.target_name, image.source_name) : image.target_name">
                            </div>
                            <div v-if="image.target_category" class="text-lg font-semibold mb-2"
                                :class="getTextDirectionClass(image.target_category)">
                                {{ image.target_category }}
                            </div>
                            <!-- <div class="text-lg font-semibold mb-2">{{ image.target_name }}</div> -->
                            <img :src="`/api/images/file?image_path=${encodeURIComponent(image.target_image)}`"
                                :alt="image.target_image" class="w-48 h-48 object-cover rounded-lg border" />
                        </div>
                    </template>
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
            showHighlights: true,
            centeredLayout: true,

            images: [],
            totalPages: 0,

            btnSaveSettings: {
                text: "Save settings",
                class: "bg-green-500 text-white px-4 py-2 rounded",
                origText: "Save settings",
                origClass: "bg-green-500 text-white px-4 py-2 rounded",
            },

            btnSyncMatches: {
                text: "Save changes to file",
                class: "bg-green-500 text-white px-4 py-2 rounded",
                origText: "Save changes to file",
                origClass: "bg-green-500 text-white px-4 py-2 rounded",
            },

            btnSyncPage: {
                text: "Save this page to file",
                class: "bg-green-500 text-white px-4 py-2 rounded",
                origText: "Save this page to file",
                origClass: "bg-green-500 text-white px-4 py-2 rounded",
            },

            btnSyncAll: {
                text: "Save all pages to file",
                class: "bg-green-500 text-white px-4 py-2 rounded",
                origText: "Save all pages to file",
                origClass: "bg-green-500 text-white px-4 py-2 rounded",
            },
        }
    },

    computed: {
        orderedSections() {
            return this.centeredLayout
                ? ['source', 'controls', 'target']
                : ['source', 'target', 'controls'];
        },
    },

    methods: {
        startsWithPersian(text) {
            if (!text) return false;

            // Persian/Farsi Unicode ranges
            const persianRange = /^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;

            return persianRange.test(text);
        },

        getTextDirectionClass(text) {
            if (this.startsWithPersian(text)) {
                return 'rtl-text';
            } else {
                return 'ltr-text';
            }
        },

        toggleHighlights() {
            this.showHighlights = !this.showHighlights;
        },

        changeLayout() {
            this.centeredLayout = !this.centeredLayout;
        },

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
            try {
                const response = await axios.get(`/api/load_settings`)
                if (response.data.settings.lastPage) this.currentPage = response.data.settings.lastPage
                if (response.data.settings.showHighlights) this.showHighlights = response.data.settings.showHighlights
                if (response.data.settings.centeredLayout) this.centeredLayout = response.data.settings.centeredLayout
            } catch (error) {
                console.error('Error loading settings:', error)
            }
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

        async syncChanges(btnState) {
            const apiUrl = '/api/sync_changes'
            await this.syncBtnHandler(apiUrl, {}, btnState)
        },

        async syncPage(btnState) {
            const apiUrl = '/api/sync_page'
            const data = {
                page: this.currentPage,
            }
            await this.syncBtnHandler(apiUrl, data, btnState)
        },

        async syncAll(btnState) {
            const apiUrl = '/api/sync_all'
            await this.syncBtnHandler(apiUrl, {}, btnState)
        },

        async syncSettings(btnState) {
            const apiUrl = '/api/save_settings'
            const data = {
                lastPage: this.currentPage,
                showHighlights: this.showHighlights,
                centeredLayout: this.centeredLayout,
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

        matchHighlighter(text, searchString) {
            if (!searchString || !text) return text;

            const searchWords = searchString.toLowerCase().split(/\s+/).filter(word => word.length > 0);

            if (searchWords.length === 0) return text;

            // Use word boundaries to match whole words only
            const pattern = new RegExp(`\\b(${searchWords.map(word => this.escapeRegExp(word)).join('|')})\\b`, 'gi');

            return text.replace(pattern, '<span class="highlight">$1</span>');
        },

        escapeRegExp(string) {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
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

.rtl-text {
    direction: rtl;
    text-align: right;
    unicode-bidi: embed;
    font-family: 'Tahoma', 'Arial', sans-serif;
    line-height: 1.6;
}

.ltr-text {
    direction: ltr;
    text-align: left;
    unicode-bidi: embed;
    font-family: 'Tahoma', 'Arial', sans-serif;
    line-height: 1.6;
    /* Let browser handle bidirectional text naturally */
    /* unicode-bidi: plaintext; */
}

.rtl-text .highlight,
.ltr-text .highlight {
    background-color: yellow;
    padding: 2px 4px;
    border-radius: 3px;
    /* unicode-bidi: inherit; */
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
