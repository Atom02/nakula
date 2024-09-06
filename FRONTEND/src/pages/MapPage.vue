<template>
  <my-page add-class="q-pt-none" add-style="flex-grow:1">
    <div class="column" style="height: 100%">
      <div class="col-12 bg-red">
        <div id="mapContainer" ref="mapContainer" class="bg-blue" style="height:100%;width:100%"></div>
      </div>
    </div>
  </my-page>
</template>
<script>
export default {
  name: "MapPage",
  inheritAttrs: true,
  customOptions: {},
};
</script>
<script setup>
import MyPage from "components/MyPage.vue";
import { ref, onMounted, nextTick } from "vue"
import _ from "lodash";
import L from "leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import "leaflet/dist/leaflet.css";
import "esri-leaflet-geocoder/dist/esri-leaflet-geocoder.css";
import * as esri from "esri-leaflet";
import * as esriGeocoding from "esri-leaflet-geocoder";
import { locationDb } from "models/db";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});
L.esri = esri;
L.geocoding = esriGeocoding;

const mapContainer = ref(null);

let zoom, mapObj, center = null;
onMounted(async () => {
  await nextTick();
  let myzoom = zoom ?? 5;
  let mycenter = center ?? [-1.033, 117.729];

  mapObj = L.map(mapContainer.value, {
    minZoom: 5,
    maxZoom: 18,
    debounceMoveend: true,
  }).setView(mycenter, myzoom);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(mapObj);
  const arcgisOnline = L.geocoding.arcgisOnlineProvider({
    countries: "IDN",
    apikey:
      "AAPKf987d6b72f164516a98df3db121b2a38tf36XsiGMPXDXVm4uzxfG3Ltb2MJyFbadVKsyPDLxFJh4BoIP6DR3IfSrOrhXhoP",
  });
  const geocodeService = L.geocoding.geocodeService();
  const geoSearchControl = L.geocoding.geosearch({
    position: "topright",
    expanded: true,
    collapseAfterResult: false,
    // countries: 'IDN',
    // zoomToResult: false,
    useMapBounds: false,
    placeholder: "Cari Lokasi",
    providers: [arcgisOnline]
  }).addTo(mapObj);


  geoSearchControl.on('results', async function (data) {
    // console.log(data.results[0]);
    await nextTick();
    // addAdministrativeBoundaries(data.results[0].properties.placeName);
    // const { lat, lng } = data.results[0].latlng;
    // mapObj.flyTo([lat, lng], mapObj.zoom, {
    //   duration: 0.1
    // });
  });

  // Define a function to query and add administrative boundaries
  function addAdministrativeBoundaries(placeName) {

    // Send a POST request to Overpass API
    bareApi.get('https://nominatim.openstreetmap.org/search', {
      q: placeName,
      format: 'jsonv2',
      polygon_geojson: 1,
      limit: 2,
      'accept-language': 'id',
      'countrycodes': 'ID'
    })
      .then(response => {
        let useItem = null;
        if (locationBoundary != null) {
          mapObj.removeLayer(locationBoundary);
          locationBoundary = null
        }
        response.data.every(item => {
          if (item.category != "boundary") {
            return true;
          } else {
            useItem = item;
            return false;
          }
        });
        if (useItem != null) {
          locationBoundary = L.geoJSON(useItem.geojson, {
            style: {
              color: '#3388ff',
              weight: 2,
              opacity: 0.8
            }
          });
          locationBoundary.addTo(mapObj);
        }
        // const geojsonLayer = L.geoJSON(response.data, {
        //   style: {
        //     color: '#3388ff',
        //     weight: 2,
        //     opacity: 0.8
        //   }
        // }).addTo(mapObj);

        // // Fit map bounds to the loaded data
        // mapObj.fitBounds(geojsonLayer.getBounds());
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }

});
</script>
