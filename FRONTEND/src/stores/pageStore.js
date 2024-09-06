import { defineStore } from "pinia";
import { pageDataDb } from "models/db";
export const usePageStore = defineStore("pageStore", {
  state: () => ({
    enterAnim: "slideInFromLeft",
    leaveAnim: "slideOutToRight",
    scrollPos: {},
    pageStack: ["/"],
    pageHash: {},
    includes: ["IndexPage"],
    pageData: { useData: "wrf" },
    contentData: null,
    dummy: {},
  }),
  persist: {
    paths: ["dummy"],
  },
  getters: {
    getScroll: (state) => (name) => {
      return name in state.scrollPos ? state.scrollPos[name] : 0;
    },
    getData: (state) => {
      return async (name) => {
        const res = await pageDataDb.getById(name);
        if (res.status == true) {
          return res.result.value;
        } else {
          return null;
        }
      };
    },
    getContent: (state) => {
      // console.log("getcontent", state.contentData);
      return state.contentData;
    },
  },
  actions: {
    async removeContent() {
      this.contentData = null;
    },
    async setContent(data) {
      // console.log("setcontent", data);
      this.contentData = data;
    },
    async setData(name, value) {
      const check = await pageDataDb.getById(name);
      let res = null;
      if (check.status == true) {
        check.result.value = value;
        // console.log("UPdate");
        res = await pageDataDb.update(check.result);
      } else {
        // console.log("Create");
        res = await pageDataDb.create({
          _id: name,
          value: value,
        });
      }
      return res;
    },
    setScroll(name, pos) {
      // console.log("setScroll", name, this.scrollPos, pos);
      this.scrollPos[name] = pos;
    },
    removeScroll(name) {
      // console.log("removeScroll", name, this.scrollPos);
      if (name in this.scrollPos) {
        delete this.scrollPos[name];
      }
    },
  },
});
