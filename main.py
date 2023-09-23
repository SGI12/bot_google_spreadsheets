from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import  InlineKeyboardButton, InlineKeyboardMarkup
import gspread
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from threading import Timer
CREDENTIALS_FILE = 'python-parser-399821-4a635701fe08.json' 
API_TOKEN = '6062085327:AAH7OiEKdvPSBDqItjnI4MTSdMoCvGblRxw'


def clear_local_storage():
    Info.user_schedule = ''
    print('Local storage has cleared.')

def get_shedule(user_name):
   
    gc = gspread.service_account()

    sh = gc.open("Таблица для тестов") 

    worksheet = sh.get_worksheet(0)

    cell = worksheet.find(user_name)

    user_row_number = cell.row


    last_col=12
    shedule_text=''
    for i in range (6, last_col+1, 2): 
        class_date = str(worksheet.cell(2, i).value)
        class_description = str(worksheet.cell(user_row_number, i).value)
        if class_description == 'None':
            class_description = 'Занятий нет. Отдыхаем!🎉'
        shedule_text+="\n<b>Дата занятий</b>" + '\n' + class_date + '\n' + class_description
    answer = "Ваше расписание на неделю:\nФамилия ученика: " + user_name + shedule_text
    return (answer)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Info:
    user_schedule = ''


class GetMessage(StatesGroup):
    answer = State()

@dp.message_handler(commands=['start'])
async def start_dialog(message: types.Message):
    await GetMessage.answer.set()
    await message.reply("Пожалуйста, напишите фамилию ученика, расписание которого хотите увидеть:")



@dp.message_handler(state=GetMessage.answer)
async def process_message(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        if (Info.user_schedule == ''):
            user_answer = get_shedule(user_message)
        else:
            user_answer = '\n Делаем запрос в локальное хранилище!\n' + Info.user_schedule
        


    Info.user_schedule = user_answer

    await bot.send_message(
            message.from_user.id,
            user_answer,
            reply_markup=None,
            parse_mode='HTML',
        )
    
  
    await state.finish() 

    t = Timer(14.0, clear_local_storage)
    t.start()
    print(Info.user_schedule)



if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=False)