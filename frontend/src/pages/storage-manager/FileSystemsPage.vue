<template>
    <q-page padding>
        <q-table
            :rows="data"
            :columns="columns"
            :pagination="pagination"
            selection="multiple"
            row-key="name"
            v-model:selected="selectedRows"
            :loading="tableLoading"
        >
            <template v-slot:top-right>
                <q-btn
                    round
                    flat
                    color="primary"
                    icon="mdi-eraser"
                    :disable="selectedRows.length == 0"
                >
                    <q-tooltip :offset="[0,2]">Clear</q-tooltip>
                </q-btn>
            </template>
            <template v-slot:body-cell-mounted>
                <q-td>
                    <q-chip class="q-mx-none"
                        label="Mounted"
                        icon="mdi-check"
                        color="green"
                    />
                </q-td>
            </template>
            <template v-slot:loading>
                <q-inner-loading showing />
            </template>
        </q-table>
    </q-page>
</template>

<script>

export default{
    data(){
        return {
            data: [],
            columns: [
                {
                    name: "device",
                    label: "Device",
                    field: "path",
                    align: "left",
                    sortable: true,
                },
                {
                    name: "type",
                    label: "Type",
                    field: "type",
                    align: "left",
                    sortable: true,
                },
                {
                    name: "filesystem",
                    label: "Filesystem",
                    field: "fstype",
                    align: "left",
                    sortable: true,
                },
                {
                    name: "size",
                    label: "Size",
                    field: "size",
                    align: "left",
                },
                {
                    name: "mounted",
                    label: "Mounted",
                    field: "mounted",
                    align: "left",
                },
                {
                    name: "mountpoint",
                    label: "Mountpoint",
                    field: "mountpoint",
                    align: "left",
                },
            ],
            pagination: {
                rowsPerPage: 15,
                sortBy: "name",
            },
            selectedRows: [],
            tableLoading: true,
        }
    },
    methods: {
        fetchData(){
            this.tableLoading = true
            this.$api.get("storage/filesystems")
            .then((response) => {
                this.data = response.data
                console.log(response.data)
                this.tableLoading = false
            })
            .catch((error) => {
                console.log(error)
            })
        }
    },
    mounted(){
        this.fetchData()
    },
}
</script>