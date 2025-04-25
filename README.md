# MySQL Automation Tool

A Streamlit-based web application that provides an intuitive interface for interacting with MySQL databases. The tool supports SQL query execution, natural language to SQL translation, and database management features.

## Features

- SQL Query Execution
- Natural Language to SQL Translation
- Database Schema Visualization
- Test Data Generation
- CSV Export Functionality
- Multi-database Support

## Prerequisites

- Python 3.7+
- MySQL Server
- Groq API Key (for natural language translation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mysql-automation-tool.git
cd mysql-automation-tool
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following variables:
```
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=your_default_database
GROQ_API_KEY=your_groq_api_key
```

## Usage

1. Start the application:
```bash
streamlit run ChatWithDB/app.py
```

2. Access the web interface at `http://localhost:8501`

## Project Structure

- `ChatWithDB/app.py`: Main Streamlit application
- `ChatWithDB/main.py`: Database connection and query execution
- `ChatWithDB/sql_translator.py`: Natural language to SQL translation
- `requirements.txt`: Project dependencies

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Vansh Jaiswal 