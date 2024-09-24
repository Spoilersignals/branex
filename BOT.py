import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token and admin chat ID
TOKEN = '6682356201:AAGTg_2nLSuwJBjThOde8H-wP3k8-smXU04'
ADMIN_CHAT_ID = 1302914589

# Main menu options
MAIN_MENU = ['ALL SUBJECTS', 'SELECT SUBJECTS', 'DAILY PAPER SUBSCRIPTION', 'GRADE RESULT']

# Subjects list
SUBJECTS = [
    'Maths', 'English', 'Kiswahili', 'Chemistry', 'Biology', 'Home Science', 'Physics',
    'Agriculture', 'Business Studies', 'Computer Studies', 'Geography', 'History', 'CRE'
]

# Week and day options
WEEKS = ['WEEK ONE', 'WEEK TWO', 'WEEK THREE']
DAYS = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']

# Paper options for each day with file IDs (replace with actual file IDs)
PAPERS = {
    'WEEK ONE': {
        'MONDAY': {'ENGLISH PAPER 1': 'file_id_1', 'CHEMISTRY PAPER 1': 'file_id_2'},
        'TUESDAY': {'MATHEMATICS PAPER 1': 'file_id_3', 'ENGLISH PAPER 2': 'file_id_4'},
        'WEDNESDAY': {'CHEMISTRY PAPER 2': 'file_id_5', 'ENGLISH PAPER 3': 'file_id_6'},
        'THURSDAY': {'KISWAHILI PAPER 1': 'file_id_7', 'KISWAHILI PAPER 2': 'file_id_8'},
        'FRIDAY': {'CHEMISTRY PAPER 3': 'file_id_9'}
    },
    'WEEK TWO': {
        'MONDAY': {'MATHS PAPER 2': 'file_id_10', 'KISWAHILI PAPER 3': 'file_id_11'},
        'TUESDAY': {'CRE PAPER 1': 'file_id_12', 'BIOLOGY PAPER 1': 'file_id_13'},
        'WEDNESDAY': {'CRE PAPER 2': 'file_id_14', 'HISTORY PAPER 1': 'file_id_15'},
        'THURSDAY': {'BIOLOGY PAPER 2': 'file_id_16', 'HISTORY PAPER 2': 'file_id_17'},
        'FRIDAY': {'BIOLOGY PAPER 3': 'file_id_18'}
    },
    'WEEK THREE': {
        'MONDAY': {'GEOGRAPHY PAPER 1': 'file_id_19', 'PHYSICS PAPER 1': 'file_id_20'},
        'TUESDAY': {'BUSINESS PAPER 1': 'file_id_21', 'AGRICULTURE PAPER 1': 'file_id_22'},
        'WEDNESDAY': {'GEOGRAPHY PAPER 2': 'file_id_23', 'PHYSICS PAPER 2': 'file_id_24'},
        'THURSDAY': {'AGRICULTURE PAPER 2': 'file_id_25', 'BUSINESS PAPER 2': 'file_id_26'},
        'FRIDAY': {'PHYSICS PAPER 3': 'file_id_27'}
    }
}

# Subject prices
SUBJECT_PRICES = {
    8: 20000,
    7: 18000,
    6: 16000,
    5: 15000,
    4: 13000,
    3: 10000
}

# Grade Result constants
VALID_YEARS = list(range(2005, 2025))
GRADES = [
    'A PLAIN', 'A MINUS', 'B PLUS', 'B PLAIN', 'B MINUS',
    'C PLUS', 'C PLAIN', 'C MINUS', 'D PLUS', 'D PLAIN', 'D MINUS'
]
GRADE_PRICES = {
    'A PLAIN': 38000, 'A MINUS': 33000, 'B PLUS': 30000, 'B PLAIN': 26000,
    'B MINUS': 24000, 'C PLUS': 20000, 'C PLAIN': 17000, 'C MINUS': 14000,
    'D PLUS': 10000, 'D PLAIN': 6000, 'D MINUS': 3500
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome_message = (
        f"Hello {user.first_name} (@{user.username})! "
        "Welcome to Kcse brigertoos VIP bot. This is a subscription bot. "
        "Please use the buttons below to access our services."
    )
    keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in MAIN_MENU]
    keyboard.append([InlineKeyboardButton("Help", callback_data="help")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "This bot provides access to KCSE leakages and papers. "
        "Use the /start command to see the main menu. "
        "For any issues, contact @knec_examiner."
    )
    if update.message:
        await update.message.reply_text(help_text)
    elif update.callback_query:
        await update.callback_query.message.reply_text(help_text)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await help_command(update, context)
        return

    if query.data == "main_menu":
        keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in MAIN_MENU]
        keyboard.append([InlineKeyboardButton("Help", callback_data="help")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Please select an option:", reply_markup=reply_markup)
        return

    if query.data == 'ALL SUBJECTS':
        await handle_all_subjects(query, context)
    elif query.data == 'all_subjects_yes':
        await handle_all_subjects_yes(query, context)
    elif query.data == 'SELECT SUBJECTS':
        await handle_select_subjects(query, context)
    elif query.data.startswith('subject_'):
        await handle_subject_selection(query, context)
    elif query.data == 'submit_subjects':
        await handle_submit_subjects(query, context)
    elif query.data == 'DAILY PAPER SUBSCRIPTION':
        await handle_daily_paper_subscription(query, context)
    elif query.data.startswith('week_'):
        await handle_week_selection(query, context)
    elif query.data.startswith('day_'):
        await handle_day_selection(query, context)
    elif query.data.startswith('paper_'):
        await handle_paper_selection(query, context)
    elif query.data == 'GRADE RESULT':
        await handle_grade_result(query, context)
    elif query.data.startswith('year_'):
        await handle_year_selection(query, context)
    elif query.data == 'overall_subject':
        await handle_overall_subject(query, context)
    elif query.data.startswith('grade_'):
        await handle_grade_selection(query, context)
    elif query.data.startswith('verify_') or query.data.startswith('unverify_'):
        await admin_verify(update, context)
    else:
        await query.edit_message_text("Invalid option. Please try again.")

async def handle_all_subjects(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data="all_subjects_yes")],
        [InlineKeyboardButton("No", callback_data="main_menu")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Would you like to proceed with All Subjects for Ksh 20,000? This includes answers.", reply_markup=reply_markup)

async def handle_all_subjects_yes(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    payment_instructions = (
        "To access All Subjects, please make a payment of Ksh 20,000:\n\n"
        "🔹Dial *334# from your M-Pesa registered line.\n"
        "🔹Next, select send money.\n"
        "🔹Enter No: 0783710330\n"
        "🔹Enter amount: 20,000.\n"
        "🔹Next, enter your M-Pesa PIN.\n"
        "🔹Confirmation Names (Joice)\n\n"
        "After making the payment, please send a screenshot of the transaction."
    )
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(payment_instructions, reply_markup=reply_markup)
    context.user_data['payment_type'] = 'ALL_SUBJECTS'


async def handle_select_subjects(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(subject, callback_data=f"subject_{subject}")] for subject in SUBJECTS]
    keyboard.append([InlineKeyboardButton("Submit", callback_data="submit_subjects")])
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Please select 3-8 subjects:", reply_markup=reply_markup)

async def handle_subject_selection(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    subject = query.data.split('_')[1]
    if 'selected_subjects' not in context.user_data:
        context.user_data['selected_subjects'] = set()
    
    if subject in context.user_data['selected_subjects']:
        context.user_data['selected_subjects'].remove(subject)
    else:
        context.user_data['selected_subjects'].add(subject)
    
    keyboard = [[InlineKeyboardButton(f"{'✅ ' if s in context.user_data['selected_subjects'] else ''}{s}", callback_data=f"subject_{s}")] for s in SUBJECTS]
    keyboard.append([InlineKeyboardButton("Submit", callback_data="submit_subjects")])
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Please select 3-8 subjects:", reply_markup=reply_markup)

async def handle_submit_subjects(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    selected_subjects = context.user_data.get('selected_subjects', set())
    num_subjects = len(selected_subjects)
    if num_subjects < 3 or num_subjects > 8:
        await query.answer("Please select 3-8 subjects!", show_alert=True)
    else:
        subjects = ", ".join(selected_subjects)
        price = SUBJECT_PRICES[num_subjects]
        payment_instructions = (
            f"Verified! Please make a payment of Ksh {price} to access the VIP channel for your selected subjects:\n\n{subjects}\n\n"
            "This includes answers.\n\n"
            "🔹Dial *334# from your M-Pesa registered line.\n"
            "🔹Next, select send money.\n"
            "🔹Enter No: 0783710330\n"
            f"🔹Enter amount: {price}.\n"
            "🔹Next, enter your M-Pesa PIN.\n"
            "🔹Confirmation Names (Joice)\n\n"
            "After making the payment, please send a screenshot of the transaction."
        )
        keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(payment_instructions, reply_markup=reply_markup)
        
        context.user_data['payment_type'] = 'SELECT_SUBJECTS'
        context.user_data['selected_subjects'] = subjects
        context.user_data['price'] = price


async def handle_daily_paper_subscription(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(week, callback_data=f"week_{week}")] for week in WEEKS]
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select a week:", reply_markup=reply_markup)

async def handle_week_selection(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    week = query.data.split('_')[1]
    keyboard = [[InlineKeyboardButton(day, callback_data=f"day_{week}_{day}")] for day in DAYS]
    keyboard.append([InlineKeyboardButton("Back to Weeks", callback_data="DAILY PAPER SUBSCRIPTION")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Select a day for {week}:", reply_markup=reply_markup)

async def handle_day_selection(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, week, day = query.data.split('_')
    keyboard = [[InlineKeyboardButton(paper, callback_data=f"paper_{week}_{day}_{paper}")] for paper in PAPERS[week][day]]
    keyboard.append([InlineKeyboardButton("Back to Days", callback_data=f"week_{week}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Select a paper for {day}, {week}:", reply_markup=reply_markup)

async def handle_paper_selection(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, week, day, paper = query.data.split('_', 3)
    payment_instructions = (
        f"You have selected {paper} for {day}, {week}.\n\n"
        "To access this paper, please make a payment of Ksh 2,500:\n\n"
        "🔹Dial *334# from your M-Pesa registered line.\n"
        "🔹Next, select send money.\n"
        "🔹Enter No: 0783710330\n"
        "🔹Enter amount: 2,500.\n"
        "🔹Next, enter your M-Pesa PIN.\n"
        "🔹Confirmation Names (Joice)\n\n"
        f"After making the payment, please send a screenshot of the transaction along with the subject name: {paper}"
    )
    keyboard = [[InlineKeyboardButton("Back", callback_data=f"day_{week}_{day}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(payment_instructions, reply_markup=reply_markup)
    context.user_data['payment_type'] = 'DAILY_PAPER'
    context.user_data['paper_details'] = f"{week},{day},{paper}"

async def handle_grade_result(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(str(year), callback_data=f"year_{year}")] for year in VALID_YEARS]
    keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Please select the year for grade change (2005-2024):", reply_markup=reply_markup)

async def handle_year_selection(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    year = query.data.split('_')[1]
    context.user_data['selected_year'] = year
    await query.edit_message_text(f"You selected the year {year}. Now, please send your index number together with the school code.")
    context.user_data['state'] = 'WAITING_FOR_INDEX'

async def handle_overall_subject(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(grade, callback_data=f"grade_{grade}")] for grade in GRADES]
    keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Please select the desired grade:", reply_markup=reply_markup)

async def handle_grade_selection(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    grade = query.data.split('_', 1)[1]
    context.user_data['selected_grade'] = grade
    await query.edit_message_text("Please send your Names, index number, and subjects to be changed.")
    context.user_data['state'] = 'WAITING_FOR_DETAILS'

async def admin_verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split('_')
    action = data_parts[0]
    user_id = int(data_parts[1])
    message_id = int(data_parts[2])
    payment_type = data_parts[3]

    if action == 'verify':
        if payment_type == 'ALL_SUBJECTS':
            vip_link = "https://t.me/+abcdefghijklmnop"  # Replace with actual link
            message = f"Your payment for All Subjects has been verified. Here's your VIP link: {vip_link}"
        elif payment_type == 'SELECT_SUBJECTS':
            vip_link = "https://t.me/+qrstuvwxyz123456"  # Replace with actual link
            message = f"Your payment for Selected Subjects has been verified. Here's your VIP link: {vip_link}"
        elif payment_type == 'DAILY_PAPER':
            paper_details = context.user_data.get('paper_details', '').split(',')
            if len(paper_details) == 3:
                week, day, paper = paper_details
                file_id = PAPERS[week][day].get(paper)
                if file_id:
                    await context.bot.send_document(chat_id=user_id, document=file_id, caption=f"Here's your requested paper: {paper}")
                    message = f"Your payment for {paper} ({day}, {week}) has been verified. The paper has been sent to you."
                else:
                    message = f"Your payment has been verified, but there was an issue retrieving the paper. Please contact support."
            else:
                message = "Your payment has been verified, but there was an issue retrieving your paper details. Please contact support."
        elif payment_type == 'GRADE_CHANGE':
            message = "Your payment for grade change has been verified. We will update your details shortly. Please wait for further instructions."
        else:
            message = f"Your payment for {payment_type} has been verified. If you don't receive your content shortly, please contact support."

        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            # Automatically return the user to the main menu
            await send_main_menu(context.bot, user_id)
            await query.edit_message_text("Payment verified and content sent to the user.")
        except Exception as e:
            print(f"Error sending message to user: {e}")
            await query.edit_message_text("Payment verified but there was an error sending content to the user.")
    elif action == 'unverify':
        try:
            reject_message = (
                "We're sorry, but the payment you made was invalid. "
                "Please try again and state your name for further confirmation."
            )
            await context.bot.send_message(chat_id=user_id, text=reject_message)
            # Automatically return the user to the main menu
            await send_main_menu(context.bot, user_id)
            await query.edit_message_text("Payment marked as invalid. User has been notified.")
        except Exception as e:
            print(f"Error sending message to user: {e}")
            await query.edit_message_text("Payment marked as invalid but there was an error notifying the user.")

    # Clear the payment-related data from the user's context
    context.user_data.pop('payment_type', None)
    context.user_data.pop('paper_details', None)
    context.user_data.pop('payment_message_id', None)

async def send_main_menu(bot, chat_id):
    keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in MAIN_MENU]
    keyboard.append([InlineKeyboardButton("Help", callback_data="help")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text="Please select an option:", reply_markup=reply_markup)



async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    photo = update.message.photo[-1]
    
    # Store the message ID of the payment screenshot
    context.user_data['payment_message_id'] = update.message.message_id
    
    payment_type = context.user_data.get('payment_type', 'Unknown')
    additional_info = ''
    
    if payment_type == 'ALL_SUBJECTS':
        additional_info = 'All Subjects (Ksh 20,000)'
    elif payment_type == 'SELECT_SUBJECTS':
        subjects = context.user_data.get('selected_subjects', 'No subjects specified')
        price = context.user_data.get('price', 'Unknown')
        additional_info = f'Selected Subjects (Ksh {price}): {subjects}'
    elif payment_type == 'DAILY_PAPER':
        paper_details = context.user_data.get('paper_details', '')
        additional_info = f'Daily Paper (Ksh 2,500): {paper_details}'
    elif payment_type == 'GRADE_CHANGE':
        year = context.user_data.get('selected_year', 'Unknown')
        grade = context.user_data.get('selected_grade', 'Unknown')
        price = GRADE_PRICES.get(grade, 'Unknown')
        additional_info = f'Grade Change (Ksh {price}): Year {year}, Grade {grade}'

    admin_message = await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo.file_id,
        caption=f"Payment screenshot from @{user.username}\nType: {payment_type}\nDetails: {additional_info}"
    )

    keyboard = [
        [InlineKeyboardButton("Verify", callback_data=f"verify_{user.id}_{admin_message.message_id}_{payment_type}")],
        [InlineKeyboardButton("Unverify", callback_data=f"unverify_{user.id}_{admin_message.message_id}_{payment_type}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await admin_message.reply_text("Verify this payment?", reply_markup=reply_markup)
    
    await update.message.reply_text("Thank you for sending the screenshot. Please wait while we verify the payment.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    state = context.user_data.get('state', None)

    if state == 'WAITING_FOR_INDEX':
        context.user_data['index_and_school'] = text
        keyboard = [
            [InlineKeyboardButton("Overall Subject", callback_data="overall_subject")],
            [InlineKeyboardButton("Specific Subjects", callback_data="specific_subjects")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Would you like to change specific subjects or the overall subject?", reply_markup=reply_markup)
        context.user_data['state'] = None
    elif state == 'WAITING_FOR_DETAILS':
        user = update.effective_user
        year = context.user_data.get('selected_year', 'Unknown')
        grade = context.user_data.get('selected_grade', 'Unknown')
        index_and_school = context.user_data.get('index_and_school', 'Unknown')
        
        admin_message = (
            f"New grade change request:\n"
            f"User: @{user.username}\n"
            f"Year: {year}\n"
            f"Index and School: {index_and_school}\n"
            f"Desired Grade: {grade}\n"
            f"Details: {text}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)
        
        price = GRADE_PRICES.get(grade, 'Unknown')
        payment_instructions = (
            f"Thank you for providing the details. The price for changing to {grade} is Ksh {price}.\n\n"
            "🔹Dial *334# from your M-Pesa registered line.\n"
            "🔹Next, select send money.\n"
            "🔹Enter No: 0783710330\n"
            f"🔹Enter amount: {price}.\n"
            "🔹Next, enter your M-Pesa PIN.\n"
            "🔹Confirmation Names (Joice)\n\n"
            "After making the payment, please send a screenshot of the transaction."
        )
        await update.message.reply_text(payment_instructions)
        context.user_data['state'] = None
        context.user_data['payment_type'] = 'GRADE_CHANGE'
    else:
        await update.message.reply_text("I'm not sure how to respond to that. Please use the /start command to access our services or /help for more information.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling()

if __name__ == '__main__':
    main()