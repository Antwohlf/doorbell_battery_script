# Wyze Doorbell Battery Monitor

Monitors your Wyze WiFi doorbell battery and sends email alerts when the battery drops below a configurable threshold.

## Features

- Checks Wyze doorbell battery level via the unofficial [wyze-sdk](https://github.com/shauntarves/wyze-sdk)
- Sends email alerts via [Resend](https://resend.com)
- Runs weekly on GitHub Actions
- Manual testing from terminal

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` with your credentials:

```env
WYZE_EMAIL=your_email@example.com
WYZE_PASSWORD=your_password
WYZE_KEY_ID=your_key_id
WYZE_API_KEY=your_api_key
RESEND_API_KEY=re_your_api_key
SENDER_EMAIL=alerts@yourdomain.com
RECIPIENT_EMAIL=your_email@example.com
```

### 3. Get Wyze API Keys (Required)

As of July 2023, Wyze requires API keys for third-party access:

1. Log in to the [Wyze Developer Console](https://developer-api-console.wyze.com/#/apikey/view)
2. Create a new API key
3. Copy the **API Key** and **Key ID** to your `.env` file

### 4. Resend Setup (for email notifications)

This script uses [Resend](https://resend.com) to send email notifications:

1. Create a [Resend account](https://resend.com)
2. Add and verify your domain
3. Create an API key and add it as `RESEND_API_KEY`
4. Set `SENDER_EMAIL` to an email on your verified domain
5. Set `RECIPIENT_EMAIL` to the email where you want alerts

## Usage

### Local Testing

```bash
# First run - discover your devices
EXPLORE_MODE=true python monitor.py

# Normal run - check battery
python monitor.py

# Test email notification
FORCE_ALERT=true python monitor.py
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BATTERY_THRESHOLD` | 20 | Alert when battery drops below this % |
| `FORCE_ALERT` | false | Send alert regardless of battery level |
| `EXPLORE_MODE` | false | Print all device info for debugging |

## Troubleshooting

### "Doorbell not found"

Run in explore mode to see all devices:

```bash
EXPLORE_MODE=true python monitor.py
```

The doorbell may use an unexpected model/type identifier.

### "Could not determine battery level"

The battery property may be named differently than expected. Check the explore mode output for battery-related fields.

### Authentication errors

- If you have 2FA enabled on Wyze, you'll need to disable it (TOTP automation not currently supported in this script)
