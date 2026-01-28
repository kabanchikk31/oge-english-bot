async def process_answer(callback_query: types.CallbackQuery):
    data = callback_query.data.split("|")
    qid = int(data[1])
    choice = data[2]  # 'a'/'b'/'c'/'d'
    user_id = callback_query.from_user.id

    # Получаем правильный ответ и объяснение
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT question,a,b,c,d,correct,explanation FROM questions WHERE id=?", (qid,))
    row = c.fetchone()
    conn.close()
    if not row:
        await bot.answer_callback_query(callback_query.id, "Вопрос не найден.")
        return
    question, a,b,c,d, correct, explanation = row
    is_correct = (choice == correct)
    record_answer(user_id, qid, choice, is_correct)

    if is_correct:
        res_text = "✅ Правильно!"
    else:
        res_text = f"❌ Неправильно. Правильный ответ: {correct.upper()}."

    res_text += f"\n\n{explanation}"

    # Кнопки: Следующий вопрос / В меню
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("Следующий", callback_data=f"next|{qid}"),
        types.InlineKeyboardButton("В меню", callback_data="menu|back")
    )
    await bot.send_message(user_id, res_text, reply_markup=kb)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("next|"))
async def process_next(callback_query: types.CallbackQuery):
    # Показать следующий вопрос той же темы, исключив уже отвеченные
    user_id = callback_query.from_user.id
    # Узнаём тему текущего вопроса
    prev_qid = int(callback_query.data.split("|",1)[1])
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT topic FROM questions WHERE id=?", (prev_qid,))
    row = c.fetchone()
    if not row:
        await bot.answer_callback_query(callback_query.id, "Ошибка: вопрос не найден.")
        conn.close()
        return
    topic = row[0]
    # Получить answered ids
    c.execute("SELECT question_id FROM user_answers WHERE user_id=?", (user_id,))
    answered = [r[0] for r in c.fetchall()]
    conn.close()
    q = get_random_question_by_topic(topic, exclude_ids=answered)
    if not q:
        await bot.answer_callback_query(callback_query.id, "В этой теме больше нет новых вопросов.")
        await bot.send_message(user_id, "В этой теме вопросов больше нет. Можешь выбрать другую тему или начать сначала (/menu).")
        return
    qid, question, a,b,c,d,correct,explanation = q
    current_questions[user_id] = qid
    text = f"Тема: {topic}\n\n{question}\n\nA) {a}\nB) {b}\nC) {c}\nD) {d}"
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("A", callback_data=f"answer|{qid}|a"),
        types.InlineKeyboardButton("B", callback_data=f"answer|{qid}|b"),
        types.InlineKeyboardButton("C", callback_data=f"answer|{qid}|c"),
        types.InlineKeyboardButton("D", callback_data=f"answer|{qid}|d")
    )
    await bot.send_message(user_id, text, reply_markup=kb)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("menu|"))
async def process_menu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Возврат в меню. Выбери режим:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("📚 Практика")))
    await bot.answer_callback_query(callback_query.id)

if name == "__main__":
    print("Bot polling started...")
    executor.start_polling(dp, skip_updates=True)
