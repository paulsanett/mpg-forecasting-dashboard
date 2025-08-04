#!/usr/bin/env python3
"""
AUTOMATED DAILY PARKING REVENUE FORECASTING
Runs daily forecasts and generates email reports automatically
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta

# Try to import email modules, fall back to file-only mode if they fail
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    from email.mime.base import MimeBase
    from email import encoders
    EMAIL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Email modules not available: {e}")
    print("📁 Will save reports to files instead of sending emails")
    EMAIL_AVAILABLE = False

class DailyForecastAutomation:
    def __init__(self):
        self.forecast_dir = "/Users/PaulSanett/Dropbox/Millenium Parking Garages/Financials/Forecast/Windsurf Forecasting Tool"
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',  # Change as needed
            'smtp_port': 587,
            'sender_email': '',  # TO BE CONFIGURED
            'sender_password': '',  # TO BE CONFIGURED (use app password)
            'recipient_email': ''  # TO BE CONFIGURED
        }
    
    def run_daily_forecast(self):
        """Run the production forecast system"""
        print(f"🔮 Running Daily Forecast - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        try:
            # Change to forecast directory
            os.chdir(self.forecast_dir)
            
            # Run the production forecast system
            result = subprocess.run([
                sys.executable, 'production_forecast_system.py'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Forecast generation successful")
                return True, result.stdout
            else:
                print(f"❌ Forecast generation failed: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            print("❌ Forecast generation timed out")
            return False, "Process timed out after 5 minutes"
        except Exception as e:
            print(f"❌ Error running forecast: {e}")
            return False, str(e)
    
    def prepare_email_content(self):
        """Prepare email content with forecast results"""
        try:
            # Find the most recent timestamped email reports
            reports_dir = os.path.join(self.forecast_dir, "Reports")
            
            # Get most recent timestamped reports
            validated_files = [f for f in os.listdir(reports_dir) if f.startswith('email_report_validated_') and f.endswith('.txt')]
            conservative_files = [f for f in os.listdir(reports_dir) if f.startswith('email_report_conservative_') and f.endswith('.txt')]
            
            # Use most recent files
            validated_report_path = os.path.join(reports_dir, max(validated_files)) if validated_files else None
            conservative_report_path = os.path.join(reports_dir, max(conservative_files)) if conservative_files else None
            
            validated_content = ""
            conservative_content = ""
            
            if os.path.exists(validated_report_path):
                with open(validated_report_path, 'r') as f:
                    validated_content = f.read()
            
            if os.path.exists(conservative_report_path):
                with open(conservative_report_path, 'r') as f:
                    conservative_content = f.read()
            
            # Create comprehensive email
            email_subject = f"Daily Parking Revenue Forecast - {datetime.now().strftime('%Y-%m-%d')}"
            
            email_body = f"""
DAILY PARKING REVENUE FORECAST
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 VALIDATED FORECAST (Historically-Validated Multipliers)
{validated_content}

🛡️ CONSERVATIVE FORECAST (Safety Multipliers)  
{conservative_content}

📊 FORECAST METHODOLOGY:
- All event multipliers validated against {3126:,} historical records
- Lollapalooza impact: 1.67x (validated from 16 historical samples)
- Sports events: 1.30x (validated from historical data)
- Festivals: 1.25x (validated from historical data)
- Performances: 1.20x-1.40x (validated from historical data)

📁 ATTACHMENTS:
- production_forecast_validated.csv (Detailed validated forecast)
- production_forecast_conservative.csv (Detailed conservative forecast)

🤖 AUTOMATION STATUS:
This forecast was generated automatically by the Production Parking Revenue Forecasting System.
For questions or adjustments, contact your system administrator.

---
Production Parking Revenue Forecasting System v2.0
Historically-Validated Event Impact Analysis
"""
            
            return email_subject, email_body
            
        except Exception as e:
            print(f"❌ Error preparing email content: {e}")
            return None, None
    
    def send_email_report(self, subject, body):
        """Send email report with CSV attachments"""
        if not EMAIL_AVAILABLE:
            print("⚠️  Email functionality not available. Saving report to file instead.")
            self.save_report_to_file(subject, body)
            return False
            
        if not all([
            self.email_config['sender_email'],
            self.email_config['sender_password'], 
            self.email_config['recipient_email']
        ]):
            print("⚠️  Email configuration incomplete. Saving report to file instead.")
            self.save_report_to_file(subject, body)
            return False
        
        try:
            # Create message
            msg = MimeMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MimeText(body, 'plain'))
            
            # Attach most recent timestamped CSV files from Reports folder
            reports_dir = os.path.join(self.forecast_dir, "Reports")
            
            # Find most recent CSV files
            validated_csvs = [f for f in os.listdir(reports_dir) if f.startswith('production_forecast_validated_') and f.endswith('.csv')]
            conservative_csvs = [f for f in os.listdir(reports_dir) if f.startswith('production_forecast_conservative_') and f.endswith('.csv')]
            
            csv_files = []
            if validated_csvs:
                csv_files.append(max(validated_csvs))
            if conservative_csvs:
                csv_files.append(max(conservative_csvs))
            
            for filename in csv_files:
                filepath = os.path.join(reports_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, "rb") as attachment:
                        part = MimeBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['sender_email'], self.email_config['recipient_email'], text)
            server.quit()
            
            print(f"✅ Email sent successfully to {self.email_config['recipient_email']}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            print("💾 Saving report to file instead...")
            self.save_report_to_file(subject, body)
            return False
    
    def save_report_to_file(self, subject, body):
        """Save report to file when email fails"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"daily_forecast_report_{timestamp}.txt"
        filepath = os.path.join(self.forecast_dir, "Reports", filename)
        
        with open(filepath, 'w') as f:
            f.write(f"SUBJECT: {subject}\n\n")
            f.write(body)
        
        print(f"💾 Report saved to: {filename}")
    
    def run_automation(self):
        """Run the complete daily automation process"""
        print("🤖 STARTING DAILY FORECAST AUTOMATION")
        print("=" * 60)
        
        # Step 1: Run forecast
        success, output = self.run_daily_forecast()
        if not success:
            print(f"❌ Automation failed at forecast generation: {output}")
            return False
        
        # Step 2: Prepare email content
        subject, body = self.prepare_email_content()
        if not subject or not body:
            print("❌ Automation failed at email preparation")
            return False
        
        # Step 3: Send email or save to file
        email_sent = self.send_email_report(subject, body)
        
        print("\n✅ DAILY AUTOMATION COMPLETE")
        print(f"   📊 Forecast generated successfully")
        print(f"   📧 Email {'sent' if email_sent else 'saved to file'}")
        print(f"   📁 CSV files available in {self.forecast_dir}")
        
        return True

def setup_email_config():
    """Interactive setup for email configuration"""
    if not EMAIL_AVAILABLE:
        print("📧 EMAIL CONFIGURATION SETUP")
        print("=" * 40)
        print("⚠️  Email modules are not available on this system.")
        print("📁 All reports will be saved to files instead.")
        print("✅ This is perfectly fine - you'll get the same forecast data!")
        return None
        
    print("📧 EMAIL CONFIGURATION SETUP")
    print("=" * 40)
    print("To enable automated email delivery, please provide:")
    print("1. Gmail account (or other SMTP email)")
    print("2. App password (not your regular password)")
    print("3. Recipient email address")
    print("\nFor Gmail:")
    print("- Enable 2-factor authentication")
    print("- Generate an 'App Password' in Google Account settings")
    print("- Use the app password, not your regular password")
    print("\nLeave blank to skip email setup (reports will be saved to files)")
    print()
    
    sender_email = input("Sender email address: ").strip()
    if not sender_email:
        print("⚠️  Skipping email setup. Reports will be saved to files.")
        return None
    
    sender_password = input("App password (hidden): ").strip()
    recipient_email = input("Recipient email address: ").strip()
    
    if not all([sender_email, sender_password, recipient_email]):
        print("⚠️  Incomplete configuration. Reports will be saved to files.")
        return None
    
    config = {
        'sender_email': sender_email,
        'sender_password': sender_password,
        'recipient_email': recipient_email
    }
    
    # Save config to file
    config_file = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/email_config.json"
    import json
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Email configuration saved to {config_file}")
    print("⚠️  Keep this file secure - it contains your email credentials")
    
    return config

def load_email_config():
    """Load email configuration from file"""
    config_file = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/email_config.json"
    
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    return None

def main():
    print("🤖 DAILY PARKING FORECAST AUTOMATION")
    print("=" * 50)
    
    # Initialize automation
    automation = DailyForecastAutomation()
    
    # Load or setup email configuration
    email_config = load_email_config()
    
    if email_config:
        automation.email_config.update(email_config)
        print(f"✅ Email configuration loaded")
        print(f"   📧 Will send reports to: {email_config.get('recipient_email', 'Not configured')}")
    else:
        print("⚠️  No email configuration found")
        setup_choice = input("Would you like to set up email delivery now? (y/n): ").lower().strip()
        
        if setup_choice == 'y':
            new_config = setup_email_config()
            if new_config:
                automation.email_config.update(new_config)
        else:
            print("📁 Reports will be saved to files instead of emailed")
    
    print()
    
    # Run the automation
    success = automation.run_automation()
    
    if success:
        print("\n🎉 Daily forecast automation completed successfully!")
        print("\nTo run this automatically every day:")
        print("1. macOS: Add to crontab with 'crontab -e'")
        print("   Example: 0 8 * * * /usr/bin/python3 /path/to/daily_forecast_automation.py")
        print("2. Or use macOS Automator to create a daily workflow")
        print("3. Or run manually each morning")
    else:
        print("\n❌ Automation encountered errors. Check the output above.")

if __name__ == "__main__":
    main()
