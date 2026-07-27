import joblib
m = joblib.load('model_metadata.pkl')
print("Model:", m['model_type'])
print("Accuracy:", m['accuracy'])
print("F1:", m['f1_score'])
print("Precision:", m['precision'])
print("Recall:", m['recall'])
print("Features:", m['n_features'])
print()
print("All models:")
for k, v in m['all_models'].items():
    print(f"  {k}: acc={v['accuracy']}%, f1={v['f1']}%")
print()
print("Top 10 features:")
for i, f in enumerate(m['top_features'][:10], 1):
    print(f"  {i}. {f}")
