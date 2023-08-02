<template>
    <q-page padding>
        <q-table
            :rows="data"
            :columns="columns"
            :pagination="pagination"
            selection="multiple"
            row-key="name"
            v-model:selected="selectedRows"
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
            <template v-slot:body-cell-name="props">
                <q-td :props="props">
                    {{ props.row.name }}
                    <q-tooltip anchor="center middle" self="center middle" :offset="[10, 10]">{{ props.row.path }}</q-tooltip>
                </q-td>
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
                    name: "name",
                    label: "Name",
                    field: "name",
                    align: "left",
                    sortable: true,
                },
                {
                    name: "model",
                    label: "Model",
                    field: "model",
                    align: "left",
                    sortable: true,
                },
                {
                    name: "serial",
                    label: "Serial",
                    field: "serial",
                    align: "left",
                },
                {
                    name: "capacity",
                    label: "Capacity",
                    field: "size",
                    align: "left",
                }
            ],
            pagination: {
                rowsPerPage: 15,
                sortBy: "name",
            },
            selectedRows: [],
        }
    },
    methods: {
        fetchData(){
            this.$api.get("storage/disks")
            .then((response) => {
                this.data = response.data
                console.log("data", this.data)
            })
            .catch((error) => {
                console.log(error)
            })
        }
    },
    mounted(){
        this.fetchData()
    }
}
</script>