import { boot } from "quasar/wrappers";
import { usePageStore } from "src/stores/pageStore";
import { isNavigationFailure } from "vue-router";
// import { nanoid } from "nanoid";
import { App } from "@capacitor/app";
import mitt from "mitt";
import { Filesystem, Directory, Encoding } from "@capacitor/filesystem";
import { Atomcontentreader } from "atmocontentreader";
// import { query } from "esri-leaflet";

const emitter = mitt();

export default boot(
  async ({ app, router, store } /* { app, router, ... } */) => {
    const pageStore = usePageStore();
    emitter["register"] = (name, func) => {
      emitter.off(name);
      emitter.on(name, func);
    };
    app.provide("mitt", emitter);

    // console.log("check emitter", emitter);

    const history = {
      action: 0,
    };
    const config = {
      componentName: "VuePageStack",
      keyName: "stack-key",
      pushName: "push",
      goName: "go",
      replaceName: "replace",
      backName: "back",
      forwardName: "forward",
      pop: "pop",
      popUntil: "popUntil",
    };
    let direction = null;

    const routerPush = router.push.bind(router);
    const routerGo = router.go.bind(router);
    const routerReplace = router.replace.bind(router);
    const routerBack = router.back.bind(router);
    const routerForward = router.forward.bind(router);

    router.push = (to, params=null) => {
      history.action = config.pushName;
      direction = "f";
      pageStore.removeContent();
      if(params != null){
        pageStore.setContent(params)
      }
      return routerPush(to);
    };
    router.pop = (params=null) => {
      // console.log("pop");
      history.action = config.pop;
      direction = "b";
      pageStore.removeContent();
      if(params != null){
        pageStore.setContent(params)
      }
      return routerBack();
    };

    router.popUntil = (to, params=null) => {
      // console.log("popUntil");
      history.action = config.popUntil;
      direction = "b";
      pageStore.removeContent();
      if(params != null){
        pageStore.setContent(params)
      }
      return routerPush(to);
    };

    router.replace = (to, dir = "f", params=null) => {
      // console.log("replace");
      history.action = config.replaceName;
      direction = dir;
      pageStore.removeContent();
      if(params != null){
        pageStore.setContent(params)
      }
      return routerReplace(to);
    };
    router.beforeEach(async (to, from, next) => {
      // console.log("check", to);
      const useKey = to.fullPath;
      // console.log("WATCH ROUTE", direction, to, "from", from, history.action);

      if (history.action == null) {
        // console.log(
        //   "is it a poooop????",
        //   pageStore.pageStack.indexOf(useKey),
        //   pageStore.pageStack.length - 2,
        //   pageStore.pageStack.indexOf(useKey) == pageStore.pageStack.length - 2
        // );
        if (
          pageStore.pageStack.indexOf(useKey) ==
          pageStore.pageStack.length - 2
        ) {
          history.action = config.pop;
          direction = "b";
        }
      }

      if (
        history.action == config.pop ||
        history.action == config.popUntil ||
        direction == "b"
      ) {
        // console.log("reverse animation");
        pageStore.enterAnim = "slideInFromLeft";
        pageStore.leaveAnim = "slideOutToRight";
      } else {
        // console.log("forward animation");
        pageStore.enterAnim = "slideInFromRight";
        pageStore.leaveAnim = "slideOutToLeft";
      }

      // console.log("DIRECTION", direction);

      if (direction == "f") {
        pageStore.removeScroll(to.name);
      }

      next();
    });

    router.afterEach((to, from, failure) => {
      if (isNavigationFailure(failure)) {
      } else {
        const useKey = to.fullPath;
        const useName = to.name;
        // console.log("KEY", to, history.action, from, useName);
        if (history.action == 0) {
          // console.log("ACTION ZERO");
          // pageStore.pageStack.push(useKey);
          // pageStore.pageHash[useKey] = pageStore.pageStack.length - 1;
        } else if (history.action == config.pushName) {
          // console.log("add to stack", useKey);
          pageStore.pageStack.push(useKey);
          pageStore.includes.push(useName);
          // pageStore.pageHash[useKey] = pageStore.pageStack.length - 1;
        } else if (history.action == config.pop) {
          // delete pageStore.pageHash[useKey];
          pageStore.pageStack.pop();
          pageStore.includes.pop();
          // pageStore.removeScroll(useName);
        } else if (history.action == config.popUntil) {
          // const index = pageStore.pageHash[useKey];
          const index = pageStore.pageStack.indexOf(useKey);
          pageStore.pageStack.splice(
            index + 1,
            pageStore.pageStack.length - index - 1
          );
          pageStore.includes.splice(
            index + 1,
            pageStore.includes.length - index - 1
          );
        } else if (history.action == config.replaceName) {
          pageStore.pageStack[pageStore.pageStack.length - 1] = useKey;
          pageStore.includes[pageStore.includes.length - 1] = useName;
        }
      }
      // console.log("stack", pageStore.pageStack, pageStore.includes);
      history.action = null;
      direction = null;
    });

    App.addListener("appUrlOpen", async (data) => {
      try {
        // console.log("handling", data.url);
        const result = await Atomcontentreader.readcontent({
          uri: data.url,
        });
        const resultObj = JSON.parse(result.content);
        await pageStore.setContent(resultObj);
        if (pageStore.pageStack.length > 1) {
          await router.popUntil({ path: "/" });
        } else {
          await router.replace({ path: "/" });
        }
        emitter.emit("app.handling.nakulaLocation", resultObj);
      } catch (error) {}
    });
  }
);
