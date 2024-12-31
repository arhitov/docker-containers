# docker-containers
Collection of docker containers

## Зависимости
- Python 3.10 и выше (включает `pkg_resources`)

## Структура
### Файл описывающий контейнер `container.yml`
```yaml
name: 'PHP CLI' # Имя контейнера.
type: 'application' # Тип контейнера.
choose: # Не обязательное. Описывает наличие версий контейнеров.
  question: 'Please select a version' # Не обязательное. Заголовок выбора.  
  list: # Список версий.
  - name: 'php-cli-8.2' # Имя версии. Если не указан `folder`, то имя является и именем каталога. 
    files: # Не обязательное. См. секция `files`. Список файлов конкретной версии, объединяется с глобальным списком.
    - file: 'php.ini'
      to: 'etc/php' 
extensions: # Не обязательное Список расширений.
  git: # Имя каталога расширения.
    name: 'Git' # Не обязательное. Имя расширения. Если не указано, то используется имя каталога. 
    folder: '../extensions/zip' # Не обязательное. Расположение расширения.
env: # Не обязательное. Список переменных окружения.
  - name: 'WWWUSER' # Имя переменной окружения.
    group: 'GLOBAL' # Не обязательное. Используется для группировки при сохранении в файл.
    default: 'www-data' # Не обязательное. Значение по умолчанию. 
folders: # Не обязательное. Список каталогов которые нужно создать.
  - patch: 'log/nginx' # 
    chmod: # Не обязательное. 
      mode: '0777' # Строка! Права в восьмеричном формате.
      owner: 'www-data' # Не обязательное. Не реализовано.
      group: 'www-data' # Не обязательное. Не реализовано.
files: # Не обязательное. См. секция `files`. Глобальный список.
  - file: 'Dockerfile'
    to: 'docker'
```

Секция `files`
```yaml
files: # Не обязательное. Список файлов которые будут скопированы или созданы.
  - file: 'example.ini' # Имя файла который будет создан. Если не указан `content`, то это имя является и именем файла откуда нужно копировать.
    to: 'example/files' # Не обязательное. Куда копировать (относительно целевого каталога). Если не указан, то копирование будет в целевой каталог.
    content: '...' # Не обязательное. Содержимое используемое для создания файла.
    folder: 'source/file' # Не обязательное. Путь где лежит исходный файл.
  - file: 'Dockerfile' # Для данного файла `content` заполняется автоматически.
    to: 'docker'
  - file: 'php.ini'
    to: 'etc/php'
  - file: 'nginx.conf'
    to: 'etc/nginx'
```