[![PDD status](http://www.0pdd.com/svg?name=fidals/refarm-site)](http://www.0pdd.com/p?name=fidals/refarm-site)


# Refarm
*bunch of ecommerce django apps* 

Стандартный функционал для интернет-магазина на Django.
Для создания собственного магазина достаточно переиспользовать Django apps из этого проекта.
Предназначен для внутреннего пользования.

Репозиторий открыт для знакомства с кодом и процессом разработки команды [Фидалс](https://fidals.com)
На текущий момент команда Фидалс использует Рефарм для сайтов [shopelectro](https://github.com/fidals/shopelectro) и [stroyprombeton](https://github.com/fidals/stroyprombeton). 

## Глоссарий

### Общее для тематики разработки сайтов

**Сквозные элементы (сквозняки)** - элементы, которые есть на каждой странице сайта.
Обычно это меню с товарами, верхняя (хедер) и нижнаяя (футер) части сайтов.

**Хлебные крошки (breadcrumbs)** - список предков текущего элемента.
Есть category page и product page вверху страницы.

**Хедер (header, шапка)** - верхняя сквозная часть сайта.

**Футер (footer, подвал)** - нижняя сквозная часть сайта.

**Контрол (control)** - любой элемент на странице, с которым юзер может взаимодейстовать.
Кнопки, галочки, области со всплывающими элементами. 
 
**Статика** - любые файлы, которые генерируются из кода или данных базы.
Бывает фронтовая статика, сайтмапы, yml files.

**Сайтмап (sitemap)** - файл со всеми страницами сайта.

**yml file (yml price, прайсы)** - [пример файла](https://www.shopelectro.ru/static/yandex.yml) (3.6 MB).
Файлы с нашими товарами для маркет-плейсов. Например Я.Маркет или Гугл мерчант.
Являются статикой.

**Роботс (robots.txt)** - настройки для поисковых машин, которые захаживают на наш сайт.
Хранятся в файле robots.txt в корне сайта.


### Каталог

[Модуль каталог](https://github.com/fidals/refarm-site/tree/master/catalog)

**Категория (category)** - раздел, в котором хранятся или другие разделы или товары.
Категории представляют из себя дерево.

**Корневая категория (root category)** - категория, которая не имеет родителей.
Обычно такие отображаются в сквозных меню.

**Категория второго уровня (second level category)** - категория, у которой только один предок - корневая категория.
В общем случае "картегория уровня n" - это категория, которая имеет n предков.
 
**Листовая категория (leaf category)** - категория, у которой потомки - товары.
По аналогии с листовыми элементами графов-деревьев.

**Смотреть ещё (watch more)** - непрерывный список товаров.
Под последней строкой товара помещаем кнопку "смотреть ещё".
Когда юзер жмёт кнопку, фронт догружает доп список элементов вниз той же страницы.
Возможен вариант с автодогрузкой:
когда юзер доскроллил до конца экрана,
фронт автоматом догружает новые элементы списка.

**Пагинация (pagination)** - список ссылок на номера страниц.
Из-за сомнительного юзабилити применяем только для СЕО.
На каждой странице свой уникальный набор товаров (элементов списка).
Один и тот же товар *не может находиться на разных страницах*.

**Теги (tags, мультисвойства)** - характеристики товаров.
`Напряжение 12В` - это тег товара.
Тегом является пара `имя группы тега`+`значение тега`. Например `Напряжение`+`12В`.
Товары можно фильтровать по тегам на category page.

**Группа тегов (tag group)** - это группа характеристик.
Из примера выше `Напряжение` - это группа тегов.
`Напряжение 12В` - это уже конкретный тег.

### Админка

[Модуль generic_admin](https://github.com/fidals/refarm-site/tree/master/generic_admin)

**Табличный редактор (Table editor)** - [линк на него](http://www.stroyprombeton.ru/admin/editor/).
Позволяет редактировать товары прямо в списке просмотра, как в excel.

### Контент

[Модуль pages](https://github.com/fidals/refarm-site/tree/master/pages)

**Страница (Page)** - любая страница на сайте. Имеет уникальный урл.
Важное правило - для одной страницы ровно один урл

**[Some] page** - тип страницы или "экран".
Например main page, admin page и тд. Полный список страниц [смотри ниже](#refarms-documentation).

**Page template (сео-шаблон)** - шаблон на django template language, который можно записать прямо через Админку в базу.
Можно изменять правила отображения контента в зависимости от выбранного тега.
Например для "Батарейки" можно отображать один текст, а для "Батарейки 12В" - другой.
Часто используем для tag pages. Подробнее описан [в модуле pages](https://github.com/fidals/refarm-site/tree/master/pages). 

### Список типов страниц
- Flat page, `/pages/*` - обычная страница.
Не имеет никакого функционала - только отображает контент, который добавили в неё через Админку.
Например "Контакты" или "Гарантии и возврат".
- Custom page, `/*` - такие страницы использует внутренняя логика сайта.
Если её не будет в базе, сайт будет некорректно отображаться.
Примеры custom page: main page, order page, admin page. 
- Model page - любая страница, данные которой хранятся не в самой сущности страницы.
Category page и product page - примеры model page.

- Admin page, `/admin/*` - любая страница Админки, включая главную - /admin.
- Table editor page

- Category page `/catalog/categories/*` - страница категории.
Категория-элемент каталога (Category) в базе связана с Категорией-страницей (Category page).
В Админке мы можем редактировать Категорию-страницу. Но её форму включены и поля Категории-элемента каталога. 
- Product page `/catalog/products/*` - аналогично Category page.
- Tag page `/catalog/categories/*/tags/*/` - [пример](https://www.shopelectro.ru/catalog/categories/bloki-pitaniia-288/tags/0-3-a/).
Страница категории, отфильтрованная по одному или нескольким тегам.
Каждая tag page может иметь свои тексты, h1 и прочие поля (все есть в Админке).

- Order page `/shop/order/*` - страница с корзиной и формой заказа.
- Search page - страница с выдачей поиска по сайту.
