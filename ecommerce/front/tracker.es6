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
    this.transport = transport;
    this.currencyCode = currencyCode;
  }
  detail(productsData) {
    this.transport.track({detail: {products: productsData}});
  }
  add(productsData) {
    this.transport.track({add: {products: productsData}});
  }
  remove(productsData) {
    this.transport.track({remove: {products: productsData}});
  }
  purchase(productsData, actionData) {
    this.transport.track({purchase: {products: productsData, actionField: actionData}});
  }
  track(data) {
    this.transport.push({
      ecommerce: {
        currencyCode: this.currencyCode,
        ...data,
      },
    });
  }
}

class GATracker extends Tracker {
  /**
   * Google analytics ecommerce tracker.
   * docs: https://developers.google.com/analytics/devguides/collection/analyticsjs/ecommerce?hl=en
  **/
  constructor(transport, name) {
    this.transport = transport;
    this.name = name;
  }
  purchase(txData, productsData) {
    this.transport('addTransaction', txData);
    for (let data of productsData)
      this.transport('addItem', data);
    this.transport('send');
  }
  track(actionName, data) {
    this.transport(`${this.name}:${actionName}`, data);
  }
}
