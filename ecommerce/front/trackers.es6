// Got these names from SEO department.
const eventNames = {
  detail: 'Detail',
  add: 'addToCart',
  remove: 'removeFromCart',
  purchase: 'Purchase',
}

class YATracker {
  /**
   * Yandex analytics ecommerce tracker.
   * docs: https://yandex.ru/support/metrika/data/e-commerce.html
  **/
  constructor(transport, currencyCode) {
    this.transport = transport;
    this.currencyCode = currencyCode;
  }
  detail(productsData) {
    this.track('detail', {products: productsData});
  }
  add(productsData) {
    this.track('add', {products: productsData});
  }
  remove(productsData) {
    this.track('remove', {products: productsData});
  }
  purchase(productsData, actionData) {
    this.track('purchase', {products: productsData, actionField: actionData});
  }
  track(event, data) {
    let payload = {};
    payload[event] = data;
    this.transport.push({
      event: eventNames[event],
      ecommerce: Object.assign({currencyCode: this.currencyCode}, payload),
    });
  }
}
