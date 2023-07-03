<template>
  <q-tooltip
    :delay="500"
    anchor="bottom middle"
    self="top middle"
    :offset="[0, 8]"
  >
    {{ content }}
  </q-tooltip>
</template>

<script>
export default {
  props: ["content"],
};
</script>
