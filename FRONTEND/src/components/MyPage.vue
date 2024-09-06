<template>
  <q-page v-scroll="handleScroll"
    style="position: relative; width: 100vw; height: 100vh; padding: 0; display:flex; flex-direction: column"
    ref="mpage" class="page full-height">
    <!-- <q-bar class="bg-primary text-white q-py-lg q-pr-lg">
      <q-btn
        class="q-mr-md"
        flat
        dense
        v-if="pageStore.pageStack.length > 1"
        @click="router.pop()"
      >
        <q-icon name="mdi-arrow-left-bold"></q-icon>
      </q-btn>
      <span class="text-h6"><slot name="title"></slot></span>
    </q-bar> -->
    <!-- <q-page-sticky expand position="top"> -->
    <q-toolbar class="bg-green-9 text-white" ref="toolbarRef" style="z-index: 10; visibility: hidden" v-if="toolbar">
      <q-btn class="q-mr-xs text-size-16" flat dense v-if="pageStore.pageStack.length > 1 && backButton"
        @click="router.pop()">
        <q-icon name="mdi-chevron-left"></q-icon>
      </q-btn>

      <slot name="title">Nakula</slot>
    </q-toolbar>
    <!-- bg-green-9 text-white  -->
    <q-toolbar class="text-bold bg-primary text-left text-white"
      style="position: fixed; width: 100vw; top: 0px; z-index: 10; pointer-events: none" ref="stickyToolbarRef"
      v-if="toolbar">
      <q-btn class="q-mr-xs text-size-16" flat dense style="pointer-events: all;" @click="router.pop()"
        v-if="pageStore.pageStack.length > 1 && backButton">
        <q-icon name="mdi-chevron-left"></q-icon>
      </q-btn>
      <q-toolbar-title>
        <slot name="title">Nakula</slot>
      </q-toolbar-title>
    </q-toolbar>
    <div class="text-size-16" :class="props.addClass" :style="props.addStyle" style="z-index: 1">
      <slot></slot>
    </div>
  </q-page>
</template>
<style lang="scss">
.page {
  overflow-y: auto;
  // background-image: url("../assets/logo20_pad.png");
  // background-size: contain;
  // background-position: center;
  // background-repeat: no-repeat;
  // background-color: white !important;
  // background-color: rgba(255, 255, 255, 0.2);
}
body.body--dark .page{
  background-color: $dark-page !important;
}

body.body--light .page{
  background-color: whitesmoke !important;
}
</style>
<script setup>
defineOptions({
  name: 'MyPage'
})
import { usePageStore } from "src/stores/pageStore";
import { useRouter, useRoute } from "vue-router";
import {
  ref,
  provide,
  onDeactivated,
  onUnmounted,
  onMounted,
  onActivated,
  nextTick,
  inject,
  onBeforeUnmount
} from "vue";
import { debounce, scroll } from "quasar";
const { getScrollTarget, setVerticalScrollPosition } = scroll;

const pageStore = usePageStore();
const router = useRouter();
const route = useRoute();
const showStick = ref(false);
let doHandleScroll = false;
const toolbarRef = ref(null);
const stickyToolbarRef = ref(null);
const mpage = ref(null);
const emitter = inject("mitt");
// mitt.register()
const props = defineProps({
  addClass: {
    type: String,
    default: "q-pa-sm",
  },
  height: {
    type: Number,
    default: 70,
  },
  backButton: {
    type: Boolean,
    default: true,
  },
  toolbar: {
    type: Boolean,
    default: true
  },
  addStyle: {
    // type: Object,
    // default: ()=>({})
    type: String,
    default: "",
  }
});

// const emitter = inject("mitt");

const handleScroll = debounce((pos) => {
  // if (!doHandleScroll) {
  //   return;
  // }
  // if (pos > props.height) {
  //   showStick.value = true;
  // } else {
  //   showStick.value = false;
  // }
  // console.log("SCROOOOL", pos);
  pageStore.setScroll(route.name, pos);
  // console.log(router, route);
}, 100);

// defineExpose({
//   toolbarRef,
// });

// onMounted(() => {
//   emitter.off("pageScroll", handleScroll);
//   emitter.on("pageScroll", handleScroll);
// });
async function handlePageEnterStart() { }
function handlePageAfterEnter() {
  if (pageStore.pageStack.length > 1 && props.backButton) {
    if (stickyToolbarRef.value != null) {
      stickyToolbarRef.value.$el.style.top = "0px";
    }
  }
}
onActivated(async () => {
  // console.log(pageStore.includes = ["IndexPage"]);
  // console.log(pageStore.includes);
  // console.log(route.path);
  // emitter.register("pageEnterStart", handlePageEnterStart);
  emitter.register("pageOnAfterEnter", handlePageAfterEnter);
  // console.log("show", showStick.value);
  // showStick.value = true;
  await nextTick();
  const toolbarEl = toolbarRef.value;
  const scrollPos = pageStore.getScroll(route.name);
  const target = getScrollTarget(mpage.value.$el);
  const duration = 0;
  // console.log("setTbar To", scrollPos);
  if (pageStore.pageStack.length > 1 && props.backButton) {
    stickyToolbarRef.value.$el.style.top = scrollPos + "px";
  }
  setVerticalScrollPosition(target, scrollPos, duration);
  await nextTick();

  // doHandleScroll = true;
});

onDeactivated(() => {
  // showStick.value = true;

  // console.log("removing emitter deactivated");
  // console.log(route.path);
  doHandleScroll = false;
  // emitter.off("pageEnterStart", handlePageEnterStart);
});
onMounted(() => {
  // console.log(pageStore.includes, pageStore.pageStack.length);
  // console.log("MOUNTED");
  // mpage.value.$el.addEventListener("scroll", handleScroll, { passive: true })
})
onBeforeUnmount(() => {
  // console.log("removing emitter unmount");
  // mpage.value.$el.addEventListener("scroll", handleScroll);
});
</script>
