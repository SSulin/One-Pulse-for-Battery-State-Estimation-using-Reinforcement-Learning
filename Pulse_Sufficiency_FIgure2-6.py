#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Figure 2

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

material_files = {
    "NMC": r"NMC_2.1Ah_W_5000.xlsx",
    "LMO": r"LMO_10Ah_W_5000.xlsx",
    "LFP": r"LFP_35Ah_W_5000.xlsx",
}

soc_levels = [10, 30, 50]
fixed_soc = 50  

U_cols = [f"U{i}" for i in range(1, 22)]
pulse_index = np.arange(1, 22)

soc_colors = plt.cm.cividis(np.linspace(0.15, 0.85, len(soc_levels)))
material_colors = {
#     "NMC": "#86BAD4",
#     "LMO": "#F5B783",
#     "LFP": "#E0795F",
}

fig = plt.figure(figsize=(4, 3), dpi=600)
gs = gridspec.GridSpec(2, 2)

axes = {
    "NMC": fig.add_subplot(gs[0, 0]),
    "LMO": fig.add_subplot(gs[0, 1]),
    "LFP": fig.add_subplot(gs[1, 0]),
    "MAT": fig.add_subplot(gs[1, 1]),
}

for ax in axes.values():
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)

for material, path in material_files.items():
    df = pd.read_excel(path)
    ax = axes[material]

    for soc, color in zip(soc_levels, soc_colors):
        df_soc = df[df["SOC"] == soc]
        if df_soc.empty:
            continue

        U_mean = df_soc[U_cols].mean().values

        ax.plot(
            pulse_index,
            U_mean,
            lw=1.8,
            color=color
        )

    ax.set_title(material, fontsize=12, weight="bold")
    ax.set_xlabel("Pulse voltage index")
    ax.set_ylabel("Voltage (V)")
    ax.set_xticks([1, 5, 10, 15, 21])
    ax.set_ylim(2.8, 4.0)
    ax.grid(False)

ax = axes["MAT"]

for material, path in material_files.items():
    df = pd.read_excel(path)
    df_soc = df[df["SOC"] == fixed_soc]
    if df_soc.empty:
        continue

    U_mean = df_soc[U_cols].mean().values

    ax.plot(
        pulse_index,
        U_mean,
        lw=2.2,
        color=material_colors[material]
    )

ax.set_title(f"SOC = {fixed_soc}%", fontsize=12, weight="bold")
ax.set_xlabel("Pulse voltage index")
ax.set_ylabel("Voltage (V)")
ax.set_xticks([1, 5, 10, 15, 21])
ax.set_ylim(2.8, 4.0)
ax.grid(False)

labels = ["a", "b", "c", "d"]
for lab, ax in zip(labels, axes.values()):
    ax.text(
        -0.12, 1.05, lab,
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
        va="top"
    )

plt.tight_layout()
plt.show()


# In[1]:


import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "notebook"
material_files = {
    "NMC": r"NMC_2.1Ah_W_5000.xlsx",
    "LMO": r"LMO_10Ah_W_5000.xlsx",
    "LFP": r"LFP_35Ah_W_5000.xlsx",
}

soc_bins = list(range(0, 101, 10))
soc_labels = [f"{soc_bins[i]}–{soc_bins[i+1]}%" for i in range(len(soc_bins) - 1)]

soh_bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
soh_labels = ["0.5–0.6", "0.6–0.7", "0.7–0.8", "0.8–0.9", "0.9–1.0"]

material_colors = {
    "NMC": "#86BAD4",
    "LMO": "#F5B783",
    "LFP": "#E0795F",
}

soc_colors = {
    "0–10%":  "#E3F2FD",
    "10–20%": "#BBDEFB",
    "20–30%": "#90CAF9",
    "30–40%": "#64B5F6",
    "40–50%": "#42A5F5",
    "50–60%": "#2196F3",
    "60–70%": "#1E88E5",
    "70–80%": "#1976D2",
    "80–90%": "#1565C0",
    "90–100%":"#0D47A1",
}

soh_node_color = "#E6E6E6"

nodes = []
node_colors = []
links = []

def node_id(name, color):
    if name not in nodes:
        nodes.append(name)
        node_colors.append(color)
    return nodes.index(name)

for material, path in material_files.items():
    df = pd.read_excel(path)

    df["SOC_bin"] = pd.cut(
        df["SOC"], bins=soc_bins, labels=soc_labels, right=False
    )
    df["SOH_bin"] = pd.cut(
        df["SOH"], bins=soh_bins, labels=soh_labels
    )

    soc_counts = df["SOC_bin"].value_counts().sort_index()

    for soc_bin, cnt in soc_counts.items():
        if cnt == 0 or pd.isna(soc_bin):
            continue

        src = node_id(material, material_colors[material])
        soc_color = soc_colors.get(str(soc_bin), "#B0BEC5")
        tgt = node_id(f"SOC {soc_bin}", soc_color)

        links.append(dict(
            source=src,
            target=tgt,
            value=int(cnt),
            color=material_colors[material]
        ))

        df_soc = df[df["SOC_bin"] == soc_bin]
        soh_counts = df_soc["SOH_bin"].value_counts().sort_index()

        for soh_bin, soh_cnt in soh_counts.items():
            if soh_cnt == 0 or pd.isna(soh_bin):
                continue

            tgt_soh = node_id(f"SOH {soh_bin}", soh_node_color)

            links.append(dict(
                source=tgt,
                target=tgt_soh,
                value=int(soh_cnt),
                color=soc_color
            ))

fig = go.Figure(go.Sankey(
    arrangement="snap",
    node=dict(
        pad=24,
        thickness=18,
        label=nodes,
        color=node_colors,
        line=dict(color="rgba(0,0,0,0)", width=0)
    ),
    link=dict(
        source=[l["source"] for l in links],
        target=[l["target"] for l in links],
        value=[l["value"] for l in links],
        color=[l["color"] for l in links]
    )
))

fig.update_layout(
    title="Dataset heterogeneity across material, SOC range, and SOH",
    font=dict(size=12),
    width=1050,
    height=540,
    margin=dict(l=20, r=20, t=60, b=20)
)

fig.write_html("dataset_sankey_material_SOC_SOH.html")
fig.show()


# In[2]:


import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, mean_absolute_error, r2_score,
    classification_report, confusion_matrix, ConfusionMatrixDisplay
)

from xgboost import XGBClassifier, XGBRegressor

material_files = {
    "NMC": [
        "NMC_2.1Ah_W_5000.xlsx",
    ],
    "LMO": [
        "LMO_10Ah_W_5000.xlsx",
    ],
    "LFP": [
        "LFP_35Ah_W_5000.xlsx",
    ],
}

def load_all_data(material_files):
    dfs = []
    for mat, files in material_files.items():
        for f in files:
            df = pd.read_excel(f)
            df["Mat"] = mat
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

df = load_all_data(material_files)

FEATURES = [f"U{i}" for i in range(1, 21)]  

TEST_RATIO = 0.25
np.random.seed(42)

test_mask = np.zeros(len(df), dtype=bool)

for mat in df["Mat"].unique():
    mat_mask = df["Mat"] == mat
    battery_ids = df.loc[mat_mask, "No."].unique()

    test_ids = np.random.choice(
        battery_ids,
        size=max(1, int(len(battery_ids) * TEST_RATIO)),
        replace=False
    )

    test_mask |= df["No."].isin(test_ids).values

df_test = df[test_mask].copy()
df_train_used = df[~test_mask].copy()

from sklearn.preprocessing import StandardScaler, LabelEncoder
from xgboost import XGBClassifier

X_train = df_train_used[FEATURES].values
y_mat = df_train_used["Mat"].values

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

le_mat = LabelEncoder()
y_mat_enc = le_mat.fit_transform(y_mat)

clf_mat = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="mlogloss",
    random_state=42
)
clf_mat.fit(X_train_scaled, y_mat_enc)


# In[3]:


from collections import defaultdict

soh_models = {}

for mat in df_train_used["Mat"].unique():

    idx = df_train_used["Mat"] == mat

    X_m = df_train_used.loc[idx, FEATURES].values
    SOC_m = df_train_used.loc[idx, "SOC"].values.reshape(-1, 1)
    X_m = np.hstack([X_m, SOC_m])

    y_m = df_train_used.loc[idx, "SOH"].values

    scaler_soh = StandardScaler()
    X_m_scaled = scaler_soh.fit_transform(X_m)

    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42
    )
    model.fit(X_m_scaled, y_m)

    soh_models[mat] = {
        "model": model,
        "scaler": scaler_soh
    }

    print(f"✅ SOH model trained for {mat}, samples={len(y_m)}")


# In[4]:


soc_models = {}

for mat in df_train_used["Mat"].unique():

    idx = df_train_used["Mat"] == mat
    X_m = df_train_used.loc[idx, FEATURES].values
    y_soc = df_train_used.loc[idx, "SOC"].values

    scaler_soc = StandardScaler()
    X_m_scaled = scaler_soc.fit_transform(X_m)

    model = XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42
    )
    model.fit(X_m_scaled, y_soc)

    soc_models[mat] = {
        "model": model,
        "scaler": scaler_soc
    }

    print(f"✅ SOC model trained for {mat}, samples={len(y_soc)}")


# In[5]:


def predict_soh_continuous(row, mode="soft"):

    U = row[FEATURES].values.reshape(1, -1)
    U_scaled = scaler.transform(U)

    if mode == "oracle":
        mat = row["Mat"]
    else:
        mat_id = clf_mat.predict(U_scaled)[0]
        mat = le_mat.inverse_transform([mat_id])[0]

    if mat not in soc_models or mat not in soh_models:
        return np.nan

    if mode == "oracle":
        soc = row["SOC"]
    else:
        soc = soc_models[mat].predict(U_scaled)[0]

    X_soh = np.hstack([U, [[soc]]])
    X_soh_scaled = soh_models[mat]["scaler"].transform(X_soh)

    return soh_models[mat]["model"].predict(X_soh_scaled)[0]

from sklearn.metrics import mean_absolute_error, r2_score

y_true, y_oracle, y_hard = [], [], []

for _, row in df_test.iterrows():
    try:
        y_true.append(row["SOH"])
        y_oracle.append(predict_soh_continuous(row, mode="oracle"))
    except:
        continue


# Figure6

# In[32]:


def predict_soh_continuous(row, mode="soft"):
    U = row[FEATURES].values.reshape(1, -1)
    U_scaled_for_clf = scaler.transform(U)

    if mode == "oracle":
        mat = row["Mat"]
    else:
        mat_id = clf_mat.predict(U_scaled_for_clf)[0]
        mat = le_mat.inverse_transform([mat_id])[0]

    if mat not in soc_models or mat not in soh_models:
        return np.nan

    curr_soc_model = soc_models[mat]["model"]
    curr_soc_scaler = soc_models[mat]["scaler"]
    
    if mode == "oracle":
        soc = row["SOC"]
    else:

        U_scaled_for_soc = curr_soc_scaler.transform(U)
        soc = curr_soc_model.predict(U_scaled_for_soc)[0]

    curr_soh_model = soh_models[mat]["model"]
    curr_soh_scaler = soh_models[mat]["scaler"]
   
    X_soh = np.hstack([U, [[soc]]])
    X_soh_scaled = curr_soh_scaler.transform(X_soh)

    return curr_soh_model.predict(X_soh_scaled)[0]
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_specific_impacts(df_test, clf_mat, le_mat, soc_models, soh_models, scaler):
    analysis_data = []
    
    for _, row in df_test.iterrows():
        u_raw = row[FEATURES].values.reshape(1, -1)
        u_s = scaler.transform(u_raw)
        true_mat = row["Mat"]
        true_soc = row["SOC"]
        true_soh = row["SOH"]

        pred_mat_id = clf_mat.predict(u_s)[0]
        pred_mat = le_mat.inverse_transform([pred_mat_id])[0]
        soc_norm = soc_models[pred_mat]["model"].predict(u_s)[0]

        wrong_mats = [m for m in material_files.keys() if m != true_mat]
        fake_mat = wrong_mats[0] 
 
        soc_on_wrong_mat = soc_models[fake_mat]["model"].predict(u_s)[0]
        x_soh_wrong = np.hstack([u_raw, [[soc_on_wrong_mat]]])
        x_soh_wrong_s = soh_models[fake_mat]["scaler"].transform(x_soh_wrong)
        soh_on_wrong_mat = soh_models[fake_mat]["model"].predict(x_soh_wrong_s)[0]

        biased_soc = true_soc * 1.3 
        x_soh_soc_err = np.hstack([u_raw, [[biased_soc]]])
        x_soh_soc_err_s = soh_models[true_mat]["scaler"].transform(x_soh_soc_err)
        soh_with_soc_bias = soh_models[true_mat]["model"].predict(x_soh_soc_err_s)[0]

        analysis_data.append({
            "True_Mat": true_mat,
            "SOC_Error_on_Wrong_Mat": abs(soc_on_wrong_mat - true_soc),
            "SOH_Error_on_Wrong_Mat": abs(soh_on_wrong_mat - true_soh),
            "SOH_Error_with_SOC_Bias": abs(soh_with_soc_bias - true_soh),
            "Normal_SOH_Error": abs(predict_soh_continuous(row, mode="hard") - true_soh)
        })

    return pd.DataFrame(analysis_data)

res_impact = analyze_specific_impacts(df_test, clf_mat, le_mat, soc_models, soh_models, scaler)


# In[33]:


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

plt.figure(figsize=(5, 4), dpi=600)

plot_df = res_impact.melt(value_vars=["Normal_SOH_Error", "SOH_Error_with_SOC_Bias", "SOH_Error_on_Wrong_Mat"],
                          var_name="Scenario", value_name="SOH_MAE")

sns.boxplot(x="Scenario", y="SOH_MAE", data=plot_df, palette="muted")

plt.xticks([0, 1, 2], ["Control\n(Best Case)", "SOC Error Impact\n(Mat Correct)", "Material Error Impact\n(Cascading Error)"])
plt.ylabel("Absolute Error in SOH")
plt.show()


# In[20]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
soc_error_records = []

for _, row in df_test.iterrows():

    U = row[FEATURES].values.reshape(1, -1)
    U_scaled = scaler.transform(U)

    true_mat = row["Mat"]
    soc_true = row["SOC"]

    for mat_wrong in soc_models:
        if mat_wrong == true_mat:
            continue

        soc_cf = soc_models[mat_wrong]["model"].predict(U_scaled)[0]

        soc_error_records.append({
            "true_mat": true_mat,
            "assumed_mat": mat_wrong,
            "SOC_true": soc_true,
            "SOC_cf": soc_cf,
            "SOC_error": soc_cf - soc_true
        })

df_soc_err = pd.DataFrame(soc_error_records)

plt.figure(figsize=(3,2),dpi=600)
for key, g in df_soc_err.groupby(["true_mat", "assumed_mat"]):
    label = f"{key[0]} → {key[1]}"
    plt.hist(g["SOC_error"], bins=40, alpha=0.5, label=label)

plt.xlabel("SOC Error")
plt.ylabel("Count")
plt.legend()
plt.tight_layout()
plt.show()


# In[24]:


soh_error_records = []

for _, row in df_test.iterrows():

    U = row[FEATURES].values.reshape(1, -1)
    true_mat = row["Mat"]

    soc_true = row["SOC"]
    soh_true = row["SOH"]

    for mat_wrong in soc_models:
        if mat_wrong == true_mat:
            continue

        soc_cf = soc_models[mat_wrong]["model"].predict(
            scaler.transform(U)
        )[0]

        X_soh = np.hstack([U, [[soc_cf]]])
        X_soh_scaled = soh_models[mat_wrong]["scaler"].transform(X_soh)
        soh_cf = soh_models[mat_wrong]["model"].predict(X_soh_scaled)[0]

        soh_error_records.append({
            "true_mat": true_mat,
            "assumed_mat": mat_wrong,
            "SOC_error": soc_cf - soc_true,
            "SOH_error": soh_cf - soh_true
        })

df_soh_err = pd.DataFrame(soh_error_records)

plt.figure(figsize=(4,3),dpi=600)

for key, g in df_soh_err.groupby(["true_mat", "assumed_mat"]):
    plt.scatter(
        g["SOC_error"], g["SOH_error"],
        alpha=0.4, label=f"{key[0]} → {key[1]}"
    )

plt.xlabel("SOC Error")
plt.ylabel("SOH Error")
plt.tight_layout()
plt.show()


# In[30]:


soc_deltas = np.linspace(-0.05, 0.05, 11)

gain_records = []

for _, row in df_test.iterrows():

    U = row[FEATURES].values.reshape(1, -1)
    mat = row["Mat"]

    soc_true = row["SOC"]
    soh_true = row["SOH"]

    for delta in soc_deltas:
        soc_perturbed = soc_true + delta

        X_soh = np.hstack([U, [[soc_perturbed]]])
        X_soh_scaled = soh_models[mat]["scaler"].transform(X_soh)
        soh_pred = soh_models[mat]["model"].predict(X_soh_scaled)[0]

        gain_records.append({
            "Mat": mat,
            "SOC_delta": delta,
            "SOH_delta": soh_pred - soh_true
        })

df_gain = pd.DataFrame(gain_records)


plt.figure(figsize=(6, 5),dpi=600)

color_map = {
    "NMC": "#86BAD4",
    "LMO": "#F5B783",
    "LFP": "#E0795F",
}

for mat, g in df_gain.groupby("Mat"):
    mean_curve = g.groupby("SOC_delta")["SOH_delta"].mean()
    plt.plot(
        mean_curve.index,
        mean_curve.values,
        marker="o",
        linewidth=2,
        markersize=5,
        color=color_map.get(mat, "gray"),
        label=mat
    )

plt.xlabel("Injected SOC Error")
plt.ylabel("Resulting SOH Error")
#plt.legend()
plt.title("Material-dependent SOC → SOH Error Gain")
plt.tight_layout()
plt.show()

summary = []

for key, g in df_soh_err.groupby(["true_mat", "assumed_mat"]):
    summary.append({
        "Case": f"{key[0]}→{key[1]}",
        "Mean_SOC_Error": g["SOC_error"].mean(),
        "Std_SOC_Error": g["SOC_error"].std(),
        "Mean_SOH_Error": g["SOH_error"].mean(),
        "Std_SOH_Error": g["SOH_error"].std()
    })

df_summary = pd.DataFrame(summary)
print(df_summary)


# In[37]:


import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(3, 2), dpi=600)

plot_df = res_impact.melt(
    value_vars=[
        "Normal_SOH_Error",
        "SOH_Error_with_SOC_Bias",
        "SOH_Error_on_Wrong_Mat"
    ],
    var_name="Scenario",
    value_name="SOH_MAE"
)

order = [
    "Normal_SOH_Error",
    "SOH_Error_with_SOC_Bias",
    "SOH_Error_on_Wrong_Mat"
]

palette = [
    "#BDBDBD",  
    "#86BAD4",  
    "#E0795F",  
]

flierprops = dict(
    marker='o',
    markerfacecolor='0.5',  
    markeredgecolor='0.5',
    markersize=2,
    linestyle='none',
    alpha=0.6
)

sns.boxplot(
    x="Scenario",
    y="SOH_MAE",
    data=plot_df,
    order=order,
    palette=palette,
    width=0.6,
    showfliers=True,
    flierprops=flierprops
)

plt.xticks(
    [0, 1, 2],
    [
        "(Best Case)",
        "(Mat Correct)",
        "(Cascading)"
    ]
)

plt.ylabel("Absolute SOH Error")
plt.xlabel("")
plt.tight_layout()
plt.show()


# Figure 3

# In[6]:


X_test = df_test[FEATURES].values
X_test_scaled = scaler.transform(X_test)

y_mat_true = df_test["Mat"].values
y_mat_pred_enc = clf_mat.predict(X_test_scaled)
y_mat_pred = le_mat.inverse_transform(y_mat_pred_enc)

print("Material classification accuracy:",
      accuracy_score(y_mat_true, y_mat_pred))

cm = confusion_matrix(
    y_mat_true,
    y_mat_pred,
    labels=le_mat.classes_
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=le_mat.classes_
)

fig, ax = plt.subplots(figsize=(3, 2),dpi=600)
disp.plot(
    ax=ax,
    cmap="Blues",
    colorbar=False,
    values_format="d"
)

ax.set_title("Material Classification Confusion Matrix\n(New Batteries)",
             fontsize=10)
ax.set_xlabel("Predicted Material", fontsize=9)
ax.set_ylabel("True Material", fontsize=9)

plt.tight_layout()
plt.show()


# In[8]:


from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

X_test = df_test[FEATURES].values
X_test_scaled = scaler.transform(X_test)

y_mat_true = df_test["Mat"].values
y_mat_pred_enc = clf_mat.predict(X_test_scaled)
y_mat_pred = le_mat.inverse_transform(y_mat_pred_enc)

print("Material classification accuracy:",
      accuracy_score(y_mat_true, y_mat_pred))

cm = confusion_matrix(
    y_mat_true,
    y_mat_pred,
    labels=le_mat.classes_
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=le_mat.classes_
)

fig, ax = plt.subplots(figsize=(3, 2), dpi=600)

disp.plot(
    ax=ax,
    cmap="Blues",
    colorbar=False,
    values_format="d"
 
)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.set_title(
    "Material Classification Confusion Matrix\n(New Batteries)",
    fontsize=10
)
ax.set_xlabel("Predicted Material", fontsize=9)
ax.set_ylabel("True Material", fontsize=9)

plt.tight_layout()
plt.show()


# In[13]:


PULSE_FEATURES = {
    1: [f"U{i}" for i in range(1, 5)],    # U1–U4
    2: [f"U{i}" for i in range(5, 9)],    # U5–U8
    3: [f"U{i}" for i in range(9, 13)],   # U9–U12
    4: [f"U{i}" for i in range(13, 17)],  # U13–U16
    5: [f"U{i}" for i in range(17, 21)],  # U17–U20
}
sample_ratios = [0.1, 0.2, 0.3,0.4, 0.5,0.6, 0.7,0.8, 0.9,1.0]
pulse_nums = [1, 2, 3, 4, 5]

import random

def sample_pulse_features(pulse_num, seed=None):
    rng = np.random.default_rng(seed)
    pulses = rng.choice(list(PULSE_FEATURES.keys()),
                         size=pulse_num,
                         replace=False)
    feats = []
    for p in pulses:
        feats.extend(PULSE_FEATURES[p])
    return feats
from sklearn.metrics import mean_absolute_error, accuracy_score

def evaluate_metrics(
    df_train,
    df_test,
    feature_cols,
    sample_ratio,
    random_state=0
):
  
    df_sub = df_train.sample(frac=sample_ratio, random_state=random_state)

    y_soh_true, y_soh_pred = [], []
    y_soc_true, y_soc_pred = [], []
    y_mat_true, y_mat_pred = [], []

    X_mat = df_sub[feature_cols].values
    y_mat = df_sub["Mat"].values

    scaler_mat = StandardScaler()
    X_mat_s = scaler_mat.fit_transform(X_mat)

    le = LabelEncoder()
    y_mat_enc = le.fit_transform(y_mat)

    clf_mat = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="mlogloss",
        random_state=0
    )
    clf_mat.fit(X_mat_s, y_mat_enc)

    soc_models, soh_models = {}, {}

    for mat in df_sub["Mat"].unique():

        train_m = df_sub[df_sub["Mat"] == mat]
        if len(train_m) < 20:
            continue

        X = train_m[feature_cols].values
        y_soc = train_m["SOC"].values
        y_soh = train_m["SOH"].values

        scaler_soc = StandardScaler()
        X_s = scaler_soc.fit_transform(X)

        soc_model = XGBRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            random_state=0
        )
        soc_model.fit(X_s, y_soc)

        soc_pred = soc_model.predict(X_s).reshape(-1, 1)

        X_soh = np.hstack([X, soc_pred])
        scaler_soh = StandardScaler()
        X_soh_s = scaler_soh.fit_transform(X_soh)

        soh_model = XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.03,
            random_state=0
        )
        soh_model.fit(X_soh_s, y_soh)

        soc_models[mat] = (soc_model, scaler_soc)
        soh_models[mat] = (soh_model, scaler_soh)

    for _, row in df_test.iterrows():

        U = row[feature_cols].values.reshape(1, -1)
        mat_true = row["Mat"]

        U_s = scaler_mat.transform(U)
        mat_pred = le.inverse_transform(clf_mat.predict(U_s))[0]

        if mat_pred not in soc_models:
            continue

        soc_model, scaler_soc = soc_models[mat_pred]
        U_soc_s = scaler_soc.transform(U)
        soc_pred = soc_model.predict(U_soc_s)[0]

        soh_model, scaler_soh = soh_models[mat_pred]
        X_soh = np.hstack([U, [[soc_pred]]])
        X_soh_s = scaler_soh.transform(X_soh)
        soh_pred = soh_model.predict(X_soh_s)[0]

        y_mat_true.append(mat_true)
        y_mat_pred.append(mat_pred)

        y_soc_true.append(row["SOC"])
        y_soc_pred.append(soc_pred)

        y_soh_true.append(row["SOH"])
        y_soh_pred.append(soh_pred)

    return {
        "soh_mae": mean_absolute_error(y_soh_true, y_soh_pred),
        "soc_mae": mean_absolute_error(y_soc_true, y_soc_pred),
        "mat_acc": accuracy_score(y_mat_true, y_mat_pred),
    }
H_soh = np.zeros((len(pulse_nums), len(sample_ratios)))
H_soc = np.zeros_like(H_soh)
H_mat = np.zeros_like(H_soh)

for i, pnum in enumerate(pulse_nums):
    for j, ratio in enumerate(sample_ratios):

        res = []
        for r in range(3):
            feats = sample_pulse_features(pnum, seed=r)
            res.append(
                evaluate_metrics(
                    df_train_used,
                    df_test,
                    feats,
                    ratio,
                    random_state=r
                )
            )

        H_soh[i, j] = np.mean([x["soh_mae"] for x in res])
        H_soc[i, j] = np.mean([x["soc_mae"] for x in res])
        H_mat[i, j] = np.mean([x["mat_acc"] for x in res])

fig, axes = plt.subplots(1, 3, figsize=(10, 3), dpi=300, sharey=True)

titles = ["SOH MAE", "SOC MAE", "Material Accuracy"]
maps = [H_soh, H_soc, H_mat]
cmaps = ["viridis", "viridis", "plasma"]

for ax, M, title, cmap in zip(axes, maps, titles, cmaps):
    im = ax.imshow(M, aspect="auto", origin="lower", cmap=cmap)
    ax.set_title(title)
    ax.set_xticks(range(len(sample_ratios)))
    ax.set_xticklabels(sample_ratios)
    ax.set_xlabel("Training sample ratio")
    fig.colorbar(im, ax=ax, fraction=0.046)

axes[0].set_yticks(range(len(pulse_nums)))
axes[0].set_yticklabels(pulse_nums)
axes[0].set_ylabel("Number of pulses")

plt.tight_layout()
plt.show()


# In[14]:


def run_task_rl(
    H_perf,
    pulse_nums,
    sample_ratios,
    task_type="min",      
    tol=0.01,
    cost_w_ratio=5.0,
    n_episodes=500,
    seed=0
):
  
    np.random.seed(seed)
    import random
    random.seed(seed)

    if task_type == "min":
        best_val = np.nanmin(H_perf)
        mask_sufficient = H_perf <= best_val + tol
    else:
        best_val = np.nanmax(H_perf)
        mask_sufficient = H_perf >= best_val - tol

    cost = np.zeros_like(H_perf)
    for i, p in enumerate(pulse_nums):
        for j, r in enumerate(sample_ratios):
            cost[i, j] = p + cost_w_ratio * r

    def reward(i, j):
        if not mask_sufficient[i, j]:
            return -10.0
        return -cost[i, j] + 1.0

    n_p, n_r = H_perf.shape
    Q = np.zeros((n_p, n_r, 4))

    ACTIONS = {
        0: (-1, 0),
        1: (1, 0),
        2: (0, -1),
        3: (0, 1),
    }

    alpha, gamma, eps = 0.2, 0.9, 0.2

    for _ in range(n_episodes):
        i = random.randint(0, n_p - 1)
        j = random.randint(0, n_r - 1)

        for _ in range(20):
            if random.random() < eps:
                a = random.randint(0, 3)
            else:
                a = np.argmax(Q[i, j])

            di, dj = ACTIONS[a]
            ni = np.clip(i + di, 0, n_p - 1)
            nj = np.clip(j + dj, 0, n_r - 1)

            r = reward(ni, nj)
            Q[i, j, a] += alpha * (
                r + gamma * np.max(Q[ni, nj]) - Q[i, j, a]
            )

            i, j = ni, nj

    V = np.max(Q, axis=2)
    i_opt, j_opt = np.unravel_index(np.argmax(V), V.shape)

    return {
        "pulse_num": pulse_nums[i_opt],
        "train_ratio": sample_ratios[j_opt],
        "mask_sufficient": mask_sufficient,
        "cost": cost,
        "Q": Q,
        "V": V,
    }


# In[15]:


res_soh = run_task_rl(
    H_perf=H_soh,
    pulse_nums=pulse_nums,
    sample_ratios=sample_ratios,
    task_type="min",
    tol=0.01,
)
res_soc = run_task_rl(
    H_perf=H_soc,
    pulse_nums=pulse_nums,
    sample_ratios=sample_ratios,
    task_type="min",
    tol=0.01,
)

res_mat = run_task_rl(
    H_perf=H_mat,
    pulse_nums=pulse_nums,
    sample_ratios=sample_ratios,
    task_type="max",
    tol=0.02,
)
print("🎯 Optimal data sufficiency per task")
print("----------------------------------")
print(f"SOH  : pulse={res_soh['pulse_num']}, ratio={res_soh['train_ratio']}")
print(f"SOC  : pulse={res_soc['pulse_num']}, ratio={res_soc['train_ratio']}")
print(f"MAT  : pulse={res_mat['pulse_num']}, ratio={res_mat['train_ratio']}")


# In[13]:


import numpy as np
POS_PULSES = {
    1: [f"U{i}" for i in range(1, 5)],    # U1–U4
    2: [f"U{i}" for i in range(9, 13)],   # U9–U12
    3: [f"U{i}" for i in range(17, 21)],  # U17–U20
}

NEG_PULSES = {
    1: [f"U{i}" for i in range(5, 9)],    # U5–U8
    2: [f"U{i}" for i in range(13, 17)],  # U13–U16
}
def sample_pos_neg_features(n_pos, n_neg, seed=None):
    rng = np.random.default_rng(seed)

    pos_keys = list(POS_PULSES.keys())
    neg_keys = list(NEG_PULSES.keys())

    if n_pos > len(pos_keys) or n_neg > len(neg_keys):
        return None
    if n_pos == 0 and n_neg == 0:
        return None

    feats = []

    if n_pos > 0:
        pos_sel = rng.choice(pos_keys, size=n_pos, replace=False)
        for k in pos_sel:
            feats.extend(POS_PULSES[k])

    if n_neg > 0:
        neg_sel = rng.choice(neg_keys, size=n_neg, replace=False)
        for k in neg_sel:
            feats.extend(NEG_PULSES[k])

    return feats

POS_COUNTS = [0, 1, 2, 3]
NEG_COUNTS = [0, 1, 2]

COMBOS = []
for np_ in POS_COUNTS:
    for nn_ in NEG_COUNTS:
        if np_ == 0 and nn_ == 0:
            continue
        COMBOS.append((np_, nn_))

H_soh = np.zeros((len(COMBOS), len(sample_ratios)))
H_soc = np.zeros_like(H_soh)
H_mat = np.zeros_like(H_soh)

for i, (n_pos, n_neg) in enumerate(COMBOS):
    for j, ratio in enumerate(sample_ratios):

        res = []
        for r in range(3):
            feats = sample_pos_neg_features(n_pos, n_neg, seed=r)
            if feats is None:
                continue

            res.append(
                evaluate_metrics(
                    df_train_used,
                    df_test,
                    feats,
                    ratio,
                    random_state=r
                )
            )

        H_soh[i, j] = np.mean([x["soh_mae"] for x in res])
        H_soc[i, j] = np.mean([x["soc_mae"] for x in res])
        H_mat[i, j] = np.mean([x["mat_acc"] for x in res])

        print(f"+{n_pos}/-{n_neg} | ratio={ratio:.2f} | "
              f"SOH={H_soh[i,j]:.4f}, "
              f"SOC={H_soc[i,j]:.4f}, "
              f"MAT={H_mat[i,j]:.3f}")
y_labels = [f"+{p} / -{n}" for p, n in COMBOS]

fig, axes = plt.subplots(1, 3, figsize=(11, 4), dpi=300, sharey=True)

titles = ["SOH MAE", "SOC MAE", "Material Accuracy"]
maps = [H_soh, H_soc, H_mat]
cmaps = ["viridis", "viridis", "plasma"]

for ax, M, title, cmap in zip(axes, maps, titles, cmaps):
    im = ax.imshow(M, aspect="auto", origin="lower", cmap=cmap)
    ax.set_title(title)
    ax.set_xticks(range(len(sample_ratios)))
    ax.set_xticklabels(sample_ratios)
    ax.set_xlabel("Training sample ratio")
    fig.colorbar(im, ax=ax, fraction=0.046)

axes[0].set_yticks(range(len(y_labels)))
axes[0].set_yticklabels(y_labels)
axes[0].set_ylabel("Pulse combination (+ / −)")

plt.tight_layout()
plt.show()


# Figure4

# In[12]:


from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np

soc_true = []
soc_pred_oracle = []
soc_pred_hard = []

for _, row in df_test.iterrows():

    U = row[FEATURES].values.reshape(1, -1)
    true_soc = row["SOC"]
    soc_true.append(true_soc)

    mat_true = row["Mat"]

    if mat_true in soc_models:
        soc_scaler = soc_models[mat_true]["scaler"]
        soc_model  = soc_models[mat_true]["model"]

        U_soc_scaled = soc_scaler.transform(U)
        soc_o = soc_model.predict(U_soc_scaled)[0]
    else:
        soc_o = np.nan

    soc_pred_oracle.append(soc_o)

soc_true = np.array(soc_true)
soc_pred_oracle = np.array(soc_pred_oracle)
def soc_report(name, y_t, y_p):
    mask = ~np.isnan(y_p)
    print(f"{name:>10s} | "
          f"MAE={mean_absolute_error(y_t[mask], y_p[mask]):.2f} | "
          f"R2={r2_score(y_t[mask], y_p[mask]):.3f}")


# In[8]:


import numpy as np
import pandas as pd

df_soc = pd.DataFrame({
    "SOC_true": soc_true,
    "SOC_pred": soc_pred_oracle,
    "Mat": df_test["Mat"].values
})

df_soc = df_soc.dropna().reset_index(drop=True)


# In[9]:


import matplotlib.pyplot as plt

for mat in df_soc["Mat"].unique():

    df_m = df_soc[df_soc["Mat"] == mat]
    if len(df_m) < 20:
        continue

    plt.figure(figsize=(3,2.5),dpi=600)

    plt.scatter(
        df_m["SOC_true"],
        df_m["SOC_pred"],
        s=14,
        alpha=0.6,
        color='#34669A'
    )

    plt.plot([0,100], [0,100], "k--", lw=1)

    plt.xlabel("True SOC (%)", fontsize=10)
    plt.ylabel("Predicted SOC (%)", fontsize=10)
    plt.title(f"SOC Prediction ({mat})", fontsize=11)

    plt.xlim(0, 100)
    plt.ylim(0, 100)

    plt.tight_layout()
    plt.show()


# In[10]:


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_soc_error_hist_by_material(df_soc):

    for mat in df_soc["Mat"].unique():

        df_m = df_soc[df_soc["Mat"] == mat]
        err = df_m["SOC_pred"].values - df_m["SOC_true"].values
        err = err[~np.isnan(err)]

        if len(err) < 20:
            continue

        plt.figure(figsize=(1.5, 1.3),dpi=600)

        sns.histplot(
            err,
            bins=20,
            kde=True,
            color="#80A2C5"
        )

        plt.axvline(0, color="k", linestyle="--", lw=1)

        plt.xlabel("SOC Prediction Error (%)", fontsize=9)
        plt.ylabel("Count", fontsize=9)
        plt.title(f"SOC Error Distribution ({mat})", fontsize=10)

        plt.tight_layout()
        plt.show()

        df_soc = pd.DataFrame({
    "SOC_true": soc_true,
    "SOC_pred": soc_pred_oracle,
    "Mat": df_test["Mat"].values
}).dropna()

plot_soc_error_hist_by_material(df_soc)


# In[53]:


df_soc_metric["R2"],


# In[48]:


color='#34669A'
import matplotlib.pyplot as plt

def plot_soc_scatter(y_true, y_pred, title):
    mask = ~np.isnan(y_pred)

    plt.figure(figsize=(3, 2.5),dpi=600)
    plt.scatter(
        y_true[mask], y_pred[mask],
        s=30, alpha=0.7,color='#34669A', #edgecolor="k"
    )

    lims = [0, 100]
    plt.plot(lims, lims, "k--", linewidth=1)

    plt.xlim(lims)
    plt.ylim(lims)

    plt.xlabel("True SOC (%)")
    plt.ylabel("Predicted SOC (%)")
    plt.title(title)
    plt.tight_layout()
    plt.show()

plot_soc_scatter(
    soc_true, soc_pred_oracle,
    "SOC Prediction"
)


# Figure5

# In[12]:


def plot_soh_parity_by_material(df_test, y_pred):

    y_pred = np.array(y_pred)

    for mat in df_test["Mat"].unique():

        idx = (df_test["Mat"].values == mat)
        y_t = df_test.loc[idx, "SOH"].values
        y_p = y_pred[idx]

        mask = ~np.isnan(y_p)
        if mask.sum() < 20:
            continue

        plt.figure(figsize=(3,2.5),dpi=600)
        plt.scatter(
            y_t[mask],
            y_p[mask],
            s=15,
            alpha=0.4,
            color='#8BCFB5'
        )

        lims = [
            min(y_t[mask].min(), y_p[mask].min()),
            max(y_t[mask].max(), y_p[mask].max())
        ]
        lims = [
            0.5,
            1.0
        ]
        plt.plot(lims, lims, "k--", lw=1)

        plt.xlabel("True SOH")
        plt.ylabel("Predicted SOH")
        plt.title(f"{mat}: SOH Prediction")
        plt.ylim(0.5,1.0)
        plt.xlim(0.5,1.0)

        plt.tight_layout()
        plt.show()

plot_soh_parity_by_material(df_test, y_oracle)


# In[61]:


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_soh_error_by_material(df_test, y_pred):

    sns.set_style("white")

    y_pred = np.array(y_pred)

    for mat in df_test["Mat"].unique():

        idx = (df_test["Mat"].values == mat)
        err = y_pred[idx] - df_test.loc[idx, "SOH"].values
        err = err[~np.isnan(err)]

        if len(err) < 20:
            continue

        fig, ax = plt.subplots(
            figsize=(1.5, 1.3),
            dpi=600
        )

        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        ax.patch.set_alpha(0)

        sns.histplot(
            err,
            bins=30,
            kde=True,
            color="#B9DA9A",
            ax=ax
        )

        ax.axvline(0, color="k", linestyle="--", lw=0.5)

        ax.set_xlabel("SOH Error", fontsize=9)
        ax.set_ylabel("Count", fontsize=9)
        ax.set_title(f"{mat}: SOH Error", fontsize=10)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(axis='both', labelsize=8)

        plt.tight_layout()
        plt.show()


plot_soh_error_by_material(df_test, y_oracle)


# In[62]:


soh_models_no_soc = {}

for mat in df_train_used["Mat"].unique():

    idx = df_train_used["Mat"] == mat

    X_m = df_train_used.loc[idx, FEATURES].values
    y_m = df_train_used.loc[idx, "SOH"].values

    scaler_m = StandardScaler()
    X_m_scaled = scaler_m.fit_transform(X_m)

    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42
    )
    model.fit(X_m_scaled, y_m)

    soh_models_no_soc[mat] = {
        "model": model,
        "scaler": scaler_m
    }

    print(f"❌ SOC-unaware SOH model trained for {mat}, samples={len(y_m)}")


# In[47]:


def predict_soh_no_soc(row):

    U = row[FEATURES].values.reshape(1, -1)
    U_scaled = scaler.transform(U)

    mat = row["Mat"]

    if mat not in soh_models_no_soc:
        return np.nan

    X_soh_scaled = soh_models_no_soc[mat]["scaler"].transform(U)

    return soh_models_no_soc[mat]["model"].predict(X_soh_scaled)[0]

y_no_soc = []

for _, row in df_test.iterrows():
    try:
        y_no_soc.append(predict_soh_no_soc(row))
    except:
        y_no_soc.append(np.nan)

y_no_soc = np.array(y_no_soc)

plot_soh_parity_by_material(df_test, y_no_soc)
plot_soh_error_by_material(df_test, y_no_soc)


# In[64]:


from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np

def compare_global_metrics(y_true, y_no_soc, y_soc):
    y_true = np.array(y_true)
    y_no_soc = np.array(y_no_soc)
    y_soc = np.array(y_soc)

    mask_no = ~np.isnan(y_no_soc)
    mask_soc = ~np.isnan(y_soc)

    print("=========== Overall SOH Performance ===========")
    print(f"SOC-unaware | MAE = {mean_absolute_error(y_true[mask_no], y_no_soc[mask_no]):.4f} "
          f"| R2 = {r2_score(y_true[mask_no], y_no_soc[mask_no]):.4f}")
    print(f"SOC-aware   | MAE = {mean_absolute_error(y_true[mask_soc], y_soc[mask_soc]):.4f} "
          f"| R2 = {r2_score(y_true[mask_soc], y_soc[mask_soc]):.4f}")

    print("\nImprovement:")
    print(f"↓ MAE improvement = "
          f"{mean_absolute_error(y_true[mask_no], y_no_soc[mask_no]) - mean_absolute_error(y_true[mask_soc], y_soc[mask_soc]):.4f}")
    print(f"↑ R2 improvement  = "
          f"{r2_score(y_true[mask_soc], y_soc[mask_soc]) - r2_score(y_true[mask_no], y_no_soc[mask_no]):.4f}")


# In[68]:


compare_global_metrics(y_true, y_no_soc, y_oracle)

import pandas as pd
import matplotlib.pyplot as plt

def compare_metrics_by_material(df_test, y_no_soc, y_soc):

    records = []

    for mat in df_test["Mat"].unique():
        idx = df_test["Mat"] == mat

        y_t = df_test.loc[idx, "SOH"].values
        y_n = np.array(y_no_soc)[idx]
        y_s = np.array(y_soc)[idx]

        mask_n = ~np.isnan(y_n)
        mask_s = ~np.isnan(y_s)

        if mask_n.sum() < 20 or mask_s.sum() < 20:
            continue

        records.append({
            "Mat": mat,
            "MAE_noSOC": mean_absolute_error(y_t[mask_n], y_n[mask_n]),
            "MAE_SOC": mean_absolute_error(y_t[mask_s], y_s[mask_s]),
            "R2_noSOC": r2_score(y_t[mask_n], y_n[mask_n]),
            "R2_SOC": r2_score(y_t[mask_s], y_s[mask_s]),
        })

    df_cmp = pd.DataFrame(records)
    df_cmp["MAE_improve"] = df_cmp["MAE_noSOC"] - df_cmp["MAE_SOC"]
    df_cmp["R2_improve"] = df_cmp["R2_SOC"] - df_cmp["R2_noSOC"]
    
    df_cmp["MAE_improve"] = (df_cmp["MAE_noSOC"] - df_cmp["MAE_SOC"])/df_cmp["MAE_noSOC"]
    df_cmp["R2_improve"] = (df_cmp["R2_SOC"] - df_cmp["R2_noSOC"])/df_cmp["R2_noSOC"]

    return df_cmp

df_cmp = compare_metrics_by_material(df_test, y_no_soc, y_oracle)
df_cmp

plt.figure(figsize=(3,2), dpi=600)
plt.bar(df_cmp["Mat"], df_cmp["R2_improve"], color="#D097BA")
plt.ylabel("MAE Reduction")
plt.title("Benefit of SOC-aware SOH Estimation")
plt.ylabel("R2 Improvement")
plt.title("Benefit of SOC-aware SOH Estimation")
plt.tight_layout()
plt.show()


# In[72]:


def plot_soh_error_box_strip_vs_soc(
    df_test, y_pred,
    soc_bins=[0, 20, 40,60,80,100]
):

    df = df_test.copy()
    df["SOH_pred"] = y_pred
    df["abs_err"] = np.abs(df["SOH_pred"] - df["SOH"])

    df["SOC_bin"] = pd.cut(
        df["SOC"],
        bins=soc_bins,
        include_lowest=True
    )

    df = df.dropna(subset=["abs_err", "SOC_bin"])

    plt.figure(figsize=(3,2.4),dpi=600)

    sns.boxplot(
        data=df,
        x="SOC_bin",
        y="abs_err",
        showfliers=False,
        color="lightgray"
    )

    sns.stripplot(
        data=df,
        x="SOC_bin",
        y="abs_err",
        size=2,
        alpha=0.35,
        jitter=True,
        color="#80BEB3"
    )

    plt.xlabel("SOC Range (%)")
    plt.ylabel("|SOH Error|")
    plt.title("SOH Error vs SOC")

    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

plot_soh_error_box_strip_vs_soc(df_test, y_oracle)


# In[71]:


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_soh_error_box_strip_by_material(df_test, y_pred):

    df = df_test.copy()
    df["SOH_pred"] = y_pred
    df["abs_err"] = np.abs(df["SOH_pred"] - df["SOH"])
    df = df.dropna(subset=["abs_err"])

    plt.figure(figsize=(3.6, 2.6), dpi=600)
    sns.boxplot(
        data=df,
        x="Mat",
        y="abs_err",
        showfliers=False,
        color="lightgray",
        width=0.55
    )

    sns.stripplot(
        data=df,
        x="Mat",
        y="abs_err",
        size=2.5,
        jitter=0.25,
        alpha=0.45,
        color="#80BEB3"
    )

    plt.xlabel("Material")
    plt.ylabel("|SOH Error|")
    plt.title("SOH Estimation Error by Material")

    plt.tight_layout()
    plt.show()

plot_soh_error_box_strip_by_material(df_test, y_oracle)


# In[14]:


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_soh_error_box_strip_by_material(df_test, y_pred):

    df = df_test.copy()
    df["SOH_pred"] = y_pred
    df["abs_err"] = np.abs(df["SOH_pred"] - df["SOH"])
    df = df.dropna(subset=["abs_err"])

    plt.figure(figsize=(3.6, 2.6), dpi=600)

    sns.boxplot(
        data=df,
        x="Mat",
        y="abs_err",
        showfliers=False,
        color="lightgray",
        width=0.55
    )

    sns.stripplot(
        data=df,
        x="Mat",
        y="abs_err",
        size=2.5,
        jitter=0.25,
        alpha=0.45,
        color="#80BEB3"
    )

    plt.xlabel("Material")
    plt.ylabel("|SOH Error|")
    plt.title("SOH Estimation Error by Material")

    plt.tight_layout()
    plt.show()

plot_soh_error_box_strip_by_material(df_test, y_oracle)


# Data density

# In[12]:


from sklearn.neighbors import NearestNeighbors
import numpy as np

def compute_knn_density(X_train, X_query, k=10):
    k = min(k, len(X_train) - 1)
    nbrs = NearestNeighbors(n_neighbors=k).fit(X_train)
    dists, _ = nbrs.kneighbors(X_query)
    return 1.0 / (np.mean(dists, axis=1) + 1e-8)


# In[48]:


from xgboost import XGBClassifier, XGBRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
from collections import defaultdict

def train_soc_continuous_pipeline(df_train, U_cols):

    X_tr = df_train[U_cols].values
    scaler_X = StandardScaler()
    X_tr_scaled = scaler_X.fit_transform(X_tr)

    le_mat = LabelEncoder()
    y_mat = le_mat.fit_transform(df_train["Mat"])

    clf_mat = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="mlogloss",
        random_state=42
    )
    clf_mat.fit(X_tr_scaled, y_mat)

    soc_models = {}

    for mat in df_train["Mat"].unique():
        idx = df_train["Mat"] == mat

        X_m = X_tr_scaled[idx]
        y_soc = df_train.loc[idx, "SOC"].values

        reg = XGBRegressor(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            objective="reg:squarederror",
            random_state=42
        )
        reg.fit(X_m, y_soc)

        soc_models[mat] = reg

    soh_models = {}

    for mat in df_train["Mat"].unique():
        idx = df_train["Mat"] == mat

        X_u = df_train.loc[idx, U_cols].values
        soc = df_train.loc[idx, "SOC"].values.reshape(-1, 1)
        X_soh = np.hstack([X_u, soc])
        y_soh = df_train.loc[idx, "SOH"].values

        scaler_soh = StandardScaler()
        X_soh_scaled = scaler_soh.fit_transform(X_soh)

        reg = XGBRegressor(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42
        )
        reg.fit(X_soh_scaled, y_soh)

        soh_models[mat] = {
            "model": reg,
            "scaler": scaler_soh
        }

    return scaler_X, clf_mat, le_mat, soc_models, soh_models


# In[49]:


def predict_soh_continuous(
    row, U_cols,
    scaler_X, clf_mat, le_mat,
    soc_models, soh_models,
    mode="oracle"
):
    U = row[U_cols].values.reshape(1, -1)
    U_scaled = scaler_X.transform(U)

    if mode == "oracle":
        mat = row["Mat"]
    else:
        mat_id = clf_mat.predict(U_scaled)[0]
        mat = le_mat.inverse_transform([mat_id])[0]

    if mat not in soc_models or mat not in soh_models:
        return np.nan

    if mode == "oracle":
        soc = row["SOC"]
    else:
        soc = soc_models[mat].predict(U_scaled)[0]

    X_soh = np.hstack([U, [[soc]]])
    X_soh_scaled = soh_models[mat]["scaler"].transform(X_soh)

    return soh_models[mat]["model"].predict(X_soh_scaled)[0]


# In[42]:


def sample_training_batteries(df_train, ratio=1.0, seed=42):
    rng = np.random.RandomState(seed)
    dfs = []

    for mat in df_train["Mat"].unique():
        df_m = df_train[df_train["Mat"] == mat]
        battery_ids = df_m["No."].unique()

        n_sel = max(1, int(len(battery_ids) * ratio))
        sel_ids = rng.choice(battery_ids, size=n_sel, replace=False)

        dfs.append(df_m[df_m["No."].isin(sel_ids)])

    return pd.concat(dfs, ignore_index=True)


# In[43]:


def sample_feature_blocks(blocks, k, seed=42):
    rng = random.Random(seed)
    keys = list(blocks.keys())
    sel_keys = rng.sample(keys, k)
    U_cols = []
    for kk in sel_keys:
        U_cols.extend(blocks[kk])
    return U_cols, sel_keys


# In[45]:


FEATURE_BLOCKS = {
    "B1": [f"U{i}" for i in range(1, 5)],    # U1–U4
    "B2": [f"U{i}" for i in range(5, 9)],    # U5–U8
    "B3": [f"U{i}" for i in range(9, 13)],   # U9–U12
    "B4": [f"U{i}" for i in range(13, 17)],  # U13–U16
    "B5": [f"U{i}" for i in range(17, 21)],  # U17–U20
}


# In[51]:


import random
results_soh = []
TRAIN_RATIOS = [0.1, 0.2, 0.3, 0.4, 0.5,0.6, 0.7,0.8, 0.9,1.0]
for k in range(1, 6):     
    for ratio in TRAIN_RATIOS:

        print(f"🔍 blocks={k}, train_ratio={ratio}")

        df_sub = sample_training_batteries(
            df_train_used, ratio=ratio, seed=42
        )
        if len(df_sub) < 80:
            continue

        U_cols, sel_blocks = sample_feature_blocks(
            FEATURE_BLOCKS, k, seed=42
        )

        scaler_X, clf_mat, le_mat, soc_models, soh_models = \
            train_soc_continuous_pipeline(df_sub, U_cols)
       
        soh_model_size = 0
        soh_n_params = 0
        soh_flops = 0

        X_tr_scaled = scaler_X.transform(df_sub[U_cols].values)
        X_te_scaled = scaler_X.transform(df_test[U_cols].values)

        densities = compute_knn_density(X_tr_scaled, X_te_scaled)
        mean_density = np.nanmean(densities)

        y_true, y_pred = [], []

        for _, row in df_test.iterrows():
            try:
                p = predict_soh_continuous(
                    row, U_cols,
                    scaler_X, clf_mat, le_mat,
                    soc_models, soh_models,
                    mode="oracle"
                )
                if not np.isnan(p):
                    y_true.append(row["SOH"])
                    y_pred.append(p)
            except:
                continue

        if len(y_pred) < 30:
            mae, r2 = np.nan, np.nan
        else:
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)

        results_soh.append({
            "n_blocks": k,
            "train_ratio": ratio,
            "mean_density": mean_density,
            "soh_mae": mae,
            "soh_r2": r2,
        })


# In[56]:


df_res = pd.DataFrame(results_soh)

BLOCKS = sorted(df_res["n_blocks"].unique())
RATIOS = sorted(df_res["train_ratio"].unique())

H_density = np.full((len(BLOCKS), len(RATIOS)), np.nan)

for i, b in enumerate(BLOCKS):
    for j, r in enumerate(RATIOS):
        v = df_res.loc[
            (df_res["n_blocks"] == b) &
            (df_res["train_ratio"] == r),
            "mean_density"
        ]
        if len(v) > 0:
            H_density[i, j] = v.values[0]

fig, ax = plt.subplots(figsize=(4, 3), dpi=600)

im = ax.imshow(
    H_density,
    origin="lower",
    aspect="auto",
    cmap="cividis"   
)

ax.set_xticks(np.arange(len(RATIOS)))
ax.set_xticklabels([f"{r:.1f}" for r in RATIOS])
ax.set_xlabel("Training sample ratio")

ax.set_yticks(np.arange(len(BLOCKS)))
ax.set_yticklabels(BLOCKS)
ax.set_ylabel("Number of pulse blocks")

ax.set_title("Feature-space data density (mean KNN)")

cbar = fig.colorbar(im, ax=ax, fraction=0.046)
cbar.set_label("Mean KNN density")

plt.tight_layout()
plt.show()


# In[123]:


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set_theme(style="white")

fig, ax = plt.subplots(figsize=(6, 5),dpi=600)

feature_sets = sorted(df_soh["n_blocks"].unique())
palette = sns.color_palette("viridis", n_colors=len(feature_sets))
color_map = dict(zip(feature_sets, palette))

size_min, size_max = 40, 180
r_min = df_soh["train_ratio"].min()
r_max = df_soh["train_ratio"].max()

def ratio_to_size(r):
    return size_min + (r - r_min) / (r_max - r_min) * (size_max - size_min)

for fs in feature_sets:
    sub = (
        df_soh[df_soh["n_blocks"] == fs]
        .sort_values("mean_density")
    )

    ax.plot(
        sub["mean_density"],
        sub["soh_mae"],
        color=color_map[fs],
        linewidth=2.0,
        alpha=0.85
    )

    ax.scatter(
        sub["mean_density"],
        sub["soh_mae"],
        s=sub["train_ratio"].apply(ratio_to_size),
        color=color_map[fs],
        edgecolor="black",
        linewidth=0.6,
        alpha=0.9,
        label=fs
    )

    ax.axhline(
        y=0.03,
        color="gray",
        linestyle=":",
        linewidth=2.5
    )

ax.set_xlabel("Mean data density", fontsize=13)
ax.set_ylabel("SOH MAE", fontsize=13)
ax.set_title(
    "Density-driven SOH sufficiency",
    fontsize=14
)

handles_color = [
    plt.Line2D([0], [0], color=color_map[f], lw=3, label=f)
    for f in feature_sets
]
legend1 = ax.legend(
    handles=handles_color,
    title="Pulse Count",
    loc="upper right",
    frameon=False
)

for r in sorted(df_soh["train_ratio"].unique()):
    ax.scatter(
        [], [],
        s=ratio_to_size(r),
        color="gray",
        edgecolor="black",
        label=f"Train ratio = {r}"
    )

ax.legend(
    title="Training data ratio",
    loc="upper center",
    bbox_to_anchor=(0.5, -0.18),
    ncol=4,
    frameon=False
)
ax.set_ylim(0.023,0.055)
sns.despine()
plt.tight_layout()
plt.show()


# In[130]:


df_soh_delta = []

for nb in sorted(df_soh["n_blocks"].unique()):
    sub = (
        df_soh[df_soh["n_blocks"] == nb]
        .sort_values("mean_density")
        .copy()
    )

    sub["delta_soh_mae"] = sub["soh_mae"].diff()
    df_soh_delta.append(abs(sub))

df_soh_delta = pd.concat(df_soh_delta, ignore_index=True)

fig, ax = plt.subplots(figsize=(5, 3.5), dpi=600)

for fs in feature_sets:
    sub = (
        df_soh_delta[df_soh_delta["n_blocks"] == fs]
        .dropna(subset=["delta_soh_mae"])
        .sort_values("mean_density")
    )

    ax.plot(
        sub["mean_density"],
        abs(-sub["delta_soh_mae"]),   
        color=color_map[fs],
        linewidth=2.0,
        alpha=0.85
    )

    ax.scatter(
        sub["mean_density"],
        abs(-sub["delta_soh_mae"]),
        s=sub["train_ratio"].apply(ratio_to_size),
        color=color_map[fs],
        edgecolor="black",
        linewidth=0.6,
        alpha=0.9
    )

ax.axhline(
    y=0.002,
    color="gray",
    linestyle=":",
    linewidth=2.5
)

ax.set_xlabel("Mean data density", fontsize=13)
ax.set_ylabel("Marginal SOH error change", fontsize=13)
ax.set_title(
    "Diminishing returns of SOH accuracy with increasing data density",
    fontsize=14
)

sns.despine()
plt.tight_layout()
plt.show()

