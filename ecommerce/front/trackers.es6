class Tracker {
  constructor(transport) {
    this.transport = transport;
  }
  track() {
    throw new Error('Track does not implemented');
  }
}

class YATracker extends Tracker {
  /**
   * Yandex analytics ecommerce tracker.
   * docs: https://yandex.ru/support/metrika/data/e-commerce.html
  **/
  constructor(transport, currencyCode) {
    super(transport);
    this.currencyCode = currencyCode;
  }
  detail(productsData) {
    this.track({detail: {products: productsData}});
  }
  add(productsData) {
    this.track({add: {products: productsData}});
  }
  remove(productsData) {
    this.track({remove: {products: productsData}});
  }
  purchase(productsData, actionData) {
    this.track({purchase: {products: productsData, actionField: actionData}});
  }
  track(data) {
    this.transport.push({
      ecommerce: Object.assign({currencyCode: this.currencyCode}, data),
    });
  }
}

class GATracker extends Tracker {
  /**
   * Google analytics ecommerce tracker.
   * docs: https://developers.google.com/analytics/devguides/collection/analyticsjs/ecommerce?hl=en
  **/
  constructor(transport, name) {
    super(transport);
    this.name = name;
  }
  purchase(productsData, txData) {
    this.track('addTransaction', txData);
    for (let data of productsData)
      this.track('addItem', data);
    this.track('send');
  }
  track(actionName, data) {
    this.transport(`${this.name}:${actionName}`, data);
  }
}


/**
 * Reliable loader of Google Analytics scripts.
 *
 * Google Analytics scripts (GA) are loading by the Google tag manager (GTM).
 * If GA is still not loaded, the function will delay execution until it is loaded.
 */
function loadGaTransport(onLoadName) {
  var state = {
    loaded: false,
    delayed: [],
  };

  let load = () => {
    ga('require', 'ecommerce');
    state.loaded = true;
  };

  try {
    load();
  } catch (e) {
    window.addEventListener(onLoadName, () => {
      load();
      // submit delayed transactions
      state.delayed.forEach((args) => ga(...args));
    });
  }

  return (...args) => {
    if (state.loaded) {
      ga(...args);
    } else {
      state.delayed.push(args);
    }
  };
}
