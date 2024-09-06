class interfaceDB {
  constructor(db) {
    this.db = db;
    // console.log("name", this.db.name);
  }
  async getDb() {
    return this.db;
  }
  async getDbAdapter() {
    return this.db.adapter;
  }
  async getById(id) {
    try {
      const res = await this.db.get(id);
      return {
        status: true,
        result: res,
      };
    } catch (error) {
      return {
        status: false,
        error: error,
      };
    }
  }

  async find(props) {
    try {
      const res = await this.db.find(props);
      return {
        status: true,
        result: res.docs,
      };
    } catch (error) {
      return {
        status: false,
        error: error,
      };
    }
  }

  async getAll() {
    try {
      const res = await this.db.allDocs({
        include_docs: true,
        startkey: "001",
      });
      return {
        status: true,
        result: res,
      };
    } catch (error) {
      return {
        status: false,
        error: error,
      };
    }
  }

  async create(data) {
    try {
      const res = await this.db.put(data);
      return {
        status: true,
        result: res,
      };
    } catch (error) {
      return {
        status: false,
        error: error,
      };
    }
  }

  async update(doc, deep = 0) {
    // data["_rev"] = doc._rev;
    try {
      const res = await this.db.put(doc);
      return {
        status: true,
        result: res,
      };
    } catch (error) {
      if (error.status === 409 && deep < 6) {
        // Conflict error, retry the update
        const oldDoc = await this.db.get(doc._id);
        // delete doc._id;
        // delete doc._rev;
        // const newDoc = Object.assign({}, oldDoc, doc);
        // console.log("Conflict detected, retrying...", oldDoc._rev, doc._rev);
        doc._rev = oldDoc._rev;
        // console.log("Using...", oldDoc._rev, doc._rev);
        deep = deep + 1;
        return await this.update(doc, deep++);
      } else {
        return {
          status: false,
          error: error,
        };
      }
    }
  }

  async remove(doc) {
    try {
      const res = await this.db.remove(doc._id, doc._rev);
      return {
        status: true,
        result: res,
      };
    } catch (error) {
      return {
        status: false,
        error: error,
      };
    }
  }

  async clear() {
    try {
      // const res = await this.db.destroy();
      const res = await this.db.allDocs({ include_docs: true });
      res.rows.forEach((item, i) => {
        // console.log(item);
        this.db.remove(item.doc);
      });
      return {
        status: true,
        result: res,
      };
    } catch (error) {
      return {
        status: false,
        error: error,
      };
    }
  }
}

export default interfaceDB;
