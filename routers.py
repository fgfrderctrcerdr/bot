import datetime
import sqlite3
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, types, F
from aiogram_calendar import SimpleCalendarCallback, SimpleCalendar
from aiogram.types import ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import or_f, Command, CommandStart, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from keyboards import *

main_router = Router()


class booking_data():
    def __init__(self, user, number, hall, date, timer_first, timer_second, id):
        self.user = user
        self.number = number
        self.hall = hall
        self.date = date
        self.timer_first = timer_first
        self.timer_second = timer_second
        self.id = id


absolute_data = booking_data(None, None, None, None, None, None, None)


class FSM_conference(StatesGroup):
    phone = State()
    hall = State()
    date = State()
    timer_first = State()
    timer_second = State()
    elect = State()
    date_change = State()
    timer_first_change = State()
    timer_second_change = State()
    removing = State()


@main_router.message(CommandStart(), StateFilter(None))
async def orderer(msg: types.Message):
    await msg.answer('Добро пожаловать!\nВыберите, что хотите сделать:', reply_markup=start_mark_up.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Что хотите сделать?'
    ))


@main_router.message(F.text == 'Мои брони:', StateFilter(None))
async def illustartion_of_bookings(msg: types.Message):
    searching_query_showing = '''
                      SELECT hall, date, time_of_beginning, time_of_ending, id FROM user_booking_data
                      WHERE username = ?
                      '''
    illustrate_connection = sqlite3.connect('datebase.db')
    cursor_showing_object = illustrate_connection.cursor()
    cursor_showing_object.execute(searching_query_showing, (f'@{msg.from_user.username}',))
    search_res = cursor_showing_object.fetchall()
    illustrate_connection.commit()
    illustrate_connection.close()

    if search_res:
        await msg.answer('Ваши брони:')
        for i in search_res:
            await msg.answer(f'Зал: {i[0]}, на: {i[1]}, с: {i[2]}, по: {i[3]}')
    else:
        await msg.answer('У вас нет бронирований.')



@main_router.message(F.text == 'Зал #1', StateFilter(FSM_conference.hall))
@main_router.message(F.text == 'Зал #2', StateFilter(FSM_conference.hall))
@main_router.message(F.text == 'Зал #3', StateFilter(FSM_conference.hall))
async def select_hall(msg: types.Message, state: FSMContext):
    selected_hall = msg.text
    await state.update_data(Зал=selected_hall)
    await msg.answer('Зал выбран', reply_markup=ReplyKeyboardRemove())
    await msg.answer('Выберите дату:', reply_markup=await SimpleCalendar(locale='ru_Ru').start_calendar())
    await state.set_state(FSM_conference.date)






@main_router.message(F.text == 'Забронировать зал', StateFilter(None))
async def contacter(msg: types.Message, state: FSMContext):
    await state.update_data(Арендатор=f'@{msg.from_user.username}')
    await msg.answer('Оправьте, пожалуйста, свой номер телефона:', reply_markup=contact_asker)
    await state.set_state(FSM_conference.phone)


@main_router.message(F.contact, StateFilter(FSM_conference.phone))
async def haller(msg: types.Message, state: FSMContext):
    await state.update_data(Телефон=msg.contact.phone_number)
    await msg.answer('Выберите зал, который хотите забронировать:', reply_markup=conference_booking_mark_up)
    await state.set_state(FSM_conference.hall)


@main_router.message(F.text == 'Зал #1', StateFilter(FSM_conference.hall))
async def orderer(msg: types.Message, state: FSMContext):
    await state.update_data(Зал=msg.text)
    await msg.answer('Зал выбран', reply_markup=ReplyKeyboardRemove())
    await msg.answer('Выберите дату:', reply_markup=await SimpleCalendar(locale='ru_Ru').start_calendar())
    await state.set_state(FSM_conference.date)


@main_router.callback_query(SimpleCalendarCallback.filter(), StateFilter(FSM_conference.date))
async def calen(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        # Преобразование даты в формат для сравнения
        today = datetime.date.today()
        selected_date = date.date()  # Преобразование datetime.datetime в datetime.date

        if selected_date < today:
            await callback.message.answer('Выберите дату в будущем, пожалуйста.')
            await callback.message.answer('Выберите дату:', reply_markup=await SimpleCalendar(locale='ru_Ru').start_calendar())
            return

        await state.update_data(Дата=selected_date.strftime('%d/%m'))

        # Получение выбранного зала из состояния
        state_data = await state.get_data()
        hall = state_data.get('Зал')

        # Запрос к базе данных для получения всех бронирований на выбранный день и зал
        connection = sqlite3.connect('datebase.db')
        cursor = connection.cursor()
        query = '''
            SELECT username, hall, date, time_of_beginning, time_of_ending 
            FROM user_booking_data
            WHERE date = ? AND hall = ?
        '''
        cursor.execute(query, (selected_date.strftime('%d/%m'), hall))
        bookings = cursor.fetchall()
        connection.close()

        if bookings:
            bookings_msg = '\n'.join(
                [f'Пользователь: {booking[0]}, Зал: {booking[1]}, Дата: {booking[2]}, С: {booking[3]}, По: {booking[4]}'
                 for booking in bookings]
            )
            await callback.message.answer(f'Все брони на {selected_date.strftime("%d/%m")} для зала {hall}:\n{bookings_msg}')
        else:
            await callback.message.answer(f'На {selected_date.strftime("%d/%m")} для зала {hall} нет бронирований.')

        await callback.message.answer('Укажите время, когда начинается встреча:', reply_markup=time_button.as_markup())
        await state.set_state(FSM_conference.timer_first)



@main_router.callback_query(StateFilter(FSM_conference.timer_first))
async def beginning(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        res = datetime.datetime.strptime(callback.data, '%H:%M')
        final_res = res.strftime('%H:%M')
        await state.update_data(С=final_res)
        await callback.message.edit_text('Укажите время, когда встреча заканчивается',
                                         reply_markup=time_button.as_markup())
        await state.set_state(FSM_conference.timer_second)
    except ValueError:
        await callback.message.answer('Некорректное время. Пожалуйста, выберите снова.')


@main_router.callback_query(StateFilter(FSM_conference.timer_second))
async def ending(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        res = datetime.datetime.strptime(callback.data, '%H:%M')
        final_res = res.strftime('%H:%M')
        await state.update_data(По=final_res)

        dictionary = await state.get_data()
        date = dictionary['Дата']
        start_time = dictionary['С']
        end_time = dictionary['По']
        hall = dictionary['Зал']

        connection = sqlite3.connect('datebase.db')
        cursor = connection.cursor()

        # Проверка на конфликты времени
        check_conflict_query = '''
            SELECT id, username, telephone_number, time_of_beginning, time_of_ending 
            FROM user_booking_data
            WHERE hall = ? AND date = ? AND (
                (time_of_beginning < ? AND time_of_ending > ?) OR
                (time_of_beginning < ? AND time_of_ending > ?)
            )
        '''
        cursor.execute(check_conflict_query, (hall, date, end_time, start_time, end_time, start_time))
        conflicts = cursor.fetchall()

        if conflicts:
            conflict_messages = '\n'.join(
                [f'Забронировано пользователем {conflict[1]} с {conflict[3]} по {conflict[4]} (ID: {conflict[0]})'
                 for conflict in conflicts]
            )
            await callback.message.answer(
                f'Время уже занято.\nКонфликтующие брони:\n{conflict_messages}\nПожалуйста, выберите другое время.',
                reply_markup=time_button.as_markup()
            )
            await callback.message.answer('Укажите время, когда начинается встреча:', reply_markup=time_button.as_markup())
            await state.set_state(FSM_conference.timer_first)  # Возврат к выбору времени начала
            return

        # Добавление записи в базу данных
        adding_query = '''
            INSERT INTO user_booking_data (username, telephone_number, hall, date, time_of_beginning, time_of_ending)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(adding_query, (dictionary['Арендатор'], dictionary['Телефон'], hall, date, start_time, end_time))

        connection.commit()
        connection.close()

        await callback.message.answer(
            f'Арендатор: {dictionary["Арендатор"]}\nТелефонный номер: {dictionary["Телефон"]}\nЗал: {hall}\nДата: {date}\nС: {start_time}\nПо: {end_time}',
            reply_markup=start_mark_up.as_markup(
                resize_keyboard=True,
                input_field_placeholder='Что хотите сделать?'
            ))
        await state.clear()

    except ValueError:
        await callback.message.answer('Некорректное время. Пожалуйста, выберите снова.')



@main_router.message(F.text == 'Перенести бронь', StateFilter(None))
async def select_booking(msg: types.Message, state: FSMContext):
    connection_object = sqlite3.connect('datebase.db')
    cursor_object = connection_object.cursor()
    query = '''
        SELECT username FROM user_booking_data
    '''
    cursor_object.execute(query)
    res = cursor_object.fetchall()

    l = [r for i in res for r in i]

    if f'@{msg.from_user.username}' not in l:
        await msg.answer('Вы пока что ничего не бронировали', reply_markup=ReplyKeyboardRemove())
        return

    searching_query = '''
        SELECT hall, date, time_of_beginning, time_of_ending, id FROM user_booking_data
        WHERE username = ?
    '''
    cursor_object.execute(searching_query, (f'@{msg.from_user.username}',))
    search_res = cursor_object.fetchall()
    connection_object.commit()
    connection_object.close()

    count = 0

    bookings_mark_up = InlineKeyboardBuilder()
    for i in search_res:
        count += 1
        bookings_mark_up.add(
            InlineKeyboardButton(text=f'Зал: {i[0]}, на: {i[1]}, с: {i[2]}, по: {i[3]}', callback_data=f'id: {i[4]}'))
    bookings_mark_up.adjust(1)

    await msg.answer('Выберите бронь, которую хотите перенести:', reply_markup=ReplyKeyboardRemove())
    await msg.answer('Ваши брони:', reply_markup=bookings_mark_up.as_markup())
    await state.set_state(FSM_conference.elect)



@main_router.callback_query(StateFilter(FSM_conference.elect))
async def postpone_booking(callback: CallbackQuery, state: FSMContext):
    data = callback.data.replace('id:', '').replace(' ', '')
    booking_id = int(data)

    # Получение данных о бронировании по ID
    connection = sqlite3.connect('datebase.db')
    cursor = connection.cursor()
    query = '''
        SELECT username, hall, date, time_of_beginning, time_of_ending 
        FROM user_booking_data
        WHERE id = ?
    '''
    cursor.execute(query, (booking_id,))
    booking = cursor.fetchone()
    connection.close()

    if booking:
        await state.update_data(Зал=booking[1])
        absolute_data.hall = booking[1]  # Сохранение выбранного зала
        absolute_data.id = booking_id  # Установка ID для дальнейшего использования

        await callback.message.answer(f'Вы перенесете бронь для:\nПользователь: {booking[0]}, Зал: {booking[1]}, Дата: {booking[2]}, С: {booking[3]}, По: {booking[4]}')
        await callback.message.answer('Выберите новую дату:', reply_markup=await SimpleCalendar(locale='ru_Ru').start_calendar())
        await state.set_state(FSM_conference.date_change)
    else:
        await callback.message.answer('Ошибка: Бронь не найдена.')


@main_router.callback_query(SimpleCalendarCallback.filter(), StateFilter(FSM_conference.date_change))
async def calen_change(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        await state.update_data(Дата=date.strftime('%d/%m'))
        await callback.message.answer('Укажите время, когда начинается встреча:', reply_markup=time_button.as_markup())
        await state.set_state(FSM_conference.timer_first_change)



@main_router.callback_query(SimpleCalendarCallback.filter(), StateFilter(FSM_conference.date_change))
async def calen_change(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        await state.update_data(Дата=date.strftime('%d/%m'))
        await callback.message.answer('Укажите время, когда начинается встреча:', reply_markup=time_button.as_markup())
        await state.set_state(FSM_conference.timer_first_change)


@main_router.callback_query(StateFilter(FSM_conference.timer_first_change))
async def beginning_change(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        res = datetime.datetime.strptime(callback.data, '%H:%M')
        final_res = res.strftime('%H:%M')
        await state.update_data(С=final_res)
        await callback.message.edit_text('Укажите время, когда встреча заканчивается',
                                         reply_markup=time_button.as_markup())
        await state.set_state(FSM_conference.timer_second_change)
    except ValueError:
        await callback.message.answer('Некорректное время. Пожалуйста, выберите снова.')


import logging

logging.basicConfig(level=logging.DEBUG)

@main_router.callback_query(StateFilter(FSM_conference.timer_second_change))
async def ending_change(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        res = datetime.datetime.strptime(callback.data, '%H:%M')
        final_res = res.strftime('%H:%M')
        await state.update_data(По=final_res)

        dictionary = await state.get_data()
        date = dictionary['Дата']
        start_time = dictionary['С']
        end_time = dictionary['По']
        hall = absolute_data.hall
        booking_id = absolute_data.id

        # Проверка значений
        if not booking_id:
            await callback.message.answer('Ошибка: ID брони не установлен.')
            return

        connection = sqlite3.connect('datebase.db')
        cursor = connection.cursor()

        # Проверка на конфликты времени
        check_conflict_query = '''
            SELECT id, username, telephone_number, time_of_beginning, time_of_ending 
            FROM user_booking_data
            WHERE hall = ? AND date = ? AND (
                (time_of_beginning < ? AND time_of_ending > ?) OR
                (time_of_beginning < ? AND time_of_ending > ?)
            ) AND id != ?
        '''
        cursor.execute(check_conflict_query, (hall, date, end_time, start_time, end_time, start_time, booking_id))
        conflicts = cursor.fetchall()

        if conflicts:
            conflict_messages = '\n'.join(
                [f'Забронировано пользователем {conflict[1]} с {conflict[3]} по {conflict[4]} (ID: {conflict[0]})'
                 for conflict in conflicts]
            )
            await callback.message.answer(
                f'Время уже занято.\nКонфликтующие брони:\n{conflict_messages}\nПожалуйста, выберите другое время.',
                reply_markup=time_button.as_markup()
            )
            await callback.message.answer('Укажите время, когда начинается встреча:', reply_markup=time_button.as_markup())
            await state.set_state(FSM_conference.timer_first_change)  # Возврат к выбору времени начала
            return

        # Обновление записи в базе данных
        update_query = '''
            UPDATE user_booking_data
            SET date = ?, time_of_beginning = ?, time_of_ending = ?
            WHERE id = ?
        '''
        cursor.execute(update_query, (date, start_time, end_time, booking_id))

        # Проверка успешности обновления
        connection.commit()
        cursor.execute('SELECT * FROM user_booking_data WHERE id = ?', (booking_id,))
        updated_booking = cursor.fetchone()
        connection.close()

        if updated_booking:
            await callback.message.answer(f'Бронь успешно перенесена.\nЗал: {hall}\nДата: {date}\nС: {start_time}\nПо: {end_time}',
                                          reply_markup=start_mark_up.as_markup(
                                              resize_keyboard=True,
                                              input_field_placeholder='Что хотите сделать?'
                                          ))
        else:
            await callback.message.answer(f'Ошибка: Не удалось обновить бронь. ID: {booking_id}', reply_markup=start_mark_up.as_markup(
                resize_keyboard=True,
                input_field_placeholder='Что хотите сделать?'
            ))
        await state.clear()

    except Exception as e:
        await callback.message.answer(f'Произошла ошибка: {str(e)}', reply_markup=start_mark_up.as_markup(
            resize_keyboard=True,
            input_field_placeholder='Что хотите сделать?'
        ))









@main_router.message(F.text == 'Отменить бронь', StateFilter(None))
async def remove_booking(msg: types.Message, state: FSMContext):
    connection_object = sqlite3.connect('datebase.db')
    cursor_object = connection_object.cursor()
    query = '''
        SELECT username FROM user_booking_data
    '''
    cursor_object.execute(query)
    res = cursor_object.fetchall()

    l = [r for i in res for r in i]

    if f'@{msg.from_user.username}' not in l:
        await msg.answer('Вы пока что ничего не бронировали', reply_markup=ReplyKeyboardRemove())
        return

    searching_query = '''
        SELECT hall, date, time_of_beginning, time_of_ending, id FROM user_booking_data
        WHERE username = ?
    '''
    cursor_object.execute(searching_query, (f'@{msg.from_user.username}',))
    search_res = cursor_object.fetchall()
    connection_object.commit()
    connection_object.close()

    count = 0

    bookings_mark_up = InlineKeyboardBuilder()
    for i in search_res:
        count += 1
        bookings_mark_up.add(
            InlineKeyboardButton(text=f'Зал: {i[0]}, на: {i[1]}, с: {i[2]}, по: {i[3]}', callback_data=f'id: {i[4]}'))
    bookings_mark_up.adjust(1)

    await msg.answer('Выберите бронь, которую хотите отменить:', reply_markup=ReplyKeyboardRemove())
    await msg.answer('Ваши брони:', reply_markup=bookings_mark_up.as_markup())
    await state.set_state(FSM_conference.removing)


@main_router.callback_query(StateFilter(FSM_conference.removing))
async def remove_booking_action(callback: CallbackQuery, state: FSMContext):
    data = callback.data.replace('id:', '').replace(' ', '')
    booking_id = int(data)
    connection = sqlite3.connect('datebase.db')
    cursor = connection.cursor()

    # Удаление записи из базы данных
    delete_query = 'DELETE FROM user_booking_data WHERE id = ?'
    cursor.execute(delete_query, (booking_id,))

    connection.commit()
    connection.close()

    await callback.message.answer('Бронь успешно отменена.', reply_markup=start_mark_up.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Что хотите сделать?'
    ))
    await state.clear()



