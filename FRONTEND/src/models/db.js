import PouchDB from "pouchdb";
import pouchdbFind from "pouchdb-find";
import interfaceDB from "./interface";

PouchDB.plugin(pouchdbFind);

const pageData = new PouchDB("pageData");
pageData.createIndex({
  index: { fields: ["name"] },
});

const locat = new PouchDB("location");
locat.createIndex({
  index: { fields: ["title"] },
});


const pageDataDb = new interfaceDB(pageData);
const locationDb = new interfaceDB(locat);



// console.log("ldb",locationDb, pageDataDb);
export { pageDataDb, locationDb };
