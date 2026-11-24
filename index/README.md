# Векторный индекс

Модель эмбеддингов [intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small),
384 измерения, работает локально на CPU. Документы кодируются с префиксом `passage: `, запросы с `query: `, так
обучена e5. В эмбеддинг чанка добавляется заголовок документа, чтобы чанк из середины статьи не терял, о ком он.

Чанки режет `RecursiveCharacterTextSplitter` из LangChain: 1 600 символов с перекрытием 240 (15%), сначала по
заголовкам разделов, потом по абзацам и предложениям. Хвосты короче 40 слов приклеиваются к предыдущему чанку.
На 35 документах из `knowledge_base/` получилось 235 чанков, от 42 до 274 слов, в среднем 175. Короче 100 слов
20 чанков, это концы коротких разделов, резать раздел пополам ради нормы я не стал.

Индекс FAISS `IndexIDMap2(IndexFlatIP)`: векторы нормализованы, поэтому скалярное произведение равно косинусу.
Обёртка с id нужна, чтобы при обновлении удалять чанки изменённого документа без пересборки.

Сборка занимает 8 секунд на M3 Pro, из них около 4 секунд загрузка модели. Первый запуск дольше, потому что модель
(~470 МБ) скачивается.

Файлы:

- `faiss.index` сам индекс;
- `chunks.json` метаданные по id чанка: `source` (файл), `title`, `section` (ближайший заголовок раздела, `intro` для
  вступления статьи), `chunk_index`, `start` (позиция в документе), `text`;
- `manifest.json` хеши документов на момент индексации.

Индекс обновляется инкрементально (`python update_index.py`, задание 6). Итоговое состояние после всех заданий:
34 файла и 221 чанк. Это 35 исходных статей, плюс `battle_of_corall.md`, добавленный при проверке обновления
(задание 6), минус три сущности, удалённые в задании 7, плюс `malicious.md` из задания 5 (его единственный чанк
в 7 слов короче всех остальных).

Полная сборка: `python build_index.py`, в конце три пробных запроса. Пример (score это косинус):

```
Q: Who trained Kaelen Vossar as a Novitiate?
  0.869 kaelen_vossar.md #1 [intro] A vergence in the Flux, Kaelen Vossar was born on the desert planet of Drysa in the Far Reach Territories in 4...
  0.845 kaelen_vossar.md #0 [intro] # Kaelen Vossar  Kaelen Vossar was a legendary Flux-sensitive human male who was a Aethari Knight of the Conco...
  0.841 tavin_vossar.md #1 [intro] The son of Aethari Knight Kaelen Vossar and Delegate Selene Corvane, Tavin Vossar was born along with his twin...
```
