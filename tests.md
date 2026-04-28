# Тестирование проекта

**Автор:** Бойцова Рада Ивановна


## 4. Инструкция по выкладыванию на GitHub

### Создание репозитория и загрузка проекта

```bash
# 1. Создайте папку проекта и перейдите в неё
mkdir random-password-generator
cd random-password-generator

# 2. Создайте файлы проекта (скопируйте код выше)
# password_generator.py
# .gitignore
# README.md

# 3. Инициализация Git
git init

# 4. Добавление файлов
git add .

# 5. Первый коммит
git commit -m "Initial commit: Random Password Generator with GUI, JSON and history"

# 6. Создайте репозиторий на GitHub (через веб-интерфейс)
# Название: random-password-generator

# 7. Привязка локального репозитория к удалённому
git remote add origin https://github.com/ВАШ_НИК/random-password-generator.git

# 8. Отправка кода на GitHub
git branch -M main
git push -u origin main

# 9. (Опционально) Добавление тега версии
git tag -a v1.0 -m "First stable release"
git push origin v1.0