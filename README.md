# Проект парсинга документации Python и PEP

## Функции проекта

* Собирает ссылки на статьи о нововведениях в Python, переходит по ним и 
забирает информацию об авторах и редакторах статей.
* Собирает информацию о статусах версий Python.
* Скачивает архив с актуальной документацией Python.
* Анализирует статусы документов PEP.

## Стек технологий
* [Python](https://www.python.org/), 
[requests_cache](https://requests-cache.readthedocs.io/en/stable/), 
[BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/en/latest/), 
[argparse](https://docs.python.org/3/library/argparse.html), 
[tqdm](https://github.com/tqdm/tqdm)

## Как развернуть проект
1. Клонируйте репозиторий и перейдите в директорию bs4_parser_pep
```bash
git git@github.com:igorKolomitseff/bs4_parser_pep.git
cd bs4_parser_pep
```

2. Создать виртуальное окружение и его активировать:
```bash
python3 -m venv venv
source venv/bin/activate  # Для Linux и macOS
source venv/Scripts/activate  # Для Windows
```
3. Обновить pip и установить зависимости проекта:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. перейти в директорию src:
```bash
cd src/
```

Доступны следующие режимы работы:
 - Собрать информацию о нововведениях в версиях Python: 

```bash
python3 main.py whats-new
```

 - Собрать информацию о статусах версий Python:

```bash
python3 main.py latest-versions
```

 - Скачать архив с актуальной документацией Python:

```bash
python3 main.py download
```
Архив сохраняется в директории ~/bs4_parser_pep/src/downloads

 - Собрать информацию о статусах документов PEP:

```bash
python3 main.py pep
```

По умолчанию итоговая информация выводится в терминал:
[![asciicast](https://asciinema.org/a/8i1DbO8bJ3elfWlgbiPNW36Y1.svg)](https://asciinema.org/a/8i1DbO8bJ3elfWlgbiPNW36Y1)

С помощью опции -o (--output) можно указать дополнительные опции для вывода 
итоговой информации:
 - pretty: вывод данных в терминал в формате PrettyTable:
```bash
python3 main.py latest-versions --output pretty
```
[![asciicast](https://asciinema.org/a/zWvMw7LHRNiaZ6Qe7wBXLAcPG.svg)](https://asciinema.org/a/zWvMw7LHRNiaZ6Qe7wBXLAcPG)

 - file: сохраняет данные в файл в формате CSV:
```bash
python3 main.py latest-versions --output file
```
Файл сохраняется в директории ~/bs4_parser_pep/src/results


С помощью опции -c (--clear-cache) можно очистить кэш запросов к сайтам 
документации Python и PEP
```bash
 python3 main.py latest-versions --output pretty --clear-cache
```

### Автор

[Игорь Коломыцев](https://github.com/igorKolomitseff)