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


calendar_keyboard = InlineKeyboardBuilder()

year_list = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057', '2058', '2059', '2060']
month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
           '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
           '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

now = datetime.datetime.today().date()
for y in year_list:
    if y != str(now.year):
        continue
    else:
        calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
        calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
        calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
        break

for m in month_list:
    if m != now.strftime('%B'):
        continue
    else:
        calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
        calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
        calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
        break

count = 0

if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
    count = 31
else:
    if m == 'February':
        if int(y) % 4 == 0:
            count = 29
        else:
            count = 28
    else:
        count = 30

counter = 0
for d in day_list[0 : day_list.index(str(now.day))]:
    counter += 1
    calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
    counter += 1
    calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

while counter % 7 != 0:
    counter += 1
    calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
calendar_keyboard.adjust(3, 3, 7)

@main_router.callback_query(F.data == 'return_to_main_menu', StateFilter('*'))
async def callback_orderer(callback : CallbackQuery, state : FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.answer('Добро пожаловать!\nВыберите, что хотите сделать:', reply_markup=start_mark_up.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Что хотите сделать?'
    ))

@main_router.message(CommandStart(), StateFilter('*'))
async def orderer(msg: types.Message, state : FSMContext):
    await state.clear()
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



@main_router.message(F.text == 'Зал Альфа', StateFilter(FSM_conference.hall))
@main_router.message(F.text == 'Зал Бета', StateFilter(FSM_conference.hall))
@main_router.message(F.text == 'Зал Гамма', StateFilter(FSM_conference.hall))
async def select_hall(msg: types.Message, state: FSMContext):
    selected_hall = msg.text
    await state.update_data(Зал=selected_hall)
    await msg.answer('Зал выбран', reply_markup=ReplyKeyboardRemove())
    await msg.answer('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
    await state.set_state(FSM_conference.date)



@main_router.callback_query(F.data.lower().contains('next_year'), StateFilter(FSM_conference.date))
async def next_year_func(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date)
    await callback.answer()
    calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                             [
                                                 []
                                             ])
    calendar_keyboard = InlineKeyboardBuilder()
    await callback.answer()
    res = callback.data.replace('next_year', '')
    now = datetime.datetime(int(res) + 1, 1, 1)

    for y in year_list:
        if y != str(now.year):
            continue
        else:
            calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
            calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
            calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
            break

    for m in month_list:
        if m != now.strftime('%B'):
            continue
        else:
            calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
            calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
            calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
            break

    count = 0

    if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
        count = 31
    else:
        if m == 'February':
            if int(y) % 4 == 0:
                count = 29
            else:
                count = 28
        else:
            count = 30

    counter = 0
    for d in day_list[0 : day_list.index(str(now.day))]:
        counter += 1
        calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
    for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
        counter += 1
        calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

    while counter % 7 != 0:
        counter += 1
        calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
    calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
    calendar_keyboard.adjust(3, 3, 7)

    await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())

@main_router.callback_query(F.data.lower().contains('last_year'), StateFilter(FSM_conference.date))
async def last_year_func(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date)
    await callback.answer()
    calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                             [
                                                 []
                                             ])
    calendar_keyboard = InlineKeyboardBuilder()
    await callback.answer()
    res = callback.data.replace('last_year', '')
    now = datetime.datetime(int(res) - 1, 1, 1)
    if now.year < datetime.datetime.today().year:
        return

    for y in year_list:
        if y != str(now.year):
            continue
        else:
            calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
            calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
            calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
            break

    for m in month_list:
        if m != now.strftime('%B'):
            continue
        else:
            calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
            calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
            calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
            break

    count = 0

    if now.year == datetime.datetime.today().year:
        calendar_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                []
            ]
        )
        calendar_keyboard = InlineKeyboardBuilder()

        now = datetime.datetime.today().date()
        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0

        if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
            count = 31
        else:
            if m == 'February':
                if int(y) % 4 == 0:
                    count = 29
                else:
                    count = 28
            else:
                count = 30

        counter = 0
        for d in day_list[0 : day_list.index(str(now.day))]:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

        while counter % 7 != 0:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
        calendar_keyboard.adjust(3, 3, 7)
        await callback.message.edit_text('Выберите дату', reply_markup=calendar_keyboard.as_markup())
        return
    else:
        if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
            count = 31
        else:
            if m == 'February':
                if int(y) % 4 == 0:
                    count = 29
                else:
                    count = 28
            else:
                count = 30
        counter = 0
        for d in day_list[0 : day_list.index(str(now.day))]:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

        while counter % 7 != 0:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
    calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
    calendar_keyboard.adjust(3, 3, 7)
    await callback.message.edit_text('Выберите дату', reply_markup=calendar_keyboard.as_markup())

@main_router.callback_query(F.data.lower().contains('next_month'), StateFilter(FSM_conference.date))
async def next_month_func(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date)
    await callback.answer()
    calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                             [
                                                 []
                                             ])
    calendar_keyboard = InlineKeyboardBuilder()
    await callback.answer()
    res = callback.data.replace('next_month', '') #{m}next_month {y}
    mon = res[0 : res.index(' ')]
    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    final_mon = 0
    for i in month_list:
        final_mon += 1
        if i == mon:
            final_mon += 1
            break
    if final_mon == 13:
        await callback.answer()
        calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                                [
                                                    []
                                                ])
        calendar_keyboard = InlineKeyboardBuilder()
        await callback.answer()
        res = callback.data.replace('next_month', '')
        now = datetime.datetime(int(res[res.index(' ')+1:]) + 1, 1, 1)

        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0

        if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
            count = 31
        else:
            if m == 'February':
                if int(y) % 4 == 0:
                    count = 29
                else:
                    count = 28
            else:
                count = 30

        counter = 0
        for d in day_list[0 : day_list.index(str(now.day))]:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

        while counter % 7 != 0:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
        calendar_keyboard.adjust(3, 3, 7)

        await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
        return
    else:
        now = datetime.datetime(int(res[res.index(' ')+1:]), final_mon, 1)
        if int(res[res.index(' ')+1:]) > datetime.datetime.today().year:
            for y in year_list:
                if y != str(now.year):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                    calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                    break

            for m in month_list:
                if m != now.strftime('%B'):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                    calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                    break

            count = 0
            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(now.day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return

        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0
    
        if now.month > datetime.datetime.today().month:
            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(now.day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month == datetime.datetime.today().month:
            calendar_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        
                    ]
                ]
            )
            calendar_keyboard = InlineKeyboardBuilder()
            for y in year_list:
                if y != str(now.year):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                    calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                    break

            for m in month_list:
                if m != now.strftime('%B'):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                    calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                    break

            count = 0

            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(datetime.datetime.today().day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(datetime.datetime.today().day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month < datetime.datetime.today().month:
            for q in range(35):
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
            
@main_router.callback_query(F.data.lower().contains('last_month'), StateFilter(FSM_conference.date))
async def last_month_func(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date)
    await callback.answer()
    calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                             [
                                                 []
                                             ])
    calendar_keyboard = InlineKeyboardBuilder()
    await callback.answer()
    res = callback.data.replace('last_month', '') 
    mon = res[0 : res.index(' ')]
    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    final_mon = 12
    for i in reversed(month_list):
        final_mon -= 1
        if i == mon:
            break
    if final_mon not in range(1, 13):
        if int(res[res.index(' ')+1:]) == datetime.datetime.today().year:
            return
    
        await callback.answer()
        calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                                [
                                                    []
                                                ])
        calendar_keyboard = InlineKeyboardBuilder()
        await callback.answer()
        res = callback.data.replace('last_month', '')
        now = datetime.datetime(int(res[res.index(' ')+1:]) - 1, 12, 1)

        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0
        if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
            count = 31
        else:
            if m == 'February':
                if int(y) % 4 == 0:
                    count = 29
                else:
                    count = 28
            else:
                count = 30

        counter = 0
        for d in day_list[0 : day_list.index(str(now.day))]:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

        while counter % 7 != 0:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
        calendar_keyboard.adjust(3, 3, 7)
        await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
        return
    else:
        now = datetime.datetime(int(res[res.index(' ')+1:]), final_mon, 1)
        if int(res[res.index(' ')+1:]) > datetime.datetime.today().year:
            for y in year_list:
                if y != str(now.year):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                    calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                    break

            for m in month_list:
                if m != now.strftime('%B'):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                    calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                    break

            count = 0
            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(now.day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return

        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0

        if now.month > datetime.datetime.today().month:
            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(now.day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month == datetime.datetime.today().month:
            calendar_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        
                    ]
                ]
            )
            calendar_keyboard = InlineKeyboardBuilder()
            for y in year_list:
                if y != str(now.year):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                    calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                    break

            for m in month_list:
                if m != now.strftime('%B'):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                    calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                    break

            count = 0

            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(datetime.datetime.today().day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(datetime.datetime.today().day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month < datetime.datetime.today().month:
            for q in range(35):
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return

@main_router.callback_query(F.data == ' ', StateFilter(FSM_conference.date))
async def skipper(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date)
    await callback.answer()      

@main_router.callback_query(F.data != ' ', StateFilter(FSM_conference.date))
async def date_getter(callback : CallbackQuery, state : FSMContext):
    await callback.answer()
    res = datetime.datetime.strptime(callback.data, '%Y/%B/%d')
    if res.month > 9:
        if res.day > 9:
            final_res = f'{res.year}/{res.day}/{res.month}'
        else:
            final_res = f'{res.year}/0{res.day}/{res.month}'
    else:
        if res.day > 9:
            final_res = f'{res.year}/{res.day}/0{res.month}'
        else:
            final_res = f'{res.year}/0{res.day}/0{res.month}'
    final_res = final_res[5:]
    await callback.message.answer(final_res)
    await state.update_data(Дата=f'{final_res}')
    final_res_for_sql = datetime.datetime.strptime(final_res, '%d/%m')
    # Получение выбранного зала из состояния
    state_data = await state.get_data()
    hall = state_data.get('Зал')

    # Запрос к базе данных для получения всех бронирований на выбранный день и зал
    connection = sqlite3.connect('datebase.db')
    cursor = connection.cursor()
    query = '''
            SELECT username, hall, date, time_of_beginning, time_of_ending, id 
            FROM user_booking_data
            WHERE date = ? AND hall = ?
        '''
    cursor.execute(query, (final_res_for_sql.strftime('%d/%m'), hall))
    bookings = cursor.fetchall()
    connection.commit()
    connection.close()
    
    if bookings:
        bookings_msg = '\n'.join(
            [f'Пользователь: {booking[0]}, Зал: {booking[1]}, Дата: {booking[2]}, С: {booking[3]}, По: {booking[4]}'
            for booking in bookings]
        )
        await callback.message.answer(f'Все брони на {final_res_for_sql.strftime("%d/%m")} для зала {hall}:\n{bookings_msg}')
    else:
        await callback.message.answer(f'На {final_res_for_sql.strftime("%d/%m")} для зала {hall} нет бронирований.')
    dictionary = await state.get_data()
    date = dictionary['Дата']
    hall = dictionary['Зал']
    time_buttons = await generate_time_buttons(date, hall, f'@{callback.message.from_user.username}')
    await callback.message.answer('Укажите время, когда начинается встреча:', reply_markup=time_buttons.as_markup())
    await state.set_state(FSM_conference.timer_first)


@main_router.message(F.text == 'Забронировать зал', StateFilter(None))
async def contacter(msg: types.Message, state: FSMContext):
    await state.update_data(Забронировал=f'@{msg.from_user.username}')
    connection = sqlite3.connect('datebase.db')
    cursor = connection.cursor()
    query = '''
            SELECT username FROM user_booking_data
            WHERE username = ?
            '''
    cursor.execute(query, (f'@{msg.from_user.username}',))
    result = cursor.fetchall()
    connection.commit()
    connection.close()
    res_list = []
    for q in result:
        for g in q:
            res_list.append(g)
    if f'@{msg.from_user.username}' not in res_list:
        await msg.answer('Отправьте, пожалуйста, свой номер телефона:', reply_markup=contact_asker)
        await state.set_state(FSM_conference.phone)
    else:
        connection = sqlite3.connect('datebase.db')
        cursor = connection.cursor()
        query = '''
                    SELECT telephone_number FROM user_booking_data
                    WHERE username = ?
                    '''
        cursor.execute(query, (f'@{msg.from_user.username}',))
        result_tuple = cursor.fetchone()
        result = ''
        for var in result_tuple:
            result = var
        connection.commit()
        connection.close()
        await state.update_data(Телефон=result)
        await msg.answer('Выберите зал, который хотите забронировать:', reply_markup=conference_booking_mark_up)
        await state.set_state(FSM_conference.hall)


@main_router.message(F.contact, StateFilter(FSM_conference.phone))
async def haller(msg: types.Message, state: FSMContext):
    await state.update_data(Телефон=msg.contact.phone_number)
    await msg.answer('Выберите зал, который хотите забронировать:', reply_markup=conference_booking_mark_up)
    await state.set_state(FSM_conference.hall)



@main_router.callback_query(StateFilter(FSM_conference.timer_first))
async def beginning(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        res = datetime.datetime.strptime(callback.data, '%H:%M')
        final_res = res.strftime('%H:%M')
        await state.update_data(С=final_res)
        dictionary = await state.get_data()
        date = dictionary['Дата']
        hall = dictionary['Зал']

        # Update time button with booked times
        
        time_buttons = await generate_time_buttons(date, hall, f'@{callback.message.from_user.username}')
        await callback.message.edit_text('Укажите время, когда встреча заканчивается', reply_markup=time_buttons.as_markup())
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

        # Check if the end time is earlier than the start time
        if datetime.datetime.strptime(end_time, '%H:%M') <= datetime.datetime.strptime(start_time, '%H:%M'):
            await callback.message.answer('Время окончания должно быть позже времени начала. Пожалуйста, выберите снова.',
                                         reply_markup=await generate_time_buttons(date, hall, f'@{callback.message.from_user.username}').as_markup())
            await state.set_state(FSM_conference.timer_first)  # Return to start time selection
            return

        connection = sqlite3.connect('datebase.db')
        cursor = connection.cursor()

        # Check for time conflicts
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
            time_but = await generate_time_buttons(date, hall, f'@{callback.message.from_user.username}')
            await callback.message.answer(
                f'Время уже занято.\nКонфликтующие брони:\n{conflict_messages}\nПожалуйста, выберите другое время.',
                reply_markup=time_but.as_markup()
            )
            await callback.message.answer('Укажите время, когда начинается встреча:', reply_markup=time_but.as_markup())
            await state.set_state(FSM_conference.timer_first)  # Return to start time selection
            return

        # Add booking to the database
        adding_query = '''
            INSERT INTO user_booking_data (username, telephone_number, hall, date, time_of_beginning, time_of_ending)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(adding_query, (dictionary['Забронировал'], dictionary['Телефон'], hall, date, start_time, end_time))

        connection.commit()
        connection.close()

        await callback.message.answer(
            f'Забронировал: {dictionary["Забронировал"]}\nТелефонный номер: {dictionary["Телефон"]}\nЗал: {hall}\nДата: {date}\nС: {start_time}\nПо: {end_time}',
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
    await callback.answer()
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
        await callback.message.answer('Выберите новую дату:', reply_markup=calendar_keyboard.as_markup())
        await state.set_state(FSM_conference.date_change)
    else:
        await callback.message.answer('Ошибка: Бронь не найдена.')




@main_router.callback_query(F.data.lower().contains('next_year'), StateFilter(FSM_conference.date_change))
async def next_year_func(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date_change)
    await callback.answer()
    calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                             [
                                                 []
                                             ])
    calendar_keyboard = InlineKeyboardBuilder()
    await callback.answer()
    res = callback.data.replace('next_year', '')
    now = datetime.datetime(int(res) + 1, 1, 1)


    for y in year_list:
        if y != str(now.year):
            continue
        else:
            calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
            calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
            calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
            break

    for m in month_list:
        if m != now.strftime('%B'):
            continue
        else:
            calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
            calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
            calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
            break

    count = 0

    if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
        count = 31
    else:
        if m == 'February':
            if int(y) % 4 == 0:
                count = 29
            else:
                count = 28
        else:
            count = 30

    counter = 0
    for d in day_list[0 : day_list.index(str(now.day))]:
        counter += 1
        calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
    for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
        counter += 1
        calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

    while counter % 7 != 0:
        counter += 1
        calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
    calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
    calendar_keyboard.adjust(3, 3, 7)

    await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())

@main_router.callback_query(F.data.lower().contains('last_year'), StateFilter(FSM_conference.date_change))
async def last_year_func(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date_change)
    await callback.answer()
    calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                             [
                                                 []
                                             ])
    calendar_keyboard = InlineKeyboardBuilder()
    await callback.answer()
    res = callback.data.replace('last_year', '')
    now = datetime.datetime(int(res) - 1, 1, 1)
    if now.year < datetime.datetime.today().year:
        return

    for y in year_list:
        if y != str(now.year):
            continue
        else:
            calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
            calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
            calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
            break

    for m in month_list:
        if m != now.strftime('%B'):
            continue
        else:
            calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
            calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
            calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
            break

    count = 0

    if now.year == datetime.datetime.today().year:
        calendar_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                []
            ]
        )
        calendar_keyboard = InlineKeyboardBuilder()

        now = datetime.datetime.today().date()
        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0

        if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
            count = 31
        else:
            if m == 'February':
                if int(y) % 4 == 0:
                    count = 29
                else:
                    count = 28
            else:
                count = 30

        counter = 0
        for d in day_list[0 : day_list.index(str(now.day))]:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

        while counter % 7 != 0:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
        calendar_keyboard.adjust(3, 3, 7)
        await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
        return
    else:
        if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
            count = 31
        else:
            if m == 'February':
                if int(y) % 4 == 0:
                    count = 29
                else:
                    count = 28
            else:
                count = 30
        counter = 0
        for d in day_list[0 : day_list.index(str(now.day))]:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

        while counter % 7 != 0:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
    calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))     
    calendar_keyboard.adjust(3, 3, 7)
    await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())

@main_router.callback_query(F.data.lower().contains('next_month'), StateFilter(FSM_conference.date_change))
async def next_month_func(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date_change)
    await callback.answer()
    calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                             [
                                                 []
                                             ])
    calendar_keyboard = InlineKeyboardBuilder()
    await callback.answer()
    res = callback.data.replace('next_month', '') #{m}next_month {y}
    mon = res[0 : res.index(' ')]
    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    final_mon = 0
    for i in month_list:
        final_mon += 1
        if i == mon:
            final_mon += 1
            break
    if final_mon == 13:
        await callback.answer()
        calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                                [
                                                    []
                                                ])
        calendar_keyboard = InlineKeyboardBuilder()
        await callback.answer()
        res = callback.data.replace('next_month', '')
        now = datetime.datetime(int(res[res.index(' ')+1:]) + 1, 1, 1)

        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0

        if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
            count = 31
        else:
            if m == 'February':
                if int(y) % 4 == 0:
                    count = 29
                else:
                    count = 28
            else:
                count = 30

        counter = 0
        for d in day_list[0 : day_list.index(str(now.day))]:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

        while counter % 7 != 0:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
        calendar_keyboard.adjust(3, 3, 7)

        await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
        return
    else:
        now = datetime.datetime(int(res[res.index(' ')+1:]), final_mon, 1)
        if int(res[res.index(' ')+1:]) > datetime.datetime.today().year:
            for y in year_list:
                if y != str(now.year):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                    calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                    break

            for m in month_list:
                if m != now.strftime('%B'):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                    calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                    break

            count = 0
            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(now.day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return

        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0
    
        if now.month > datetime.datetime.today().month:
            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(now.day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month == datetime.datetime.today().month:
            calendar_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        
                    ]
                ]
            )
            calendar_keyboard = InlineKeyboardBuilder()
            for y in year_list:
                if y != str(now.year):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                    calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                    break

            for m in month_list:
                if m != now.strftime('%B'):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                    calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                    break

            count = 0

            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(datetime.datetime.today().day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(datetime.datetime.today().day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month < datetime.datetime.today().month:
            for q in range(35):
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
            
@main_router.callback_query(F.data.lower().contains('last_month'), StateFilter(FSM_conference.date_change))
async def last_month_func(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date_change)
    await callback.answer()
    calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                             [
                                                 []
                                             ])
    calendar_keyboard = InlineKeyboardBuilder()
    await callback.answer()
    res = callback.data.replace('last_month', '') 
    mon = res[0 : res.index(' ')]
    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    final_mon = 12
    for i in reversed(month_list):
        final_mon -= 1
        if i == mon:
            break
    if final_mon not in range(1, 13):
        if int(res[res.index(' ')+1:]) == datetime.datetime.today().year:
            return
    
        await callback.answer()
        calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                                [
                                                    []
                                                ])
        calendar_keyboard = InlineKeyboardBuilder()
        await callback.answer()
        res = callback.data.replace('last_month', '')
        now = datetime.datetime(int(res[res.index(' ')+1:]) - 1, 12, 1)

        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0
        if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
            count = 31
        else:
            if m == 'February':
                if int(y) % 4 == 0:
                    count = 29
                else:
                    count = 28
            else:
                count = 30

        counter = 0
        for d in day_list[0 : day_list.index(str(now.day))]:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

        while counter % 7 != 0:
            counter += 1
            calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
        calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
        calendar_keyboard.adjust(3, 3, 7)
        await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
        return
    else:
        now = datetime.datetime(int(res[res.index(' ')+1:]), final_mon, 1)
        if int(res[res.index(' ')+1:]) > datetime.datetime.today().year:
            for y in year_list:
                if y != str(now.year):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                    calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                    break

            for m in month_list:
                if m != now.strftime('%B'):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                    calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                    break

            count = 0
            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(now.day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
        for y in year_list:
            if y != str(now.year):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                break

        for m in month_list:
            if m != now.strftime('%B'):
                continue
            else:
                calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                break

        count = 0

        if now.month > datetime.datetime.today().month:
            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(now.day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(now.day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month == datetime.datetime.today().month:
            calendar_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        
                    ]
                ]
            )
            calendar_keyboard = InlineKeyboardBuilder()
            for y in year_list:
                if y != str(now.year):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{y}last_year'))
                    calendar_keyboard.add(InlineKeyboardButton(text=y, callback_data='year'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{y}next_year'))
                    break

            for m in month_list:
                if m != now.strftime('%B'):
                    continue
                else:
                    calendar_keyboard.add(InlineKeyboardButton(text='<-', callback_data=f'{m}last_month {y}'))
                    calendar_keyboard.add(InlineKeyboardButton(text=m, callback_data='month'))
                    calendar_keyboard.add(InlineKeyboardButton(text='->', callback_data=f'{m}next_month {y}'))
                    break

            count = 0

            if m == 'January' or m == 'March' or m == 'May' or m == 'July' or m == 'August' or m == 'October' or m == 'December':
                count = 31
            else:
                if m == 'February':
                    if int(y) % 4 == 0:
                        count = 29
                    else:
                        count = 28
                else:
                    count = 30

            counter = 0
            for d in day_list[0 : day_list.index(str(datetime.datetime.today().day))]:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            for d in list(day_list[day_list.index(str(datetime.datetime.today().day)) : day_list.index(str(count)) + 1]):
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=d, callback_data=f'{y}/{m}/{d}'))

            while counter % 7 != 0:
                counter += 1
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month < datetime.datetime.today().month:
            for q in range(35):
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Выберите дату:', reply_markup=calendar_keyboard.as_markup())
            return

@main_router.callback_query(F.data == ' ', StateFilter(FSM_conference.date_change))
async def skipper(callback : CallbackQuery, state : FSMContext):
    await state.set_state(FSM_conference.date_change)
    await callback.answer()      



@main_router.callback_query(F.data != ' ', StateFilter(FSM_conference.date_change))
async def calen_change(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    res = datetime.datetime.strptime(callback.data, '%Y/%B/%d')
    if res.month > 9:
        if res.day > 9:
            final_res = f'{res.year}/{res.day}/{res.month}'
        else:
            final_res = f'{res.year}/0{res.day}/{res.month}'
    else:
        if res.day > 9:
            final_res = f'{res.year}/{res.day}/0{res.month}'
        else:
            final_res = f'{res.year}/0{res.day}/0{res.month}'
    final_res = final_res[5:]
    if final_res:
        await state.update_data(Дата=final_res)
        hall = absolute_data.hall
        time_buttons = await generate_time_buttons(final_res, hall, f'@{callback.message.from_user.username}')
        await callback.message.answer('Укажите время, когда начинается встреча:', reply_markup=time_buttons.as_markup())
        await state.set_state(FSM_conference.timer_first_change)


@main_router.callback_query(StateFilter(FSM_conference.timer_first_change))
async def beginning_change(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        res = datetime.datetime.strptime(callback.data, '%H:%M')
        final_res = res.strftime('%H:%M')
        await state.update_data(С=final_res)
        dictionary = await state.get_data()
        date = dictionary['Дата']
        hall = absolute_data.hall
        time_buttons = await generate_time_buttons(date, hall, f'@{callback.message.from_user.id}')
        await callback.message.edit_text('Укажите время, когда встреча заканчивается', reply_markup=time_buttons.as_markup())
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
            # Gather all occupied start and end times
            occupied_start_times = [conflict[3] for conflict in conflicts]
            occupied_end_times = [conflict[4] for conflict in conflicts]

            # Generate available time buttons considering occupied times
            start_time_buttons = await generate_time_buttons(date, hall, user=f'@{callback.message.from_user.username}', is_start_time=True,
                                                             occupied_times=occupied_start_times)
            end_time_buttons = await generate_time_buttons(date, hall, user=f'@{callback.message.from_user.username}', is_start_time=False,
                                                           occupied_times=occupied_end_times)

            # Notify user and request new time choices
            conflict_messages = '\n'.join(
                [f'Забронировано пользователем {conflict[1]} с {conflict[3]} по {conflict[4]} (ID: {conflict[0]})'
                 for conflict in conflicts]
            )
            await callback.message.answer(
                f'Время уже занято.\nКонфликтующие брони:\n{conflict_messages}\nПожалуйста, выберите другое время.',
                reply_markup=start_time_buttons
            )
            await callback.message.answer('Укажите время, когда заканчивается встреча:', reply_markup=end_time_buttons)
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
            await callback.message.answer(
                f'Бронь успешно перенесена.\nЗал: {hall}\nДата: {date}\nС: {start_time}\nПо: {end_time}',
                reply_markup=start_mark_up.as_markup(
                    resize_keyboard=True,
                    input_field_placeholder='Что хотите сделать?'
                ))
        else:
            await callback.message.answer(f'Ошибка: Не удалось обновить бронь. ID: {booking_id}',
                                          reply_markup=start_mark_up.as_markup(
                                              resize_keyboard=True,
                                              input_field_placeholder='Что хотите сделать?'
                                          ))
        await state.clear()

    except Exception as e:
        #до этого бот просто отправлял сообщение со ошибкой, а сейчас проверяет конфликтующие брони
        # await callback.message.answer(f'Произошла ошибка: {str(e)}', reply_markup=start_mark_up.as_markup(
        #     resize_keyboard=True,
        #     input_field_placeholder='Что хотите сделать?'
        # ))
        connection = sqlite3.connect('datebase.db')
        cursor = connection.cursor()

        # Check for time conflicts
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
            time_but = await generate_time_buttons(date, hall, f'@{callback.message.from_user.username}')
            await callback.message.answer(
                f'Время уже занято.\nКонфликтующие брони:\n{conflict_messages}\nПожалуйста, выберите другое время.',
                reply_markup=time_but.as_markup()
            )
            await callback.message.answer('Укажите время, когда начинается встреча:', reply_markup=time_but.as_markup())
            await state.set_state(FSM_conference.timer_first_change)  # Return to start time selection
            return


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

    await callback.answer()
    await callback.message.answer('Бронь успешно отменена.', reply_markup=start_mark_up.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Что хотите сделать?'
    ))
    await state.clear()


# async def generate_time_buttons(date: str, hall: str):
#     connection = sqlite3.connect('datebase.db')
#     cursor = connection.cursor()
#     query = '''
#         SELECT time_of_beginning, time_of_ending
#         FROM user_booking_data
#         WHERE date = ? AND hall = ?
#     '''
#     cursor.execute(query, (date, hall))
#     bookings = cursor.fetchall()
#     connection.close()

#     # Generate time buttons
#     time_button = InlineKeyboardBuilder()
#     for hour in range(7, 23):  # Start from 7:00
#         for minute in range(0, 60, 30):  # Assuming 30-minute intervals
#             time_str = f'{hour:02d}:{minute:02d}'
#             if hour == 23 and minute > 0:  # Stop generating buttons after 23:00
#                 break
#             if any(start <= time_str <= end for start, end in bookings):
#                 time_button.add(InlineKeyboardButton(text=f' ❌{time_str} ❌', callback_data=time_str))
#             else:
#                 time_button.add(InlineKeyboardButton(text=time_str, callback_data=time_str))
#     time_button.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
#     time_button.adjust(4)  # Adjust buttons per row
#     return time_button










async def generate_time_buttons(date: str, hall: str, user):
    connection = sqlite3.connect('datebase.db')
    cursor = connection.cursor()
    query = '''
        SELECT time_of_beginning, time_of_ending
        FROM user_booking_data
        WHERE date = ? AND hall = ? 
    '''
    cursor.execute(query, (date, hall))
    bookings = cursor.fetchall()
    connection.close()

    connection_second = sqlite3.connect('datebase.db')
    cursor_second = connection_second.cursor()    

    #дополнительный запрос для извлечения броней других людей на этот же зал в этот же день
    check_query = '''
                  SELECT time_of_beginning, time_of_ending FROM user_booking_data
                  WHERE username != ? AND hall = ? AND date = ?
                  '''

    cursor_second.execute(check_query, (user, hall, date))
    list_out_of_username = cursor_second.fetchall()
    connection_second.commit()
    connection_second.close()
    unavailable_list = []
    for i in list_out_of_username:
        for f in i:
            unavailable_list.append(f)

    # Generate time buttons
    time_button = InlineKeyboardBuilder()
    for hour in range(7, 23):  # Start from 7:00
        for minute in range(0, 60, 30):  # Assuming 30-minute intervals
            time_str = f'{hour:02d}:{minute:02d}'
            if hour == 23 and minute > 0:  # Stop generating buttons after 23:00
                break
            if any(start <= time_str <= end for start, end in bookings):
                if time_str not in unavailable_list: #если бронь не находится в списке чужих броней, то кнопка добавляется без крестика
                    time_button.add(InlineKeyboardButton(text=time_str, callback_data=time_str))
                else:
                    time_button.add(InlineKeyboardButton(text=f' ❌{time_str} ❌', callback_data=f' ❌{time_str} ❌'))
                    
            else:
                time_button.add(InlineKeyboardButton(text=time_str, callback_data=time_str))
    time_button.add(InlineKeyboardButton(text='Главное меню', callback_data='return_to_main_menu'))
    time_button.adjust(4)  # Adjust buttons per row
    return time_button