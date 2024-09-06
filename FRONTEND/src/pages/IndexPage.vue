<template>
    <my-page add-class="q-pt-none text-size-16" add-style="flex-grow:1" :toolbar="false">
        <div class="row q-mt-sm q-mb-md">
            <div class="col-12 col-sm-12 text-center text-size-24">
                NAKULA
            </div>
        </div>
        
        <div class="row">
            <div class="col-12 col-sm-12 text-center">
                <q-chip outline color="white" text-color="white" icon="location_on" class="text-size-16">
                    CITY NAME
                </q-chip>
            </div>
        </div>
        <div class="row">
            <div class="col-12 col-sm-12 text-center">
                {{ ctime }}
            </div>
        </div>
        <div class="row">
            <div class="col-12 col-sm-12 text-center">
                <q-img fit="contain" src="~assets/rain.png" style="width:50%"></q-img>
            </div>
        </div>
        <div class="row">
            <div class="col-12 text-size-80 text-center" style="line-height: 1.1;">
                27
            </div>
        </div>
        <div class="row q-mb-md">
            <div class="col-12 text-center text-size-16">
                mm/jam
            </div>
        </div>
        <div class="row">
            <div class="col-12 text-center text-size-24">
                Hujan Deras
            </div>
        </div>
        <div class="row q-mt-md justify-center q-gutter-x-sm">
            <div class="col-3 col-md-2 text-center q-pa-none">
                <div class="q-mb-sm"><q-icon name="air" class="text-size-32 text-white"></q-icon></div>
                <div>10 km/h</div>
                <div>Angin</div>
            </div>
            <div class="col-3 col-md-2 text-center q-pa-none">
                <div class="q-mb-sm"><q-icon name="water_drop" class="text-size-32 text-blue"></q-icon></div>
                <div>10%</div>
                <div>Kelembaban</div>
            </div>
            <div class="col-3 col-md-2 text-center q-pa-none">
                <div class="q-mb-sm"><q-icon name="device_thermostat" class="text-size-32 text-yellow"></q-icon></div>
                <div>27&deg;</div>
                <div>Suhu</div>
            </div>
        </div>
        <div class="row q-mt-md q-pr-sm">
            <div class="col-12 text-right text-size-16 text-weight-light">
                <div @click="router.push('/map')">Selengkapnya <q-icon name="chevron_right"></q-icon></div>
            </div>
        </div>
        <div class="row no-wrap" style="overflow-x: scroll;">
            <div class="col-4 col-sm-3 q-py-md q-px-xs" v-for="item in 24" :key="item + '_num'">
                <q-card class="my-card text-center q-pa-none" :class="{
                    'bg-blue shadow-5': activeTap == item, 'no-shadow': activeTap != item
                }" @click="setActiveTap(item)">
                    <q-card-section>
                        <div>27&deg;</div>
                        <div class="q-my-sm"><q-icon name="device_thermostat" class="text-size-64 text-white"></q-icon>
                        </div>
                        <div>{{ item + ":00" }}</div>
                    </q-card-section>
                </q-card>
            </div>
        </div>
    </my-page>
</template>

<script setup>
import MyPage from "components/MyPage.vue";
import { ref, nextTick, onMounted, onUnmounted, onActivated, onDeactivated } from "vue";
import { useRouter } from "vue-router";
import { DateTime } from 'luxon';
defineOptions({
    name: "IndexPage",
    inheritAttrs: true,
    customOptions: {},
});
const router = useRouter();

const ctime = ref(null);
function getTime() {
    const currentTime = DateTime.now();
    const formattedTime = currentTime.toFormat('HH:mm'); // or use .toISO() for ISO format
    ctime.value = formattedTime;
}
const activeTap = ref(null);
function setActiveTap(item) {
    activeTap.value = item
}

let interval = null;
onMounted(async () => {
    await nextTick();
    getTime();
    interval = setInterval(()=>{
        getTime();
    },1000)
});
</script>

<style></style>