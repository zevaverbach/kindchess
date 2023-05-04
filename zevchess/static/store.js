let _store = {};
const storeHandler = {
    get: function(obj, prop) {
        return obj[prop];
    },
    set: function(obj, prop, value) {
        document.dispatchEvent(new CustomEvent(`set-${prop}`, {
            detail: {
                value: value
            }
        }));
        obj[prop] = value;
    },
};
export let store = new Proxy(store, storeHandler);

export function initializeStore(obj) {
    for (let prop in obj) {
        store[prop] = obj[prop];
    }
}
