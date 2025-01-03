import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7804488689:AAFNLGHbiJOJV0OBDKjg2b3XMh2wZ7Wb7eQ"
LOG_CHANNEL_ID = "-1002350041459"
OWNER_USER_ID = 7494727691

# Global variables for registration status and allowed division
registration_open = False
allowed_division = None

# Command to toggle registration on/off
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global registration_open
    if update.effective_user.id == OWNER_USER_ID:
        if context.args and context.args[0].lower() == 'on':
            registration_open = True
            await update.message.reply_text("Pendaftaran telah dibuka.")
        elif context.args and context.args[0].lower() == 'off':
            registration_open = False
            await update.message.reply_text("Pendaftaran telah ditutup.")
        else:
            await update.message.reply_text("Gunakan /register on untuk membuka pendaftaran atau /register off untuk menutup pendaftaran.")
    else:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")

# Command to set the allowed division for registration
async def set_division(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global allowed_division
    if update.effective_user.id == OWNER_USER_ID:
        if context.args and context.args[0].isdigit():
            division = int(context.args[0])
            if 1 <= division <= 5:
                allowed_division = division
                await update.message.reply_text(f"Pendaftaran dibuka untuk divisi {division}.")
            else:
                await update.message.reply_text("Mohon masukkan nomor divisi yang valid (1-5).")
        else:
            await update.message.reply_text("Gunakan /setdev <nomor_divisi> untuk mengatur divisi yang dibuka.")
    else:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")

# Initial welcome message with video
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not registration_open:
        await update.message.reply_text("Pendaftaran telah ditutup.")
        return

    keyboard = [[InlineKeyboardButton("Lanjutkan Mendaftar", callback_data='continue_register')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video="https://nyxiannetwork.web.id/vid/logo.mp4",
        caption="Selamat datang di pendaftaran admin grup Nyxian Network!",
        reply_markup=reply_markup
    )

# Handler for 'Lanjutkan Mendaftar' button
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'continue_register':
        await query.message.delete()
        keyboard = [[InlineKeyboardButton("Setuju", callback_data='agree_rules')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Rules Admin Nyxian: \n\n"
            "ⓘ Ramah\n"
            "ⓘ Berfikir Tenang\n"
            "ⓘ Bisa Menghormati Admin dan Member Lain\n"
            "ⓘ Memasang Pdn/Title\n"
            "ⓘ Menjalankan Trial 3 Hari\n"
            "ⓘ Siap Diberikan Tugas Apapun Selama Tidak Di Luar Logika\n"
            "ⓘ Bisa Menjaga Privasi Diri Sendiri dan Tidak Membocorkannya ke Sembarang Orang\n\n"
            "Peringatan:\n\n"
            "⚠ Bermain judol tidak akan diterima dalam pendaftaran jadi admin.\n"
            "⚠ Bergabung ke SQ perusuh akan langsung mendiskualifikasi dari pendaftaran.\n"
            "⚠ Toxic berlebihan akan menjadi alasan penolakan tanpa toleransi.",
            reply_markup=reply_markup
        )
    elif query.data == 'agree_rules':
        await query.message.delete()
        await query.message.reply_text(
            "Pendaftaran Devisi Berapa (1-5)?",
            reply_markup=InlineKeyboardMarkup([])
        )
        context.user_data['step'] = 'division'

# Message handler for user responses
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global allowed_division
    user_response = update.message.text
    user_data = context.user_data

    if user_data.get('step') == 'division':
        if user_response.isdigit():
            division = int(user_response)
            if division == allowed_division:
                user_data['division'] = division
                await update.message.reply_text("Pertanyaan 1: Mengapa Anda ingin menjadi admin?")
                user_data['step'] = 'question_1'
            else:
                await update.message.reply_text(
                    f"Maaf, pendaftaran untuk divisi {division} tidak dibuka. "
                    f"Divisi yang sedang dibuka: {allowed_division}."
                )
        else:
            await update.message.reply_text("Mohon masukkan nomor divisi yang valid (1-5).")
    elif user_data.get('step') == 'question_1':
        user_data['answer_1'] = user_response
        await update.message.reply_text("Pertanyaan 2: Apa yang akan Anda lakukan jika terjadi konflik di grup?")
        user_data['step'] = 'question_2'
    elif user_data.get('step') == 'question_2':
        user_data['answer_2'] = user_response
        await update.message.reply_text("Pertanyaan 3: Bagaimana cara Anda menghadapi kritik?")
        user_data['step'] = 'question_3'
    elif user_data.get('step') == 'question_3':
        user_data['answer_3'] = user_response
        await update.message.reply_text("Pertanyaan 4: Bagaimana cara Anda membuat suasana grup tetap nyaman?")
        user_data['step'] = 'question_4'
    elif user_data.get('step') == 'question_4':
        user_data['answer_4'] = user_response
        await update.message.reply_text("Pertanyaan 5: Apakah Anda siap diberikan tugas kapan saja?")
        user_data['step'] = 'question_5'
    elif user_data.get('step') == 'question_5':
        user_data['answer_5'] = user_response
        await update.message.reply_text("Jawaban anda telah terkirim.")

        # Prepare log message
        log_message = (
            f"Nama: {update.effective_user.full_name}\n"
            f"Username: @{update.effective_user.username}\n"
            f"User ID: {update.effective_user.id}\n"
            f"Pendaftaran Devisi: {user_data['division']}\n"
            f"Pertanyaan 1: Mengapa Anda ingin menjadi admin?\n"
            f"Jawaban 1: {user_data['answer_1']}\n"
            f"Pertanyaan 2: Apa yang akan Anda lakukan jika terjadi konflik di grup?\n"
            f"Jawaban 2: {user_data['answer_2']}\n"
            f"Pertanyaan 3: Bagaimana cara Anda menghadapi kritik?\n"
            f"Jawaban 3: {user_data['answer_3']}\n"
            f"Pertanyaan 4: Bagaimana cara Anda membuat suasana grup tetap nyaman?\n"
            f"Jawaban 4: {user_data['answer_4']}\n"
            f"Pertanyaan 5: Apakah Anda siap diberikan tugas kapan saja?\n"
            f"Jawaban 5: {user_data['answer_5']}\n"
        )

        # Send log message to log channel
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=log_message
        )

# Main function to run the bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    set_division_handler = CommandHandler('setdev', set_division)
    button_query_handler = CallbackQueryHandler(handle_button)
    message_response_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)

    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.add_handler(set_division_handler)
    application.add_handler(button_query_handler)
    application.add_handler(message_response_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
