import os
import re
import time
import urllib3
from io import BytesIO

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import telebot
from telebot import TeleBot, types


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

STATIONS = {'AEROPORT HOUARI BOUMEDIENE': '560', 'AIN AFFRA': '39', 'AIN BELDHA': '494', 'AIN BOUZIANE': '518', 'AIN DEFLA': '42', 'AIN DOUZ': '43', 'AIN EL BERD': '44', 'AIN FEZZA': '45', 'AIN HADJEL': '572', 'AIN KECHRA': '466', 'AIN KERMES': '582', 'AIN M LILA': '48', 'AIN NAADJA': '49', 'AIN NOUISSY': '509', 'AIN ROUIBAH': '563', 'AIN SEFRA': '52', 'AIN SENNOUR': '53', 'AIN TAHMIMINE': '55', 'AIN TELLOUT': '56', 'AIN TEMOUCHENT': '413', 'AIN TORKI': '57', 'AIN TOUTA': '58', 'AIN YAGOUT': '59', 'AIN_FEKROUN': '62', 'AKBOU': '67', 'AKID ABBAS': '68', 'ALGER': '69', 'ALGER (AGHA )': '37', 'ALLAGHAN': '70', 'AMMAL': '549', 'ANNABA': '71', 'ARIB': '501', 'ARZEW': '456', 'ATELIERS': '75', 'ATH-MANSOUR': '569', 'AZIB-BEN-ALI-CHERIF': '546', 'AZZABA': '78', 'AZZAGHAR': '513', 'BAB EZZOUAR': '83', 'BABA ALI': '84', 'BAKIRA': '470', 'BARIKA': '85', 'BATNA': '86', 'BAZOUL': '556', 'BECHAR': '88', 'BECHLOUL': '570', 'BEJAIA': '90', 'BENI AMRANE': '94', 'BENI MANSOUR': '95', 'BENI MERED': '96', 'BENI OUNIF': '97', 'BENI SAF': '502', 'BERRAHAL': '538', 'BIBAN EL HADID': '561', 'BIR AISSA AYADA': '547', 'Bir saf saf': '542', 'BIRINE': '574', 'BIRTOUTA': '112', 'BISKRA': '113', 'BLIDA': '114', 'BORDJ BOU ARRERIDJ': '115', 'BORDJ MENAIEL': '80', 'BOU MEDFAA': '118', 'BOUCHEGOUF': '119', 'BOUDAROUA': '120', 'BOUDOUAOU': '121', 'BOUFARIK': '122', 'BOUGHEZOUL': '575', 'BOUGURRA': '579', 'BOUHENNI': '125', 'BOUIRA': '126', 'BOUKADIR': '127', 'BOUKANEFIS': '583', 'BOUKHADRA': '128', 'BOUKHALFA': '129', 'BOUKHAMOUZA': '498', 'BOUMAHRA': '133', 'BOUMERDES': '134', 'BOUTI SAYEH': '573', 'BOUTLELIS': '137', 'CAROUBIER': '141', 'Chabat El Lham': '473', 'CHABOUNIA': '576', 'CHAIBA': '142', 'CHALET DES PINS': '443', 'CHEBAITA M': '143', 'CHIFFA': '145', 'CHIHANI BACHIR': '146', 'CHLEF': '147', 'CONSTANTINE': '148', 'CORSO': '149', 'DAR EL BEIDA': '155', 'DIDOUCH MOURAD': '440', 'DJAMA': '559', 'DJAMAA': '158', 'Djenien Boureizg': '472', 'DJENIENE MESKINE': '450', 'DJERMA': '490', 'DRA EL MIZAN': '162', 'DRAA BENKHEDDA': '150', 'DREA': '164', 'DREAN': '471', 'EL ADJIBA': '89', 'EL AFFROUN': '168', 'EL AMRA': '545', 'EL AMRIA': '170', 'EL AOUINET': '476', 'EL ARROUCHE': '562', 'EL ATTAF': '175', 'EL ESNAM': '179', 'EL GOURZI': '181', 'EL HADJAR': '182', 'EL HAMRI': '183', 'EL HARRACH': '185', 'EL HARROUCH': '186', 'EL KANTARA': '187', 'EL KHARMA': '477', 'EL KHROUB': '189', 'El KSEUR': '529', 'El KSEUR-O-AMIZOUR': '475', 'EL MALEH': '194', 'EL MEGHAIER': '193', 'EL MILIA': '196', 'EL OUTAYA': '198', 'EL-ANCER': '554', 'EL-ANNASSER': '548', 'EL-EULMA': '202', 'EL-KANTARA-GORGES': '523', 'EMDJEZ EDCHICHE': '205', 'ES SENIA': '206', 'Fac Hadj Lakhder': '474', 'FESDIS': '550', 'FORNAKA': '508', 'FRENDA': '581', 'GARITA': '468', 'GDYEL': '462', 'GHAZAOUET': '215', 'GUE DE CONSTANTINE': '218', 'HAI El KASAB': '568', 'HAI EL SABAH': '457', 'HAMMA -MARCH': '517', 'HAMMA BOUZIANE': '480', 'HAMOUDI KROUMA': '478', 'HANIF': '539', 'HASSI AMEUR': '460', 'HASSI BEN OKBA': '461', 'HASSI BOUNIF': '459', 'HASSI EL GHELLA': '46', 'HASSI FEDOUL': '578', 'HASSI MAFSOUKH': '479', 'HASSI MAMECHE': '510', 'HOCEINIA': '447', 'HUSSEIN DEY': '237', 'IGHZER AMOUKRAN': '495', 'IMAMA': '453', 'ISSERS': '240', 'JIJEL': '241', 'KADIRIA': '551', 'KEF NAAJA': '445', 'KEF SALAH': '488', 'KHEDARA': '246', 'KHEMIS.MILLIANA': '242', 'LA MACTA': '522', 'LAKHDARIA': '251', 'LOTTA': '255', "M'DAOUROUCH": '269', "M'DJEZ": '270', "M'SILA": '294', "M'ZITA EL-MCHIR": '295', 'MADROUMA': '484', 'MAGHNIA': '260', 'MANBAA EL GHAZEL': '481', 'MANSOURAH': '265', 'MAZAGRAN': '511', 'MECHERIA': '271', 'MECHROHA': '273', 'MEDJEZ SFA': '274', 'MELIANA': '448', 'MERS EL HADJADJ (GRANDE PLAGE)': '520', 'MERS EL HADJADJ (TERMINUS)': '521', 'MESKIANA': '280', 'MESLOUG': '557', 'MISSERGHINE': '282', 'MOGHRAR': '285', 'MOHAMMADIA': '286', 'MOHGOUN': '464', 'MORSOTT': '289', 'MOSTAGANEM': '504', 'Moudrou': '541', 'MOULEY SLISSEN': '534', 'MOUZAIA': '293', 'NAAMA': '297', 'NACIRIA': '298', 'OAIC KHROUB': '442', 'OGGAZ': '304', 'ORAN': '305', 'OUED AISSI': '446', 'OUED AISSI UNIVERSITE': '530', 'OUED ALI': '326', 'OUED CHOUK': '306', 'OUED DAMOUS': '309', 'OUED DJEMAA': '310', 'OUED DJER': '311', 'OUED FARAH': '483', 'OUED FODDA': '312', 'OUED GHIR': '314', 'OUED HAMIMINE': '487', 'OUED KEBRIT': '316', 'OUED MOUGRAS': '482', 'OUED RHIOU': '318', 'OUED SLY': '319', 'OUED SMAR': '320', 'OUED TINN': '507', 'OUED TLELAT': '322', 'OUED ZIED': '324', 'OUED ZITOUN': '454', 'OULED AMMAR': '571', 'OULED BENZIANE': '503', 'OULED CHOULY': '565', 'OULED DHIA': '330', 'OULED MIMOUN': '329', 'OULED RAHMOUNE': '486', 'OUM BOUAGHI': '338', 'OUMACHE': '489', 'PASTEUR': '485', 'R DEMOUCHE': '342', 'R.U MEDAGUINE MOHAMED': '566', 'RAMDANE DJAMEL': '343', 'RAS EL MA': '345', 'RAS EL OUED': '512', 'REGHAIA': '348', 'REGHAIA INDUSTRIEL': '439', 'REGOUCHE AHMED': '499', 'RELIZANE': '349', 'ROUIBA': '353', 'ROUIBA INDUSTRIEL': '438', 'ROUINA': '500', 'SABRA': '496', 'SAFSAF': '492', 'SAHKI AHMED': '552', 'SAIDA': '531', 'SALAH BOUCHAOUR': '491', 'SETIF': '376', 'SETTARA': '564', 'SI MUSTAPHA': '378', 'SIDI ABD ALLAH': '525', 'SIDI ABD ALLAH  UNIVERSITE': '528', 'SIDI ABEDMOUMEN': '519', 'SIDI ABID': '505', 'SIDI ACHOUR': '465', 'SIDI AICH': '379', 'SIDI ALI BENYOUB': '535', 'SIDI AMAR': '381', 'SIDI BADER': '382', 'SIDI BEL ABBES': '362', 'SIDI BENZERGA': '506', 'SIDI BOUABIDA': '543', 'SIDI BRAHIM': '383', 'SIDI EL HEMISSI': '364', 'SIDI KHALED': '567', 'SIDI LADJEL': '577', 'SIDI LHASSENE': '584', 'SIDI MABROUK': '390', 'SIDI MAROUF': '388', 'SIDI MDJAHED': '449', 'SIDI MEZGHICH': '553', 'SIDI YAHIA': '389', 'SIDI-ABDELAZIZ': '555', 'SIDI-LAKHDAR': '544', 'SIG': '392', 'SKIKDA': '393', 'SOUK AHRAS': '395', 'SOUK-EL-HAD': '537', 'STIL': '558', 'TABIA': '399', 'TADJENANET': '400', 'TADMAIT': '401', 'TAKOUKA': '467', 'TAKRIETS-SEDDOUK': '404', 'TAMALOUS': '405', 'TAMEZRIT-IL-MATTEN': '516', 'TARJA': '409', 'TAZMALT': '410', 'TEBESSA': '411', 'TELEGH': '533', 'TELEGMA': '412', 'TESSALA EL MERDJA': '524', 'THENIA': '415', 'TIARET': '416', 'TIDJELABINE': '417', 'TIOUT': '419', 'TISSEMSILT': '580', 'TIZI OUZOU': '423', 'TLEMCEN': '424', 'TOGHZA': '493', 'TOUGGOURT': '425', 'TRALIMET': '428', 'TUILLERIES': '429', 'YALOU': '540', 'YELLEL': '431', 'YOUB': '532', 'ZAHANA': '432', 'ZELBOUN': '433', 'ZERALDA': '527', 'ZIGHOUT Y': '435'}

bot = TeleBot('6010079103:AAFbufM-nT9Ekd7J_WeT9PrwpvaKnXITuVQ')

# Define the message handler for the "/start" command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, f"👋 مرحباً بك {user_name} في بوت مواقيت القطارات الخاصة بـ SNTF ALGERIA!\n\n"
                                  "يرجى إرسال الأمر /trains لمعرفة مواعيد القطارات بين محطتي الاقلاع والوصول 🚉")

# Define the message handler for the "/info" command
@bot.message_handler(commands=['info'])
def handle_info(message):
    bot.send_message(message.chat.id, f"info")


# Define the message handler for the "/trains" command
@bot.message_handler(commands=['trains'])
def handle_trains(message):
    # Create the markup for the departure station buttons
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for station in STATIONS:
        button = types.KeyboardButton(station)
        markup.add(button)
    # Send the message with the departure station buttons
    bot.send_message(message.chat.id, "🚉 يرجى اختيار محطة الإقلاع الخاصة بك:", reply_markup=markup)

# Define the message handler for the departure station selection
@bot.message_handler(func=lambda message: True)
def handle_departure_station(message):
    message.text = message.text.upper()
    if message.text not in STATIONS:
       bot.send_message(message.chat.id, "❌ تم اختيار محطة الإقلاع غير صالحة. يرجى اختيار محطة صالحة.")
       return
    # Save the departure station code and remove the departure station buttons
    departure_code = STATIONS[message.text]
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, f"🚉 محطة الإقلاع الخاصة بك هي {message.text}", reply_markup=markup)
    # Create the markup for the arrival station buttons
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for station in STATIONS:
        if station != message.text:
            button = types.KeyboardButton(station)
            markup.add(button)
    # Ask for the arrival station and register the next message handler
    bot.send_message(message.chat.id, "🚉 يرجى اختيار محطة الوصول الخاصة بك:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_arrival_station, departure_code, message.text)

def get_url_data(url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Raise an exception if the request was not successful
        return response.text
    except RequestException as e:
        print(f"Error: Connection error - {e}")
        return None

url = None
# Define the message handler for the arrival station selection
def handle_arrival_station(message, departure_code, departure_station):
    # Save the arrival station code and remove the arrival station buttons
    message.text = message.text.upper()
    if message.text not in STATIONS:
        bot.send_message(message.chat.id, "❌ تم اختيار محطة الوصول غير صالحة. الرجاء المحاولة مرة أخرى /trains.")
        return
    arrival_code = STATIONS[message.text]
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, f"🚉 محطة الوصول الخاصة بك هي {message.text}", reply_markup=markup)
    # TODO: Implement the train schedule retrieval and display

    process_msg = bot.send_message(message.chat.id, "جاري معالجة الطلب، الرجاء الانتظار... ⌛️")

    current_date = time.strftime("%Y%m%d")
    current_date2 = time.strftime("%d-%m-%Y")
    global url
    url = "https://www.sntf.dz/index.php/component/sntf/?gd=" + (departure_code) + "&ga=" + (arrival_code) + "&dd=" + (current_date) + "&view=train"
    url_data = get_url_data(url)

    if url_data is None:
        bot.delete_message(message.chat.id, process_msg.message_id)
        bot.send_message(message.chat.id, "❌ An error occurred while retrieving data from the URL. Please try again later.")
        return

    # create a soup object from the response text
    soup = BeautifulSoup(url_data, 'html.parser')

    # find all the rows in the table
    rows = soup.find_all('tr')
    tr = 1
    markup = types.ReplyKeyboardRemove(selective=False)

    # iterate through each row and extract the train number and other information
    if not rows:
        bot.delete_message(message.chat.id, process_msg.message_id)
        bot.send_message(message.chat.id, "❌ لم يتم العثور على قطارات بناءً على المعلمات المحددة. يرجى المحاولة مرة أخرى /trains ")

    else:

        # iterate through each row and extract the train number and other information
        bot.delete_message(message.chat.id, process_msg.message_id)

        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        stop_button = types.KeyboardButton("Stop 🚫")
        keyboard.add(stop_button)

        for row in rows:

            # find the cells in the row
            cells = row.find_all('td')

            # check if the row has cells (some rows are just headers)
            if len(cells) > 0:

                    # extract the train number
                    train_number = cells[0].text.strip()

                    # extract other information (departure time, arrival time, etc.)
                    train_tp = cells[1].text.strip()
                    train_tps = re.sub('\s+', ' ', train_tp).strip()
                    train_tipo = re.sub('\s+', ' ', train_tps).strip()
                    pattern = r'\b[Cc]ircule[^.]*\b'
                    names = re.findall(pattern, train_tipo)
                    names_text = ' '.join(names)

                    train_type = train_tps.replace(names_text, "")
                    departure_gare = cells[2].text.strip()
                    departure_time = cells[3].text.strip()
                    arrival_gare = cells[4].text.strip()
                    arrival_time = cells[5].text.strip()
                    prix_k = cells[7].find('a')['href']
                    prix_link =  ("https://www.sntf.dz" + (prix_k))

                    message_text = f"🚂 *القطار رقم :* {tr}\n\n"

                    message_text += "ℹ️ *معلومات القطار :*\n\n"


                    message_text += f"- _رقم القطار : _ {train_number}\n"
                    message_text += f"- _نوع القطار : _ {train_type}\n\n"

                    message_text += f"🚉 *تفاصيل الرحلة :*\n\n"

                    message_text += f"- _محطة الإقلاع : _ {departure_gare}\n"
                    message_text += f"- _وقت الإقلاع : _ {departure_time}\n\n"

                    message_text += f"- _محطة الوصول : _ {arrival_gare}\n"
                    message_text += f"- _وقت الوصول : _ {arrival_time}\n\n"

                    response2 = requests.get(prix_link, verify=False)
                    html2 = response2.content.decode()
                    soup2 = BeautifulSoup(html2, 'html.parser')
                    tarif_divs = soup2.find_all('div', {'style': ['background:rgb(240,240,240);padding-left:10px;', 'background:rgb(234,234,234);padding-left:10px;']})                    
                    class_names = []
                    prices = []

                    for tarif_div in tarif_divs:
                       class_name = tarif_div.find('b').text
                       prix = tarif_div.find('div', string='Prix').find_next_sibling().text.strip()

                       # Map class names to Arabic equivalents
                       if class_name == "Tarif de la 1ère classe":
                          class_name = "سعر الدرجة الأولى"
                       elif class_name == "Tarif de la 2ème classe":
                          class_name = "سعر الدرجة الثانية"

                       class_names.append(class_name)
                       prices.append(prix)

                    if not class_names or not prices:
                         message_text += "🏷️ *الأسعار :*\n\n"
                         message_text += "- _لا يوجد معلومات عن الأسعار الخاصة بهذا القطار_"
                    else:
                       message_text += "🏷️ *الأسعار :*\n\n"
                       for i in range(len(class_names)):
                             message_text += f"- _{class_names[i]} : _ {prices[i]}\n"

                    bot.send_message(message.chat.id, message_text, parse_mode="Markdown")

                    tr +=1

        keyboard = telebot.types.InlineKeyboardMarkup()
        download_button = telebot.types.InlineKeyboardButton(text='Download PDF', callback_data='download_pdf')
        keyboard.add(download_button)
        bot.send_message(message.chat.id, 'اضغط على الزر إذا كنت ترغب في تحميل ملف PDF لوجهتك 📥', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "download_pdf")
def handle_download_pdf(callback_query):
            # Specific urls
            global url
            pdf_url = "https://www.sntf.dz/index.php/component/sntf/?task=trainspdf"
            headers = {
                "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
                "sec-fetch-dest": "document",
                "referer": url
            }

            # Make a request to the websites
            response = requests.get(url, headers=headers, verify=False)
            cookies = response.cookies.get_dict()
            headers["cookie"] = "; ".join([f"{key}={val}" for key, val in cookies.items()])
            response_pdf = requests.get(pdf_url, headers=headers, verify=False)
            print (headers)
            pdf_filename = "Sntf.pdf"

            pdf_file = BytesIO(response_pdf.content)
            pdf_file.name = pdf_filename

            bot.send_document(callback_query.message.chat.id, pdf_file)
            bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)            

bot.polling()
