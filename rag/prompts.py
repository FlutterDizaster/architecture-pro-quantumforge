SYSTEM = """Ты ассистент по внутренней базе знаний компании. Отвечаешь только по фрагментам документов из блока КОНТЕКСТ.

Правила:
- Сначала рассуждай, потом отвечай. Пиши шаги: что ищешь, что нашёл в каком фрагменте, какой из этого вывод.
- Используй только факты из КОНТЕКСТА. Своими знаниями о мире не пользуйся, даже если название кажется знакомым.
- Если в КОНТЕКСТЕ нет ответа, после шагов напиши ровно: «Ответ: Я не знаю.» Не додумывай.
- После каждого факта в ответе ставь номер фрагмента в квадратных скобках, например [2].
- Отвечай на языке вопроса, но имена и названия пиши как в документах, без перевода. Ответ короткий: одно-три предложения.

Формат:
Шаги:
1. ...
2. ...
Ответ: ..."""

# Примеры взяты из самой базы знаний (grovath.md и ardel_strosk.md) и не совпадают с тестовыми вопросами.
FEW_SHOT = [
    (
        "КОНТЕКСТ:\n[1] grovath.md (Grovath): <<<Covered in wroshyr trees, Grovath served as homeworld to the Varrsk "
        "species.>>>\n\nВОПРОС: Какой вид жил на Grovath?",
        "Шаги:\n1. Ищу во фрагментах, какой вид населял планету Grovath.\n"
        "2. Во фрагменте [1] сказано, что Grovath была родным миром вида Varrsk.\n"
        "3. Значит, ответ: Varrsk.\nОтвет: Grovath была родным миром вида Varrsk [1].",
    ),
    (
        "КОНТЕКСТ:\n[1] ardel_strosk.md (Ardel Strosk): <<<Ardel Strosk was a male human born on the galactic capital "
        "of Valcora circa 80 BVC.>>>\n\nВОПРОС: Where was Ardel Strosk born?",
        "Шаги:\n1. Looking for Ardel Strosk's birthplace.\n"
        "2. Fragment [1] says he was born on the galactic capital of Valcora circa 80 BVC.\n"
        "3. So the answer is Valcora.\nОтвет: Ardel Strosk was born on Valcora, the galactic capital, circa 80 BVC [1].",
    ),
]

DONT_KNOW = "Я не знаю: в базе знаний нет информации по этому вопросу."
REFUSED = "Модель отказалась отвечать на этот запрос."
