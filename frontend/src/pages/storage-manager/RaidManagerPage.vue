<template>
    <q-page padding>
        <q-table
            :rows="data"
            :columns="columns"
            :pagination="pagination"
            selection="multiple"
            row-key="path"
            v-model:selected="selectedRows"
        >
            <template v-slot:top-right>
                <q-btn
                    round
                    flat
                    color="primary"
                    icon="mdi-delete"
                    :disable="selectedRows.length == 0"
                >
                    <q-tooltip :offset="[0,2]">Delete</q-tooltip>    
                </q-btn>
                <q-btn
                    round
                    flat
                    color="primary"
                    icon="mdi-plus"
                > 
                    <q-tooltip :offset="[0,2]">New</q-tooltip>    
                </q-btn>
                <q-btn
                    round
                    flat
                    color="primary"
                    icon="mdi-stop"
                    :disable="selectedRows.length == 0 || selectedRows.some((item) => item.active == false)"
                >
                    <q-tooltip :offset="[0,2]">Stop</q-tooltip>
                </q-btn>
                <q-btn
                    round
                    flat
                    color="primary"
                    icon="mdi-play"
                    :disable="selectedRows.length == 0  || selectedRows.some((item) => item.active == true)"
                >
                    <q-tooltip :offset="[0,2]">Start</q-tooltip>
                </q-btn>
            </template>
            <template v-slot:body-cell-active="props">
                <q-td :props="props">
                    <q-chip class="q-mx-none"
                        :label="props.row.active ? 'Active' : 'Inactive'"
                        :color="props.row.active ? 'green' : 'red'"
                    />
                </q-td>
            </template>
            <template v-slot:body-cell-level="props">
                <q-td :props="props">
                    <q-chip
                        class="q-mx-none"
                        :label="props.row.personality "
                        color="primary"
                    />
                </q-td>
            </template>
            <template v-slot:body-cell-devices="props">
                <q-td :props="props">
                    <span v-for="disk in props.row.disks" :key="disk" class="row items-center">
                        <q-icon
                            class="q-pa-none q-mr-xs"
                            name="mdi-circle"
                            color="primary"
                        />
                        {{ disk }}
                </span>
                </q-td>
            </template>
            <template v-slot:body-cell-capacity="props">
                <q-td :props="props">
                    {{ props.row.size }}
                </q-td>
            </template>
        </q-table>
    </q-page>
</template>

<script>

export default{
    data(){
        return {
            data: [
                // {
                //     name: "md0",
                //     path: "/dev/md0",
                //     uuid: "1234",
                //     active: true,
                //     personality: "raid1",
                //     disks: [
                //         "/dev/sda1",
                //         "/dev/sdb1"
                //     ],
                //     size: "1.8T"
                // },
                // {
                //     name: "md1",
                //     path: "/dev/md1",
                //     uuid: "1243",
                //     active: false,
                //     personality: "raid1",
                //     disks: [
                //         "/dev/sdc1",
                //         "/dev/sdd1"
                //     ],
                //     size: "1.8T"
                // }
            ],
            columns: [
                {
                    name: "name",
                    label: "Name",
                    field: "path",
                    align: "left",
                    sortable: true,
                },
                {
                    name: "active",
                    label: "Status",
                    field: "active",
                    align: "left",
                    sortable: true,
                },
                {
                    name: "level",
                    label: "Level",
                    field: "level",
                    align: "left",
                },
                {
                    name: "devices",
                    label: "Devices",
                    field: "devices",
                    align: "left",
                },
                {
                    name: "capacity",
                    label: "Capacity",
                    field: "capacity",
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
            this.$api.get("storage/raid-manager")
            .then((response) => {
                this.data = response.data
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