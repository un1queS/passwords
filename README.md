Генератор паролей

Простой генератор паролей на Flask.

Установка и запуск

```bash
# Клонировать репозиторий
git clone https://github.com/your-username/password-generator.git
cd password-generator

# Установить зависимости
pip install flask

# Запустить приложение
python app.py
```

Перейдите по адресу: http://localhost:5000

Использование

1. Укажите длину пароля
2. Выберите типы символов:
   · Заглавные буквы (A-Z)
   · Строчные буквы (a-z)
   · Цифры (0-9)
   · Специальные символы
3. Нажмите "Сгенерировать пароль"

Структура

```
password-generator/
├── app.py              # Flask приложение
├── templates/
│   └── index.html      # HTML шаблоны
│   └── login.html
│   └── register.html
├── static/
│   └── style.css       # Стили
└── README.md
```
Скриншот сайта
<img width="729" height="837" alt="image" src="https://github.com/user-attachments/assets/4c5fd6d8-5889-45fb-9b89-a2b3095f517a" />

