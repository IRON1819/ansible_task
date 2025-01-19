# ansible_task
## Задание
Objective: Use Ansible to deploy a typical application server stack on Ubuntu 24.04. The stack should include:

Django + Django REST Framework for the application layer.
PostgreSQL as the database.
nginx as a reverse proxy in front of Django.
Additional Requirement:
Implement a basic REST API endpoint (GET /healthcheck/) in the Django application to return JSON indicating the operational status of nginx, Django, and PostgreSQL.

Requirements:

The Ansible playbook must be idempotent.
All steps should be documented.
Provide instructions for running the playbook and verifying component statuses via /healthcheck/.

## Решение
Структура ansible плэйбука следующая:
```shell
.
├── ansible.cfg
├── group_vars
│   └── all
├── hosts
├── host_vars
│   └── host1
├── main_playbook.yml
└── roles
    ├── Django
    │   ├── files
    │   │   └── views.py
    │   └── tasks
    │       └── main.yml
    ├── Gunicorn
    │   ├── tasks
    │   │   └── main.yml
    │   └── templates
    │       ├── gunicorn.service.j2
    │       └── gunicorn.socket.j2
    ├── Nginx
    │   ├── handlers
    │   │   └── main.yml
    │   ├── tasks
    │   │   └── main.yml
    │   └── templates
    │       └── reverse_proxy.j2
    └── Postgresql
        └── tasks
            └── main.yml
```
В файле gpoup_vars/all содержатся общие переменные для всех групп, в файле host_vars/host1 - для конкретного хоста. 
Файл hosts - inventory файл.
main_playbook.yml - основновной плэйбук, содержит следующие:
```yml
---
# Название плэйбука и указание к каким хостам будет применен
- name: Main playbook
  hosts: local_group
# Предварительные задачи, выполняемые перед ролями
  pre_tasks:
# Получение списка последних доступных пакетов из репозитория 
    - name: Update cache
      ...
# Установка всех необходимых пакетов
    - name: install dependences
      ...
# Установка python библиотек в виртуальное окружение
    - name: install python libraries in a virtual environment
      ...
# Вызов и выполнение ролей
  roles:
    ...
```
Роль Django содержит файл file/views.py с кодом веб приложения, и файл tasks/main.yml со следующим содержанием:
```yml
---
# Создание рабочей директории 
- name: make work directory for project
  ...
# Инициализация django проекта
- name: initialize django project
  ...
# Следующие 2 таска конфигурируют файл settings.py для указания хостов для подключения и настроек для подключения к бд
- name: Configurate allowed hosts in settings.py
  ...
- name: Configuration the database connection in settings.py
  ...
# Следующие 2 таска настраивают подключение и добавления маршрута endpoint в файл urls.py
- name: Add import of endpoint in urls.py
  ...
- name: Add route of endpoint in urls.py
  ...
# Копирование оновного файла с веб приложением на конечный хост
- name: Copy views.py
  ...
# Создание и принятие миграций с бд
- name: make and apply migrations
  ...
```
Роль Gunicorn содержит 2 jinja шаблона для создания сокета и службы application сервера и файл со следующими tasks:
```yml
---
# Копирование шаблонных файлов сокета и демона на конечную машину
- name: Upload configuration of gunicorn socket and gunicorn daemon
  ...
# Запуск демона gunicorn
- name: Start the gunicorn daemon
  ...
```
Роль Nginx содержит jinja шаблон настройки прокси и файлы tasks/main.yml и обработчик handlers/main.yaml.
tasks/main.yml:
```yml
---
# Блок всех задач, которым повышаются привилегии 
- name: Configure nginx
  become: yes
  block:
# Запуск nginx
    - name: Start nginx
      ...
# Загрузка конфигурации прокси на хост
    - name: Upload configuration of reverse proxy
      ...
    notify: Restart nginx  # Вызов обработчика для перезагрузки nginx на случай, если конфиг изменится
# Создание символической ссылки конфига из sites-available в sites-enabled
    - name: Create the symbolic link in sites-enabled
      ...
```
handlers/main.yaml:
```yml
---
# Handler для перезагрузки nginx 
- name: Restart nginx
```
Роль Postgresql содержит файл с tasks:
```yml
---
# Запуск postrgresql
- name: Start postgresql
  ...
# Блок конфигурации postgresql с выполнением от юзера postgres для успешной peer аутентификации
- name: Configure postgresql
  become: yes
  become_user: postgres
  block:
# Создание базы данных
    - name: Create database
      ...
# Создание роли
    - name: Create role
      ...
# Выдача привелегий созданной роли на созданную бд
    - name: Grant priveleges
      ...
```
## Использование
Для запуска плейбука необходимо склонировать данный проект командой git clone https://github.com/IRON1819/ansible_task  
Далее настроить inventory файл и файлы с переменными host_vars/* и group_vars/* под свою систему (например, для теста можно использовать localhost).   Запустить playbook командой:  
```shell
 ansible-playbook main_playbook.yml -K
```  
В поле become password: ввести пароль для повышения привилегий.  
Для проверки работоспособности /healthcheck в браузере в адресную строку введите htttp://<Ваш ip адрес>/healthcheck (без < >)
