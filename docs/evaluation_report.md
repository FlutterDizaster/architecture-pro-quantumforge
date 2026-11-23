# Отчёт автотеста по золотому набору

Прогон 2026-11-23T22:33:38+03:00, модель `claude-haiku-5-5`, эмбеддинги `intfloat/multilingual-e5-small`, чанков в индексе 221.

- Общая точность: 14/14 (100%).
- Известные темы: ответил верно 8/8, нужный документ в топ-5 (hit@5): 8/8, средняя полнота по ключевым словам 1.00.
- Удалённые и отсутствующие темы: корректный отказ 5/5.
- Побочные пробелы (факт ушёл вместе с удалённой сущностью): не выдумал 1/1.
- Ошибок выполнения: 0.

| Тип | Вопрос | Итог | Найдено в индексе (score) | Процитировано | Ответ |
|---|---|---|---|---|---|
| known | Кто обнаружил Kaelen Vossar? | ok | kaelen_vossar.md, ardel_strosk.md (0.832) | kaelen_vossar.md, ardel_strosk.md | Kaelen Vossar обнаружил Ardel Strosk, Aethari Master, на планете Drysa в 32 BVC [2][5]. |
| known | What happened to the planet Seravel? | ok | seravel.md, kryvel.md (0.9) | seravel.md | Seravel была уничтожена, когда Grand Prefect Corvin Vessic испытал на полной мощности суперлазер Void Core из-за связей планеты с League [1]. Среди немногих выж |
| known | Какой вид обитал на Kryvel? | ok | kryvel.md, battle_of_kryvel.md (0.818) | kryvel.md | На Kryvel обитали пятнадцать подвидов snowstriders и вид frostmaws, а разумной жизни там не было [1][2]. |
| known | Кто построил первый Void Core? | ok | vc_1_orbital_battle_station.md, league_to_restore_the_concord.md, battle_of_sylvar.md (0.81) | vc_1_orbital_battle_station.md, league_to_restore_the_concord.md | Первый Void Core построил Dominion of Astra. Изначальный проект создали Karrikans, а после падения Confederacy строительство перешло к Dominion [1][3]. |
| known | Кто был вторым пилотом Dace Rennick? | ok | dace_rennick.md (0.813) | dace_rennick.md | Вторым пилотом Dace Rennick был Grawlok, его доверенный копилот, связанный с ним клятвой жизненного долга [4]. |
| known | Who was Kaelen Vossar's secret wife? | ok | kaelen_vossar.md, morrak.md (0.875) | kaelen_vossar.md | Kaelen Vossar's secret wife was Delegate Selene Corvane of Lirael [1]. |
| known | Где находилась Frostpoint Base? | ok | battle_of_kryvel.md, kryvel.md (0.804) | kryvel.md, battle_of_kryvel.md | Frostpoint Base находилась на ледяной планете Kryvel, в секторе Velisk регион Far Reach Territories [2][4]. |
| side | Как Dace Rennick получил Crimson Kestrel? | ok | dace_rennick.md, crimson_kestrel.md (0.844) | dace_rennick.md, crimson_kestrel.md | В контексте не указано, как Dace Rennick впервые получил Crimson Kestrel: сказано только, что он стал его капитаном [1]. Позже он вернул корабль, забрав его у N |
| known | Кто был наставником Odrin Halvane? | ok | odrin_halvane.md (0.806) | odrin_halvane.md | Главным наставником Odrin Halvane был Aethari Master Ardel Strosk, который взял его в Novitiate [1][5]. Также его учили Grand Master Morro (Flux и традиции Aeth |
| removed | Что такое aurite crystal и где его добывают? | ok | — (0.0) | — | Я не знаю: в базе знаний нет информации по этому вопросу. |
| removed | Расскажи про планету Muirn | ok | drysa.md, grovath.md, seravel.md, lirael.md, xarn_nocturne.md (0.821) | — | Я не знаю. |
| removed | Who is Teodor Vashell? | ok | kaelen_vossar.md, tavin_vossar.md (0.806) | — | Я не знаю. |
| absent | Как подключиться к корпоративному VPN? | ok | — (0.0) | — | Я не знаю: в базе знаний нет информации по этому вопросу. |
| absent | Who won the 2022 FIFA World Cup? | ok | — (0.0) | — | Я не знаю: в базе знаний нет информации по этому вопросу. |

## Журнал запросов

Всего запросов в журнале: 14 (eval: 14), без ответа: 5, из них отклонено защитой: 1, поиск ничего не нашёл: 3; запросов, где из выдачи отброшен подозрительный чанк: 1.

Документы, которые чаще всего оказываются первыми в выдаче у запросов без ответа:

- `drysa.md`: 1
- `kaelen_vossar.md`: 1
