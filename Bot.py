import logging
import apiai, json

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

"""У бота есть ветка команд
    Попытался прикрутить Dialogflow"""

HELLO,  HOWAREYOU, TYPING_CHOICE, DIALOG = range(4)
hello_array=['hi', 'hello', 'привет', "здравствуй", "здравствуйте"]
unknow= "Я тебя не понимаю("

reply_keyboard = [['Привет'],
                  ['/calc'],
                  ['/done']]

reply_keyboard_inf = [["Возраст"],
                     ["Пол"],
                     ["Имя"], ["Dialog"],
                     ["Назад"]]

reply_keyboard_over = [["Отмена"]]

#flag=0
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
markup_inf = ReplyKeyboardMarkup(reply_keyboard_inf, one_time_keyboard=True)
markup_over = ReplyKeyboardMarkup(reply_keyboard_over, one_time_keyboard=True)

def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    update.message.reply_text(
        "Привет, я бот "
        "Напиши мне привет, если хочешь пообщаться",
        reply_markup=markup)
    return HELLO

def hello(update, context):
    text = update.message.text
    
    if text.lower() in  hello_array or text.lower() == 'назад':
        
        if text.lower() == 'назад':
            update.message.reply_text("Заканчиваю разговор")
            return ConversationHandler.END
        
        update.message.reply_text(
        "Отлично, разговор начат!"
        "Можешь мне сообщить что-нибудь о себе", reply_markup=markup_inf)
        return HOWAREYOU
    
    else:
        update.message.reply_text(unknow)
        return HELLO


def howareyou(update, context):
    text = update.message.text
    if text.lower() == 'dialog':
        return DIALOG
    if text.lower() == 'назад':
        update.message.reply_text("Возвращаюсь обратно.", reply_markup=markup_inf)
        return HELLO
    
    context.user_data['choice'] = text
    update.message.reply_text(' {}? Ну хорошо, послушаем!'.format(text.lower()))
    return TYPING_CHOICE

  
def getInf(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user = update.message.from_user
    if category=="Имя" and text!= user.first_name:
           update.message.reply_text("Мне кажется, ты что-то скрываешь...")
    user_data[category] = text
    del user_data['choice']
    update.message.reply_text("Я знаю о тебе:"
                              "{} Можешь рассказать мне что-нибудь еще"
                              .format(facts_to_str(user_data)),
                              reply_markup=markup_inf)

    return HOWAREYOU


def done(update, context):
    user = update.message.from_user
    text= "Заканчиваю разговор, " + user.first_name
    update.message.reply_text("Заканчиваю разговор")
    return ConversationHandler.END
          
    
def calc(update, context): 
    number= str(int(' '.join(context.args))**2)
    text = "Возвращаю тебе твое число в квадрате" +" " + number
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    

def ourdialog(update, context):
    request = apiai.ApiAI('a7311f4ce3874dc294d9754f4b0d68cb').text_request() 
    request.lang = 'ru' 
    request.session_id = '' 
    request.query = update.message.text 
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech'] 
    
    if request.query.lower() == 'отмена':
        update.message.reply_text("Ну отмена так отмена.")
        return ConversationHandler.END
    
    if response:
        update.message.reply_text(response, reply_markup=markup_over)
        return DIALOG
    else:
        update.message.reply_text(unknow)
        return DIALOG


def main():
    
    REQUEST_KWARGS={'proxy_url': 'socks4://171.103.9.22:4145/', 'urllib3_proxy_kwargs': {
        'assert_hostname': 'True',
       'cert_reqs': 'CERT_NONE'
    }}
    
    updater = Updater("1029121456:AAE1obyCzUQt1y07wqh2Uu0u_Gh6gTAK96s", use_context=True,  request_kwargs=REQUEST_KWARGS)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            HELLO: [MessageHandler(Filters.text, hello) ],
            
            HOWAREYOU:[MessageHandler(Filters.text,howareyou)],

            TYPING_CHOICE: [MessageHandler(Filters.text,getInf)],
            
            DIALOG: [MessageHandler(Filters.text, ourdialog)]
        },

        fallbacks=[CommandHandler("done", done)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('calc', calc))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
