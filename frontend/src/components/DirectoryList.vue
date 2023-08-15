<template>
    <q-input
        v-model="currentPath" 
        type="text" 
        @update:model-value="updateCurrentPath"
        class="q-my-none q-py-none"
        :label="label"
        bottom-slots
        :loading="loading"
        ref="input"
    >
        <template v-slot:append>
            <q-btn 
                icon="mdi-menu-down"
                class="q-pa-none"
                flat
                @click="focused = true"
                v-if="focused == false"
            />
            <q-btn 
                icon="mdi-menu-up"
                class="q-pa-none"
                flat
                @click="focused = false"
                v-if="focused == true"
            />
            <slot name="append"></slot>
        </template>
        <template v-slot:hint>
            <q-menu 
                v-model="focused" 
                fit 
                class="q-my-none q-py-none"
                @hide="$refs.input.focus(); $refs.input.blur();"
            >
                <q-list 
                    class="q-my-none q-py-none dropdown shadow-3" 
                    :class="{ 'bg-dark': $q.dark.isActive, 'bg-white': !$q.dark.isActive }"
                    v-show="focused"
                >
                    <q-item v-for="option in options" clickable @click="clickItem(option)" :key="option.name">
                        <q-item-section side>
                            <q-icon 
                                :name="option.type == 'file' ? 'mdi-file' : 'mdi-folder'"
                                color="white"
                            />
                        </q-item-section>
                        <q-item-section>
                            <q-item-label>{{ option.name }}</q-item-label>
                        </q-item-section>
                    </q-item>
                </q-list>
            </q-menu>
        </template>
    </q-input>
</template>

<script>
export default {
    data(){
        return {
            options: [],
            selectedPath: '',
            currentPath: this.modelValue,
            focused: false,
            isValid: false,
            loading: false
        }
    },
    props: {
        modelValue: {
            type: String,
            default: null
        },
        selectiontype: {
            type: String,
            default: 'file'
        },
        startpath: {
            type: String,
            default: '/mnt/sharedfolders'
        },
        label: {
            type: String,
            default: undefined
        }
    },
    methods: {
        getData(path, init=false) {
            this.loading = true
            this.$api.post('system/file-manager', {
                path: path
            })
            .then(response => {
                this.options = response.data.list
                if (init == false){
                    this.currentPath = response.data.path
                }
                this.loading = false
            })
        },
        updateCurrentPath(value) {
            this.getData(value)
        },
        clickItem(value){
            if (value.type == 'dir') {
                if(this.selectiontype == 'dir'){
                    this.setCurrentPath(value)
                }
                this.getData(value.path)
            }
            else if (value.type == 'dirparent'){
                if(this.selectiontype == 'dir'){
                    this.setCurrentPath(value)
                }
                this.getData(value.path)
            }
            else if (value.type == 'file' && this.selectiontype == 'file') {
                this.setCurrentPath(value)
                this.focused = false
            }
        },
        setCurrentPath(value) {
            this.currentPath = value.path
            this.$emit('update:modelValue', value.path);
            if(this.selectiontype == 'dir'){
                value.type == 'dir' ? this.isValid = true : this.isValid = false
            }
            else if(this.selectiontype == 'file'){
                value.type == 'file' ? this.isValid = true : this.isValid = false
            }
        }
    },
    mounted() {
        if (this.modelValue == null || this.modelValue == ''){
            this.$emit('update:modelValue', null);
            this.currentPath = this.startpath
            this.getData(this.currentPath)
            return
        }
        this.$api.post('system/file-manager/validate-path', {
            path: this.modelValue
        })
        .then((response) => {
            this.currentPath = this.modelValue
            this.$emit('update:modelValue', this.modelValue);
            if (response.data.type == 'dir'){
                this.getData(this.currentPath)
            }
            else if (response.data.type == 'file'){
                this.getData(response.data.parent, true)
            }
        })
        .catch((error) => {
            this.$emit('update:modelValue', null);
            this.currentPath = this.startpath
            this.getData(this.currentPath)
        })
    },
}

</script>