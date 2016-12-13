class AdminSideBar {
  constructor() {
    this.DOM = {
      $sidebarToggle: $('.js-toggle-sidebar'),
      $header: $('.js-admin-header-wrapper'),
      $sidebarTree: $('#js-tree'),
      $sidebarLinks: $('#sidebar-links'),
    };

    this.localStorageKey = {
      isSidebarOpened: 'isSidebarOpened',
    };

    this.tableEditorPageUrl = '/admin/editor/?search_term=';
    this.getTreeItemsUrl = '/admin/get-tree-items/';
    this.scrollMagicRatio = 1.75;

    this.init();
  }

  init() {
    this.pluginsInit();
    this.setUpListeners();
  }

  pluginsInit() {
    this.jsTreeInit();
    this.slimScrollInit();
  }

  setUpListeners() {
    $(document).ready(() => this.setSidebarState());
    this.DOM.$sidebarToggle.click(() => {
      this.toggleSidebar();
      this.toggleSidebarLocalStorageState();
    });
    this.DOM.$sidebarTree.bind('state_ready.jstree',
      () => this.DOM.$sidebarTree.bind('select_node.jstree', this.redirectToEditPage));
    $(window).on('resize orientationChange', () => this.slimScrollReinit());
  }

  isSidebarOpened() {
    const sideBarState = localStorage.getItem(this.localStorageKey.isSidebarOpened);

    // Set sidebar state as open if page was loaded first time.
    if (sideBarState === null) {
      localStorage.setItem(this.localStorageKey.isSidebarOpened, 'true');
      return true;
    }

    return sideBarState === 'true';
  }

  setSidebarState() {
    // Sidabar is always opened on page load.
    if (!this.isSidebarOpened()) {
      this.toggleSidebar();
    }
  }

  toggleSidebarLocalStorageState() {
    localStorage.setItem(this.localStorageKey.isSidebarOpened, this.isSidebarOpened() ? 'false' : 'true');
  }

  toggleSidebar() {
    $('body').toggleClass('collapsed');
  }

  /**
   * https://www.jstree.com/
   */
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

  slimScrollReinit() {
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
