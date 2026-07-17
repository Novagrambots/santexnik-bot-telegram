"""Простой словарный i18n. t(key, lang, **kwargs) -> str."""

TEXTS: dict[str, dict[str, str]] = {
    # --- Общее / регистрация ---
    "choose_lang": {
        "ru": "Выберите язык / Tilni tanlang:",
        "uz": "Tilni tanlang / Выберите язык:",
    },
    "ask_name": {
        "ru": "Здравствуйте! Как вас зовут? Напишите имя.",
        "uz": "Assalomu alaykum! Ismingiz nima? Ismingizni yozing.",
    },
    "ask_phone": {
        "ru": "Отправьте номер телефона кнопкой ниже.",
        "uz": "Quyidagi tugma orqali telefon raqamingizni yuboring.",
    },
    "btn_share_phone": {
        "ru": "📱 Отправить номер",
        "uz": "📱 Raqamni yuborish",
    },
    "registered": {
        "ru": "Готово, {name}! Теперь добавьте своё оборудование, чтобы получать напоминания о профилактике.",
        "uz": "Tayyor, {name}! Endi profilaktika eslatmalarini olish uchun jihozingizni qo‘shing.",
    },
    "main_menu": {
        "ru": "Главное меню:",
        "uz": "Asosiy menyu:",
    },
    # --- Кнопки главного меню ---
    "btn_my_equipment": {"ru": "🔧 Моё оборудование", "uz": "🔧 Mening jihozlarim"},
    "btn_add_equipment": {"ru": "➕ Добавить оборудование", "uz": "➕ Jihoz qo‘shish"},
    "btn_call_master": {"ru": "🧰 Вызвать мастера", "uz": "🧰 Usta chaqirish"},
    "btn_emergency": {"ru": "🚨 Аварийная заявка", "uz": "🚨 Favqulodda ariza"},
    "btn_contacts": {"ru": "📞 Контакты", "uz": "📞 Kontaktlar"},
    "btn_my_bonuses": {"ru": "💰 Мои бонусы", "uz": "💰 Mening bonuslarim"},
    "btn_change_lang": {"ru": "🌐 Язык", "uz": "🌐 Til"},
    # --- Виды оборудования (коды -> локализованные названия) ---
    "kind_boiler": {"ru": "Котёл", "uz": "Qozon"},
    "kind_water_heater": {"ru": "Бойлер", "uz": "Bo‘yler"},
    "kind_water_filter": {"ru": "Фильтр воды", "uz": "Suv filtri"},
    "kind_pump": {"ru": "Насос", "uz": "Nasos"},
    "kind_radiators": {"ru": "Радиаторы", "uz": "Radiatorlar"},
    # --- Оборудование ---
    "ask_kind": {
        "ru": "Какое оборудование? Выберите или напишите свой вариант.",
        "uz": "Qaysi jihoz? Tanlang yoki o‘zingiznikini yozing.",
    },
    "btn_kind_other": {"ru": "✏️ Другое (напишу сам)", "uz": "✏️ Boshqa (o‘zim yozaman)"},
    "ask_kind_custom": {
        "ru": "Напишите название вашего оборудования:",
        "uz": "Jihozingiz nomini yozing:",
    },
    "ask_model": {
        "ru": "Модель оборудования? Можно пропустить.",
        "uz": "Jihoz modeli? O‘tkazib yuborish mumkin.",
    },
    "btn_skip": {"ru": "Пропустить", "uz": "O‘tkazib yuborish"},
    "ask_install_date": {
        "ru": "Дата установки в формате ДД.ММ.ГГГГ (например 15.03.2024):",
        "uz": "O‘rnatilgan sana KK.OO.YYYY formatida (masalan 15.03.2024):",
    },
    "bad_date": {
        "ru": "Не понял дату. Формат: ДД.ММ.ГГГГ, например 15.03.2024.",
        "uz": "Sana tushunarsiz. Format: KK.OO.YYYY, masalan 15.03.2024.",
    },
    "ask_period": {
        "ru": "Как часто нужна профилактика?",
        "uz": "Profilaktika qanchalik tez-tez kerak?",
    },
    "period_6": {"ru": "Раз в 6 месяцев", "uz": "6 oyda bir marta"},
    "period_12": {"ru": "Раз в год", "uz": "Yiliga bir marta"},
    "equipment_added": {
        "ru": "✅ Добавлено: {kind}. Следующая профилактика: {date}.",
        "uz": "✅ Qo‘shildi: {kind}. Keyingi profilaktika: {date}.",
    },
    "no_equipment": {
        "ru": "У вас пока нет оборудования. Нажмите «Добавить оборудование».",
        "uz": "Sizda hali jihoz yo‘q. «Jihoz qo‘shish» tugmasini bosing.",
    },
    "equipment_item": {
        "ru": "🔧 {kind}{model}\nПрофилактика: {date}",
        "uz": "🔧 {kind}{model}\nProfilaktika: {date}",
    },
    "btn_delete": {"ru": "🗑 Удалить", "uz": "🗑 O‘chirish"},
    "equipment_deleted": {"ru": "Оборудование удалено.", "uz": "Jihoz o‘chirildi."},
    # --- Напоминания ---
    "reminder_soon": {
        "ru": "🔔 Напоминание!\nЧерез {days} дн. плановая профилактика: {kind}{model}.\nДата: {date}.\nПора записаться?",
        "uz": "🔔 Eslatma!\n{days} kundan so‘ng rejali profilaktika: {kind}{model}.\nSana: {date}.\nYozilasizmi?",
    },
    "reminder_today": {
        "ru": "🔔 Сегодня плановая профилактика: {kind}{model}.\nЗапишитесь на удобное время.",
        "uz": "🔔 Bugun rejali profilaktika: {kind}{model}.\nQulay vaqtga yoziling.",
    },
    "btn_book": {"ru": "✅ Записаться", "uz": "✅ Yozilish"},
    "btn_done": {"ru": "☑️ Уже сделал", "uz": "☑️ Bajarildi"},
    "btn_postpone": {"ru": "⏳ Перенести", "uz": "⏳ Kechiktirish"},
    "booked": {
        "ru": "Заявка принята! Мастер свяжется с вами.",
        "uz": "Ariza qabul qilindi! Usta siz bilan bog‘lanadi.",
    },
    "marked_done": {
        "ru": "Отлично! Следующая профилактика: {date}.",
        "uz": "Zo‘r! Keyingi profilaktika: {date}.",
    },
    "postpone_ask": {
        "ru": "На сколько перенести?",
        "uz": "Qanchaga kechiktiramiz?",
    },
    "postpone_7": {"ru": "+7 дней", "uz": "+7 kun"},
    "postpone_30": {"ru": "+30 дней", "uz": "+30 kun"},
    "postponed": {
        "ru": "Перенесено. Напомним снова: {date}.",
        "uz": "Kechiktirildi. Yana eslatamiz: {date}.",
    },
    # --- Заявки ---
    "confirm_master": {
        "ru": "Вызвать мастера? Подтвердите.",
        "uz": "Usta chaqirasizmi? Tasdiqlang.",
    },
    "confirm_emergency": {
        "ru": "Отправить аварийную заявку? Подтвердите.",
        "uz": "Favqulodda ariza yuborilsinmi? Tasdiqlang.",
    },
    "btn_confirm_yes": {"ru": "✅ Да", "uz": "✅ Ha"},
    "btn_cancel": {"ru": "❌ Отмена", "uz": "❌ Bekor qilish"},
    "btn_admin_panel": {
        "ru": "🛠 Админ-панель",
        "uz": "🛠 Admin-panel",
    },
    "choose_master": {
        "ru": "По какому оборудованию вызвать мастера?",
        "uz": "Qaysi jihoz bo‘yicha usta chaqiramiz?",
    },
    "btn_any_master": {"ru": "🧰 Любой мастер", "uz": "🧰 Istalgan usta"},
    "master_request_sent": {
        "ru": "🧰 Заявка на вызов мастера отправлена. Скоро свяжемся!",
        "uz": "🧰 Usta chaqirish arizasi yuborildi. Tez orada bog‘lanamiz!",
    },
    "emergency_sent": {
        "ru": "🚨 Аварийная заявка отправлена! Свяжемся в приоритетном порядке.",
        "uz": "🚨 Favqulodda ariza yuborildi! Birinchi navbatda bog‘lanamiz.",
    },
    "work_hours_line": {
        "ru": "🕒 Время работы: {hours}",
        "uz": "🕒 Ish vaqti: {hours}",
    },
    # --- Бонусы (клиент) ---
    "bonus_screen": {
        "ru": "💰 Ваши бонусы\n\nБаланс: {balance} сум\nВсего оплачено: {paid} сум\nДо следующей скидки {bonus} сум осталось оплатить: {left} сум",
        "uz": "💰 Sizning bonuslaringiz\n\nBalans: {balance} so‘m\nJami to‘langan: {paid} so‘m\nKeyingi {bonus} so‘m chegirmagacha to‘lash qoldi: {left} so‘m",
    },
    "bonus_earned": {
        "ru": "🎉 Поздравляем! Вам начислена скидка {delta} сум за оплаченные услуги.\nВаш бонусный баланс: {balance} сум.",
        "uz": "🎉 Tabriklaymiz! To‘langan xizmatlar uchun sizga {delta} so‘m chegirma berildi.\nBonus balansingiz: {balance} so‘m.",
    },
    "bonus_spent": {
        "ru": "🎁 С вашего бонусного счёта списано {spent} сум (скидка на услугу).\nОстаток: {balance} сум.",
        "uz": "🎁 Bonus hisobingizdan {spent} so‘m yechildi (xizmatga chegirma).\nQoldiq: {balance} so‘m.",
    },
    # --- Прочее ---
    "cancelled": {"ru": "Отменено.", "uz": "Bekor qilindi."},
    "not_registered": {
        "ru": "Сначала пройдите регистрацию: /start",
        "uz": "Avval ro‘yxatdan o‘ting: /start",
    },

    # ================= АДМИН-ПАНЕЛЬ =================
    "a_panel_title": {"ru": "🛠 Админ-панель", "uz": "🛠 Admin-panel"},
    "a_btn_clients": {"ru": "📋 Клиенты", "uz": "📋 Mijozlar"},
    "a_btn_stats": {"ru": "📊 Статистика", "uz": "📊 Statistika"},
    "a_btn_requests": {"ru": "📨 Заявки", "uz": "📨 Arizalar"},
    "a_btn_broadcast": {"ru": "📢 Рассылка", "uz": "📢 Tarqatma"},
    "a_btn_export": {"ru": "⬇️ Экспорт (Excel)", "uz": "⬇️ Eksport (Excel)"},
    "a_btn_settings": {"ru": "⚙️ Настройки", "uz": "⚙️ Sozlamalar"},
    "a_btn_admins": {"ru": "👤 Админы", "uz": "👤 Adminlar"},
    "a_btn_menu": {"ru": "🏠 Меню", "uz": "🏠 Menyu"},
    "a_btn_back": {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga"},
    "a_test_done": {
        "ru": "Проверка напоминаний выполнена. Отправлено: {n}",
        "uz": "Eslatmalar tekshiruvi bajarildi. Yuborildi: {n}",
    },
    "a_stats": {
        "ru": "📊 Статистика\n\nКлиентов: {total}\nПрофилактик в этом месяце: {month}\nПросрочено: {overdue}",
        "uz": "📊 Statistika\n\nMijozlar: {total}\nShu oyda profilaktika: {month}\nMuddati o‘tgan: {overdue}",
    },
    "a_clients_title": {"ru": "📋 Клиенты ({n})", "uz": "📋 Mijozlar ({n})"},
    "a_card_no_equip": {"ru": "Оборудования нет.", "uz": "Jihoz yo‘q."},
    "a_card_equip": {
        "ru": "🔧 {name}{model} — профилактика {date}",
        "uz": "🔧 {name}{model} — profilaktika {date}",
    },
    "a_btn_setdate": {"ru": "📅 Дата: {name}", "uz": "📅 Sana: {name}"},
    "a_btn_to_list": {"ru": "⬅️ К списку", "uz": "⬅️ Ro‘yxatga"},
    "a_not_found": {"ru": "Не найден", "uz": "Topilmadi"},
    "a_ask_date": {
        "ru": "Введите новую дату профилактики ДД.ММ.ГГГГ:",
        "uz": "Yangi profilaktika sanasini kiriting KK.OO.YYYY:",
    },
    "a_bad_date": {"ru": "Не понял дату. Формат ДД.ММ.ГГГГ.", "uz": "Sana tushunarsiz. Format KK.OO.YYYY."},
    "a_date_updated": {
        "ru": "✅ Дата профилактики обновлена: {date}",
        "uz": "✅ Profilaktika sanasi yangilandi: {date}",
    },
    "rtype_запись": {"ru": "запись", "uz": "yozuv"},
    "rtype_вызов": {"ru": "вызов мастера", "uz": "usta chaqiruvi"},
    "rtype_авария": {"ru": "авария", "uz": "favqulodda"},
    "a_no_requests": {"ru": "Новых заявок нет.", "uz": "Yangi arizalar yo‘q."},
    "a_requests_title": {"ru": "📨 Новые заявки:\n", "uz": "📨 Yangi arizalar:\n"},
    "a_btn_req_done": {"ru": "✅ Выполнено #{id}", "uz": "✅ Bajarildi #{id}"},
    "a_req_done_toast": {"ru": "Отмечено выполненным", "uz": "Bajarilgan deb belgilandi"},
    "a_btn_time": {"ru": "🕘 Время напоминаний", "uz": "🕘 Eslatma vaqti"},
    "a_btn_stages": {"ru": "📆 Этапы (дни)", "uz": "📆 Bosqichlar (kun)"},
    "a_btn_contacts_cfg": {"ru": "📞 Контакты", "uz": "📞 Kontaktlar"},
    "a_btn_workhours_cfg": {"ru": "🕒 Рабочее время", "uz": "🕒 Ish vaqti"},
    "a_btn_bonus_cfg": {"ru": "🎁 Бонусы (порог/сумма)", "uz": "🎁 Bonuslar (chegara/summa)"},
    "a_settings": {
        "ru": "⚙️ Настройки\n\n🕘 Время ежедневной проверки: {time}\n📆 Этапы (за сколько дней слать): {stages}\n🕒 Рабочее время: {work_hours}\n🎁 Бонус {bonus} сум за каждые {threshold} сум оплат\n\n📞 Контакты:\n{contacts}",
        "uz": "⚙️ Sozlamalar\n\n🕘 Kunlik tekshiruv vaqti: {time}\n📆 Bosqichlar (necha kun oldin): {stages}\n🕒 Ish vaqti: {work_hours}\n🎁 Har {threshold} so‘m to‘lovga {bonus} so‘m bonus\n\n📞 Kontaktlar:\n{contacts}",
    },
    "a_ask_workhours": {
        "ru": "Введите время работы (например «09:00–18:00, Пн–Сб»). Клиенты увидят его в разделе «Контакты»:",
        "uz": "Ish vaqtini kiriting (masalan «09:00–18:00, Du–Sh»). Mijozlar buni «Kontaktlar» bo‘limida ko‘radi:",
    },
    "a_workhours_set": {"ru": "✅ Рабочее время обновлено.", "uz": "✅ Ish vaqti yangilandi."},
    "a_ask_bonus_thr": {
        "ru": "Введите порог оплат для начисления бонуса (сум), например 20000000:",
        "uz": "Bonus uchun to‘lov chegarasini kiriting (so‘m), masalan 20000000:",
    },
    "a_ask_bonus_amt": {
        "ru": "Введите сумму бонуса за порог (сум), например 1000000:",
        "uz": "Chegara uchun bonus summasini kiriting (so‘m), masalan 1000000:",
    },
    "a_bad_amount": {
        "ru": "Нужно число (сумма в сумах). Попробуйте ещё раз.",
        "uz": "Raqam kerak (so‘mdagi summa). Qayta urinib ko‘ring.",
    },
    "a_bonus_cfg_set": {
        "ru": "✅ Бонус {bonus} сум за каждые {threshold} сум оплат.",
        "uz": "✅ Har {threshold} so‘m to‘lovga {bonus} so‘m bonus.",
    },
    "a_ask_time": {
        "ru": "Введите время в формате ЧЧ:ММ (например 09:00):",
        "uz": "Vaqtni SS:DD formatida kiriting (masalan 09:00):",
    },
    "a_bad_time": {
        "ru": "Не понял время. Формат ЧЧ:ММ, например 09:00.",
        "uz": "Vaqt tushunarsiz. Format SS:DD, masalan 09:00.",
    },
    "a_time_set": {"ru": "✅ Время напоминаний: {time}", "uz": "✅ Eslatma vaqti: {time}"},
    "a_ask_stages": {
        "ru": "Введите этапы напоминаний — за сколько дней до профилактики слать, через запятую.\nНапример: 14,3,0  (0 = в день профилактики):",
        "uz": "Eslatma bosqichlarini kiriting — profilaktikadan necha kun oldin yuborish, vergul bilan.\nMasalan: 14,3,0  (0 = profilaktika kuni):",
    },
    "a_bad_stages": {
        "ru": "Не понял. Введите числа через запятую, например 14,3,0.",
        "uz": "Tushunarsiz. Raqamlarni vergul bilan kiriting, masalan 14,3,0.",
    },
    "a_stages_set": {"ru": "✅ Этапы напоминаний: {stages}", "uz": "✅ Eslatma bosqichlari: {stages}"},
    "a_ask_contacts": {
        "ru": "Отправьте новый текст контактов (телефон, адрес, часы работы). Он будет показываться клиентам по кнопке «Контакты»:",
        "uz": "Yangi kontakt matnini yuboring (telefon, manzil, ish vaqti). U mijozlarga «Kontaktlar» tugmasida ko‘rsatiladi:",
    },
    "a_contacts_set": {"ru": "✅ Контакты обновлены.", "uz": "✅ Kontaktlar yangilandi."},
    "a_export_caption": {"ru": "⬇️ База клиентов", "uz": "⬇️ Mijozlar bazasi"},
    "a_sheet_title": {"ru": "Клиенты", "uz": "Mijozlar"},
    "a_col_name": {"ru": "Имя", "uz": "Ism"},
    "a_col_phone": {"ru": "Телефон", "uz": "Telefon"},
    "a_col_lang": {"ru": "Язык", "uz": "Til"},
    "a_col_equipment": {"ru": "Оборудование", "uz": "Jihoz"},
    "a_col_model": {"ru": "Модель", "uz": "Model"},
    "a_col_install": {"ru": "Установка", "uz": "O‘rnatilgan"},
    "a_col_service": {"ru": "Профилактика", "uz": "Profilaktika"},
    "a_admins_title": {"ru": "👤 Администраторы\n", "uz": "👤 Administratorlar\n"},
    "a_supers": {"ru": "⭐ Супер-админы (из конфигурации):", "uz": "⭐ Super-adminlar (konfiguratsiyadan):"},
    "a_added_admins": {"ru": "\n👥 Добавленные админы:", "uz": "\n👥 Qo‘shilgan adminlar:"},
    "a_btn_del_admin": {"ru": "🗑 Удалить {id}", "uz": "🗑 O‘chirish {id}"},
    "a_btn_add_admin": {"ru": "➕ Добавить админа", "uz": "➕ Admin qo‘shish"},
    "a_super_only": {"ru": "Только для супер-админа", "uz": "Faqat super-admin uchun"},
    "a_ask_admin_id": {
        "ru": "Пришлите Telegram ID нового админа (число).\nУзнать ID: пусть человек напишет боту @userinfobot и пришлёт вам число.",
        "uz": "Yangi adminning Telegram ID raqamini yuboring (raqam).\nID ni bilish: odam @userinfobot ga yozib, raqamni sizga yuborsin.",
    },
    "a_bad_admin_id": {
        "ru": "Нужно число — Telegram ID. Попробуйте ещё раз или /admin для отмены.",
        "uz": "Raqam kerak — Telegram ID. Qayta urinib ko‘ring yoki /admin bilan bekor qiling.",
    },
    "a_already_super": {"ru": "Этот пользователь уже супер-админ.", "uz": "Bu foydalanuvchi allaqachon super-admin."},
    "a_admin_added": {"ru": "✅ Админ {id} добавлен.", "uz": "✅ Admin {id} qo‘shildi."},
    "a_admin_removed": {"ru": "Админ удалён", "uz": "Admin o‘chirildi"},
    "a_btn_masters": {"ru": "👷 Мастера", "uz": "👷 Ustalar"},
    "a_masters_title": {"ru": "👷 Мастера компании\n", "uz": "👷 Kompaniya ustalari\n"},
    "a_btn_add_master": {"ru": "➕ Добавить мастера", "uz": "➕ Usta qo‘shish"},
    "a_btn_del_master": {"ru": "🗑 Удалить: {name}", "uz": "🗑 O‘chirish: {name}"},
    "a_ask_master_id": {
        "ru": "Пришлите Telegram ID мастера (число) или выберите из списка админов ниже.\nВажно: мастер должен сам запустить бота, иначе уведомления ему не дойдут.",
        "uz": "Ustaning Telegram ID raqamini yuboring (raqam) yoki quyidagi adminlar ro‘yxatidan tanlang.\nMuhim: usta botni o‘zi ishga tushirishi kerak, aks holda xabarlar yetib bormaydi.",
    },
    "a_master_exists": {
        "ru": "Такой мастер с этим видом оборудования уже есть.",
        "uz": "Bunday usta bu jihoz turi bilan allaqachon mavjud.",
    },
    "a_confirm_del_master": {
        "ru": "Удалить мастера {name}?",
        "uz": "{name} ustani o‘chirasizmi?",
    },
    "a_ask_master_name": {"ru": "Имя мастера:", "uz": "Usta ismi:"},
    "a_ask_master_kind": {
        "ru": "За какое оборудование отвечает мастер? Выберите или напишите свой вариант.",
        "uz": "Usta qaysi jihozga mas’ul? Tanlang yoki o‘zingiznikini yozing.",
    },
    "a_master_added": {"ru": "✅ Мастер {name} добавлен.", "uz": "✅ Usta {name} qo‘shildi."},
    "a_master_removed": {"ru": "Мастер удалён", "uz": "Usta o‘chirildi"},

    # ================= ОПЛАТЫ И БОНУСЫ (АДМИН) =================
    "a_card_money": {
        "ru": "💵 Оплачено: {paid} сум\n💰 Бонусов: {balance} сум",
        "uz": "💵 To‘langan: {paid} so‘m\n💰 Bonuslar: {balance} so‘m",
    },
    "a_btn_pay": {"ru": "💵 Внести платёж", "uz": "💵 To‘lov kiritish"},
    "a_btn_spend": {"ru": "🎁 Списать бонус", "uz": "🎁 Bonusdan yechish"},
    "a_ask_pay": {
        "ru": "Введите сумму оплаты (сум), например 20000000:",
        "uz": "To‘lov summasini kiriting (so‘m), masalan 20000000:",
    },
    "a_ask_spend": {
        "ru": "Введите сумму списания бонуса (сум). Доступно: {balance} сум.",
        "uz": "Yechiladigan bonus summasini kiriting (so‘m). Mavjud: {balance} so‘m.",
    },
    "a_pay_done": {
        "ru": "✅ Платёж {amount} сум учтён. Начислено бонуса: {delta} сум. Баланс: {balance} сум.",
        "uz": "✅ To‘lov {amount} so‘m hisobga olindi. Bonus: {delta} so‘m. Balans: {balance} so‘m.",
    },
    "a_spend_done": {
        "ru": "✅ Списано {spent} сум. Остаток бонусов: {balance} сум.",
        "uz": "✅ {spent} so‘m yechildi. Bonus qoldig‘i: {balance} so‘m.",
    },
    "a_ask_req_amount": {
        "ru": "Сумма оплаты по заявке (сум), например 20000000. Или нажмите «Без оплаты».",
        "uz": "Ariza bo‘yicha to‘lov summasi (so‘m), masalan 20000000. Yoki «To‘lovsiz».",
    },
    "a_btn_no_pay": {"ru": "Без оплаты", "uz": "To‘lovsiz"},
    "n_bonus_earned": {
        "ru": "🎁 Клиенту {name} начислен бонус {delta} сум (оплата {amount} сум). Баланс: {balance} сум.",
        "uz": "🎁 {name} mijozga {delta} so‘m bonus berildi (to‘lov {amount} so‘m). Balans: {balance} so‘m.",
    },

    # ================= РАССЫЛКА =================
    "bc_seg_all": {"ru": "Все", "uz": "Hammaga"},
    "bc_seg_overdue": {"ru": "Просроченные", "uz": "Muddati o‘tganlar"},
    "bc_seg_lang_ru": {"ru": "Русскоязычные", "uz": "Rus tilidagilar"},
    "bc_seg_lang_uz": {"ru": "Узбекоязычные", "uz": "O‘zbek tilidagilar"},
    "bc_kind_prefix": {"ru": "Оборуд.: {kind}", "uz": "Jihoz: {kind}"},
    "bc_cancel": {"ru": "⬅️ Отмена", "uz": "⬅️ Bekor qilish"},
    "bc_choose": {"ru": "📢 Кому отправляем?", "uz": "📢 Kimga yuboramiz?"},
    "bc_no_recipients": {"ru": "В этом сегменте нет получателей", "uz": "Bu segmentda qabul qiluvchilar yo‘q"},
    "bc_ask_content": {
        "ru": "Получателей: {n}.\n\nОтправьте сообщение для рассылки (текст, фото с подписью и т.д.).",
        "uz": "Qabul qiluvchilar: {n}.\n\nTarqatma uchun xabar yuboring (matn, izohli rasm va h.k.).",
    },
    "bc_send": {"ru": "✅ Отправить", "uz": "✅ Yuborish"},
    "bc_cancel2": {"ru": "❌ Отмена", "uz": "❌ Bekor qilish"},
    "bc_preview": {
        "ru": "⬆️ Так будет выглядеть рассылка.\nПолучателей: {n}.\nОтправляем?",
        "uz": "⬆️ Tarqatma shunday ko‘rinadi.\nQabul qiluvchilar: {n}.\nYuboramizmi?",
    },
    "bc_sending": {"ru": "📤 Отправка… (получателей: {n})", "uz": "📤 Yuborilmoqda… (qabul qiluvchilar: {n})"},
    "bc_done": {
        "ru": "✅ Рассылка завершена.\nДоставлено: {sent}\nНе доставлено: {failed}",
        "uz": "✅ Tarqatma yakunlandi.\nYetkazildi: {sent}\nYetkazilmadi: {failed}",
    },

    # ================= УВЕДОМЛЕНИЯ АДМИНАМ =================
    "n_master": {
        "ru": "🧰 Вызов мастера\nКлиент: {name} ({phone})\nid: {id}",
        "uz": "🧰 Usta chaqiruvi\nMijoz: {name} ({phone})\nid: {id}",
    },
    "n_emergency": {
        "ru": "🚨 АВАРИЙНАЯ ЗАЯВКА\nКлиент: {name} ({phone})\nid: {id}",
        "uz": "🚨 FAVQULODDA ARIZA\nMijoz: {name} ({phone})\nid: {id}",
    },
    "n_master_kind": {
        "ru": "🧰 Вызов мастера\nКлиент: {name} ({phone})\nid: {id}\nОборудование: {kind}",
        "uz": "🧰 Usta chaqiruvi\nMijoz: {name} ({phone})\nid: {id}\nJihoz: {kind}",
    },
    "n_booking": {
        "ru": "🗓 Запись на профилактику\nКлиент: {name} ({phone})\nid: {id}\nОборудование: {kind}",
        "uz": "🗓 Profilaktikaga yozuv\nMijoz: {name} ({phone})\nid: {id}\nJihoz: {kind}",
    },
}

DEFAULT_LANG = "ru"


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    entry = TEXTS.get(key, {})
    template = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template


def kind_label(kind: str, lang: str = DEFAULT_LANG) -> str:
    """Название вида оборудования на нужном языке.

    Известные коды (boiler, water_heater, …) переводятся; произвольный
    текст, введённый пользователем вручную, показывается как есть."""
    key = f"kind_{kind}"
    if key in TEXTS:
        return t(key, lang)
    return kind
