#!/bin/bash

# Step 1: Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo "Creating a virtual environment..."
    python3 -m venv venv
fi

# Step 2: Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Step 3: Upgrade pip to the latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Step 4: Install required Python dependencies
echo "Installing required Python dependencies..."
pip install beautifulsoup4 duckduckgo-search pandas selenium chromedriver-autoinstaller

# Step 5: Download and install ChromeDriver if needed (since Selenium requires it)
echo "Installing ChromeDriver..."
python3 -m chromedriver_autoinstaller

# Step 6: Run the Python script
echo "Running the Python script..."
python3 searcher.py  # Replace with your actual Python script name

# Step 7: Deactivate the virtual environment
echo "Deactivating the virtual environment..."
deactivate

echo "✅ Script execution completed."