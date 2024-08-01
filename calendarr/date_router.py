import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


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
calendar_keyboard.adjust(3, 3, 7)

router = Router()

# @router.message(F.text)
# async def returner(msg : types.Message):
#     await msg.answer('Календарь:', reply_markup=calendar_keyboard.as_markup())

@main_router.callback_query(F.data.lower().contains('next_year'))
async def next_year_func(callback : CallbackQuery):
    await callback.answer()
    calendar_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                             [
                                                 []
                                             ])
    calendar_keyboard = InlineKeyboardBuilder()
    await callback.answer()
    res = callback.data.replace('next_year', '')
    now = datetime.datetime(int(res) + 1, 1, 1)
    year_list = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057', '2058', '2059', '2060']
    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
           '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
           '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

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
    calendar_keyboard.adjust(3, 3, 7)

    await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())

@main_router.callback_query(F.data.lower().contains('last_year'))
async def last_year_func(callback : CallbackQuery):
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
    year_list = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057', '2058', '2059', '2060']
    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
           '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
           '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

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
        calendar_keyboard.adjust(3, 3, 7)
        await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
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
            
    calendar_keyboard.adjust(3, 3, 7)
    await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())

@main_router.callback_query(F.data.lower().contains('next_month'))
async def next_month_func(callback : CallbackQuery):
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
        year_list = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057', '2058', '2059', '2060']
        month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

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
        calendar_keyboard.adjust(3, 3, 7)

        await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
        return
    else:
        now = datetime.datetime(int(res[res.index(' ')+1:]), final_mon, 1)
        if int(res[res.index(' ')+1:]) > datetime.datetime.today().year:
            year_list = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057', '2058', '2059', '2060']
            month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
                '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

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
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
            return
        year_list = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057', '2058', '2059', '2060']
        month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

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
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
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
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month < datetime.datetime.today().month:
            for q in range(35):
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
            return
            
@main_router.callback_query(F.data.lower().contains('last_month'))
async def last_month_func(callback : CallbackQuery):
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
        year_list = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057', '2058', '2059', '2060']
        month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

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
        calendar_keyboard.adjust(3, 3, 7)
        await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
        return
    else:
        now = datetime.datetime(int(res[res.index(' ')+1:]), final_mon, 1)
        if int(res[res.index(' ')+1:]) > datetime.datetime.today().year:
            year_list = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057', '2058', '2059', '2060']
            month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
                '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

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
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
            return
        year_list = ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057', '2058', '2059', '2060']
        month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        day_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

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
            calendar_keyboard.adjust(3, 3, 7)

            await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
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
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
            return
        elif now.month < datetime.datetime.today().month:
            for q in range(35):
                calendar_keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '))
            calendar_keyboard.adjust(3, 3, 7)
            await callback.message.edit_text('Календарь:', reply_markup=calendar_keyboard.as_markup())
            return

@main_router.callback_query(F.data == ' ')
async def skipper(callback : CallbackQuery):
    await callback.answer()      

@main_router.callback_query(F.data != ' ')
async def date_getter(callback : CallbackQuery):
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
    await callback.message.answer(final_res)