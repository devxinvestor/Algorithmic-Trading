import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from datetime import datetime as dt
from stock_screen import Stock

# Set up the email
sender_email = 'myemail@gmail.com'
sender_password = 'randompassword'
recipient_emails = ['randomemail@gmail.com']
subject = 'Algorithmic Trading: Daily Update'
body = f'''Hello! Today is {dt.now().strftime("%A, %B %d, %Y")}. Here are the stocks to check out:

'''

while True:
    now = dt.now()
    if (now.hour == 9 and now.minute == 0 and now.second == 0) and (dt.now().strftime('%A') != 'Saturday' and (dt.now().strftime('%A') != 'Sunday'):
        stock = Stock("One year")
        stocks = stock.get_tickers(12)
        stock_data = stock.get_stock_data(stocks)
        PSAR = stock.get_PSAR_Indicator(stock_data)
        RSI = stock.get_RSI(stock_data)
        PSAR_indicator = f'PSAR Indicator: {stock.get_PSAR_Indicator(stock_data)}\n\n'
        RSI_indicator = f'RSI Indicator: {stock.get_RSI(stock_data)}\n\n'
        PSAR_RSI_indicator = f'PSAR and RSI Indicator: {list(set(PSAR) & set(RSI))}\n\n'
        ADX_indicator = f'ADX Indicator: {stock.get_ADX(stock_data)}\n\n'
        Short_SMA_indicator = f'10 and 20 SMA Indicator: {stock.get_Short_SMA_Crossover(stock_data)}\n\n'
        Long_SMA_indicator = f'20 and 50 SMA Indicator: {stock.get_Long_SMA_Crossover(stock_data)}\n\n'

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ', '.join(recipient_emails)
        message['Subject'] = subject
        message.attach(MIMEText(body + PSAR_indicator + RSI_indicator + PSAR_RSI_indicator + ADX_indicator + Short_SMA_indicator + Long_SMA_indicator, 'plain'))

        smtp_server = 'smtp.gmail.com'
        port = 587

        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_emails, message.as_string())
        server.quit()
        print('Email sent at', now)
        time.sleep(60*60)
