import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load data
url = "https://raw.githubusercontent.com/tim-blackmore/launch-monitor-regression/main/data.csv"
df = pd.read_csv(url)

# Define features and targets
features = ['ball_speed', 'launch_angle', 'spin_rate', 'carry_distance', 'total_distance', 'smash_factor']
targets = ['angle_of_attack', 'club_path', 'face_to_target']

# Drop rows with missing values
df = df.dropna(subset=features + targets)

X = df[features]
y = df[targets]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate each target
for i, target in enumerate(targets):
    print(f"=== {target.upper()} ===")
    print("R² Score:", r2_score(y_test.iloc[:, i], y_pred[:, i]))
    print("MSE:", mean_squared_error(y_test.iloc[:, i], y_pred[:, i]))
    print()