from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

start_mark_up = ReplyKeyboardBuilder()
start_mark_up.add(
    KeyboardButton(text='Забронировать зал'),
    KeyboardButton(text='Перенести бронь'),
    KeyboardButton(text='Отменить бронь'),
    KeyboardButton(text='Мои брони:')
)
start_mark_up.adjust(1, 2, 1)

time_list = ['7:00', '7:30', '8:00', '8:30', '9:00',
             '9:30', '10:00', '10:30', '11:00', '11:30',
             '12:00', '12:30', '13:00', '13:30', '14:00',
             '14:30', '15:00', '15:30', '16:00', '16:30',
             '17:00', '17:30', '18:00', '18:30', '19:00',
             '19:30', '20:00', '20:30', '21:00', '21:30',
             '22:00']
time_button = InlineKeyboardBuilder()
for i in time_list:
    time_button.add(
        InlineKeyboardButton(text=i, callback_data=i)
    )

time_button.adjust(5, 5, 5, 5, 5, 6)

contact_asker = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отправить контакт', request_contact=True)]
    ],
    resize_keyboard=True,
)

conference_booking_mark_up = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Зал #1'),
            KeyboardButton(text='Зал #2'),
            KeyboardButton(text='Зал #3')
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Бронирование:'
)