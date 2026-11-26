import unittest

import bot


class ResponseLanguageTests(unittest.TestCase):
    def test_russian_answer_passes(self):
        self.assertFalse(bot.answer_has_unwanted_language(
            "Сегодня хорошая погода, вечером будет прохладнее.",
            "Какая сегодня погода?",
        ))

    def test_one_or_two_english_words_in_russian_answer_pass(self):
        self.assertFalse(bot.answer_has_unwanted_language(
            "Пожалуйста, включите feature flag в настройках API.",
            "Как настроить функцию?",
        ))

    def test_technical_terms_brands_and_commands_pass(self):
        answer = (
            "Проверьте Telegram и GitHub, затем запустите llama.cpp "
            "с моделью DeepSeek-R1-Distill-Qwen-1.5B-Q4_0."
        )
        self.assertFalse(bot.answer_has_unwanted_language(answer, "Как проверить запуск?"))

    def test_english_names_are_not_rejected(self):
        self.assertFalse(bot.answer_has_unwanted_language(
            "Я смотрел доклад Will Smith для OpenAI.",
            "Кто выступал?",
        ))
        self.assertFalse(bot.answer_has_unwanted_language("Hello Kitty", "Что это?"))

    def test_fully_english_answer_is_rejected(self):
        self.assertTrue(bot.answer_has_unwanted_language(
            "I'm ready to help you with that.",
            "Помоги мне",
        ))

    def test_english_dominant_mixed_answer_is_rejected(self):
        self.assertTrue(bot.answer_has_unwanted_language(
            "Привет! I'm ready to help you.",
            "Представься",
        ))

    def test_short_english_majority_is_rejected(self):
        self.assertTrue(bot.answer_has_unwanted_language("Привет! I'm ready.", "Представься"))

    def test_cjk_and_hangul_are_checked_in_prose(self):
        self.assertTrue(bot.answer_has_unwanted_language("你好", "Привет"))
        self.assertTrue(bot.answer_has_unwanted_language("こんにちは", "Привет"))
        self.assertTrue(bot.answer_has_unwanted_language("안녕하세요", "Привет"))

    def test_code_and_technical_names_do_not_trigger_cjk_check(self):
        answer = "Строка " + chr(96) + "你好" + chr(96) + " передаётся в приложении 微信."
        self.assertFalse(bot.answer_has_unwanted_language(answer, "Что это за пример?"))

    def test_requested_foreign_language_is_allowed(self):
        self.assertFalse(bot.answer_has_unwanted_language(
            "I'm ready to help you.",
            "Напиши эту фразу на английском",
        ))
        self.assertFalse(bot.answer_has_unwanted_language(
            "你好",
            "Переведи фразу на китайский",
        ))

    def test_closed_reasoning_blocks_leave_final_text(self):
        answer = "<think>внутренний текст</think>Готовый ответ."
        self.assertEqual(bot.strip_internal_reasoning(answer), "Готовый ответ.")

    def test_reasoning_tags_inside_code_are_preserved(self):
        code = chr(96) + "<analysis>literal</analysis>" + chr(96)
        self.assertEqual(bot.strip_internal_reasoning("Пример: " + code), "Пример: " + code)

    def test_unclosed_reasoning_marker_does_not_truncate_answer(self):
        answer = "<analysis>Подготовка. Ответ: полезная информация."
        cleaned = bot.strip_internal_reasoning(answer)
        self.assertIn("полезная информация.", cleaned)


class _FakeMessage:
    def __init__(self, text):
        self.text = text
        self.chat = self
        self.replies = []

    async def send_action(self, action):
        return None

    async def reply_text(self, text):
        self.replies.append(text)


class _FakeApplication:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

        async def model_executor(messages):
            self.calls.append([dict(message) for message in messages])
            output = self.outputs.pop(0)
            if isinstance(output, Exception):
                raise output
            return output

        self.bot_data = {"model_executor": model_executor}

    def create_task(self, coroutine):
        return coroutine


class _FakeContext:
    def __init__(self, outputs):
        self.application = _FakeApplication(outputs)


class _FakeUpdate:
    def __init__(self, user_id, text):
        self.effective_user = type("User", (), {"id": user_id})()
        self.message = _FakeMessage(text)


class RetryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.user_id = 908172
        self.previous_history = [
            {"role": "user", "content": "Привет"},
            {"role": "assistant", "content": "Здравствуйте!"},
        ]
        bot.user_histories[self.user_id] = [dict(item) for item in self.previous_history]

    async def asyncTearDown(self):
        bot.user_histories.pop(self.user_id, None)

    async def test_retry_preserves_history_and_does_not_store_bad_answer(self):
        update = _FakeUpdate(self.user_id, "Как дела?")
        context = _FakeContext(
            ["I'm ready to help you.", "Хорошо, спасибо! Чем могу помочь?"]
        )
        await bot.handle_message(update, context)

        self.assertEqual(len(context.application.calls), 2)
        first, retry = context.application.calls
        self.assertEqual(first[1:-1], self.previous_history)
        self.assertEqual(retry[1:-1], self.previous_history)
        self.assertEqual(first[-1], retry[-1])
        self.assertNotIn("I'm ready to help you.", repr(retry))
        self.assertNotIn("I'm ready to help you.", repr(bot.user_histories[self.user_id]))
        self.assertNotIn("ДОПОЛНИТЕЛЬНО ДЛЯ ЭТОЙ ПОПЫТКИ", first[0]["content"])
        self.assertIn("ДОПОЛНИТЕЛЬНО ДЛЯ ЭТОЙ ПОПЫТКИ", retry[0]["content"])
        self.assertEqual(update.message.replies, ["Хорошо, спасибо! Чем могу помочь?"])

    async def test_second_invalid_answer_gets_user_facing_fallback_once(self):
        update = _FakeUpdate(self.user_id, "Расскажи подробнее")
        context = _FakeContext(["你好", "I'm ready to help you."])
        await bot.handle_message(update, context)

        self.assertEqual(len(context.application.calls), 2)
        self.assertEqual(len(update.message.replies), 1)
        fallback = update.message.replies[0]
        self.assertNotIn("провер", fallback.lower())
        self.assertNotIn("корректный ответ на русском", fallback.lower())
        self.assertEqual(bot.user_histories[self.user_id][-1]["content"], fallback)
        self.assertNotIn("你好", repr(bot.user_histories[self.user_id]))
        self.assertNotIn("I'm ready to help you.", repr(bot.user_histories[self.user_id]))


if __name__ == "__main__":
    unittest.main()
