from flask import Flask, jsonify, request
import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

app = Flask(__name__)
fake = Faker()

# -----------------------------
# Helper: Safe Month Increment
# -----------------------------
def add_month(dt):
    if dt.month == 12:
        return dt.replace(year=dt.year + 1, month=1, day=1)
    else:
        return dt.replace(month=dt.month + 1, day=1)

# -----------------------------
# Generate Mock Data (~1000 records)
# -----------------------------
def generate_mock_data():
    data = []

    start_date = (datetime.now() - timedelta(days=730)).replace(day=1)
    end_date = datetime.now()

    current_date = start_date

    while current_date <= end_date:
        # 35–45 records per month → ~1000 total
        num_records = random.randint(35, 45)

        for _ in range(num_records):
            record_date = current_date.replace(day=random.randint(1, 28))

            data.append({
                "id": fake.uuid4(),
                "name": fake.name(),
                "email": fake.email(),
                "amount": round(random.uniform(100, 1000), 2),
                "date": record_date.strftime("%Y-%m-%d"),
                "status": random.choice(["SUCCESS", "FAILED", "PENDING"]),
                "created_at": datetime.now().isoformat()
            })

        current_date = add_month(current_date)

    return pd.DataFrame(data)

# Generate data once at startup
df = generate_mock_data()

# -----------------------------
# API Endpoints
# -----------------------------

@app.route('/')
def home():
    return "Flask Mock API Running 🚀"


# Get all data
@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(df.to_dict(orient="records"))


# Filter by date
@app.route('/data/filter', methods=['GET'])
def filter_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    filtered_df = df.copy()

    if start_date:
        filtered_df = filtered_df[filtered_df['date'] >= start_date]

    if end_date:
        filtered_df = filtered_df[filtered_df['date'] <= end_date]

    return jsonify(filtered_df.to_dict(orient="records"))


# Pagination (useful for batch pipelines)
@app.route('/data/paginate', methods=['GET'])
def paginate_data():
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))

    paginated_df = df.iloc[offset: offset + limit]

    return jsonify({
        "limit": limit,
        "offset": offset,
        "total": len(df),
        "data": paginated_df.to_dict(orient="records")
    })


# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)