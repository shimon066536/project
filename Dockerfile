# שימוש בבסיס Python
FROM python:3.10-slim

# מיקום העבודה
WORKDIR /app

# העתקת קבצים
COPY . /app

# התקנת חבילות
RUN pip install --no-cache-dir -r requirements.txt

# פתיחת הפורט
EXPOSE 5000

# הרצת Flask
CMD ["python", "app.py"]
