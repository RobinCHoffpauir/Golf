#%% 📦 Imports
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import r2_score
from xgboost import XGBRegressor
from sklearn.linear_model import RidgeCV

#%% 🧹 Data Loading and Cleaning
# Replace with your file paths
file_paths = ["7-6-25_range.csv", "7-15-25_range.csv", "range_7-2-25.csv"]
dfs = [pd.read_csv(fp, header=2) for fp in file_paths]
df_combined = pd.concat(dfs, ignore_index=True)

# Fix column header row
header_row = df_combined[df_combined.apply(lambda r: r.astype(str).str.contains('Club Type').any(), axis=1)].index[0]
df_combined.columns = df_combined.iloc[header_row]
df_combined = df_combined.drop(index=range(0, header_row + 1)).reset_index(drop=True)

# Ensure numeric
numeric_cols = [
    'Club Path', 'Club Speed', 'Launch Angle', 'Launch Direction',
    'Attack Angle', 'Spin Axis', 'Side Carry', 'Ball Speed',
    'Apex', 'Descent Angle', 'Smash Factor'
]
df_combined[numeric_cols] = df_combined[numeric_cols].apply(pd.to_numeric, errors='coerce')
df_combined = df_combined.dropna(subset=numeric_cols).reset_index(drop=True)

#%% 🧮 Feature Engineering
df = df_combined.copy()
df['Face Angle'] = df['Club Path'] + df['Spin Axis'] * 0.1
df['Face to Path'] = df['Face Angle'] - df['Club Path']
df['FaceEst1'] = df['Launch Direction']
df['FaceEst2'] = df['Launch Direction'] + 0.5 * (df['Spin Axis'] - df['Launch Direction'])
df['FaceEst3'] = df['Club Path'] + df['Spin Axis'] * 0.07
df['FaceToPathEstimate1'] = df['FaceEst1'] - df['Club Path']
df['FaceToPathEstimate2'] = df['FaceEst2'] - df['Club Path']
df['FaceToPathEstimate3'] = df['FaceEst3'] - df['Club Path']
df['SpinAxisLaunchDiff'] = df['Spin Axis'] - df['Launch Direction']
df['ClubSpeedSquared'] = df['Club Speed'] ** 2
df['AngleCombo'] = df['Attack Angle'] + df['Launch Angle']

features = numeric_cols + [
    'FaceEst1', 'FaceEst2', 'FaceEst3',
    'FaceToPathEstimate1', 'FaceToPathEstimate2', 'FaceToPathEstimate3',
    'SpinAxisLaunchDiff', 'ClubSpeedSquared', 'AngleCombo'
]

X = df[features]
y = df[['Face Angle', 'Face to Path']]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#%% 🤖 Model Training Functions
def train_and_score(model, name):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred, multioutput='raw_values')
    return {'Model': name, 'Face Angle R2': r2[0], 'FtP R2': r2[1]}

#%% 🚂 Train Models
rf = MultiOutputRegressor(RandomForestRegressor(n_estimators=150, random_state=42))
gb = MultiOutputRegressor(GradientBoostingRegressor(n_estimators=150, random_state=42))
xgb = MultiOutputRegressor(XGBRegressor(n_estimators=150, learning_rate=0.1, verbosity=0, random_state=42))

stacking_model = MultiOutputRegressor(
    StackingRegressor(
        estimators=[
            ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),
            ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
            ('xgb', XGBRegressor(n_estimators=100, learning_rate=0.1, verbosity=0, random_state=42))
        ],
        final_estimator=RidgeCV()
    )
)

#%% 📊 Compare Performance
results = [
    train_and_score(rf, 'Random Forest'),
    train_and_score(gb, 'Gradient Boosting'),
    train_and_score(xgb, 'XGBoost'),
    train_and_score(stacking_model, 'Stacked Ensemble')
]

results_df = pd.DataFrame(results)
print(results_df)

#%% 🧠 Optional: Save results
results_df.to_csv("model_comparison_results.csv", index=False)