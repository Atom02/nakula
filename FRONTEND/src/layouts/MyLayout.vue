<template>
  <q-layout view="hHh LpR fFf" id="myLayout">
    <!-- <q-header elevated> -->
    <!-- <q-toolbar>
        <q-toolbar-title> Quasar App </q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar> -->
    <!-- </q-header> -->
    <q-page-container style="padding: 0" ref="pageContainer">
      <router-view v-slot="{ Component }">
        <transition appear leave-active-class="leave" enter-active-class="enter" @before-enter="onBeforeEnter"
          @after-enter="onAfterEnter">
          <KeepAlive :include="pageStore.includes">
            <component :is="Component" :key="$route.name" class="scroll" style="position: fixed;">
            </component>
          </KeepAlive>
        </transition>
      </router-view>
      <q-resize-observer @resize="onResize" />
    </q-page-container>
  </q-layout>
</template>
<script>
export default {
  name: "MyLayout",
  inheritAttrs: true,
  customOptions: {},
};
</script>
<script setup>
// import VuePageStack from "vue-page-stack";
import {
  defineComponent,
  ref,
  onMounted,
  nextTick,
  watch,
  onActivated,
  inject,
  onDeactivated,
} from "vue";
import { useQuasar, debounce, AddressbarColor, colors } from "quasar";
import { useRoute } from "vue-router";
import { usePageStore } from "src/stores/pageStore";

const route = useRoute();
const pageStore = usePageStore();
const { getPaletteColor } = colors;
const emitter = inject("mitt");
const pageContainer = ref(null);
const transSpeed = "0.4s"

// const debouncedScroll = debounce(onScroll, 100);
const $q = useQuasar();

function onBeforeEnter(el) {
  // console.log("entering start");
  // alert("YEAH");
  // done();
  // emitter.emit("pageEnterStart");
}
function onAfterEnter(el) {
  // console.log("ending transition")
  emitter.emit("pageOnAfterEnter");
}


const onResize = debounce((size) => {
  emitter.emit("pageResizes", size);
}, 300)
onMounted(async () => {
  // console.log(getPaletteColor("primary"));
  await nextTick();
  // console.log("mylayout",pageContainer.value.$el.style);
  pageContainer.value.$el.style.height = "100%";
  pageContainer.value.$el.style.position = "fixed";
  pageContainer.value.$el.style.width = "100%";
  pageContainer.value.$el.style.top = "0px";
  pageContainer.value.$el.style.left = "0px";
  pageContainer.value.$el.style.padding = "0px";
  // pageContainer.value.$el.style.overflow = "hidden";
  // AddressbarColor.set(getPaletteColor("primary"));
  // $q.addressbarColor.set("#a2e3fa");
});
</script>
<style lang="scss">
.enter {
  animation: v-bind("pageStore.enterAnim") v-bind("transSpeed") forwards;
  box-shadow: 0px 0px 5px 5px rgba(0, 0, 0, 0.2);  
  z-index: 99;
  // position: fixed;
  // top: 0;
  // left: 0;
}
body.body--dark .enter{
  background-color: $dark-page !important;
}

body.body--light .enter{
  background-color: whitesmoke !important;
}


.leave {
  animation: v-bind("pageStore.leaveAnim") v-bind("transSpeed") forwards;
  z-index: 1;
}

@keyframes slideInFromRight {
  from {
    transform: translateX(100%);
  }

  to {
    transform: translateX(0);
  }
}

@keyframes slideOutToLeft {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(-20%);
  }
}

@keyframes slideInFromLeft {
  from {
    transform: translateX(-100%);
  }

  to {
    transform: translateX(0);
  }
}

@keyframes slideOutToRight {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(20%);
  }
}
</style>
