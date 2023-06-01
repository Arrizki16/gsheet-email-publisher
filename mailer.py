import smtplib, ssl
import concurrent.futures
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont

class Mailer:
    def __init__(self, main_email, password, sender_email, smtp_server='smtp.office365.com', port=587):
        self.main_email = main_email
        self.password = password
        self.sender_email = sender_email
        self.smtp_server = smtp_server
        self.port = port
        self.subject = "Fill the email subject here!"
        

    def set_body(self, recipient):
        body = f"""Write the subject here (html format)
"""
        return MIMEText(body, 'html')


    def generate_certificate(self, recipient):
        img = Image.open('template_sertifikat.png')
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("Inter-Bold.ttf", 56) 
        text = f"{recipient['fullname'].upper()}"

        img_width, _ = img.size
        text_width, _ = draw.textsize(text, font)
        x = (img_width - text_width) / 2
        draw.text((x,320), text, fill="black", font=font)

        edited_certificate_file = f"output/{recipient['nrp']}_{recipient['fullname']}_certificate.png"
        img.save(edited_certificate_file, "PNG")

        return edited_certificate_file


    def send_email(self, context, recipient):
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = recipient['email']
        message["Subject"] = self.subject
        message.attach(self.set_body(recipient))
            
        certificate_file = self.generate_certificate(recipient)
        if certificate_file.endswith('.png'):
            with open(certificate_file, 'rb') as file:
                img_data = file.read()
            image = MIMEImage(img_data)
            image.add_header('Content-Disposition', 'attachment', filename='certificate.png')
            message.attach(image)
        else:
            print(f"Certificate file {certificate_file} has unsupported format. Skipping attachment.")

        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.starttls(context=context)
            try:
                server.login(self.main_email, self.password)
            except smtplib.SMTPAuthenticationError:
                return("Failed to log in to the SMTP server. Please check your email address and password.")
            
            try:
                server.sendmail(self.sender_email, recipient['email'], message.as_string())
                return f"[SUCCEED] Email sent to {recipient['fullname'].upper()} at {recipient['email']}"
            except smtplib.SMTPRecipientsRefused:
                return f"[FAILED] Email sent to {recipient['fullname'].upper()} at {recipient['email']}"


    def send_email_concurrently(self, recipients):
        context = ssl.create_default_context()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor, open('output.txt', 'w') as fp:
            futures = []
            for recipient in recipients:
                futures.append(executor.submit(self.send_email, context, recipient))

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    fp.write(result + '\n')
                    fp.flush()
                except Exception as e:
                    fp.write(f"An error occurred: {e}\n")
                    fp.flush()