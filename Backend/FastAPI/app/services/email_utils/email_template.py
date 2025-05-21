# app/services/email_template.py
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

def get_email_template(subject, content, button_text=None, button_url=None):
    """
    Generate an email template that works in email clients
    
    Parameters:
    - subject: Email subject
    - content: Main email content (can include HTML)
    - button_text: Optional text for CTA button
    - button_url: Optional URL for CTA button
    
    Returns:
    - message: MIMEMultipart message object ready for sending
    """
    
    # Create message container
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_FROM
    
    # SVG truck icon - embedded directly into the HTML
    truck_svg = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>
    '''
    
    # Create HTML version with table-based layout for email compatibility
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>{subject}</title>
    </head>
    <body style="margin:0; padding:0; font-family: Arial, sans-serif;">
        <!-- Main Table -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5;">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <!-- Content Table -->
                    <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <!-- Header -->
                        <tr>
                            <td align="center" bgcolor="#0f172a" style="padding: 20px; border-top-left-radius: 5px; border-top-right-radius: 5px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td width="60" style="text-align: center;">
                                            <table border="0" cellpadding="0" cellspacing="0" bgcolor="rgba(255,255,255,0.1)" style="border-radius: 8px; display: inline-block;">
                                                <tr>
                                                    <td style="padding: 8px;">
                                                        <!-- Truck SVG Icon -->
                                                        {truck_svg}
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                        <td style="color: #ffffff; font-size: 24px; font-weight: bold; text-align: left; letter-spacing: 0.5px;">
                                            TRUCKING
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px 30px 20px 30px; color: #333333;">
                                {content}
                                
                                {f'''
                                <!-- Button -->
                                <table border="0" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                    <tr>
                                        <td align="center">
                                            <table border="0" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td align="center" bgcolor="#eab308" style="border-radius: 5px;">
                                                        <a href="{button_url}" target="_blank" style="display: inline-block; padding: 12px 30px; font-family: Arial, sans-serif; font-size: 16px; color: #000000; text-decoration: none; border-radius: 5px; font-weight: bold;">
                                                            {button_text}
                                                        </a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                ''' if button_text and button_url else ''}
                                
                                <p style="font-size: 14px; color: #777777; margin-top: 30px;">
                                    If you did not request this email, please ignore it or <a href="{settings.WEBSITE_URL}/contact" style="color: #0066cc;">contact support</a>.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td bgcolor="#0f172a" style="padding: 20px 30px; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="color: #9ca3af; font-size: 14px; text-align: center; padding-bottom: 15px;">
                                            <p style="margin: 0 0 10px 0;">Comprehensive fleet management solutions for modern businesses.</p>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="color: #6b7280; font-size: 12px; text-align: center; padding-top: 20px; border-top: 1px solid #1f2937; margin-top: 20px;">
                                            <p style="margin: 0;">TRUCKING {settings.CURRENT_YEAR}. ALL RIGHTS RESERVED.</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Only attach HTML version (remove plain text version)
    message.attach(MIMEText(html_content, "html"))
    
    return message