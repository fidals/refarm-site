/**
 * Class for handle user backcall request.
 */
class Backcall {
  constructor(sendBtnClass, url) {
    this.sendBtnClass = sendBtnClass || 'js-send-backcall';
    this.url = url || '/shop/order-backcall/';

    this.$sendBtn = $(`.${this.sendBtnClass}`);
    this.inputFields = $('.js-backcall-field');
    this.successMessage = 'Backcall request has been send.';
    this.$sendBtn.click(() => this.orderCall());
  }

  orderCall() {
    if (!this.isValid()) return;

    const orderData = this.getOrderData();
    this.disableButton();

    this.sendOrderData(orderData)
      .success(() => {
        this.sendOrderCallback();
      })
      .fail(error => console.warn('Backcall request failed.', error));
  }

  disableButton() {
    this.$sendBtn.attr('disabled', true);
  }

  getOrderData() {
    const fields = {};

    this.inputFields.each((_, item) => {
      fields[$(item).attr('id')] = $(item).val();
    });

    fields.url = location.href;

    return fields;
  }

  sendOrderData(orderData) {
    return $.post(this.url, { orderData });
  }

  sendOrderCallback() {
    console.info(this.successMessage);
  }

  static isValid() {
    return true;
  }
}
