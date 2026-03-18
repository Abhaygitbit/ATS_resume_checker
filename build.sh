apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt