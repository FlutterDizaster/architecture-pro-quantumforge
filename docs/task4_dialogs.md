# Задание 4. Примеры диалогов

Получены консольным ботом (`python cli.py --steps`) на модели claude-haiku-5-5. Шаги это Chain-of-Thought из system-промпта.

## Как Dace Rennick получил Crimson Kestrel?

Шаги:

```
1. Ищу во фрагментах, как Dace Rennick получил Crimson Kestrel.
2. Во фрагменте [3] сказано, что Vashell владел Crimson Kestrel, а Dace выиграл корабль у Teodor Vashell в игре в tarrok после рейса Varn Run за двенадцать парсеков.
3. Фрагмент [4] подтверждает: Rennick выиграл корабль у Vashell в игре в tarrok вскоре после Varn Run.
4. Фрагмент [2] говорит, что позже Rennick вернул корабль у Nira и Jorel, но это не отвечает на вопрос о первом получении.
```

Ответ: Dace Rennick выиграл Crimson Kestrel у Teodor Vashell в игре в tarrok [3][4].

Источники: dace_rennick.md, crimson_kestrel.md; лучший score поиска 0.844

## Кто такая Selene Corvane?

Шаги:

```
1. Ищу во фрагментах, кто такая Selene Corvane.
2. Во фрагменте [1] она описана как человек-политик, женщина, представлявшая народ Лираэль в последние годы Конкордата миров, а до работы делегатом Галактической ассамблеи была выбранной правительницей Королевского дома Лираэль.
3. Во фрагменте [2] сказано, что она родилась как Selene Talvane в 46 BVC на Лираэль. Во фрагменте [1] сказано, что в 32 BVC она была избрана королевой и взяла регнальное имя «Corvane».
4. Вывод: Selene Corvane — политик с Лираэль, бывшая королева, которая родилась как Selene Talvane.
```

Ответ: Selene Corvane (родилась как Selene Talvane) — женщина-политик, представлявшая Лираэль в последние годы Конкордата миров и ставшая королевой Лираэль [1][2].

Источники: selene_corvane_talvane.md; лучший score поиска 0.819

## What happened to the planet Seravel?

Шаги:

```
1. I'm looking for what happened to the planet Seravel.
2. Fragment [1] says Seravel was destroyed when Grand Prefect Corvin Vessic tested the superlaser of the Void Core at full strength, because of the planet's ties with the League.
3. Fragment [1] also says a few people survived, including Princess Ilsa Marrow.
```

Ответ: Seravel was destroyed when Grand Prefect Corvin Vessic tested the full-strength superlaser of the Void Core, because of its ties with the League [1]. Among the few survivors was Princess Ilsa Marrow [1].

Источники: seravel.md; лучший score поиска 0.900

## Кто учил Odrin Halvane?

Шаги:

```
1. Ищу во фрагментах, кто обучал Odrin Halvane.
2. Во фрагменте [1] сказано, что Halvane изучал пути Потока и традиции Aethari под руководством Grand Master Morro.
3. Там же сказано, что он получил инструкции по бою на lumeblade от Aethari Master Ven Dallis, который обучал его базовым формам и техникам.
4. Во фрагменте [2] сказано, что в детстве Halvane был закреплён за Aethari Master Ardel Strosk. Фрагмент не говорит прямо, что Strosk его обучал, поэтому в ответ я его не включаю.
5. Вывод: известные из контекста учителя — Morro (Flux и традиции Aethari) и Ven Dallis (lumeblade).
```

Ответ: Odrin Halvane учился у Grand Master Morro в путях Потока и традициях Aethari [1], а навыкам боя на lumeblade его обучал Aethari Master Ven Dallis [1].

Источники: odrin_halvane.md; лучший score поиска 0.817

## Чем закончилась битва при Sylvar?

Шаги:

```
1. Ищу во фрагментах, чем закончилась битва при Sylvar.
2. Во фрагменте [1] сказано, что League to Restore the Concord сокрушила власть Dominion of Astra, VC-2 Void Core II был уничтожен, а Xarn Nocturne и Xarn Velgor погибли.
3. Во фрагменте [3] описан ход финала: Velgor убил Nocturne и погиб сам, после чего силы Free League уничтожили Void Core, а силы Dominion оказались в руинах.
4. Значит, битва закончилась победой League, крахом Dominion и уничтожением Void Core.
```

Ответ: Битва закончилась победой League to Restore the Concord: власть Dominion of Astra была сокрушена, VC-2 Void Core II уничтожен, а Xarn Nocturne и Xarn Velgor погибли [1][3].

Источники: battle_of_sylvar.md; лучший score поиска 0.850

## Who is Darth Vader?

Шаги:

```
1. Ищу во фрагментах упоминания Darth Vader.
2. Во фрагментах [1]–[5] встречаются Xarn Nocturne, Dace Rennick, Kaelen Vossar, Jask Morvain, но имени Darth Vader нет.
3. Фрагмент [3] упоминает Vossar, но это Kaelen Vossar, а не Darth Vader. Отождествлять их на основании имени нельзя.
4. В контексте нет сведений о Darth Vader.
```

Ответ: Я не знаю.

Источники: нет; лучший score поиска 0.800

## Как настроить Kafka consumer group?

Ответ: Я не знаю: в базе знаний нет информации по этому вопросу.

Источники: нет; поиск ничего не вернул выше порога 0.78, LLM не вызывалась
