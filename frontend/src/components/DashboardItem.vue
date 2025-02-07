<template>
  <q-item clickable tag="a" :to="to">
    <div class="row items-center">
      <div class="q-pr-sm"><q-icon :name="icon" size="sm" /></div>
      <div>{{ name }}</div>
    </div>
  </q-item>
</template>

<script>
export default {
  props: {
    to: {
      type: String,
      default: "/",
    },
    icon: {
      type: String,
      default: undefined,
    },
    name: {
      type: String,
      default: undefined,
    },
  },
};
</script>
