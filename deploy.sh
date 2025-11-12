#!/bin/bash

# Binance Dashboard Deployment Script

set -e

echo "🚀 Starting Binance Dashboard Deployment..."

# Check if API keys are set
if [ -z "$BINANCE_API_KEY" ] || [ -z "$BINANCE_SECRET_KEY" ]; then
    echo "❌ Error: Please set BINANCE_API_KEY and BINANCE_SECRET_KEY environment variables"
    exit 1
fi

# Update and install system packages
echo "📦 Installing system dependencies..."
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git curl nginx certbot

# Create application directory
APP_DIR="/var/www/binance-dashboard"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or copy application files
echo "📁 Setting up application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/binance-dashboard.service > /dev/null <<EOF
[Unit]
Description=Binance Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=BINANCE_API_KEY=$BINANCE_API_KEY
Environment=BINANCE_SECRET_KEY=$BINANCE_SECRET_KEY
Environment=USE_TESTNET=false
ExecStart=$APP_DIR/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx reverse proxy
echo "🌐 Setting up nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/binance-dashboard > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/binance-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Set permissions
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Start and enable services
echo "🔄 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable binance-dashboard
sudo systemctl start binance-dashboard
sudo systemctl enable nginx
sudo systemctl start nginx

# Setup SSL (optional)
if [ -n "$DOMAIN" ]; then
    echo "🔒 Setting up SSL certificate..."
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
fi

echo "✅ Deployment complete!"
echo "🌐 Your dashboard is available at: http://your-domain.com"
echo "📊 Check service status: sudo systemctl status binance-dashboard"