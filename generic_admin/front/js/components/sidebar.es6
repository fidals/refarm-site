class SideBar{
  constructor() {
    this.DOM = {
      $sidebarToggle: $('.js-toggle-sidebar'),
      $header: $('.js-admin-header-wrapper'),
      $sidebarTree: $('#js-tree'),
      $sidebarLinks: $('#sidebar-links'),
    };

    this.localStorageKey = {
      isSidebarOpen: 'isSidebarOpen',
    };

    this.tableEditorPageUrl = '/admin/editor/?search_term=';
    this.getTreeItemsUrl = '/admin/get-tree-items/';
    this.scrollMagicRatio = 1.75;

    this.init();
  }

  init() {
    this.setSidebarState();
    this.pluginsInit();
    this.setUpListeners();
  }

  setUpListeners() {
    this.DOM.$sidebarToggle.click(this.toggleSidebar);
    this.DOM.$sidebarTree.bind('state_ready.jstree',
      () => this.DOM.$sidebarTree.bind('select_node.jstree', this.redirectToEditPage));
    $(window).on('resize orientationChange', this.slimScrollReInit);
  }

  pluginsInit() {
    this.jsTreeInit();
    this.slimScrollInit();
  }

  /**
   * Check sidebar stored state.
   */
  isSidebarOpen() {
    return localStorage.getItem(this.localStorageKey.isSidebarOpen) === 'true';
  }

  /**
   * Set sidebar state depending on stored key.
   */
  setSidebarState() {
    if (!this.isSidebarOpen()) {
      this.toggleSidebar();
    }
  }

  toggleSidebar() {
    $('body').toggleClass('collapsed');
    localStorage.setItem(this.localStorageKey.isSidebarOpen, this.isSidebarOpen() ? 'false' : 'true');
  }

  jsTreeInit() {
    this.DOM.$sidebarTree
      .jstree({
        core: {
          data: {
            url: this.getTreeItemsUrl,
            dataType: 'json',
            data(node) {
              return node.id === '#' ? false : { id: node.id };
            },
          },
          check_callback: true,
        },
        plugins: ['contextmenu', 'state'],
        contextmenu: {
          items: {
            'to-tableEditor': {
              separator_before: false,
              separator_after: false,
              label: 'Table Editor',
              icon: 'fa fa-columns',
              action: (data) => {
                window.location.assign(this.tableEditorPageUrl +
                  $(data.reference[0]).attr('search-term'));
              },
              _disabled(obj) {
                const $referenceParent = $(obj.reference).parent();
                return !($referenceParent.hasClass('jstree-leaf') ||
                         $referenceParent.find('ul:first').find('li:first')
                         .hasClass('jstree-leaf'));
              },
            },
            'to-site-page': {
              separator_before: false,
              separator_after: false,
              label: 'На страницу',
              icon: 'fa fa-link',
              action: data => {
                window.location.assign($(data.reference[0]).attr('href-site-page'));
              },
            },
          },
        },
      });
  }

  redirectToEditPage(_, data) {
    if (data.event.which === 1) {
      const path = $(data.event.target).attr('href-admin-page');
      if (path !== window.location.pathname) {
        window.location.assign(path);
      }
    }
  }

  slimScrollReInit() {
    this.DOM.$sidebarTree.slimScroll({
      destroy: true,
    });

    this.slimScrollInit();
  }

  slimScrollInit() {
    const scrollHeight =
      $(window).outerHeight()
      - (this.scrollMagicRatio * this.DOM.$header.outerHeight())
      - this.DOM.$sidebarLinks.outerHeight();

    this.DOM.$sidebarTree.slimScroll({
      height: `${scrollHeight}px`,
    });
  }
}
