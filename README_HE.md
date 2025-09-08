# פרויקט מחסן נתונים וניתוח - Chinook

פרויקט זה נבנה כחלק מהכשרתי כ־Data Analyst.  
הוא מדגים כיצד לעצב מחסן נתונים (DWH), ליישם תהליכי ETL, ולבצע ניתוחים מתקדמים בעזרת SQL ו־Python.

## מודל הנתונים

מסד הנתונים Chinook הוסב לעיצוב **Star Schema** (`dwh2`):

- **טבלאות מימד (Dimensions):** לקוחות, עובדים, שירים, פלייליסטים, מטבעות וכו’.  
- **טבלאות עובדה (Facts):** חשבוניות ושורות חשבונית.

מבנה זה מאפשר להריץ שאילתות אנליטיות בצורה יעילה על פני שאלות עסקיות מגוונות.

![Star Schema](images/star_schema.png)

## תהליך ה־ETL

הוטמע תהליך מלא של ETL (Extract, Transform, Load):

- **Extract (שליפה):** שליפת נתונים גולמיים ממסד הנתונים Chinook ומ־API חיצוני לשערי מטבע.  
- **Transform (עיבוד):** ניקוי וסטנדרטיזציה של הנתונים, המרת ערכים במטבעות, והחלת כללי עסקים.  
- **Load (טעינה):** טעינת הנתונים המעובדים לסכימת `dwh2` (טבלאות מימד ועובדה).

כך מתקבלים נתונים נקיים, אמינים ומוכנים לשימוש עסקי.

## תוצאות ניתוח

דוגמאות לפלטים חזותיים (בגרסת Pandas):

1. **מגמת מכירות חודשית**  
   זיהוי עונתיות ודפוסי צמיחה.  
   ![Monthly Sales Trend](images/PythonAnalyses (pandas)/monthly_sales_trend_bars.png)

2. **5 הלקוחות המובילים (USD לעומת ILS)**  
   השוואת סך ההוצאות בדולרים לעומת בשקלים.  
   ![Top 5 Customers](images/PythonAnalyses (pandas)/top5_customers_spend_usd_ils.png)

3. **עונתיות לפי ז’אנר**  
   בחינת עונתיות במכירות לפי ז’אנרים מובילים.  
   ![Seasonality by Genre](images/PythonAnalyses (pandas)/seasonality_by_genre.png)


> כל ניתוח יושם פעמיים — בעזרת SQL ישיר (באמצעות SQLAlchemy) ובעזרת Pandas.  
> הגרפים שמוצגים כאן מבוססים על Pandas; גם התוצאות ב־SQL כלולות במאגר.

[דו"ח מלא (PDF)](docs/Answer_File_chinook.pdf)

## מבנה הפרויקט

- **`sql/`** – סקריפטים של DDL ושאילתות ניתוח.  
  - `dwh2/` – יצירת סכימה וטבלאות (מימדים ועובדות)  
  - `analysis/` – שאילתות אנליטיות
- **`python/`** – סקריפטים של ETL וניתוח.  
  - `etl/` – סקריפטים לשליפה/עיבוד/טעינה  
  - `analysis/` – ניתוח והצגת גרפים (SQL + Pandas)
- **`data/`** – פלטים מעובדים בלבד (קבצי raw מוחרגים ע"י `.gitignore`).  
- **`images/`** – תרשימים וגרפים (מוצגים בקובץ README).  
- **`docs/`** – מסמכי תיעוד (למשל קובץ PDF).  
- **`requirements.txt`** – תלות חבילות ב־Python.  
- **`.env.example`** – דוגמה לקובץ משתני סביבה (ללא סודות).

## איך להריץ

### 1) יצירת והפעלת סביבה וירטואלית (אופציונלי)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2) התקנת חבילות
```bash
pip install -r requirements.txt
```

### 3) הגדרת משתני סביבה
צרי קובץ בשם `.env` בתיקיית השורש (עפ"י `.env.example`).  
הוסיפי מחרוזת חיבור למסד הנתונים:
```
DB_URL=postgresql://<user>:<password>@localhost:5432/chinook
```

### 4) יצירת סכימה וטבלאות
הריצי את הסקריפטים שבתיקייה `sql/dwh2/` (סדר: create_schema.sql, מימדים ואז עובדות).

### 5) הרצת ETL
הריצי את הסקריפטים שבתיקייה `python/etl/` לשליפת נתונים, עיבוד וטעינה ל־`dwh2`.  
קיים גם סקריפט אופציונלי (`python/etl/currency_api_loader.py`) לשליפת שערי USD→ILS יומיים:

- טווח התאריכים נקבע לפי החשבוניות (למשל stg.invoice / dwh2.fact_invoice)  
- פלט: טבלה `stg.usd_ils_rates`  
- תומך במצב **dry-run** לבדיקה בטוחה

### 6) הרצת ניתוחים
- שאילתות SQL: `sql/analysis/`  
- ניתוחים ב־Python: `python/analysis/`  
- גרפים נשמרים תחת `images/` ו־`data/outputs/`.

מחבר: מור מחלב

