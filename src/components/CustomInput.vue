<template>
    <div class="input-wrapper">
        <label v-if="label" :for="id" class="input-label">{{ label }}:</label>
        <div class="input-container">
            <input :id="id" :type="type" :value="modelValue" :placeholder="placeholder" :disabled="disabled"
                class="input-field" @input="$emit('update:modelValue', $event.target.value)"
                @keyup.enter="$emit('enter', modelValue)" />
            <span v-if="error" class="input-error">{{ error }}</span>
        </div>
    </div>
</template>

<script>
export default {
    name: 'CustomInput',
    props: {
        modelValue: {
            type: [String, Number],
            default: ''
        },
        label: {
            type: String,
            default: ''
        },
        placeholder: {
            type: String,
            default: ''
        },
        type: {
            type: String,
            default: 'text'
        },
        error: {
            type: String,
            default: ''
        },
        disabled: {
            type: Boolean,
            default: false
        },
        id: {
            type: String,
            required: true
        }
    },
    emits: ['update:modelValue', 'enter']
}
</script>

<style scoped>
.input-wrapper {
    float: left;
    display: inline;
    align-items: center;
    gap: 0.5rem;
}

.input-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    white-space: nowrap;
}

.input-container {
    display: flex;
    align-items: center;
}

.input-field {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.2s ease;
}

.input-field:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.input-field:disabled {
    background-color: #f3f4f6;
    cursor: not-allowed;
}

.input-error {
    margin-left: 0.5rem;
    font-size: 0.875rem;
    color: #dc2626;
}
</style>