"""
Email templates for Ken platform
Simple and professional design
"""

def get_otp_email_html(username, otp_code):
    """
    Simple OTP verification email
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #ffffff; padding: 40px 40px 20px 40px; border-bottom: 2px solid #f0f0f0;">
                            <h1 style="margin: 0; font-size: 28px; color: #1a1a1a; font-weight: 600;">Ken</h1>
                            <p style="margin: 5px 0 0 0; font-size: 14px; color: #666666;">Earn Money Online</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px 0; font-size: 20px; color: #1a1a1a; font-weight: 600;">Email Verification</h2>
                            
                            <p style="margin: 0 0 20px 0; font-size: 15px; color: #333333; line-height: 1.6;">
                                Hello <strong>{username}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 30px 0; font-size: 15px; color: #333333; line-height: 1.6;">
                                Use the code below to verify your email address:
                            </p>
                            
                            <!-- OTP Code -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 30px 0;">
                                        <div style="background-color: #f8f8f8; border: 2px solid #e0e0e0; border-radius: 8px; padding: 20px; display: inline-block;">
                                            <span style="font-size: 36px; font-weight: bold; color: #1a1a1a; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                                {otp_code}
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 20px 0 0 0; font-size: 13px; color: #666666; line-height: 1.6;">
                                This code expires in <strong>10 minutes</strong>.
                            </p>
                            
                            <p style="margin: 10px 0 0 0; font-size: 13px; color: #666666; line-height: 1.6;">
                                If you didn't request this code, please ignore this email.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f8f8; padding: 30px 40px; border-top: 1px solid #e0e0e0; text-align: center;">
                            <p style="margin: 0 0 5px 0; font-size: 12px; color: #999999;">
                                © 2025 Ken. All rights reserved.
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #999999;">
                                Complete tasks, earn money instantly
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def get_influencer_approved_email_html(username):
    """
    Influencer account approved notification
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #ffffff; padding: 40px 40px 20px 40px; border-bottom: 2px solid #f0f0f0;">
                            <h1 style="margin: 0; font-size: 28px; color: #1a1a1a; font-weight: 600;">Ken</h1>
                            <p style="margin: 5px 0 0 0; font-size: 14px; color: #666666;">Influencer Platform</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <div style="text-align: center; margin-bottom: 30px;">
                                <div style="width: 60px; height: 60px; background-color: #f0f0f0; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                                    <span style="font-size: 30px;">✓</span>
                                </div>
                            </div>
                            
                            <h2 style="margin: 0 0 20px 0; font-size: 20px; color: #1a1a1a; font-weight: 600; text-align: center;">
                                Account Approved!
                            </h2>
                            
                            <p style="margin: 0 0 20px 0; font-size: 15px; color: #333333; line-height: 1.6;">
                                Hello <strong>{username}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 20px 0; font-size: 15px; color: #333333; line-height: 1.6;">
                                Congratulations! Your influencer account has been approved. You can now start creating tasks and promoting your content.
                            </p>
                            
                            <div style="background-color: #f8f8f8; border-left: 3px solid #1a1a1a; padding: 15px; margin: 25px 0;">
                                <p style="margin: 0 0 10px 0; font-size: 14px; color: #333333; font-weight: 600;">
                                    What you can do now:
                                </p>
                                <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #666666; line-height: 1.8;">
                                    <li>Create unlimited tasks</li>
                                    <li>Track your campaign performance</li>
                                    <li>Validate user submissions</li>
                                    <li>Grow your audience</li>
                                </ul>
                            </div>
                            
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 30px;">
                                <tr>
                                    <td align="center">
                                        <a href="https://ken.com/influencer/dashboard/" 
                                           style="display: inline-block; background-color: #1a1a1a; color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 6px; font-size: 15px; font-weight: 600;">
                                            Go to Dashboard
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f8f8; padding: 30px 40px; border-top: 1px solid #e0e0e0; text-align: center;">
                            <p style="margin: 0 0 5px 0; font-size: 12px; color: #999999;">
                                © 2025 Ken. All rights reserved.
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #999999;">
                                Questions? Contact us at support@ken.com
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def get_otp_email_text(username, otp_code):
    """
    Plain text version of OTP email
    """
    return f"""
Ken - Email Verification

Hello {username},

Your verification code is: {otp_code}

This code expires in 10 minutes.

If you didn't request this code, please ignore this email.

---
Ken - Earn Money Online
© 2025 Ken. All rights reserved.
"""


def get_influencer_approved_email_text(username):
    """
    Plain text version of approval email
    """
    return f"""
Ken - Account Approved

Hello {username},

Congratulations! Your influencer account has been approved.

You can now:
- Create unlimited tasks
- Track your campaign performance
- Validate user submissions
- Grow your audience

Login to your dashboard: https://ken.com/influencer/dashboard/

---
Ken - Influencer Platform
© 2025 Ken. All rights reserved.
"""
