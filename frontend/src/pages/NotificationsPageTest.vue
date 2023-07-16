<template>
  <q-page padding>
    <q-btn label="Add 1" @click="AddOne" />
    <q-btn label="Add 2 warning" @click="AddTwo('warning')" />
    <q-btn label="Add 2 error" @click="AddTwo('error')" />
    <q-btn label="Add 2 info" @click="AddTwo('info')" />
    <q-btn label="Add 2 success" @click="AddTwo('success')" />
  </q-page>
</template>

<script>
export default {
  methods: {
    AddOne() {
      this.$api
        .post("/notifications", [
          {
            title: "Test One Message",
            type: "info",
            message: "Test Single Message",
          },
        ])
        .then((response) => {
          console.log("success adding notification");
        })
        .catch((error) => {
          console.log("error adding notification", error);
        });
    },
    AddTwo(type = "info") {
      this.$api
        .post("/notifications", [
          {
            title: "Test Two Message",
            type: type,
            message: "Test Double Message",
          },
          {
            title: "Test Two Message 2",
            type: type,
            message: "Test Double Message 2",
          },
        ])
        .then((response) => {
          console.log("success adding notification");
        })
        .catch((error) => {
          console.log("error adding notification", error);
        });
    },
  },
};
</script>
