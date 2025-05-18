# app/services/auth/auth_templates.py
"""
Common HTML templates for authentication-related pages
"""

# Common HTML templates
HTML_TEMPLATES = {
    "verification_success": """
    <html>
        <head>
            <title>Email Verified</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; text-align: center; }
                h1 { color: #28a745; }
                p { margin: 20px 0; }
                .btn { background: #007bff; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; display: inline-block; }
            </style>
        </head>
        <body>
            <h1>Email Successfully Verified!</h1>
            <p>Your account has been verified. You can now log in to your account.</p>
            <a href="/" class="btn">Go to Login</a>
        </body>
    </html>
    """,
    
    "password_reset_success": """
    <html>
        <head>
            <title>Password Reset Success</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; text-align: center; }
                h1 { color: #28a745; }
                p { margin: 20px 0; }
                .btn { background: #007bff; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; display: inline-block; }
            </style>
        </head>
        <body>
            <h1>Password Reset Successful!</h1>
            <p>Your password has been updated successfully.</p>
            <a href="/" class="btn">Go to Login</a>
        </body>
    </html>
    """
}

def get_reset_password_form(token: str) -> str:
    """Generate password reset form HTML"""
    return f"""
    <html>
        <head>
            <title>Reset Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; }}
                .form-group {{ margin-bottom: 15px; }}
                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
                button {{ background: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }}
                .password-requirements {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; }}
                .error {{ color: red; display: none; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <h1>Reset Your Password</h1>
            <form id="resetForm" method="POST" action="/api/reset-password-confirm">
                <input type="hidden" name="token" value="{token}">
                <div class="form-group">
                    <label for="new_password">New Password</label>
                    <input type="password" id="new_password" name="new_password" required>
                    <div class="error" id="password-error">Password must be at least 8 characters with uppercase, lowercase, numbers, and special characters</div>
                </div>
                <div class="form-group">
                    <label for="confirm_password">Confirm Password</label>
                    <input type="password" id="confirm_password" name="confirm_password" required>
                    <div class="error" id="confirm-error">Passwords do not match</div>
                </div>
                <div class="password-requirements">
                    Password must contain at least 8 characters including:
                    <ul>
                        <li>At least one uppercase letter</li>
                        <li>At least one lowercase letter</li>
                        <li>At least one number</li>
                        <li>At least one special character (!@#$%^&*...)</li>
                    </ul>
                </div>
                <button type="submit">Reset Password</button>
            </form>
            
            <script>
                document.getElementById('resetForm').addEventListener('submit', function(e) {{
                    const password = document.getElementById('new_password').value;
                    const confirmPassword = document.getElementById('confirm_password').value;
                    let valid = true;
                    
                    // Reset errors
                    document.getElementById('password-error').style.display = 'none';
                    document.getElementById('confirm-error').style.display = 'none';
                    
                    // Check password strength
                    const hasUppercase = /[A-Z]/.test(password);
                    const hasLowercase = /[a-z]/.test(password);
                    const hasNumber = /[0-9]/.test(password);
                    const hasSpecial = /[!@#$%^&*(),.?":{{}}|<>]/.test(password);
                    
                    if (password.length < 8 || !hasUppercase || !hasLowercase || !hasNumber || !hasSpecial) {{
                        document.getElementById('password-error').style.display = 'block';
                        valid = false;
                    }}
                    
                    // Check password match
                    if (password !== confirmPassword) {{
                        document.getElementById('confirm-error').style.display = 'block';
                        valid = false;
                    }}
                    
                    if (!valid) {{
                        e.preventDefault();
                    }}
                }});
            </script>
        </body>
    </html>
    """