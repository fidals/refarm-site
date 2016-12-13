class TableEditorDialogBoxes {
  constructor() {
    this.modalToDeleteProduct = {
        $: $('#confirm-modal'),
        $acceptBtn: $('.js-modal-delete'),
        $cancelBtn: $('.js-modal-delete-cancel'),
        $textField: $('#product-to-remove'),
        deleteProductBtnClass: 'js-confirm-delete-modal',
    };

    // https://goo.gl/TzEvoR
    this.popover = {
      className: '#popover',
      settings: {
        animation: 'pop',
        backdrop: true,
        closeable: true,
        content: 'Content',
        placement: 'top',
        title: 'Title',
        width: 300,
      },
    };

    this.init();
  }

  init() {
    this.setUpListeners();
  }

  setUpListeners() {
    $(document).on('click', `.${this.modalToDeleteProduct.deleteProductBtnClass}`, (event) => {
      this.showModal(
        event, this.modalToDeleteProduct.$, this.modalToDeleteProduct.$textField);
    });

    $(document).on('keyup', event => {
      const escapeBtnKeyCode = 27;
      if (event.which === escapeBtnKeyCode) {
        this.closeModal(event, this.modalToDeleteProduct.$);
      }
    });

    this.modalToDeleteProduct.$cancelBtn.click((event) => {
      this.closeModal(event, this.modalToDeleteProduct.$);
    });
  }

  /**
   * Extend jQgrid formatter.
   * Render html for Product removing icon.
   * @link http://goo.gl/9xcr7q
   */


  showModal(event, $modal, $textField, text = 'this product') {
    event.stopImmediatePropagation();

    $textField.text(text);
    $modal.addClass('modal-show');
  }

  closeModal(event, $modal) {
    event.stopImmediatePropagation();
    $modal.removeClass('modal-show');
  }

  showPopover($currentRow, colName, message) {
    const offset = $currentRow
      .find(`td[aria-describedby="jqGrid_${colName}"]`)
      .offset();

    const extendedSettings = $.extend(
      {}, this.popover.settings, {
        content: message,
        offsetTop: offset.top,
        offsetLeft: offset.left + (this.popover.settings.width / 2),
        title: 'Error',
      });
    $(`${this.popover.className}`).webuiPopover('destroy').webuiPopover(extendedSettings);
    WebuiPopovers.show(`${this.popover.className}`);
  }
}
